# data_access/parquet_reader.py

import os
import polars as pl
from datetime import date
from typing import Optional

class ParquetReader:
    """
    Low-level reader for Parquet candle files.
    """

    def read(
        self,
        parquet_path: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> pl.DataFrame:
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

        df = pl.read_parquet(parquet_path)

        # Defensive sort (cheap, safe)
        df = df.sort("timestamp")

        # Optional date filtering
        if start_date:
            df = df.filter(pl.col("timestamp") >= start_date)
        if end_date:
            df = df.filter(pl.col("timestamp") <= end_date)

        return df
