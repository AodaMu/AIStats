"""数据视图模块：导入/预览/导出/删除数据"""
import streamlit as st
import pandas as pd
import io
from src.lib.variable_labels import get_value_labels
from src.lib.i18n import t, get_lang

def render_data_view():
    lang = get_lang()
    
    # 标题行和快捷按钮
    col1, col2, col3 = st.columns([3.2, 2.2, 0.6])
    with col1:
        title = "📁 数据视图" if lang == 'zh' else "📁 Өгөгдлийн харах"
        st.title(title)
    with col2:
        # 快捷按钮组
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        with btn_col1:
            btn_text = "📈 绘图" if lang == 'zh' else "📈 График"
            btn_help = "跳转到绘图视图" if lang == 'zh' else "График харах руу шилжих"
            if st.button(btn_text, help=btn_help, use_container_width=True, type="secondary"):
                st.session_state.current_page = "plot"
                st.rerun()
        with btn_col2:
            btn_text = "📊 统计" if lang == 'zh' else "📊 Статистик"
            btn_help = "跳转到统计视图" if lang == 'zh' else "Статистик харах руу шилжих"
            if st.button(btn_text, help=btn_help, use_container_width=True, type="secondary"):
                st.session_state.current_page = "stat"
                st.rerun()
        with btn_col3:
            btn_help = "跳转到AI辅助分析" if lang == 'zh' else "AI туслах шинжилгээ рүү шилжих"
            if st.button("🤖 AI", help=btn_help, use_container_width=True, type="secondary"):
                st.session_state.current_page = "ai"
                st.rerun()
    with col3:
        btn_help = "查看新手指南" if lang == 'zh' else "гарын авлага үзэх"
        if st.button("❓", help=btn_help, use_container_width=True, type="secondary"):
            st.session_state.current_page = "help"
            st.rerun()
    
    # 数据导入区域
    header_text = "数据导入" if lang == 'zh' else "Өгөгдөл импортлох"
    st.header(header_text)
    
    col_import1, col_import2 = st.columns([3, 1])
    with col_import1:
        label_text = "选择数据文件" if lang == 'zh' else "Өгөгдлийн файл сонгох"
        help_text = "支持 CSV、Excel 格式" if lang == 'zh' else "CSV, Excel форматыг дэмжинэ"
        st.caption(label_text)
        uploaded_file = st.file_uploader(
            label_text,
            type=['csv', 'xlsx', 'xls'],
            help=help_text,
            label_visibility="collapsed"
        )
    with col_import2:
        btn_text = "📥 加载示例数据" if lang == 'zh' else "📥 Жишээ өгөгдөл ачаалах"
        btn_help = "加载中学生作业数据示例" if lang == 'zh' else "Дунд сургуулийн сурагчдын даалгаврын жишээ өгөгдөл"
        if st.button(btn_text, use_container_width=True, help=btn_help):
            import os
            example_file = "中学生作业数据_Homework_Data.csv"
            if os.path.exists(example_file):
                try:
                    df = pd.read_csv(example_file)
                    
                    # 检查是否有旧标签和对话
                    old_data_name = st.session_state.get('data_name')
                    has_old_labels = bool(st.session_state.get('value_labels', {}))
                    has_old_chat = bool(st.session_state.get('chat_history', []))
                    
                    # 如果是不同的数据且有旧配置，自动清除
                    if (has_old_labels or has_old_chat) and old_data_name != example_file:
                        st.session_state.value_labels = {}
                        st.session_state.manual_values = {}
                        st.session_state.chat_history = []
                        st.session_state.stat_result = None
                        info_text = "💡 已自动清除旧标签和对话历史" if lang == 'zh' else "💡 Хуучин тэмдэглэгээ болон харилцан ярианы түүхийг автоматаар устгалаа"
                        st.info(info_text)
                    
                    st.session_state.data = df
                    st.session_state.data_name = example_file
                    success_text = f"✅ 成功加载示例数据：{example_file}" if lang == 'zh' else f"✅ Жишээ өгөгдлийг амжилттай ачааллаа：{example_file}"
                    st.success(success_text)
                    st.rerun()
                except Exception as e:
                    error_text = f"❌ 加载示例数据失败：{str(e)}" if lang == 'zh' else f"❌ Жишээ өгөгдөл ачаалах амжилтгүй：{str(e)}"
                    st.error(error_text)
            else:
                warning_text = f"⚠️ 示例数据文件不存在：{example_file}" if lang == 'zh' else f"⚠️ Жишээ өгөгдлийн файл байхгүй байна：{example_file}"
                st.warning(warning_text)
    
    if uploaded_file is not None:
        try:
            # 根据文件类型读取
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            elif uploaded_file.name.endswith('.xls'):
                df = pd.read_excel(uploaded_file, engine='xlrd')
            
            # 将数字列名转换为字符串，避免类型错误
            df.columns = [str(col) for col in df.columns]
            
            # 检查是否有旧的数据和标签
            old_data_name = st.session_state.get('data_name')
            has_old_labels = bool(st.session_state.get('value_labels', {}))
            has_old_chat = bool(st.session_state.get('chat_history', []))
            
            # 如果是不同的数据文件且有旧标签或对话历史，提示清除
            if (has_old_labels or has_old_chat) and old_data_name != uploaded_file.name:
                if 'clear_labels_on_new_data' not in st.session_state:
                    warning_msg = "⚠️ 检测到之前数据的配置：" if lang == 'zh' else "⚠️ Өмнөх өгөгдлийн тохиргоо илэрлээ："
                    if has_old_labels:
                        warning_msg += "\n- 值标签配置" if lang == 'zh' else "\n- Утгын тэмдэглэгээний тохиргоо"
                    if has_old_chat:
                        warning_msg += "\n- AI对话历史" if lang == 'zh' else "\n- AI харилцан ярианы түүх"
                    warning_msg += "\n\n是否清除这些旧数据？" if lang == 'zh' else "\n\nЭдгээр хуучин өгөгдлийг устгах уу?"
                    st.warning(warning_msg)
                    
                    col_warn1, col_warn2 = st.columns(2)
                    with col_warn1:
                        btn_text = "🗑️ 清除旧数据" if lang == 'zh' else "🗑️ Хуучин өгөгдөл устгах"
                        if st.button(btn_text, use_container_width=True, type="primary"):
                            # 清除标签
                            st.session_state.value_labels = {}
                            st.session_state.manual_values = {}
                            # 清除对话历史和统计结果
                            st.session_state.chat_history = []
                            st.session_state.stat_result = None
                            st.session_state.clear_labels_on_new_data = True
                            success_text = "✅ 已清除旧标签和对话历史" if lang == 'zh' else "✅ Хуучин тэмдэглэгээ болон харилцан ярианы түүхийг устгалаа"
                            st.success(success_text)
                    with col_warn2:
                        btn_text = "📌 保留旧数据" if lang == 'zh' else "📌 Хуучин өгөгдөл хадгалах"
                        if st.button(btn_text, use_container_width=True, type="secondary"):
                            st.session_state.clear_labels_on_new_data = False
                            info_text = "💡 已保留旧配置（可能需要手动调整）" if lang == 'zh' else "💡 Хуучин тохиргоог хадгалсан (гараар тохируулах шаардлагатай байж болно)"
                            st.info(info_text)
                    st.stop()
            
            st.session_state.data = df
            st.session_state.data_name = uploaded_file.name
            # 清除标志
            if 'clear_labels_on_new_data' in st.session_state:
                del st.session_state.clear_labels_on_new_data
            success_text = f"✅ 成功导入数据：{uploaded_file.name}" if lang == 'zh' else f"✅ Өгөгдлийг амжилттай оруулсан：{uploaded_file.name}"
            st.success(success_text)
        except Exception as e:
            error_text = f"❌ 数据导入失败：{str(e)}" if lang == 'zh' else f"❌ Өгөгдөл оруулах амжилтгүй：{str(e)}"
            st.error(error_text)
    
    # 数据预览与操作
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # 数据预览标题和切换按钮
        col_header, col_toggle = st.columns([4, 1])
        with col_header:
            header_text = "数据预览" if lang == 'zh' else "Өгөгдлийн урьдчилсан үзэлт"
            st.header(header_text)
        with col_toggle:
            # 检查是否有任何值标签
            has_labels = any(get_value_labels(col) for col in df.columns)
            if has_labels:
                # 初始化显示模式
                if 'show_labels' not in st.session_state:
                    st.session_state.show_labels = False
                
                # 切换按钮
                if not st.session_state.show_labels:
                    btn_text = "🏷️ 显示标签" if lang == 'zh' else "🏷️ Тэмдэглэгээ харуулах"
                else:
                    btn_text = "🔢 显示原值" if lang == 'zh' else "🔢 Анхны утга харуулах"
                btn_help = "点击切换显示标签/原始值" if lang == 'zh' else "Тэмдэглэгээ/анхны утга харуулахыг сольж дарна уу"
                if st.button(btn_text, help=btn_help, use_container_width=True, type="secondary"):
                    st.session_state.show_labels = not st.session_state.show_labels
                    st.rerun()
        
        # 数据基本信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            label = "总行数" if lang == 'zh' else "Нийт мөрийн тоо"
            st.metric(label, len(df))
        with col2:
            label = "总列数" if lang == 'zh' else "Нийт баганын тоо"
            st.metric(label, len(df.columns))
        with col3:
            label = "数据集" if lang == 'zh' else "Өгөгдлийн багц"
            unnamed = "未命名" if lang == 'zh' else "Нэргүй"
            st.metric(label, st.session_state.data_name or unnamed)
        with col4:
            label = "内存占用" if lang == 'zh' else "Санах ойн эзэлхүүн"
            st.metric(label, f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # 数据表格
        # 根据切换状态决定显示内容
        if st.session_state.get('show_labels', False):
            # 显示标签版本
            display_df = df.copy()
            for col in display_df.columns:
                labels = get_value_labels(col)
                if labels:
                    # 将值替换为标签
                    display_df[col] = display_df[col].apply(
                        lambda x: labels.get(x, labels.get(int(x) if isinstance(x, float) and x == int(x) else x, str(x)))
                    )
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            caption = "🏷️ 当前显示：标签值" if lang == 'zh' else "🏷️ Одоо харуулж байна: Тэмдэглэгээний утга"
            st.caption(caption)
        else:
            st.dataframe(
                df,
                use_container_width=True,
                height=400
            )
        
        # 数据操作
        header_text = "数据操作" if lang == 'zh' else "Өгөгдлийн үйлдэл"
        st.header(header_text)
        
        # 快捷操作按钮行
        col_action1, col_action2 = st.columns(2)
        with col_action1:
            btn_text = "📊 查看描述统计" if lang == 'zh' else "📊 Тайлбарлах статистик үзэх"
            if st.button(btn_text, use_container_width=True, type="primary"):
                subheader_text = "📋 数值型变量描述统计" if lang == 'zh' else "📋 Тоон хувьсагчийн тайлбарлах статистик"
                st.subheader(subheader_text)
                numeric_df = df.select_dtypes(include=['int64', 'float64'])
                if len(numeric_df.columns) > 0:
                    st.dataframe(numeric_df.describe(), use_container_width=True)
                else:
                    warning_text = "⚠️ 数据集中没有数值型变量" if lang == 'zh' else "⚠️ Өгөгдлийн багцад тоон хувьсагч байхгүй байна"
                    st.warning(warning_text)
        
        with col_action2:
            # 删除数据
            btn_text = "🗑️ 删除数据" if lang == 'zh' else "🗑️ Өгөгдөл устгах"
            if st.button(btn_text, use_container_width=True, type="secondary"):
                if st.session_state.get('confirm_delete', False):
                    st.session_state.data = None
                    st.session_state.data_name = None
                    st.session_state.stat_result = None
                    # 同时清除标签和对话历史
                    st.session_state.value_labels = {}
                    st.session_state.manual_values = {}
                    st.session_state.chat_history = []
                    st.session_state.confirm_delete = False
                    success_text = "✅ 已删除数据及相关配置（标签、对话历史）" if lang == 'zh' else "✅ Өгөгдөл болон холбогдох тохиргоог устгалаа (тэмдэглэгээ, харилцан ярианы түүх)"
                    st.success(success_text)
                    st.rerun()
                else:
                    st.session_state.confirm_delete = True
                    warning_text = "⚠️ 再次点击确认删除（数据、标签、对话历史都会被清除）" if lang == 'zh' else "⚠️ Устгахыг баталгаажуулахын тулд дахин дарна уу (өгөгдөл, тэмдэглэгээ, харилцан ярианы түүх бүгдийг устгана)"
                    st.warning(warning_text)
        
        # 导出数据部分
        st.markdown("---")
        subheader_text = "📥 导出数据" if lang == 'zh' else "📥 Өгөгдөл экспортлох"
        st.subheader(subheader_text)
        
        col_export1, col_export2, col_export3 = st.columns([1, 1, 1])
        
        with col_export1:
            label_text = "导出格式" if lang == 'zh' else "Экспортын формат"
            help_text = "选择导出的文件格式" if lang == 'zh' else "Экспортлох файлын форматыг сонгох"
            export_format = st.selectbox(
                label_text, 
                ["CSV", "Excel"],
                help=help_text
            )
        
        with col_export2:
            label_text = "文件名" if lang == 'zh' else "Файлын нэр"
            help_text = "输入导出文件的名称（不含扩展名）" if lang == 'zh' else "Экспортлох файлын нэрийг оруулна уу (өргөтгөлгүй)"
            export_name = st.text_input(
                label_text, 
                value="exported_data",
                help=help_text
            )
        
        with col_export3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            btn_text = "📤 导出数据" if lang == 'zh' else "📤 Өгөгдөл экспортлох"
            export_button = st.button(btn_text, use_container_width=True, type="primary")
        
        # 处理导出
        if export_button:
            try:
                if export_format == "CSV":
                    buffer = io.StringIO()
                    df.to_csv(buffer, index=False)
                    data_bytes = buffer.getvalue().encode('utf-8')
                    mime = 'text/csv'
                    ext = 'csv'
                elif export_format == "Excel":
                    buffer = io.BytesIO()
                    df.to_excel(buffer, index=False, engine='openpyxl')
                    data_bytes = buffer.getvalue()
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    ext = 'xlsx'

                download_label = f"⬇️ 下载 {export_format} 文件" if lang == 'zh' else f"⬇️ {export_format} файл татах"
                st.download_button(
                    label=download_label,
                    data=data_bytes,
                    file_name=f"{export_name}.{ext}",
                    mime=mime,
                    use_container_width=True
                )
                success_text = f"✅ {export_format} 文件已准备好，点击上方按钮下载" if lang == 'zh' else f"✅ {export_format} файл бэлэн боллоо, дээрх товчийг дарж татаж авна уу"
                st.success(success_text)
            except Exception as e:
                error_text = f"❌ 导出失败：{str(e)}" if lang == 'zh' else f"❌ Экспортлох амжилтгүй：{str(e)}"
                st.error(error_text)
    
    else:
        info_text = "💡 请先导入数据" if lang == 'zh' else "💡 Эхлээд өгөгдөл импортлоно уу"
        st.info(info_text)

