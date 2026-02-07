import os
from datetime import date

import polars as pl

from dtos.candle_series_dto import CandleSeriesDTO
from dtos.data_request_dto import DataRequestDTO
from dtos.candle_dataset_meta_dto import CandleDatasetMetaDTO
from storage.path_resolver import PathResolver

class ParquetWriter:
    """
    Writes normalized candle data to yearly Parquet files.
    """

    def __init__(self, path_resolver: PathResolver):
        self.path_resolver = path_resolver

    def write(
        self,
        series: CandleSeriesDTO,
        request: DataRequestDTO
    ) -> CandleDatasetMetaDTO:
        """
        Writes candle data to a Parquet file and returns metadata.
        """

        if not series.candles:
            raise ValueError("Cannot write empty candle series")

        # Resolve path
        parquet_path = self.path_resolver.get_parquet_path(request)

        # Ensure directories exist
        os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

        # Convert candles to Polars DataFrame
        df = pl.DataFrame(
            {
                "timestamp": [c.timestamp for c in series.candles],
                "open": [c.open for c in series.candles],
                "high": [c.high for c in series.candles],
                "low": [c.low for c in series.candles],
                "close": [c.close for c in series.candles],
                "volume": [c.volume for c in series.candles],
                "spread": [c.spread for c in series.candles],
                "real_volume": [c.real_volume for c in series.candles],
            }
        )

        # Sort defensively
        df = df.sort("timestamp")

        # Write Parquet (overwrite if exists is intentional for snapshots)
        df.write_parquet(parquet_path)

        # Metadata derivation
        start_date = df.select(pl.col("timestamp").min()).item().date()
        end_date = df.select(pl.col("timestamp").max()).item().date()
        row_count = df.height

        return CandleDatasetMetaDTO(
            instrument_token=series.instrument_token,
            exchange=request.instrument.exchange,
            timeframe=request.timeframe.code,
            year=request.year,
            start_date=start_date,
            end_date=end_date,
            parquet_path=parquet_path,
            row_count=row_count,
        )
