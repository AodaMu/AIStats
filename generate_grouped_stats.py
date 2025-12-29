"""
生成按年级分组的描述统计表
用于分析 666.xlsx 数据
"""
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_excel('666.xlsx')

# 定义5个维度（根据你的问卷结构调整）
dimensions = {
    'ZXaa': ['1.1', '1.2', '1.3'],  # 维度1：题目1.1-1.3的平均
    '哈рилцаа хөлбөө ба хамтын ажиллагаа': ['2.1', '2.2'],  # 维度2
    'Асуудал шийдвэрлэх': ['3.1', '3.2', '3.3'],  # 维度3
    'Мэзээзэл ба өгөгдлийн бичиг үсэг': ['4.1', '4.2'],  # 维度4
    'Дижитал контент бүтээх': ['5.1', '5.2']  # 维度5
}

# 将列名转换为字符串（避免数字列名问题）
df.columns = [str(col) for col in df.columns]

# 创建结果表
results = []

# 按年级分组
for grade in sorted(df['class'].unique()):
    grade_data = df[df['class'] == grade]
    row = {'年级': f'{int(grade)} анги'}
    
    # 计算每个维度的均值和标准差
    for dim_name, questions in dimensions.items():
        # 确保题目列存在（将列名转为字符串比较）
        valid_questions = [q for q in questions if str(q) in df.columns]
        
        if valid_questions:
            # 计算该维度的平均分（每个学生的题目平均分）
            dim_scores = grade_data[valid_questions].apply(pd.to_numeric, errors='coerce').mean(axis=1)
            
            # 计算均值和标准差
            mean_val = dim_scores.mean()
            std_val = dim_scores.std()
            
            row[f'{dim_name}_均值'] = round(mean_val, 1)
            row[f'{dim_name}_标准差'] = round(std_val, 1)
        else:
            row[f'{dim_name}_均值'] = np.nan
            row[f'{dim_name}_标准差'] = np.nan
    
    results.append(row)

# 创建结果DataFrame
result_df = pd.DataFrame(results)

# 显示结果
print("=" * 100)
print("按年级分组的描述统计结果")
print("=" * 100)
print(result_df.to_string(index=False))
print("\n")

# 保存为Excel
output_file = '分组描述统计结果.xlsx'
result_df.to_excel(output_file, index=False)
print(f"✅ 结果已保存到：{output_file}")

# 也保存为CSV（方便查看）
result_df.to_csv('分组描述统计结果.csv', index=False, encoding='utf-8-sig')
print(f"✅ 结果已保存到：分组描述统计结果.csv")
