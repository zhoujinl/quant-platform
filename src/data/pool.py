import akshare as ak
import pandas as pd
from typing import List, Dict
import warnings


class StockPool:
    """股票池管理"""
    
    def __init__(self):
        self._pools: Dict[str, List[str]] = {}
    
    def get_default(self, pool_name: str = 'hs300') -> List[str]:
        """获取默认股票池
        
        Args:
            pool_name: 股票池名称
                - 'hs300': 沪深300成分股
                - 'zz500': 中证500成分股
                - 'cyb': 创业板指成分股
        
        Returns:
            股票代码列表，如果API失败返回空列表
        """
        try:
            if pool_name == 'hs300':
                df = ak.index_stock_cons_csindex(symbol='sh000300')
            elif pool_name == 'zz500':
                df = ak.index_stock_cons_csindex(symbol='sh000905')
            elif pool_name == 'cyb':
                df = ak.index_stock_cons_csindex(symbol='sz399006')
            else:
                return []
            
            return df['成分券代码'].tolist()
        except Exception as e:
            warnings.warn(f"获取股票池失败: {e}")
            return []
    
    def get(self, name: str) -> List[str]:
        """获取指定股票池"""
        if name not in self._pools:
            return self.get_default(name)
        return self._pools[name]
    
    def add_pool(self, name: str, symbols: List[str]):
        """添加自定义股票池"""
        self._pools[name] = symbols
    
    def list_pools(self) -> List[str]:
        """列出所有股票池"""
        return list(self._pools.keys())