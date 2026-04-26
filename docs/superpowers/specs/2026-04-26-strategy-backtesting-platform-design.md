# A股选股策略回测平台 - 设计规范

**目标**: 构建个人投资研究用的A股策略回测平台，支持灵活策略验证

## 1. 技术栈

- **语言**: Python
- **数据存储**: SQLite + Parquet (本地文件)
- **数据源**: akShare (免费开源)
- **计算**: Pandas + NumPy
- **可视化**: Streamlit + Plotly
- **回测框架**: 自研 (轻量灵活)

## 2. 整体架构

```
用户界面 (Streamlit)
       ↓
┌──────────────────────────────────────┐
│            核心模块                  │
│  ┌─────────┐  ┌─────────┐        │
│  │ 因子引擎 │  │ 信号生成 │        │
│  └─────────┘  └─────────┘        │
│  ┌─────────┐  ┌─────────┐        │
│  │ 回测引擎 │  │ 风控模块 │        │
│  └─────────┘  └─────────┘        │
│  ┌──────────────────────────┐    │
│  │       组合管理           │    │
│  └──────────────────────────┘    │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│             数据层                    │
│  数据获取 → 本地缓存 → 股票池管理     │
└──────────────────────────────────────┘
```

## 3. 核心功能

### 3.1 数据管理

- **数据获取**: 通过 akShare 获取A股行情/财务数据
- **本地缓存**: Parquet 格式存储，支持增量更新
- **股票池管理**: 支持自定义股票池 (自选股/行业板块)

### 3.2 因子与信号

- **内置因子**:
  - 估值因子: PE、PB、PS、PCF
  - 规模因子: 总市值、流通市值
  - 质量因子: ROE、ROA、毛利率、资产负债率
  - 动量因子: 20日/60日/120日涨跌幅
- **自定义因子**: 支持 pandas 表达式
- **信号生成**: 买入/卖出/持有信号

### 3.3 组合管理

- **仓位分配**: 固定仓位、等权配置、按因子权重
- **仓位优化**: 风险平价 (简化版)
- **个股限制**: 单股最大权重、单股最大股数

### 3.4 风控模块

- **止损规则**: 单股止损比例、持有期止损
- **组合风控**: 最大回撤限制、单一行业上限
- **黑名单**: 退市风险、ST股票排除

### 3.5 回测引擎

- **调仓频率**: 日频/周频/月频
- **成本模拟**: 手续费、滑点
- **事件记录**: 每次调仓记录

### 3.6 绩效分析

- **收益指标**: 年化收益、夏普比率、最大回撤、卡玛比率
- **交易统计**: 胜率、盈亏比、交易次数
- **可视化**: 权益曲线、回撤曲线、收益分布

## 4. 目录结构

```
quant-platform/
├── src/
│   ├── data/
│   │   ├── fetcher.py      # 数据获取
│   │   ├── cache.py       # 本地缓存
│   │   └── pool.py       # 股票池管理
│   ├── factors/
│   │   ├── base.py       # 基础因子
│   │   └── registry.py   # 因子注册表
│   ├── signals/
│   │   ├── generator.py  # 信号生成
│   │   └── registry.py   # 信号注册表
│   ├── portfolio/
│   │   ├── manager.py   # 组合管理
│   │   └── optimizer.py # 仓���优化
│   ├── backtest/
│   │   ├── engine.py     # 回测引擎
│   │   └── recorder.py  # 交易记录
│   ├── risk/
│   │   ├── stop_loss.py # 止损规则
│   │   └── limits.py    # 组合限制
│   ├── metrics/
│   │   ├── performance.py  # 绩效指标
│   │   └── attribution.py  # 归因分析
│   └── app.py           # Streamlit 入口
├── strategies/         # 策略文件
├── cache/              # 数据缓存
├── outputs/            # 回测结果
└── tests/              # 测试
```

## 5. 核心接口

### 5.1 Factor (因子)

```python
class Factor:
    name: str
    def compute(self, data: DataFrame) -> Series:
        pass
```

### 5.2 Signal (信号)

```python
class Signal:
    name: str
    def generate(self, factors: Dict[str, Series]) -> Series:
        pass
```

### 5.3 Strategy (策略)

```python
class Strategy:
    name: str
    factors: List[Factor]
    signal: Signal
    rebalance_freq: str  # 'D', 'W', 'M'
    
    def get_weights(self, date: Date, data: DataFrame) -> Series:
        pass
```

### 5.4 BacktestResult (回测结果)

```python
@dataclass
class BacktestResult:
    returns: Series
    positions: DataFrame
    trades: List[Trade]
    metrics: Dict[str, float]
```

## 6. 实施顺序

1. 数据层 (fetcher + cache)
2. 因子引擎基础
3. 信号生成
4. 回测引擎
5. 绩效指标
6. 组合管理
7. 风控模块
8. Streamlit UI

---

**创建时间**: 2026-04-26