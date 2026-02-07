# dtos/candle_dataset_meta_dto.py
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class CandleDatasetMetaDTO:
    instrument_token: int
    exchange: str
    timeframe: str
    year: int
    start_date: date
    end_date: date
    parquet_path: str
    row_count: int
