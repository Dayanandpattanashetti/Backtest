# backtester/portfolio.py

from backtester.trade import Trade
from backtester.position import Position


class Portfolio:
    def __init__(self, initial_cash: float):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = Position()
        self.trades: list[Trade] = []

    # -------------------------------------------------
    # Position lifecycle
    # -------------------------------------------------
    def open_position(self, price: float, quantity: int, timestamp):
        """
        Open a long position.
        """
        if self.position.is_open():
            return

        cost = price * quantity
        if cost > self.cash:
            return

        self.cash -= cost
        self.position.open(price, quantity)

        self.trades.append(
            Trade(
                side="BUY",
                price=price,
                quantity=quantity,
                timestamp=timestamp,
            )
        )

    def close_position(self, price: float, timestamp):
        """
        Close the currently open position.
        """
        if not self.position.is_open():
            return

        quantity = self.position.quantity
        proceeds = price * quantity

        self.cash += proceeds
        self.position.close()

        self.trades.append(
            Trade(
                side="SELL",
                price=price,
                quantity=quantity,
                timestamp=timestamp,
            )
        )
