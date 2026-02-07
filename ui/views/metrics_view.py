import streamlit as st


def render_metrics(metrics, initial_cash, total_pnl):
    final_capital = initial_cash + total_pnl

    st.subheader("Performance Metrics")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Return (%)", f"{metrics.total_return_pct:.2f}")
    c2.metric("CAGR (%)", f"{metrics.cagr_pct:.2f}")
    c3.metric("Max Drawdown (%)", f"{metrics.max_drawdown_pct:.2f}")
    c4.metric("Sharpe Ratio", f"{metrics.sharpe_ratio:.2f}")

    c5, c6, c7 = st.columns(3)
    c5.metric("Initial Capital", f"{initial_cash:,.0f}")
    c6.metric("Final Capital", f"{final_capital:,.0f}")
    c7.metric("Net P&L", f"{total_pnl:,.0f}")
