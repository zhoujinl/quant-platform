import pytest
from datetime import datetime
from src.data.fetcher import StockFetcher


def test_fetch_index_daily():
    """测试获取指数行情"""
    fetcher = StockFetcher()
    df = fetcher.get_index_daily('000300.SH', '2024-01-01', '2024-12-31')
    assert not df.empty
    assert 'close' in df.columns
    assert df['close'].iloc[0] > 0