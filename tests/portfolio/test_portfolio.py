import pandas as pd
import numpy as np
from src.portfolio.manager import PortfolioManager
from src.portfolio.optimizer import RiskParityOptimizer


def test_allocate_equal():
    manager = PortfolioManager(max_positions=3)
    selected = pd.Series([1.0, 2.0, 3.0], index=['A', 'B', 'C'])
    prices = pd.Series({'A': 10, 'B': 20, 'C': 30})
    
    positions = manager.allocate_equal(selected, 100000, prices)
    
    assert len(positions) <= 3
    assert 'A' in positions
    assert 'B' in positions
    assert 'C' in positions
    
    total_value = sum(positions[s] * prices[s] for s in positions)
    assert total_value <= 100000
    
    print(f"allocate_equal test passed: {positions}")


def test_allocate_by_factor():
    manager = PortfolioManager(max_positions=3)
    selected = pd.Series([1.0, 2.0, 3.0], index=['A', 'B', 'C'])
    prices = pd.Series({'A': 10, 'B': 20, 'C': 30})
    
    positions = manager.allocate_by_factor(selected, 100000, prices)
    
    assert len(positions) <= 3
    print(f"allocate_by_factor test passed: {positions}")


def test_risk_parity_optimizer():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100)
    returns = pd.DataFrame({
        'A': np.random.randn(100) * 0.02,
        'B': np.random.randn(100) * 0.015,
        'C': np.random.randn(100) * 0.01,
    }, index=dates)
    
    optimizer = RiskParityOptimizer()
    weights = optimizer.optimize(returns, 100000)
    
    assert len(weights) == 3
    total = weights.sum()
    assert total <= 100000
    
    print(f"risk_parity_optimizer test passed, total={total}")


if __name__ == '__main__':
    from src.portfolio import PortfolioManager, RiskParityOptimizer
    
    test_allocate_equal()
    test_allocate_by_factor()
    test_risk_parity_optimizer()
    print("All tests passed!")