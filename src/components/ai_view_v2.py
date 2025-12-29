"""
AI 辅助分析模块：带 function calling 和结果展示

【核心功能】
实现"双向绑定"机制：AI ⇄ 统计引擎的实时双向交互

【用户输入到API的完整流程】（答辩重点）
第576-585行：步骤1 - 用户输入
第587-617行：步骤2 - 构建System Prompt（数据上下文 + 值标签）
第705-727行：步骤3 - 组装消息列表
第729-747行：步骤4 - 第一次API调用（AI理解意图）⭐
第753-778行：步骤5 - 执行统计函数（调用实际计算）
第780-841行：步骤6 - 第二次API调用（AI解读结果）⭐

【双向绑定流程】
用户问题 → AI理解 → 选择统计方法 → 执行计算 → 返回结果 → AI解读 → 用户看到答案
一句话完成整个统计分析！

【文件结构】
- 第10-15行：工具函数映射
- 第17-370行：工具定义（9个统计函数的JSON Schema）
- 第72-375行：display_stat_result() - 统计结果展示
- 第377-463行：format_ai_response() - AI回复格式化
- 第465-903行：render_ai_view() - 主渲染函数（包含6步流程）
"""
import streamlit as st
from openai import OpenAI
import json
import pandas as pd
import re
from src.lib.stat_functions import independent_t_test, descriptive_stats, pearson_correlation
from src.lib.variable_labels import get_labels_context
from src.lib.i18n import get_lang

# 工具函数映射
TOOL_FUNCTIONS = {
    "independent_t_test": independent_t_test,
    "descriptive_stats": descriptive_stats,
    "pearson_correlation": pearson_correlation
}

# 工具定义
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "independent_t_test",
            "description": "执行独立样本 t 检验，比较两组之间的均值差异",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_var": {"type": "string", "description": "数据变量名"},
                    "group_var": {"type": "string", "description": "分组变量名"}
                },
                "required": ["data_var", "group_var"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "descriptive_stats",
            "description": "对变量进行描述统计分析。自动识别变量类型：数值型变量计算均值、标准差等；多选题（分号分隔）自动拆分并统计每个选项的频次和百分比；普通分类变量显示频次分布。适用于所有类型的变量分析。",
            "parameters": {
                "type": "object",
                "properties": {
                    "variables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要分析的变量名列表（完整的变量名，包括中英文）"
                    }
                },
                "required": ["variables"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pearson_correlation",
            "description": "计算变量之间的 Pearson 相关系数",
            "parameters": {
                "type": "object",
                "properties": {
                    "variables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "变量名列表"
                    }
                },
                "required": ["variables"]
            }
        }
    }
]

def display_stat_result(result, lang='zh'):
    """展示统计结果"""
    if isinstance(result, dict) and "error" in result:
        st.error(f"❌ {result['error']}")
        return
    
    # 独立样本 t 检验结果
    if isinstance(result, dict) and result.get("test_type") == "独立样本 t 检验":
        title = "### 📊 统计检验结果" if lang == 'zh' else "### 📊 Статистик шалгалтын үр дүн"
        st.markdown(title)
        
        # 检验表
        if lang == 'zh':
            test_df = pd.DataFrame({
                "均值差异": [result["mean_diff"]],
                "自由度": [result["df"]],
                "t值": [result["t_statistic"]],
                "p值": [result["p_value"]],
                "95%置信区间": [f"[{result['ci_95_lower']:.3f}, {result['ci_95_upper']:.3f}]"],
                "效应量(Cohen's d)": [result["cohens_d"]],
                "显著性": [result["significant"]]
            })
        else:
            test_df = pd.DataFrame({
                "Дундажийн ялгаа": [result["mean_diff"]],
                "Чөлөөний зэрэг": [result["df"]],
                "t утга": [result["t_statistic"]],
                "p утга": [result["p_value"]],
                "95% итгэлцлийн интервал": [f"[{result['ci_95_lower']:.3f}, {result['ci_95_upper']:.3f}]"],
                "Нөлөөний хэмжээ(Cohen's d)": [result["cohens_d"]],
                "Ач холбогдол": [result["significant"]]
            })
        st.dataframe(test_df, use_container_width=True)
        
        # 描述统计表
        title = "### 📋 描述统计" if lang == 'zh' else "### 📋 Тайлбар статистик"
        st.markdown(title)
        if lang == 'zh':
            desc_df = pd.DataFrame({
                "组别": [result["group1_name"], result["group2_name"]],
                "样本量": [result["group1_n"], result["group2_n"]],
                "均值": [f"{result['group1_mean']:.3f}", f"{result['group2_mean']:.3f}"],
                "标准差": [f"{result['group1_std']:.3f}", f"{result['group2_std']:.3f}"]
            })
        else:
            desc_df = pd.DataFrame({
                "Бүлэг": [result["group1_name"], result["group2_name"]],
                "Түүврийн хэмжээ": [result["group1_n"], result["group2_n"]],
                "Дундаж": [f"{result['group1_mean']:.3f}", f"{result['group2_mean']:.3f}"],
                "Стандарт хазайлт": [f"{result['group1_std']:.3f}", f"{result['group2_std']:.3f}"]
            })
        st.dataframe(desc_df, use_container_width=True)
        
        # 结论
        title = "### 💡 结论" if lang == 'zh' else "### 💡 Дүгнэлт"
        st.markdown(title)
        if result["p_value"] < 0.05:
            # 显著结果 - 绿色背景
            st.markdown(f"""<div style="background-color: #D4EDDA; padding: 15px; border-radius: 5px; border-left: 5px solid #28A745; margin: 0;"><h4 style="color: #155724; margin: 0 0 10px 0;">✅ 差异显著</h4><p style="color: #155724; margin: 5px 0;"><strong>{result["group_var"]}对{result["data_var"]}有显著影响</strong> (p = {result["p_value"]:.3f} < 0.05)</p><p style="color: #155724; margin: 5px 0;">{result["group1_name"]}的平均值为 <strong>{result["group1_mean"]:.3f}</strong>，{result["group2_name"]}的平均值为 <strong>{result["group2_mean"]:.3f}</strong>，两组差异为 <strong>{abs(result["mean_diff"]):.3f}</strong>，效应量 Cohen's d = <strong>{result["cohens_d"]:.3f}</strong>。</p></div>""", unsafe_allow_html=True)
        else:
            # 不显著结果 - 灰色背景
            st.markdown(f"""<div style="background-color: #F8F9FA; padding: 15px; border-radius: 5px; border-left: 5px solid #6C757D; margin: 0;"><h4 style="color: #495057; margin: 0 0 10px 0;">ℹ️ 差异不显著</h4><p style="color: #495057; margin: 5px 0;"><strong>{result["group_var"]}对{result["data_var"]}无显著影响</strong> (p = {result["p_value"]:.3f} > 0.05)</p><p style="color: #495057; margin: 5px 0;">虽然{result["group1_name"]}的平均值为 {result["group1_mean"]:.3f}，{result["group2_name"]}的平均值为 {result["group2_mean"]:.3f}，但这种差异在统计上不显著。效应量 Cohen's d = {result["cohens_d"]:.3f}。</p></div>""", unsafe_allow_html=True)
        
        # 绘图建议
        title = "### 📊 推荐图表" if lang == 'zh' else "### 📊 Зөвлөмж болгох график"
        st.markdown(title)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if lang == 'zh':
                st.markdown("#### 1. 分组柱状图")
                st.markdown(f"""
- **用途**：比较 {result["group1_name"]} 和 {result["group2_name"]} 的均值差异
- **变量**：
  - Y轴：`{result["data_var"]}`
  - X轴：`{result["group_var"]}`
- **特点**：展示均值和误差棒
                """)
            else:
                st.markdown("#### 1. Бүлгийн багана график")
                st.markdown(f"""
- **Зорилго**：{result["group1_name"]} ба {result["group2_name"]}-ийн дундажийн ялгааг харьцуулах
- **Хувьсагч**：
  - Y тэнхлэг：`{result["data_var"]}`
  - X тэнхлэг：`{result["group_var"]}`
- **Онцлог**：Дундаж ба алдааны мөрийг харуулна
                """)
        
        with col2:
            if lang == 'zh':
                st.markdown("#### 2. 分组箱线图")
                st.markdown(f"""
- **用途**：展示两组的完整分布特征
- **变量**：
  - Y轴：`{result["data_var"]}`
  - X轴：`{result["group_var"]}`
- **特点**：显示中位数、四分位数、异常值
                """)
            else:
                st.markdown("#### 2. Бүлгийн хайрцаг график")
                st.markdown(f"""
- **Зорилго**：Хоёр бүлгийн бүрэн тархалтын шинж чанарыг харуулах
- **Хувьсагч**：
  - Y тэнхлэг：`{result["data_var"]}`
  - X тэнхлэг：`{result["group_var"]}`
- **Онцлог**：Медиан, дөрвөн хувиар, гажуудлыг харуулна
                """)
        
        with col3:
            if lang == 'zh':
                st.markdown("#### 3. 直方图")
                st.markdown(f"""
- **用途**：查看各组数据分布形态
- **变量**：
  - X轴：`{result["data_var"]}`
  - 颜色：`{result["group_var"]}`
- **特点**：展示分布形态和对比
                """)
            else:
                st.markdown("#### 3. Гистограмм")
                st.markdown(f"""
- **Зорилго**：Бүлэг бүрийн өгөгдлийн тархалтын хэлбэрийг харах
- **Хувьсагч**：
  - X тэнхлэг：`{result["data_var"]}`
  - Өнгө：`{result["group_var"]}`
- **Онцлог**：Тархалтын хэлбэр ба харьцуулалтыг харуулна
                """)
        
        if lang == 'zh':
            st.info("💡 **操作步骤**：前往 **📈 绘图视图** → 选择对应图表类型 → 设置变量 → 生成图表")
        else:
            st.info("💡 **Алхам**：**📈 График харах** руу очих → Графикийн төрөл сонгох → Хувьсагч тохируулах → График үүсгэх")
    
    # 描述统计结果
    elif isinstance(result, dict) and not result.get("test_type"):
        title = "### 📋 描述统计结果" if lang == 'zh' else "### 📋 Тайлбар статистик"
        st.markdown(title)
        
        # 分别处理不同类型的变量
        for var, stats in result.items():
            if isinstance(stats, dict):
                st.markdown(f"#### 📌 {var}")
                
                # 如果有错误，显示错误信息
                if "error" in stats:
                    st.error(f"❌ {stats['error']}")
                    if "n" in stats:
                        st.info(f"样本量: {stats['n']}, 缺失值: {stats.get('missing', 0)}")
                    continue
                
                # 🎯 多选题类型
                if stats.get("type") == "multiple_choice":
                    st.success(f"✅ 自动识别为多选题（检测到分号分隔）")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("有效回答", stats["n"])
                    col2.metric("总选择次数", stats["n_selections"])
                    col3.metric("人均选择", stats["avg_per_person"])
                    col4.metric("缺失值", stats["missing"])
                    
                    # 选项频次表
                    if stats["option_frequencies"]:
                        freq_df = pd.DataFrame({
                            "选项": list(stats["option_frequencies"].keys()),
                            "选择人数": list(stats["option_frequencies"].values()),
                            "百分比(%)": [f"{stats['option_percentages'][opt]:.1f}%" 
                                         for opt in stats["option_frequencies"].keys()]
                        }).sort_values("选择人数", ascending=False)
                        
                        st.dataframe(freq_df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("⚠️ 该变量无有效数据")
                    
                    st.markdown("---")
                
                # 数值型变量
                elif stats.get("type") == "numeric" and "mean" in stats and "error" not in stats:
                    try:
                        stat_row = {
                            "样本量": stats["n"],
                            "均值": f"{stats['mean']:.2f}",
                            "标准差": f"{stats['std']:.2f}",
                            "最小值": f"{stats['min']:.2f}",
                            "Q1": f"{stats['q1']:.2f}",
                            "中位数": f"{stats['median']:.2f}",
                            "Q3": f"{stats['q3']:.2f}",
                            "最大值": f"{stats['max']:.2f}",
                            "缺失值": stats["missing"]
                        }
                        st.dataframe(pd.DataFrame([stat_row]), use_container_width=True, hide_index=True)
                    except Exception as e:
                        st.error(f"显示数值统计时出错: {str(e)}")
                    st.markdown("---")
                
                # 普通分类变量
                elif stats.get("type") == "categorical":
                    try:
                        col1, col2, col3 = st.columns(3)
                        col1.metric("样本量", stats.get("n", 0))
                        col2.metric("唯一值", stats.get("unique", 0))
                        col3.metric("缺失值", stats.get("missing", 0))
                        
                        # 使用all_values显示所有值，而不是只显示前5个
                        values_dict = stats.get("all_values") or stats.get("top_values")
                        
                        if values_dict:
                            # 获取值标签
                            value_labels = stats.get("value_labels", {})
                            
                            # 构建数据框，包含标签信息
                            categories = []
                            frequencies = []
                            percentages_list = []
                            
                            # 安全排序：检查所有键是否为数字类型
                            all_keys = list(values_dict.keys())
                            all_numeric = all(isinstance(k, (int, float)) and not isinstance(k, bool) for k in all_keys)
                            
                            if all_numeric:
                                sorted_keys = sorted(all_keys)
                            else:
                                sorted_keys = sorted(all_keys, key=str)
                            
                            for cat in sorted_keys:
                                # 如果有标签，显示"数值（标签）"格式
                                if value_labels and cat in value_labels:
                                    cat_display = f"{cat} ({value_labels[cat]})"
                                else:
                                    cat_display = str(cat)
                                
                                # 如果频次为0，添加标记
                                freq = values_dict[cat]
                                if freq == 0:
                                    cat_display = f"{cat_display} 🔵"
                                
                                categories.append(cat_display)
                                frequencies.append(freq)
                                percentages_list.append(f"{stats['percentages'].get(cat, 0):.1f}%")
                            
                            if lang == 'zh':
                                freq_df = pd.DataFrame({
                                    "类别": categories,
                                    "频次": frequencies,
                                    "百分比(%)": percentages_list
                                })
                                freq_df = freq_df.sort_values("频次", ascending=False)
                            else:
                                freq_df = pd.DataFrame({
                                    "Ангилал": categories,
                                    "Давтамж": frequencies,
                                    "Хувь(%)": percentages_list
                                })
                                freq_df = freq_df.sort_values("Давтамж", ascending=False)
                            
                            st.dataframe(freq_df, use_container_width=True, hide_index=True)
                            
                            # 如果有频次为0的值，显示提示
                            if any(values_dict[k] == 0 for k in values_dict.keys()):
                                info_msg = "🔵 蓝色标记表示该值在值标签中定义，但数据中未出现（频次=0）" if lang == 'zh' else "🔵 Цэнхэр тэмдэглэгээ нь утгын тэмдэглэгээнд тодорхойлсон боловч өгөгдөлд байхгүй утгыг илэрхийлнэ (давтамж=0)"
                                st.info(info_msg)
                        else:
                            warn_msg = "⚠️ 该变量无有效数据" if lang == 'zh' else "⚠️ Энэ хувьсагчид хүчинтэй өгөгдөл байхгүй"
                            st.warning(warn_msg)
                    except Exception as e:
                        err_msg = f"显示分类统计时出错: {str(e)}" if lang == 'zh' else f"Ангиллын статистик харуулахад алдаа: {str(e)}"
                        st.error(err_msg)
                    
                    st.markdown("---")
        
        # 绘图建议
        title = "### 📊 推荐图表" if lang == 'zh' else "### 📊 Зөвлөмж болгох график"
        st.markdown(title)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if lang == 'zh':
                st.markdown("#### 1. 直方图")
                st.markdown("""
- **用途**：查看数据分布形态
- **可识别**：
  - 正态性
  - 偏态（左偏/右偏）
  - 峰度（尖峰/平峰）
                """)
            else:
                st.markdown("#### 1. Гистограмм")
                st.markdown("""
- **Зорилго**：Өгөгдлийн тархалтын хэлбэрийг харах
- **Таних**：
  - Хэвийн байдал
  - Хазайлт (зүүн/баруун)
  - Оргил (өндөр/намхан)
                """)
        
        with col2:
            if lang == 'zh':
                st.markdown("#### 2. 箱线图")
                st.markdown("""
- **用途**：识别异常值和分布特征
- **显示内容**：
  - 中位数、四分位数
  - 最小值、最大值
  - 离群点
                """)
            else:
                st.markdown("#### 2. Хайрцаг график")
                st.markdown("""
- **Зорилго**：Гажуудал ба тархалтын онцлогийг тодорхойлох
- **Харуулах**：
  - Медиан, дөрвөн хувиар
  - Хамгийн бага, хамгийн их утга
  - Гажуудлын цэг
                """)
        
        if lang == 'zh':
            st.info("💡 **操作步骤**：前往 **📈 绘图视图** → 选择图表类型 → 选择变量")
        else:
            st.info("💡 **Алхам**：**📈 График харах** руу очих → Графикийн төрөл сонгох → Хувьсагч сонгох")
    
    # Pearson 相关结果
    elif isinstance(result, dict) and result.get("test_type") == "Pearson 相关分析":
        title = "### 📊 相关系数矩阵" if lang == 'zh' else "### 📊 Корреляцийн коэффициентийн матриц"
        st.markdown(title)
        corr_df = pd.DataFrame(result["correlation_matrix"])
        st.dataframe(corr_df.style.background_gradient(cmap='coolwarm', vmin=-1, vmax=1), use_container_width=True)
        
        title = "### 📊 显著性(p值)矩阵" if lang == 'zh' else "### 📊 Ач холбогдол(p утга) матриц"
        st.markdown(title)
        p_df = pd.DataFrame(result["p_value_matrix"])
        st.dataframe(p_df, use_container_width=True)
        
        # 绘图建议 - 基于相关分析结果
        title = "### 📊 可视化建议" if lang == 'zh' else "### 📊 Дүрслэлийн зөвлөмж"
        st.markdown(title)
        
        # 找出显著相关的变量对
        corr_matrix = result["correlation_matrix"]
        p_matrix = result["p_value_matrix"]
        variables = result["variables"]
        
        strong_correlations = []
        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                if i < j:  # 避免重复
                    r = corr_matrix[var1][var2]
                    p = p_matrix[var1][var2]
                    if p < 0.05 and abs(r) > 0.3:  # 显著且中等以上相关
                        strong_correlations.append({
                            'var1': var1,
                            'var2': var2,
                            'r': r,
                            'p': p,
                            'strength': ('强' if lang == 'zh' else 'Хүчтэй') if abs(r) > 0.7 else ('中等' if lang == 'zh' else 'Дунд') if abs(r) > 0.5 else ('弱到中等' if lang == 'zh' else 'Сул-Дунд')
                        })
        
        if strong_correlations:
            msg = "**✅ 发现显著相关关系！**" if lang == 'zh' else "**✅ Мэдэгдэхүйц хамаарал олдсон！**"
            st.success(msg)
            
            # 展示相关关系详情
            for corr in strong_correlations:
                if lang == 'zh':
                    direction = "正相关" if corr['r'] > 0 else "负相关"
                    sig_level = "***" if corr['p'] < 0.001 else "**" if corr['p'] < 0.01 else "*"
                    st.markdown(f"- **`{corr['var1']}`** 与 **`{corr['var2']}`**：{direction}，r = {corr['r']:.3f} (p = {corr['p']:.3f}{sig_level})，强度：{corr['strength']}")
                else:
                    direction = "Эерэг хамаарал" if corr['r'] > 0 else "Сөрөг хамаарал"
                    sig_level = "***" if corr['p'] < 0.001 else "**" if corr['p'] < 0.01 else "*"
                    st.markdown(f"- **`{corr['var1']}`** ба **`{corr['var2']}`**：{direction}，r = {corr['r']:.3f} (p = {corr['p']:.3f}{sig_level})，Хүч：{corr['strength']}")
            
            title = "### 📊 推荐图表" if lang == 'zh' else "### 📊 Зөвлөмж болгох график"
            st.markdown(title)
            
            # 为每个显著相关对提供散点图建议
            for idx, corr in enumerate(strong_correlations[:3], 1):
                expander_title = f"📈 散点图 {idx}：`{corr['var1']}` vs `{corr['var2']}`" if lang == 'zh' else f"📈 Цэгэн график {idx}：`{corr['var1']}` vs `{corr['var2']}`"
                with st.expander(expander_title, expanded=(idx==1)):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if lang == 'zh':
                            st.markdown(f"""
**变量设置**：
- X轴：`{corr['var1']}`
- Y轴：`{corr['var2']}`

**预期结果**：
- 相关系数：r = {corr['r']:.3f}
- 趋势方向：{'正向（右上）' if corr['r'] > 0 else '负向（右下）'}
- 线性强度：{corr['strength']}
                            """)
                        else:
                            st.markdown(f"""
**Хувьсагчийн тохиргоо**：
- X тэнхлэг：`{corr['var1']}`
- Y тэнхлэг：`{corr['var2']}`

**Хүлээгдэж буй үр дүн**：
- Корреляцийн коэффициент：r = {corr['r']:.3f}
- Чиг хандлага：{'Эерэг (баруун дээш)' if corr['r'] > 0 else 'Сөрөг (баруун доош)'}
- Шугаман хүч：{corr['strength']}
                            """)
                    with col2:
                        label = "相关系数" if lang == 'zh' else "Корреляци"
                        st.metric(label, f"{corr['r']:.3f}")
                        label = "显著性" if lang == 'zh' else "Ач холбогдол"
                        st.metric(label, f"p={corr['p']:.4f}")
            
            if lang == 'zh':
                st.info("💡 **操作步骤**：前往 **📈 绘图视图** → 选择「散点图」→ 按上述变量设置")
            else:
                st.info("💡 **Алхам**：**📈 График харах** руу очих → 「Цэгэн график」сонгох → Дээрх хувьсагчийн тохиргоог дагах")
        else:
            if lang == 'zh':
                st.warning("**未发现显著的强相关关系**")
                vars_list = ", ".join([f"`{v}`" for v in variables])
                st.info(f"""
变量 {vars_list} 之间的相关性较弱或不显著。

**可选可视化**：
- 仍可绘制散点图矩阵查看整体分布
- 或分别对各变量进行描述性可视化（直方图、箱线图）
                """)
            else:
                st.warning("**Мэдэгдэхүйц хүчтэй хамаарал олдсонгүй**")
                vars_list = ", ".join([f"`{v}`" for v in variables])
                st.info(f"""
{vars_list} хувьсагчдын хоорондын хамаарал сул эсвэл мэдэгдэхүйц бус байна.

**Сонголтот дүрслэл**：
- Бүх тархалтыг харахын тулд цэгэн график матриц зурж болно
- Эсвэл хувьсагч бүрийг тус тусад нь тайлбарлах дүрслэл (гистограмм, хайрцаг график)
                """)

def format_ai_response(content: str):
    """格式化AI回复，高亮显示结论性语句"""
    if not content:
        return
    
    # 过滤掉不应该显示的内容
    # 1. 过滤"undefined"
    content = content.replace("undefined", "").strip()
    
    # 2. 过滤代码块（三个反引号包裹的内容）
    content = re.sub(r'```[\s\S]*?```', '', content)
    content = re.sub(r'`[^`]*`', '', content)  # 过滤单个反引号
    
    # 2.5 过滤表格（markdown表格或文本表格）
    content = re.sub(r'\|.*?\|.*?\n', '', content)  # 过滤markdown表格行
    content = re.sub(r'[┌┬┐├┼┤└┴┘─│]+', '', content)  # 过滤文本表格边框
    
    # 3. 过滤函数调用代码（如 independent_t_test(...) 等）
    content = re.sub(r'independent_t_test\([^)]*\)', '', content)
    content = re.sub(r'descriptive_stats\([^)]*\)', '', content)
    content = re.sub(r'pearson_correlation\([^)]*\)', '', content)
    content = re.sub(r'multiple_choice_analysis\([^)]*\)', '', content)
    
    # 4. 过滤"基于...结果："这类提示语
    content = re.sub(r'基于[^：]*检验结果[：:]\s*', '', content)
    content = re.sub(r'基于[^：]*分析结果[：:]\s*', '', content)
    content = re.sub(r'基于[^：]*统计[：:]\s*', '', content)
    
    # 5. 过滤"让我..."这类提示语
    content = re.sub(r'^让我[^。！？\n]*[。！？\n]', '', content)
    content = re.sub(r'^我[将会已][^。！？\n]*[。！？\n]', '', content)
    
    # 5.5 过滤常见的说明性标题
    content = re.sub(r'实际效果[:：]\s*\n', '', content)
    content = re.sub(r'分析结果[:：]\s*\n', '', content)
    content = re.sub(r'统计结果[:：]\s*\n', '', content)
    
    # 6. 过滤空行和多余空格
    content = re.sub(r'\n\s*\n', '\n', content).strip()
    
    if not content:
        return
    
    # 定义结论性关键词模式
    conclusion_patterns = [
        r'.*?有(非常)?显著.*?影响.*?',
        r'.*?没有显著.*?影响.*?',
        r'.*?无显著.*?影响.*?',
        r'.*?存在显著.*?(差异|相关|关系).*?',
        r'.*?不存在显著.*?(差异|相关|关系).*?',
        r'.*?显著(高|低|大|小)于.*?',
        r'.*?有(正面|负面|积极|消极)影响.*?',
        r'.*?具有统计学意义.*?',
        r'.*?差异(不)?具有统计学意义.*?'
    ]
    
    # 按句子分割（支持中英文句号、感叹号、问号）
    sentences = re.split(r'([。！？\n])', content)
    
    # 重组句子（保留分隔符）
    full_sentences = []
    for i in range(0, len(sentences)-1, 2):
        if i+1 < len(sentences):
            full_sentences.append(sentences[i] + sentences[i+1])
    if len(sentences) % 2 == 1:
        full_sentences.append(sentences[-1])
    
    # 处理每个句子
    for sentence in full_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # 检查是否为结论性语句
        is_conclusion = False
        for pattern in conclusion_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                is_conclusion = True
                break
        
        if is_conclusion:
            # 用蓝底高亮显示
            st.markdown(f"""<div style="background-color: #2196F3; padding: 12px; border-radius: 5px; border-left: 4px solid #0D47A1; margin: 0; color: white;"><strong>📌 {sentence}</strong></div>""", unsafe_allow_html=True)
        else:
            # 普通显示（去掉前后空白）
            if sentence.strip():
                st.markdown(f'<p style="margin: 0 0 8px 0;">{sentence}</p>', unsafe_allow_html=True)

def render_ai_view():
    lang = get_lang()
    
    # 强制检查并清理损坏的对话历史
    has_error = False
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        try:
            # 深度验证对话历史中的统计结果
            for msg in st.session_state.chat_history:
                if 'stat_result' in msg:
                    result = msg['stat_result']
                    if isinstance(result, dict):
                        # 检查是否包含无效的数据类型
                        for var, stats in result.items():
                            if isinstance(stats, dict):
                                # 检查数值型变量的数据
                                if stats.get('type') == 'numeric' and 'mean' in stats:
                                    # 尝试访问mean值
                                    _ = float(stats['mean'])
                if 'stat_results' in msg:
                    for result in msg['stat_results']:
                        if isinstance(result, dict):
                            for var, stats in result.items():
                                if isinstance(stats, dict) and stats.get('type') == 'numeric' and 'mean' in stats:
                                    _ = float(stats['mean'])
        except Exception as e:
            # 如果发现任何错误，标记需要清空
            has_error = True
    
    # 如果检测到错误，清空对话历史并立即返回
    if has_error:
        st.session_state.chat_history = []
        success_text = "✅ 已自动清理损坏的对话历史" if lang == 'zh' else "✅ Гэмтэгдсэн харилцан ярианы түүхийг автоматаар цэвэрлэлээ"
        st.success(success_text)
        info_text = "💡 页面将自动刷新..." if lang == 'zh' else "💡 Хуудас автоматаар сэргээнэ..."
        st.info(info_text)
        st.rerun()
        return
    
    # 添加紧急清空按钮（在顶部）
    emergency_col1, emergency_col2 = st.columns([0.85, 0.15])
    with emergency_col2:
        btn_text = "🆘 紧急清空" if lang == 'zh' else "🆘 Яаралтай цэвэрлэх"
        btn_help = "如果出现错误，点击此按钮" if lang == 'zh' else "Алдаа гарвал энэ товчийг дарна уу"
        if st.button(btn_text, help=btn_help, type="secondary", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # 标题行和快捷按钮
    col1, col2, col3 = st.columns([2.0, 2.2, 0.4])
    with col1:
        title = "🤖 AI 辅助分析" if lang == 'zh' else "🤖 AI туслах шинжилгээ"
        st.title(title)
    with col2:
        # 快捷按钮组
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            btn_text = "📁 数据" if lang == 'zh' else "📁 Өгөгдөл"
            btn_help = "跳转到数据视图" if lang == 'zh' else "Өгөгдлийн харах руу шилжих"
            if st.button(btn_text, help=btn_help, use_container_width=True):
                st.session_state.current_page = "data"
                st.rerun()
        with btn_col2:
            btn_text = "📈 绘图" if lang == 'zh' else "📈 График"
            btn_help = "跳转到绘图视图" if lang == 'zh' else "График харах руу шилжих"
            if st.button(btn_text, help=btn_help, use_container_width=True):
                st.session_state.current_page = "plot"
                st.rerun()
        with btn_col3:
            btn_text = "📊 统计" if lang == 'zh' else "📊 Статистик"
            btn_help = "跳转到统计视图" if lang == 'zh' else "Статистик харах руу шилжих"
            if st.button(btn_text, help=btn_help, use_container_width=True):
                st.session_state.current_page = "stat"
                st.rerun()
    with col3:
        btn_help = "查看新手指南" if lang == 'zh' else "гарын авлага үзэх"
        if st.button("❓", help=btn_help, use_container_width=True, type="secondary"):
            st.session_state.current_page = "help"
            st.rerun()
    
    # AI 配置
    expander_title = "⚙️ AI 配置" if lang == 'zh' else "⚙️ AI тохиргоо"
    with st.expander(expander_title, expanded=not st.session_state.ai_config['enabled']):
        config_title = "### DeepSeek API 配置" if lang == 'zh' else "### DeepSeek API тохиргоо"
        st.markdown(config_title)
        checkbox_label = "开启 AI 辅助分析" if lang == 'zh' else "AI туслах шинжилгээг асаах"
        enable = st.checkbox(checkbox_label, value=st.session_state.ai_config['enabled'])
        api_key = st.text_input("API Key", value=st.session_state.ai_config['api_key'], type="password")
        base_url = st.text_input("API Base URL", value=st.session_state.ai_config['base_url'])
        model_label = "模型名称" if lang == 'zh' else "Моделийн нэр"
        model = st.text_input(model_label, value=st.session_state.ai_config['model'])
        
        save_btn = "保存配置" if lang == 'zh' else "Тохиргоо хадгалах"
        if st.button(save_btn):
            st.session_state.ai_config = {'enabled': enable, 'api_key': api_key, 'base_url': base_url, 'model': model}
            success_text = "✅ 配置已保存" if lang == 'zh' else "✅ Тохиргоог хадгаллаа"
            st.success(success_text)
    
    if not st.session_state.ai_config['enabled'] or not st.session_state.ai_config['api_key']:
        info_text = "💡 请先配置并开启 AI 辅助分析" if lang == 'zh' else "💡 Эхлээд AI туслах шинжилгээг тохируулж асаана уу"
        st.info(info_text)
        return
    
    st.markdown("---")
    subheader = "💬 AI 助手" if lang == 'zh' else "💬 AI туслах"
    st.subheader(subheader)
    
    # 显示对话历史
    try:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                if msg['role'] == 'user':
                    st.markdown(msg['content'])
                else:
                    # AI 回复可能包含统计结果
                    if 'stat_result' in msg:
                        display_stat_result(msg['stat_result'], lang)
                    elif 'stat_results' in msg:
                        # 显示多个统计结果
                        for result in msg['stat_results']:
                            display_stat_result(result, lang)
                            st.markdown("---")  # 分隔线
                    if 'content' in msg and msg['content']:
                        format_ai_response(msg['content'])
    except Exception as e:
        error_text = f"❌ 显示对话历史时出错: {str(e)}" if lang == 'zh' else f"❌ Харилцан ярианы түүхийг харуулах үед алдаа гарлаа: {str(e)}"
        st.error(error_text)
        warning_text = "⚠️ 对话历史可能包含损坏的数据。请点击下方'清空对话'按钮。" if lang == 'zh' else "⚠️ Харилцан ярианы түүх гэмтсэн өгөгдөл агуулж байж болно. Доорх 'Харилцаа цэвэрлэх' товчийг дарна уу."
        st.warning(warning_text)
        # 自动提示清空
        btn_text = "🗑️ 立即清空对话" if lang == 'zh' else "🗑️ Одоо цэвэрлэх"
        if st.button(btn_text, type="primary"):
            st.session_state.chat_history = []
            st.rerun()
    
    # ================================
    # 🎯 步骤1: 用户输入
    # ================================
    # 功能：获取用户在聊天框中输入的问题
    # 示例：用户输入 "父母监督对作业完成率有影响吗？"
    input_placeholder = "输入您的问题..." if lang == 'zh' else "Асуултыгаа оруулна уу..."
    user_input = st.chat_input(input_placeholder)
    
    if user_input:
        # 将用户输入保存到对话历史中
        # 格式：{'role': 'user', 'content': '用户的问题'}
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        # ================================
        # 🎯 步骤2: 构建System Prompt（系统提示词）
        # ================================
        # 目的：告诉AI它的角色、能力和数据上下文
        
        # 2.1 准备数据上下文
        # 功能：将当前数据集的基本信息传递给AI
        # 包括：数据行数、列数、变量名列表
        data_context = ""
        if st.session_state.data is not None:
            df = st.session_state.data
            # 创建简化的变量列表（用于AI参考）
            columns_list = "\n".join([f"  - {col}" for col in df.columns])
            data_context = f"""当前数据集：{len(df)}行，{len(df.columns)}列。

**变量列表**（参考，调用函数时可以使用关键词模糊匹配）：
{columns_list}

💡 **模糊匹配功能**：
- 可以使用简短的关键词，如"满意度"、"选项"、"类别"
- 系统会自动匹配到完整的变量名
- 不需要输入完整的变量名（包括括号、标点符号等）"""
        
        # 2.2 获取值标签上下文
        # 功能：如果用户设置了值标签（如 1=是, 0=否），传递给AI
        # 作用：让AI能理解数值的含义，在解释结果时使用标签
        labels_context = get_labels_context()
        
        # 2.3 组装完整的系统提示词
        # 这是AI的"使用说明书"，定义了它的能力、规则和输出格式
        system_prompt = f"""你是 AIStats 的 AI 助手。{data_context}

🌍 **【重要】双语输出要求 / Хоёр хэлээр гаргах шаардлага**：
你必须使用**汉语（中文）**和**西里尔蒙古语（Кирилл монгол хэл）**双语输出所有分析结果。

**输出格式规范 / Гаралтын формат**：
每段分析内容都要按以下格式：
🇨🇳 [中文内容]
🇲🇳 [Кирилл монгол хэлээр илэрхийлсэн агуулга]

**统计学术语对照表 / Статистикийн нэр томъёо**：
- 平均值 = Дундаж утга
- 标准差 = Стандарт хазайлт  
- 显著性 = Ач холбогдол
- 相关性 = Хамаарал
- 假设检验 = Таамаглалын шалгалт
- t检验 = t шалгалт
- 方差分析 = Дисперсийн шинжилгээ
- 回归分析 = Регрессийн шинжилгээ
- 频次 = Давтамж
- 百分比 = Хувь
- 差异 = Ялгаа
- 样本量 = Түүврийн хэмжээ
- 结论 = Дүгнэлт
- 分析结果 = Шинжилгээний үр дүн

**可用函数**：
- independent_t_test: 比较两组均值差异
- descriptive_stats: 描述统计（智能识别变量类型）
  - 数值型连续变量：计算均值、标准差等
  - 分类变量（包括数值型但设置了值标签的）：统计频次、占比
  - 多选题（分号分隔）：统计各选项频次
- pearson_correlation: 相关分析

**核心规则**：
1. 用户询问"统计"、"分析"、"频次"时 → **立即调用函数**，不要解释
2. **可以使用关键词**：如"满意度"、"选项"、"类别"，系统会自动模糊匹配到完整变量名
3. descriptive_stats 会**自动识别**变量类型（数值/分类/多选题），无需判断
4. **严禁**输出：代码、表格数据、"让我..."、"实际效果"等
5. **解释结果时必须同时显示数值和标签**：例如"3（一般）"而不是只说"一般"
6. **必须列出所有值的频次**：包括频次为0的值
7. 🔴 **学术规范（极其重要）**：任何结论前必须先说明统计依据
8. 🌍 **双语输出（必须遵守）**：每段内容都要中蒙双语

**关于值标签的使用**：
- 值标签定义了变量的完整值域（例如：1=非常不满意，2=不满意，3=一般，4=满意，5=非常满意）
- 统计结果会显示所有定义的值，包括频次为0的值
- **解释时必须**：结合数值和标签，列出所有值的频次（包括0）
- 格式："数值（标签）频次"，例如"3（一般）5人"

**调用函数示例**（使用模糊匹配）：
示例1：
用户："统计满意度"
→ 调用 descriptive_stats(["满意度"]) ← 使用关键词即可

示例2：
用户："分析选择题"
→ 调用 descriptive_stats(["选择题"]) ← 使用关键词
→ 系统会自动识别单选、多选、数值型

**正确的回答方式**：
- 函数会返回完整统计（包括频次为0的值）
- 如果有值标签，必须在回复中显示"数值（标签）频次"
- 例如："满意度分布：1（非常不满意）0人，2（不满意）3人，3（一般）5人，4（满意）8人，5（非常满意）4人。大部分人满意。"

**关键要求**：
✅ 列出所有值及其频次（包括频次为0的）
✅ 数值和标签都要显示，格式：数值（标签）频次
✅ 频次为0的值也要明确说明
✅ 严格使用实际数据中的值标签，不要编造或使用示例标签

**🔴 学术规范回答格式（必须遵守）**：

正确格式：
1. **先说明统计依据**（检验方法+统计量+p值+实际数据）
2. **再给出结论**（因为XXX，所以YYY）

🔴 **严禁编造数据**：
- 必须使用函数返回的实际统计结果
- 不要编造任何数字、百分比、统计量
- 数据必须与统计结果完全一致

示例1（相关分析）：
✅ 正确："基于Pearson相关分析，r=0.65, p<0.001，所以父母监督程度与作业完成率之间存在显著的正相关关系。"
❌ 错误："父母监督程度与作业完成率之间存在显著的正相关关系。"（缺少统计依据）

示例2（t检验）：
✅ 正确："根据独立样本t检验，t=3.45, p=0.002<0.05，所以男生和女生在成绩上存在显著差异。"
❌ 错误："男生和女生在成绩上存在显著差异。"（缺少统计依据）

示例3（描述统计/频次统计）：
✅ 正确："根据频次统计，7年级7人（35%），8年级7人（35%），9年级6人（30%），所以7年级和8年级人数相同。"
❌ 错误："7年级5人（25%），8年级10人（50%），9年级5人（25%）"（编造数据，与实际不符）
❌ 错误："初二学生最多。"（缺少具体数据）

**关键原则**：
🔴 任何带有"显著"、"存在"、"差异"、"相关"等结论性词汇的语句
🔴 必须在前面加上"基于XXX分析/检验，统计量=X, p=X，所以..."

**错误示例**：
❌ 只说描述性文字，不列出具体数值
❌ 忽略频次为0的值
❌ 只说标签不说数值
❌ 只说数值不说标签
❌ 使用不存在的值或标签
❌ **编造数据**：给出的数字与统计结果不一致（极其严重的错误！）
❌ **直接给结论，不说明统计依据**（严重错误）

❌ 禁止：解释步骤、输出表格、显示代码

{labels_context if labels_context else ""}"""
        
        try:
            # ================================
            # 🎯 步骤3: 组装消息列表
            # ================================
            # 功能：将系统提示 + 历史对话 组装成完整的消息列表
            # 格式：[{role: 'system', content: '...'}, {role: 'user', content: '...'}, ...]
            
            # 3.1 创建OpenAI客户端
            # 使用用户配置的API Key和Base URL连接到AI服务
            client = OpenAI(
                api_key=st.session_state.ai_config['api_key'], 
                base_url=st.session_state.ai_config['base_url']
            )
            
            # 3.2 组装消息列表
            # 结构：[系统消息] + [用户和AI的历史对话]
            # 系统消息（system）：定义AI的角色和能力
            # 历史对话：包含之前所有的user和assistant消息
            messages = [
                {"role": "system", "content": system_prompt}  # 系统提示（只有一条）
            ] + [
                {"role": m['role'], "content": m.get('content', '')}  # 历史对话（可能有多条）
                for m in st.session_state.chat_history
            ]
            
            # ================================
            # 🎯 步骤4: 第一次API调用（核心）⭐
            # ================================
            # 目的：将用户问题发送到AI，让AI决定是否需要调用统计函数
            # 这是"双向绑定"机制的第一步：用户 → AI
            
            spinner_text = "AI 分析中..." if lang == 'zh' else "AI шинжилж байна..."
            with st.spinner(spinner_text):
                # 4.1 调用OpenAI API（第一次）
                # 参数说明：
                # - model: 使用的AI模型（如 deepseek-chat）
                # - messages: 上面组装的消息列表（包含系统提示+历史对话）
                # - tools: 可用的工具列表（9个统计函数的定义）
                # - tool_choice: "auto" 表示让AI自动决定是否调用工具
                response = client.chat.completions.create(
                    model=st.session_state.ai_config['model'],
                    messages=messages,
                    tools=TOOLS,  # 传递工具定义，让AI知道有哪些函数可以调用
                    tool_choice="auto"  # 让AI自动判断是否需要调用工具
                )
                
                # 4.2 获取AI的响应
                assistant_message = response.choices[0].message
                stat_results = []  # 用于保存所有统计函数的执行结果
                
                # ================================
                # 🎯 步骤5: 处理工具调用（执行统计函数）
                # ================================
                # 目的：如果AI决定调用统计函数，执行实际的统计计算
                # 这是"双向绑定"机制的第二步：AI → 统计引擎
                
                # 5.1 检查AI是否决定调用工具
                # assistant_message.tool_calls 包含AI想调用的函数信息
                # 如果为空，说明AI认为不需要统计，直接文字回复
                if assistant_message.tool_calls:
                    function_results = []  # 存储函数执行结果的文本描述
                    
                    # 5.2 遍历所有工具调用（可能有多个）
                    # 例如：AI可能同时调用 descriptive_stats 和 correlation
                    for tool_call in assistant_message.tool_calls:
                        # 解析函数名和参数
                        function_name = tool_call.function.name  # 例如："independent_t_test"
                        function_args = json.loads(tool_call.function.arguments)  # 例如：{"data_var": "...", "group_var": "..."}
                        
                        # 5.3 执行实际的统计函数
                        # TOOL_FUNCTIONS 是一个字典，包含所有可调用的统计函数
                        # 例如：TOOL_FUNCTIONS["independent_t_test"](data_var="...", group_var="...")
                        if function_name in TOOL_FUNCTIONS:
                            result = TOOL_FUNCTIONS[function_name](**function_args)  # 执行统计计算
                            stat_results.append(result)  # 保存结果（用于显示统计表格）
                            function_results.append(f"{function_name}: {json.dumps(result, ensure_ascii=False)}")  # 保存结果文本（用于传递给AI）
                    
                    # ================================
                    # 🎯 步骤6: 第二次API调用（让AI解读结果）⭐
                    # ================================
                    # 目的：将统计结果发送给AI，让AI用通俗语言解释
                    # 这是"双向绑定"机制的第三步：统计结果 → AI → 用户
                    
                    # 6.1 准备结果文本
                    # 将所有统计结果合并成一个字符串
                    results_text = "\n".join(function_results)
                    
                    # 6.2 将统计结果添加到消息列表
                    # 先添加AI的"我已经执行了统计"的消息
                    messages.append({
                        "role": "assistant", 
                        "content": f"已执行统计分析并获得结果：\n\n{results_text}"
                    })
                    
                    # 6.3 添加用户的"请解释结果"指令
                    # 这个提示词要求AI用通俗语言解释统计结果
                    messages.append({
                        "role": "user",
                        "content": """请基于上面的统计结果，用2-3句话解释。

🌍 **【关键】必须双语输出（中文+西里尔蒙文）/ Хоёр хэлээр гаргах**：
每段分析都要先用中文🇨🇳，然后用西里尔蒙文🇲🇳，格式如下：
🇨🇳 [中文内容]
🇲🇳 [Кирилл монгол хэлээр]

🔴 必须遵守的格式（三段式 / Гурван хэсэг）：
1. 先说明统计依据（包含实际的统计数据）
2. 分析数据特点（哪个最多/最少，趋势如何等）
3. **最后给出明确结论**（用"因此"、"所以"、"表明"等词，说明有/无关系、影响、差异）

🔴 严禁编造数据 / Өгөгдөл зохиож болохгүй：
- 必须使用上面提供的实际统计结果
- 不要编造任何数字或百分比
- 如果是频次统计，必须列出所有类别的实际频次和百分比

⚠️ 重要原则：
- 描述统计：只说分布特征，不推测变量关系
- 推断统计（t检验、相关等）：直接给出明确的关系结论
- **不要说"需要进一步分析"**，基于当前结果给结论

📌 双语示例 / Хоёр хэлний жишээ：

示例1（频次统计 - 描述统计 / Давтамжийн статистик）：
🇨🇳 根据频次统计，7年级7人（35%），8年级7人（35%），9年级6人（30%）。各年级人数分布较为均匀，7、8年级人数相同。
🇲🇳 Давтамжийн статистикийн дагуу, 7-р анги 7 хүн (35%), 8-р анги 7 хүн (35%), 9-р анги 6 хүн (30%). Анги тус бүрийн хүний тоо жигд тархсан бөгөөд 7, 8-р ангийн хүний тоо ижил байна.

示例2（相关分析 - 推断统计 / Хамаарлын шинжилгээ）：
🇨🇳 基于Pearson相关分析，r=0.65, p<0.001，为中等正相关。因此，变量X与变量Y存在显著正相关关系。
🇲🇳 Pearson-ийн хамаарлын шинжилгээнд үндэслэн, r=0.65, p<0.001, дунд зэргийн эерэг хамаарал байна. Иймд X хувьсагч ба Y хувьсагчийн хооронд мэдэгдэхүйц эерэг хамаарал байна.

示例3（t检验 - 推断统计 / t шалгалт）：
🇨🇳 根据独立样本t检验，t=3.45, p=0.002<0.05，两组存在显著差异。因此，分组变量对数据变量有显著影响。
🇲🇳 Бие даасан түүврийн t шалгалтын дагуу, t=3.45, p=0.002<0.05, хоёр бүлгийн хооронд мэдэгдэхүйц ялгаа байна. Иймд бүлгийн хувьсагч нь өгөгдлийн хувьсагчид мэдэгдэхүйц нөлөө үзүүлж байна.

❌ 错误示例 / Буруу жишээ：
- 只用中文或只用蒙文 / Зөвхөн хятад эсвэл зөвхөн монгол
- 不说明统计依据 / Статистик үндэслэлийг дурдаагүй
- 说"需要进一步分析" / "Цаашид шинжилгээ хийх шаардлагатай" гэж хэлэх

不要包含代码或表格。"""
                    })
                    
                    # 6.4 调用OpenAI API（第二次）
                    # 这次调用的目的是让AI解读统计结果
                    # messages 现在包含：系统提示 + 历史对话 + 统计结果 + 解释要求
                    final_response = client.chat.completions.create(
                        model=st.session_state.ai_config['model'],
                        messages=messages  # 包含了统计结果的完整对话
                    )
                    
                    # 6.5 获取AI的解释文字
                    # 这就是最终显示给用户的通俗易懂的分析结果
                    assistant_content = final_response.choices[0].message.content
                    
                    # ================================
                    # ✅ 双向绑定流程完成！
                    # ================================
                    # 完整流程回顾：
                    # 1. 用户输入问题："父母监督对作业完成率有影响吗？"
                    # 2. 构建系统提示（数据上下文 + 值标签 + 工具定义）
                    # 3. 组装消息列表（系统消息 + 历史对话）
                    # 4. 第一次API调用：AI理解意图，决定调用 independent_t_test
                    # 5. 执行统计函数：调用实际的统计计算，得到t值、p值等
                    # 6. 第二次API调用：AI解读结果，生成通俗易懂的文字
                    # 
                    # 最终效果：
                    # - 用户只说了一句话
                    # - AI自动完成了：选择方法 → 执行计算 → 解释结果
                    # - 这就是"双向绑定"：AI ⇄ 统计引擎 的实时交互
                    
                else:
                    # 分支：AI没有调用工具，直接回复了文字
                    # 这种情况通常是用户问了一般性问题，不需要统计计算
                    # 例如："你好"、"怎么用这个软件"等
                    assistant_content = assistant_message.content
                    # 检测用户是否在询问统计分析但AI没有调用工具
                    user_query = st.session_state.chat_history[-1]['content'].lower()
                    stat_keywords = ['统计', '分析', '描述', '多选', '频次', '百分比', '有效', '占比', '选项']
                    
                    if any(keyword in user_query for keyword in stat_keywords):
                        # 用户在询问统计但AI没有执行，提供帮助性回复
                        assistant_content = (
                            "⚠️ 我没有正确执行统计分析。\n\n"
                            "**正确的提问格式**：\n"
                            '对"你认为哪些作业方式有效？(Which Homework Methods Are Effective?) [Multiple Choice]"进行统计\n\n'
                            "**提示**：请使用完整的变量名（包括中英文和标点符号），我会自动识别是单选题还是多选题，并展示相应的统计结果。"
                        )
                    # 检测是否包含不应该出现的内容
                    elif any(keyword in assistant_content for keyword in ['```', 'python', 'descriptive_stats(', '让我', '实际效果']):
                        # AI可能在解释而不是执行，过滤掉这些内容
                        assistant_content = None  # 不显示
                
                # 添加回复
                msg = {'role': 'assistant'}
                if stat_results:
                    # 如果只有一个结果，保持向后兼容
                    if len(stat_results) == 1:
                        msg['stat_result'] = stat_results[0]
                    else:
                        msg['stat_results'] = stat_results  # 多个结果
                if assistant_content:
                    msg['content'] = assistant_content
                
                # 只有在有内容时才添加到历史记录
                if stat_results or assistant_content:
                    st.session_state.chat_history.append(msg)
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ {str(e)}")
    
    clear_btn = "🗑️ 清空对话" if lang == 'zh' else "🗑️ Харилцаа цэвэрлэх"
    if st.session_state.chat_history and st.button(clear_btn):
        st.session_state.chat_history = []
        st.rerun()

