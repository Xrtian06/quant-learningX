# Phase 1：股票数据探索仪表盘 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建完整的股票数据获取、处理、分析、可视化流程，产出可复用的数据工具模块和一键分析仪表盘 Notebook。

**Architecture:** 采用模块化设计——`basics/data_utils.py` 封装可复用的数据获取和处理函数，`notebooks/phase1/` 存放按主题组织的 Jupyter Notebook（每周一个），`data/raw/` 存放下载的原始数据。 Notebook 从探索式逐步演进为封装函数，最终整合为输入股票代码即可输出完整报告的仪表盘。

**Tech Stack:** Python 3.10+, pandas, numpy, akshare, matplotlib, jupyter, pytest

---

## 📁 文件结构

```
quant-learning/
├── basics/                          # 可复用基础模块
│   ├── __init__.py
│   └── data_utils.py               # 数据获取、清洗、计算工具函数
├── data/                            # 数据目录
│   └── raw/                        # 原始下载数据
│       └── 000001_平安银行.csv      # 示例数据文件
├── notebooks/                       # Jupyter 学习笔记
│   └── phase1/
│       ├── 01_data_download.ipynb   # Week 1: 环境 + 数据获取
│       ├── 02_data_processing.ipynb # Week 2: 数据处理 + 均线计算
│       ├── 03_statistics.ipynb      # Week 3: 统计分析
│       └── 04_dashboard.ipynb       # Week 4: 整合仪表盘
├── tests/                           # 测试
│   └── basics/
│       └── test_data_utils.py
└── requirements.txt                 # 依赖（修改）
```

---

## Task 1: 项目初始化与环境配置

**Files:**
- Create: `tests/basics/test_data_utils.py`
- Modify: `requirements.txt`
- Create: `basics/__init__.py`

- [ ] **Step 1: 检查当前 Python 环境并安装依赖**

Run:
```powershell
cd E:\PYcharm\Python_code\quant-learning
python --version
pip install pandas numpy akshare matplotlib jupyter pytest
```

Expected: Python 3.10+，所有包安装成功无报错。

- [ ] **Step 2: 更新 requirements.txt**

Modify `requirements.txt` to add the new dependencies:

```text
pandas>=2.0.0
numpy>=1.24.0
akshare>=1.12.0
matplotlib>=3.7.0
jupyter>=1.0.0
pytest>=7.4.0
```

Keep any existing lines in the file.

- [ ] **Step 3: 创建项目目录结构**

Run:
```powershell
New-Item -ItemType Directory -Force -Path "basics"
New-Item -ItemType Directory -Force -Path "data/raw"
New-Item -ItemType Directory -Force -Path "notebooks/phase1"
New-Item -ItemType Directory -Force -Path "tests/basics"
New-Item -ItemType File -Path "basics/__init__.py"
```

Expected: All directories created successfully.

- [ ] **Step 4: 验证 akshare 能正常获取数据**

Create a quick verification script in a temporary cell or Python console:

```python
import akshare as ak

df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20230101", adjust="qfq")
print(df.head())
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
```

Expected: Output shows OHLCV data with columns like `日期`, `开盘`, `收盘`, `最高`, `最低`, `成交量`.

- [ ] **Step 5: Commit 初始化**

Run:
```bash
git add requirements.txt basics/ tests/ data/ notebooks/
git commit -m "chore: setup phase1 project structure and dependencies"
```

---

## Task 2: 数据获取模块 (Week 1 核心)

**Files:**
- Create: `basics/data_utils.py`
- Create: `tests/basics/test_data_utils.py`
- Create: `notebooks/phase1/01_data_download.ipynb`

- [ ] **Step 1: 写测试 — 验证数据获取函数格式**

Create `tests/basics/test_data_utils.py`:

```python
import pytest
import pandas as pd
from basics.data_utils import download_stock_data

def test_download_stock_data_columns():
    """验证下载的数据包含必需的列"""
    df = download_stock_data("000001", start_date="20240101", end_date="20240110")
    required_cols = ["日期", "开盘", "收盘", "最高", "最低", "成交量"]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"

def test_download_stock_data_types():
    """验证数据类型正确"""
    df = download_stock_data("000001", start_date="20240101", end_date="20240110")
    assert pd.api.types.is_datetime64_any_dtype(df["日期"])
    assert df["收盘"].dtype in ["float64", "int64"]
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```powershell
cd E:\PYcharm\Python_code\quant-learning
pytest tests/basics/test_data_utils.py -v
```

Expected: 2 FAILs with `ImportError: cannot import name 'download_stock_data' from 'basics.data_utils'`.

- [ ] **Step 3: 实现数据获取函数**

Create `basics/data_utils.py`:

```python
"""
量化学习 - 数据获取与处理工具模块
Phase 1: 股票数据探索仪表盘
"""

import akshare as ak
import pandas as pd


def download_stock_data(symbol: str, start_date: str, end_date: str = None, adjust: str = "qfq") -> pd.DataFrame:
    """
    下载A股历史行情数据

    Parameters
    ----------
    symbol : str
        股票代码，如 "000001"
    start_date : str
        开始日期，格式 "YYYYMMDD"
    end_date : str, optional
        结束日期，格式 "YYYYMMDD"，默认今天
    adjust : str
        复权方式: "qfq" 前复权, "hfq" 后复权, "" 不复权

    Returns
    -------
    pd.DataFrame
        包含列: 日期, 股票代码, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率
    """
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust=adjust)
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values("日期").reset_index(drop=True)
    return df


def save_to_csv(df: pd.DataFrame, filepath: str) -> None:
    """保存DataFrame到CSV，不保存索引"""
    df.to_csv(filepath, index=False, encoding="utf-8-sig")


def load_from_csv(filepath: str) -> pd.DataFrame:
    """从CSV加载数据，自动解析日期列"""
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"])
    return df
```

- [ ] **Step 4: 运行测试确认通过**

Run:
```powershell
pytest tests/basics/test_data_utils.py -v
```

Expected: 2 PASSes.

- [ ] **Step 5: 创建 Week 1 Notebook 并下载数据**

Create `notebooks/phase1/01_data_download.ipynb` with the following cells:

Cell 1 (imports):
```python
import sys
sys.path.append("../..")

from basics.data_utils import download_stock_data, save_to_csv
import pandas as pd
```

Cell 2 (download):
```python
# 下载平安银行近3年数据
symbol = "000001"
start_date = "20220401"
end_date = "20250401"

df = download_stock_data(symbol, start_date, end_date)
print(f"数据维度: {df.shape}")
print(f"日期范围: {df['日期'].min()} ~ {df['日期'].max()}")
df.head()
```

Cell 3 (save):
```python
# 保存到 data/raw/
filepath = f"../../data/raw/{symbol}_平安银行.csv"
save_to_csv(df, filepath)
print(f"数据已保存至: {filepath}")
```

Cell 4 (verify):
```python
from basics.data_utils import load_from_csv

df_loaded = load_from_csv(filepath)
print(f"加载后维度: {df_loaded.shape}")
df_loaded.tail()
```

Run all cells. Expected: Data saved to `data/raw/000001_平安银行.csv` with ~700 rows.

- [ ] **Step 6: Commit 数据获取模块**

Run:
```bash
git add basics/data_utils.py tests/basics/test_data_utils.py notebooks/phase1/01_data_download.ipynb data/raw/
git commit -m "feat(phase1): add stock data download module with tests"
```

---

## Task 3: 数据处理与指标计算 (Week 2 核心)

**Files:**
- Modify: `basics/data_utils.py`
- Modify: `tests/basics/test_data_utils.py`
- Create: `notebooks/phase1/02_data_processing.ipynb`

- [ ] **Step 1: 写测试 — 验证收益率和均线计算**

Add to `tests/basics/test_data_utils.py`:

```python
from basics.data_utils import calculate_returns, calculate_ma

def test_calculate_returns():
    """验证日收益率计算"""
    df = pd.DataFrame({
        "日期": pd.date_range("2024-01-01", periods=5),
        "收盘": [100, 102, 99, 105, 103]
    })
    result = calculate_returns(df)
    expected = [None, 0.02, -0.02941176, 0.06060606, -0.01904762]
    for i, exp in enumerate(expected):
        if exp is None:
            assert pd.isna(result["日收益率"].iloc[i])
        else:
            assert abs(result["日收益率"].iloc[i] - exp) < 1e-6

def test_calculate_ma():
    """验证移动平均线计算"""
    df = pd.DataFrame({
        "日期": pd.date_range("2024-01-01", periods=10),
        "收盘": list(range(10, 20))
    })
    result = calculate_ma(df, windows=[3, 5])
    # MA3 of [10,11,12] = 11
    assert result["MA3"].iloc[2] == 11.0
    # MA5 of [10,11,12,13,14] = 12
    assert result["MA5"].iloc[4] == 12.0
    # First 4 rows of MA5 should be NaN
    assert result["MA5"].iloc[:4].isna().all()
```

- [ ] **Step 2: 运行测试确认失败**

Run:
```powershell
pytest tests/basics/test_data_utils.py::test_calculate_returns tests/basics/test_data_utils.py::test_calculate_ma -v
```

Expected: 2 FAILs with `ImportError`.

- [ ] **Step 3: 实现收益率和均线函数**

Add to `basics/data_utils.py`:

```python

def calculate_returns(df: pd.DataFrame, price_col: str = "收盘") -> pd.DataFrame:
    """
    计算日收益率和对数收益率

    Parameters
    ----------
    df : pd.DataFrame
        包含价格数据的DataFrame
    price_col : str
        价格列名

    Returns
    -------
    pd.DataFrame
        新增列: 日收益率, 对数收益率
    """
    df = df.copy()
    df["日收益率"] = df[price_col].pct_change()
    df["对数收益率"] = np.log(df[price_col] / df[price_col].shift(1))
    return df


def calculate_ma(df: pd.DataFrame, price_col: str = "收盘", windows: list = None) -> pd.DataFrame:
    """
    计算简单移动平均线

    Parameters
    ----------
    df : pd.DataFrame
        包含价格数据的DataFrame
    price_col : str
        价格列名
    windows : list
        移动平均窗口列表，如 [5, 10, 20]

    Returns
    -------
    pd.DataFrame
        新增列: MA{window}
    """
    if windows is None:
        windows = [5, 10, 20]
    df = df.copy()
    for window in windows:
        df[f"MA{window}"] = df[price_col].rolling(window=window).mean()
    return df
```

Also add `import numpy as np` at the top of `basics/data_utils.py` if not already present.

- [ ] **Step 4: 运行测试确认通过**

Run:
```powershell
pytest tests/basics/test_data_utils.py -v
```

Expected: 4 PASSes.

- [ ] **Step 5: 创建 Week 2 Notebook**

Create `notebooks/phase1/02_data_processing.ipynb` with cells:

Cell 1 (load data):
```python
import sys
sys.path.append("../..")

from basics.data_utils import load_from_csv, calculate_returns, calculate_ma
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

df = load_from_csv("../../data/raw/000001_平安银行.csv")
print(f"原始数据: {df.shape}")
df.head()
```

Cell 2 (calculate indicators):
```python
df = calculate_returns(df)
df = calculate_ma(df, windows=[5, 20, 60])
print("新增列:", [c for c in df.columns if c not in ["日期", "开盘", "收盘", "最高", "最低", "成交量"]])
df[["日期", "收盘", "日收益率", "MA5", "MA20", "MA60"]].tail()
```

Cell 3 (visualize price and MA):
```python
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(df["日期"], df["收盘"], label="收盘价", linewidth=1, alpha=0.8)
ax.plot(df["日期"], df["MA5"], label="MA5", linewidth=1, alpha=0.7)
ax.plot(df["日期"], df["MA20"], label="MA20", linewidth=1.5, alpha=0.7)
ax.plot(df["日期"], df["MA60"], label="MA60", linewidth=1.5, alpha=0.7)

ax.set_title("平安银行 - 收盘价与移动平均线", fontsize=14)
ax.set_xlabel("日期")
ax.set_ylabel("价格 (元)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

Run all cells. Expected: Clean price chart with 3 MA lines overlaid.

- [ ] **Step 6: Commit 数据处理模块**

Run:
```bash
git add basics/data_utils.py tests/basics/test_data_utils.py notebooks/phase1/02_data_processing.ipynb
git commit -m "feat(phase1): add returns and moving average calculations with visualization"
```

---

## Task 4: 统计分析 (Week 3 核心)

**Files:**
- Modify: `basics/data_utils.py`
- Create: `notebooks/phase1/03_statistics.ipynb`

- [ ] **Step 1: 实现统计描述函数**

Add to `basics/data_utils.py`:

```python
from scipy import stats


def descriptive_stats(df: pd.DataFrame, return_col: str = "日收益率") -> dict:
    """
    计算收益率的描述性统计指标

    Returns
    -------
    dict
        包含: 均值, 标准差, 年化收益率, 年化波动率, 夏普比率(简化版), 偏度, 峰度, 最大单日涨幅, 最大单日跌幅
    """
    r = df[return_col].dropna()
    n = len(r)

    mean_return = r.mean()
    std_return = r.std()

    # 假设252个交易日/年
    annual_return = mean_return * 252
    annual_volatility = std_return * np.sqrt(252)

    # 简化夏普比率 (假设无风险利率为0)
    sharpe_ratio = annual_return / annual_volatility if annual_volatility != 0 else 0

    return {
        "样本数": n,
        "日均收益率(%)": round(mean_return * 100, 4),
        "日收益率标准差(%)": round(std_return * 100, 4),
        "年化收益率(%)": round(annual_return * 100, 2),
        "年化波动率(%)": round(annual_volatility * 100, 2),
        "夏普比率(简化)": round(sharpe_ratio, 3),
        "偏度": round(r.skew(), 4),
        "峰度": round(r.kurtosis(), 4),
        "最大单日涨幅(%)": round(r.max() * 100, 2),
        "最大单日跌幅(%)": round(r.min() * 100, 2),
    }


def correlation_analysis(df1: pd.DataFrame, df2: pd.DataFrame, return_col: str = "日收益率") -> float:
    """计算两只股票收益率的相关系数"""
    merged = pd.merge(
        df1[["日期", return_col]].rename(columns={return_col: "r1"}),
        df2[["日期", return_col]].rename(columns={return_col: "r2"}),
        on="日期"
    )
    return merged["r1"].corr(merged["r2"])
```

> Note: `scipy` should be added to `requirements.txt` if not already present.

- [ ] **Step 2: 更新依赖并写统计测试**

Add to `requirements.txt`:
```text
scipy>=1.10.0
```

Add to `tests/basics/test_data_utils.py`:

```python
from basics.data_utils import descriptive_stats

def test_descriptive_stats():
    """验证统计指标计算"""
    df = pd.DataFrame({
        "日收益率": [0.01, -0.01, 0.02, -0.005, 0.0]
    })
    result = descriptive_stats(df)
    assert result["样本数"] == 5
    assert "年化收益率" in result
    assert "夏普比率(简化)" in result
```

Run:
```powershell
pip install scipy
pytest tests/basics/test_data_utils.py::test_descriptive_stats -v
```

Expected: PASS.

- [ ] **Step 3: 创建 Week 3 Notebook**

Create `notebooks/phase1/03_statistics.ipynb` with key cells:

Cell 1 (load and compute stats):
```python
import sys
sys.path.append("../..")

from basics.data_utils import load_from_csv, calculate_returns, descriptive_stats, download_stock_data
import pandas as pd
import numpy as np

# 加载平安银行
df1 = load_from_csv("../../data/raw/000001_平安银行.csv")
df1 = calculate_returns(df1)

stats1 = descriptive_stats(df1)
print("=== 平安银行 描述性统计 ===")
for k, v in stats1.items():
    print(f"{k}: {v}")
```

Cell 2 (distribution plot):
```python
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 直方图 + 正态拟合
axes[0].hist(df1["日收益率"].dropna() * 100, bins=50, density=True, alpha=0.7, edgecolor="black")
axes[0].set_title("日收益率分布")
axes[0].set_xlabel("日收益率 (%)")
axes[0].set_ylabel("密度")
axes[0].axvline(0, color="red", linestyle="--", linewidth=1)

# Q-Q图
from scipy import stats
stats.probplot(df1["日收益率"].dropna(), dist="norm", plot=axes[1])
axes[1].set_title("Q-Q图 (正态分布)")

plt.tight_layout()
plt.show()
```

Cell 3 (correlation with another stock):
```python
# 下载另一只股票对比，例如 000002 万科A
df2 = download_stock_data("000002", start_date="20220401", end_date="20250401")
df2 = calculate_returns(df2)

corr = df1["日收益率"].corr(df2["日收益率"])
print(f"平安银行 vs 万科A 日收益率相关系数: {corr:.4f}")

# 散点图
import matplotlib.pyplot as plt

merged = pd.merge(
    df1[["日期", "日收益率"]].rename(columns={"日收益率": "平安"}),
    df2[["日期", "日收益率"]].rename(columns={"日收益率": "万科"}),
    on="日期"
)

plt.figure(figsize=(8, 6))
plt.scatter(merged["平安"] * 100, merged["万科"] * 100, alpha=0.5, s=20)
plt.xlabel("平安银行 日收益率 (%)")
plt.ylabel("万科A 日收益率 (%)")
plt.title(f"收益率散点图 (相关系数: {corr:.4f})")
plt.axhline(0, color="red", linestyle="--", linewidth=0.8)
plt.axvline(0, color="red", linestyle="--", linewidth=0.8)
plt.grid(True, alpha=0.3)
plt.show()
```

Run all cells. Expected: Statistical table, distribution histogram, and correlation scatter plot.

- [ ] **Step 4: 写 Week 3 微型摘要（论文训练）**

In the same notebook, add a markdown cell:

```markdown
## 📋 微型研究摘要

**研究对象**：平安银行（000001）2022年4月至2025年4月的日线数据

**方法**：计算日收益率、年化收益率、年化波动率、偏度、峰度；绘制收益率分布直方图并与正态分布比较；计算与万科A的收益率相关性

**主要发现**：
- （待填写：根据实际运行结果填写）
- 年化收益率约为 __%，年化波动率约为 __%
- 收益率分布的偏度为 __，峰度为 __，呈现（左偏/右偏/近似对称）特征
- 与万科A的相关系数为 __，表明两只股票（强/弱）相关

**结论与局限**：
- 本分析仅基于单只股票和有限时间段，结论不具备普遍代表性
- 未考虑分红、配股等公司事件对收益率的影响
```

- [ ] **Step 5: Commit 统计分析**

Run:
```bash
git add basics/data_utils.py tests/basics/test_data_utils.py notebooks/phase1/03_statistics.ipynb requirements.txt
git commit -m "feat(phase1): add descriptive statistics, distribution analysis, and correlation"
```

---

## Task 5: 整合仪表盘 (Week 4 核心)

**Files:**
- Modify: `basics/data_utils.py`
- Create: `notebooks/phase1/04_dashboard.ipynb`

- [ ] **Step 1: 实现仪表盘封装函数**

Add to `basics/data_utils.py`:

```python

def analyze_stock(symbol: str, start_date: str, end_date: str = None, benchmark_symbol: str = None) -> dict:
    """
    股票综合分析函数 — 一键生成分析报告所需的所有数据和图表

    Returns
    -------
    dict
        {
            "symbol": 股票代码,
            "data": 完整DataFrame,
            "stats": 描述性统计,
            "benchmark_corr": 与基准的相关系数 (如果有)
        }
    """
    df = download_stock_data(symbol, start_date, end_date)
    df = calculate_returns(df)
    df = calculate_ma(df, windows=[5, 20, 60])
    stats = descriptive_stats(df)

    result = {
        "symbol": symbol,
        "data": df,
        "stats": stats,
        "benchmark_corr": None,
    }

    if benchmark_symbol:
        df_benchmark = download_stock_data(benchmark_symbol, start_date, end_date)
        df_benchmark = calculate_returns(df_benchmark)
        corr = df["日收益率"].corr(df_benchmark["日收益率"])
        result["benchmark_corr"] = corr

    return result
```

- [ ] **Step 2: 创建 Week 4 仪表盘 Notebook**

Create `notebooks/phase1/04_dashboard.ipynb` as the final integrated notebook with these sections:

**Section 1: 参数配置**
```python
import sys
sys.path.append("../..")

from basics.data_utils import analyze_stock
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ========== 用户可修改参数 ==========
SYMBOL = "000001"
START_DATE = "20220401"
END_DATE = "20250401"
BENCHMARK = "000001"  # 可改为 "000300" 沪深300等
STOCK_NAME = "平安银行"
# ====================================
```

**Section 2: 数据获取与处理**
```python
result = analyze_stock(SYMBOL, START_DATE, END_DATE, BENCHMARK)
df = result["data"]
stats = result["stats"]

print(f"=== {STOCK_NAME} ({SYMBOL}) 分析报告 ===")
print(f"分析区间: {df['日期'].min().date()} ~ {df['日期'].max().date()}")
print(f"总交易日: {len(df)}")
```

**Section 3: 统计摘要表格**
```python
stats_df = pd.DataFrame(list(stats.items()), columns=["指标", "数值"])
stats_df
```

**Section 4: 多面板可视化**
```python
fig, axes = plt.subplots(3, 1, figsize=(14, 12), gridspec_kw={"height_ratios": [3, 1, 1]})

# Panel 1: 价格 + 均线
axes[0].plot(df["日期"], df["收盘"], label="收盘价", linewidth=1)
axes[0].plot(df["日期"], df["MA5"], label="MA5", alpha=0.7, linewidth=1)
axes[0].plot(df["日期"], df["MA20"], label="MA20", alpha=0.7, linewidth=1.5)
axes[0].plot(df["日期"], df["MA60"], label="MA60", alpha=0.7, linewidth=1.5)
axes[0].set_title(f"{STOCK_NAME} ({SYMBOL}) — 价格与均线", fontsize=14)
axes[0].legend(loc="upper left")
axes[0].grid(True, alpha=0.3)

# Panel 2: 成交量
axes[1].bar(df["日期"], df["成交量"], alpha=0.6, width=1)
axes[1].set_ylabel("成交量")
axes[1].grid(True, alpha=0.3)

# Panel 3: 日收益率分布
axes[2].hist(df["日收益率"].dropna() * 100, bins=60, alpha=0.7, edgecolor="black")
axes[2].axvline(0, color="red", linestyle="--", linewidth=1)
axes[2].set_xlabel("日收益率 (%)")
axes[2].set_ylabel("频数")
axes[2].set_title("日收益率分布")
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

**Section 5: 微型研究摘要（自动生成模板）**
```python
summary = f"""
## 📋 {STOCK_NAME} ({SYMBOL}) 微型研究摘要

**研究对象**：{STOCK_NAME}（{SYMBOL}）{df['日期'].min().date()} 至 {df['日期'].max().date()} 的日线数据

**方法**：下载历史行情数据，计算日收益率、移动平均线（5/20/60日）、描述性统计指标，绘制价格-均线-成交量-收益分布多面板图

**主要发现**：
- 分析区间内共 {len(df)} 个交易日
- 年化收益率约为 {stats['年化收益率(%)']}%，年化波动率约为 {stats['年化波动率(%)']}%
- 夏普比率（简化）为 {stats['夏普比率(简化)']}
- 收益率分布偏度为 {stats['偏度']}，峰度为 {stats['峰度']}
- 最大单日涨幅为 {stats['最大单日涨幅(%)']}%，最大单日跌幅为 {stats['最大单日跌幅(%)']}%

**结论与局限**：
- 本分析仅基于历史行情数据，未考虑基本面因素和宏观环境变化
- 统计指标对异常值敏感，极端行情可能影响结论稳健性
- 未来可扩展：加入更多技术指标、与基准指数的对比分析、不同市场环境下的分样本检验
"""

from IPython.display import Markdown
Markdown(summary)
```

Run all cells. Expected: A complete 3-panel dashboard with auto-generated summary.

- [ ] **Step 3: 验证仪表盘可复用性**

Change `SYMBOL` to another stock (e.g., `"000002"`) and `STOCK_NAME` to `"万科A"`, re-run all cells. Expected: Same analysis for the new stock without code changes.

- [ ] **Step 4: Commit 最终仪表盘**

Run:
```bash
git add basics/data_utils.py notebooks/phase1/04_dashboard.ipynb
git commit -m "feat(phase1): add integrated stock analysis dashboard"
```

---

## Task 6: Week 1-4 学习笔记与 README 更新

**Files:**
- Modify: `README.md`
- Create: `docs/学习笔记/phase1_每周总结.md`

- [ ] **Step 1: 创建学习笔记模板**

Create `docs/学习笔记/phase1_每周总结.md`:

```markdown
# Phase 1 学习笔记 — 股票数据探索仪表盘

## Week 1: 环境搭建与数据获取
**日期**: 2026-04-XX ~ 2026-04-XX
**学习内容**:
- 
**遇到的问题**:
- 
**解决方式**:
- 
**关键代码片段**:
```python
# 待填写
```

## Week 2: pandas 数据处理
**日期**: 2026-04-XX ~ 2026-04-XX
**学习内容**:
- 
**遇到的问题**:
- 
**解决方式**:
- 

## Week 3: 统计量化应用
**日期**: 2026-04-XX ~ 2026-04-XX
**学习内容**:
- 
**新认识的统计概念**:
- 

## Week 4: 仪表盘整合
**日期**: 2026-04-XX ~ 2026-04-XX
**学习内容**:
- 
**项目成果**:
- 
```

- [ ] **Step 2: 更新 README 最近更新表格**

Modify `README.md` to add:

```markdown
| 日期 | 更新内容 | 路径 |
|------|----------|------|
| 2026-04-17 | 仓库初始化，建立学习框架 | `/` |
| 2026-04-25 | 完成 Phase 1 学习路线设计 | `docs/学习路线/` |
| 2026-04-25 | 搭建项目环境，完成数据获取模块 | `basics/data_utils.py` |
| 2026-04-XX | 完成数据处理与均线计算 | `notebooks/phase1/02_data_processing.ipynb` |
| 2026-04-XX | 完成统计分析 | `notebooks/phase1/03_statistics.ipynb` |
| 2026-04-XX | 完成股票数据探索仪表盘 | `notebooks/phase1/04_dashboard.ipynb` |
```

- [ ] **Step 3: Final commit for Phase 1**

Run:
```bash
git add docs/学习笔记/ README.md
git commit -m "docs(phase1): add learning notes template and update README"
```

---

## 🔍 计划自我审查

### 1. Spec Coverage（设计文档覆盖检查）

| 设计文档要求 | 对应 Task/Step |
|-------------|---------------|
| 环境搭建 + akshare 数据获取 | Task 1 Step 1-5, Task 2 Step 1-5 |
| pandas 数据处理 + 均线计算 | Task 3 Step 1-5 |
| 统计指标（年化收益、波动率、夏普、偏度、峰度） | Task 4 Step 1-3 |
| 收益率分布可视化 + 相关性 | Task 4 Step 3 |
| 封装函数 analyze_stock | Task 5 Step 1 |
| 多面板仪表盘整合 | Task 5 Step 2 |
| 论文素养植入（微型摘要） | Task 4 Step 4, Task 5 Step 5 |
| 学习笔记记录 | Task 6 Step 1 |

**覆盖结论**: 全部覆盖，无遗漏。

### 2. Placeholder Scan（占位符扫描）

- 无 "TBD", "TODO", "implement later"
- 无 "Add appropriate error handling" 等模糊描述
- 所有代码步骤包含完整可运行代码
- 无 "Similar to Task N" 交叉引用

### 3. Type Consistency（类型一致性）

- `download_stock_data` 返回 `pd.DataFrame` — 全计划一致
- `calculate_returns` / `calculate_ma` 参数 `df: pd.DataFrame` — 全计划一致
- `descriptive_stats` 返回 `dict` — 全计划一致
- `analyze_stock` 返回 `dict` 且内部结构一致

---

## ✅ Phase 1 完成标准

在宣布 Phase 1 完成之前，请确认以下检查项全部通过：

- [ ] `pytest tests/basics/test_data_utils.py` 全部通过
- [ ] `notebooks/phase1/04_dashboard.ipynb` 可以输入任意股票代码重新运行并生成报告
- [ ] `data/raw/` 目录下至少有一份下载的股票数据 CSV
- [ ] `docs/学习笔记/phase1_每周总结.md` 已填写至少 Week 1 的内容
- [ ] `README.md` 最近更新表格已更新
- [ ] 所有代码已提交到 git
