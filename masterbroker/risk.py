from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date
from .config import RiskConfig

@dataclass
class RiskState:
    balance: float
    day: date | None = None
    day_start_balance: float = 0.0
    daily_pnl: float = 0.0
    trades_today: int = 0
    consecutive_losses: int = 0
    halted: bool = False
    halt_reason: str = ''

class RiskEngine:
    def __init__(self, config: RiskConfig):
        self.config, self.state = config, RiskState(balance=config.starting_balance)

    def _new_day(self, today: date) -> None:
        if self.state.day != today:
            self.state.day, self.state.day_start_balance = today, self.state.balance
            self.state.daily_pnl, self.state.trades_today, self.state.consecutive_losses = 0.0, 0, 0
            self.state.halted, self.state.halt_reason = False, ''

    def can_trade(self, today: date) -> tuple[bool, str]:
        self._new_day(today)
        s, c = self.state, self.config
        if s.halted: return False, s.halt_reason
        if s.trades_today >= c.max_trades_per_day: return False, 'L�mite de operaciones diario'
        if s.daily_pnl <= -s.day_start_balance * c.daily_loss_limit:
            s.halted, s.halt_reason = True, 'Cortacircuitos: p�rdida diaria m�xima'
            return False, s.halt_reason
        if s.consecutive_losses >= c.max_consecutive_losses:
            s.halted, s.halt_reason = True, 'Cortacircuitos: racha m�xima de p�rdidas'
            return False, s.halt_reason
        return True, 'OK'

    def stake(self, stop_distance_ratio: float) -> float:
        raw = self.state.balance * self.config.risk_per_trade / max(stop_distance_ratio, 0.002)
        return round(min(self.config.max_position_value, max(self.config.min_position_value, raw)), 2)

    def record(self, pnl: float) -> None:
        s = self.state
        s.balance += pnl; s.daily_pnl += pnl; s.trades_today += 1
        s.consecutive_losses = s.consecutive_losses + 1 if pnl < 0 else 0

