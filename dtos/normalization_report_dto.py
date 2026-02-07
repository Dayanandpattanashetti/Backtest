# dtos/normalization_report_dto.py
from dataclasses import dataclass
from typing import List

@dataclass
class NormalizationReportDTO:
    total_raw_candles: int
    total_clean_candles: int

    removed_duplicates: int
    removed_out_of_year: int
    removed_invalid_ohlc: int

    was_sorted: bool

    notes: List[str]
