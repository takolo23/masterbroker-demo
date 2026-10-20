from __future__ import annotations
import argparse, csv, hashlib, json, time
from pathlib import Path
from masterbroker.activity import ActivityLog
from masterbroker.config import StrategyConfig
from masterbroker.engine import load_csv
from masterbroker.strategy import ConfluenceStrategy

ROOT=Path(__file__).parent; REPORTS=ROOT/'reports'
STATE=REPORTS/'demo_autopilot_state.json'; STATUS=REPORTS/'demo_autopilot_status.json'; TRADES=REPORTS/'demo_autopilot_trades.jsonl'

def synthetic_candles(count=900):
    # Deterministic market-like data used only to test the paper execution loop.
    from run_demo import synthetic
    return synthetic(count)

def read_json(path, fallback):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return fallback

def save_json(path, value):
    path.parent.mkdir(exist_ok=True); path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def fresh_state():
    return {'balance':12550.0,'last_index':0,'source_id':'','higher':{'wins':0,'losses':0},'lower':{'wins':0,'losses':0},'trades':0,'daily':{}}

def posterior(bucket):
    # Beta(1,1) prior: it learns without pretending certainty after one trade.
    return (bucket['wins']+1)/(bucket['wins']+bucket['losses']+2)

def run(candles, source, reset=False):
    REPORTS.mkdir(exist_ok=True)
    # The source name stays stable as new candles are appended, so the next run
    # processes only the newly closed candles instead of replaying history.
    source_id=hashlib.sha256(source.encode()).hexdigest()[:16]
    state=fresh_state() if reset else read_json(STATE,fresh_state())
    settings=read_json(REPORTS/'bot_settings.json',{})
    control=read_json(REPORTS/'bot_control.json',{})
    if control.get('autopilot')=='STOPPED':
        status={'mode':'DEMO_AUTOPILOT_STOPPED','execution':'VIRTUAL_DEMO_ONLY','source':source,'latest_decision':'WAIT','new_virtual_trades':0,'note':'Stopped from the Operar panel.'}
        save_json(STATUS,status); return status
    if state.get('source_id')!=source_id:
        state=fresh_state(); state['source_id']=source_id
    strategy=ConfluenceStrategy(StrategyConfig()); signals=strategy.signals(candles); activity=ActivityLog(REPORTS/'activity.jsonl')
    start=max(34,int(state.get('last_index',0))); opened=[]
    for i in range(start,len(candles)-strategy.config.holding_bars):
        signal=signals[i]
        if not signal or signal.score<0.55: continue
        decision='HIGHER' if signal.side=='LONG' else 'LOWER'; bucket=state[decision.lower()]
        # Combine the technical confluence score with the learned directional
        # reliability.  It starts conservative and needs strong confluence to
        # cross the default 78% demo threshold.
        confidence=round(min(.95,.45+signal.score*.55+(posterior(bucket)-.5)*.20),3)
        # The adaptive gate rejects weak ideas until evidence accumulates in demo.
        min_confidence=max(0.30,float(settings.get('confidence',78))/100)
        if confidence<min_confidence or bool(settings.get('onlyAnalyze',False)): continue
        if float(settings.get('payout',80))>85: continue
        day=candles[i].timestamp.date().isoformat(); guard=state['daily'].setdefault(day,{'trades':0,'pnl':0.0,'loss_streak':0})
        max_trades=int(settings.get('maxTrades',4)); max_losses=int(settings.get('losses',3))
        if guard['trades']>=max_trades or guard['loss_streak']>=max_losses or guard['pnl']<=-state['balance']*0.02: continue
        exit_candle=candles[i+strategy.config.holding_bars]
        won=(exit_candle.close>candles[i].close) if decision=='HIGHER' else (exit_candle.close<candles[i].close)
        pnl=0.85 if won else -1.0; bucket['wins' if won else 'losses']+=1; state['balance']+=pnl; state['trades']+=1
        guard['trades']+=1; guard['pnl']+=pnl; guard['loss_streak']=0 if won else guard['loss_streak']+1
        record={'timestamp':candles[i].timestamp.isoformat(),'asset':'EUR/USD','decision':decision,'outcome':'WIN' if won else 'LOSS','stake':1.0,'pnl':pnl,'confidence':confidence,'entry':candles[i].close,'exit':exit_candle.close,'reason':signal.rationale,'execution':'VIRTUAL_DEMO_ONLY','source':source}
        with TRADES.open('a',encoding='utf-8',newline='\n') as f: f.write(json.dumps(record,ensure_ascii=False)+'\n')
        activity.add('demo_trade',f"Operacion demo {decision}: {record['outcome']}",record); opened.append(record)
    state['last_index']=max(0,len(candles)-strategy.config.holding_bars); save_json(STATE,state)
    wins=state['higher']['wins']+state['lower']['wins']; trades=state['trades']
    latest=opened[-1] if opened else None
    status={'mode':'DEMO_AUTOPILOT','execution':'VIRTUAL_DEMO_ONLY','source':source,'balance_demo':round(state['balance'],2),'trades':trades,'wins':wins,'win_rate_pct':round(wins/trades*100,2) if trades else 0.0,'higher_confidence':round(posterior(state['higher']),3),'lower_confidence':round(posterior(state['lower']),3),'latest_decision':latest['decision'] if latest else 'WAIT','latest_trade':latest,'new_virtual_trades':len(opened),'note':'Decision loop only. It never clicks IQ Option or sends real orders.'}
    save_json(STATUS,status); return status

def main():
    p=argparse.ArgumentParser(description='MasterBroker adaptive demo autopilot')
    p.add_argument('--csv',type=Path); p.add_argument('--simulate',action='store_true',help='Run on synthetic test candles'); p.add_argument('--reset',action='store_true'); p.add_argument('--watch',action='store_true'); p.add_argument('--interval',type=int,default=60); args=p.parse_args()
    first=True
    while True:
        if args.csv: candles,source=load_csv(args.csv),args.csv.name
        elif args.simulate: candles,source=synthetic_candles(),'synthetic test candles'
        else:
            candidates=sorted((ROOT/'data'/'inbox').glob('*.csv'))
            if not candidates:
                if args.watch:
                    print('Waiting for an OHLC CSV in data/inbox...'); time.sleep(max(20,args.interval)); continue
                raise SystemExit('No OHLC CSV found. Use --csv or --simulate.')
            candles,source=load_csv(candidates[-1]),candidates[-1].name
        if len(candles)<50: raise SystemExit('At least 50 candles are required.')
        print(json.dumps(run(candles,source,args.reset and first),ensure_ascii=False,indent=2)); first=False
        if not args.watch: break
        time.sleep(max(20,args.interval))

if __name__=='__main__': main()

