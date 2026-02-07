# dtos/raw_candle_dto.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class RawCandleDTO:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

    spread: Optional[int] = None
    real_volume: Optional[int] = None