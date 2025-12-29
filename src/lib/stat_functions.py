"""统计分析函数库，供 AI 调用"""
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from src.lib.fuzzy_match import find_variable_by_keyword

def independent_t_test(data_var: str, group_var: str):
    """独立样本 t 检验"""
    if st.session_state.data is None:
        return {"error": "未导入数据"}
    
    df = st.session_state.data
    
    if data_var not in df.columns or group_var not in df.columns:
        return {"error": f"变量 {data_var} 或 {group_var} 不存在"}
    
    groups = df[group_var].unique()
    if len(groups) != 2:
        return {"error": "分组变量必须恰好有 2 个水平"}
    
    group1 = df[df[group_var] == groups[0]][data_var].dropna()
    group2 = df[df[group_var] == groups[1]][data_var].dropna()
    
    # t 检验
    t_stat, p_value = stats.ttest_ind(group1, group2)
    
    # Cohen's d
    pooled_std = np.sqrt(((len(group1)-1)*group1.std()**2 + (len(group2)-1)*group2.std()**2) / (len(group1)+len(group2)-2))
    cohens_d = (group1.mean() - group2.mean()) / pooled_std
    
    # 置信区间
    mean_diff = group1.mean() - group2.mean()
    se_diff = pooled_std * np.sqrt(1/len(group1) + 1/len(group2))
    ci_lower = mean_diff - 1.96 * se_diff
    ci_upper = mean_diff + 1.96 * se_diff
    
    result = {
        "test_type": "独立样本 t 检验",
        "data_var": data_var,
        "group_var": group_var,
        "group1_name": str(groups[0]),
        "group2_name": str(groups[1]),
        "group1_n": len(group1),
        "group2_n": len(group2),
        "group1_mean": float(group1.mean()),
        "group2_mean": float(group2.mean()),
        "group1_std": float(group1.std()),
        "group2_std": float(group2.std()),
        "mean_diff": float(mean_diff),
        "t_statistic": float(t_stat),
        "df": len(group1) + len(group2) - 2,
        "p_value": float(p_value),
        "ci_95_lower": float(ci_lower),
        "ci_95_upper": float(ci_upper),
        "cohens_d": float(cohens_d),
        "significant": "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
    }
    
    # 保存到 session_state
    st.session_state.stat_result = result
    
    return result

def descriptive_stats(variables: list):
    """描述统计 - 自动检测并处理多选题，支持模糊匹配变量名"""
    if st.session_state.data is None:
        return {"error": "未导入数据"}
    
    df = st.session_state.data
    
    results = {}
    for var in variables:
        # 先尝试精确匹配，失败则模糊匹配
        original_var = var
        was_fuzzy_matched = False
        
        if var not in df.columns:
            # 如果精确匹配失败，尝试模糊匹配
            matched_var = find_variable_by_keyword(var)
            if matched_var:
                var = matched_var  # 使用匹配到的完整变量名
                was_fuzzy_matched = True
            else:
                results[original_var] = {"error": f"变量 '{original_var}' 不存在（也未找到匹配的变量）"}
                continue
        
            # 确认变量存在后进行统计
        if var in df.columns:
            # 如果使用了模糊匹配，在结果中标注
            matched_info = f" (匹配: {original_var} → {var})" if was_fuzzy_matched else ""
            data = df[var].dropna()
            
            # 安全检查：如果数据为空，返回错误
            if len(data) == 0:
                results[var] = {
                    "type": "empty",
                    "error": "变量中没有有效数据（全部为缺失值）",
                    "n": 0,
                    "missing": int(df[var].isnull().sum())
                }
                continue
            
            # 🔍 自动检测多选题（包含分号分隔）
            is_multiple_choice = False
            try:
                sample = data.head(20).astype(str)
                # 检测是否有分号分隔的模式
                if sample.str.contains(';', regex=False).any():
                    is_multiple_choice = True
            except:
                is_multiple_choice = False
            
            # 获取值标签（如果有）
            from src.lib.variable_labels import get_value_labels
            value_labels = get_value_labels(var)
            
            # 智能判断：数值型变量但设置了值标签 → 当作分类变量处理
            # 或者：唯一值很少（≤15个）→ 也当作分类变量
            is_categorical_numeric = False
            if df[var].dtype in ['int64', 'float64']:
                unique_count = df[var].nunique()
                if value_labels or unique_count <= 15:
                    is_categorical_numeric = True
            
            # 数值型变量（连续型）
            if df[var].dtype in ['int64', 'float64'] and not is_categorical_numeric:
                try:
                    stats_dict = {
                        "type": "numeric",
                        "n": len(data),
                        "mean": float(data.mean()),
                        "std": float(data.std()),
                        "min": float(data.min()),
                        "q1": float(data.quantile(0.25)),
                        "median": float(data.median()),
                        "q3": float(data.quantile(0.75)),
                        "max": float(data.max()),
                        "missing": int(df[var].isnull().sum())
                    }
                except Exception as e:
                    stats_dict = {
                        "type": "numeric",
                        "error": f"计算数值统计时出错: {str(e)}",
                        "n": len(data),
                        "missing": int(df[var].isnull().sum())
                    }
            
            # 🎯 多选题处理
            elif is_multiple_choice:
                all_options = []
                valid_responses = 0
                
                for value in data:
                    if pd.notna(value):
                        valid_responses += 1
                        options = [opt.strip() for opt in str(value).split(';')]
                        all_options.extend(options)
                
                # 避免除零错误
                if valid_responses > 0:
                    option_counts = pd.Series(all_options).value_counts()
                    percentages = (option_counts / valid_responses * 100).round(2)
                    avg_per_person = round(len(all_options) / valid_responses, 2)
                else:
                    option_counts = pd.Series(dtype=int)
                    percentages = pd.Series(dtype=float)
                    avg_per_person = 0
                
                stats_dict = {
                    "type": "multiple_choice",  # 标记为多选题
                    "n": valid_responses,
                    "n_selections": len(all_options),
                    "avg_per_person": avg_per_person,
                    "option_frequencies": option_counts.to_dict(),
                    "option_percentages": percentages.to_dict(),
                    "missing": int(df[var].isnull().sum())
                }
            
            # 普通分类变量（包括设置了值标签的数值型变量）
            else:
                try:
                    # 安全获取value_counts
                    value_counts = df[var].value_counts(dropna=True)
                    
                    # value_labels 已在上面获取过了
                    # 合并：数据中的值 + 标签中定义的值
                    all_possible_values = set(value_counts.keys())
                    if value_labels:
                        all_possible_values.update(value_labels.keys())
                    
                    # 为所有可能的值创建完整的频次字典（包括频次为0的）
                    complete_values = {}
                    complete_percentages = {}
                    
                    # 安全排序：检查所有值是否为数字类型
                    all_numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in all_possible_values)
                    
                    if all_numeric:
                        # 所有值都是数字，直接数值排序
                        sorted_values = sorted(all_possible_values)
                    else:
                        # 包含非数字，转换为字符串后排序
                        sorted_values = sorted(all_possible_values, key=str)
                    
                    for val in sorted_values:
                        count = value_counts.get(val, 0)
                        complete_values[val] = int(count)
                        if len(data) > 0:
                            complete_percentages[val] = round((count / len(data) * 100), 2)
                        else:
                            complete_percentages[val] = 0.0
                    
                    stats_dict = {
                        "type": "categorical",
                        "n": len(data),
                        "unique": int(df[var].nunique()),
                        "all_values": complete_values,  # 完整的值频次（包括0）
                        "percentages": complete_percentages,
                        "value_labels": value_labels,  # 包含值标签
                        "missing": int(df[var].isnull().sum())
                    }
                except Exception as e:
                    # 如果出错，返回基本信息
                    stats_dict = {
                        "type": "categorical",
                        "n": len(data),
                        "unique": int(df[var].nunique()),
                        "error": f"处理分类变量时出错: {str(e)}",
                        "missing": int(df[var].isnull().sum())
                    }
            
            results[var] = stats_dict
    
    st.session_state.stat_result = results
    return results

def pearson_correlation(variables: list):
    """Pearson 相关分析"""
    if st.session_state.data is None:
        return {"error": "未导入数据"}
    
    df = st.session_state.data
    
    for var in variables:
        if var not in df.columns:
            return {"error": f"变量 {var} 不存在"}
    
    # 相关矩阵
    corr_matrix = df[variables].corr()
    
    # 计算 p 值矩阵
    n = len(df[variables].dropna())
    p_matrix = {}
    
    for var1 in variables:
        p_matrix[var1] = {}
        for var2 in variables:
            if var1 != var2:
                r = corr_matrix.loc[var1, var2]
                # 防止除零错误：当r接近±1时，1-r²接近0
                if abs(r) >= 0.9999:
                    # 完全相关或完全负相关，p值极小
                    p_matrix[var1][var2] = 0.0
                else:
                    t = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)
                    p = 2 * (1 - stats.t.cdf(abs(t), n - 2))
                    p_matrix[var1][var2] = float(p)
            else:
                p_matrix[var1][var2] = 1.0
    
    result = {
        "test_type": "Pearson 相关分析",
        "variables": variables,
        "n": n,
        "correlation_matrix": corr_matrix.to_dict(),
        "p_value_matrix": p_matrix
    }
    
    st.session_state.stat_result = result
    return result

