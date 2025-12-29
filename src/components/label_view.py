"""值标签视图模块：管理变量值标签"""
import streamlit as st
from src.lib.variable_labels import (
    set_value_labels, get_value_labels,
    get_labels_context, clear_variable_labels
)
from src.lib.i18n import get_lang

def render_label_view():
    lang = get_lang()
    
    # 标题行和快捷按钮
    col1, col2, col3 = st.columns([2.0, 2.2, 0.4])
    with col1:
        title = "🏷️ 值标签" if lang == 'zh' else "🏷️ Утгын тэмдэглэгээ"
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
    
    # 检查是否有数据
    if st.session_state.data is not None:
        df = st.session_state.data
        
        header_text = "变量值标签管理" if lang == 'zh' else "Хувьсагчийн утгын тэмдэглэгээ удирдлага"
        st.header(header_text)
        
        if lang == 'zh':
            st.markdown("""
            💡 **值标签功能**：为数值变量添加含义标签，让AI更好地理解数据
            
            **示例**：满意度 1-5 → 1=非常满意, 2=满意, 3=一般, 4=不满意, 5=非常不满意
            """)
        else:
            st.markdown("""
            💡 **Утгын тэмдэглэгээний үүрэг**：Тоон хувьсагчд утгатай тэмдэглэгээ нэмэх, AI-д өгөгдлийг илүү ойлгоход туслах
            
            **Жишээ**：Сэтгэл хангамж 1-5 → 1=маш сэтгэлтэй, 2=сэтгэлтэй, 3=зөвхөн, 4=сэтгэлгүй, 5=маш сэтгэлгүй
            """)
        
        # 选择要设置标签的变量
        label_text = "选择变量" if lang == 'zh' else "Хувьсагч сонгох"
        var_to_label = st.selectbox(
            label_text,
            df.columns,
            key="label_var_select"
        )
        
        # 显示变量的唯一值（安全排序）
        unique_vals_list = df[var_to_label].dropna().unique().tolist()
        # 检查是否全是数字
        all_numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in unique_vals_list)
        if all_numeric:
            unique_values = sorted(unique_vals_list)
        else:
            unique_values = sorted(unique_vals_list, key=str)
        if lang == 'zh':
            st.info(f"📊 变量 **{var_to_label}** 的数据中出现的值: {', '.join(map(str, unique_values))}")
        else:
            st.info(f"📊 Хувьсагч **{var_to_label}** -ын өгөгдлөөс гарсан утгууд: {', '.join(map(str, unique_values))}")
        
        # 自定义标签
        section_title = "### ✏️ 设置标签值" if lang == 'zh' else "### ✏️ Тэмдэглэгээний утга тохируулах"
        st.markdown(section_title)
        
        # 初始化手动添加的值列表
        if 'manual_values' not in st.session_state:
            st.session_state.manual_values = {}
        if var_to_label not in st.session_state.manual_values:
            st.session_state.manual_values[var_to_label] = []
        
        # 获取当前标签（包括之前设置的未出现的值）
        current_labels = get_value_labels(var_to_label)
        
        # 合并：数据中的值 + 已设置标签的值 + 手动添加的值
        all_values = set(unique_values)
        if current_labels:
            all_values.update(current_labels.keys())
        # 添加手动添加的值
        all_values.update(st.session_state.manual_values[var_to_label])
        
        # 安全排序
        all_values_list = list(all_values)
        all_numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in all_values_list)
        if all_numeric:
            all_values = sorted(all_values_list)
        else:
            all_values = sorted(all_values_list, key=str)
        
        # 手动添加值的功能
        expander_title = "➕ 添加数据中未出现的值" if lang == 'zh' else "➕ Өгөгдлөөс гарагуй утга нэмэх"
        with st.expander(expander_title, expanded=False):
            if lang == 'zh':
                st.markdown("💡 **使用场景**：满意度1-3分，但数据中只有1和2，需要为3设置标签")
            else:
                st.markdown("💡 **Ашиглах нөхцөл**：Сэтгэл хангамж 1-3 оноо, харин өгөгдлөөс зөвхөн 1, 2 байгаа, 3-д тэмдэглэгээ тохируулах шаардлагатай")
            
            col_add1, col_add2, col_add3 = st.columns([1, 2, 1])
            with col_add1:
                label = "值" if lang == 'zh' else "Утга"
                help_text = "输入要添加的值（如：3）" if lang == 'zh' else "Нэмэх утгыг оруул (жишээ: 3)"
                new_value = st.text_input(
                    label, 
                    key=f"new_value_{var_to_label}",
                    help=help_text,
                    placeholder="3"
                )
            with col_add2:
                label = "标签" if lang == 'zh' else "Тэмдэглэгээ"
                help_text = "输入该值的标签（如：不喜欢）" if lang == 'zh' else "Тэр утгын тэмдэглэгээ оруул (жишээ: дургүй)"
                new_value_label = st.text_input(
                    label,
                    key=f"new_value_label_{var_to_label}",
                    help=help_text
                )
            with col_add3:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                btn_text = "➕ 添加" if lang == 'zh' else "➕ Нэмэх"
                add_button = st.button(btn_text, use_container_width=True, type="primary")
            
            if add_button:
                if new_value and new_value_label:
                    try:
                        # 尝试转换为数字，如果失败则保持字符串
                        try:
                            val_to_add = int(new_value) if '.' not in new_value else float(new_value)
                        except:
                            val_to_add = new_value
                        
                        # 检查是否已存在
                        if val_to_add not in all_values:
                            # 保存到session_state
                            st.session_state.manual_values[var_to_label].append(val_to_add)
                            # 同时保存标签
                            current_labels[val_to_add] = new_value_label
                            set_value_labels(var_to_label, current_labels)
                            success_text = f"✅ 已添加值 {val_to_add} = {new_value_label}" if lang == 'zh' else f"✅ Утга нэмэгдлээ {val_to_add} = {new_value_label}"
                            st.success(success_text)
                            st.rerun()
                        else:
                            warning_text = f"⚠️ 值 {val_to_add} 已存在" if lang == 'zh' else f"⚠️ Утга {val_to_add} аль хэдийн байна"
                            st.warning(warning_text)
                    except Exception as e:
                        error_text = f"❌ 添加失败：{str(e)}" if lang == 'zh' else f"❌ Нэмэхэд алдаа гарлаа：{str(e)}"
                        st.error(error_text)
                else:
                    warning_text = "⚠️ 请同时输入值和标签" if lang == 'zh' else "⚠️ Утга ба тэмдэглэгээийг нэг дор оруулна уу"
                    st.warning(warning_text)
        
        # 为所有值设置标签（包括数据中的和手动添加的）
        st.markdown("---")
        new_labels = {}
        for val in all_values:
            try:
                val_key = int(val) if isinstance(val, (int, float)) else val
                default_label = current_labels.get(val_key, "")
                
                # 标记数据中是否出现
                in_data = val in unique_values
                if in_data:
                    label_suffix = ""
                else:
                    label_suffix = " 🔴 (数据中未出现)" if lang == 'zh' else " 🔴 (өгөгдлөөс олдохгүй)"
                
                input_label = f"值 {val} 的标签{label_suffix}" if lang == 'zh' else f"Утга {val} -ын тэмдэглэгээ{label_suffix}"
                help_text = f"为数值 {val} 设置有意义的标签" if lang == 'zh' else f"Тоон утга {val} -д утга бүхий тэмдэглэгээ тохируулах"
                
                label = st.text_input(
                    input_label,
                    value=default_label,
                    key=f"label_{var_to_label}_{val}",
                    help=help_text
                )
                if label:
                    new_labels[val_key] = label
            except:
                pass
        
        # 保存和清除按钮
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            btn_text = "💾 保存所有标签" if lang == 'zh' else "💾 Бүх тэмдэглэгээ хадгалах"
            if st.button(btn_text, use_container_width=True, type="primary"):
                if new_labels:
                    set_value_labels(var_to_label, new_labels)
                    success_text = f"✅ 已保存 {var_to_label} 的值标签（共 {len(new_labels)} 个）" if lang == 'zh' else f"✅ {var_to_label} -ын утгын тэмдэглэгээ хадгаллаа（нийт {len(new_labels)} ширхэг）"
                    st.success(success_text)
                    st.rerun()
                else:
                    warning_text = "⚠️ 请至少设置一个标签" if lang == 'zh' else "⚠️ Хамгийн багадаа нэг тэмдэглэгээ тохируулна уу"
                    st.warning(warning_text)
        
        with btn_col2:
            btn_text = "🗑️ 清除当前变量标签" if lang == 'zh' else "🗑️ Одоогийн хувьсагчийн тэмдэглэгээ арилгах"
            if st.button(btn_text, use_container_width=True, type="secondary"):
                # 使用清除函数
                clear_variable_labels(var_to_label)
                # 清除相关的统计结果和对话历史（避免残留）
                st.session_state.stat_result = None
                st.session_state.chat_history = []
                success_text = f"✅ 已清除 {var_to_label} 的所有标签和相关缓存" if lang == 'zh' else f"✅ {var_to_label} -ын бүх тэмдэглэгээ болон холбогдох кэш арилгалаа"
                st.success(success_text)
                st.rerun()
        
        # 显示已设置的所有标签
        labels_context = get_labels_context()
        if labels_context:
            st.markdown("---")
            section_title = "### 📋 已设置的值标签" if lang == 'zh' else "### 📋 Тохируулсан утгын тэмдэглэгээ"
            st.markdown(section_title)
            st.markdown(labels_context)
            
            # 清除所有标签按钮
            btn_text = "🗑️ 清除所有变量的标签" if lang == 'zh' else "🗑️ Бүх хувьсагчийн тэмдэглэгээ арилгах"
            btn_help = "清除当前数据集的所有值标签和相关缓存" if lang == 'zh' else "Одоогийн өгөгдлийн багцын бүх утгын тэмдэглэгээ болон холбогдох кэшийг арилгах"
            if st.button(btn_text, use_container_width=True, type="secondary", help=btn_help):
                clear_variable_labels()  # 不传参数，清除所有标签
                # 清除相关的统计结果和对话历史（避免残留）
                st.session_state.stat_result = None
                st.session_state.chat_history = []
                success_text = "✅ 已清除所有变量的标签和相关缓存（AI对话历史、统计结果）" if lang == 'zh' else "✅ Бүх хувьсагчийн тэмдэглэгээ болон холбогдох кэш (AI ярианы түүх, статистикийн үр дүн) арилгалаа"
                st.success(success_text)
                st.rerun()
    
    else:
        info_text = "💡 请先在 **📁 数据视图** 中导入数据文件" if lang == 'zh' else "💡 Эхлээд **📁 Өгөгдлийн харах** -аас өгөгдлийн файл оруулна уу"
        st.info(info_text)
        btn_text = "📁 前往数据视图" if lang == 'zh' else "📁 Өгөгдлийн харах руу очих"
        if st.button(btn_text, use_container_width=True, type="primary"):
            st.session_state.current_page = "data"
            st.rerun()

