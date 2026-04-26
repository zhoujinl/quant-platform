from abc import ABC, abstractmethod
import pandas as pd


class Signal(ABC):
    """信号基类"""
    
    @abstractmethod
    def generate(self, factors) -> pd.Series:
        """生成信号
        
        Args:
            factors: pd.Series，股票代码为index，值为因子值
            
        Returns:
            pd.Series，股票代码为index，值为信号强度 (1.0 表示选中)
        """
        pass


class TopNSignal(Signal):
    """取Top N股票"""
    
    def __init__(self, n: int = 10, ascending: bool = False):
        self.n = n
        self.ascending = ascending
    
    def generate(self, factors: pd.Series) -> pd.Series:
        if self.ascending:
            return factors.nsmallest(self.n)
        return factors.nlargest(self.n)


class ThresholdSignal(Signal):
    """阈值过滤"""
    
    def __init__(self, threshold: float, operator: str = 'gt'):
        self.threshold = threshold
        self.operator = operator
    
    def generate(self, factors: pd.Series) -> pd.Series:
        ops = {
            'gt': factors > self.threshold,
            'ge': factors >= self.threshold,
            'lt': factors < self.threshold,
            'le': factors <= self.threshold,
        }
        mask = ops[self.operator]
        return factors[mask]


class CompositeSignal(Signal):
    """组合信号 (AND交集) - 所有因子都选中的股票才保留"""
    
    def __init__(self, signals: list):
        self.signals = signals
    
    def generate(self, factors_list: list) -> pd.Series:
        result = None
        for factors in factors_list:
            if result is None:
                result = set(factors.index)
            else:
                result = result.intersection(set(factors.index))
        return pd.Series(1.0, index=list(result))