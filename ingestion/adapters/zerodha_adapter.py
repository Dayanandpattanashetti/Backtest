# ingestion/adapters/zerodha_adapter.py

from datetime import datetime, timedelta, date
from typing import List
import os
from dotenv import load_dotenv

from kiteconnect import KiteConnect

from dtos.data_request_dto import DataRequestDTO
from dtos.raw_candle_dto import RawCandleDTO
from api_tracker import api_tracker

# Load .env file
load_dotenv()

class ZerodhaAdapter:
    """
    Adapter for fetching historical candle data from Zerodha Kite Connect.
    """

    MAX_DAYS_PER_REQUEST = 60  # Zerodha limit

    def __init__(self, api_key: str = None, access_token: str = None):
        self.api_key = api_key or os.getenv('API_KEY')
        self.access_token = access_token or os.getenv('ACCESS_TOKEN')
        
        if not self.api_key or not self.access_token:
            raise ValueError("API_KEY and ACCESS_TOKEN must be set in .env file")
        
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)


    def fetch_yearly_candles(
        self,
        request: DataRequestDTO
    ) -> List[RawCandleDTO]:
        """
        Fetches one full year of candle data for the given request.
        """

        start = date(request.year, 1, 1)
        end = date(request.year, 12, 31)

        return self._fetch_range(
            instrument_token=request.instrument.instrument_token,
            timeframe=request.timeframe.code,
            start_date=start,
            end_date=end,
        )
        
    def _fetch_range(
        self,
        instrument_token: int,
        timeframe: str,
        start_date: date,
        end_date: date,
    ) -> List[RawCandleDTO]:

        all_candles: List[RawCandleDTO] = []

        # Convert timeframe to Zerodha API format
        api_timeframe_map = {
            "1m": "minute",
            "5m": "5minute", 
            "15m": "15minute",
            "30m": "30minute",
            "60m": "60minute",
            "day": "day"
        }
        
        api_timeframe = api_timeframe_map.get(timeframe, timeframe)

        current_start = start_date

        while current_start <= end_date:
            current_end = min(
                current_start + timedelta(days=self.MAX_DAYS_PER_REQUEST),
                end_date
            )

            candles = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=current_start,
                to_date=current_end,
                interval=api_timeframe,
                continuous=False,
                oi=False,
            )
            
            # Track API call
            api_tracker.log_call(
                'historical_data',
                {
                    'instrument_token': instrument_token,
                    'from_date': str(current_start),
                    'to_date': str(current_end),
                    'interval': api_timeframe
                },
                len(candles)
            )

            for c in candles:
                all_candles.append(
                    RawCandleDTO(
                        timestamp=c["date"],
                        open=c["open"],
                        high=c["high"],
                        low=c["low"],
                        close=c["close"],
                        volume=c["volume"],
                    )
                )

            current_start = current_end + timedelta(days=1)

        return all_candles

