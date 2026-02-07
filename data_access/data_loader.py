# data_access/data_loader.py

from datetime import date
from typing import Optional, List

import polars as pl
from dtos.data_request_dto import DataRequestDTO
from dtos.instrument_dto import InstrumentDTO
from dtos.timeframe_dto import TimeframeDTO
from metadata.candle_datasets_repo import CandleDatasetRepository
from data_access.parquet_reader import ParquetReader
class DataLoader:
    """
    High-level loader for candle data.
    Uses metadata + parquet files.
    """

    def __init__(
        self,
        metadata_repo: CandleDatasetRepository,
        parquet_reader: ParquetReader,
    ):
        self.metadata_repo = metadata_repo
        self.parquet_reader = parquet_reader
        
    def load(
        self,
        instrument: InstrumentDTO,
        timeframe: TimeframeDTO,
        start_date: date,
        end_date: date,
    ) -> pl.DataFrame:
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

        years = list(range(start_date.year, end_date.year + 1))
        dataframes: List[pl.DataFrame] = []

        for year in years:
            request_like = self._request_stub(instrument, timeframe, year)

            meta = self.metadata_repo.get(request_like)
            if meta is None:
                raise RuntimeError(
                    f"Missing dataset for {instrument.tradingsymbol}, "
                    f"{timeframe.code}, {year}"
                )

            df = self.parquet_reader.read(
                parquet_path=meta.parquet_path,
                start_date=start_date,
                end_date=end_date,
            )

            if df.height > 0:
                dataframes.append(df)

        if not dataframes:
            raise RuntimeError("No candle data loaded")

        # Concatenate & final sort
        final_df = pl.concat(dataframes, how="diagonal").sort("timestamp")

        return final_df

    def _request_stub(
        self,
        instrument: InstrumentDTO,
        timeframe: TimeframeDTO,
        year: int,
    ):

        return DataRequestDTO(
            instrument=instrument,
            timeframe=timeframe,
            year=year,
            source="LOCAL",
        )
