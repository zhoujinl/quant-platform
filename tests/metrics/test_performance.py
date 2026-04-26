import pytest
import pandas as pd
import numpy as np
from src.metrics.performance import PerformanceMetrics


class TestPerformanceMetrics:
    def test_performance_metrics(self):
        returns = pd.Series([0.01, -0.02, 0.03, 0.02, -0.01])
        metrics = PerformanceMetrics()
        result = metrics.compute(returns)
        
        assert 'total_return' in result
        assert 'annual_return' in result
        assert 'sharpe_ratio' in result
        assert 'max_drawdown' in result
        assert 'calmar_ratio' in result
        assert 'win_rate' in result
        assert 'avg_win' in result
        assert 'avg_loss' in result
        assert 'profit_loss_ratio' in result
        assert 'num_trades' in result
        assert 'volatility' in result

    def test_total_return(self):
        returns = pd.Series([0.01, 0.01, 0.01])
        metrics = PerformanceMetrics()
        result = metrics.compute(returns)
        expected = (1.01 * 1.01 * 1.01) - 1
        assert abs(result['total_return'] - expected) < 1e-6

    def test_max_drawdown(self):
        returns = pd.Series([0.05, -0.10, 0.02, -0.05, 0.08])
        metrics = PerformanceMetrics()
        result = metrics.compute(returns)
        assert result['max_drawdown'] < 0

    def test_win_rate(self):
        returns = pd.Series([0.01, -0.01, 0.01, 0.01, -0.01])
        metrics = PerformanceMetrics()
        result = metrics.compute(returns)
        assert result['win_rate'] == 0.6

    def test_empty_returns(self):
        returns = pd.Series([])
        metrics = PerformanceMetrics()
        result = metrics.compute(returns)
        assert result['total_return'] == 0.0
        assert result['num_trades'] == 0

    def test_custom_days_per_year(self):
        returns = pd.Series([0.01, -0.01])
        metrics = PerformanceMetrics(days_per_year=365)
        result = metrics.compute(returns)
        assert 'annual_return' in result