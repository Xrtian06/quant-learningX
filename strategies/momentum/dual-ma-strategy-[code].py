"""
标题: 双均线动量策略（纯逻辑版）
作者: quant-learner
日期: 2026-04-17
标签: [code]
描述: 使用短期均线和长期均线的交叉产生买卖信号，是最经典的动量策略之一
"""

import pandas as pd
import numpy as np

# ============== 1. 准备数据 ==============
# 这里用随机数据模拟，实际使用时替换为真实股票数据
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='B')
prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.8)
df = pd.DataFrame({'close': prices}, index=dates)

# ============== 2. 计算指标 ==============
short_window = 20   # 短期均线
long_window = 60    # 长期均线

df['ma_short'] = df['close'].rolling(window=short_window).mean()
df['ma_long'] = df['close'].rolling(window=long_window).mean()

# ============== 3. 生成交易信号 ==============
# signal: 1 = 多头, 0 = 空仓
# 金叉：短期均线上穿长期均线 → 买入
# 死叉：短期均线下穿长期均线 → 卖出
df['signal'] = 0
df['signal'][short_window:] = np.where(
    df['ma_short'][short_window:] > df['ma_long'][short_window:], 1, 0
)

# 交易点：信号变化的位置
df['position'] = df['signal'].diff()

# ============== 4. 策略回测（简化版） ==============
# 假设可以全仓买卖，不考虑手续费和滑点
df['returns'] = df['close'].pct_change()
df['strategy_returns'] = df['signal'].shift(1) * df['returns']

# 累计收益
df['cumulative_market'] = (1 + df['returns']).cumprod()
df['cumulative_strategy'] = (1 + df['strategy_returns']).cumprod()

# ============== 5. 绩效指标 ==============
# 年化收益率
trading_days = 252
total_return_strategy = df['cumulative_strategy'].iloc[-1] - 1
annual_return_strategy = (1 + total_return_strategy) ** (trading_days / len(df)) - 1

total_return_market = df['cumulative_market'].iloc[-1] - 1
annual_return_market = (1 + total_return_market) ** (trading_days / len(df)) - 1

# 最大回撤
strategy_peak = df['cumulative_strategy'].cummax()
strategy_drawdown = (df['cumulative_strategy'] - strategy_peak) / strategy_peak
max_drawdown = strategy_drawdown.min()

# 夏普比率（简化版，假设无风险利率为0）
sharpe_ratio = np.sqrt(trading_days) * df['strategy_returns'].mean() / df['strategy_returns'].std()

# ============== 6. 输出结果 ==============
print(f"\n========== 双均线策略回测结果 ==========")
print(f"短期均线: {short_window}日 | 长期均线: {long_window}日")
print(f"策略年化收益: {annual_return_strategy:.2%}")
print(f"基准年化收益: {annual_return_market:.2%}")
print(f"最大回撤: {max_drawdown:.2%}")
print(f"夏普比率: {sharpe_ratio:.2f}")
print(f"交易次数: {abs(df['position']).sum() / 2:.0f} 次")

# ============== 7. 买卖点示例 ==============
buy_signals = df[df['position'] == 1]
sell_signals = df[df['position'] == -1]

print(f"\n最近 3 次买入信号:")
print(buy_signals[['close', 'ma_short', 'ma_long']].tail(3))

print(f"\n最近 3 次卖出信号:")
print(sell_signals[['close', 'ma_short', 'ma_long']].tail(3))

print("\n✅ 双均线策略逻辑演示完成")
print("提示：这是简化版回测，未考虑交易成本、滑点、涨跌停等因素。")
