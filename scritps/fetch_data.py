"""
Script to fetch historical data for a specific instrument and store in parquet files.

Usage:
    python scritps/fetch_data.py RELIANCE NSE 5m 2024
"""

import sys
from datetime import date

from config.settings import BASE_DATA_DIR
from dtos.instrument_dto import InstrumentDTO
from dtos.timeframe_dto import TimeframeDTO
from dtos.data_request_dto import DataRequestDTO

from metadata.instruments_repo import InstrumentsRepository
from metadata.candle_datasets_repo import CandleDatasetRepository
from ingestion.adapters.zerodha_adapter import ZerodhaAdapter
from ingestion.adapters.mt5_adapter import MT5Adapter
from ingestion.normalizer import CandleNormalizer
from ingestion.ingest_manager import IngestionManager
from storage.path_resolver import PathResolver
from storage.parquet_writer import ParquetWriter


def main():
    if len(sys.argv) < 5:
        print("Usage: python scritps/fetch_data.py <SYMBOL> <EXCHANGE> <TIMEFRAME> <YEAR>")
        print("Example: python scritps/fetch_data.py RELIANCE NSE 5m 2024")
        sys.exit(1)
    
    symbol = sys.argv[1]
    exchange = sys.argv[2]
    timeframe_code = sys.argv[3]
    year = int(sys.argv[4])
    
    # Parse timeframe
    timeframe_map = {
        "1m": TimeframeDTO(code="1m", minutes=1),
        "5m": TimeframeDTO(code="5m", minutes=5),
        "15m": TimeframeDTO(code="15m", minutes=15),
        "30m": TimeframeDTO(code="30m", minutes=30),
        "60m": TimeframeDTO(code="60m", minutes=60),
        "day": TimeframeDTO(code="day", minutes=1440),
    }
    
    if timeframe_code not in timeframe_map:
        print(f"Invalid timeframe. Choose from: {list(timeframe_map.keys())}")
        sys.exit(1)
    
    timeframe = timeframe_map[timeframe_code]
    
    # Find instrument
    print(f"Searching for {symbol} on {exchange}...")
    instruments_repo = InstrumentsRepository()
    results = instruments_repo.search(query=symbol, exchange=exchange, limit=10)
    
    if not results:
        print(f"Instrument {symbol} not found on {exchange}")
        print("Run: python scritps/sync_instruments.py first")
        sys.exit(1)
    
    # Find exact match
    instrument = None
    for inst in results:
        if inst.tradingsymbol == symbol and inst.exchange == exchange:
            instrument = inst
            break
    
    if not instrument:
        print(f"Exact match not found. Available:")
        for inst in results[:5]:
            print(f"  - {inst.tradingsymbol} ({inst.exchange})")
        sys.exit(1)
    
    print(f"✓ Found: {instrument.tradingsymbol} (Token: {instrument.instrument_token})")
    
    # Create request
    request = DataRequestDTO(
        instrument=instrument,
        timeframe=timeframe,
        year=year,
        source="ZERODHA",
    )
    
    # Initialize components
    print(f"\nInitializing ingestion pipeline...")
    metadata_repo = CandleDatasetRepository()
    adapter = ZerodhaAdapter()
    normalizer = CandleNormalizer()
    path_resolver = PathResolver(base_data_dir=BASE_DATA_DIR)
    parquet_writer = ParquetWriter(path_resolver=path_resolver)
    
    ingest_manager = IngestionManager(
        metadata_repo=metadata_repo,
        adapters={
            "ZERODHA": adapter,
            "MT5": MT5Adapter(),
        },
        normalizer=normalizer,
        parquet_writer=parquet_writer
    )
    
    # Run ingestion
    print(f"\nFetching {year} data for {symbol} ({timeframe_code})...")
    try:
        meta, report = ingest_manager.ingest(request)
        
        print(f"\n✓ Ingestion complete!")
        print(f"\nMetadata:")
        print(f"  File: {meta.parquet_path}")
        print(f"  Rows: {meta.row_count}")
        print(f"  Date Range: {meta.start_date} to {meta.end_date}")
        
        print(f"\nNormalization Report:")
        print(f"  Raw candles: {report.total_raw_candles}")
        print(f"  Clean candles: {report.total_clean_candles}")
        print(f"  Removed duplicates: {report.removed_duplicates}")
        print(f"  Removed invalid: {report.removed_invalid_ohlc}")
        
    except Exception as e:
        print(f"\n✗ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
