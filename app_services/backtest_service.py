from backtester.engine import BacktestEngine
from backtester.metrics import MetricsEngine


class BacktestService:
    def run(
        self,
        data,
        strategy,
        initial_cash,
        trade_quantity,
    ):
        engine = BacktestEngine(
            data=data,
            strategy=strategy,
            initial_cash=initial_cash,
            trade_quantity=trade_quantity,
        )

        equity_curve = engine.run()

        metrics = MetricsEngine(
            equity_curve=equity_curve,
            trades=engine.portfolio.trades,
        ).compute()

        return {
            "metrics": metrics,
            "trades": engine.portfolio.trades,
        }
