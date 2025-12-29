"""关于页面模块：系统介绍与项目信息"""
import streamlit as st
from src.lib.i18n import get_lang


def render_about_view():
    lang = get_lang()

    # 获取要显示的部分（默认显示全部）
    section = st.session_state.get('about_section', 'all')

    # 标题
    if section == 'tech':
        title = "💻 技术架构" if lang == 'zh' else "💻 Техникийн архитектур"
    elif section == 'overview':
        title = "🎯 项目介绍" if lang == 'zh' else "🎯 Төслийн танилцуулга"
    else:
        title = "ℹ️ 关于 AIStats" if lang == 'zh' else "ℹ️ AIStats-ийн тухай"

    st.title(title)

    if section == 'all':
        caption = "AI 驱动的在线统计分析平台" if lang == 'zh' else "Хиймэл оюун ухаанд суурилсан онлайн статистик шинжилгээний платформ"
        st.caption(caption)

    st.markdown("---")

    # ========== 项目概述部分 ==========
    if section == 'overview' or section == 'all':
        if lang == 'zh':
            st.markdown("## 📋 项目概述")
            st.markdown("""
**AIStats**（AI Statistical Package for the Social Sciences）是一个集成人工智能辅助能力的在线数据分析平台，旨在为研究人员、数据分析师和学生提供一个易用、强大且智能的统计分析工具。

本系统为**毕业设计作品**，论文题目：《基于人工智能的在线统计分析系统设计与实现》
            """)
        else:
            st.markdown("## 📋 Төслийн тойм")
            st.markdown("""
**AIStats**（AI Statistical Package for the Social Sciences）бол хиймэл оюун ухааны туслах чадвартай онлайн өгөгдлийн шинжилгээний платформ бөгөөд судлаачид, өгөгдөл шинжлэгчид болон оюутнуудад хялбар, хүчирхэг, ухаалаг статистик шинжилгээний хэрэгсэл өгөх зорилготой.

Энэ систем бол **төгсөлтийн ажил**, сэдэв: ХИЙМЭЛ ОЮУН УХААНД СУУРИЛСАН AISTATS ОНЛАЙН ӨГӨГДЛИЙН ШИНЖИЛГЭЭНИЙ СИСТЕМ
            """)

        st.markdown("---")

        # 核心特色
        if lang == 'zh':
            st.markdown("## 🎯 核心特色")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🤖 AI 智能助手")
                st.markdown("""
- 自然语言交互，无需记忆复杂操作
- 基于 Function Calling 的双向绑定机制
- 智能方法推荐与结果解读
- 支持多轮对话上下文
                """)

                st.markdown("### 📊 专业统计分析")
                st.markdown("""
- 16 种常用统计方法
- 涵盖描述统计、假设检验、回归分析等
- 支持信度分析、中介效应分析
                """)

            with col2:
                st.markdown("### 📈 交互式可视化")
                st.markdown("""
- 7 种交互式图表类型
- 基于 Plotly 的动态图表
- 支持缩放、悬停、导出
- AI 智能图表分析
                """)

                st.markdown("### 🎨 现代化界面")
                st.markdown("""
- 简洁直观的 Web 界面
- 零编程基础即可使用
- 双语支持（中文/蒙古语）
- 响应式设计，适配多种设备
                """)
        else:
            st.markdown("## 🎯 Гол онцлог")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🤖 AI ухаалаг туслах")
                st.markdown("""
- Байгалийн хэлээр харилцах, нарийн үйлдлийг санах шаардлагагүй
- Function Calling дээр суурилсан хоёр талын холболтын механизм
- Ухаалаг арга санал болгох, үр дүн тайлбарлах
- Олон удаагийн ярианы контекст дэмжих
                """)

                st.markdown("### 📊 Мэргэжлийн статистик шинжилгээ")
                st.markdown("""
- 16 түгээмэл статистик арга
- Тайлбарлах статистик, таамаглал шалгах, регресс шинжилгээ гэх мэт
- Найдвартай шинжилгээ, зуучлалын нөлөөллийн шинжилгээ дэмжих
                """)

            with col2:
                st.markdown("### 📈 Интерактив дүрслэл")
                st.markdown("""
- 7 төрлийн интерактив график
- Plotly дээр суурилсан динамик график
- Томруулах, hover, экспорт дэмжих
- AI ухаалаг график шинжилгээ
                """)

                st.markdown("### 🎨 Орчин үеийн интерфэйс")
                st.markdown("""
- Энгийн ойлгомжтой вэб интерфэйс
- Програмчлалын үндсэн мэдлэггүйгээр ашиглах боломжтой
- Хоёр хэлний дэмжлэг（Хятад/Монгол）
- Responsive дизайн, олон төхөөрөмжид тохирно
                """)

        st.markdown("---")

        # 应用价值
        if lang == 'zh':
            st.markdown("## 🎓 应用价值")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 教育领域")
                st.markdown("""
**统计学教学**
- 实时演示统计方法操作流程
- AI 辅助解读提升教学直观性
- 学生可独立完成分析任务

**毕业论文指导**
- 学生独立完成数据分析
- 减轻导师操作指导负担
- 提升研究效率
                """)

            with col2:
                st.markdown("### 科研领域")
                st.markdown("""
**跨学科研究**
- 非统计专业研究者可独立分析
- 降低跨学科合作沟通成本
- 提升研究自主性

**快速探索**
- 低时间成本完成多轮探索
- 加快研究假设生成与筛选
- 集成分析与可视化
                """)
        else:
            st.markdown("## 🎓 Хэрэглээний үнэ цэнэ")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Боловсролын салбар")
                st.markdown("""
**Статистикийн сургалт**
- Статистик аргын үйл ажиллагааны урсгалыг бодит цагт үзүүлэх
- AI туслах тайлбар нь сургалтын ойлгомжтой байдлыг нэмэгдүүлэх
- Оюутнууд бие даан шинжилгээний даалгавар гүйцэтгэх боломжтой
                """)

            with col2:
                st.markdown("### Судалгааны салбар")
                st.markdown("""
**Салбар хоорондын судалгаа**
- Статистикийн мэргэжлийн бус судлаачид бие даан шинжилгээ хийх боломжтой
- Салбар хоорондын хамтын ажиллагааны харилцааны зардлыг бууруулах
- Судалгааны бие даасан байдлыг нэмэгдүүлэх
                """)

    # ========== 技术架构部分 ==========
    if section == 'tech' or section == 'all':
        if lang == 'zh':
            st.markdown("## 🏗️ 技术架构")
            st.markdown("### 核心技术栈")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Web 框架**")
                st.code("Streamlit 1.28.0+")
                st.markdown("快速构建数据应用")

            with col2:
                st.markdown("**数据处理**")
                st.code("pandas 2.2.0+\nNumPy 1.26.0+")
                st.markdown("强大的数据处理能力")

            with col3:
                st.markdown("**统计计算**")
                st.code("SciPy 1.12.0+\nstatsmodels 0.14.0+")
                st.markdown("专业统计分析引擎")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**可视化**")
                st.code("Plotly 5.20.0+")
                st.markdown("交互式图表库")

            with col2:
                st.markdown("**AI 集成**")
                st.code("DeepSeek API")
                st.markdown("大语言模型服务")

            with col3:
                st.markdown("**开发语言**")
                st.code("Python 3.8+")

            st.markdown("---")
            st.markdown("### 系统架构")
            st.markdown("""
```
表示层（Streamlit UI）
    ↓
业务逻辑层（数据管理、统计分析、AI助手、可视化）
    ↓
数据访问层（Session State）
    ↓
技术支撑层（pandas/SciPy/Plotly/DeepSeek）
```
            """)
        else:
            st.markdown("## 🏗️ Техникийн архитектур")
            st.markdown("### Гол технологийн стек")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Вэб фреймворк**")
                st.code("Streamlit 1.28.0+")
                st.markdown("Өгөгдлийн апп хурдан бүтээх")

            with col2:
                st.markdown("**Өгөгдөл боловсруулалт**")
                st.code("pandas 2.2.0+\nNumPy 1.26.0+")
                st.markdown("Хүчирхэг өгөгдөл боловсруулах чадвар")

            with col3:
                st.markdown("**Статистик тооцоолол**")
                st.code("SciPy 1.12.0+\nstatsmodels 0.14.0+")
                st.markdown("Мэргэжлийн статистик шинжилгээний хөдөлгүүр")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Дүрслэл**")
                st.code("Plotly 5.20.0+")
                st.markdown("Интерактив график сан")

            with col2:
                st.markdown("**AI интеграци**")
                st.code("DeepSeek API")
                st.markdown("Том хэлний загварын үйлчилгээ")

            with col3:
                st.markdown("**Хөгжүүлэлтийн хэл**")
                st.code("Python 3.8+")

            st.markdown("---")
            st.markdown("### Системийн архитектур")
            st.markdown("""
```
Харуулах давхарга（Streamlit UI）
    ↓
Бизнес логикийн давхарга（Өгөгдөл удирдлага, статистик шинжилгээ, AI туслах, дүрслэл）
    ↓
Өгөгдөл хандах давхарга（Session State）
    ↓
Техникийн дэмжлэгийн давхарга（pandas/SciPy/Plotly/DeepSeek）
```
            """)

        st.markdown("---")

        # 核心创新
        if lang == 'zh':
            st.markdown("## 💡 核心创新")

            with st.expander("🔄 **双向绑定机制**", expanded=True):
                st.markdown("""
基于 Function Calling 实现"自然语言 → 统计引擎 → 自然语言"的完整闭环：

1. **第一次 AI 调用**：理解用户意图，生成结构化函数调用
2. **函数执行**：统计引擎进行真实计算，返回准确结果
3. **第二次 AI 调用**：基于真实统计结果，生成通俗易懂的解释

**关键特点**：
- 正向绑定：自然语言 → 结构化函数调用
- 反向绑定：统计结果 → 通俗解释
- 防幻觉：AI 只基于真实计算结果解读，不捏造数据
                """)

            with st.expander("📝 **三层 Prompt 工程策略**"):
                st.markdown("""
面向统计分析任务设计的多层 Prompt 工程框架：

**系统级 Prompt**：定义 AI 角色、能力边界、行为准则

**任务级 Prompt**：针对具体统计方法的专业指导

**输出级 Prompt**：控制输出格式和语言风格
                """)


        else:
            st.markdown("## 💡 Гол шинэлэг зүйл")

            with st.expander("🔄 **Хоёр талын холболтын механизм**", expanded=True):
                st.markdown("""
Function Calling дээр суурилан "байгалийн хэл → статистик хөдөлгүүр → байгалийн хэл" бүрэн гогцоо хэрэгжүүлэх：

1. **Эхний AI дуудлага**：Хэрэглэгчийн санааг ойлгож, бүтэцтэй функц дуудлага үүсгэх
2. **Функц гүйцэтгэл**：Статистик хөдөлгүүр бодит тооцоолол хийж, нарийвчлалтай үр дүн буцаах
3. **Хоёр дахь AI дуудлага**：Бодит статистик үр дүн дээр үндэслэн ойлгомжтой тайлбар үүсгэх
                """)

            with st.expander("📝 **Гурван давхаргын Prompt инженерийн стратеги**"):
                st.markdown("""
Статистик шинжилгээний даалгаварт зориулсан олон давхаргын Prompt инженерийн хүрээ：

**Системийн түвшний Prompt**：AI-ийн үүрэг, чадварын хязгаар, зан үйлийн зарчмыг тодорхойлох

**Даалгаврын түвшний Prompt**：Тодорхой статистик аргад зориулсан мэргэжлийн удирдамж

**Гаралтын түвшний Prompt**：Гаралтын формат, хэлний хэв маягийг хянах
                """)


