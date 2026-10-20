from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

class ResearchMemory:
    """Append-only store for research files placed locally by the user or a permitted data feed."""
    def __init__(self, path: Path): self.path = path
    def ingest(self, source: Path) -> bool:
        text = source.read_text(encoding='utf-8', errors='replace')
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
        previous = set()
        if self.path.exists():
            for line in self.path.read_text(encoding='utf-8').splitlines():
                try: previous.add(json.loads(line)['sha256'])
                except (json.JSONDecodeError, KeyError): pass
        if digest in previous: return False
        record = {'at':datetime.now(timezone.utc).isoformat(),'source':source.name,'sha256':digest,'characters':len(text),'preview':text[:300].replace('\n',' ')}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a',encoding='utf-8',newline='\n') as f: f.write(json.dumps(record,ensure_ascii=False)+'\n')
        return True

