"""
标题: [策略名称] - 回测代码
作者: quant-learner
日期: YYYY-MM-DD
标签: [backtest]
描述: 对 [策略名称] 进行简化回测，计算关键绩效指标
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# 把当前目录加入路径，以便导入 strategy-[code].py
sys.path.append(str(Path(__file__).parent))

# 注意：因为 Python 导入不能包含方括号，实际使用时请把文件名中的方括号去掉
# 例如：from strategy_code import load_data, generate_signals
# from strategy___code__ import load_data, generate_signals


def backtest(df: pd.DataFrame, params: dict) -> dict:
    """
    执行简化回测

    Returns
    -------
    dict : 包含回测结果和绩效指标
    """
    # 实际使用时，导入并调用 generate_signals
    # df = generate_signals(df, params)

    # 示例：直接计算一些简单信号
    short_window = params.get('short_window', 20)
    long_window = params.get('long_window', 60)
    df['ma_short'] = df['close'].rolling(window=short_window).mean()
    df['ma_long'] = df['close'].rolling(window=long_window).mean()
    df['signal'] = 0
    df.loc[df.index[short_window:], 'signal'] = np.where(
        df['ma_short'].iloc[short_window:] > df['ma_long'].iloc[short_window:], 1, 0
    )

    # 计算每日收益率
    df['returns'] = df['close'].pct_change()

    # 策略收益：按前一日信号持仓
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']

    # 累计收益曲线
    df['cum_market'] = (1 + df['returns']).cumprod()
    df['cum_strategy'] = (1 + df['strategy_returns']).cumprod()

    # 绩效指标计算
    trading_days = 252
    total_return = df['cum_strategy'].iloc[-1] - 1
    annual_return = (1 + total_return) ** (trading_days / len(df)) - 1

    # 最大回撤
    peak = df['cum_strategy'].cummax()
    drawdown = (df['cum_strategy'] - peak) / peak
    max_drawdown = drawdown.min()

    # 夏普比率（简化版，无风险利率=0）
    sharpe = np.sqrt(trading_days) * df['strategy_returns'].mean() / df['strategy_returns'].std()

    # 胜率
    trades = df['strategy_returns'][df['strategy_returns'] != 0]
    win_rate = (trades > 0).sum() / len(trades) if len(trades) > 0 else 0

    # 交易次数
    trade_count = abs(df['signal'].diff()).sum() / 2

    results = {
        'total_return': total_return,
        'annual_return': annual_return,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe,
        'win_rate': win_rate,
        'trade_count': trade_count,
        'df': df
    }

    return results


def print_results(results: dict):
    """打印回测结果"""
    print("\n" + "=" * 40)
    print("📊 回测结果")
    print("=" * 40)
    print(f"总收益率:     {results['total_return']:.2%}")
    print(f"年化收益率:   {results['annual_return']:.2%}")
    print(f"最大回撤:     {results['max_drawdown']:.2%}")
    print(f"夏普比率:     {results['sharpe_ratio']:.2f}")
    print(f"胜率:         {results['win_rate']:.2%}")
    print(f"交易次数:     {results['trade_count']:.0f}")
    print("=" * 40)
    print("⚠️ 注意：这是简化回测，未考虑交易成本、滑点和涨跌停限制。")


def load_data():
    """加载示例数据"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='B')
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.8)
    return pd.DataFrame({'close': prices}, index=dates)


if __name__ == '__main__':
    params = {
        'short_window': 20,
        'long_window': 60
    }

    df = load_data()
    results = backtest(df, params)
    print_results(results)
