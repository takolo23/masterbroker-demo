from __future__ import annotations
import csv,json,webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from agent_service import run_cycle
from masterbroker.activity import ActivityLog
ROOT=Path(__file__).parent; REPORTS=ROOT/'reports'; BG='#0a1020'; PANEL='#121c31'; CARD='#192844'; TEXT='#eff6ff'; MUTED='#a9bad5'; GREEN='#42d392'; ORANGE='#f6ae4a'; RED='#ff7373'; BLUE='#65b7ff'
def read_json(name,fallback):
    try:return json.loads((REPORTS/name).read_text(encoding='utf-8'))
    except Exception:return fallback
class Card(tk.Frame):
    def __init__(self,parent,label,value,color=BLUE):
        super().__init__(parent,bg=CARD,highlightthickness=1,highlightbackground='#25395b'); self.value=tk.StringVar(value=value)
        tk.Label(self,text=label.upper(),bg=CARD,fg=MUTED,font=('Segoe UI',8,'bold')).pack(anchor='w',padx=14,pady=(12,1));tk.Label(self,textvariable=self.value,bg=CARD,fg=color,font=('Segoe UI',18,'bold')).pack(anchor='w',padx=14,pady=(0,12))
class LiveTicker(tk.Toplevel):
    """Always-on-top compact monitor for demo signals and bot events."""
    def __init__(self, app):
        super().__init__(app); self.app=app
        self.title('MasterBroker - Live'); self.geometry('385x285+24+84'); self.minsize(330,240)
        self.configure(bg=BG); self.attributes('-topmost',True); self.protocol('WM_DELETE_WINDOW',self.withdraw)
        header=tk.Frame(self,bg='#0e1a2e'); header.pack(fill='x')
        tk.Label(header,text='LIVE OPERATIONS',bg='#0e1a2e',fg=GREEN,font=('Segoe UI',10,'bold')).pack(side='left',padx=14,pady=12)
        self.mode=tk.Label(header,text='DEMO',bg='#0e1a2e',fg=ORANGE,font=('Segoe UI',9,'bold')); self.mode.pack(side='right',padx=14)
        overview=tk.Frame(self,bg=BG); overview.pack(fill='x',padx=14,pady=(12,6))
        self.signal=tk.Label(overview,text='WAITING FOR MARKET',bg=BG,fg=ORANGE,font=('Segoe UI',15,'bold')); self.signal.pack(anchor='w')
        self.detail=tk.Label(overview,text='No quote received yet',bg=BG,fg=MUTED,font=('Segoe UI',9)); self.detail.pack(anchor='w',pady=(2,8))
        tk.Label(self,text='LATEST BOT MOVEMENTS',bg=BG,fg=MUTED,font=('Segoe UI',8,'bold')).pack(anchor='w',padx=14)
        self.feed=tk.Text(self,bg=PANEL,fg=TEXT,relief='flat',height=8,wrap='word',font=('Consolas',9),padx=10,pady=8)
        self.feed.pack(fill='both',expand=True,padx=14,pady=(5,12)); self.feed.configure(state='disabled')
        self.refresh()
    def write(self, value):
        self.feed.configure(state='normal'); self.feed.delete('1.0','end'); self.feed.insert('end',value); self.feed.configure(state='disabled')
    def refresh(self):
        s=read_json('agent_status.json',{}); sig=read_json('paper_signal.json',{'action':'WAIT'}); auto=read_json('demo_autopilot_status.json',{})
        session=s.get('browser_session') or {}; action=auto.get('latest_decision') or sig.get('action','WAIT'); asset=session.get('asset','Market')
        colors={'BUY':GREEN,'SELL':RED,'HIGHER':GREEN,'LOWER':RED,'WAIT':ORANGE}; labels={'BUY':'BUY SIGNAL','SELL':'SELL SIGNAL','HIGHER':'HIGHER (DEMO)','LOWER':'LOWER (DEMO)','WAIT':'WAITING FOR MARKET'}
        self.signal.configure(text=labels.get(action,action),fg=colors.get(action,BLUE)); self.mode.configure(text=auto.get('mode',s.get('mode','DEMO_ONLY')))
        detail=f"{asset}  |  Gate: {s.get('trade_gate','-')}"
        if auto: detail=f"{asset}  |  Demo balance: ${auto.get('balance_demo','-')}  |  Win: {auto.get('win_rate_pct','-')}%"
        self.detail.configure(text=detail)
        events=ActivityLog(REPORTS/'activity.jsonl').recent(5)
        feed='\n\n'.join(f"{x['at'][11:19]}  {x['message']}" for x in events) or 'No movements yet.\nThis window updates automatically.'
        self.write(feed); self.after(1000,self.refresh)

class MasterBrokerApp(tk.Tk):
    def __init__(self):
        super().__init__();self.title('MasterBroker | IQ Option Demo Monitor');self.geometry('1060x700');self.minsize(880,600);self.configure(bg=BG)
        head=tk.Frame(self,bg=BG);head.pack(fill='x',padx=26,pady=(22,8));tk.Label(head,text='MASTERBROKER',bg=BG,fg=TEXT,font=('Segoe UI',22,'bold')).pack(side='left');self.live=tk.Label(head,text='? LIVE MONITOR',bg=BG,fg=GREEN,font=('Segoe UI',10,'bold'));self.live.pack(side='left',padx=14)
        controls=tk.Frame(head,bg=BG);controls.pack(side='right');self.button(controls,'Live window',self.show_ticker,BLUE).pack(side='left',padx=4);self.button(controls,'Actualizar',self.refresh,BLUE).pack(side='left',padx=4);self.button(controls,'Ciclo de aprendizaje',self.run_cycle,ORANGE).pack(side='left',padx=4);self.button(controls,'Abrir IQ Option',lambda:webbrowser.open('https://iqoption.com/pwa/traderoom'),GREEN).pack(side='left',padx=4)
        cards=tk.Frame(self,bg=BG);cards.pack(fill='x',padx=26,pady=10);self.cards={}
        for key,label,color in [('balance','Saldo demo',GREEN),('asset','Activo',BLUE),('signal','Se�al',ORANGE),('gate','Gate',GREEN),('orders','�rdenes reales',RED)]:self.cards[key]=Card(cards,label,'-',color);self.cards[key].pack(side='left',fill='x',expand=True,padx=4)
        body=tk.Frame(self,bg=BG);body.pack(fill='both',expand=True,padx=26,pady=(8,20));left=tk.Frame(body,bg=PANEL);left.pack(side='left',fill='both',expand=True,padx=(0,8));right=tk.Frame(body,bg=PANEL,width=340);right.pack(side='right',fill='both',padx=(8,0));right.pack_propagate(False)
        tk.Label(left,text='Actividad en vivo del agente',bg=PANEL,fg=TEXT,font=('Segoe UI',13,'bold')).pack(anchor='w',padx=16,pady=(16,8));self.activity=tk.Text(left,bg=PANEL,fg=TEXT,insertbackground=TEXT,relief='flat',wrap='word',font=('Consolas',10));self.activity.pack(fill='both',expand=True,padx=16,pady=(0,16));self.activity.configure(state='disabled')
        tk.Label(right,text='Estado de sesi�n',bg=PANEL,fg=TEXT,font=('Segoe UI',13,'bold')).pack(anchor='w',padx=16,pady=(16,8));self.session=tk.Text(right,bg=PANEL,fg='#cbd9ef',relief='flat',wrap='word',font=('Consolas',9));self.session.pack(fill='both',expand=True,padx=16,pady=(0,10));self.session.configure(state='disabled');self.footer=tk.Label(self,text='Actualizaci�n autom�tica cada 2 segundos � Datos del bot y de fuentes permitidas',bg=BG,fg=MUTED,font=('Segoe UI',9));self.footer.pack(anchor='w',padx=26,pady=(0,15));self.ticker=LiveTicker(self);self.refresh();self.after(2000,self.auto)
    def button(self,parent,text,cmd,color):return tk.Button(parent,text=text,command=cmd,bg=color,fg='#07101f',activebackground=color,relief='flat',font=('Segoe UI',9,'bold'),padx=11,pady=7,cursor='hand2')
    def write(self,widget,value):widget.configure(state='normal');widget.delete('1.0','end');widget.insert('end',value);widget.configure(state='disabled')
    def run_cycle(self):
        try:run_cycle()
        finally:self.refresh()
    def show_ticker(self):
        self.ticker.deiconify();self.ticker.lift();self.ticker.attributes('-topmost',True)
    def refresh(self):
        s=read_json('agent_status.json',{'mode':'STARTING','live_orders':'DISABLED'});session=s.get('browser_session') or {};sig=read_json('paper_signal.json',{'action':'WAIT'})
        self.cards['balance'].value.set('$12,550 DEMO' if session else '-');self.cards['asset'].value.set(session.get('asset','EUR/USD'));self.cards['signal'].value.set(sig.get('action','WAIT'));self.cards['gate'].value.set(s.get('trade_gate','-'));self.cards['orders'].value.set(s.get('live_orders','DISABLED'))
        items=ActivityLog(REPORTS/'activity.jsonl').recent(60);lines=[f"[{x['at'][11:19]}] {x['kind'].upper()}  {x['message']}\n{x.get('details',{})}\n" for x in items] or ['Esperando nueva actividad.'];self.write(self.activity,'\n'.join(lines));self.write(self.session,json.dumps(session,ensure_ascii=False,indent=2)+"\n\nSe�al\n"+json.dumps(sig,ensure_ascii=False,indent=2));self.footer.configure(text=f"�ltimo ciclo: {s.get('at','-')}  �  Actividades: {s.get('activity_count',len(items))}  �  Demo y fuentes permitidas")
    def auto(self):self.refresh();self.after(2000,self.auto)
if __name__=='__main__':MasterBrokerApp().mainloop()

