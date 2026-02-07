import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

from metadata.instruments_repo import InstrumentsRepository
from metadata.candle_datasets_repo import CandleDatasetRepository
from data_access.parquet_reader import ParquetReader
from data_access.data_loader import DataLoader

from app_services.ingestion_service import IngestionService
from app_services.data_service import DataService
from app_services.backtest_service import BacktestService

from ui.sidebar import render_sidebar
from ui.views.metrics_view import render_metrics
from ui.views.trades_view import render_trades
from ui.views.pnl_view import render_pnl_chart

from ingestion.ingest_manager import IngestionManager
from ingestion.normalizer import CandleNormalizer
from ingestion.adapters.zerodha_adapter import ZerodhaAdapter
from ingestion.adapters.mt5_adapter import MT5Adapter
from storage.parquet_writer import ParquetWriter
from storage.path_resolver import PathResolver
from config.settings import BASE_DATA_DIR

st.set_page_config("Backtesting Platform", layout="wide")
st.title("Backtesting Platform")

# -------------------------------
# Session guards
# -------------------------------
if "run_backtest" not in st.session_state:
    st.session_state.run_backtest = False

# -------------------------------
# Infra wiring
# -------------------------------
path_resolver = PathResolver(BASE_DATA_DIR)

ingestion_manager = IngestionManager(
    CandleDatasetRepository(),
    {
        "ZERODHA": ZerodhaAdapter(os.getenv("API_KEY"), os.getenv("ACCESS_TOKEN")),
        "MT5": MT5Adapter(auto_init=False),
    },
    CandleNormalizer(),
    ParquetWriter(path_resolver),
    default_source="ZERODHA",
)

ingestion_service = IngestionService(ingestion_manager)

data_service = DataService(
    DataLoader(CandleDatasetRepository(), ParquetReader())
)

backtest_service = BacktestService()

# -------------------------------
# Sidebar
# -------------------------------
state = render_sidebar(InstrumentsRepository())

# -------------------------------
# Fetch data
# -------------------------------
if state["fetch"]:
    if not state["instrument"]:
        st.warning("Select an instrument first")
        st.stop()

    with st.spinner("Fetching candlestick data..."):
        results = ingestion_service.fetch_candles(
            state["instrument"],
            state["timeframe"],
            state["start"].year,
            state["end"].year,
        )

    for r in results:
        st.success(f"{r['year']} processed")

    st.stop()

# -------------------------------
# Run backtest (ONE SHOT)
# -------------------------------
if state["run"]:
    st.session_state.run_backtest = True

if st.session_state.run_backtest:
    st.session_state.run_backtest = False

    try:
        data = data_service.load(
            state["instrument"],
            state["timeframe"],
            state["start"],
            state["end"],
        )
    except RuntimeError as e:
        st.error(str(e))
        st.info("⬇ Fetch candlestick data before running backtest.")
        st.stop()

    strategy = state["strategy_cls"](**state["strategy_params"])

    result = backtest_service.run(
        data,
        strategy,
        state["cash"],
        state["qty"],
    )

    trades = result["trades"]
    metrics = result["metrics"]

    total_pnl = sum(
        (t.price * t.quantity if t.side == "SELL" else -t.price * t.quantity)
        for t in trades
    )

    render_metrics(metrics, state["cash"], total_pnl)
    completed = render_trades(trades)
    render_pnl_chart(completed)
