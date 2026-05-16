# -*- coding: utf-8 -*-
"""
沪深300IF股指期货关联规则分析
基于Apriori算法挖掘价格、成交量、持仓量与次日收益率之间的关联规则
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def load_data(filepath):
    """加载数据"""
    df = pd.read_excel(filepath)
    df['时间'] = pd.to_datetime(df['时间'])
    df = df.sort_values('时间').reset_index(drop=True)
    print(f"数据加载完成，共 {len(df)} 条记录，时间范围：{df['时间'].min().date()} 至 {df['时间'].max().date()}")
    return df


def discretize_data(df):
    """将连续变量离散化为类别变量，构造用于关联规则分析的数据集"""
    data = pd.DataFrame()
    data['时间'] = df['时间']
    
    # 1. 对数收益率离散化（核心价格状态）
    data['收益率状态'] = pd.cut(
        df['对数收益率'],
        bins=[-np.inf, -0.02, -0.005, 0.005, 0.02, np.inf],
        labels=['大跌', '小跌', '震荡', '小涨', '大涨']
    )
    
    # 2. 成交量变化率离散化
    data['成交量状态'] = pd.cut(
        df['成交量变化率'],
        bins=[-np.inf, -0.20, 0, 0.20, np.inf],
        labels=['缩量', '量平减', '量平增', '放量']
    )
    
    # 3. 持仓量变化率离散化
    data['持仓量状态'] = pd.cut(
        df['持仓量变化率'],
        bins=[-np.inf, -0.10, 0, 0.10, np.inf],
        labels=['大幅减仓', '小幅减仓', '小幅增仓', '大幅增仓']
    )
    
    # 4. 成交额变化率离散化
    data['成交额状态'] = pd.cut(
        df['成交额变化率'],
        bins=[-np.inf, -0.20, 0, 0.20, np.inf],
        labels=['成交额萎缩', '成交额减少', '成交额增加', '成交额大增']
    )
    
    # 5. 隔夜跳空幅度离散化（用实际百分比，原始数据已经是比例）
    data['跳空状态'] = pd.cut(
        df['隔夜跳空幅度'],
        bins=[-np.inf, -0.01, 0, 0.01, np.inf],
        labels=['大幅低开', '小幅低开', '小幅高开', '大幅高开']
    )
    
    # 6. 日内波动离散化（原始数据是点数，基于分位数分箱）
    vol_q25 = df['日内波动'].quantile(0.25)
    vol_q75 = df['日内波动'].quantile(0.75)
    data['波动状态'] = pd.cut(
        df['日内波动'],
        bins=[-np.inf, vol_q25, vol_q75, np.inf],
        labels=['低波动', '中波动', '高波动']
    )
    
    # 7. 振幅离散化（原始数据是比例，基于分位数分箱更稳健）
    amp_q25 = df['振幅'].quantile(0.25)
    amp_q75 = df['振幅'].quantile(0.75)
    data['振幅状态'] = pd.cut(
        df['振幅'],
        bins=[-np.inf, amp_q25, amp_q75, np.inf],
        labels=['低振幅', '中振幅', '高振幅']
    )
    
    # 8. 次日收益率离散化（目标变量）
    data['次日收益状态'] = pd.cut(
        df['次日收益率'],
        bins=[-np.inf, -0.02, 0, 0.02, np.inf],
        labels=['次日大跌', '次日下跌', '次日上涨', '次日大涨']
    )
    
    # 注：不加入"是否换月附近"和"是否换月跳空"，因为分布极度不平衡
    # （非换月期占89%，非换月跳空占99.8%），会导致大量无意义的背景规则
    # 也不加入"价格涨跌""持仓变化""价仓状态"，因为它们与连续变量离散化后的结果存在定义冗余
    
    # 删除含有NaN的行
    data = data.dropna().reset_index(drop=True)
    print(f"离散化完成，有效记录 {len(data)} 条，共 {len(data.columns)-1} 个分析维度")
    return data


def create_transaction_matrix(data):
    """将离散化后的数据转换为one-hot编码的事务矩阵"""
    cat_cols = data.columns.drop('时间')
    
    transactions = []
    for idx, row in data.iterrows():
        transaction = []
        for col in cat_cols:
            transaction.append(f"{col}={row[col]}")
        transactions.append(transaction)
    
    te = TransactionEncoder()
    te_array = te.fit_transform(transactions)
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)
    
    print(f"事务矩阵构建完成，共 {len(df_encoded)} 条事务，{len(te.columns_)} 个项")
    return df_encoded, te.columns_


def mine_frequent_itemsets(df_encoded, min_support=0.05):
    """挖掘频繁项集"""
    frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True, verbose=0)
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
    frequent_itemsets = frequent_itemsets.sort_values(['length', 'support'], ascending=[False, False])
    print(f"频繁项集挖掘完成，共找到 {len(frequent_itemsets)} 个频繁项集（min_support={min_support}）")
    return frequent_itemsets


def generate_rules(frequent_itemsets, min_threshold=0.6, metric='confidence'):
    """生成关联规则"""
    if len(frequent_itemsets) == 0:
        print("没有找到频繁项集，无法生成关联规则")
        return pd.DataFrame()
    
    rules = association_rules(frequent_itemsets, metric=metric, min_threshold=min_threshold, num_itemsets=len(frequent_itemsets))
    if len(rules) == 0:
        print(f"未找到满足 {metric}>={min_threshold} 的关联规则")
        return rules
    
    rules = rules.sort_values(['lift', 'confidence'], ascending=[False, False])
    print(f"关联规则生成完成，共找到 {len(rules)} 条规则（{metric}>={min_threshold}）")
    return rules


def filter_target_rules(rules, target_patterns, antecedent_only=True):
    """筛选包含目标模式的规则"""
    if len(rules) == 0:
        return rules
    
    mask = False
    for pattern in target_patterns:
        if antecedent_only:
            mask |= rules['consequents'].apply(lambda x: any(pattern in item for item in x))
        else:
            mask |= rules['antecedents'].apply(lambda x: any(pattern in item for item in x)) | \
                    rules['consequents'].apply(lambda x: any(pattern in item for item in x))
    
    filtered = rules[mask].copy()
    return filtered


def plot_top_rules(rules, title, save_path, top_n=20):
    """可视化Top关联规则（散点图：支持度 vs 置信度，提升度作为颜色）"""
    if len(rules) == 0:
        print(f"没有规则可可视化: {title}")
        return
    
    plot_df = rules.head(top_n).copy()
    plot_df['rule_str'] = plot_df.apply(
        lambda row: f"{','.join(list(row['antecedents']))} → {','.join(list(row['consequents']))}", axis=1
    )
    
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(plot_df['support'], plot_df['confidence'], 
                        c=plot_df['lift'], cmap='RdYlGn', s=100, alpha=0.7, edgecolors='black', vmin=0.5, vmax=2.5)
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('提升度 (Lift)', fontsize=12)
    
    ax.set_xlabel('支持度 (Support)', fontsize=12)
    ax.set_ylabel('置信度 (Confidence)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max(plot_df['support']) * 1.1)
    ax.set_ylim(0, 1.05)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"图表已保存: {save_path}")


def plot_lift_heatmap(rules, title, save_path, top_n=15):
    """绘制提升度热力图"""
    if len(rules) == 0:
        return
    
    plot_df = rules.head(top_n).copy()
    plot_df['antecedent_str'] = plot_df['antecedents'].apply(lambda x: ','.join(list(x))[:35])
    plot_df['consequent_str'] = plot_df['consequents'].apply(lambda x: ','.join(list(x))[:25])
    plot_df['label'] = plot_df['antecedent_str'] + ' →\n' + plot_df['consequent_str']
    
    fig, ax = plt.subplots(figsize=(14, 10))
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(plot_df)))
    bars = ax.barh(range(len(plot_df)), plot_df['lift'].values, color=colors)
    ax.set_yticks(range(len(plot_df)))
    ax.set_yticklabels(plot_df['label'].values, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('提升度 (Lift)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axvline(x=1.0, color='red', linestyle='--', alpha=0.5, label='Lift=1 (独立)')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')
    
    for i, (bar, lift) in enumerate(zip(bars, plot_df['lift'].values)):
        ax.text(lift + 0.02, i, f'{lift:.2f}', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"图表已保存: {save_path}")


def save_rules_to_excel(rules, filepath, max_rows=500000):
    """将关联规则保存为Excel"""
    if len(rules) == 0:
        print(f"没有规则可保存: {filepath}")
        return
    
    out_df = rules.copy()
    out_df['antecedents'] = out_df['antecedents'].apply(lambda x: ','.join(list(x)))
    out_df['consequents'] = out_df['consequents'].apply(lambda x: ','.join(list(x)))
    out_df = out_df[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'leverage', 'conviction']]
    out_df.columns = ['前项', '后项', '支持度', '置信度', '提升度', '杠杆率', '确信度']
    
    if len(out_df) > max_rows:
        print(f"警告: 规则数量({len(out_df)})超过Excel最大行数限制，仅保存前{max_rows}条")
        out_df = out_df.head(max_rows)
    
    out_df.to_excel(filepath, index=False)
    print(f"规则已保存: {filepath} (共{len(out_df)}条)")


def plot_item_support(freq_itemsets, title, save_path, min_len=2, top_n=20):
    """绘制频繁项集支持度条形图"""
    plot_df = freq_itemsets[freq_itemsets['length'] >= min_len].head(top_n).copy()
    if len(plot_df) == 0:
        return
    plot_df['item_str'] = plot_df['itemsets'].apply(lambda x: ','.join(list(x))[:50])
    
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(plot_df)))
    bars = ax.barh(range(len(plot_df)), plot_df['support'].values, color=colors)
    ax.set_yticks(range(len(plot_df)))
    ax.set_yticklabels(plot_df['item_str'].values, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('支持度 (Support)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    for i, (bar, sup) in enumerate(zip(bars, plot_df['support'].values)):
        ax.text(sup + 0.001, i, f'{sup:.3f}', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"图表已保存: {save_path}")


def main():
    print("="*60)
    print("沪深300IF股指期货 - 关联规则分析")
    print("="*60)
    
    # 1. 加载数据
    df = load_data('../data/沪深300IF_清洗后_2015_2022.xlsx')
    
    # 2. 数据离散化
    data_discrete = discretize_data(df)
    
    # 3. 构建事务矩阵
    df_encoded, items = create_transaction_matrix(data_discrete)
    
    # 保存离散化数据
    data_discrete.to_excel('离散化数据.xlsx', index=False)
    print("离散化数据已保存: 离散化数据.xlsx")
    
    # ===== 分析1: 整体频繁项集 =====
    print("\n" + "="*60)
    print("分析1: 整体频繁项集挖掘 (min_support=0.05)")
    print("="*60)
    freq_itemsets_all = mine_frequent_itemsets(df_encoded, min_support=0.05)
    freq_itemsets_save = freq_itemsets_all[freq_itemsets_all['length'] >= 2].sort_values('support', ascending=False).head(100000)
    freq_itemsets_save.to_excel('频繁项集_整体.xlsx', index=False)
    print(f"保存了 {len(freq_itemsets_save)} 个长度>=2的频繁项集")
    plot_item_support(freq_itemsets_all, 'Top频繁项集支持度', '频繁项集支持度.png', min_len=2, top_n=20)
    
    # ===== 分析2: 次日收益率预测规则 =====
    print("\n" + "="*60)
    print("分析2: 预测次日收益率的关联规则")
    print("="*60)
    # 提高min_support到0.04以减少计算量
    freq_itemsets_2 = mine_frequent_itemsets(df_encoded, min_support=0.04)
    rules_2 = generate_rules(freq_itemsets_2, min_threshold=0.55, metric='confidence')
    rules_next_day = filter_target_rules(rules_2, ['次日收益状态='], antecedent_only=True)
    # 过滤提升度>1的有意义规则
    rules_next_day = rules_next_day[rules_next_day['lift'] > 1.0]
    save_rules_to_excel(rules_next_day, '关联规则_次日收益率.xlsx')
    plot_top_rules(rules_next_day, '预测次日收益率的Top关联规则', '关联规则_次日收益率散点图.png')
    plot_lift_heatmap(rules_next_day, '预测次日收益率的关联规则提升度', '关联规则_次日收益率提升度.png')
    
    # ===== 分析3: 量价关系规则 =====
    print("\n" + "="*60)
    print("分析3: 收益率与量能关系规则")
    print("="*60)
    freq_itemsets_3 = mine_frequent_itemsets(df_encoded, min_support=0.05)
    rules_3 = generate_rules(freq_itemsets_3, min_threshold=0.60, metric='confidence')
    target_patterns = ['收益率状态=', '成交量状态=', '持仓量状态=']
    rules_volume = filter_target_rules(rules_3, target_patterns, antecedent_only=False)
    rules_volume = rules_volume[rules_volume['lift'] > 1.0]
    save_rules_to_excel(rules_volume, '关联规则_量价关系.xlsx')
    plot_top_rules(rules_volume, '量价关系的Top关联规则', '关联规则_量价关系散点图.png')
    
    # ===== 分析4: 波动与收益关系 =====
    print("\n" + "="*60)
    print("分析4: 波动/振幅与收益关联规则")
    print("="*60)
    target_patterns_4 = ['波动状态=', '振幅状态=', '收益率状态=']
    rules_volatility = filter_target_rules(rules_3, target_patterns_4, antecedent_only=False)
    rules_volatility = rules_volatility[rules_volatility['lift'] > 1.0]
    save_rules_to_excel(rules_volatility, '关联规则_波动收益.xlsx')
    plot_top_rules(rules_volatility, '波动与收益关系的Top关联规则', '关联规则_波动收益散点图.png')
    
    # ===== 分析5: 跳空与次日收益关系 =====
    print("\n" + "="*60)
    print("分析5: 隔夜跳空与次日收益关联规则")
    print("="*60)
    target_patterns_5 = ['跳空状态=', '次日收益状态=']
    rules_gap = filter_target_rules(rules_2, target_patterns_5, antecedent_only=False)
    rules_gap = rules_gap[rules_gap['lift'] > 1.0].sort_values('lift', ascending=False)
    save_rules_to_excel(rules_gap, '关联规则_隔夜跳空.xlsx')
    plot_top_rules(rules_gap, '隔夜跳空相关的Top关联规则', '关联规则_隔夜跳空散点图.png')
    
    # ===== 分析6: 高提升度强关联规则 =====
    print("\n" + "="*60)
    print("分析6: 高提升度强关联规则 (lift>=1.3)")
    print("="*60)
    rules_lift = generate_rules(freq_itemsets_3, min_threshold=1.3, metric='lift')
    # 排除确信度为inf的完美规则（通常是变量定义冗余导致的）
    rules_lift = rules_lift[rules_lift['conviction'].replace([np.inf], np.nan) < 10].dropna(subset=['conviction'])
    save_rules_to_excel(rules_lift, '关联规则_高提升度.xlsx')
    plot_lift_heatmap(rules_lift, '高提升度关联规则 (Lift≥1.3)', '关联规则_高提升度.png', top_n=20)
    
    # ===== 汇总报告 =====
    print("\n" + "="*60)
    print("分析完成！生成文件汇总:")
    print("="*60)
    print("1. 离散化数据.xlsx - 离散化后的原始数据")
    print("2. 频繁项集_整体.xlsx / .png - 所有频繁项集")
    print("3. 关联规则_次日收益率.xlsx / .png - 次日收益预测规则")
    print("4. 关联规则_量价关系.xlsx / .png - 量价联动规则")
    print("5. 关联规则_波动收益.xlsx / .png - 波动与收益规则")
    print("6. 关联规则_隔夜跳空.xlsx / .png - 跳空与收益规则")
    print("7. 关联规则_高提升度.xlsx / .png - 强关联规则")
    print("="*60)
    
    # 输出Top10规则摘要
    print("\n【Top 10 高提升度关联规则（已过滤冗余）】")
    if len(rules_lift) > 0:
        for i, row in rules_lift.head(10).iterrows():
            ant = ','.join(list(row['antecedents']))
            con = ','.join(list(row['consequents']))
            print(f"  {ant} → {con}")
            print(f"     支持度={row['support']:.3f}, 置信度={row['confidence']:.3f}, 提升度={row['lift']:.3f}")
    
    print("\n分析全部完成！")


if __name__ == '__main__':
    main()
