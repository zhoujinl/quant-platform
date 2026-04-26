import pytest
import pandas as pd
from src.data.cache import DataCache


def test_cache_save_load():
    """测试缓存存取"""
    cache = DataCache('cache/')
    df = pd.DataFrame({'a': [1, 2, 3]}, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))
    
    cache.save('test', df)
    loaded = cache.load('test')
    assert loaded is not None
    assert len(loaded) == 3


def test_cache_exists():
    """测试缓存检查"""
    import os
    cache = DataCache('cache/')
    test_file = os.path.join('cache/', 'test.parquet')
    if os.path.exists(test_file):
        os.remove(test_file)
    assert not cache.exists('test')
    df = pd.DataFrame({'a': [1]})
    cache.save('test', df)
    assert cache.exists('test')