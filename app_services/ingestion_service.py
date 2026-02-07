from ingestion.ingest_manager import IngestionManager
from dtos.data_request_dto import DataRequestDTO


class IngestionService:
    def __init__(self, ingestion_manager: IngestionManager):
        self.ingestion_manager = ingestion_manager

    def _resolve_source(self, instrument, source: str | None) -> str:
        if source:
            return source

        exchange = (instrument.exchange or "").upper()
        if exchange in {"NSE", "BSE", "NFO"}:
            return "ZERODHA"
        if exchange in {"FX", "FOREX", "MT5"}:
            return "MT5"

        raise ValueError(
            f"Unable to resolve data source for exchange: {instrument.exchange}"
        )

    def fetch_candles(
        self,
        instrument,
        timeframe,
        start_year: int,
        end_year: int,
        source: str | None = None,
    ):
        results = []
        resolved_source = self._resolve_source(instrument, source)

        for year in range(start_year, end_year + 1):
            request = DataRequestDTO(
                instrument=instrument,
                timeframe=timeframe,
                year=year,
                source=resolved_source,
            )

            meta, report = self.ingestion_manager.ingest(request)

            results.append({
                "year": year,
                "rows": meta.row_count if meta else 0,
                "notes": report.notes,
            })

        return results
