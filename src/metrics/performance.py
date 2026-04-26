import pandas as pd
import numpy as np
from math import sqrt
from typing import Dict


class PerformanceMetrics:
    def __init__(self, days_per_year: int = 252):
        self.days_per_year = days_per_year

    def compute(self, returns: pd.Series) -> Dict[str, float]:
        if len(returns) == 0:
            return self._empty_metrics()

        total_return = (1 + returns).prod() - 1
        annual_return = (1 + total_return) ** (self.days_per_year / len(returns)) - 1
        
        mean_return = returns.mean()
        std_return = returns.std()
        sharpe_ratio = mean_return / std_return * sqrt(self.days_per_year) if std_return != 0 else 0.0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = cumulative / running_max - 1
        max_drawdown = drawdown.min()
        
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
        
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        win_rate = len(positive_returns) / len(returns) if len(returns) > 0 else 0.0
        avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0.0
        avg_loss = negative_returns.mean() if len(negative_returns) > 0 else 0.0
        profit_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0.0
        
        num_trades = len(returns)
        volatility = std_return * sqrt(self.days_per_year)

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_loss_ratio': profit_loss_ratio,
            'num_trades': num_trades,
            'volatility': volatility
        }

    def _empty_metrics(self) -> Dict[str, float]:
        return {
            'total_return': 0.0,
            'annual_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'calmar_ratio': 0.0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_loss_ratio': 0.0,
            'num_trades': 0,
            'volatility': 0.0
        }