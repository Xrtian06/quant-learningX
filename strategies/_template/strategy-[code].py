"""
标题: [策略名称] - 核心逻辑
作者: quant-learner
日期: YYYY-MM-DD
标签: [code]
描述: [一句话描述这个策略是干什么的]
"""

import pandas as pd
import numpy as np


def load_data():
    """加载数据（示例：生成随机数据）"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='B')
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.8)
    df = pd.DataFrame({'close': prices}, index=dates)
    return df


def generate_signals(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    根据策略逻辑生成交易信号

    Parameters
    ----------
    df : pd.DataFrame
        包含价格数据的 DataFrame，至少有一列 'close'
    params : dict
        策略参数字典

    Returns
    -------
    pd.DataFrame
        增加了 'signal' 列的 DataFrame
        signal: 1 = 做多, 0 = 空仓, -1 = 做空（如允许做空）
    """
    df = df.copy()

    # TODO: 在这里实现你的策略逻辑
    # 示例：简单的双均线信号
    short_window = params.get('short_window', 20)
    long_window = params.get('long_window', 60)

    df['ma_short'] = df['close'].rolling(window=short_window).mean()
    df['ma_long'] = df['close'].rolling(window=long_window).mean()

    df['signal'] = 0
    df.loc[df.index[short_window:], 'signal'] = np.where(
        df['ma_short'].iloc[short_window:] > df['ma_long'].iloc[short_window:], 1, 0
    )

    return df


def run_strategy(params: dict = None):
    """运行策略的主函数"""
    if params is None:
        params = {'short_window': 20, 'long_window': 60}

    df = load_data()
    df = generate_signals(df, params)

    print(f"\n策略参数: {params}")
    print(df[['close', 'ma_short', 'ma_long', 'signal']].dropna().tail(10))

    return df


if __name__ == '__main__':
    run_strategy()
