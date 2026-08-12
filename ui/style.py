"""Y2K 像素风格 CSS 注入"""

import streamlit as st
import streamlit.components.v1 as components

from config import Y2K_COLORS, GOOGLE_FONTS_URL


def inject_y2k_style():
    """注入 Y2K 像素风格全局 CSS"""

    # 加载 Google Fonts
    st.markdown(
        f'<link href="{GOOGLE_FONTS_URL}" rel="stylesheet">',
        unsafe_allow_html=True,
    )

    css = f"""
    <style>
    /* ─── 全局像素化渲染 ─── */
    html, body, [class*="css"] {{
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        -webkit-font-smoothing: none !important;
        font-smooth: never !important;
    }}

    /* ─── 主背景 ─── */
    .stApp {{
        background-color: {Y2K_COLORS["bg_main"]} !important;
        background-image:
            linear-gradient(rgba(0, 206, 209, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 206, 209, 0.03) 1px, transparent 1px);
        background-size: 20px 20px;
    }}

    /* ─── 标题 ─── */
    h1, h2, h3, .stTitle {{
        font-family: 'Press Start 2P', cursive !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
        letter-spacing: 1px;
        text-shadow: 3px 3px 0 {Y2K_COLORS["accent_secondary"]};
    }}

    /* ─── 主标题区域 ─── */
    .y2k-header {{
        text-align: center;
        padding: 20px 0;
        border-bottom: 4px solid {Y2K_COLORS["accent_primary"]};
        margin-bottom: 30px;
    }}
    .y2k-header h1 {{
        font-family: 'Press Start 2P', cursive;
        font-size: 28px;
        color: {Y2K_COLORS["accent_primary"]};
        text-shadow: 4px 4px 0 {Y2K_COLORS["accent_secondary"]};
        margin: 0;
    }}
    .y2k-header p {{
        font-family: 'VT323', monospace;
        font-size: 20px;
        color: {Y2K_COLORS["accent_secondary"]};
        margin: 10px 0 0 0;
    }}

    /* ─── 输入框 ─── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border: 3px solid {Y2K_COLORS["border"]} !important;
        border-radius: 0 !important;
        box-shadow: 4px 4px 0 {Y2K_COLORS["border"]} !important;
        background: {Y2K_COLORS["bg_card"]} !important;
        font-family: 'VT323', monospace !important;
        font-size: 20px !important;
        color: {Y2K_COLORS["text_main"]} !important;
    }}

    /* ─── 按钮 ─── */
    .stButton > button {{
        border: 3px solid {Y2K_COLORS["border"]} !important;
        border-radius: 0 !important;
        box-shadow: 4px 4px 0 {Y2K_COLORS["border"]} !important;
        background: {Y2K_COLORS["accent_primary"]} !important;
        color: {Y2K_COLORS["text_main"]} !important;
        font-family: 'Press Start 2P', cursive !important;
        font-size: 12px !important;
        padding: 14px 24px !important;
        transition: none !important;
        cursor: pointer;
    }}
    .stButton > button:hover {{
        background: {Y2K_COLORS["accent_secondary"]} !important;
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0 {Y2K_COLORS["border"]} !important;
    }}
    .stButton > button:active {{
        transform: translate(4px, 4px) !important;
        box-shadow: 0 0 0 {Y2K_COLORS["border"]} !important;
    }}

    /* ─── 单选框 / 下拉框 ─── */
    .stRadio > div, .stSelectbox > div {{
        color: {Y2K_COLORS["bg_card"]} !important;
    }}
    .stRadio label, .stSelectbox label {{
        font-family: 'VT323', monospace !important;
        font-size: 20px !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
    }}

    /* ─── 折叠面板 ─── */
    .streamlit-expanderHeader {{
        font-family: 'Press Start 2P', cursive !important;
        font-size: 12px !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
        background: {Y2K_COLORS["bg_main"]} !important;
        border: 2px solid {Y2K_COLORS["accent_primary"]} !important;
    }}
    .streamlit-expanderContent {{
        background: {Y2K_COLORS["bg_card"]} !important;
        border: 2px solid {Y2K_COLORS["accent_primary"]} !important;
        border-top: none !important;
    }}

    /* ─── Markdown 内容（折叠面板内：浅底深字） ─── */
    .streamlit-expanderContent .stMarkdown {{
        color: {Y2K_COLORS["text_main"]} !important;
    }}
    .streamlit-expanderContent h1,
    .streamlit-expanderContent h2,
    .streamlit-expanderContent h3 {{
        color: {Y2K_COLORS["bg_main"]} !important;
        text-shadow: none !important;
    }}
    .streamlit-expanderContent table {{
        width: 100% !important;
        border: 2px solid {Y2K_COLORS["border"]} !important;
    }}
    .streamlit-expanderContent th {{
        background: {Y2K_COLORS["accent_primary"]} !important;
        color: {Y2K_COLORS["text_main"]} !important;
        font-family: 'VT323', monospace !important;
        border: 1px solid {Y2K_COLORS["border"]} !important;
        padding: 8px !important;
    }}
    .streamlit-expanderContent td {{
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        border: 1px solid {Y2K_COLORS["border"]} !important;
        padding: 6px 8px !important;
    }}

    /* ─── 报告正文（主页面深底亮字） ─── */
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown ul,
    .stMarkdown ol,
    .stMarkdown strong,
    .stMarkdown em,
    .stMarkdown blockquote {{
        color: #F0F0FF !important;
        font-size: 18px !important;
        line-height: 1.6 !important;
    }}
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4 {{
        color: {Y2K_COLORS["accent_primary"]} !important;
    }}
    .stMarkdown table {{
        width: 100% !important;
        border: 2px solid {Y2K_COLORS["accent_primary"]} !important;
        border-collapse: collapse !important;
        margin: 10px 0 !important;
    }}
    .stMarkdown th {{
        background: rgba(0, 206, 209, 0.2) !important;
        color: {Y2K_COLORS["accent_primary"]} !important;
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        border: 1px solid rgba(0, 206, 209, 0.4) !important;
        padding: 8px !important;
    }}
    .stMarkdown td {{
        color: #F0F0FF !important;
        font-family: 'VT323', monospace !important;
        font-size: 18px !important;
        border: 1px solid rgba(0, 206, 209, 0.3) !important;
        padding: 6px 8px !important;
    }}
    .stMarkdown strong {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    .stMarkdown code {{
        color: {Y2K_COLORS["success"]} !important;
        background: rgba(0, 255, 65, 0.1) !important;
        padding: 2px 6px !important;
        border-radius: 0 !important;
    }}

    /* 折叠面板内报告文字覆盖（浅底深字） */
    .streamlit-expanderContent .stMarkdown p,
    .streamlit-expanderContent .stMarkdown li,
    .streamlit-expanderContent .stMarkdown strong,
    .streamlit-expanderContent .stMarkdown em,
    .streamlit-expanderContent .stMarkdown td {{
        color: {Y2K_COLORS["text_main"]} !important;
    }}
    .streamlit-expanderContent .stMarkdown strong {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    .streamlit-expanderContent .stMarkdown code {{
        color: {Y2K_COLORS["error"]} !important;
        background: rgba(255, 0, 64, 0.1) !important;
    }}

    /* ─── 侧边栏：霓虹发光边框 + 脉冲动画 ─── */
    @keyframes sidebar-glow {{
        0%, 100% {{
            box-shadow: 0 0 10px {Y2K_COLORS["accent_secondary"]},
                        0 0 20px {Y2K_COLORS["accent_secondary"]},
                        inset -3px 0 0 {Y2K_COLORS["accent_secondary"]};
        }}
        50% {{
            box-shadow: 0 0 20px {Y2K_COLORS["accent_primary"]},
                        0 0 40px {Y2K_COLORS["accent_primary"]},
                        inset -3px 0 0 {Y2K_COLORS["accent_primary"]};
        }}
    }}
    section[data-testid="stSidebar"] {{
        background-color: {Y2K_COLORS["bg_main"]} !important;
        border-right: 4px solid {Y2K_COLORS["accent_secondary"]} !important;
        animation: sidebar-glow 2s ease-in-out infinite !important;
    }}
    section[data-testid="stSidebar"] label {{
        color: {Y2K_COLORS["accent_primary"]} !important;
        font-family: 'VT323', monospace !important;
        font-size: 22px !important;
    }}

    /* 侧边栏标题 */
    .y2k-sidebar-title {{
        font-family: 'Press Start 2P', cursive !important;
        font-size: 16px !important;
        color: {Y2K_COLORS["accent_secondary"]} !important;
        text-shadow: 2px 2px 0 {Y2K_COLORS["accent_primary"]};
        text-align: center;
        padding: 16px 0 !important;
        border-bottom: 3px solid {Y2K_COLORS["accent_primary"]};
        margin-bottom: 16px;
    }}

    /* 侧边栏展开/折叠按钮：霓虹粉风格 */
    button[kind="header"] {{
        background: {Y2K_COLORS["accent_secondary"]} !important;
        color: {Y2K_COLORS["text_main"]} !important;
        border: 2px solid {Y2K_COLORS["border"]} !important;
        border-radius: 0 !important;
        box-shadow: 3px 3px 0 {Y2K_COLORS["border"]} !important;
    }}
    button[kind="header"] span[data-testid="stIconMaterial"] {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    /* 所有 Material 图标默认霓虹粉 */
    span[data-testid="stIconMaterial"] {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
    }}

    /* ─── 状态指示器 ─── */
    .y2k-status {{
        font-family: 'Press Start 2P', cursive;
        font-size: 10px;
        padding: 10px 16px;
        border: 3px solid {Y2K_COLORS["border"]};
        box-shadow: 4px 4px 0 {Y2K_COLORS["border"]};
        display: inline-block;
        margin: 5px 0;
    }}
    .y2k-status-info {{
        background: {Y2K_COLORS["accent_primary"]};
        color: {Y2K_COLORS["text_main"]};
    }}
    .y2k-status-success {{
        background: {Y2K_COLORS["success"]};
        color: {Y2K_COLORS["text_main"]};
    }}
    .y2k-status-error {{
        background: {Y2K_COLORS["error"]};
        color: {Y2K_COLORS["bg_card"]};
    }}

    /* ─── 进度条 ─── */
    .stProgress > div > div > div {{
        background-color: {Y2K_COLORS["accent_primary"]} !important;
    }}

    /* ─── 链接 ─── */
    a {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
        text-decoration: underline !important;
    }}

    /* ─── 隐藏 Streamlit 默认元素 ─── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    /* ─── 强制覆盖 Material 图标颜色 ─── */
    span[data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"],
    .st-emotion-cache-5r6ut5,
    [class*="st-emotion-cache"] span[translate="no"] {{
        color: {Y2K_COLORS["accent_secondary"]} !important;
        fill: {Y2K_COLORS["accent_secondary"]} !important;
        -webkit-text-fill-color: {Y2K_COLORS["accent_secondary"]} !important;
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    # 通过 iframe 访问父页面 DOM，强制修改 Material 图标颜色
    components.html(
        """
        <script>
        function fixIconColors() {
            try {
                var doc = window.parent.document;
                var icons = doc.querySelectorAll('[data-testid="stIconMaterial"]');
                icons.forEach(function(el) {
                    el.style.setProperty('color', '#FF6EC7', 'important');
                    el.style.setProperty('-webkit-text-fill-color', '#FF6EC7', 'important');
                    el.removeAttribute('color');
                });
            } catch(e) {}
        }
        setInterval(fixIconColors, 500);
        </script>
        """,
        height=0,
    )


def render_header():
    """渲染 Y2K 风格页面头部"""
    st.markdown(
        """
        <div class="y2k-header">
            <h1>BILIDECODE</h1>
            <p>B站视频分析终端 v1.0</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
