# ingestion/adapters/zerodha_instruments_adapter.py

from typing import List
from kiteconnect import KiteConnect
from dtos.instrument_dto import InstrumentDTO
from api_tracker import api_tracker


class ZerodhaInstrumentsAdapter:
    """
    Fetches full instrument master from Zerodha.
    """

    def __init__(self, api_key: str, access_token: str):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        
        # Validate token
        try:
            self.kite.profile()
        except Exception as e:
            if "Incorrect api_key or access_token" in str(e):
                raise ValueError(
                    "Invalid or expired access token. Please update ACCESS_TOKEN in .env file.\n"
                    "Get a fresh token from: https://developers.kite.trade/apps"
                )
            raise

    def fetch_all(self) -> List[InstrumentDTO]:
        instruments = self.kite.instruments()
        
        # Track API call
        api_tracker.log_call('instruments', response_count=len(instruments))

        results: List[InstrumentDTO] = []

        for inst in instruments:
            # Filter only tradable instruments
            if inst["instrument_token"] is None:
                continue

            results.append(
                InstrumentDTO(
                    instrument_token=inst["instrument_token"],
                    tradingsymbol=inst["tradingsymbol"],
                    exchange=inst["exchange"],
                    instrument_type=inst["instrument_type"],
                    name=inst.get("name"),
                    source="ZERODHA",
                )
            )

        return results
