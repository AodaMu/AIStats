"""模糊匹配变量名"""
import streamlit as st
from difflib import SequenceMatcher

def find_variable_by_keyword(keyword: str):
    """根据关键词模糊匹配变量名"""
    if st.session_state.data is None:
        return None
    
    df = st.session_state.data
    columns = df.columns.tolist()
    
    keyword = keyword.strip().lower()
    
    # 方法1：直接包含匹配
    for col in columns:
        if keyword in col.lower():
            return col
    
    # 方法2：计算相似度
    best_match = None
    best_score = 0
    
    for col in columns:
        # 计算相似度
        similarity = SequenceMatcher(None, keyword, col.lower()).ratio()
        if similarity > best_score and similarity > 0.3:  # 相似度阈值
            best_score = similarity
            best_match = col
    
    return best_match

