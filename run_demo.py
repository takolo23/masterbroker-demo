from __future__ import annotations
import argparse, json, random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from masterbroker import RiskConfig, StrategyConfig, ValidationConfig, backtest, load_csv, stats, export_trades, Journal, choose_strategy, ConfluenceStrategy
from masterbroker.models import Candle

def synthetic(n=1800):
    rng, price, out = random.Random(7), 100.0, []
    t = datetime(2026,1,1,tzinfo=timezone.utc)
    for i in range(n):
        drift = 0.00018 if (i//220)%2==0 else -0.00012
        change = drift + rng.gauss(0,0.0017)
        open_ = price; close = max(1, price*(1+change)); span = abs(rng.gauss(0.0013,0.00055))*price
        out.append(Candle(t+timedelta(minutes=5*i),open_,max(open_,close)+span/2,min(open_,close)-span/2,close,1000+rng.random()*500)); price=close
    return out

def main():
    p=argparse.ArgumentParser(description='MasterBroker research and paper-trading runner')
    p.add_argument('--csv', type=Path); args=p.parse_args()
    root=Path(__file__).parent; reports=root/'reports'; reports.mkdir(exist_ok=True)
    candles=load_csv(args.csv) if args.csv else synthetic()
    risk, base, validation=RiskConfig(), StrategyConfig(), ValidationConfig()
    selected, validation_report=choose_strategy(candles,risk,base,validation)
    journal=Journal(reports/'masterbroker.sqlite')
    trades=backtest(candles,ConfluenceStrategy(selected),risk,journal)
    result={'mode':'PAPER_TRADING_ONLY','source':str(args.csv) if args.csv else 'synthetic demo data','validation':validation_report,'final':stats(trades,risk.starting_balance),'safety':{'live_execution':'disabled','credentials':'not_requested','risk_limits':'enabled'}}
    (reports/'walk_forward_report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    export_trades(reports/'trades.csv',trades)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()

