# backtester/position.py

class Position:
    def __init__(self):
        self.entry_price: float | None = None
        self.quantity: int = 0

    def open(self, price: float, quantity: int):
        self.entry_price = price
        self.quantity = quantity

    def close(self):
        self.entry_price = None
        self.quantity = 0

    def is_open(self) -> bool:
        return self.entry_price is not None
