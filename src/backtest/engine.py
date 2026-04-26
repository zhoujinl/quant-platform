import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Trade:
    date: str
    symbol: str
    action: str
    quantity: int
    price: float
    commission: float


@dataclass
class BacktestResult:
    initial_capital: float
    final_value: float
    total_commission: float
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.DataFrame = field(default_factory=pd.DataFrame)


class BacktestEngine:
    
    def __init__(self, initial_capital: float = 100000, commission: float = 0.0003):
        self.initial_capital = initial_capital
        self.commission = commission
        self.positions: Dict[str, int] = {}
        self.cash = initial_capital
        self.total_commission = 0.0
        self.trades: List[Trade] = []
        self.equity_curve_data: List[Dict] = []
    
    def run(self, prices: pd.DataFrame, signals: Dict[str, Dict[str, int]]):
        """运行回测
        
        Args:
            prices: DataFrame，index为日期，columns为股票代码，值为价格
            signals: Dict[date, Dict[symbol, quantity]] - 目标持仓
        """
        for date in prices.index:
            date_str = date.strftime('%Y-%m-%d') if isinstance(date, pd.Timestamp) else str(date)
            day_prices = prices.loc[date]
            
            if date_str in signals:
                self._rebalance(date_str, day_prices, signals[date_str])
            
            self._record_equity(date_str, day_prices)
    
    def _rebalance(self, date: str, prices: pd.Series, new_positions: Dict[str, int]):
        current_value = self._get_total_value(prices)
        
        for symbol in list(self.positions.keys()):
            if symbol not in new_positions:
                self._sell(date, symbol, self.positions[symbol], prices[symbol])
        
        for symbol, quantity in new_positions.items():
            if symbol in self.positions:
                diff = quantity - self.positions[symbol]
                if diff > 0:
                    self._buy(date, symbol, diff, prices[symbol])
                elif diff < 0:
                    self._sell(date, symbol, -diff, prices[symbol])
            else:
                self._buy(date, symbol, quantity, prices[symbol])
    
    def _buy(self, date: str, symbol: str, quantity: int, price: float):
        cost = quantity * price
        commission = cost * self.commission
        self.cash -= (cost + commission)
        self.total_commission += commission
        
        if symbol in self.positions:
            self.positions[symbol] += quantity
        else:
            self.positions[symbol] = quantity
        
        self.trades.append(Trade(date, symbol, 'buy', quantity, price, commission))
    
    def _sell(self, date: str, symbol: str, quantity: int, price: float):
        proceeds = quantity * price
        commission = proceeds * self.commission
        self.cash += (proceeds - commission)
        self.total_commission += commission
        
        self.positions[symbol] -= quantity
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        
        self.trades.append(Trade(date, symbol, 'sell', quantity, price, commission))
    
    def _get_total_value(self, prices: pd.Series) -> float:
        position_value = 0.0
        for symbol, quantity in self.positions.items():
            if symbol in prices:
                position_value += quantity * prices[symbol]
        return self.cash + position_value
    
    def _record_equity(self, date: str, prices: pd.Series):
        total_value = self._get_total_value(prices)
        self.equity_curve_data.append({
            'date': date,
            'value': total_value,
            'cash': self.cash,
            'position_value': total_value - self.cash
        })
    
    def get_results(self) -> BacktestResult:
        if not self.equity_curve_data:
            return BacktestResult(
                initial_capital=self.initial_capital,
                final_value=self.initial_capital,
                total_commission=self.total_commission,
                trades=self.trades
            )
        
        equity_curve = pd.DataFrame(self.equity_curve_data)
        equity_curve['date'] = pd.to_datetime(equity_curve['date'])
        equity_curve = equity_curve.set_index('date')
        
        final_value = self._get_total_value(pd.Series())
        
        return BacktestResult(
            initial_capital=self.initial_capital,
            final_value=final_value,
            total_commission=self.total_commission,
            trades=self.trades,
            equity_curve=equity_curve
        )