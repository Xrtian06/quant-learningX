# 策略模板说明

> 这是策略文件夹的标准模板。每次学习新策略时，复制这个文件夹并重命名。

## 复制命令

```bash
# Linux / Mac
cp -r _template my-new-strategy-[project]

# Windows PowerShell
Copy-Item -Recurse -Path _template -Destination my-new-strategy-[project]
```

## 模板结构

```
my-new-strategy-[project]/
├── README.md                      # 策略说明文档（必填）
├── requirements.txt               # 该策略特有的依赖（可选）
├── config.yaml                    # 策略参数配置（可选）
├── principle-[note].md            # 策略原理学习笔记
├── strategy-[code].py             # 策略核心逻辑
├── backtest-[backtest].py         # 回测代码
├── data/                          # 策略使用的数据
│   └── .gitkeep
├── results/                       # 回测结果输出
│   └── .gitkeep
└── notebooks/                     # 探索性分析 notebook
    └── analysis-[note].ipynb
```

## 使用步骤

1. 复制 `_template` 文件夹
2. 按策略命名（如 `dual-ma-[project]`）
3. 填写 `README.md` 和 `principle-[note].md`
4. 编写策略逻辑和回测代码
5. 运行回测，将结果图表放入 `results/`
