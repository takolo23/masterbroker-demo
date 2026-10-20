from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

class ActivityLog:
    def __init__(self,path:Path): self.path=path
    def add(self,kind:str,message:str,details:dict|None=None):
        event={'at':datetime.now(timezone.utc).isoformat(),'kind':kind,'message':message,'details':details or {}}
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
        return event
    def recent(self,count=50):
        if not self.path.exists(): return []
        rows=[]
        for line in self.path.read_text(encoding='utf-8').splitlines()[-count:]:
            try: rows.append(json.loads(line))
            except json.JSONDecodeError: pass
        return list(reversed(rows))

