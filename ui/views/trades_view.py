import streamlit as st

MAX_ROWS = 1000


def render_trades(trades):
    completed = []
    open_trade = None

    for t in trades:
        if t.side == "BUY":
            open_trade = t
        elif t.side == "SELL" and open_trade:
            pnl = (t.price - open_trade.price) * t.quantity
            completed.append({
                "Entry Time": open_trade.timestamp,
                "Exit Time": t.timestamp,
                "Entry Price": open_trade.price,
                "Exit Price": t.price,
                "Qty": t.quantity,
                "PnL": round(pnl, 2),
            })
            open_trade = None

    st.subheader("Trade Breakdown")

    if not completed:
        st.info("No completed trades")
        return []

    st.dataframe(
        completed[:MAX_ROWS],
        use_container_width=True,
    )

    if len(completed) > MAX_ROWS:
        st.caption(f"Showing first {MAX_ROWS} trades out of {len(completed)}")

    return completed
