# ingestion/normalizer.py

from typing import List
from datetime import datetime

from dtos.raw_candle_dto import RawCandleDTO
from dtos.candle_series_dto import CandleSeriesDTO
from dtos.data_request_dto import DataRequestDTO
from dtos.normalization_report_dto import NormalizationReportDTO

# ingestion/normalizer.py

from typing import List
from datetime import datetime

from dtos.raw_candle_dto import RawCandleDTO
from dtos.candle_series_dto import CandleSeriesDTO
from dtos.data_request_dto import DataRequestDTO
from dtos.normalization_report_dto import NormalizationReportDTO

class CandleNormalizer:
    """
    Normalizes raw candle data with full transparency.
    Timezone is preserved as-is.
    """

    def normalize(
        self,
        raw_candles: List[RawCandleDTO],
        request: DataRequestDTO
    ) -> tuple[CandleSeriesDTO, NormalizationReportDTO]:

        notes: List[str] = []
        total_raw = len(raw_candles)
        sorted_candles = sorted(raw_candles, key=lambda c: c.timestamp)
        was_sorted = sorted_candles != raw_candles
        if was_sorted:
            notes.append("Candles were sorted by timestamp")
            
        unique_candles = []
        seen_timestamps = set()
        removed_duplicates = 0

        for c in sorted_candles:
            if c.timestamp in seen_timestamps:
                removed_duplicates += 1
                continue
            seen_timestamps.add(c.timestamp)
            unique_candles.append(c)

        if removed_duplicates > 0:
            notes.append(f"Removed {removed_duplicates} duplicate timestamps")


        year = request.year
        in_year_candles = []
        removed_out_of_year = 0

        for c in unique_candles:
            if c.timestamp.year != year:
                removed_out_of_year += 1
                continue
            in_year_candles.append(c)

        if removed_out_of_year > 0:
            notes.append(f"Removed {removed_out_of_year} candles outside year {year}")
            
        clean_candles = []
        removed_invalid_ohlc = 0

        for c in in_year_candles:
            if (
                c.high < max(c.open, c.close)
                or c.low > min(c.open, c.close)
                or c.volume < 0
            ):
                removed_invalid_ohlc += 1
                continue

            clean_candles.append(c)

        if removed_invalid_ohlc > 0:
            notes.append(f"Removed {removed_invalid_ohlc} candles with invalid OHLC")
            
        series = CandleSeriesDTO(
            instrument_token=request.instrument.instrument_token,
            timeframe=request.timeframe.code,
            candles=clean_candles,
        )

        report = NormalizationReportDTO(
            total_raw_candles=total_raw,
            total_clean_candles=len(clean_candles),
            removed_duplicates=removed_duplicates,
            removed_out_of_year=removed_out_of_year,
            removed_invalid_ohlc=removed_invalid_ohlc,
            was_sorted=was_sorted,
            notes=notes,
        )

        return series, report


