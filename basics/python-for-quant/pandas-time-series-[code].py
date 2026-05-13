"""
标题: Pandas 时间序列基础操作
作者: quant-learner
日期: 2026-04-17
标签: [code]
描述: 量化交易中常见的时间序列数据处理操作，包括重采样、移动平均、滞后变量等
"""

import pandas as pd
import numpy as np

# 生成示例数据：一年的日度股价数据
np.random.seed(42)
dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='B')  # 工作日
prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
df = pd.DataFrame({'close': prices}, index=dates)

print("=== 原始数据前5行 ===")
print(df.head())

# 1. 计算收益率
df['returns'] = df['close'].pct_change()

# 2. 计算移动平均线（双均线）
df['ma_20'] = df['close'].rolling(window=20).mean()
df['ma_60'] = df['close'].rolling(window=60).mean()

# 3. 重采样：日数据 → 周数据
weekly = df['close'].resample('W').last()
weekly_returns = weekly.pct_change()

print("\n=== 周度收盘价前5个 ===")
print(weekly.head())

# 4. 滞后变量（用于预测模型）
df['close_lag1'] = df['close'].shift(1)
df['returns_lag1'] = df['returns'].shift(1)

# 5. 按月份分组统计
df['month'] = df.index.month
monthly_stats = df.groupby('month')['returns'].agg(['mean', 'std', 'count'])

print("\n=== 月度收益率统计 ===")
print(monthly_stats)

# 保存示例（实际使用时注意 .gitignore 屏蔽大文件）
# df.to_csv('sample-time-series.csv')

print("\n✅ Pandas 时间序列基础操作示例完成")
