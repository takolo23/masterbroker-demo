from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from math import exp
from typing import Iterable

@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

@dataclass(frozen=True)
class Signal:
    side: str  # LONG or SHORT
    score: float
    rationale: str

@dataclass
class Trade:
    timestamp: datetime
    side: str
    entry: float
    exit: float
    stake: float
    pnl: float
    reason: str

def ema(values: list[float], period: int) -> list[float]:
    if not values: return []
    alpha = 2 / (period + 1)
    result = [values[0]]
    for value in values[1:]: result.append(alpha * value + (1 - alpha) * result[-1])
    return result

def rsi(values: list[float], period: int) -> list[float]:
    result = [50.0] * len(values)
    if len(values) <= period: return result
    gains, losses = 0.0, 0.0
    for i in range(1, period + 1):
        change = values[i] - values[i - 1]
        gains += max(change, 0); losses += max(-change, 0)
    avg_gain, avg_loss = gains / period, losses / period
    result[period] = 100 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)
    for i in range(period + 1, len(values)):
        change = values[i] - values[i - 1]
        avg_gain = (avg_gain * (period - 1) + max(change, 0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-change, 0)) / period
        result[i] = 100 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss)
    return result

def atr(candles: list[Candle], period: int) -> list[float]:
    if not candles: return []
    tr = [candles[0].high - candles[0].low]
    for i in range(1, len(candles)):
        prev = candles[i-1].close
        tr.append(max(candles[i].high-candles[i].low, abs(candles[i].high-prev), abs(candles[i].low-prev)))
    return ema(tr, period)

