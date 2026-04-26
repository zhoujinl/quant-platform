import pytest
import pandas as pd
from src.backtest import BacktestEngine


def test_simple_backtest():
    engine = BacktestEngine(initial_capital=100000, commission=0.0003)
    
    prices = pd.DataFrame({
        'A': [10.0, 11.0, 12.0],
        'B': [20.0, 21.0, 22.0]
    }, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))
    
    positions = {'2024-01-01': {'A': 1000, 'B': 500}}
    
    engine.run(prices, positions)
    result = engine.get_results()
    
    assert result.final_value > 0
    assert len(result.trades) > 0


def test_rebalance():
    engine = BacktestEngine(initial_capital=100000, commission=0.0003)
    
    prices = pd.DataFrame({
        'A': [10.0, 11.0, 12.0],
        'B': [20.0, 21.0, 22.0]
    }, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))
    
    positions = {
        '2024-01-01': {'A': 1000, 'B': 500},
        '2024-01-02': {'A': 1500, 'B': 0},
    }
    
    engine.run(prices, positions)
    result = engine.get_results()
    
    assert len(result.trades) == 4


def test_sell_all():
    engine = BacktestEngine(initial_capital=100000, commission=0.0003)
    
    prices = pd.DataFrame({
        'A': [10.0, 11.0],
    }, index=pd.to_datetime(['2024-01-01', '2024-01-02']))
    
    positions = {
        '2024-01-01': {'A': 1000},
        '2024-01-02': {},
    }
    
    engine.run(prices, positions)
    result = engine.get_results()
    
    assert len(list(filter(lambda t: t.action == 'sell', result.trades))) == 1


def test_equity_curve():
    engine = BacktestEngine(initial_capital=100000, commission=0.0003)
    
    prices = pd.DataFrame({
        'A': [10.0, 11.0, 12.0],
    }, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))
    
    positions = {'2024-01-01': {'A': 1000}}
    
    engine.run(prices, positions)
    result = engine.get_results()
    
    assert len(result.equity_curve) == 3


def test_commission():
    engine = BacktestEngine(initial_capital=100000, commission=0.001)
    
    prices = pd.DataFrame({
        'A': [10.0],
    }, index=pd.to_datetime(['2024-01-01']))
    
    positions = {'2024-01-01': {'A': 1000}}
    
    engine.run(prices, positions)
    result = engine.get_results()
    
    assert result.total_commission > 0