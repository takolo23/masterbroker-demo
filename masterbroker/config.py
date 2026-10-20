from dataclasses import dataclass

@dataclass(frozen=True)
class RiskConfig:
    starting_balance: float = 10_000.0
    risk_per_trade: float = 0.005
    daily_loss_limit: float = 0.02
    max_trades_per_day: int = 4
    max_consecutive_losses: int = 3
    min_position_value: float = 1.0
    max_position_value: float = 50.0
    estimated_cost_rate: float = 0.0008

@dataclass(frozen=True)
class StrategyConfig:
    fast_ema: int = 12
    slow_ema: int = 26
    rsi_period: int = 14
    atr_period: int = 14
    rsi_long_floor: float = 52.0
    rsi_short_ceiling: float = 48.0
    min_atr_ratio: float = 0.00035
    holding_bars: int = 6

@dataclass(frozen=True)
class ValidationConfig:
    train_fraction: float = 0.60
    min_test_trades: int = 30
    min_profit_factor: float = 1.05
    max_drawdown: float = 0.08

