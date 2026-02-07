import streamlit as st
import pandas as pd


def render_pnl_chart(completed_trades):
    if not completed_trades:
        st.info("No trades to plot P&L")
        return

    rows = [{
        "timestamp": pd.to_datetime(t["Exit Time"]),
        "pnl": t["PnL"],
    } for t in completed_trades]

    df = pd.DataFrame(rows).set_index("timestamp").sort_index()

    freq = st.selectbox("PnL View", ["Daily", "Weekly", "Monthly"])

    rule = {"Daily": "D", "Weekly": "W", "Monthly": "M"}[freq]
    ts = df.resample(rule).sum()

    st.subheader("Profit & Loss Over Time")
    st.line_chart(ts, y="pnl", height=280)

    st.subheader("Cumulative P&L")
    st.line_chart(ts.cumsum(), y="pnl", height=280)
