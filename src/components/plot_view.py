"""绘图视图模块：折线图/散点图/柱状图/箱线图/饼图等"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from openai import OpenAI
from src.lib.variable_labels import get_value_labels
from src.lib.i18n import get_lang

def apply_value_labels(df, columns):
    """
    为指定列应用值标签，返回处理后的数据框副本
    
    参数:
        df: 原始数据框
        columns: 需要应用标签的列名列表
    
    返回:
        处理后的数据框（原始数据框的副本）
    """
    df_labeled = df.copy()
    
    for col in columns:
        if col not in df.columns:
            continue
            
        # 获取该列的值标签
        value_labels = get_value_labels(col)
        
        if value_labels:
            # 将数值映射为标签文本
            df_labeled[col] = df[col].map(lambda x: value_labels.get(x, x) if pd.notna(x) else x)
    
    return df_labeled

def get_ai_chart_analysis(chart_data, chart_type):
    """调用AI分析图表"""
    if not st.session_state.ai_config.get('enabled') or not st.session_state.ai_config.get('api_key'):
        return None
    
    try:
        client = OpenAI(
            api_key=st.session_state.ai_config['api_key'],
            base_url=st.session_state.ai_config['base_url']
        )
        
        # 构建提示词
        if chart_type == "scatter_with_trend":
            prompt = f"""
请用简单易懂的语言分析这个散点图：

- X轴变量：{chart_data['x']}
- Y轴变量：{chart_data['y']}
- 相关系数r：{chart_data['r']:.3f}
- 决定系数R²：{chart_data['r2']:.3f}
- 显著性p值：{chart_data['p']:.4f}
- 斜率：{chart_data['slope']:.3f}

请分析：
1. 两个变量的关系（正相关/负相关/无关）
2. 关系强度（强/中等/弱）
3. 用大白话解释这意味着什么
4. 这个关系是否可靠（看p值）

要求：口语化，小白能懂，直接给出结论和建议。不要重复列数据。
"""
        elif chart_type == "boxplot":
            prompt = f"""
请用简单易懂的语言分析这个箱线图：

- 变量：{chart_data['variable']}
- 分组：{chart_data['group']}
- 各组统计：
{chart_data['stats']}

请分析：
1. 哪个组的数值更高/更低
2. 各组的数据分布特征（集中/分散）
3. 是否有明显差异
4. 用大白话解释这意味着什么

要求：口语化，小白能懂，直接给出观察结论。
"""
        elif chart_type == "bar":
            prompt = f"""
请用简单易懂的语言分析这个柱状图：

- 变量：{chart_data['variable']}
- 分组：{chart_data['group']}
- 各组数值：
{chart_data['values']}

请分析：
1. 哪个组的数值最高/最低
2. 各组之间的差距如何
3. 用大白话解释这个对比的含义

要求：口语化，小白能懂，直接给出对比结论。
"""
        elif chart_type == "histogram":
            prompt = f"""
请用简单易懂的语言分析这个直方图：

- 变量：{chart_data['variable']}
- 平均值：{chart_data['mean']:.2f}
- 标准差：{chart_data['std']:.2f}
- 最小值：{chart_data['min']:.2f}
- 最大值：{chart_data['max']:.2f}

请分析：
1. 数据主要集中在什么范围
2. 分布是否均匀（有没有明显的高峰）
3. 用大白话解释这个分布的特点

要求：口语化，小白能懂，直接说观察到什么。
"""
        elif chart_type == "pie":
            prompt = f"""
请用简单易懂的语言分析这个饼图：

- 变量：{chart_data['variable']}
- 各部分占比：
{chart_data['proportions']}

请分析：
1. 哪个部分占比最大/最小
2. 是否有某个部分占主导地位
3. 用大白话解释这个分布的含义

要求：口语化，小白能懂，直接给出结论。
"""
        elif chart_type == "line":
            prompt = f"""
请用简单易懂的语言分析这个折线图：

- X轴：{chart_data['x_var']}
- Y轴变量：{chart_data['y_vars']}
- 趋势摘要：
{chart_data['trends']}

请分析：
1. 各条线的整体趋势（上升/下降/波动）
2. 是否有明显的峰值或低谷
3. 用大白话解释这些变化的含义

要求：口语化，小白能懂，直接描述观察到的趋势。
"""
        else:
            return None
        
        response = client.chat.completions.create(
            model=st.session_state.ai_config['model'],
            messages=[
                {"role": "system", "content": """你是一个数据可视化专家，擅长用简单的语言解读图表。

🌍 **【重要】双语输出要求**：
你必须使用**汉语（中文）**和**西里尔蒙古语（Кирилл монгол хэл）**双语输出所有分析结果。

**输出格式**：
🇨🇳 [中文内容]
🇲🇳 [Кирилл монгол хэлээр илэрхийлсэн агуулга]

**图表术语对照**：
趋势=Чиг хандлага, 上升=Өсөлт, 下降=Бууралت, 分布=Тархалт, 相关=Хамаарал"""},
                {"role": "user", "content": prompt + "\n\n🌍 请务必使用双语输出（中文+西里尔蒙文）！"}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"AI分析失败：{str(e)}")
        return None

def render_plot_view():
    lang = get_lang()
    
    # 标题行和快捷按钮
    col1, col2, col3 = st.columns([2.0, 2.2, 0.4])
    with col1:
        title = "📈 绘图视图" if lang == 'zh' else "📈 График харах"
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
            btn_text = "📊 统计" if lang == 'zh' else "📊 Статистик"
            btn_help = "跳转到统计视图" if lang == 'zh' else "Статистик харах руу шилжих"
            if st.button(btn_text, help=btn_help, use_container_width=True):
                st.session_state.current_page = "stat"
                st.rerun()
        with btn_col3:
            btn_help = "跳转到AI辅助分析" if lang == 'zh' else "AI туслах шинжилгээ рүү шилжих"
            if st.button("🤖 AI", help=btn_help, use_container_width=True):
                st.session_state.current_page = "ai"
                st.rerun()
    with col3:
        btn_help = "查看新手指南" if lang == 'zh' else "гарын авлага үзэх"
        if st.button("❓", help=btn_help, use_container_width=True, type="secondary"):
            st.session_state.current_page = "help"
            st.rerun()
    
    if st.session_state.data is None:
        warning_text = "⚠️ 请先在数据视图导入数据" if lang == 'zh' else "⚠️ Эхлээд өгөгдлийн харахаар өгөгдөл оруулна уу"
        st.warning(warning_text)
        return
    
    df = st.session_state.data
    
    # 提示用户关于值标签的功能
    if lang == 'zh':
        st.info("💡 **提示**：如果在 **🏷️ 值标签** 页面设置了值标签，图表会自动显示标签文字而不是原始数值。")
    else:
        st.info("💡 **Мэдээлэл**：Хэрэв **🏷️ Утгын тэмдэглэгээ** хуудсанд утгын тэмдэглэгээ тохируулсан бол график автоматаар анхны тоон утгын оронд тэмдэглэгээний текстийг харуулна.")
    
    # 选择图表类型
    if lang == 'zh':
        plot_types = ["折线图", "散点图", "柱状图", "箱线图", "饼图", "直方图", "3D散点图"]
        label = "选择图表类型"
    else:
        plot_types = ["Шугаман график", "Цэгэн график", "Багана график", "Хайрцаг график", "Дугуй диаграмм", "Гистограмм", "3D цэгэн график"]
        label = "Графикийн төрөл сонгох"
    
    plot_type = st.selectbox(label, plot_types)
    
    st.markdown("---")
    
    # 根据语言确定图表类型索引
    plot_index = plot_types.index(plot_type) if plot_type in plot_types else 0
    
    # 折线图 (index 0)
    if plot_index == 0:
        subheader = "📉 折线图" if lang == 'zh' else "📉 Шугаман график"
        st.subheader(subheader)
        
        label = "X 轴变量" if lang == 'zh' else "X тэнхлэгийн хувьсагч"
        x_col = st.selectbox(label, df.columns, key="line_x")
        label = "Y 轴变量（可多选）" if lang == 'zh' else "Y тэнхлэгийн хувьсагч (олон сонголттой)"
        y_cols = st.multiselect(label, df.columns, key="line_y")
        
        if y_cols:
            label = "显示数据点" if lang == 'zh' else "Өгөгдлийн цэгүүдийг харуулах"
            show_markers = st.checkbox(label, value=True)
            label = "线条样式" if lang == 'zh' else "Шугамын хэлбэр"
            line_shape = st.selectbox(label, ["linear", "spline"], key="line_shape")
            
            btn = "生成折线图" if lang == 'zh' else "Шугаман график үүсгэх"
            if st.button(btn):
                # 应用值标签（对X轴应用）
                df_plot = apply_value_labels(df, [x_col])
                
                fig = go.Figure()
                for y_col in y_cols:
                    fig.add_trace(go.Scatter(
                        x=df_plot[x_col],
                        y=df_plot[y_col],
                        mode='lines+markers' if show_markers else 'lines',
                        name=y_col,
                        line_shape=line_shape
                    ))
                fig.update_layout(
                    title="折线图",
                    xaxis_title=x_col,
                    yaxis_title="数值",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # AI智能分析
                st.markdown("---")
                st.markdown("### 🤖 AI 智能分析")
                
                with st.spinner("AI正在分析图表..."):
                    try:
                        # 为每条线生成趋势摘要
                        trends_info = []
                        for y_col in y_cols:
                            y_data = pd.to_numeric(df[y_col], errors='coerce').dropna()
                            if len(y_data) == 0:
                                continue
                            
                            start_val = float(y_data.iloc[0])
                            end_val = float(y_data.iloc[-1])
                            mean_val = float(y_data.mean())
                            max_val = float(y_data.max())
                            min_val = float(y_data.min())
                            
                            if end_val > start_val * 1.1:
                                trend = "上升"
                            elif end_val < start_val * 0.9:
                                trend = "下降"
                            else:
                                trend = "波动"
                            
                            trends_info.append(f"- {y_col}：整体{trend}，从{start_val:.2f}到{end_val:.2f}，平均{mean_val:.2f}，范围[{min_val:.2f}, {max_val:.2f}]")
                        
                        if trends_info:
                            chart_data = {
                                'x_var': x_col,
                                'y_vars': ', '.join(y_cols),
                                'trends': '\n'.join(trends_info)
                            }
                            
                            ai_analysis = get_ai_chart_analysis(chart_data, "line")
                            
                            if ai_analysis:
                                st.info(ai_analysis)
                            else:
                                st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
                        else:
                            st.warning("⚠️ 所选变量不包含有效的数值数据。")
                    except Exception as e:
                        st.warning(f"⚠️ 无法生成AI分析：{str(e)}")
    
    # 散点图 (index 1)
    elif plot_index == 1:
        subheader = "🔵 散点图" if lang == 'zh' else "🔵 Цэгэн график"
        st.subheader(subheader)
        
        label = "X 轴变量" if lang == 'zh' else "X тэнхлэгийн хувьсагч"
        x_col = st.selectbox(label, df.columns, key="scatter_x")
        label = "Y 轴变量" if lang == 'zh' else "Y тэнхлэгийн хувьсагч"
        y_col = st.selectbox(label, df.columns, key="scatter_y")
        label = "颜色分组（可选）" if lang == 'zh' else "Өнгөний бүлэг (сонголттой)"
        color_col = st.selectbox(label, [None] + list(df.columns), key="scatter_color")
        label = "大小变量（可选）" if lang == 'zh' else "Хэмжээний хувьсагч (сонголттой)"
        size_col = st.selectbox(label, [None] + list(df.columns), key="scatter_size")
        
        label = "显示趋势线" if lang == 'zh' else "Чиг хандлагын шугам харуулах"
        show_trendline = st.checkbox(label, value=False)
        
        btn = "生成散点图" if lang == 'zh' else "Цэгэн график үүсгэх"
        if st.button(btn):
            # 应用值标签（仅对分类变量color应用）
            cols_to_label = []
            if color_col:
                cols_to_label.append(color_col)
            df_plot = apply_value_labels(df, cols_to_label)
            
            fig = px.scatter(
                df_plot,
                x=x_col,
                y=y_col,
                color=color_col,
                size=size_col,
                trendline='ols' if show_trendline else None,
                title="散点图"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if show_trendline:
                # 显示回归方程
                import numpy as np
                from scipy import stats
                try:
                    # 确保数据是数值类型
                    x_vals = pd.to_numeric(df[x_col], errors='coerce').dropna()
                    y_vals = pd.to_numeric(df[y_col], errors='coerce').dropna()
                    
                    # 确保x和y数据长度相同（取交集索引）
                    common_idx = x_vals.index.intersection(y_vals.index)
                    x_vals = x_vals.loc[common_idx]
                    y_vals = y_vals.loc[common_idx]
                    
                    if len(x_vals) < 2:
                        st.warning("⚠️ 数据点太少，无法计算趋势线。")
                    else:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                        st.info(f"📐 回归方程：y = {slope:.4f}x + {intercept:.4f}  |  R² = {r_value**2:.4f}  |  p = {p_value:.4f}")
                        
                        # AI智能分析
                        st.markdown("---")
                        st.markdown("### 🤖 AI 智能分析")
                        
                        with st.spinner("AI正在分析图表..."):
                            chart_data = {
                                'x': x_col,
                                'y': y_col,
                                'r': float(r_value),
                                'r2': float(r_value**2),
                                'p': float(p_value),
                                'slope': float(slope)
                            }
                            
                            ai_analysis = get_ai_chart_analysis(chart_data, "scatter_with_trend")
                            
                            if ai_analysis:
                                if p_value < 0.05:
                                    st.success(ai_analysis)
                                else:
                                    st.info(ai_analysis)
                            else:
                                st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
                except Exception as e:
                    st.warning(f"⚠️ 无法计算趋势线：{str(e)}")
            else:
                # 没有趋势线时的简单说明
                st.markdown("---")
                st.markdown("### 📝 图表说明")
                st.info(f"""
**散点图解读**：

此图展示了 `{x_col}` 和 `{y_col}` 之间的关系。

- 每个点代表一个样本
- 横坐标(X轴)：{x_col}
- 纵坐标(Y轴)：{y_col}

💡 **建议**：勾选"显示趋势线"可以查看两者的相关关系，并获得AI智能分析。
                """)
    
    # 柱状图 (index 2)
    elif plot_index == 2:
        subheader = "📊 柱状图" if lang == 'zh' else "📊 Багана график"
        st.subheader(subheader)
        
        label = "X 轴变量（分类）" if lang == 'zh' else "X тэнхлэгийн хувьсагч (ангилал)"
        x_col = st.selectbox(label, df.columns, key="bar_x")
        label = "Y 轴变量（数值）" if lang == 'zh' else "Y тэнхлэгийн хувьсагч (тоон)"
        y_col = st.selectbox(label, df.columns, key="bar_y")
        label = "颜色分组（可选）" if lang == 'zh' else "Өнгөний бүлэг (сонголттой)"
        color_col = st.selectbox(label, [None] + list(df.columns), key="bar_color")
        
        label = "聚合函数" if lang == 'zh' else "Нэгтгэх функц"
        agg_func = st.selectbox(label, ["mean", "sum", "count", "median"], key="bar_agg")
        
        btn = "生成柱状图" if lang == 'zh' else "Багана график үүсгэх"
        if st.button(btn):
            # 应用值标签
            cols_to_label = [x_col]
            if color_col:
                cols_to_label.append(color_col)
            df_plot = apply_value_labels(df, cols_to_label)
            
            fig = px.bar(
                df_plot,
                x=x_col,
                y=y_col,
                color=color_col,
                barmode='group',
                title=f"柱状图 ({agg_func})"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # AI智能分析
            st.markdown("---")
            st.markdown("### 🤖 AI 智能分析")
            
            with st.spinner("AI正在分析图表..."):
                try:
                    # 收集各组数据 - 使用标签后的数据
                    agg_name = {"mean": "平均值", "sum": "总和", "count": "数量", "median": "中位数"}
                    groups = df_plot[x_col].unique()
                    values_info = []
                    for group in groups:
                        # 使用标签后的分组来筛选数据
                        group_data = pd.to_numeric(df_plot[df_plot[x_col] == group][y_col], errors='coerce').dropna()
                        if len(group_data) == 0:
                            continue
                        
                        if agg_func == "mean":
                            val = float(group_data.mean())
                        elif agg_func == "sum":
                            val = float(group_data.sum())
                        elif agg_func == "count":
                            val = len(group_data)
                        else:
                            val = float(group_data.median())
                        values_info.append(f"- {group}：{val:.2f}")
                    
                    if values_info:
                        chart_data = {
                            'variable': y_col,
                            'group': x_col,
                            'values': '\n'.join(values_info)
                        }
                        
                        ai_analysis = get_ai_chart_analysis(chart_data, "bar")
                        
                        if ai_analysis:
                            st.success(ai_analysis)
                        else:
                            st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
                    else:
                        st.warning("⚠️ 所选变量不包含有效的数值数据。")
                except Exception as e:
                    st.warning(f"⚠️ 无法生成AI分析：{str(e)}")
    
    # 箱线图 (index 3)
    elif plot_index == 3:
        subheader = "📦 箱线图" if lang == 'zh' else "📦 Хайрцаг график"
        st.subheader(subheader)
        
        label = "数值变量（可多选）" if lang == 'zh' else "Тоон хувьсагч (олон сонголттой)"
        y_cols = st.multiselect(label, df.columns, key="box_y")
        label = "分组变量（可选）" if lang == 'zh' else "Бүлгийн хувьсагч (сонголттой)"
        x_col = st.selectbox(label, [None] + list(df.columns), key="box_x")
        
        btn = "生成箱线图" if lang == 'zh' else "Хайрцаг график үүсгэх"
        if y_cols and st.button(btn):
            # 应用值标签（仅对分组变量x应用）
            if x_col:
                df_plot = apply_value_labels(df, [x_col])
            else:
                df_plot = df
            
            if x_col:
                fig = go.Figure()
                for y_col in y_cols:
                    fig.add_trace(go.Box(
                        y=df_plot[y_col],
                        x=df_plot[x_col],
                        name=y_col
                    ))
            else:
                fig = go.Figure()
                for y_col in y_cols:
                    fig.add_trace(go.Box(
                        y=df_plot[y_col],
                        name=y_col
                    ))
            fig.update_layout(title="箱线图")
            st.plotly_chart(fig, use_container_width=True)
            
            # AI智能分析
            st.markdown("---")
            st.markdown("### 🤖 AI 智能分析")
            
            if x_col:
                # 分组箱线图 - 用AI分析
                with st.spinner("AI正在分析图表..."):
                    try:
                        # 收集各组统计数据 - 使用标签后的数据
                        groups = df_plot[x_col].unique()
                        stats_info = []
                        for group in groups:
                            for y_col in y_cols:
                                # 使用标签后的分组来筛选数据
                                group_data = pd.to_numeric(df_plot[df_plot[x_col] == group][y_col], errors='coerce').dropna()
                                if len(group_data) == 0:
                                    continue
                                stats_info.append(f"- {group}组的{y_col}：中位数={float(group_data.median()):.2f}，平均值={float(group_data.mean()):.2f}，范围=[{float(group_data.min()):.2f}, {float(group_data.max()):.2f}]")
                        
                        if stats_info:
                            chart_data = {
                                'variable': ', '.join(y_cols),
                                'group': x_col,
                                'stats': '\n'.join(stats_info)
                            }
                            
                            ai_analysis = get_ai_chart_analysis(chart_data, "boxplot")
                            
                            if ai_analysis:
                                st.success(ai_analysis)
                            else:
                                st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
                        else:
                            st.warning("⚠️ 所选变量不包含有效的数值数据。")
                    except Exception as e:
                        st.warning(f"⚠️ 无法生成AI分析：{str(e)}")
            else:
                # 单变量箱线图 - 简单说明
                st.info(f"""
**箱线图解读**：

此图展示了 `{', '.join(y_cols)}` 的分布情况。

**如何看懂？**
- **箱体**：包含50%的数据
- **中间线**：中位数
- **须**：数据范围
- **圆点**：异常值

💡 **提示**：选择"分组变量"可以对比不同组的分布差异，并获得AI智能分析。
                """)
    
    # 饼图 (index 4)
    elif plot_index == 4:
        subheader = "🥧 饼图" if lang == 'zh' else "🥧 Дугуй диаграмм"
        st.subheader(subheader)
        
        label = "标签变量" if lang == 'zh' else "Тэмдэглэгээний хувьсагч"
        names_col = st.selectbox(label, df.columns, key="pie_names")
        label = "数值变量" if lang == 'zh' else "Тоон хувьсагч"
        values_col = st.selectbox(label, df.columns, key="pie_values")
        
        label = "显示百分比" if lang == 'zh' else "Хувь харуулах"
        show_percent = st.checkbox(label, value=True)
        
        btn = "生成饼图" if lang == 'zh' else "Дугуй диаграмм үүсгэх"
        if st.button(btn):
            # 应用值标签
            df_plot = apply_value_labels(df, [names_col])
            
            fig = px.pie(
                df_plot,
                names=names_col,
                values=values_col,
                title="饼图"
            )
            if show_percent:
                fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            # AI智能分析
            st.markdown("---")
            st.markdown("### 🤖 AI 智能分析")
            
            with st.spinner("AI正在分析图表..."):
                try:
                    # 计算各部分占比 - 使用标签后的数据
                    # 确保数值列是数字类型
                    numeric_values = pd.to_numeric(df_plot[values_col], errors='coerce')
                    total = numeric_values.sum()
                    
                    proportions_info = []
                    for name in df_plot[names_col].unique():
                        value = numeric_values[df_plot[names_col] == name].sum()
                        percent = (float(value) / float(total) * 100) if total > 0 else 0
                        proportions_info.append(f"- {name}：{percent:.1f}%")
                    
                    chart_data = {
                        'variable': names_col,
                        'proportions': '\n'.join(proportions_info)
                    }
                    
                    ai_analysis = get_ai_chart_analysis(chart_data, "pie")
                    
                    if ai_analysis:
                        st.info(ai_analysis)
                    else:
                        st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
                except Exception as e:
                    st.warning(f"⚠️ 无法生成AI分析：{str(e)}")
    
    # 直方图 (index 5)
    elif plot_index == 5:
        subheader = "📊 直方图" if lang == 'zh' else "📊 Гистограмм"
        st.subheader(subheader)
        
        label = "变量" if lang == 'zh' else "Хувьсагч"
        col = st.selectbox(label, df.columns, key="hist_col")
        label = "分组数" if lang == 'zh' else "Бүлгийн тоо"
        bins = st.slider(label, 5, 100, 30)
        
        btn = "生成直方图" if lang == 'zh' else "Гистограмм үүсгэх"
        if st.button(btn):
            fig = px.histogram(
                df,
                x=col,
                nbins=bins,
                title=f"{col} 的分布"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # AI智能分析
            st.markdown("---")
            st.markdown("### 🤖 AI 智能分析")
            
            with st.spinner("AI正在分析图表..."):
                try:
                    numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                    chart_data = {
                        'variable': col,
                        'mean': float(numeric_data.mean()),
                        'std': float(numeric_data.std()),
                        'min': float(numeric_data.min()),
                        'max': float(numeric_data.max())
                    }
                    
                    ai_analysis = get_ai_chart_analysis(chart_data, "histogram")
                    
                    if ai_analysis:
                        st.info(ai_analysis)
                    else:
                        st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
                except Exception as e:
                    st.warning(f"⚠️ 无法生成AI分析：{str(e)}")
    
    # 3D散点图 (index 6)
    elif plot_index == 6:
        subheader = "🌐 3D 散点图" if lang == 'zh' else "🌐 3D цэгэн график"
        st.subheader(subheader)
        
        label = "X 轴变量" if lang == 'zh' else "X тэнхлэгийн хувьсагч"
        x_col = st.selectbox(label, df.columns, key="3d_x")
        label = "Y 轴变量" if lang == 'zh' else "Y тэнхлэгийн хувьсагч"
        y_col = st.selectbox(label, df.columns, key="3d_y")
        label = "Z 轴变量" if lang == 'zh' else "Z тэнхлэгийн хувьсагч"
        z_col = st.selectbox(label, df.columns, key="3d_z")
        label = "颜色变量（可选）" if lang == 'zh' else "Өнгөний хувьсагч (сонголттой)"
        color_col = st.selectbox(label, [None] + list(df.columns), key="3d_color")
        
        btn = "生成 3D 散点图" if lang == 'zh' else "3D цэгэн график үүсгэх"
        if st.button(btn):
            # 应用值标签（仅对颜色分组变量应用）
            cols_to_label = []
            if color_col:
                cols_to_label.append(color_col)
            df_plot = apply_value_labels(df, cols_to_label)
            
            fig = px.scatter_3d(
                df_plot,
                x=x_col,
                y=y_col,
                z=z_col,
                color=color_col,
                title="3D 散点图"
            )
            st.plotly_chart(fig, use_container_width=True)

