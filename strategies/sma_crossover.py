from strategies.base import Strategy, StrategyParameter
import polars as pl


class SMACrossoverStrategy(Strategy):

    def __init__(self, fast: int, slow: int):
        self.fast = fast
        self.slow = slow

    @classmethod
    def name(cls) -> str:
        return "SMA Crossover"

    @classmethod
    def parameters(cls):
        return {
            "fast": StrategyParameter(
                name="Fast SMA",
                type=int,
                default=20,
                min=2,
                max=100,
                step=1,
            ),
            "slow": StrategyParameter(
                name="Slow SMA",
                type=int,
                default=50,
                min=5,
                max=300,
                step=1,
            ),
        }

    def on_candle(self, idx, data: pl.DataFrame, portfolio):
        if idx < self.slow:
            return None

        fast_sma = data["close"][idx - self.fast:idx].mean()
        slow_sma = data["close"][idx - self.slow:idx].mean()

        if fast_sma > slow_sma and not portfolio.position.is_open():
            return "BUY"

        if fast_sma < slow_sma and portfolio.position.is_open():
            return "SELL"

        return None
