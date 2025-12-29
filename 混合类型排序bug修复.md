# 混合类型排序Bug修复

## 问题描述

用户遇到错误：
```
could not convert string to float: '星'
```

### 错误原因

在Python 3中，不能直接对包含不同类型的列表进行排序。例如：

```python
# ❌ 错误示例
mixed_list = [1, 2, '星', 3]
sorted(mixed_list)  # TypeError!
```

当数据中包含：
- 数值：1, 2, 3
- 中文字符："星"
- 或其他混合类型

系统在尝试排序时会失败。

### 触发场景

1. 统计函数处理分类变量时，对所有唯一值进行排序（第184行）
2. AI视图显示统计结果时，对字典键进行排序（第232行）

## 修复方案

### 修复1：统计函数（stat_functions.py）

**位置**：`src/lib/stat_functions.py` 第184-192行

**修复前**：
```python
for val in sorted(all_possible_values):  # ❌ 混合类型会报错
```

**修复后**：
```python
# 安全排序：检查所有值是否为数字类型
all_numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) 
                  for v in all_possible_values)

if all_numeric:
    # 所有值都是数字，直接数值排序
    sorted_values = sorted(all_possible_values)
else:
    # 包含非数字，转换为字符串后排序
    sorted_values = sorted(all_possible_values, key=str)
```

### 修复2：AI视图显示（ai_view_v2.py）

**位置**：`src/components/ai_view_v2.py` 第232-241行

**修复前**：
```python
for cat in sorted(values_dict.keys()):  # ❌ 混合类型会报错
```

**修复后**：
```python
# 安全排序：检查所有键是否为数字类型
all_keys = list(values_dict.keys())
all_numeric = all(isinstance(k, (int, float)) and not isinstance(k, bool) 
                  for k in all_keys)

if all_numeric:
    sorted_keys = sorted(all_keys)
else:
    sorted_keys = sorted(all_keys, key=str)

for cat in sorted_keys:
```

## 修复逻辑

### 1. 检查类型一致性
```python
all_numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) 
                  for v in values)
```

- 检查所有值是否都是数字（int或float）
- 排除布尔值（Python中bool是int的子类）

### 2. 分情况排序

#### 情况A：纯数字
```python
if all_numeric:
    sorted_values = sorted(values)  # 数值排序：1, 2, 3, 7, 8, 9
```

#### 情况B：包含非数字
```python
else:
    sorted_values = sorted(values, key=str)  # 字符串排序：'1', '2', '星', '月'
```

## 测试案例

### 案例1：纯数字（年级）
```python
values = [7, 8, 9]
# 结果：[7, 8, 9]
```

### 案例2：混合类型
```python
values = [1, 2, '星', 3]
# 结果（按字符串排序）：[1, 2, 3, '星']
```

### 案例3：纯字符串
```python
values = ['星', '月', '日']
# 结果：['日', '星', '月']（按Unicode排序）
```

## 影响范围

### 修复的功能
- ✅ 描述统计中的分类变量排序（stat_functions.py）
- ✅ AI分析结果的显示排序（ai_view_v2.py）
- ✅ 值标签视图中的唯一值显示（label_view.py 第53行）
- ✅ 值标签视图中的合并值排序（label_view.py 第74行）
- ✅ 标签上下文生成中的排序（variable_labels.py 第93行）

### 适用场景
- 数值型分类变量（年级：7, 8, 9）
- 字符串分类变量（颜色："红"、"绿"、"蓝"）
- 混合类型（评级：1, 2, 3, "优秀", "良好"）

## 更新日志

### 2025-11-06 (第二次修复)
- ✅ 修复：值标签视图中的唯一值显示排序（label_view.py）
- ✅ 修复：值标签视图中的合并值排序（label_view.py）
- ✅ 修复：标签上下文生成中的排序（variable_labels.py）
- ✅ 全面排查：修复了所有5处混合类型排序问题

### 2025-11-06 (第一次修复)
- ✅ 修复：分类变量排序时的混合类型错误（stat_functions.py）
- ✅ 修复：AI分析结果显示排序（ai_view_v2.py）
- ✅ 新增：智能类型检测，自动选择排序方式
- ✅ 修复：`could not convert string to float: '星'` 错误

---

如有问题，请在 GitHub 提交 Issue。

