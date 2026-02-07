# backtester/metrics.py

from dataclasses import dataclass
from datetime import datetime
from typing import List

import polars as pl
import math

from backtester.trade import Trade

@dataclass
class PerformanceMetrics:
    total_return_pct: float
    cagr_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float

    total_trades: int
    win_rate_pct: float
    avg_win: float
    avg_loss: float
    profit_factor: float


class MetricsEngine:
    """
    Computes performance metrics from equity curve and trades.
    """

    def __init__(
        self,
        equity_curve: pl.DataFrame,
        trades: List[Trade],
        risk_free_rate: float = 0.0,  # annual
        periods_per_year: int = 252,
    ):
        self.equity = equity_curve
        self.trades = trades
        self.risk_free_rate = risk_free_rate
        self.periods_per_year = periods_per_year
        
    def total_return_pct(self) -> float:
        equity_col = self.equity["equity"]
        start = equity_col.to_list()[0]
        end = equity_col.to_list()[-1]
        return ((end - start) / start) * 100
    
    def cagr_pct(self) -> float:
        equity_col = self.equity["equity"].to_list()
        timestamp_col = self.equity["timestamp"].to_list()
        
        start_value = equity_col[0]
        end_value = equity_col[-1]
        start_time = timestamp_col[0]
        end_time = timestamp_col[-1]

        years = (end_time - start_time).days / 365.25
        if years <= 0:
            return 0.0

        return ((end_value / start_value) ** (1 / years) - 1) * 100
    
    def max_drawdown_pct(self) -> float:
        equity = self.equity["equity"].to_list()
        peak = equity[0]
        max_dd = 0.0

        for value in equity:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)

        return max_dd * 100
    
    def sharpe_ratio(self) -> float:
        returns = self.equity.select(
            pl.col("equity").pct_change().drop_nulls()
        )["equity"]

        if len(returns) == 0:
            return 0.0

        mean_return = returns.mean()
        std_return = returns.std()

        if std_return == 0:
            return 0.0

        annualized_return = mean_return * self.periods_per_year
        annualized_std = std_return * math.sqrt(self.periods_per_year)

        return (annualized_return - self.risk_free_rate) / annualized_std
    
    def _trade_pnls(self) -> List[float]:
        pnls = []
        stack = []

        for trade in self.trades:
            if trade.side == "BUY":
                stack.append(trade)
            elif trade.side == "SELL" and stack:
                buy = stack.pop(0)
                pnl = (trade.price - buy.price) * trade.quantity
                pnls.append(pnl)

        return pnls
    
    def trade_metrics(self):
        pnls = self._trade_pnls()

        if not pnls:
            return 0, 0.0, 0.0, 0.0, 0.0

        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]

        total_trades = len(pnls)
        win_rate = (len(wins) / total_trades) * 100

        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0

        profit_factor = (
            sum(wins) / abs(sum(losses))
            if losses else float("inf")
        )

        return total_trades, win_rate, avg_win, avg_loss, profit_factor
    
    def compute(self) -> PerformanceMetrics:
        total_trades, win_rate, avg_win, avg_loss, profit_factor = self.trade_metrics()

        return PerformanceMetrics(
            total_return_pct=self.total_return_pct(),
            cagr_pct=self.cagr_pct(),
            max_drawdown_pct=self.max_drawdown_pct(),
            sharpe_ratio=self.sharpe_ratio(),
            total_trades=total_trades,
            win_rate_pct=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
        )







