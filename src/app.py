import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

from src.factors.registry import FACTOR_REGISTRY
from src.signals.registry import get_signal
from src.backtest.engine import BacktestEngine


st.set_page_config(page_title="A股回测平台", layout="wide")

st.title("A股回测平台")


def calculate_performance_metrics(result) -> pd.DataFrame:
    equity = result.equity_curve
    if equity.empty:
        return pd.DataFrame()
    
    total_return = (result.final_value - result.initial_capital) / result.initial_capital * 100
    days = (equity.index[-1] - equity.index[0]).days
    annual_return = total_return / days * 252 if days > 0 else 0
    
    equity_curve = equity['value']
    returns = equity_curve.pct_change().dropna()
    sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
    
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    max_drawdown = drawdown.min() * 100
    
    metrics = pd.DataFrame({
        '指标': ['初始资金', '最终资金', '总收益率(%)', '年化收益率(%)', '夏普比率', '最大回撤(%)', '总手续费'],
        '值': [
            f"¥{result.initial_capital:,.2f}",
            f"¥{result.final_value:,.2f}",
            f"{total_return:.2f}",
            f"{annual_return:.2f}",
            f"{sharpe:.2f}",
            f"{max_drawdown:.2f}",
            f"¥{result.total_commission:,.2f}"
        ]
    })
    return metrics


def run_placeholder_backtest(start_date, end_date, pool, factor, signal_type, initial_capital, max_positions, commission):
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    dates = [d for d in dates if d.weekday() < 5]
    
    np.random.seed(42)
    symbols = {'沪深300': ['SH600000', 'SH600016', 'SH600019', 'SH600028', 'SH600030'],
              '中证500': ['SH600000', 'SH600015', 'SH600028', 'SH600030', 'SH600060'],
              '自选': ['SH600000', 'SH600016', 'SH600028']}[pool]
    
    data = {}
    for sym in symbols:
        prices = 10 + np.random.randn(len(dates)).cumsum()
        prices = np.maximum(prices, 5)
        data[sym] = prices
    
    prices_df = pd.DataFrame(data, index=dates)
    prices_df.index.name = 'date'
    
    signals = {}
    for i, date in enumerate(dates):
        if i % 5 == 0:
            date_str = date.strftime('%Y-%m-%d')
            signals[date_str] = {}
            n = min(max_positions, len(symbols))
            selected = np.random.choice(symbols, n, replace=False)
            for sym in selected:
                signals[date_str][sym] = 100
    
    engine = BacktestEngine(initial_capital=initial_capital, commission=commission)
    engine.run(prices_df, signals)
    return engine.get_results()


with st.sidebar:
    st.header("参数设置")
    initial_capital = st.number_input("初始资金", value=100000, step=10000)
    max_positions = st.number_input("最大持仓", value=10, step=1, min_value=1)
    commission = st.number_input("手续费率", value=0.0003, format="%.4f")


tab1, tab2, tab3 = st.tabs(["回测", "因子库", "策略"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        factor = st.selectbox("选择因子", list(FACTOR_REGISTRY.keys()))
    with col2:
        signal_type = st.selectbox("信号类型", ["top_n", "threshold", "composite"])
    with col3:
        pool = st.selectbox("股票池", ["沪深300", "中证500", "自选"])
    with col4:
        n_select = st.number_input("选股数量", value=5, step=1, min_value=1)
    
    col5, col6 = st.columns(2)
    with col5:
        start_date = st.date_input("开始日期", value=datetime.today() - timedelta(days=365))
    with col6:
        end_date = st.date_input("结束日期", value=datetime.today())
    
    run_button = st.button("运行回测", type="primary")
    
    if run_button:
        with st.spinner("运行回测中..."):
            result = run_placeholder_backtest(
                start_date, end_date, pool, factor, signal_type,
                initial_capital, max_positions, commission
            )
        
        st.success("回测完成!")
        
        st.subheader("绩效指标")
        metrics = calculate_performance_metrics(result)
        st.table(metrics)
        
        st.subheader("权益曲线")
        if not result.equity_curve.empty:
            fig = px.line(result.equity_curve, x='date', y='value', 
                         title='账户权益曲线', labels={'value': '账户价值'})
            st.plotly_chart(fig, use_container_width=True)
        
        if result.trades:
            with st.expander("交易记录"):
                trades_df = pd.DataFrame([
                    {'日期': t.date, '股票': t.symbol, '操作': t.action, 
                     '数量': t.quantity, '价格': t.price, '手续费': t.commission}
                    for t in result.trades
                ])
                st.table(trades_df)

with tab2:
    st.subheader("内置因子")
    factor_info = []
    for name, cls in FACTOR_REGISTRY.items():
        factor_info.append({'名称': name, '类': cls.__name__, '描述': cls.__doc__.strip() if cls.__doc__ else ''})
    st.table(pd.DataFrame(factor_info))

with tab3:
    st.subheader("策略管理")
    st.info("策略文件放在 strategies/ 目录下")
    st.markdown("""
    ```text
    strategies/
    ├── example/
    │   └── strategy.py    # 策略文件示例
    └── README.md
    ```
    """)