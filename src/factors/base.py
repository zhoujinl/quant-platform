from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class Factor(ABC):
    """因子基类"""
    
    @abstractmethod
    def compute(self, df: pd.DataFrame) -> pd.Series:
        """计算因子值
        
        Args:
            df: 包含所需字段的DataFrame
        
        Returns:
            因子值Series
        """
        pass


class PE(Factor):
    """市盈率因子: close / eps"""
    
    def compute(self, df: pd.DataFrame) -> pd.Series:
        return df['close'] / df['eps']


class PB(Factor):
    """市净率因子: close / bps"""
    
    def compute(self, df: pd.DataFrame) -> pd.Series:
        return df['close'] / df['bps']


class MarketCap(Factor):
    """市值因子: close * shares"""
    
    def compute(self, df: pd.DataFrame) -> pd.Series:
        return df['close'] * df['shares']


class ROE(Factor):
    """净资产收益率因子: net_profit / equity"""
    
    def compute(self, df: pd.DataFrame) -> pd.Series:
        return df['net_profit'] / df['equity']


class Momentum(Factor):
    """动量因子: 指定周期的涨跌幅"""
    
    def __init__(self, period: int = 1):
        self.period = period
    
    def compute(self, df: pd.DataFrame) -> pd.Series:
        return df['close'].pct_change(periods=self.period)