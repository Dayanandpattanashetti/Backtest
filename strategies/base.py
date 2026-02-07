from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict
import polars as pl


@dataclass
class StrategyParameter:
    name: str
    type: type
    default: Any
    min: Any | None = None
    max: Any | None = None
    step: Any | None = None


class Strategy(ABC):
    """
    Base class for all strategies.
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Human-readable strategy name"""
        pass

    @classmethod
    def parameters(cls) -> Dict[str, StrategyParameter]:
        """
        Return parameter definitions.
        Override if strategy has parameters.
        """
        return {}

    @abstractmethod
    def on_candle(self, idx: int, data: pl.DataFrame, portfolio):
        pass
