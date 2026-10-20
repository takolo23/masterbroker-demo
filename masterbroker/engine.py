from __future__ import annotations
import csv, json, sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from .config import RiskConfig
from .models import Candle, Trade
from .risk import RiskEngine
from .strategy import ConfluenceStrategy

class Journal:
    def __init__(self, db_path: Path):
        self.con = sqlite3.connect(db_path)
        self.con.execute('CREATE TABLE IF NOT EXISTS trades (timestamp TEXT, side TEXT, entry REAL, exit REAL, stake REAL, pnl REAL, reason TEXT)')
    def log(self, t: Trade) -> None:
        self.con.execute('INSERT INTO trades VALUES (?,?,?,?,?,?,?)', (t.timestamp.isoformat(),t.side,t.entry,t.exit,t.stake,t.pnl,t.reason)); self.con.commit()

def load_csv(path: Path) -> list[Candle]:
    with path.open(newline='', encoding='utf-8-sig') as f:
        rows = csv.DictReader(f)
        return [Candle(datetime.fromisoformat(r['timestamp'].replace('Z','+00:00')), *[float(r[k]) for k in ('open','high','low','close')], float(r.get('volume', 0))) for r in rows]

def backtest(candles: list[Candle], strategy: ConfluenceStrategy, risk_config: RiskConfig, journal: Journal | None = None) -> list[Trade]:
    signals, risk, trades = strategy.signals(candles), RiskEngine(risk_config), []
    h = strategy.config.holding_bars
    for i, signal in enumerate(signals):
        if not signal or i+h >= len(candles): continue
        allowed, reason = risk.can_trade(candles[i].timestamp.date())
        if not allowed: continue
        entry, exit_ = candles[i].close, candles[i+h].close
        gross_return = (exit_ - entry)/entry * (1 if signal.side == 'LONG' else -1)
        stake = risk.stake(max(abs(candles[i].high-candles[i].low) / entry, 0.002))
        pnl = stake * gross_return - stake * risk_config.estimated_cost_rate
        trade = Trade(candles[i].timestamp, signal.side, entry, exit_, stake, pnl, signal.rationale)
        risk.record(pnl); trades.append(trade)
        if journal: journal.log(trade)
    return trades

def stats(trades: list[Trade], starting_balance: float) -> dict:
    pnls = [t.pnl for t in trades]; equity = starting_balance; peak = equity; max_dd = 0.0
    for pnl in pnls:
        equity += pnl; peak = max(peak, equity); max_dd = max(max_dd, (peak-equity)/peak if peak else 0)
    wins = [x for x in pnls if x>0]; losses = [-x for x in pnls if x<0]
    return {'trades':len(trades),'net_pnl':round(sum(pnls),2),'return_pct':round((equity/starting_balance-1)*100,3),'win_rate_pct':round(100*len(wins)/len(pnls),2) if pnls else 0,'profit_factor':round(sum(wins)/sum(losses),3) if losses else (99.0 if wins else 0.0),'max_drawdown_pct':round(max_dd*100,3)}

def export_trades(path: Path, trades: list[Trade]):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp','side','entry','exit','stake','pnl','reason']); writer.writeheader()
        for t in trades: writer.writerow(asdict(t))

