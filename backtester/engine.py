# backtester/engine.py

import polars as pl
from backtester.portfolio import Portfolio
from backtester.strategy_base import Strategy


class BacktestEngine:
    def __init__(
        self,
        data: pl.DataFrame,
        strategy: Strategy,
        initial_cash: float = 100_000,
        trade_quantity: int = 1,
    ):
        self.data = data
        self.strategy = strategy
        self.portfolio = Portfolio(initial_cash)
        self.trade_quantity = trade_quantity
        self.equity_curve = []

    def run(self):
        """
        Run backtest over entire dataset.
        Automatically closes any open position at the end.
        """

        for idx in range(len(self.data)):
            signal = self.strategy.on_candle(idx, self.data, self.portfolio)
            self._handle_signal(signal, idx)
            self._update_equity(idx)

        # -------------------------------------------------
        # AUTO-CLOSE OPEN POSITION AT END OF BACKTEST
        # -------------------------------------------------
        if self.portfolio.position.is_open():
            last_idx = len(self.data) - 1
            last_price = self.data["close"][last_idx]
            last_ts = self.data["timestamp"][last_idx]

            self.portfolio.close_position(
                price=last_price,
                timestamp=last_ts,
            )

            # Update equity one final time after forced exit
            self._update_equity(last_idx)

        return pl.DataFrame(self.equity_curve)

    # -------------------------------------------------
    # Internal helpers
    # -------------------------------------------------
    def _handle_signal(self, signal, idx: int):
        """
        Execute trading signal.
        """
        if signal == "BUY" and not self.portfolio.position.is_open():
            price = self.data["close"][idx]
            timestamp = self.data["timestamp"][idx]

            self.portfolio.open_position(
                price=price,
                quantity=self.trade_quantity,
                timestamp=timestamp,
            )

        elif signal == "SELL" and self.portfolio.position.is_open():
            price = self.data["close"][idx]
            timestamp = self.data["timestamp"][idx]

            self.portfolio.close_position(
                price=price,
                timestamp=timestamp,
            )

    def _update_equity(self, idx: int):
        """
        Mark-to-market equity calculation.
        """
        price = self.data["close"][idx]
        timestamp = self.data["timestamp"][idx]

        equity = self.portfolio.cash

        if self.portfolio.position.is_open():
            equity += (
                self.portfolio.position.quantity
                * price
            )

        self.equity_curve.append({
            "timestamp": timestamp,
            "equity": equity,
        })
