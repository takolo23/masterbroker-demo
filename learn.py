from __future__ import annotations
import argparse, json
from pathlib import Path
from masterbroker.engine import load_csv
from masterbroker.learner_agent import LearningAgent
from run_demo import synthetic

def main():
    parser=argparse.ArgumentParser(description='Autonomous model-review cycle. It only promotes validated PAPER_TRADING candidates.')
    parser.add_argument('--csv',type=Path,help='OHLC CSV: timestamp,open,high,low,close,volume')
    args=parser.parse_args(); root=Path(__file__).parent
    candles=load_csv(args.csv) if args.csv else synthetic()
    source=str(args.csv) if args.csv else 'synthetic-demo-data'
    state=LearningAgent(root/'reports'/'model_registry.json').learn(candles,source)
    print(json.dumps({'status':state['status'],'mode':state['mode'],'last_event':state['last_event']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

