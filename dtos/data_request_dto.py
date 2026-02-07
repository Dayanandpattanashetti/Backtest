# dtos/data_request_dto.py
from dataclasses import dataclass
from dtos.instrument_dto import InstrumentDTO
from dtos.timeframe_dto import TimeframeDTO

@dataclass(frozen=True)
class DataRequestDTO:
    instrument: InstrumentDTO
    timeframe: TimeframeDTO
    year: int
    source: str            # 'ZERODHA' | 'MT5'
