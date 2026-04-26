import os
import pandas as pd


class DataCache:
    """本地数据缓存"""
    
    def __init__(self, cache_dir: str = 'cache/'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def save(self, name: str, df: pd.DataFrame):
        """保存为 parquet"""
        path = os.path.join(self.cache_dir, f'{name}.parquet')
        df.to_parquet(path, engine='pyarrow')
    
    def load(self, name: str) -> pd.DataFrame:
        """读取 parquet"""
        path = os.path.join(self.cache_dir, f'{name}.parquet')
        if not os.path.exists(path):
            return None
        return pd.read_parquet(path)
    
    def exists(self, name: str) -> bool:
        """检查缓存是否存在"""
        return os.path.exists(os.path.join(self.cache_dir, f'{name}.parquet'))