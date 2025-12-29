"""
生成格式化的分组描述统计表（与图片格式一致）
"""
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_excel('666.xlsx')

# 将列名转换为字符串
df.columns = [str(col) for col in df.columns]

# 定义5个维度及其蒙古语名称
dimensions = {
    'Асуулгүй байдал': ['1.1', '1.2', '1.3'],
    'Харилцаа хөлбөө ба хамтын ажиллагаа': ['2.1', '2.2'],
    'Асуудал шийдвэрлэх': ['3.1', '3.2', '3.3'],
    'Мэзээзэл ба өгөгдлийн бичиг үсэг': ['4.1', '4.2'],
    'Дижитал контент бүтээх': ['5.1', '5.2']
}

# 创建结果列表
results = []

# 按年级分组计算
for grade in sorted(df['class'].unique()):
    grade_data = df[df['class'] == grade]
    
    row_data = {
        'ZXaa': f'{int(grade)} анги'
    }
    
    # 计算每个维度
    for dim_name, questions in dimensions.items():
        valid_questions = [q for q in questions if str(q) in df.columns]
        
        if valid_questions:
            # 计算每个学生在该维度的平均分
            dim_scores = grade_data[valid_questions].apply(pd.to_numeric, errors='coerce').mean(axis=1)
            
            # 计算该年级在该维度的均值和标准差
            mean_val = dim_scores.mean()
            std_val = dim_scores.std()
            
            row_data[f'{dim_name}_Дундаж'] = round(mean_val, 1)
            row_data[f'{dim_name}_Стандарт'] = round(std_val, 1)
    
    results.append(row_data)

# 创建DataFrame
result_df = pd.DataFrame(results)

# 重新排列列顺序，使其与图片格式一致
columns_order = ['ZXaa']
for dim_name in dimensions.keys():
    columns_order.append(f'{dim_name}_Дундаж')
    columns_order.append(f'{dim_name}_Стандарт')

result_df = result_df[columns_order]

# 显示结果
print("\n" + "="*150)
print("按年级分组的描述统计结果（蒙古语格式）")
print("="*150)
print(result_df.to_string(index=False))
print("\n")

# 保存为Excel（带格式）
with pd.ExcelWriter('分组统计_蒙古语格式.xlsx', engine='openpyxl') as writer:
    result_df.to_excel(writer, index=False, sheet_name='统计结果')
    
    # 获取工作表
    worksheet = writer.sheets['统计结果']
    
    # 调整列宽
    for idx, col in enumerate(result_df.columns, 1):
        max_length = max(
            result_df[col].astype(str).apply(len).max(),
            len(str(col))
        )
        worksheet.column_dimensions[chr(64 + idx)].width = max_length + 2

print("✅ 结果已保存到：分组统计_蒙古语格式.xlsx")

# 也创建一个简化的中文版本
result_df_cn = result_df.copy()
result_df_cn.columns = ['年级', 
                        '维度1_均值', '维度1_标准差',
                        '维度2_均值', '维度2_标准差', 
                        '维度3_均值', '维度3_标准差',
                        '维度4_均值', '维度4_标准差',
                        '维度5_均值', '维度5_标准差']

result_df_cn.to_excel('分组统计_中文格式.xlsx', index=False)
print("✅ 结果已保存到：分组统计_中文格式.xlsx")

# 打印维度说明
print("\n" + "="*150)
print("维度说明：")
print("="*150)
for i, (dim_name, questions) in enumerate(dimensions.items(), 1):
    print(f"维度{i}（{dim_name}）：题目 {', '.join(questions)}")
print("="*150)
