# dtos/instrument_dto.py
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class InstrumentDTO:
    instrument_token: int
    tradingsymbol: str
    exchange: str          # NSE, BSE, BINANCE
    instrument_type: str   # EQ, FUT, OPT, CRYPTO
    name: Optional[str] = None
    source: Optional[str] = None
