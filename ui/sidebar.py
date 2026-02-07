import os
import streamlit as st
from datetime import date
from dtos.timeframe_dto import TimeframeDTO
from strategies.registry import discover_strategies


@st.cache_resource
def load_strategies():
    return discover_strategies()


def render_sidebar(instrument_repo):
    st.sidebar.header("Instrument Selection")

    search = st.sidebar.text_input("Search Instrument", "")
    exchange = st.sidebar.selectbox("Exchange", ["", "NSE", "BSE", "NFO", "FX"])
    inst_type = st.sidebar.selectbox("Instrument Type", ["", "EQ", "FUT", "OPT", "FX"])

    selected_instrument = None
    if search:
        results = instrument_repo.search(
            query=search,
            exchange=exchange or None,
            instrument_type=inst_type or None,
        )
        if results:
            labels = [
                f"{i.tradingsymbol} ({i.exchange}, {i.instrument_type})"
                for i in results
            ]
            choice = st.sidebar.selectbox("Select Instrument", labels)
            selected_instrument = results[labels.index(choice)]

    st.sidebar.header("Backtest Settings")

    TF_1M = TimeframeDTO("1m", 1)
    TF_5M = TimeframeDTO("5m", 5)
    TF_15M = TimeframeDTO("15m", 15)
    TF_30M = TimeframeDTO("30m", 30)
    TF_60M = TimeframeDTO("60m", 60)
    TF_1D = TimeframeDTO("day", 1440)

    timeframe = st.sidebar.selectbox(
        "Timeframe",
        [TF_1M, TF_5M, TF_15M, TF_30M, TF_60M, TF_1D],
        format_func=lambda tf: tf.code,
    )

    default_start = os.getenv("DEFAULT_START_DATE", "2005-01-01")
    default_end = os.getenv("DEFAULT_END_DATE", "2025-12-31")

    start_date = st.sidebar.date_input("Start Date", date.fromisoformat(default_start))
    end_date = st.sidebar.date_input("End Date", date.fromisoformat(default_end))

    initial_cash = st.sidebar.number_input(
        "Initial Capital", min_value=10_000, step=10_000, value=100_000
    )

    quantity = st.sidebar.number_input(
        "Trade Quantity", min_value=1, step=1, value=1
    )

    st.sidebar.header("Strategy")

    strategies = load_strategies()
    strat_name = st.sidebar.selectbox("Select Strategy", list(strategies.keys()))
    strat_cls = strategies[strat_name]

    params = {}
    for key, param in strat_cls.parameters().items():
        params[key] = st.sidebar.number_input(
            param.name,
            value=param.default,
            min_value=param.min,
            max_value=param.max,
            step=param.step or 1,
        )

    st.sidebar.header("Actions")

    fetch = st.sidebar.button("⬇ Fetch Candles")
    run = st.sidebar.button("▶ Run Backtest")

    return {
        "instrument": selected_instrument,
        "timeframe": timeframe,
        "start": start_date,
        "end": end_date,
        "cash": initial_cash,
        "qty": quantity,
        "strategy_cls": strat_cls,
        "strategy_params": params,
        "fetch": fetch,
        "run": run,
    }
