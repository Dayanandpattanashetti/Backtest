# backtester/trade.py

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Trade:
    side: str          # "BUY" or "SELL"
    price: float
    quantity: int
    timestamp: datetime
