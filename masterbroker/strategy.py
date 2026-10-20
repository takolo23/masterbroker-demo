from __future__ import annotations
from .config import StrategyConfig
from .models import Candle, Signal, atr, ema, rsi

class ConfluenceStrategy:
    """Deterministic and explainable strategy. No black-box decision is allowed."""
    def __init__(self, config: StrategyConfig): self.config = config

    def signals(self, candles: list[Candle]) -> list[Signal | None]:
        close = [c.close for c in candles]
        fast, slow = ema(close, self.config.fast_ema), ema(close, self.config.slow_ema)
        momentum, volatility = rsi(close, self.config.rsi_period), atr(candles, self.config.atr_period)
        warmup = max(self.config.slow_ema, self.config.rsi_period, self.config.atr_period)
        result: list[Signal | None] = [None] * len(candles)
        for i in range(warmup, len(candles)):
            ratio = volatility[i] / close[i] if close[i] else 0
            if ratio < self.config.min_atr_ratio: continue
            spread = (fast[i] - slow[i]) / close[i]
            if fast[i] > slow[i] and momentum[i] >= self.config.rsi_long_floor:
                result[i] = Signal('LONG', min(1.0, 0.5 + abs(spread) * 250 + (momentum[i]-50)/100), f'EMA alcista; RSI={momentum[i]:.1f}; ATR={ratio:.4%}')
            elif fast[i] < slow[i] and momentum[i] <= self.config.rsi_short_ceiling:
                result[i] = Signal('SHORT', min(1.0, 0.5 + abs(spread) * 250 + (50-momentum[i])/100), f'EMA bajista; RSI={momentum[i]:.1f}; ATR={ratio:.4%}')
        return result

