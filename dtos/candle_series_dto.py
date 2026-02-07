# dtos/candle_series_dto.py
from dataclasses import dataclass
from dtos.raw_candle_dto import RawCandleDTO

@dataclass
class CandleSeriesDTO:
    instrument_token: int
    timeframe: str
    candles: list[RawCandleDTO]
