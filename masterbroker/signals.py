from __future__ import annotations
from dataclasses import asdict
from .config import StrategyConfig
from .models import Candle
from .strategy import ConfluenceStrategy

def latest_signal(candles: list[Candle], config: StrategyConfig | None = None) -> dict:
    if not candles: return {'action':'WAIT','reason':'Sin velas disponibles'}
    signal = ConfluenceStrategy(config or StrategyConfig()).signals(candles)[-1]
    if not signal: return {'action':'WAIT','timestamp':candles[-1].timestamp.isoformat(),'reason':'No hay confluencia suficiente'}
    return {'action':'ALERT_ONLY','timestamp':candles[-1].timestamp.isoformat(),'side':signal.side,'score':round(signal.score,3),'reason':signal.rationale}

