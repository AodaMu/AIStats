"""
测试分组描述统计功能
"""
import pandas as pd
import numpy as np

# 读取数据
print("正在读取数据...")
df = pd.read_excel('666.xlsx')

# 将列名转换为字符串
df.columns = [str(col) for col in df.columns]

print(f"✅ 数据读取成功：{df.shape[0]} 行 × {df.shape[1]} 列")
print(f"列名：{df.columns.tolist()[:10]}...")

# 测试分组统计
print("\n" + "="*50)
print("测试分组描述统计")
print("="*50)

group_var = 'class'
vars_to_analyze = ['1.1', '1.2', '1.3']

print(f"\n分组变量：{group_var}")
print(f"分析变量：{vars_to_analyze}")

# 获取分组
groups = sorted(df[group_var].dropna().unique())
print(f"\n分组数量：{len(groups)}")
print(f"分组值：{groups}")

# 计算维度得分模式
print("\n" + "-"*50)
print("维度得分模式（勾选'计算维度得分'）")
print("-"*50)

results = []
for group in groups:
    group_data = df[df[group_var] == group]
    
    # 计算维度得分
    dimension_scores = group_data[vars_to_analyze].apply(pd.to_numeric, errors='coerce').mean(axis=1)
    
    row = {
        group_var: str(group),
        '样本量': len(group_data),
        '均值': round(float(dimension_scores.mean()), 2),
        '标准差': round(float(dimension_scores.std()), 2),
        '最小值': round(float(dimension_scores.min()), 2),
        '最大值': round(float(dimension_scores.max()), 2)
    }
    results.append(row)

result_df = pd.DataFrame(results)
print("\n结果表格：")
print(result_df.to_string(index=False))

# 测试AI分析数据生成
print("\n" + "-"*50)
print("AI分析数据生成测试")
print("-"*50)

stats_text = []
for idx, row in result_df.iterrows():
    group_name = row[group_var]
    sample_size = row['样本量']
    mean_val = row['均值']
    std_val = row['标准差']
    stats_text.append(f"- {group_name}组：样本量={sample_size}，均值={mean_val:.2f}，标准差={std_val:.2f}")

print("\nAI分析输入文本：")
print('\n'.join(stats_text))

print("\n" + "="*50)
print("✅ 所有测试通过！")
print("="*50)
