from strategies.base import Strategy
import polars as pl


class BuyAndHoldStrategy(Strategy):

    @classmethod
    def name(cls) -> str:
        return "Buy & Hold"

    def on_candle(self, idx, data: pl.DataFrame, portfolio):
        if idx == 0 and not portfolio.position.is_open():
            return "BUY"
        return None
