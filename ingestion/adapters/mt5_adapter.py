# ingestion/adapters/mt5_adapter.py
from datetime import datetime, date
from typing import List
import MetaTrader5 as mt5

from dtos.data_request_dto import DataRequestDTO
from dtos.raw_candle_dto import RawCandleDTO


class MT5Adapter:
    """
    Adapter for fetching historical Forex data from MetaTrader 5.
    """

    def __init__(self, auto_init: bool = True):
        self._initialized = False
        if auto_init:
            self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        if not mt5.initialize():
            raise RuntimeError("Failed to initialize MetaTrader5")
        self._initialized = True

    def fetch_yearly_candles(
        self,
        request: DataRequestDTO
    ) -> List[RawCandleDTO]:
        symbol = request.instrument.tradingsymbol
        timeframe = self._map_timeframe(request.timeframe.code)

        self._ensure_initialized()

        start = datetime(request.year, 1, 1)
        end = datetime(request.year, 12, 31)

        rates = mt5.copy_rates_range(
            symbol,
            timeframe,
            start,
            end
        )

        if rates is None:
            raise RuntimeError(f"No data returned for {symbol}")

        candles: List[RawCandleDTO] = []
        has_spread = "spread" in rates.dtype.names
        has_real_volume = "real_volume" in rates.dtype.names

        for r in rates:
            spread = int(r["spread"]) if has_spread and r["spread"] is not None else None
            real_volume = (
                int(r["real_volume"])
                if has_real_volume and r["real_volume"] is not None
                else None
            )

            candles.append(
                RawCandleDTO(
                    timestamp=datetime.fromtimestamp(r["time"]),
                    open=r["open"],
                    high=r["high"],
                    low=r["low"],
                    close=r["close"],
                    volume=int(r["tick_volume"]),
                    spread=spread,
                    real_volume=real_volume,
                )
            )

        return candles

    def shutdown(self):
        mt5.shutdown()
        self._initialized = False

    @staticmethod
    def _map_timeframe(tf: str):
        mapping = {
            "1m": mt5.TIMEFRAME_M1,
            "5m": mt5.TIMEFRAME_M5,
            "15m": mt5.TIMEFRAME_M15,
            "30m": mt5.TIMEFRAME_M30,
            "1h": mt5.TIMEFRAME_H1,
            "60m": mt5.TIMEFRAME_H1,
            "1d": mt5.TIMEFRAME_D1,
            "day": mt5.TIMEFRAME_D1,
        }
        if tf not in mapping:
            raise ValueError(f"Unsupported timeframe: {tf}")
        return mapping[tf]
