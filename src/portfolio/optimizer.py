import pandas as pd
import numpy as np


class RiskParityOptimizer:
    """风险平价优化器"""

    def optimize(self, returns: pd.DataFrame, capital: float) -> pd.Series:
        """风险平价优化
        
        计算协方差矩阵，分配使各资产风险贡献相等
        
        Args:
            returns: 收益率DataFrame (行: 时间, 列: 资产)
            capital: 可用资金
        
        Returns:
            weight: 各资产权重Series
        """
        cov = returns.cov()
        
        n = len(cov)
        if n == 0:
            return pd.Series(dtype=float)
        
        try:
            cov_arr = cov.values
            ones = np.ones(n)
            
            Sigma_inv = np.linalg.inv(cov_arr)
            w = Sigma_inv @ ones
            w = w / w.sum()
            
            weights = pd.Series(w, index=cov.index)
            weights = weights.abs()
            weights = weights / weights.sum()
            
            return weights * capital
            
        except np.linalg.LinAlgError:
            return pd.Series(1.0 / n, index=cov.index) * capital