import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.adapters.zerodha_instruments_adapter import ZerodhaInstrumentsAdapter
from ingestion.adapters.mt5_instruments_adapter import MT5InstrumentsAdapter
from metadata.instruments_repo import InstrumentsRepository


def _usage():
    print("Usage: python scritps/sync_instruments.py [ZERODHA|MT5]")
    print("Example: python scritps/sync_instruments.py ZERODHA")
    print("Example: python scritps/sync_instruments.py MT5")


def main():
    source = sys.argv[1].upper() if len(sys.argv) > 1 else "ZERODHA"

    repo = InstrumentsRepository()

    if source == "ZERODHA":
        api_key = os.environ.get("API_KEY")
        access_token = os.environ.get("ACCESS_TOKEN")
        if not api_key or not access_token:
            raise ValueError("API_KEY and ACCESS_TOKEN must be set in .env file")
        adapter = ZerodhaInstrumentsAdapter(api_key, access_token)
    elif source == "MT5":
        mt5_path = os.environ.get("MT5_PATH")
        adapter = MT5InstrumentsAdapter(terminal_path=mt5_path)
    else:
        _usage()
        sys.exit(1)

    instruments = adapter.fetch_all()
    repo.bulk_upsert(instruments)

    print(f"Synced {len(instruments)} instruments from {source}")


if __name__ == "__main__":
    main()
