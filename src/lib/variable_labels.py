"""变量标签和值标签管理模块"""
import streamlit as st
from src.lib.i18n import get_lang

def init_value_labels():
    """初始化值标签存储"""
    if 'variable_labels' not in st.session_state:
        st.session_state.variable_labels = {}
    if 'value_labels' not in st.session_state:
        st.session_state.value_labels = {}

def set_variable_label(var_name: str, label: str):
    """设置变量标签"""
    init_value_labels()
    st.session_state.variable_labels[var_name] = label

def set_value_labels(var_name: str, labels: dict):
    """设置值标签"""
    init_value_labels()
    st.session_state.value_labels[var_name] = labels

def get_variable_label(var_name: str) -> str:
    """获取变量标签"""
    init_value_labels()
    return st.session_state.variable_labels.get(var_name, var_name)

def get_value_labels(var_name: str) -> dict:
    """获取值标签"""
    init_value_labels()
    return st.session_state.value_labels.get(var_name, {})

def get_value_label(var_name: str, value) -> str:
    """获取单个值的标签"""
    labels = get_value_labels(var_name)
    if not labels:
        return str(value)
    return labels.get(value, str(value))

def get_labels_context() -> str:
    """生成包含标签信息的上下文文本，供AI使用"""
    init_value_labels()
    lang = get_lang()
    
    if not st.session_state.value_labels:
        return ""
    
    if lang == 'zh':
        context = "\n## 变量值标签说明\n"
        context += "💡 以下标签定义了变量的完整值域。统计结果会显示所有定义的值（包括频次为0的值）。\n"
    else:
        context = "\n## Хувьсагчийн утгын тэмдэглэгээний тайлбар\n"
        context += "💡 Дараах тэмдэглэгээ нь хувьсагчийн бүрэн утгын хүрээг тодорхойлно. Статистикийн үр дүнд тодорхойлсон бүх утгыг харуулна (давтамж=0 ч бай).\n"
    
    for var_name, labels in st.session_state.value_labels.items():
        var_label = st.session_state.variable_labels.get(var_name, var_name)
        if lang == 'zh':
            context += f"\n**{var_name}** ({var_label}) - 完整值域定义:\n"
        else:
            context += f"\n**{var_name}** ({var_label}) - Бүрэн утгын хүрээ:\n"
        
        # 安全排序：检查所有键是否为数字类型
        all_keys = list(labels.keys())
        all_numeric = all(isinstance(k, (int, float)) and not isinstance(k, bool) for k in all_keys)
        
        if all_numeric:
            sorted_items = sorted(labels.items(), key=lambda x: x[0])
        else:
            sorted_items = sorted(labels.items(), key=lambda x: str(x[0]))
        
        for value, label in sorted_items:
            context += f"  - {value} = {label}\n"
    
    if lang == 'zh':
        context += "\n💡 说明：统计结果中，定义了但数据中未出现的值会显示为0（频次=0）。\n"
    else:
        context += "\n💡 Тайлбар：Статистикийн үр дүнд тодорхойлсон боловч өгөгдөлд байхгүй утгыг 0 гэж харуулна (давтамж=0).\n"
    
    return context

def export_labels() -> dict:
    """导出所有标签配置"""
    init_value_labels()
    return {
        "variable_labels": st.session_state.variable_labels,
        "value_labels": st.session_state.value_labels
    }

def import_labels(config: dict):
    """导入标签配置"""
    init_value_labels()
    if "variable_labels" in config:
        st.session_state.variable_labels = config["variable_labels"]
    if "value_labels" in config:
        st.session_state.value_labels = config["value_labels"]

def clear_variable_labels(var_name: str = None):
    """清除标签
    
    Args:
        var_name: 变量名。如果为None，清除所有标签；否则只清除指定变量的标签
    """
    init_value_labels()
    if var_name is None:
        # 清除所有标签
        st.session_state.variable_labels = {}
        st.session_state.value_labels = {}
        if 'manual_values' in st.session_state:
            st.session_state.manual_values = {}
    else:
        # 清除指定变量的标签
        if var_name in st.session_state.variable_labels:
            del st.session_state.variable_labels[var_name]
        if var_name in st.session_state.value_labels:
            del st.session_state.value_labels[var_name]
        if 'manual_values' in st.session_state and var_name in st.session_state.manual_values:
            del st.session_state.manual_values[var_name]

