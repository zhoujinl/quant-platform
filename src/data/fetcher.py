import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


class StockFetcher:
    """A股数据获取器"""
    
    def get_index_daily(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """获取指数日线
        
        Args:
            symbol: 指数代码，如 '000300.SH' (沪深300), '000001.SH' (上证指数)
            start: 开始日期 'YYYY-MM-DD'
            end: 结束日期 'YYYY-MM-DD'
        """
        symbol_map = {
            '000300.SH': 'sh000300',
            '000001.SH': 'sh000001',
            '399001.SZ': 'sz399001',
            '399006.SZ': 'sz399006',
        }
        ak_symbol = symbol_map.get(symbol, symbol)
        
        df = ak.stock_zh_index_daily(symbol=ak_symbol)
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= start) & (df['date'] <= end)]
        df = df.set_index('date').sort_index()
        return df
    
    def get_index_components(self, symbol: str) -> list:
        """获取指数成分股
        
        Args:
            symbol: '000300' (沪深300), '000852' (中证2000)
        Returns:
            股票代码列表，如 ['600000.SH', '000001.SZ']
        """
        df = ak.index_stock_cons_csindex(symbol=symbol)
        # 根据交易所添加后缀
        stocks = []
        for _, row in df.iterrows():
            code = row['成分券代码']
            exchange = row['交易所']
            if exchange == '上海证券交易所':
                stocks.append(f'{code}.SH')
            else:
                stocks.append(f'{code}.SZ')
        return stocks
    
    def get_hs300_symbols(self) -> list:
        """获取沪深300成分股"""
        return self.get_index_components('000300')
    
    def get_cz2000_symbols(self) -> list:
        """获取中证2000成分股"""
        return self.get_index_components('000852')
    
    def get_stock_daily(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """获取个股日线
        
        Args:
            symbol: 股票代码，如 '600519.SH' (贵州茅台), '000001.SZ' (平安银行)
            start: 开始日期 'YYYY-MM-DD'
            end: 结束日期 'YYYY-MM-DD'
        """
        code = symbol.replace('.SH', '').replace('.SZ', '')
        
        df = ak.stock_zh_a_hist(
            symbol=code,
            start_date=start.replace('-', ''),
            end_date=end.replace('-', ''),
            adjust='qfq'
        )
        df['date'] = pd.to_datetime(df['日期'])
        df = df.set_index('date').sort_index()
        df = df.rename(columns={
            '开盘': 'open', '最高': 'high', '最低': 'low',
            '收盘': 'close', '成交量': 'volume', '成交额': 'amount'
        })
        return df[['open', 'high', 'low', 'close', 'volume', 'amount']]
    
    def get_stock_info(self, symbol: str) -> pd.DataFrame:
        """获取个股基本信息
        
        Args:
            symbol: 股票代码，如 '600519.SH'
        """
        return ak.stock_individual_info_em(symbol=symbol)