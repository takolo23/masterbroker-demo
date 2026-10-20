from __future__ import annotations
from dataclasses import asdict, replace
from itertools import product
from .config import RiskConfig, StrategyConfig, ValidationConfig
from .engine import backtest, stats
from .strategy import ConfluenceStrategy

def choose_strategy(candles, risk: RiskConfig, base: StrategyConfig, validation: ValidationConfig):
    split = int(len(candles)*validation.train_fraction)
    train, test = candles[:split], candles[split:]
    candidates = []
    for fast, slow, floor, ceiling, holding in product((8,12,16),(21,26,34),(50,52,55),(50,48,45),(4,6,8)):
        if fast >= slow: continue
        cfg = replace(base, fast_ema=fast, slow_ema=slow, rsi_long_floor=floor, rsi_short_ceiling=ceiling, holding_bars=holding)
        train_stats = stats(backtest(train, ConfluenceStrategy(cfg), risk), risk.starting_balance)
        candidates.append((train_stats['net_pnl'] - train_stats['max_drawdown_pct']*3, cfg, train_stats))
    candidates.sort(key=lambda row: row[0], reverse=True)
    for _, cfg, training in candidates[:20]:
        test_stats = stats(backtest(test, ConfluenceStrategy(cfg), risk), risk.starting_balance)
        accepted = test_stats['trades'] >= validation.min_test_trades and test_stats['profit_factor'] >= validation.min_profit_factor and test_stats['max_drawdown_pct']/100 <= validation.max_drawdown
        if accepted: return cfg, {'accepted':True,'training':training,'test':test_stats,'params':asdict(cfg)}
    return base, {'accepted':False,'reason':'Ning�n candidato pas� la validaci�n fuera de muestra; se mantiene la estrategia base en modo demo.'}

