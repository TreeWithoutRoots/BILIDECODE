"""Y2K 像素风自定义 Streamlit 组件"""

import base64
import streamlit as st
import requests

from config import Y2K_COLORS


def pixel_status(text: str, level: str = "info"):
    """
    渲染像素风状态指示器。
    level: "info" | "success" | "error"
    """
    st.markdown(
        f'<div class="y2k-status y2k-status-{level}">{text}</div>',
        unsafe_allow_html=True,
    )


def pixel_progress(label: str, percent: int):
    """
    渲染像素风进度条。
    """
    st.markdown(
        f"""
        <div style="font-family: 'Press Start 2P', cursive; font-size: 10px;
                    color: {Y2K_COLORS['accent_primary']}; margin-bottom: 5px;">
            {label}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(percent / 100)


def render_cost_box(input_tokens: int, output_tokens: int, cost: float, model: str):
    """渲染 Token 用量和费用信息"""
    st.markdown(
        f"""
        <div style="
            border: 3px solid {Y2K_COLORS['accent_primary']};
            box-shadow: 4px 4px 0 {Y2K_COLORS['border']};
            background: {Y2K_COLORS['bg_card']};
            padding: 16px;
            margin-top: 20px;
            font-family: 'VT323', monospace;
            font-size: 20px;
            color: {Y2K_COLORS['text_main']};
        ">
            <span style="font-family: 'Press Start 2P', cursive; font-size: 10px;
                         color: {Y2K_COLORS['bg_main']};">
                ANALYSIS METRICS
            </span>
            <br><br>
            Model: {model}<br>
            Input Tokens: {input_tokens:,}<br>
            Output Tokens: {output_tokens:,}<br>
            Est. Cost: ¥{cost:.4f}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cover_preview(cover_url: str, title: str):
    """渲染封面图预览（通过后端下载绕过防盗链）"""
    if not cover_url:
        return

    try:
        # 带 Referer 头下载图片，绕过 B站防盗链
        headers = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        resp = requests.get(cover_url, headers=headers, timeout=10)
        resp.raise_for_status()

        # 转为 base64 data URL
        img_b64 = base64.b64encode(resp.content).decode("utf-8")
        # 根据内容判断 MIME 类型
        mime = "image/jpeg"
        if resp.content[:4] == b"\x89PNG":
            mime = "image/png"
        elif resp.content[:3] == b"GIF":
            mime = "image/gif"
        elif resp.content[:4] == b"RIFF":
            mime = "image/webp"
        data_url = f"data:{mime};base64,{img_b64}"

        st.markdown(
            f"""
            <div style="
                border: 3px solid {Y2K_COLORS['accent_secondary']};
                box-shadow: 4px 4px 0 {Y2K_COLORS['border']};
                padding: 4px;
                display: inline-block;
                margin: 10px 0;
                background: {Y2K_COLORS['bg_card']};
            ">
                <img src="{data_url}" alt="{title}"
                     style="max-width: 320px; width: 100%; display: block;">
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.markdown(
            f"""
            <div style="
                border: 3px solid {Y2K_COLORS['accent_secondary']};
                box-shadow: 4px 4px 0 {Y2K_COLORS['border']};
                padding: 16px;
                margin: 10px 0;
                background: {Y2K_COLORS['bg_main']};
                font-family: 'VT323', monospace;
                font-size: 18px;
                color: {Y2K_COLORS['accent_secondary']};
            ">
                封面加载失败: {str(e)[:80]}<br>
                <a href="{cover_url}" target="_blank"
                   style="color: {Y2K_COLORS['accent_primary']};">
                   点击直接查看封面
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
