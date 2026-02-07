# backtester/strategy_base.py

from abc import ABC, abstractmethod
from typing import Optional
import polars as pl

class Strategy(ABC):
    """
    Base class for all strategies.
    """

    @abstractmethod
    def on_candle(
        self,
        idx: int,
        data: pl.DataFrame,
        portfolio,
    ) -> Optional[str]:
        """
        Called on every candle.

        Return:
            'BUY', 'SELL', or None
        """
        pass
