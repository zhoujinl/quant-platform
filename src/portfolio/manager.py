import pandas as pd
import numpy as np
from typing import Dict


class PortfolioManager:
    """组合管理"""

    def __init__(self, max_positions: int = 10):
        self.max_positions = max_positions

    def allocate_equal(
        self, 
        selected: pd.Series, 
        capital: float, 
        prices: pd.Series
    ) -> Dict[str, int]:
        """等权分配
        
        Args:
            selected: 选股因子值Series
            capital: 可用资金
            prices: 各股票价格Series
        
        Returns:
            {symbol: quantity}
        """
        valid = selected.dropna()
        valid = valid[valid.index.isin(prices.index)]
        symbols = valid.head(self.max_positions).index.tolist()
        
        n = len(symbols)
        if n == 0:
            return {}
        
        amount_per_stock = capital / n
        positions = {}
        
        for symbol in symbols:
            price = prices[symbol]
            if price > 0:
                quantity = int(amount_per_stock / price)
                if quantity > 0:
                    positions[symbol] = quantity
        
        return positions

    def allocate_by_factor(
        self, 
        selected: pd.Series, 
        capital: float, 
        prices: pd.Series
    ) -> Dict[str, int]:
        """按因子权重分配
        
        Args:
            selected: 选股因子值Series
            capital: 可用资金
            prices: 各股票价格Series
        
        Returns:
            {symbol: quantity}
        """
        valid = selected.dropna()
        valid = valid[valid.index.isin(prices.index)]
        
        weights = valid.head(self.max_positions)
        total = weights.sum()
        if total <= 0:
            return {}
        
        weights = weights / total
        
        positions = {}
        for symbol in weights.index:
            amount = capital * weights[symbol]
            price = prices[symbol]
            if price > 0:
                quantity = int(amount / price)
                if quantity > 0:
                    positions[symbol] = quantity
        
        return positions