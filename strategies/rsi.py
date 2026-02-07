# strategies/rsi.py
from strategies.base import Strategy, StrategyParameter
import polars as pl

class RSIStrategy(Strategy):

    def __init__(self, period: int = 14, buy: int = 30, sell: int = 70):
        self.period = period
        self.buy = buy
        self.sell = sell

    @classmethod
    def name(cls):
        return "RSI Mean Reversion"

    @classmethod
    def parameters(cls):
        return {
            "period": StrategyParameter("RSI Period", int, 14, 2, 50),
            "buy": StrategyParameter("Buy Below", int, 30, 10, 50),
            "sell": StrategyParameter("Sell Above", int, 70, 50, 90),
        }

    def on_candle(self, idx: int, data: pl.DataFrame, portfolio):
        if idx < self.period:
            return None

        # Calculate RSI
        closes = data["close"][idx - self.period:idx + 1]
        deltas = closes.diff().drop_nulls()
        gains = deltas.filter(deltas > 0)
        losses = deltas.filter(deltas < 0).abs()
        
        avg_gain = gains.mean() if len(gains) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # Trading logic
        if rsi < self.buy and not portfolio.position.is_open():
            return "BUY"
        elif rsi > self.sell and portfolio.position.is_open():
            return "SELL"
        
        return None
