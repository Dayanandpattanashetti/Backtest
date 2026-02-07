from typing import List
import zlib
import MetaTrader5 as mt5

from dtos.instrument_dto import InstrumentDTO


class MT5InstrumentsAdapter:
    """
    Fetches MT5 symbols and maps them to InstrumentDTO.
    """

    def __init__(self, auto_init: bool = True, terminal_path: str | None = None):
        self._initialized = False
        self._terminal_path = terminal_path
        if auto_init:
            self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        ok = mt5.initialize(path=self._terminal_path) if self._terminal_path else mt5.initialize()
        if not ok:
            code, message = mt5.last_error()
            raise RuntimeError(
                f"Failed to initialize MetaTrader5 (error {code}: {message})"
            )
        self._initialized = True

    def fetch_all(self) -> List[InstrumentDTO]:
        self._ensure_initialized()

        symbols = mt5.symbols_get()
        if symbols is None:
            raise RuntimeError("No symbols returned from MetaTrader5")

        instruments: List[InstrumentDTO] = []

        for s in symbols:
            # Use a deterministic 32-bit token for MT5 symbols.
            token = zlib.crc32(s.name.encode("utf-8"))

            instruments.append(
                InstrumentDTO(
                    instrument_token=token,
                    tradingsymbol=s.name,
                    exchange="FX",
                    instrument_type="FX",
                    name=getattr(s, "description", None),
                    source="MT5",
                )
            )

        return instruments

    def shutdown(self) -> None:
        mt5.shutdown()
        self._initialized = False
