from __future__ import annotations
import hashlib, json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .config import RiskConfig, StrategyConfig, ValidationConfig
from .engine import backtest, stats
from .learning import choose_strategy
from .strategy import ConfluenceStrategy

class LearningAgent:
    """Auditable learner: candidates are promoted only after out-of-sample demo validation."""
    def __init__(self, registry_path: Path, risk: RiskConfig | None = None, base: StrategyConfig | None = None, validation: ValidationConfig | None = None):
        self.registry_path = registry_path
        self.ledger_path = registry_path.parent / 'learning_ledger.jsonl'
        self.risk, self.base, self.validation = risk or RiskConfig(), base or StrategyConfig(), validation or ValidationConfig()

    def current(self) -> dict:
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text(encoding='utf-8'))
        return {'mode':'PAPER_TRADING_ONLY','status':'baseline','params':asdict(self.base),'history':[]}

    def _append_ledger(self, event: dict) -> None:
        """Append-only memory: it never discards previous learning cycles."""
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open('a', encoding='utf-8', newline='\n') as ledger:
            ledger.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n')

    def learn(self, candles, source: str) -> dict:
        if len(candles) < 100:
            raise ValueError('Se requieren al menos 100 velas para aprender y validar.')
        current = self.current()
        candidate, report = choose_strategy(candles, self.risk, self.base, self.validation)
        evaluation = stats(backtest(candles, ConfluenceStrategy(candidate), self.risk), self.risk.starting_balance)
        fingerprint = hashlib.sha256((source + str(len(candles)) + str(candles[-1].timestamp)).encode()).hexdigest()[:16]
        event = {'at':datetime.now(timezone.utc).isoformat(),'source':source,'data_fingerprint':fingerprint,'validation':report,'evaluation':evaluation,'mode':'PAPER_TRADING_ONLY'}
        self._append_ledger(event)
        # The registry is convenient for current status; the JSONL ledger preserves every event forever.
        history = (current.get('history') or [])[-29:] + [event]
        if report.get('accepted'):
            current = {'mode':'PAPER_TRADING_ONLY','status':'candidate_promoted_for_demo','params':asdict(candidate),'last_event':event,'history':history}
        else:
            current['mode']='PAPER_TRADING_ONLY'; current['status']='candidate_rejected_baseline_retained'; current['last_event']=event; current['history']=history
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding='utf-8')
        return current

