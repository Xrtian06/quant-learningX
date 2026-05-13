# 📊 数据获取与处理

> "Garbage in, garbage out." 数据质量决定策略上限。

---

## 目录说明

| 子目录 | 数据源 | 适用市场 | 状态 |
|--------|--------|----------|------|
| `yfinance/` | Yahoo Finance | 美股/全球 | ⬜ |
| `akshare/` | AkShare | A股 | ⬜ |
| `tushare/` | Tushare Pro | A股 | ⬜ |

---

## 每个子目录的标准内容

- `download-[data].py`：数据下载脚本
- `clean-[data].py`：数据清洗脚本
- `sample-data/`：小型样本数据（用于测试和示例）

---

## 注意事项

- **不要把大容量数据文件提交到 GitHub**，`.gitignore` 已经屏蔽了常见的数据格式。
- API Key 等敏感信息请放在 `.env` 文件中，也不要上传。
- 样本数据（几百 KB 以内）可以放在 `sample-data/` 中供他人复现。

---

## 已完成内容

*暂无*
