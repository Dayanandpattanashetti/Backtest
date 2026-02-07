from typing import Optional
from dtos.data_request_dto import DataRequestDTO
from dtos.candle_dataset_meta_dto import CandleDatasetMetaDTO
from metadata.db import get_db_connection

class CandleDatasetRepository:
    """
    Repository for candle dataset metadata.
    Handles persistence and retrieval of CandleDatasetMetaDTO.
    """

    def exists(self, request: DataRequestDTO) -> bool:
        query = """
            SELECT 1
            FROM candle_datasets
            WHERE instrument_token = ?
              AND timeframe = ?
              AND year = ?
        """
        with get_db_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    request.instrument.instrument_token,
                    request.timeframe.code,
                    request.year,
                ),
            )
            return cursor.fetchone() is not None
        
    def get(self, request: DataRequestDTO) -> Optional[CandleDatasetMetaDTO]:
        query = """
            SELECT
                instrument_token,
                exchange,
                timeframe,
                year,
                start_date,
                end_date,
                parquet_path,
                row_count
            FROM candle_datasets
            WHERE instrument_token = ?
              AND timeframe = ?
              AND year = ?
        """

        with get_db_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    request.instrument.instrument_token,
                    request.timeframe.code,
                    request.year,
                ),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return CandleDatasetMetaDTO(
                instrument_token=row["instrument_token"],
                exchange=row["exchange"],
                timeframe=row["timeframe"],
                year=row["year"],
                start_date=row["start_date"],
                end_date=row["end_date"],
                parquet_path=row["parquet_path"],
                row_count=row["row_count"],
            )
            
    def save(self, meta: CandleDatasetMetaDTO) -> None:
        query = """
            INSERT INTO candle_datasets (
                instrument_token,
                exchange,
                timeframe,
                year,
                start_date,
                end_date,
                parquet_path,
                row_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        with get_db_connection() as conn:
            conn.execute(
                query,
                (
                    meta.instrument_token,
                    meta.exchange,
                    meta.timeframe,
                    meta.year,
                    meta.start_date,
                    meta.end_date,
                    meta.parquet_path,
                    meta.row_count,
                ),
            )


