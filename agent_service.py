from __future__ import annotations
import argparse, hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
from masterbroker.activity import ActivityLog
from masterbroker.alerting import NewsSafetyFilter
from masterbroker.engine import load_csv
from masterbroker.learner_agent import LearningAgent
from masterbroker.research_memory import ResearchMemory
from masterbroker.signals import latest_signal
from masterbroker.agents import evaluate_team
ROOT=Path(__file__).parent; REPORTS=ROOT/'reports'; INBOX=ROOT/'data'/'inbox'; RESEARCH=ROOT/'data'/'research'; STATE_FILE=REPORTS/'agent_runtime_state.json'; STATUS_FILE=REPORTS/'agent_status.json'
def load_state(): return json.loads(STATE_FILE.read_text(encoding='utf-8')) if STATE_FILE.exists() else {'processed_market_files':{},'cycles':0}
def save_state(state): REPORTS.mkdir(exist_ok=True); STATE_FILE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
def fingerprint(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run_cycle():
    REPORTS.mkdir(exist_ok=True); INBOX.mkdir(parents=True,exist_ok=True); RESEARCH.mkdir(parents=True,exist_ok=True)
    state, learner, activity=load_state(),LearningAgent(REPORTS/'model_registry.json'),ActivityLog(REPORTS/'activity.jsonl'); market_events=[]; pause_alerts=[]
    for csv_file in sorted(INBOX.glob('*.csv')):
        digest=fingerprint(csv_file)
        if state['processed_market_files'].get(csv_file.name)==digest: continue
        try:
            candles=load_csv(csv_file); result=learner.learn(candles,csv_file.name); signal=latest_signal(candles); signal.update({'source':csv_file.name,'execution':'DEMO_ALERT_ONLY'}); (REPORTS/'paper_signal.json').write_text(json.dumps(signal,ensure_ascii=False,indent=2),encoding='utf-8')
            event={'file':csv_file.name,'status':result['status'],'trades':result['last_event']['evaluation']['trades'],'signal':signal['action']}; market_events.append(event); activity.add('market','Archivo de velas procesado',event); state['processed_market_files'][csv_file.name]=digest
        except Exception as exc:
            event={'file':csv_file.name,'status':'rejected','reason':str(exc)}; market_events.append(event); activity.add('error','Archivo de mercado rechazado',event)
    memory=ResearchMemory(REPORTS/'research_memory.jsonl'); safety=NewsSafetyFilter(REPORTS/'alerts.jsonl'); research_events=0
    for item in list(RESEARCH.glob('*.md'))+list(RESEARCH.glob('*.txt')):
        if memory.ingest(item):
            research_events+=1; alert=safety.assess(item); activity.add('research','Nueva lectura de investigaci�n',{'file':item.name,'gate':alert['level']})
            if alert['level']=='PAUSE': pause_alerts.append(alert); activity.add('alert','Pausa por noticia de alto impacto',alert)
    state['cycles']+=1; state['last_cycle_at']=datetime.now(timezone.utc).isoformat(); save_state(state)
    session=json.loads((REPORTS/'browser_connection.json').read_text(encoding='utf-8')) if (REPORTS/'browser_connection.json').exists() else None
    settings=json.loads((REPORTS/'bot_settings.json').read_text(encoding='utf-8')) if (REPORTS/'bot_settings.json').exists() else {'confidence':85,'onlyAnalyze':True,'askConfirm':True}
    try:
        signal=json.loads((REPORTS/'paper_signal.json').read_text(encoding='utf-8'))
    except Exception:
        signal={'action':'WAIT','reason':'Esperando velas demo'}
    team=evaluate_team(signal, settings, news_paused=bool(pause_alerts))
    (REPORTS/'agent_team_status.json').write_text(json.dumps(team,ensure_ascii=False,indent=2),encoding='utf-8')
    status={'mode':'DEMO_ONLY','live_orders':'DISABLED','trade_gate':'PAUSED_FOR_NEWS' if pause_alerts else 'RESEARCH_AND_RISK_GATE','cycle':state['cycles'],'at':state['last_cycle_at'],'market_events':market_events,'research_files_ingested':research_events,'new_pause_alerts':pause_alerts,'browser_session':session,'activity_count':len(activity.recent(50)),'agents':team}
    STATUS_FILE.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); activity.add('system','Ciclo de agente completado',{'cycle':state['cycles'],'market_files':len(market_events),'research_files':research_events})
    (REPORTS/'daily_report.md').write_text(f"# Reporte MasterBroker\n\n- Ciclo: {status['cycle']}\n- Modo: {status['mode']}\n- Gate: {status['trade_gate']}\n- Archivos de mercado nuevos: {len(market_events)}\n- Lecturas nuevas: {research_events}\n- Se�ales: {[x.get('signal','N/A') for x in market_events]}\n",encoding='utf-8')
    return status
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--watch',action='store_true');parser.add_argument('--interval',type=int,default=60);args=parser.parse_args()
    while True:
        s=run_cycle();print(f"[{s['at']}] demo cycle {s['cycle']}: {len(s['market_events'])} market, {s['research_files_ingested']} research")
        if not args.watch:break
        time.sleep(max(30,args.interval))
if __name__=='__main__':main()

