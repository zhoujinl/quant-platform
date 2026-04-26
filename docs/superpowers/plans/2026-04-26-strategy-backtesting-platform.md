# A股选股策略回测平台 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标**: 构建个人投资研究用的A股策略回测平台，支持灵活策略验证

**架构**: 模块化架构，数据层 → 因子引擎 → 信号生成 → 回测引擎 → 绩效分析

**技术栈**: Python, Pandas, NumPy, akShare, Streamlit, Plotly

---

## Task 1: 数据层 - 数据获取与缓存

**Files:**
- Create: `src/data/__init__.py`
- Create: `src/data/fetcher.py`
- Create: `src/data/cache.py`
- Create: `src/data/pool.py`
- Create: `tests/data/test_fetcher.py`
- Create: `tests/data/test_cache.py`

### Step 1: 创建目录和基础结构

```bash
mkdir -p src/data tests/data cache strategies outputs
```

### Step 2: 测试用例 - fetcher

```python
# tests/data/test_fetcher.py
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
```

### Step 3: 运行测试确认失败

```bash
pytest tests/data/test_fetcher.py::test_fetch_index_daily -v
# Expected: FAIL (StockFetcher not defined)
```

### Step 4: 实现 fetcher

```python
# src/data/fetcher.py
import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Optional

class StockFetcher:
    """A股数据获取器"""
    
    def get_index_daily(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """获取指数日线"""
        if symbol == '000300.SH':
            df = ak.stock_zh_index_daily(symbol='sh000300')
        elif symbol == '000001.SH':
            df = ak.stock_zh_index_daily(symbol='sh000001')
        else:
            df = ak.stock_zh_index_daily(symbol=symbol)
        
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= start) & (df['date'] <= end)]
        df = df.set_index('date').sort_index()
        return df
    
    def get_stock_daily(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """获取个股日线"""
        df = ak.stock_zh_a_hist(symbol=symbol.replace('.SH', '').replace('.SZ', ''), 
                           start_date=start.replace('-', ''), 
                           end_date=end.replace('-', ''),
                           adjust='qfq')
        df['date'] = pd.to_datetime(df['日期'])
        df = df.set_index('date').sort_index()
        df = df.rename(columns={
            '开盘': 'open', '最高': 'high', '最低': 'low', 
            '收盘': 'close', '成交量': 'volume', '成交额': 'amount'
        })
        return df[['open', 'high', 'low', 'close', 'volume', 'amount']]
    
    def get_stock_info(self, symbol: str) -> pd.DataFrame:
        """获取个股基本信息"""
        df = ak.stock_individual_info_em(symbol=symbol)
        return df
```

### Step 5: 运行测试

```bash
pytest tests/data/test_fetcher.py::test_fetch_index_daily -v
# Expected: PASS (网络请求可能需要几秒)
```

### Step 6: 测试缓存

```python
# tests/data/test_cache.py
import pytest
from datetime import datetime
from src.data.cache import DataCache

def test_cache_save_load():
    """测试缓存存取"""
    cache = DataCache('cache/')
    import pandas as pd
    df = pd.DataFrame({'a': [1, 2, 3]}, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))
    
    cache.save('test', df)
    loaded = cache.load('test')
    assert loaded is not None
    assert len(loaded) == 3
```

### Step 7: 实现缓存

```python
# src/data/cache.py
import os
import pandas as pd
import parquet as pq

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
```

### Step 8: 测试通过后提交

```bash
git add src/data/ tests/data/ cache/
git commit -m "feat: add data layer with fetcher and cache"
```

---

## Task 2: 因子引擎 - 基础因子与注册表

**Files:**
- Create: `src/factors/__init__.py`
- Create: `src/factors/base.py`
- Create: `src/factors/registry.py`
- Create: `tests/factors/test_base.py`

### Step 1: 测试用例

```python
# tests/factors/test_base.py
import pytest
import pandas as pd
from src.factors.base import PE, PB, MarketCap, ROE

def test_pe_factor():
    """测试PE因子"""
    data = pd.DataFrame({
        'close': [10.0, 20.0, 30.0],
        'eps': [1.0, 2.0, 3.0]
    }, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))
    
    pe = PE()
    result = pe.compute(data)
    assert result.iloc[0] == 10.0
```

### Step 2: 运行测试确认失败

```bash
pytest tests/factors/test_base.py::test_pe_factor -v
# Expected: FAIL
```

### Step 3: 实现基础因子

```python
# src/factors/base.py
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class Factor(ABC):
    """因子基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def compute(self, data: pd.DataFrame) -> pd.Series:
        pass

class PE(Factor):
    """市盈率因子"""
    
    @property
    def name(self) -> str:
        return 'pe'
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        return data['close'] / data['eps']

class PB(Factor):
    """市净率因子"""
    
    @property
    def name(self) -> str:
        return 'pb'
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        return data['close'] / data['bps']

class MarketCap(Factor):
    """市值因子"""
    
    @property
    def name(self) -> str:
        return 'market_cap'
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        return data['close'] * data['shares']

class ROE(Factor):
    """净资产收益率"""
    
    @property
    def name(self) -> str:
        return 'roe'
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        return data['net_profit'] / data['equity']

class Momentum(Factor):
    """动量因子"""
    
    def __init__(self, period: int = 20):
        self.period = period
    
    @property
    def name(self) -> str:
        return f'momentum_{self.period}'
    
    def compute(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change(self.period)
```

### Step 4: 实现注册表

```python
# src/factors/registry.py
from .base import Factor, PE, PB, MarketCap, ROE, Momentum

FACTOR_REGISTRY = {
    'pe': PE,
    'pb': PB,
    'market_cap': MarketCap,
    'roe': ROE,
    'momentum_20': lambda: Momentum(20),
    'momentum_60': lambda: Momentum(60),
}

def get_factor(name: str) -> Factor:
    """获取因子实例"""
    if name in FACTOR_REGISTRY:
        factory = FACTOR_REGISTRY[name]
        return factory() if callable(factory) else factory
    raise ValueError(f"Unknown factor: {name}")
```

### Step 5: 测试通过后提交

```bash
git add src/factors/ tests/factors/
git commit -m "feat: add factor engine with base factors"
```

---

## Task 3: 信号生成模块

**Files:**
- Create: `src/signals/__init__.py`
- Create: `src/signals/generator.py`
- Create: `src/signals/registry.py`
- Create: `tests/signals/test_generator.py`

### Step 1: 测试用例

```python
# tests/signals/test_generator.py
import pytest
import pandas as pd
from src.signals.generator import TopNSignal

def test_top_n_signal():
    """测试选前N名信号"""
    factors = pd.Series([1.0, 3.0, 2.0], index=['A', 'B', 'C'])
    signal = TopNSignal(n=2)
    result = signal.generate(factors)
    assert len(result) == 2
    assert 'B' in result.index
    assert 'C' in result.index
```

### Step 2: 运行测试确认失败

```bash
pytest tests/signals/test_generator.py::test_top_n_signal -v
```

### Step 3: 实现信号生成

```python
# src/signals/generator.py
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class Signal(ABC):
    """信号基类"""
    
    @abstractmethod
    def generate(self, factors: pd.Series) -> pd.Series:
        """生成信号，返回持仓股票"""
        pass

class TopNSignal(Signal):
    """选前N名"""
    
    def __init__(self, n: int = 10, ascending: bool = False):
        self.n = n
        self.ascending = ascending
    
    def generate(self, factors: pd.Series) -> pd.Series:
        if self.ascending:
            selected = factors.nsmallest(self.n)
        else:
            selected = factors.nlargest(self.n)
        return selected

class ThresholdSignal(Signal):
    """阈值选股"""
    
    def __init__(self, threshold: float, operator: str = 'gt'):
        self.threshold = threshold
        self.operator = operator
    
    def generate(self, factors: pd.Series) -> pd.Series:
        if self.operator == 'gt':
            return factors[factors > self.threshold]
        elif self.operator == 'ge':
            return factors[factors >= self.threshold]
        elif self.operator == 'lt':
            return factors[factors < self.threshold]
        else:
            return factors[factors <= self.threshold]

class CompositeSignal(Signal):
    """复合信号 (满足多个条件)"""
    
    def __init__(self, signals: list):
        self.signals = signals
    
    def generate(self, factors_list: list) -> pd.Series:
        result = None
        for factors in factors_list:
            if result is None:
                result = factors.index
            else:
                result = result.intersection(factors.index)
        return pd.Series(1.0, index=result)
```

### Step 4: 注册表

```python
# src/signals/registry.py
from .generator import Signal, TopNSignal, ThresholdSignal

SIGNAL_REGISTRY = {
    'top_n': TopNSignal,
    'threshold': ThresholdSignal,
}

def get_signal(name: str, **kwargs) -> Signal:
    if name in SIGNAL_REGISTRY:
        return SIGNAL_REGISTRY[name](**kwargs)
    raise ValueError(f"Unknown signal: {name}")
```

### Step 5: 提交

```bash
git add src/signals/ tests/signals/
git commit -m "feat: add signal generation module"
```

---

## Task 4: 回测引擎

**Files:**
- Create: `src/backtest/__init__.py`
- Create: `src/backtest/engine.py`
- Create: `src/backtest/recorder.py`
- Create: `tests/backtest/test_engine.py`

### Step 1: 测试用例

```python
# tests/backtest/test_engine.py
import pytest
import pandas as pd
from datetime import datetime
from src.backtest.engine import BacktestEngine

def test_simple_backtest():
    """测试简单回测"""
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.0003
    )
    
    prices = pd.DataFrame({
        'A': [10.0, 11.0, 12.0],
        'B': [20.0, 21.0, 22.0]
    }, index=pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']))
    
    positions = {
        '2024-01-01': {'A': 100, 'B': 50},
    }
    
    engine.run(prices, positions)
    result = engine.get_results()
    
    assert result['final_value'] > 0
    assert len(result['trades']) > 0
```

### Step 2: 运行测试确认失败

```bash
pytest tests/backtest/test_engine.py::test_simple_backtest -v
```

### Step 3: 实现回测引擎

```python
# src/backtest/engine.py
import pandas as pd
import numpy as np
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Trade:
    date: str
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: int
    price: float
    commission: float

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, 
                 initial_capital: float = 100000,
                 commission: float = 0.0003,
                 slippage: float = 0.0):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.cash = initial_capital
        self.positions = {}
        self.trades: List[Trade] = []
        self.portfolio_value = []
        
    def run(self, prices: pd.DataFrame, signals: Dict[str, Dict[str, int]]) -> 'BacktestEngine':
        """运行回测
        
        Args:
            prices: 价格 DataFrame，index 为日期，columns 为股票代码
            signals: dict[date] -> dict[symbol] -> quantity
        """
        for date in prices.index:
            date_str = str(date.date())
            
            # 处理调仓信号
            if date_str in signals:
                new_positions = signals[date_str]
                self._rebalance(date, prices.loc[date], new_positions)
            
            # 更新组合价值
            value = self._calc_portfolio_value(date, prices.loc[date])
            self.portfolio_value.append({
                'date': date,
                'value': value,
                'cash': self.cash,
                'position_value': value - self.cash
            })
        
        return self
    
    def _rebalance(self, date, prices: pd.Series, new_positions: Dict[str, int]):
        """调仓"""
        # 卖出不在持仓的
        for symbol in list(self.positions.keys()):
            if symbol not in new_positions:
                self._sell(date, symbol, self.positions[symbol], prices[symbol])
        
        # 买入新持仓
        for symbol, quantity in new_positions.items():
            if symbol in self.positions:
                diff = quantity - self.positions[symbol]
                if diff > 0:
                    self._buy(date, symbol, diff, prices[symbol])
                elif diff < 0:
                    self._sell(date, symbol, -diff, prices[symbol])
            else:
                self._buy(date, symbol, quantity, prices[symbol])
    
    def _buy(self, date, symbol: str, quantity: int, price: float):
        """买入"""
        cost = quantity * price * (1 + self.commission + self.slippage)
        if cost > self.cash:
            quantity = int(self.cash / (price * (1 + self.commission + self.slippage)))
            if quantity <= 0:
                return
            cost = quantity * price * (1 + self.commission + self.slippage)
        
        self.cash -= cost
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        self.trades.append(Trade(str(date.date()), symbol, 'buy', quantity, price, cost * self.commission))
    
    def _sell(self, date, symbol: str, quantity: int, price: float):
        """卖出"""
        if symbol not in self.positions:
            return
        quantity = min(quantity, self.positions[symbol])
        
        proceed = quantity * price * (1 - self.commission - self.slippage)
        self.cash += proceed
        self.positions[symbol] -= quantity
        
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        
        self.trades.append(Trade(str(date.date()), symbol, 'sell', quantity, price, proceed * self.commission))
    
    def _calc_portfolio_value(self, date, prices: pd.Series) -> float:
        """计算组合市值"""
        position_value = 0
        for symbol, quantity in self.positions.items():
            if symbol in prices:
                position_value += quantity * prices[symbol]
        return self.cash + position_value
    
    def get_results(self) -> Dict:
        """获取回测结果"""
        df = pd.DataFrame(self.portfolio_value)
        returns = df['value'].pct_change().dropna()
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': df['value'].iloc[-1] if len(df) > 0 else self.initial_capital,
            'total_return': (df['value'].iloc[-1] / self.initial_capital - 1) if len(df) > 0 else 0,
            'trades': self.trades,
            'portfolio_value': df,
            'returns': returns
        }
    ```

### Step 4: 测试通过后提交

```bash
git add src/backtest/ tests/backtest/
git commit -m "feat: add backtest engine"
```

---

## Task 5: 绩效指标

**Files:**
- Create: `src/metrics/__init__.py`
- Create: `src/metrics/performance.py`
- Create: `tests/metrics/test_performance.py`

### Step 1: 测试用例

```python
# tests/metrics/test_performance.py
import pytest
import pandas as pd
import numpy as np
from src.metrics.performance import PerformanceMetrics

def test_performance_metrics():
    """测试绩效指标"""
    returns = pd.Series([0.01, -0.02, 0.03, 0.02, -0.01])
    metrics = PerformanceMetrics()
    result = metrics.compute(returns)
    
    assert 'total_return' in result
    assert 'annual_return' in result
    assert 'sharpe_ratio' in result
    assert 'max_drawdown' in result
```

### Step 2: 运行测试确认失败

```bash
pytest tests/metrics/test_performance.py::test_performance_metrics -v
```

### Step 3: 实现绩效指标

```python
# src/metrics/performance.py
import pandas as pd
import numpy as np
from typing import Dict

class PerformanceMetrics:
    """绩效指标计算"""
    
    def __init__(self, days_per_year: int = 252):
        self.days_per_year = days_per_year
    
    def compute(self, returns: pd.Series) -> Dict[str, float]:
        """计算绩效指标
        
        Args:
            returns: 日收益率序列
        """
        if len(returns) == 0:
            return self._empty_metrics()
        
        total_return = (1 + returns).prod() - 1
        annual_return = (1 + total_return) ** (self.days_per_year / len(returns)) - 1
        sharpe = self._sharpe_ratio(returns)
        max_dd = self._max_drawdown(returns)
        calmar = annual_return / abs(max_dd) if max_dd != 0 else 0
        
        win_rate = (returns > 0).sum() / len(returns)
        avg_win = returns[returns > 0].mean() if (returns > 0).any() else 0
        avg_loss = returns[returns < 0].mean() if (returns < 0).any() else 0
        profit_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'calmar_ratio': calmar,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_loss_ratio': profit_loss_ratio,
            'num_trades': len(returns),
            'volatility': returns.std() * np.sqrt(self.days_per_year)
        }
    
    def _sharpe_ratio(self, returns: pd.Series) -> float:
        """夏普比率"""
        if returns.std() == 0:
            return 0
        return returns.mean() / returns.std() * np.sqrt(self.days_per_year)
    
    def _max_drawdown(self, returns: pd.Series) -> float:
        """最大回撤"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = cumulative / running_max - 1
        return drawdown.min()
    
    def _empty_metrics(self) -> Dict[str, float]:
        return {
            'total_return': 0,
            'annual_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'calmar_ratio': 0,
            'win_rate': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_loss_ratio': 0,
            'num_trades': 0,
            'volatility': 0
        }
```

### Step 4: 测试通过后提交

```bash
git add src/metrics/ tests/metrics/
git commit -m "feat: add performance metrics"
```

---

## Task 6: 组合管理

**Files:**
- Create: `src/portfolio/__init__.py`
- Create: `src/portfolio/manager.py`
- Create: `src/portfolio/optimizer.py`

### Step 1: 实现组合管理

```python
# src/portfolio/manager.py
import pandas as pd
import numpy as np
from typing import Dict, List

class PortfolioManager:
    """组合管理"""
    
    def __init__(self, max_positions: int = 10):
        self.max_positions = max_positions
    
    def allocate_equal(self, selected: pd.Series, capital: float, prices: pd.Series) -> Dict[str, int]:
        """等权分配
        
        Returns:
            dict[symbol] -> quantity
        """
        n = min(len(selected), self.max_positions)
        per_position = capital / n
        
        positions = {}
        for symbol in selected.head(n).index:
            if symbol in prices:
                quantity = int(per_position / prices[symbol])
                if quantity > 0:
                    positions[symbol] = quantity
        
        return positions
    
    def allocate_by_factor(self, selected: pd.Series, capital: float, prices: pd.Series) -> Dict[str, int]:
        """按因子值加权分配"""
        n = min(len(selected), self.max_positions)
        weights = selected.head(n)
        weights = weights / weights.sum()
        total_value = capital
        
        positions = {}
        for symbol in weights.index:
            if symbol in prices:
                value = total_value * weights[symbol]
                quantity = int(value / prices[symbol])
                if quantity > 0:
                    positions[symbol] = quantity
        
        return positions

class RiskParityOptimizer:
    """风险平价优化 (简化版)"""
    
    def __init__(self, max_positions: int = 10):
        self.max_positions = max_positions
    
    def optimize(self, returns: pd.DataFrame, capital: float) -> pd.Series:
        """风险平价优化
        
        Args:
            returns: 各股票的收益率矩阵
        """
        cov = returns.cov()
        inv_var = 1 / np.diag(cov)
        weights = inv_var / inv_var.sum()
        
        return pd.Series(weights, index=returns.columns)
```

### Step 2: 提交

```bash
git add src/portfolio/
git commit -m "feat: add portfolio management"
```

---

## Task 7: 风控模块

**Files:**
- Create: `src/risk/__init__.py`
- Create: `src/risk/stop_loss.py`
- Create: `src/risk/limits.py`

### Step 1: 实现风控

```python
# src/risk/stop_loss.py
import pandas as pd
from typing import Dict

class StopLoss:
    """止损规则"""
    
    def __init__(self, stop_pct: float = -0.10):
        self.stop_pct = stop_pct
    
    def should_stop(self, entry_price: float, current_price: float) -> bool:
        """是否触发止损"""
        return (current_price / entry_price - 1) <= self.stop_pct

class TimeStop:
    """时间止损"""
    
    def __init__(self, max_days: int = 20):
        self.max_days = max_days
    
    def should_stop(self, hold_days: int) -> bool:
        return hold_days >= self.max_days

# src/risk/limits.py
class PositionLimits:
    """仓位限制"""
    
    def __init__(self, max_single_weight: float = 0.2):
        self.max_single_weight = max_single_weight
    
    def check(self, symbol: str, value: float, total_value: float) -> bool:
        return value / total_value <= self.max_single_weight
```

### Step 2: 提交

```bash
git add src/risk/
git commit -m "feat: add risk management module"
```

---

## Task 8: Streamlit UI

**Files:**
- Create: `src/app.py`
- Create: `requirements.txt`

### Step 1: 实现 Streamlit 应用

```python
# src/app.py
import streamlit as st
import pandas as pd
import plotly as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="A股回测平台", layout="wide")
st.title("A股选股策略回测平台")

st.sidebar.header("参数设置")
initial_capital = st.sidebar.number_input("初始资金", value=100000)
max_positions = st.sidebar.slider("最大持仓", 3, 30, 10)

tab1, tab2, tab3 = st.tabs(["回测", "因子库", "策略"])

with tab1:
    st.header("运行回测")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("选择因子和信号...")
    
    if st.button("运行回测"):
        st.info("回测功能开发中...")
        st.write("请先在因子库配置策略参数")

with tab2:
    st.header("因子库")
    st.write("内置因子: PE, PB, MarketCap, ROE, Momentum")

with tab3:
    st.header("策略管理")
    st.write("策略文件目录: strategies/")
```

### Step 2: requirements.txt

```text
pandas>=2.0.0
numpy>=1.24.0
akshare>=1.12.0
streamlit>=1.30.0
plotly>=5.18.0
pyarrow>=14.0.0
```

### Step 3: 提交

```bash
git add src/app.py requirements.txt
git commit -m "feat: add streamlit ui"
```

---

## Task 9: 整合测试

### Step 1: 集成测试

```bash
# 确保各模块能正确导入
python -c "from src.data import fetcher; from src.factors import base; from src.signals import generator; from src.backtest import engine; from src.metrics import performance; print('All imports OK')"
```

### Step 2: 运行所有测试

```bash
pytest tests/ -v
```

---

## 执行计划完成

**Plan saved to:** `docs/superpowers/plans/2026-04-26-strategy-backtesting-platform.md`

---

**"Plan complete and saved to `docs/superpowers/plans/2026-04-26-strategy-backtesting-platform.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?"**