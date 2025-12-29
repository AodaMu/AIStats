"""统计视图模块：描述统计/t检验/方差分析/相关回归/信度/中介效应"""
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import f_oneway, levene
import statsmodels.api as sm
from openai import OpenAI
from src.lib.i18n import get_lang

def get_ai_analysis(result_data, analysis_type):
    """调用AI分析统计结果"""
    if not st.session_state.ai_config.get('enabled') or not st.session_state.ai_config.get('api_key'):
        return None
    
    try:
        client = OpenAI(
            api_key=st.session_state.ai_config['api_key'],
            base_url=st.session_state.ai_config['base_url']
        )
        
        # 构建提示词
        if analysis_type == "t_test":
            prompt = f"""
请用简单易懂的语言分析这个独立样本t检验的结果：

- 分组变量：{result_data['group_var']}
- 数据变量：{result_data['data_var']}
- {result_data['group1']}组平均值：{result_data['mean1']:.2f}
- {result_data['group2']}组平均值：{result_data['mean2']:.2f}
- t值：{result_data['t']:.4f}
- p值：{result_data['p']:.4f}

🔴 必须遵守的格式：
1. 先说明统计依据（t值、p值）
2. 再给出结论（是否有显著差异）
3. 最后明确说明两者的关系

格式："根据独立样本t检验，t={result_data['t']:.2f}, p={result_data['p']:.3f}，所以...。**因此，{result_data['group_var']}与{result_data['data_var']}有/无显著关系。**"

要求：语言口语化，小白也能看懂。必须有明确的关系判断。
"""
        elif analysis_type == "correlation":
            prompt = f"""
请用简单易懂的语言分析这个相关分析的结果：

变量对及其相关系数：
{result_data['pairs']}

🔴 必须遵守的格式：
1. 每对变量先说明统计依据（r值、p值）
2. 说明相关程度和方向（强/中/弱，正/负）
3. 最后明确说明是否有显著相关关系

格式："基于Pearson相关分析，X与Y的r=0.XX, p=0.XXX，为XX相关。**因此，X与Y存在/不存在显著相关关系。**"

要求：语言口语化，小白也能看懂。每对变量必须有明确的关系判断。
"""
        elif analysis_type == "anova":
            prompt = f"""
请用简单易懂的语言分析这个方差分析的结果：

- 因变量：{result_data['dependent']}
- 分组变量：{result_data['factor']}
- 组数：{result_data['n_groups']}
- F值：{result_data['f']:.4f}
- p值：{result_data['p']:.4f}

🔴 必须遵守的格式：
1. 先说明统计依据（F值、p值）
2. 说明组间差异情况
3. 最后明确说明是否有显著影响

格式："根据单因素方差分析，F={result_data['f']:.2f}, p={result_data['p']:.3f}，各组存在显著差异。**因此，{result_data['factor']}对{result_data['dependent']}有/无显著影响。**"

要求：语言口语化，小白能懂。必须有明确的影响判断。
"""
        elif analysis_type == "regression":
            prompt = f"""
请用简单易懂的语言分析这个回归分析的结果：

- 自变量：{result_data['predictors']}
- 因变量：{result_data['outcome']}
- R²：{result_data['r2']:.4f}
- p值：{result_data['p']:.4f}

🔴 必须遵守的格式：
1. 先说明统计依据（R²、p值）
2. 说明解释力度（能解释多少变异）
3. 最后明确说明预测关系

格式："根据回归分析，R²={result_data['r2']:.2f}, p={result_data['p']:.3f}，能解释XX%的变异。**因此，{result_data['predictors']}对{result_data['outcome']}有/无显著预测作用。**"

要求：语言口语化，小白能懂。必须有明确的关系。
"""
        elif analysis_type == "reliability":
            prompt = f"""
请用简单易懂的语言分析这个信度分析的结果：

- 题目数：{result_data['n_items']}
- Cronbach's Alpha：{result_data['alpha']:.4f}

🔴 必须遵守的格式：
先说明统计结果，再给出评价。
格式："根据信度分析，Cronbach's Alpha={result_data['alpha']:.2f}，所以..."

要求：语言口语化，小白能懂。
"""
        elif analysis_type == "descriptive":
            prompt = f"""
请用简单易懂的语言分析这些描述统计结果：

变量统计：
{result_data['stats']}

🔴 必须遵守的格式：
1. 直接说明统计结果（频次、占比或均值等）
2. 给出数据分布的明确结论

⚠️ 重要规则：
- 描述统计只能说明单个变量的分布特征
- **不要**说"需要进一步分析"
- **不要**推测变量之间的关系
- 只描述当前看到的数据事实

示例格式：
"根据频次统计，7年级7人（35%），8年级7人（35%），9年级6人（30%）。**各年级人数分布较为均匀，7、8年级人数相同。**"

要求：
- 语言口语化，小白能懂
- 只陈述数据事实和分布特征
- 不要推测因果关系或建议做其他分析
"""
        elif analysis_type == "one_sample_t":
            prompt = f"""
请用简单易懂的语言分析这个单样本t检验的结果：

- 变量：{result_data['variable']}
- 样本均值：{result_data['mean']:.2f}
- 检验值：{result_data['test_value']}
- t值：{result_data['t']:.4f}
- p值：{result_data['p']:.4f}

🔴 必须遵守的格式：
1. 先说明统计依据（t值、p值）
2. 说明是否显著不同于检验值
3. 最后给出明确结论

格式："根据单样本t检验，t={result_data['t']:.2f}, p={result_data['p']:.3f}，样本均值显著不同于检验值。**因此，{result_data['variable']}与预期值{result_data['test_value']}有/无显著差异。**"

要求：语言口语化，小白能懂。必须有明确的差异判断。
"""
        elif analysis_type == "paired_t":
            prompt = f"""
请用简单易懂的语言分析这个配对样本t检验的结果：

- 第一次测量：{result_data['var1']}（平均值：{result_data['mean1']:.2f}）
- 第二次测量：{result_data['var2']}（平均值：{result_data['mean2']:.2f}）
- 平均差值：{result_data['mean_diff']:.2f}
- t值：{result_data['t']:.4f}
- p值：{result_data['p']:.4f}

🔴 必须遵守的格式：
1. 先说明统计依据（t值、p值）
2. 说明前后是否有显著变化
3. 最后给出明确结论

格式："根据配对样本t检验，t={result_data['t']:.2f}, p={result_data['p']:.3f}，前后测量有显著差异。**因此，{result_data['var1']}与{result_data['var2']}之间存在/不存在显著变化。**"

要求：语言口语化，小白能懂。必须有明确的变化判断。
"""
        elif analysis_type == "mediation":
            prompt = f"""
请用简单易懂的语言分析这个中介效应分析的结果：

- 自变量X：{result_data['x_var']}
- 中介变量M：{result_data['m_var']}
- 因变量Y：{result_data['y_var']}
- 路径a（X→M）：{result_data['a']:.4f}（p={result_data['p_a']:.4f}）
- 路径b（M→Y）：{result_data['b']:.4f}（p={result_data['p_b']:.4f}）
- 总效应c：{result_data['c']:.4f}
- 直接效应c'：{result_data['c_prime']:.4f}
- 间接效应（中介效应）：{result_data['indirect']:.4f}
- 中介比例：{result_data['mediation_ratio']:.1f}%

🔴 必须遵守的格式：
1. 先说明统计依据（路径a、b的p值和中介比例）
2. 说明中介效应是否显著
3. 最后给出明确的中介关系结论

格式："根据中介效应分析，路径a(p={result_data['p_a']:.3f})和路径b(p={result_data['p_b']:.3f})均显著，中介比例={result_data['mediation_ratio']:.1f}%。**因此，{result_data['m_var']}在{result_data['x_var']}对{result_data['y_var']}的影响中起到/不起到显著中介作用。**"

要求：语言口语化，小白能懂。必须有明确的中介作用判断。
"""
        else:
            return None
        
        response = client.chat.completions.create(
            model=st.session_state.ai_config['model'],
            messages=[
                {"role": "system", "content": """你是一个统计分析专家，擅长用简单的语言解释复杂的统计结果。

🌍 **【重要】双语输出要求**：
你必须使用**汉语（中文）**和**西里尔蒙古语（Кирилл монгол хэл）**双语输出所有分析结果。

**输出格式**：
🇨🇳 [中文内容]
🇲🇳 [Кирилл монгол хэлээр илэрхийлсэн агуулга]

**统计术语对照**：
平均值=Дундаж утга, 标准差=Стандарт хазайлт, 显著性=Ач холбогдол, 相关性=Хамаарал, 差异=Ялгаа, 结论=Дүгнэлт"""},
                {"role": "user", "content": prompt + "\n\n🌍 请务必使用双语输出（中文+西里尔蒙文）！"}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"AI分析失败：{str(e)}")
        return None

def render_stat_view():
    lang = get_lang()
    
    # 标题行和快捷按钮
    col1, col2, col3 = st.columns([2.0, 2.2, 0.4])
    with col1:
        title = "📊 统计视图" if lang == 'zh' else "📊 Статистик харах"
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
    
    # 选择统计方法
    if lang == 'zh':
        stat_methods = [
            "📊 描述统计",
            "📊 分组描述统计",
            "🔬 单样本 t 检验",
            "🔬 配对样本 t 检验",
            "🔬 独立样本 t 检验",
            "📈 单因素方差分析",
            "🔗 Pearson 相关分析",
            "📉 一元线性回归",
            "📉 多元线性回归",
            "✅ Cronbach's Alpha 信度",
            "🔄 简单中介效应分析"
        ]
        label = "选择统计方法"
    else:
        stat_methods = [
            "📊 Тайлбарлах статистик",
            "📊 Бүлгээр тайлбарлах статистик",
            "🔬 Нэг түүврийн t шалгалт",
            "🔬 Хослосон түүврийн t шалгалт",
            "🔬 Бие даасан түүврийн t шалгалт",
            "📈 Нэг хүчин зүйлийн ANOVA",
            "🔗 Pearson корреляцийн шинжилгээ",
            "📉 Нэг хувьсагчтай шугаман регресс",
            "📉 Олон хувьсагчтай шугаман регресс",
            "✅ Cronbach's Alpha найдвартай байдал",
            "🔄 Энгийн зуучлах нөлөөний шинжилгээ"
        ]
        label = "Статистикийн арга сонгох"
    
    stat_type = st.selectbox(label, stat_methods)
    stat_index = stat_methods.index(stat_type) if stat_type in stat_methods else 0
    
    st.markdown("---")
    
    # 描述统计 (index 0)
    if stat_index == 0:
        subheader = "📋 描述统计" if lang == 'zh' else "📋 Тайлбарлах статистик"
        st.subheader(subheader)
        
        label = "选择变量" if lang == 'zh' else "Хувьсагч сонгох"
        vars = st.multiselect(label, df.columns, key="desc_vars")
        
        btn_text = "计算描述统计" if lang == 'zh' else "Тайлбарлах статистик тооцоолох"
        if vars and st.button(btn_text):
            # 分离数值型和非数值型变量
            numeric_vars = df[vars].select_dtypes(include=['int64', 'float64']).columns.tolist()
            non_numeric_vars = [v for v in vars if v not in numeric_vars]
            
            # 检测包含非数值内容的"数值型"列
            problematic_vars = []
            for var in numeric_vars:
                try:
                    test_convert = pd.to_numeric(df[var], errors='raise')
                except (ValueError, TypeError):
                    problematic_vars.append(var)
            
            if problematic_vars:
                warn_msg = f"⚠️ 以下变量包含非数值内容，将被转换或忽略：{', '.join(problematic_vars)}" if lang == 'zh' else f"⚠️ Дараах хувьсагчд тоон бус агуулга агуулж байна, хөрвүүлэх эсвэл алгасна：{', '.join(problematic_vars)}"
                st.warning(warn_msg)
            
            if numeric_vars:
                # 数值型变量的统计 - 先转换为数值类型以处理混合类型
                numeric_df = df[numeric_vars].apply(pd.to_numeric, errors='coerce')
                result = numeric_df.describe().T
                result['count_missing'] = numeric_df.isnull().sum()
                result['skewness'] = numeric_df.skew()
                result['kurtosis'] = numeric_df.kurt()
                
                title = "#### 📊 数值型变量" if lang == 'zh' else "#### 📊 Тоон хувьсагч"
                st.markdown(title)
                st.dataframe(result, use_container_width=True)
                
                # 为数值型变量添加频次与占比（如果唯一值较少）
                from src.lib.variable_labels import get_value_labels
                st.markdown("---")
                title = "#### 📊 数值型变量 - 频次与占比" if lang == 'zh' else "#### 📊 Тоон хувьсагч - Давтамж ба хувь"
                st.markdown(title)
                
                for var in numeric_vars:
                    value_labels = get_value_labels(var)
                    # 转换为数值类型以避免字符串错误
                    var_data = pd.to_numeric(df[var], errors='coerce')
                    unique_count = var_data.nunique()
                    
                    # 只为唯一值≤20的变量显示频次占比
                    if unique_count <= 20:
                        st.markdown(f"**{var}**")
                        
                        # 获取频次和占比
                        value_counts = var_data.value_counts().sort_index()
                        percentages = (value_counts / var_data.count() * 100).round(2)
                        
                        # 创建带占比和标签的数据框
                        categories = []
                        for val in value_counts.index:
                            if value_labels and val in value_labels:
                                categories.append(f"{val} ({value_labels[val]})")
                            else:
                                categories.append(str(val))
                        
                        freq_df = pd.DataFrame({
                            '值': categories,
                            '频次': value_counts.values,
                            '占比(%)': [f"{p:.2f}%" for p in percentages.values]
                        })
                        
                        st.dataframe(freq_df, use_container_width=True, hide_index=True)
                        st.markdown("---")
            
            if non_numeric_vars:
                # 非数值型变量的统计（包括多选题）
                st.markdown("#### 📝 分类/文本变量")
                for var in non_numeric_vars:
                    st.markdown(f"**{var}**")
                    
                    # 检测是否为多选题
                    sample = df[var].dropna().head(20).astype(str)
                    is_multiple_choice = sample.str.contains(';', regex=False).any()
                    
                    if is_multiple_choice:
                        st.info("✅ 检测到多选题格式（分号分隔），建议使用AI视图进行详细分析")
                    
                    # 显示基本统计
                    col1, col2, col3 = st.columns(3)
                    col1.metric("样本量", df[var].count())
                    col2.metric("唯一值", df[var].nunique())
                    col3.metric("缺失值", df[var].isnull().sum())
                    
                    # 显示前5个最常见的值（添加占比）
                    if not is_multiple_choice:
                        st.write("最常见的值：")
                        value_counts = df[var].value_counts().head(5)
                        percentages = (value_counts / df[var].count() * 100).round(2)
                        
                        # 创建带占比的数据框
                        freq_df = pd.DataFrame({
                            '值': value_counts.index.astype(str),
                            '频次': value_counts.values,
                            '占比(%)': [f"{p:.2f}%" for p in percentages.values]
                        })
                        
                        st.dataframe(freq_df, use_container_width=True, hide_index=True)
                    st.markdown("---")
            
            if not numeric_vars and not non_numeric_vars:
                st.warning("⚠️ 未选择任何变量")
            st.session_state.stat_result = f"描述统计结果：{len(vars)} 个变量"
            
            # AI智能分析（仅针对数值型变量）
            if numeric_vars:
                st.markdown("---")
                st.markdown("### 🤖 AI 智能分析")
                
                with st.spinner("AI正在分析结果..."):
                    try:
                        # 生成统计摘要文本（仅数值型变量）
                        stats_text = []
                        for var in numeric_vars:
                            # 使用已转换的数值数据
                            numeric_data = numeric_df[var].dropna()
                            if len(numeric_data) == 0:
                                continue
                            mean = float(numeric_data.mean())
                            std = float(numeric_data.std())
                            min_val = float(numeric_data.min())
                            max_val = float(numeric_data.max())
                            stats_text.append(f"- {var}：平均值={mean:.2f}，标准差={std:.2f}，范围=[{min_val:.2f}, {max_val:.2f}]")
                    
                        if stats_text:
                            result_data = {
                                'stats': '\n'.join(stats_text)
                            }
                            
                            ai_analysis = get_ai_analysis(result_data, "descriptive")
                            
                            if ai_analysis:
                                st.info(ai_analysis)
                            else:
                                st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
                        else:
                            st.warning("⚠️ 所选变量不包含有效的数值数据。")
                    except Exception as e:
                        st.warning(f"⚠️ 无法生成AI分析：{str(e)}")
            
            # 为非数值型变量提供提示
            if non_numeric_vars:
                st.info("💡 **提示**：检测到分类/文本变量。如需对多选题进行详细分析，请前往 **🤖 AI 辅助分析** 视图。")
    
    # 分组描述统计 (index 1)
    elif stat_index == 1:
        subheader = "📊 分组描述统计" if lang == 'zh' else "📊 Бүлгээр тайлбарлах статистик"
        st.subheader(subheader)
        
        # 选择分组变量
        label = "选择分组变量" if lang == 'zh' else "Бүлгийн хувьсагч сонгох"
        help_text = "按此变量分组计算统计量（如：年级、性别、学校等）" if lang == 'zh' else "Энэ хувьсагчаар бүлэглэн статистик тооцоолох (жишээ: анги, хүйс, сургууль)"
        group_var = st.selectbox(label, df.columns, key="group_desc_var", help=help_text)
        
        # 选择要分析的变量
        label = "选择要分析的变量" if lang == 'zh' else "Шинжлэх хувьсагч сонгох"
        help_text = "可以选择多个变量进行分组统计" if lang == 'zh' else "Олон хувьсагч сонгож бүлгийн статистик хийж болно"
        vars = st.multiselect(label, df.columns, key="group_desc_vars", help=help_text)
        
        # 高级选项：是否计算维度得分
        with st.expander("🔧 高级选项：维度得分计算" if lang == 'zh' else "🔧 Нэмэлт сонголт: Хэмжээсийн оноо"):
            calc_dimension = st.checkbox(
                "计算维度得分（将选中的变量平均后再统计）" if lang == 'zh' else "Хэмжээсийн оноо тооцоолох (сонгосон хувьсагчдын дунджийг авна)",
                value=False,
                key="calc_dimension",
                help="勾选后，会先计算每个样本在所选变量上的平均分，然后按组统计" if lang == 'zh' else "Сонговол эхлээд сонгосон хувьсагчдын дунджийг тооцоолж, дараа нь бүлгээр статистик хийнэ"
            )
        
        btn_text = "计算分组统计" if lang == 'zh' else "Бүлгийн статистик тооцоолох"
        if vars and st.button(btn_text):
            try:
                # 获取分组
                groups = sorted(df[group_var].dropna().unique())
                
                if len(groups) < 2:
                    warning_text = "⚠️ 分组变量至少需要2个不同的值" if lang == 'zh' else "⚠️ Бүлгийн хувьсагч хамгийн багадаа 2 өөр утгатай байх ёстой"
                    st.warning(warning_text)
                else:
                    # 准备结果数据
                    results = []
                    
                    for group in groups:
                        group_data = df[df[group_var] == group]
                        row = {group_var: str(group), '样本量' if lang == 'zh' else 'Түүврийн тоо': len(group_data)}
                        
                        if calc_dimension:
                            # 计算维度得分模式：先计算每个样本的平均分
                            dimension_scores = group_data[vars].apply(pd.to_numeric, errors='coerce').mean(axis=1)
                            
                            row['均值' if lang == 'zh' else 'Дундаж'] = round(float(dimension_scores.mean()), 2)
                            row['标准差' if lang == 'zh' else 'Стандарт хазайлт'] = round(float(dimension_scores.std()), 2)
                            row['最小值' if lang == 'zh' else 'Хамгийн бага'] = round(float(dimension_scores.min()), 2)
                            row['最大值' if lang == 'zh' else 'Хамгийн их'] = round(float(dimension_scores.max()), 2)
                        else:
                            # 普通模式：分别统计每个变量
                            for var in vars:
                                var_data = pd.to_numeric(group_data[var], errors='coerce').dropna()
                                
                                if len(var_data) > 0:
                                    row[f'{var}_均值' if lang == 'zh' else f'{var}_Дундаж'] = round(float(var_data.mean()), 2)
                                    row[f'{var}_标准差' if lang == 'zh' else f'{var}_Стандарт'] = round(float(var_data.std()), 2)
                                else:
                                    row[f'{var}_均值' if lang == 'zh' else f'{var}_Дундаж'] = np.nan
                                    row[f'{var}_标准差' if lang == 'zh' else f'{var}_Стандарт'] = np.nan
                        
                        results.append(row)
                    
                    # 创建结果DataFrame
                    result_df = pd.DataFrame(results)
                    
                    # 显示结果
                    if calc_dimension:
                        title = f"#### 📊 维度得分分组统计（变量：{', '.join(vars)}）" if lang == 'zh' else f"#### 📊 Хэмжээсийн оноо бүлгийн статистик（Хувьсагч：{', '.join(vars)}）"
                    else:
                        title = "#### 📊 分组描述统计结果" if lang == 'zh' else "#### 📊 Бүлгийн тайлбарлах статистикийн үр дүн"
                    
                    st.markdown(title)
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                    
                    # 保存结果
                    st.session_state.stat_result = f"分组描述统计：按 {group_var} 分组，{len(vars)} 个变量"
                    
                    # 提供下载选项
                    st.markdown("---")
                    col_download1, col_download2 = st.columns(2)
                    
                    with col_download1:
                        # 导出为CSV
                        csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                        download_label = "📥 下载 CSV" if lang == 'zh' else "📥 CSV татах"
                        st.download_button(
                            label=download_label,
                            data=csv,
                            file_name=f"分组统计_{group_var}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col_download2:
                        # 导出为Excel
                        import io
                        buffer = io.BytesIO()
                        result_df.to_excel(buffer, index=False, engine='openpyxl')
                        download_label = "📥 下载 Excel" if lang == 'zh' else "📥 Excel татах"
                        st.download_button(
                            label=download_label,
                            data=buffer.getvalue(),
                            file_name=f"分组统计_{group_var}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    # AI智能分析
                    st.markdown("---")
                    st.markdown("### 🤖 AI 智能分析")
                    
                    with st.spinner("AI正在分析结果..."):
                        try:
                            # 生成统计摘要文本
                            stats_text = []
                            for idx, row in result_df.iterrows():
                                group_name = row[group_var]
                                sample_size = row['样本量' if lang == 'zh' else 'Түүврийн тоо']
                                
                                if calc_dimension:
                                    mean_val = row['均值' if lang == 'zh' else 'Дундаж']
                                    std_val = row['标准差' if lang == 'zh' else 'Стандарт хазайлт']
                                    stats_text.append(f"- {group_name}组：样本量={sample_size}，均值={mean_val:.2f}，标准差={std_val:.2f}")
                                else:
                                    # 普通模式：列出每个变量的统计
                                    var_stats = []
                                    for var in vars:
                                        mean_col = f'{var}_均值' if lang == 'zh' else f'{var}_Дундаж'
                                        std_col = f'{var}_标准差' if lang == 'zh' else f'{var}_Стандарт'
                                        if mean_col in row and not pd.isna(row[mean_col]):
                                            var_stats.append(f"{var}(均值={row[mean_col]:.2f}, 标准差={row[std_col]:.2f})")
                                    if var_stats:
                                        stats_text.append(f"- {group_name}组：样本量={sample_size}，{', '.join(var_stats)}")
                            
                            if stats_text:
                                result_data = {
                                    'stats': '\n'.join(stats_text)
                                }
                                
                                ai_analysis = get_ai_analysis(result_data, "descriptive")
                                
                                if ai_analysis:
                                    st.info(ai_analysis)
                                else:
                                    st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
                        except Exception as e:
                            st.warning(f"⚠️ 无法生成AI分析：{str(e)}")
                    
                    # 使用说明
                    st.markdown("---")
                    st.info("💡 提示：如果需要生成多个维度的分组统计表，可以多次运行此分析，每次选择不同的变量组合。" if lang == 'zh' else "💡 Зөвлөмж: Олон хэмжээсийн бүлгийн статистик үүсгэх шаардлагатай бол энэ шинжилгээг олон удаа ажиллуулж, өөр өөр хувьсагчдын хослолыг сонгоно уу.")
                    
            except Exception as e:
                error_text = f"❌ 计算失败：{str(e)}" if lang == 'zh' else f"❌ Тооцоолох амжилтгүй：{str(e)}"
                st.error(error_text)
    
    # 单样本 t 检验 (index 2)
    elif stat_index == 2:
        subheader = "🔬 单样本 t 检验" if lang == 'zh' else "🔬 Нэг түүврийн t шалгалт"
        st.subheader(subheader)
        
        label = "选择变量" if lang == 'zh' else "Хувьсагч сонгох"
        var = st.selectbox(label, df.columns, key="t1_var")
        label = "检验值 (μ₀)" if lang == 'zh' else "Шалгах утга (μ₀)"
        mu = st.number_input(label, value=0.0, key="t1_mu")
        
        btn = "执行检验" if lang == 'zh' else "Шалгалт гүйцэтгэх"
        if st.button(btn):
            try:
                # 转换为数值类型
                data = pd.to_numeric(df[var], errors='coerce').dropna()
                
                if len(data) < 2:
                    st.error("❌ 数据点太少，无法执行t检验（至少需要2个有效数据点）")
                else:
                    t_stat, p_value = stats.ttest_1samp(data, mu)
                    
                    result_df = pd.DataFrame({
                        '变量': [var],
                        '样本量': [len(data)],
                        '均值': [float(data.mean())],
                        '标准差': [float(data.std())],
                        '检验值': [mu],
                        't 统计量': [float(t_stat)],
                        'p 值': [float(p_value)],
                        '显著性': ['***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns']
                    })
                    
                    st.dataframe(result_df, use_container_width=True)
                    st.session_state.stat_result = f"单样本 t 检验：{var} vs {mu}, p={p_value:.4f}"
                    
                    # AI智能分析
                    st.markdown("---")
                    st.markdown("### 🤖 AI 智能分析")
                    
                    with st.spinner("AI正在分析结果..."):
                        result_data = {
                            'variable': var,
                            'mean': float(data.mean()),
                            'test_value': mu,
                            't': float(t_stat),
                            'p': float(p_value)
                        }
                        
                        ai_analysis = get_ai_analysis(result_data, "one_sample_t")
                        
                        if ai_analysis:
                            if p_value < 0.05:
                                st.success(ai_analysis)
                            else:
                                st.info(ai_analysis)
                        else:
                            st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 执行检验时出错：{str(e)}")
    
    # 配对样本 t 检验 (index 3)
    elif stat_index == 3:
        subheader = "👥 配对样本 t 检验" if lang == 'zh' else "👥 Хослосон түүврийн t шалгалт"
        st.subheader(subheader)
        
        label1 = "变量 1" if lang == 'zh' else "Хувьсагч 1"
        var1 = st.selectbox(label1, df.columns, key="t2_var1")
        label2 = "变量 2" if lang == 'zh' else "Хувьсагч 2"
        var2 = st.selectbox(label2, df.columns, key="t2_var2")
        
        btn = "执行检验" if lang == 'zh' else "Шалгалт гүйцэтгэх"
        if st.button(btn):
            try:
                # 转换为数值类型
                data1 = pd.to_numeric(df[var1], errors='coerce').dropna()
                data2 = pd.to_numeric(df[var2], errors='coerce').dropna()
                
                if len(data1) < 2 or len(data2) < 2:
                    st.error("❌ 数据点太少，无法执行t检验（至少需要2个有效数据点）")
                else:
                    # 保证配对 - 使用共同的索引
                    common_idx = data1.index.intersection(data2.index)
                    data1_paired = data1.loc[common_idx]
                    data2_paired = data2.loc[common_idx]
                    
                    if len(data1_paired) < 2:
                        st.error("❌ 配对数据点太少，无法执行配对t检验（至少需要2对有效数据）")
                    else:
                        t_stat, p_value = stats.ttest_rel(data1_paired, data2_paired)
                        
                        result_df = pd.DataFrame({
                            '变量1': [var1],
                            '变量2': [var2],
                            '样本量': [len(data1_paired)],
                            '均值差': [float(data1_paired.mean() - data2_paired.mean())],
                            't 统计量': [float(t_stat)],
                            'p 值': [float(p_value)],
                            '显著性': ['***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns']
                        })
                        
                        st.dataframe(result_df, use_container_width=True)
                        st.session_state.stat_result = f"配对 t 检验：{var1} vs {var2}, p={p_value:.4f}"
                        
                        # AI智能分析
                        st.markdown("---")
                        st.markdown("### 🤖 AI 智能分析")
                        
                        with st.spinner("AI正在分析结果..."):
                            result_data = {
                                'var1': var1,
                                'var2': var2,
                                'mean1': float(data1_paired.mean()),
                                'mean2': float(data2_paired.mean()),
                                'mean_diff': float(data1_paired.mean() - data2_paired.mean()),
                                't': float(t_stat),
                                'p': float(p_value)
                            }
                            
                            ai_analysis = get_ai_analysis(result_data, "paired_t")
                            
                            if ai_analysis:
                                if p_value < 0.05:
                                    st.success(ai_analysis)
                                else:
                                    st.info(ai_analysis)
                            else:
                                st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 执行检验时出错：{str(e)}")
    
    # 独立样本 t 检验 (index 4)
    elif stat_index == 4:
        subheader = "🔀 独立样本 t 检验" if lang == 'zh' else "🔀 Бие даасан түүврийн t шалгалт"
        st.subheader(subheader)
        
        label = "数据变量" if lang == 'zh' else "Өгөгдлийн хувьсагч"
        data_var = st.selectbox(label, df.columns, key="t3_data")
        label = "分组变量" if lang == 'zh' else "Бүлгийн хувьсагч"
        group_var = st.selectbox(label, df.columns, key="t3_group")
        
        btn = "执行检验" if lang == 'zh' else "Шалгалт гүйцэтгэх"
        if st.button(btn):
            try:
                groups = df[group_var].unique()
                if len(groups) != 2:
                    st.error("❌ 分组变量必须恰好有 2 个水平")
                else:
                    # 转换为数值类型
                    group1 = pd.to_numeric(df[df[group_var] == groups[0]][data_var], errors='coerce').dropna()
                    group2 = pd.to_numeric(df[df[group_var] == groups[1]][data_var], errors='coerce').dropna()
                    
                    if len(group1) < 2 or len(group2) < 2:
                        st.error("❌ 每组至少需要2个有效数据点")
                    else:
                        t_stat, p_value = stats.ttest_ind(group1, group2)
                        
                        result_df = pd.DataFrame({
                            '分组变量': [group_var],
                            '组1': [groups[0]],
                            '组2': [groups[1]],
                            'n1': [len(group1)],
                            'n2': [len(group2)],
                            'M1': [float(group1.mean())],
                            'M2': [float(group2.mean())],
                            't 统计量': [float(t_stat)],
                            'p 值': [float(p_value)],
                            '显著性': ['***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns']
                        })
                        
                        st.dataframe(result_df, use_container_width=True)
                        st.session_state.stat_result = f"独立 t 检验：{data_var} by {group_var}, p={p_value:.4f}"
                        
                        # AI智能分析
                        st.markdown("---")
                        st.markdown("### 🤖 AI 智能分析")
                        
                        with st.spinner("AI正在分析结果..."):
                            result_data = {
                                'group_var': group_var,
                                'data_var': data_var,
                                'group1': str(groups[0]),
                                'group2': str(groups[1]),
                                'mean1': float(group1.mean()),
                                'mean2': float(group2.mean()),
                                't': float(t_stat),
                                'p': float(p_value)
                            }
                            
                            ai_analysis = get_ai_analysis(result_data, "t_test")
                            
                            if ai_analysis:
                                if p_value < 0.05:
                                    st.success(ai_analysis)
                                else:
                                    st.info(ai_analysis)
                            else:
                                # 如果AI分析失败，显示简单提示
                                st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 执行检验时出错：{str(e)}")
    
    # 单因素方差分析 (index 5)
    elif stat_index == 5:
        subheader = "📐 单因素方差分析 (ANOVA)" if lang == 'zh' else "📐 Нэг хүчин зүйлийн ANOVA"
        st.subheader(subheader)
        
        label = "因变量" if lang == 'zh' else "Хамааралтай хувьсагч"
        data_var = st.selectbox(label, df.columns, key="anova_data")
        label = "因素（分组变量）" if lang == 'zh' else "Хүчин зүйл (бүлгийн хувьсагч)"
        group_var = st.selectbox(label, df.columns, key="anova_group")
        
        btn = "执行分析" if lang == 'zh' else "Шинжилгээ гүйцэтгэх"
        if st.button(btn):
            try:
                groups = df[group_var].unique()
                # 转换为数值类型
                group_data = [pd.to_numeric(df[df[group_var] == g][data_var], errors='coerce').dropna() for g in groups]
                
                # 检查每组至少有数据
                valid_groups = [g for g in group_data if len(g) >= 1]
                if len(valid_groups) < 2:
                    st.error("❌ 至少需要2组有效数据才能进行方差分析")
                else:
                    f_stat, p_value = f_oneway(*valid_groups)
                    
                    result_df = pd.DataFrame({
                        '因变量': [data_var],
                        '因素': [group_var],
                        '组数': [len(valid_groups)],
                        'F 统计量': [float(f_stat)],
                        'p 值': [float(p_value)],
                        '显著性': ['***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns']
                    })
                    
                    st.dataframe(result_df, use_container_width=True)
                    
                    # 方差齐性检验
                    lev_stat, lev_p = levene(*valid_groups)
                    st.info(f"📊 Levene 方差齐性检验：F={lev_stat:.4f}, p={lev_p:.4f}")
                    
                    st.session_state.stat_result = f"单因素 ANOVA：{data_var} by {group_var}, F={f_stat:.4f}, p={p_value:.4f}"
                    
                    # AI智能分析
                    st.markdown("---")
                    st.markdown("### 🤖 AI 智能分析")
                    
                    with st.spinner("AI正在分析结果..."):
                        result_data = {
                            'dependent': data_var,
                            'factor': group_var,
                            'n_groups': len(valid_groups),
                            'f': float(f_stat),
                            'p': float(p_value)
                        }
                        
                        ai_analysis = get_ai_analysis(result_data, "anova")
                        
                        if ai_analysis:
                            if p_value < 0.05:
                                st.success(ai_analysis)
                            else:
                                st.info(ai_analysis)
                        else:
                            st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 执行分析时出错：{str(e)}")
    
    # Pearson 相关分析 (index 6)
    elif stat_index == 6:
        subheader = "🔗 Pearson 相关分析" if lang == 'zh' else "🔗 Pearson корреляцийн шинжилгээ"
        st.subheader(subheader)
        
        label = "选择变量（至少2个）" if lang == 'zh' else "Хувьсагч сонгох (хамгийн багадаа 2)"
        vars = st.multiselect(label, df.columns, key="corr_vars")
        
        btn = "计算相关" if lang == 'zh' else "Корреляци тооцоолох"
        if len(vars) >= 2 and st.button(btn):
            try:
                # 转换为数值类型
                numeric_df = df[vars].apply(pd.to_numeric, errors='coerce')
                numeric_df = numeric_df.dropna()
                
                if len(numeric_df) < 3:
                    st.error("❌ 有效数据点太少，无法进行相关分析（至少需要3个有效数据点）")
                else:
                    corr_matrix = numeric_df.corr()
                    
                    st.write("#### 相关系数矩阵")
                    st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm', vmin=-1, vmax=1), use_container_width=True)
                    
                    # 显著性检验
                    st.write("#### 显著性检验")
                    n = len(numeric_df)
                    p_matrix = pd.DataFrame(index=vars, columns=vars)
                    
                    for i, var1 in enumerate(vars):
                        for j, var2 in enumerate(vars):
                            if i != j:
                                r = float(corr_matrix.loc[var1, var2])
                                # 防止除零错误：当r接近±1时，1-r²接近0
                                if abs(r) >= 0.9999:
                                    # 完全相关或完全负相关，p值极小
                                    p_matrix.loc[var1, var2] = 0.0
                                else:
                                    t = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)
                                    p = 2 * (1 - stats.t.cdf(abs(t), n - 2))
                                    p_matrix.loc[var1, var2] = p
                            else:
                                p_matrix.loc[var1, var2] = 1.0
                    
                    st.dataframe(p_matrix.astype(float).style.format("{:.4f}"), use_container_width=True)
                    st.session_state.stat_result = f"Pearson 相关：{len(vars)} 个变量"
                    
                    # AI智能分析
                    st.markdown("---")
                    st.markdown("### 🤖 AI 智能分析")
                    
                    with st.spinner("AI正在分析结果..."):
                        # 准备所有变量对的数据
                        pairs_info = []
                        for i, var1 in enumerate(vars):
                            for j, var2 in enumerate(vars):
                                if i < j:  # 避免重复
                                    r = float(corr_matrix.loc[var1, var2])
                                    p = float(p_matrix.loc[var1, var2])
                                    pairs_info.append(f"- {var1} 与 {var2}：r={r:.3f}, p={p:.4f}")
                        
                        result_data = {
                            'pairs': '\n'.join(pairs_info)
                        }
                        
                        ai_analysis = get_ai_analysis(result_data, "correlation")
                        
                        if ai_analysis:
                            st.success(ai_analysis)
                        else:
                            st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 执行分析时出错：{str(e)}")
    
    # 一元线性回归 (index 7)
    elif stat_index == 7:
        subheader = "📈 一元线性回归" if lang == 'zh' else "📈 Нэг хувьсагчтай шугаман регресс"
        st.subheader(subheader)
        
        label = "自变量 (X)" if lang == 'zh' else "Бие даасан хувьсагч (X)"
        x_var = st.selectbox(label, df.columns, key="reg1_x")
        label = "因变量 (Y)" if lang == 'zh' else "Хамааралтай хувьсагч (Y)"
        y_var = st.selectbox(label, df.columns, key="reg1_y")
        
        btn = "执行回归" if lang == 'zh' else "Регресс гүйцэтгэх"
        if st.button(btn):
            try:
                # 转换为数值类型
                data = df[[x_var, y_var]].apply(pd.to_numeric, errors='coerce').dropna()
                
                if len(data) < 3:
                    st.error("❌ 有效数据点太少，无法进行回归分析（至少需要3个有效数据点）")
                else:
                    X = sm.add_constant(data[x_var])
                    y = data[y_var]
                    
                    model = sm.OLS(y, X).fit()
                    
                    st.write("#### 回归摘要")
                    st.text(model.summary())
                    
                    st.write("#### 回归方程")
                    st.latex(f"Y = {model.params[1]:.4f} \\times X + {model.params[0]:.4f}")
                    st.info(f"R² = {model.rsquared:.4f}, p = {model.f_pvalue:.4f}")
                    
                    st.session_state.stat_result = f"一元回归：{y_var} ~ {x_var}, R²={model.rsquared:.4f}"
                    
                    # AI智能分析
                    st.markdown("---")
                    st.markdown("### 🤖 AI 智能分析")
                    
                    with st.spinner("AI正在分析结果..."):
                        result_data = {
                            'predictors': x_var,
                            'outcome': y_var,
                            'r2': float(model.rsquared),
                            'p': float(model.f_pvalue)
                        }
                        
                        ai_analysis = get_ai_analysis(result_data, "regression")
                        
                        if ai_analysis:
                            if model.f_pvalue < 0.05:
                                st.success(ai_analysis)
                            else:
                                st.info(ai_analysis)
                        else:
                            st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 执行回归时出错：{str(e)}")
    
    # 多元线性回归 (index 8)
    elif stat_index == 8:
        subheader = "📊 多元线性回归" if lang == 'zh' else "📊 Олон хувьсагчтай шугаман регресс"
        st.subheader(subheader)
        
        label = "因变量 (Y)" if lang == 'zh' else "Хамааралтай хувьсагч (Y)"
        y_var = st.selectbox(label, df.columns, key="regm_y")
        label = "自变量 (X, 可多选)" if lang == 'zh' else "Бие даасан хувьсагч (X, олон сонголттай)"
        x_vars = st.multiselect(label, [c for c in df.columns if c != y_var], key="regm_x")
        
        btn = "执行回归" if lang == 'zh' else "Регресс гүйцэтгэх"
        if x_vars and st.button(btn):
            try:
                # 转换为数值类型
                data = df[[y_var] + x_vars].apply(pd.to_numeric, errors='coerce').dropna()
                
                if len(data) < len(x_vars) + 2:
                    st.error(f"❌ 有效数据点太少，无法进行回归分析（至少需要{len(x_vars) + 2}个有效数据点）")
                else:
                    X = sm.add_constant(data[x_vars])
                    y = data[y_var]
                    
                    model = sm.OLS(y, X).fit()
                    
                    st.write("#### 回归摘要")
                    st.text(model.summary())
                    
                    st.info(f"R² = {model.rsquared:.4f}, Adj R² = {model.rsquared_adj:.4f}, p = {model.f_pvalue:.4f}")
                    
                    st.session_state.stat_result = f"多元回归：{y_var} ~ {'+'.join(x_vars)}, R²={model.rsquared:.4f}"
                    
                    # AI智能分析
                    st.markdown("---")
                    st.markdown("### 🤖 AI 智能分析")
                    
                    with st.spinner("AI正在分析结果..."):
                        result_data = {
                            'predictors': '+'.join(x_vars),
                            'outcome': y_var,
                            'r2': float(model.rsquared),
                            'p': float(model.f_pvalue)
                        }
                        
                        ai_analysis = get_ai_analysis(result_data, "regression")
                        
                        if ai_analysis:
                            if model.f_pvalue < 0.05:
                                st.success(ai_analysis)
                            else:
                                st.info(ai_analysis)
                        else:
                            st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 执行回归时出错：{str(e)}")
    
    # Cronbach's Alpha 信度 (index 9)
    elif stat_index == 9:
        subheader = "🎯 Cronbach's Alpha 信度分析" if lang == 'zh' else "🎯 Cronbach's Alpha найдвартай байдлын шинжилгээ"
        st.subheader(subheader)
        
        label = "选择题目/量表项" if lang == 'zh' else "Асуулт/хэмжүүрийн зүйл сонгох"
        items = st.multiselect(label, df.columns, key="alpha_items")
        
        btn = "计算信度" if lang == 'zh' else "Найдвартай байдлыг тооцоолох"
        if len(items) >= 2 and st.button(btn):
            try:
                # 转换为数值类型
                data = df[items].apply(pd.to_numeric, errors='coerce').dropna()
                
                if len(data) < 2:
                    st.error("❌ 有效数据点太少，无法计算信度（至少需要2个有效数据点）")
                else:
                    n_items = len(items)
                    
                    # 计算 Cronbach's Alpha
                    item_vars = float(data.var(axis=0).sum())
                    total_var = float(data.sum(axis=1).var())
                    
                    if total_var == 0:
                        st.error("❌ 数据方差为0，无法计算信度")
                    else:
                        alpha = float((n_items / (n_items - 1)) * (1 - item_vars / total_var))
                        
                        result_df = pd.DataFrame({
                            '题目数': [n_items],
                            '样本量': [len(data)],
                            "Cronbach's Alpha": [alpha]
                        })
                        
                        st.dataframe(result_df, use_container_width=True)
                        
                        if alpha >= 0.9:
                            st.success("✅ 优秀信度 (α ≥ 0.9)")
                        elif alpha >= 0.8:
                            st.success("✅ 良好信度 (α ≥ 0.8)")
                        elif alpha >= 0.7:
                            st.info("ℹ️ 可接受信度 (α ≥ 0.7)")
                        else:
                            st.warning("⚠️ 信度偏低 (α < 0.7)")
                        
                        st.session_state.stat_result = f"Cronbach's Alpha = {alpha:.4f}"
                        
                        # AI智能分析
                        st.markdown("---")
                        st.markdown("### 🤖 AI 智能分析")
                        
                        with st.spinner("AI正在分析结果..."):
                            result_data = {
                                'n_items': n_items,
                                'alpha': alpha
                            }
                            
                            ai_analysis = get_ai_analysis(result_data, "reliability")
                            
                            if ai_analysis:
                                if alpha >= 0.7:
                                    st.success(ai_analysis)
                                else:
                                    st.warning(ai_analysis)
                            else:
                                st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 计算信度时出错：{str(e)}")
    
    # 简单中介效应 (index 10)
    elif stat_index == 10:
        subheader = "🔄 简单中介效应分析" if lang == 'zh' else "🔄 Энгийн зуучлах нөлөөний шинжилгээ"
        st.subheader(subheader)
        
        model_text = "模型：X → M → Y" if lang == 'zh' else "Загвар：X → M → Y"
        st.markdown(model_text)
        
        label = "自变量 (X)" if lang == 'zh' else "Бие даасан хувьсагч (X)"
        x_var = st.selectbox(label, df.columns, key="med_x")
        label = "中介变量 (M)" if lang == 'zh' else "Зуучлагч хувьсагч (M)"
        m_var = st.selectbox(label, df.columns, key="med_m")
        label = "因变量 (Y)" if lang == 'zh' else "Хамааралтай хувьсагч (Y)"
        y_var = st.selectbox(label, df.columns, key="med_y")
        
        btn = "执行中介分析" if lang == 'zh' else "Зуучлах шинжилгээ гүйцэтгэх"
        if st.button(btn):
            try:
                # 转换为数值类型
                data = df[[x_var, m_var, y_var]].apply(pd.to_numeric, errors='coerce').dropna()
                
                if len(data) < 4:
                    st.error("❌ 有效数据点太少，无法进行中介分析（至少需要4个有效数据点）")
                else:
                    # 路径 a: X → M
                    X_a = sm.add_constant(data[x_var])
                    model_a = sm.OLS(data[m_var], X_a).fit()
                    a = float(model_a.params[1])
                    
                    # 路径 b: M → Y (控制 X)
                    X_b = sm.add_constant(data[[x_var, m_var]])
                    model_b = sm.OLS(data[y_var], X_b).fit()
                    b = float(model_b.params[m_var])
                    c_prime = float(model_b.params[x_var])
                    
                    # 路径 c: X → Y (总效应)
                    X_c = sm.add_constant(data[x_var])
                    model_c = sm.OLS(data[y_var], X_c).fit()
                    c = float(model_c.params[1])
                    
                    # 中介效应
                    indirect = a * b
                    direct = c_prime
                    total = c
                    
                    result_df = pd.DataFrame({
                        '路径': ['a (X→M)', 'b (M→Y)', "c' (X→Y直接)", 'c (X→Y总)', '中介效应 (a×b)'],
                        '系数': [a, b, c_prime, c, indirect],
                        'p值': [float(model_a.pvalues[1]), float(model_b.pvalues[m_var]), float(model_b.pvalues[x_var]), float(model_c.pvalues[1]), np.nan]
                    })
                    
                    st.dataframe(result_df, use_container_width=True)
                    
                    st.info(f"""
                    📊 中介效应分析结果：
                    - 总效应 c = {c:.4f}
                    - 直接效应 c' = {c_prime:.4f}
                    - 间接效应 a×b = {indirect:.4f}
                    - 中介比例 = {(indirect/c*100 if c != 0 else 0):.2f}%
                    """)
                    
                    st.session_state.stat_result = f"中介效应：{x_var}→{m_var}→{y_var}, 间接效应={indirect:.4f}"
                    
                    # AI智能分析
                    st.markdown("---")
                    st.markdown("### 🤖 AI 智能分析")
                    
                    with st.spinner("AI正在分析结果..."):
                        result_data = {
                            'x_var': x_var,
                            'm_var': m_var,
                            'y_var': y_var,
                            'a': a,
                            'p_a': float(model_a.pvalues[1]),
                            'b': b,
                            'p_b': float(model_b.pvalues[m_var]),
                            'c': c,
                            'c_prime': c_prime,
                            'indirect': indirect,
                            'mediation_ratio': (indirect/c*100 if c != 0 else 0)
                        }
                        
                        ai_analysis = get_ai_analysis(result_data, "mediation")
                        
                        if ai_analysis:
                            # 判断中介效应是否显著
                            if model_a.pvalues[1] < 0.05 and model_b.pvalues[m_var] < 0.05:
                                st.success(ai_analysis)
                            else:
                                st.info(ai_analysis)
                        else:
                            st.info("💡 请在 **🤖 AI 辅助分析** 中配置AI后，可获得智能分析结果。")
            except Exception as e:
                st.error(f"❌ 执行中介分析时出错：{str(e)}")


