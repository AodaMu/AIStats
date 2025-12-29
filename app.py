"""
AIStats - AI 加持的在线统计分析应用 (Python 版)
包含数据/绘图/统计/AI 辅助分析四大模块
支持中文/蒙古语切换
"""
import sys
from pathlib import Path
import base64

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from src.components.data_view import render_data_view
from src.components.label_view import render_label_view
from src.components.plot_view import render_plot_view
from src.components.stat_view import render_stat_view
from src.components.ai_view_v2 import render_ai_view
from src.components.help_view import render_help_view
from src.components.terminology_view import render_terminology_view
from src.components.about_view import render_about_view
from src.lib.i18n import t, get_lang, set_lang, render_language_switcher

# 页面配置
st.set_page_config(
    page_title="AIStats",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入全局 CSS
st.markdown("""
<style>
/* 固定顶部栏 - 在侧边栏上方 */
.fixed-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 50px;
    background: #ffffff;
    z-index: 1000001;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px 0 50px;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}

/* 展开按钮占位符 */
.expand-btn-placeholder {
    position: fixed;
    top: 10px;
    left: 10px;
    width: 32px;
    height: 32px;
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: #666;
    z-index: 1000003;
    cursor: pointer;
}
.expand-btn-placeholder:hover {
    background: #e0e2e6;
}

/* 侧边栏折叠时隐藏左边白色背景 */
body:has([data-testid="collapsedControl"]) .fixed-header::before,
body:has([data-testid="stSidebarCollapsedControl"]) .fixed-header::before {
    display: none;
}
.fixed-header .logo {
    font-size: 22px;
    font-weight: bold;
    color: #111827;
}
.fixed-header .lang-switch {
    display: flex;
    gap: 8px;
    align-items: center;
}
.fixed-header .lang-btn {
    cursor: pointer;
    padding: 4px 6px;
    border-radius: 5px;
    transition: all 0.2s;
    text-align: center;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 5px;
    color: inherit;
    border: none;
    background: transparent;
}
.fixed-header .lang-btn:hover {
    background: rgba(0,0,0,0.04);
}
.fixed-header .lang-btn.active {
    background: rgba(0,0,0,0.04);
    border: 2px solid rgba(0,0,0,0.15);
}
.fixed-header .lang-btn.inactive {
    opacity: 0.7;
    border: 1px solid rgba(0,0,0,0.10);
}
.fixed-header .lang-btn img {
    width: 28px;
    height: auto;
    border-radius: 2px;
}
.fixed-header .lang-btn span {
    font-size: 13px;
}

.fixed-header .flag-wrap {
    cursor: pointer;
    width: 44px;
    height: 28px;
    border-radius: 3px;
    overflow: hidden;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: transparent;
}
.fixed-header .flag-wrap img {
    width: 44px;
    height: 28px;
    display: block;
    object-fit: cover;
    pointer-events: none;
}
.fixed-header .flag-wrap.active {
    border: 2px solid rgba(0,0,0,0.35);
}
.fixed-header .flag-wrap.inactive {
    border: 1px solid rgba(0,0,0,0.12);
    opacity: 0.85;
}
.fixed-header .flag-wrap:hover {
    background: rgba(0,0,0,0.03);
}

/* 固定底部栏 - 论文介绍 */
.fixed-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 40px;
    background: #f8f9fa;
    z-index: 1000001;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 20px;
    border-top: 1px solid rgba(0,0,0,0.08);
    font-size: 13px;
    color: #666;
}
.fixed-footer a {
    color: #1a73e8;
    text-decoration: none;
    margin: 0 4px;
}
.fixed-footer a:hover {
    text-decoration: underline;
}

/* 主内容区域下移 */
.main .block-container {
    padding-top: 70px !important;
}

/* 侧边栏折叠后的展开按钮 - 覆盖在占位符上 */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
div[data-testid="collapsedControl"],
div[data-testid="stSidebarCollapsedControl"] {
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    width: 32px !important;
    height: 32px !important;
    z-index: 1000004 !important;
    background: transparent !important;
    overflow: visible !important;
}

[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] button,
button[aria-label="Expand sidebar"] {
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    width: 32px !important;
    height: 32px !important;
    z-index: 1000005 !important;
    opacity: 0.01 !important;
    cursor: pointer !important;
}

/* 侧边栏展开后的折叠按钮 */
button[aria-label="Collapse sidebar"] {
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 1000002 !important;
}

/* 侧边栏展开时隐藏占位符 */
body:has(section[data-testid="stSidebar"][aria-expanded="true"]) .expand-btn-placeholder {
    display: none !important;
}

section[data-testid="stSidebar"] > div {
    padding-top: 60px !important;
    margin-top: 50px !important;
}

/* 语言切换按钮 - 中文按钮 */
div.stElementContainer.st-key-__lang_zh_btn,
div[class*="stElementContainer"][class*="st-key-__lang_zh_btn"] {
    position: fixed !important;
    top: 8px !important;
    right: 66px !important;
    left: auto !important;
    width: 52px !important;
    height: 36px !important;
    z-index: 1000002 !important;
    overflow: visible !important;
    margin: 0 !important;
    padding: 0 !important;
}

div.stElementContainer.st-key-__lang_zh_btn button,
div[class*="st-key-__lang_zh_btn"] button {
    width: 52px !important;
    height: 36px !important;
    min-height: 36px !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
    opacity: 0 !important;
    cursor: pointer !important;
}

/* 语言切换按钮 - 蒙古语按钮 */
div.stElementContainer.st-key-__lang_mn_btn,
div[class*="stElementContainer"][class*="st-key-__lang_mn_btn"] {
    position: fixed !important;
    top: 8px !important;
    right: 12px !important;
    left: auto !important;
    width: 52px !important;
    height: 36px !important;
    z-index: 1000002 !important;
    overflow: visible !important;
    margin: 0 !important;
    padding: 0 !important;
}

div.stElementContainer.st-key-__lang_mn_btn button,
div[class*="st-key-__lang_mn_btn"] button {
    width: 52px !important;
    height: 36px !important;
    min-height: 36px !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
    opacity: 0 !important;
    cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<script>
(function () {
  function fixSidebarToggle() {
    const expandBtn =
      document.querySelector('button[aria-label="Expand sidebar"]') ||
      document.querySelector('[data-testid="collapsedControl"] button') ||
      document.querySelector('[data-testid="stSidebarCollapsedControl"] button');

    const collapseBtn =
      document.querySelector('button[aria-label="Collapse sidebar"]') ||
      document.querySelector('button[data-testid="stSidebarCollapseButton"]');

    // 展开按钮（侧边栏折叠时显示）
    if (expandBtn) {
      expandBtn.style.cssText = 'position:fixed!important;top:60px!important;left:12px!important;z-index:1000010!important;display:block!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;';
    }
    // 折叠按钮（侧边栏展开时显示）
    if (collapseBtn) {
      collapseBtn.style.cssText = 'position:fixed!important;top:60px!important;left:20px!important;z-index:1000003!important;display:block!important;visibility:visible!important;opacity:1!important;pointer-events:auto!important;';
    }
  }

  function moveLangButtons() {
    const zhContainer = document.querySelector('[id*="__lang_zh_btn"]');
    const mnContainer = document.querySelector('[id*="__lang_mn_btn"]');
    const header = document.querySelector('.fixed-header .lang-switch');
    
    if (zhContainer && header) {
      const zhBtn = zhContainer.querySelector('button');
      if (zhBtn && !zhBtn.classList.contains('lang-btn-zh')) {
        zhBtn.classList.add('lang-btn-zh');
        zhBtn.style.cssText = 'position:fixed!important;top:11px!important;right:72px!important;z-index:100001!important;width:48px!important;height:32px!important;padding:0!important;margin:0!important;border:none!important;background:transparent!important;opacity:0!important;cursor:pointer!important;pointer-events:auto!important;';
        header.appendChild(zhBtn);
      }
    }
    if (mnContainer && header) {
      const mnBtn = mnContainer.querySelector('button');
      if (mnBtn && !mnBtn.classList.contains('lang-btn-mn')) {
        mnBtn.classList.add('lang-btn-mn');
        mnBtn.style.cssText = 'position:fixed!important;top:11px!important;right:20px!important;z-index:100001!important;width:48px!important;height:32px!important;padding:0!important;margin:0!important;border:none!important;background:transparent!important;opacity:0!important;cursor:pointer!important;pointer-events:auto!important;';
        header.appendChild(mnBtn);
      }
    }
  }

  setTimeout(fixSidebarToggle, 200);
  setInterval(fixSidebarToggle, 1000);
  setTimeout(moveLangButtons, 300);
  setInterval(moveLangButtons, 500);
})();
</script>
""", unsafe_allow_html=True)

# 初始化 session_state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'data_name' not in st.session_state:
    st.session_state.data_name = None
if 'stat_result' not in st.session_state:
    st.session_state.stat_result = None
if 'ai_config' not in st.session_state:
    st.session_state.ai_config = {
        'enabled': True,
        'api_key': 'sk-6299528af8be4fffa13ae14a20f0db69',
        'base_url': 'https://api.deepseek.com',
        'model': 'deepseek-chat'
    }
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
else:
    # 清理可能损坏的对话历史
    try:
        # 验证对话历史的完整性
        for msg in st.session_state.chat_history:
            if not isinstance(msg, dict):
                raise ValueError("Invalid message format")
    except Exception:
        # 如果验证失败，清空对话历史
        st.session_state.chat_history = []

# 初始化语言设置
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# 初始化页面（使用内部key，不受语言影响）
if 'current_page' not in st.session_state:
    st.session_state.current_page = "data"

# 页面映射（内部key -> 显示文本）
PAGE_KEYS = ["data", "label", "ai", "plot", "stat", "terminology"]
PAGE_NAMES = {
    "data": {"zh": "📁 数据视图", "mn": "📁 Өгөгдлийн харах"},
    "label": {"zh": "🏷️ 值标签", "mn": "🏷️ Утгын шошго"},
    "ai": {"zh": "🤖 AI 辅助分析", "mn": "🤖 AI туслах шинжилгээ"},
    "plot": {"zh": "📈 绘图视图", "mn": "📈 График харах"},
    "stat": {"zh": "📊 统计视图", "mn": "📊 Статистик харах"},
    "terminology": {"zh": "📚 术语解释", "mn": "📚 Нэр томьёоны тайлбар"}
}

def get_page_name(key):
    """根据当前语言获取页面名称"""
    lang = get_lang()
    return PAGE_NAMES.get(key, {}).get(lang, key)

# ========== 处理 URL 参数语言切换 ==========
lang = get_lang()

# 国旗图片 URL
def _svg_data_uri(svg_path: str) -> str:
    p = Path(__file__).parent / svg_path
    svg_bytes = p.read_bytes()
    encoded = base64.b64encode(svg_bytes).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"

CN_FLAG = _svg_data_uri("cn.svg")
MN_FLAG = _svg_data_uri("mn.svg")

def _set_lang_to(code: str):
    current = get_lang()
    if code in ['zh', 'mn'] and code != current:
        set_lang(code)

st.button("", key="__lang_zh_btn", help="中文", on_click=_set_lang_to, args=("zh",))
st.button("", key="__lang_mn_btn", help="Монгол", on_click=_set_lang_to, args=("mn",))

# 渲染固定顶部栏（国旗可点击）
zh_class = "active" if lang == 'zh' else "inactive"
mn_class = "active" if lang == 'mn' else "inactive"

# 底部论文介绍内容（双语）
if lang == 'zh':
    footer_text = '本系统为毕业设计作品 | 论文题目：《基于AI的在线统计分析系统设计与实现》'
else:
    footer_text = 'Энэ систем бол төгсөлтийн ажил | Сэдэв: Хиймэл оюун ухаанд суурилсан AIStats онлайн өгөгдлийн шинжилгээний систем'

st.markdown(f'''
<div class="expand-btn-placeholder">»</div>
<div class="fixed-header">
    <div class="logo">AIStats</div>
    <div class="lang-switch">
        <div class="flag-wrap {zh_class}">
            <img src="{CN_FLAG}" alt="中文">
        </div>
        <div class="flag-wrap {mn_class}">
            <img src="{MN_FLAG}" alt="Монгол">
        </div>
    </div>
</div>
<div class="fixed-footer">
    {footer_text}
</div>
''', unsafe_allow_html=True)

# 注入JavaScript处理展开按钮点击
import streamlit.components.v1 as components
components.html("""
<script>
(function() {
    function setup() {
        const placeholder = window.parent.document.querySelector('.expand-btn-placeholder');
        const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
        
        if (placeholder) {
            // 侧边栏展开时隐藏占位符
            if (sidebar) {
                const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
                placeholder.style.display = isExpanded ? 'none' : 'flex';
            }
            
            // 绑定点击事件
            if (!placeholder._bindClick) {
                placeholder._bindClick = true;
                placeholder.onclick = function() {
                    // 查找所有可能的展开按钮
                    const allBtns = window.parent.document.querySelectorAll('button');
                    let expandBtn = null;
                    
                    // 遍历所有按钮找到展开按钮
                    allBtns.forEach(btn => {
                        const label = btn.getAttribute('aria-label') || '';
                        const testId = btn.getAttribute('data-testid') || '';
                        if (label.includes('Expand') || label.includes('expand') || 
                            testId.includes('collapse') || testId.includes('Collapse')) {
                            expandBtn = btn;
                        }
                    });
                    
                    // 也尝试查找父容器中的按钮
                    if (!expandBtn) {
                        const container = window.parent.document.querySelector('[data-testid*="collapse"]') ||
                                         window.parent.document.querySelector('[data-testid*="Collapse"]');
                        if (container) {
                            expandBtn = container.querySelector('button');
                        }
                    }
                    
                    if (expandBtn) {
                        expandBtn.click();
                    } else {
                        // 直接模拟键盘快捷键或其他方式
                        const event = new KeyboardEvent('keydown', {
                            key: '[',
                            code: 'BracketLeft',
                            ctrlKey: true,
                            bubbles: true
                        });
                        window.parent.document.dispatchEvent(event);
                    }
                };
            }
        }
    }
    setTimeout(setup, 200);
    setInterval(setup, 300);
})();
</script>
""", height=0)

# ========== 侧边栏导航 ==========

# 判断当前是否在关于页面
is_in_about = st.session_state.get('show_about_page', False) or st.session_state.get('show_help_page', False)

# 主模块选项
page_options = [get_page_name(key) for key in PAGE_KEYS]

# 如果在关于页面，主模块不选中任何项
if is_in_about:
    main_index = None
else:
    main_index = PAGE_KEYS.index(st.session_state.current_page) if st.session_state.current_page in PAGE_KEYS else 0

# 选择模块标签
select_label = "选择模块" if lang == 'zh' else "Модуль сонгох"
page = st.sidebar.radio(
    select_label,
    page_options,
    index=main_index,
    key="main_radio"
)

# 处理主模块选择
if page and not is_in_about:
    selected_index = page_options.index(page) if page in page_options else 0
    new_page_key = PAGE_KEYS[selected_index]
    if new_page_key != st.session_state.current_page:
        st.session_state.current_page = new_page_key
        st.session_state.show_about_page = False
        st.session_state.show_help_page = False
        st.rerun()
elif page and is_in_about:
    # 如果在关于页面但点击了主模块，切换到主模块
    selected_index = page_options.index(page) if page in page_options else 0
    new_page_key = PAGE_KEYS[selected_index]
    st.session_state.current_page = new_page_key
    st.session_state.show_about_page = False
    st.session_state.show_help_page = False
    st.rerun()

st.sidebar.markdown("---")

# 关于区域标题（不可选择）
about_title = "### ℹ️ 关于" if lang == 'zh' else "### ℹ️ Тухай"
st.sidebar.markdown(about_title)

# 关于选项
ABOUT_KEYS = ["tech", "overview", "help"]
ABOUT_NAMES = {
    "tech": {"zh": "💻 基于 Streamlit + DeepSeek", "mn": "💻 Streamlit + DeepSeek"},
    "overview": {"zh": "🎯 Python 在线统计分析工具", "mn": "🎯 Python статистик хэрэгсэл"},
    "help": {"zh": "❓ 新手指南", "mn": "❓ гарын авлага"}
}

def get_about_name(key):
    return ABOUT_NAMES.get(key, {}).get(lang, key)

about_options = [get_about_name(key) for key in ABOUT_KEYS]

# 确定关于区域当前选中项
if st.session_state.get('show_about_page', False):
    current_about = st.session_state.get('about_section', 'tech')
    about_index = ABOUT_KEYS.index(current_about) if current_about in ABOUT_KEYS else None
elif st.session_state.get('show_help_page', False):
    about_index = ABOUT_KEYS.index("help")
else:
    about_index = None

about_selection = st.sidebar.radio(
    "",  # 空标签，因为上面已经有标题了
    about_options,
    index=about_index,
    key="about_radio",
    label_visibility="collapsed"
)

# 处理关于选项的选择
if about_selection:
    selected_about_index = about_options.index(about_selection)
    selected_about_key = ABOUT_KEYS[selected_about_index]
    
    if selected_about_key == "help":
        if not st.session_state.get('show_help_page', False):
            st.session_state.show_help_page = True
            st.session_state.show_about_page = False
            st.rerun()
    elif selected_about_key in ["tech", "overview"]:
        if not st.session_state.get('show_about_page', False) or st.session_state.get('about_section') != selected_about_key:
            st.session_state.show_about_page = True
            st.session_state.show_help_page = False
            st.session_state.about_section = selected_about_key
            st.rerun()

# 检查是否需要显示关于页面（覆盖当前页面）
if st.session_state.get('show_about_page', False):
    # 显示关于页面（不包含新手指南）
    render_about_view()
    
    # 返回按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        back_text = "← 返回" if lang == 'zh' else "← Буцах"
        if st.button(back_text, use_container_width=True, type="primary"):
            st.session_state.show_about_page = False
            st.rerun()

# 检查是否需要显示新手指南页面（覆盖当前页面）
elif st.session_state.get('show_help_page', False):
    # 显示新手指南页面（原来的完整内容）
    render_help_view()
    
    # 返回按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        back_text = "← 返回" if lang == 'zh' else "← Буцах"
        if st.button(back_text, use_container_width=True, type="primary"):
            st.session_state.show_help_page = False
            st.rerun()

else:
    # 路由到对应模块
    current_page = st.session_state.current_page
    if current_page == "data":
        render_data_view()
    elif current_page == "label":
        render_label_view()
    elif current_page == "ai":
        render_ai_view()
    elif current_page == "plot":
        render_plot_view()
    elif current_page == "stat":
        render_stat_view()
    elif current_page == "terminology":
        render_terminology_view()

