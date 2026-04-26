# A股量化回测平台

基于 Python 的 A股量化投资回测系统，支持因子选股、信号生成、回测引擎、风险管理等完整流程。

## 功能特性

- **数据获取** - 实时获取A股行情、指数成分股、财务数据
- **因子库** - 内置多种选股因子（PE、ROE、MACD等）
- **信号生成** - 支持Top-N、阈值、复合信号等选股策略
- **回测引擎** - 支持日线级别回测，模拟真实交易
- **风险管理** - 内置止损机制、仓位限制
- **绩效分析** - 计算收益率、夏普比率、最大回撤等指标
- **Web界面** - Streamlit交互式回测平台

## 目录结构

```
quant-platform/
├── src/
│   ├── data/          # 数据获取与缓存
│   │   ├── fetcher.py  # A股数据获取
│   │   ├── pool.py     # 股票池管理
│   │   └── cache.py    # 数据缓存
│   ├── factors/        # 因子管理
│   │   ├── base.py     # 因子基类
│   │   └── registry.py # 因子注册
│   ├── signals/       # 信号生成
│   │   ├── generator.py
│   │   └── registry.py
│   ├── backtest/      # 回测引擎
│   │   └── engine.py
│   ├── portfolio/      # 组合管理
│   │   ├── manager.py
│   │   └── optimizer.py
│   ├── risk/          # 风险管理
│   │   ├── stop_loss.py
│   │   └── limits.py
│   ├── metrics/       # 绩效指标
│   │   └── performance.py
│   └── app.py         # Web应用入口
├── tests/             # 单元测试
├── strategies/        # 策略文件
└── requirements.txt
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动Web界面

```bash
streamlit run src/app.py
```

### 命令行回测示例

```python
from src.backtest.engine import BacktestEngine
from src.data.fetcher import StockFetcher
import pandas as pd

# 获取数据
fetcher = StockFetcher()
df = fetcher.get_stock_daily('600519.SH', '2023-01-01', '2024-01-01')

# 定义信号（月末调仓，买入100股）
signals = {
    '2023-06-30': {'600519.SH': 100},
    '2023-07-31': {'600519.SH': 100},
}

# 运行回测
engine = BacktestEngine(initial_capital=100000, commission=0.0003)
engine.run(df, signals)
result = engine.get_results()

print(f"总收益率: {(result.final_value - result.initial_capital) / result.initial_capital:.2%}")
```

## 模块说明

### 数据层 (data/)

| 模块 | 功能 |
|------|------|
| `fetcher.py` | 获取A股日线数据、指数成分股、个股信息 |
| `pool.py` | 股票池管理（沪深300、中证2000） |
| `cache.py` | 数据缓存，避免重复请求 |

### 因子层 (factors/)

内置因子：
- `pe_ratio` - 市盈率
- `pb_ratio` - 市净率
- `roe` - 净资产收益率
- `macd` - MACD指标
- `volume_ratio` - 量比

### 信号层 (signals/)

支持信号类型：
- `top_n` - 选取因子值最高/最低的N只股票
- `threshold` - 阈值过滤
- `composite` - 多因子复合信号

### 回测层 (backtest/)

- 模拟真实交易（买入/卖出、费用计算）
- 记录每日权益曲线
- 生成交易清单

### 风险管理 (risk/)

- `stop_loss.py` - 移动止损、百分比止损
- `limits.py` - 单票仓位限制、总仓位限制

### 绩效分析 (metrics/)

- 总收益率
- 年化收益率
- 夏普比率
- 最大回撤
- 总手续费

## 数据来源

使用 [akshare](https://akshare.akfamily.xyz/) 获取数据：
- 股票日线行情
- 指数成分股列表
- 个股基本信息

## 技术栈

- **Python 3.10+**
- **pandas** - 数据处理
- **akshare** - 金融数据获取
- **streamlit** - Web界面
- **plotly** - 图表可视化

## License

MIT