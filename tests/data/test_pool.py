import pytest
from src.data.pool import StockPool


def test_default_pool():
    """测试默认股票池"""
    pool = StockPool()
    symbols = pool.get_default()
    if symbols:
        assert len(symbols) > 0


def test_custom_pool():
    """测试自定义股票池"""
    pool = StockPool()
    pool.add_pool('test_pool', ['600519.SH', '000001.SZ'])
    symbols = pool.get('test_pool')
    assert '600519.SH' in symbols
    assert '000001.SZ' in symbols


def test_list_pools():
    """测试列出股票池"""
    pool = StockPool()
    pool.add_pool('my_pool', ['600519.SH'])
    pools = pool.list_pools()
    assert 'my_pool' in pools