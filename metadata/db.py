import sqlite3
from contextlib import contextmanager
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "trading_data.db"
_SCHEMA_CHECKED = False

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    _ensure_schema(conn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Create instruments and candle_datasets tables with indexes"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Instruments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instruments (
                instrument_token INTEGER PRIMARY KEY,
                tradingsymbol TEXT NOT NULL,
                exchange TEXT NOT NULL,
                instrument_type TEXT NOT NULL,
                name TEXT,
                source TEXT
            )
        ''')
        
        # Indexes for instruments
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_instruments_symbol ON instruments (tradingsymbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_instruments_exchange ON instruments (exchange)')

        
        
        # Candle datasets table (metadata for parquet files)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candle_datasets (
                instrument_token INTEGER NOT NULL,
                exchange TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                year INTEGER NOT NULL CHECK (year >= 2000 AND year <= 2100),
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                parquet_path TEXT NOT NULL CHECK (length(parquet_path) > 0),
                row_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (instrument_token, timeframe, year),
                FOREIGN KEY (instrument_token) REFERENCES instruments (instrument_token)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candle_datasets_lookup ON candle_datasets (instrument_token, timeframe, year);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candle_datasets_timeframe ON candle_datasets (timeframe, year);')
        
        conn.commit()
        print("✅ Tables and indexes created")

def _ensure_schema(conn: sqlite3.Connection) -> None:
    global _SCHEMA_CHECKED
    if _SCHEMA_CHECKED:
        return

    _SCHEMA_CHECKED = True

    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='instruments'"
    )
    if cursor.fetchone() is None:
        return

    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(instruments)")
    }

    if "name" not in columns:
        conn.execute("ALTER TABLE instruments ADD COLUMN name TEXT")

    if "source" not in columns:
        conn.execute("ALTER TABLE instruments ADD COLUMN source TEXT")


# if __name__ == "__main__":
#     init_database()
