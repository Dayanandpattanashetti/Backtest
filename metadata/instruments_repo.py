# metadata/instruments_repo.py

from typing import List
from dtos.instrument_dto import InstrumentDTO
from metadata.db import get_db_connection


class InstrumentsRepository:
    """
    Repository for instrument master data.
    """

    def bulk_upsert(self, instruments: List[InstrumentDTO]) -> None:
        query = """
            INSERT INTO instruments (
                instrument_token,
                tradingsymbol,
                exchange,
                instrument_type,
                name,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(instrument_token)
            DO UPDATE SET
                tradingsymbol = excluded.tradingsymbol,
                exchange = excluded.exchange,
                instrument_type = excluded.instrument_type,
                name = excluded.name,
                source = excluded.source
        """

        with get_db_connection() as conn:
            conn.executemany(
                query,
                [
                    (
                        i.instrument_token,
                        i.tradingsymbol,
                        i.exchange,
                        i.instrument_type,
                        i.name,
                        i.source,
                    )
                    for i in instruments
                ],
            )

    def search(
        self,
        query: str,
        exchange: str | None = None,
        instrument_type: str | None = None,
        limit: int = 50,
    ) -> List[InstrumentDTO]:

        sql = """
            SELECT instrument_token, tradingsymbol, exchange, instrument_type, name, source
            FROM instruments
            WHERE tradingsymbol LIKE ?
        """
        params = [f"%{query.upper()}%"]

        if exchange:
            sql += " AND exchange = ?"
            params.append(exchange)

        if instrument_type:
            sql += " AND instrument_type = ?"
            params.append(instrument_type)

        sql += " ORDER BY tradingsymbol LIMIT ?"
        params.append(limit)

        with get_db_connection() as conn:
            rows = conn.execute(sql, params).fetchall()

            return [
                InstrumentDTO(
                    instrument_token=row["instrument_token"],
                    tradingsymbol=row["tradingsymbol"],
                    exchange=row["exchange"],
                    instrument_type=row["instrument_type"],
                    name=row["name"],
                    source=row["source"],
                )
                for row in rows
            ]
