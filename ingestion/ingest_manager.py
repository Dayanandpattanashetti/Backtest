# ingestion/ingest_manager.py

from typing import Mapping, Protocol

from dtos.data_request_dto import DataRequestDTO
from dtos.candle_dataset_meta_dto import CandleDatasetMetaDTO
from dtos.normalization_report_dto import NormalizationReportDTO
from dtos.raw_candle_dto import RawCandleDTO

from metadata.candle_datasets_repo import CandleDatasetRepository
from ingestion.normalizer import CandleNormalizer
from storage.parquet_writer import ParquetWriter


class CandleAdapter(Protocol):
    def fetch_yearly_candles(self, request: DataRequestDTO) -> list[RawCandleDTO]:
        ...

class IngestionManager:
    """
    Orchestrates data ingestion:
    - checks metadata
    - fetches raw data
    - normalizes data
    - writes parquet
    - saves metadata
    """

    def __init__(
        self,
        metadata_repo: CandleDatasetRepository,
        adapters: Mapping[str, CandleAdapter],
        normalizer: CandleNormalizer,
        parquet_writer: ParquetWriter,
        default_source: str | None = None,
    ):
        self.metadata_repo = metadata_repo
        self.adapters = adapters
        self.normalizer = normalizer
        self.parquet_writer = parquet_writer
        self.default_source = default_source


    def ingest(
        self,
        request: DataRequestDTO
    ) -> tuple[CandleDatasetMetaDTO, NormalizationReportDTO]:
        """
        Executes one full ingestion cycle for the given request.
        """

        # 1. Check metadata (snapshot rule)
        if self.metadata_repo.exists(request):
            meta = self.metadata_repo.get(request)
            if meta is None:
                raise RuntimeError("Metadata exists but could not be retrieved")
            return meta, NormalizationReportDTO(
                total_raw_candles=0,
                total_clean_candles=0,
                removed_duplicates=0,
                removed_out_of_year=0,
                removed_invalid_ohlc=0,
                was_sorted=False,
                notes=["Dataset already exists. Ingestion skipped."],
            )

        # 2. Select adapter by source
        source = request.source or self.default_source
        if not source:
            raise ValueError("DataRequestDTO.source is required to select adapter")

        adapter = self.adapters.get(source)
        if adapter is None:
            raise ValueError(f"No adapter configured for source: {source}")

        # 3. Fetch raw candles
        raw_candles = adapter.fetch_yearly_candles(request)

        if not raw_candles:
            raise RuntimeError("No candle data fetched from source")

        # 4. Normalize candles (with audit)
        series, report = self.normalizer.normalize(raw_candles, request)

        if not series.candles:
            raise RuntimeError("All candles were removed during normalization")

        # 5. Write Parquet and get metadata DTO
        meta = self.parquet_writer.write(series, request)

        # 6. Persist metadata
        self.metadata_repo.save(meta)

        return meta, report
