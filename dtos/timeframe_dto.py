# dtos/timeframe_dto.py
from dataclasses import dataclass

@dataclass(frozen=True)
class TimeframeDTO:
    code: str              # '1m', '5m', '15m'
    minutes: int           # 1, 5, 15
