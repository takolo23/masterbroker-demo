from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from masterbroker.activity import ActivityLog

ROOT=Path(__file__).parent; REPORTS=ROOT/'reports'; UI=ROOT/'operar.html'
DEFAULT_SETTINGS={'assets':'EUR/USD, GBP/USD','hours':'08:00-18:00','timeframe':'1m, 5m','confidence':'85','payout':'80','maxTrades':'5','risk':'0.5','losses':'3','onlyAnalyze':True,'askConfirm':True}

def read_json(path,fallback):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception:return fallback
def write_json(path,value):
    path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*_):pass
    def respond(self,status,body,ctype='application/json; charset=utf-8'):
        data=body if isinstance(body,bytes) else json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
    def do_GET(self):
        route=self.path.split('?',1)[0]
        if route=='/':return self.respond(200,UI.read_bytes(),'text/html; charset=utf-8')
        if route=='/api/status':return self.respond(200,read_json(REPORTS/'agent_status.json',{'mode':'STARTING'}))
        if route=='/api/signal':return self.respond(200,read_json(REPORTS/'paper_signal.json',{'action':'WAIT'}))
        if route=='/api/autopilot':return self.respond(200,read_json(REPORTS/'demo_autopilot_status.json',{'mode':'DEMO_AUTOPILOT','latest_decision':'WAIT'}))
        if route=='/api/agents':return self.respond(200,read_json(REPORTS/'agent_team_status.json',{'mode':'DEMO_ONLY','live_orders':'DISABLED','proposal':'NO_OPERAR','agents':[]}))
        if route=='/api/activity':return self.respond(200,ActivityLog(REPORTS/'activity.jsonl').recent(8))
        if route=='/api/settings':return self.respond(200,read_json(REPORTS/'bot_settings.json',DEFAULT_SETTINGS))
        if route=='/api/alerts':
            lines=(REPORTS/'alerts.jsonl').read_text(encoding='utf-8').splitlines()[-10:] if (REPORTS/'alerts.jsonl').exists() else []
            return self.respond(200,[json.loads(x) for x in lines])
        return self.respond(404,{'error':'Not found'})
    def do_POST(self):
        route=self.path.split('?',1)[0]
        try:data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0')) or 0) or b'{}')
        except json.JSONDecodeError:return self.respond(400,{'error':'Invalid JSON'})
        activity=ActivityLog(REPORTS/'activity.jsonl')
        if route=='/api/settings':
            clean={**DEFAULT_SETTINGS,**{k:v for k,v in data.items() if k in DEFAULT_SETTINGS}}
            write_json(REPORTS/'bot_settings.json',clean);activity.add('settings','Configuracion demo actualizada',clean);return self.respond(200,clean)
        if route=='/api/control':
            action=data.get('action')
            if action=='stop':
                control={'autopilot':'STOPPED','at':'user_request'};write_json(REPORTS/'bot_control.json',control);activity.add('control','Bot demo detenido por el usuario',control);return self.respond(200,control)
            if action=='manual_demo':
                entry={'execution':'VIRTUAL_DEMO_ONLY','decision':data.get('decision'),'asset':data.get('asset'),'mode':data.get('mode'),'amount':data.get('amount'),'expiry':data.get('expiry')}
                activity.add('manual_demo','Entrada demo solicitada',entry);return self.respond(200,entry)
            if action=='analyze':
                entry={'asset':data.get('asset'),'timeframe':data.get('timeframe','1m'),'execution':'LOCAL_ANALYSIS_ONLY'}
                activity.add('analysis','Analisis local solicitado',entry);return self.respond(200,entry)
            return self.respond(400,{'error':'Unknown control action'})
        return self.respond(404,{'error':'Not found'})

def main():
    server=ThreadingHTTPServer(('127.0.0.1',8765),Handler);print('Panel Operar: http://127.0.0.1:8765');server.serve_forever()
if __name__=='__main__':main()

