from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

HIGH_IMPACT_TERMS = ('fomc', 'fed ', 'interest rate', 'cpi', 'inflation', 'nonfarm', 'nfp', 'employment report', 'guerra', 'war ', 'breaking news')

class NewsSafetyFilter:
    def __init__(self, alerts_path: Path): self.alerts_path = alerts_path
    def assess(self, source: Path) -> dict:
        text = source.read_text(encoding='utf-8', errors='replace').lower()
        matches = [term.strip() for term in HIGH_IMPACT_TERMS if term in text]
        result = {'at':datetime.now(timezone.utc).isoformat(),'source':source.name,'level':'PAUSE' if matches else 'CLEAR','matches':matches}
        if matches:
            self.alerts_path.parent.mkdir(parents=True,exist_ok=True)
            with self.alerts_path.open('a',encoding='utf-8',newline='\n') as file: file.write(json.dumps(result,ensure_ascii=False)+'\n')
        return result

