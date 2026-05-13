"""
标题: 使用 AkShare 下载 A股历史行情数据
作者: quant-learner
日期: 2026-04-17
标签: [code], [data]
描述: 通过 akshare 获取单只股票的日K线数据，并保存为 CSV
"""

import akshare as ak
import pandas as pd

# 获取贵州茅台（600519）的历史日线数据
stock_code = "600519"
stock_name = "贵州茅台"

print(f"正在下载 {stock_name}({stock_code}) 的历史数据...")

# akshare 接口：stock_zh_a_hist
# 参数说明：
#   symbol: 股票代码
#   period: daily / weekly / monthly
#   start_date: 开始日期（YYYYMMDD）
#   end_date: 结束日期（YYYYMMDD）
#   adjust: qfq 前复权 / hfq 后复权 / "" 不复权

df = ak.stock_zh_a_hist(
    symbol=stock_code,
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"
)

print(f"下载完成，共 {len(df)} 条数据")
print(df.head())

# 简单的数据清洗
df.columns = [
    'date', 'open', 'close', 'high', 'low', 'volume',
    'amount', 'amplitude', 'pct_change', 'change_amount', 'turnover'
]
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# 计算额外指标：5日、20日均线
df['ma_5'] = df['close'].rolling(window=5).mean()
df['ma_20'] = df['close'].rolling(window=20).mean()

print("\n清洗后的数据预览：")
print(df[['date', 'open', 'close', 'high', 'low', 'volume', 'ma_5', 'ma_20']].tail())

# 保存到本地（小样本可以放入 git，大数据请加入 .gitignore）
# df.to_csv(f"{stock_code}_{stock_name}_daily.csv", index=False)

print("\n✅ 数据下载与处理完成")
print("提示：如需保存数据，请取消注释最后一行。大数据文件建议添加到 .gitignore 中。")
