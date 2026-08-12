"""BiliDecode —— B站视频分析终端（公开元数据分析版）"""

import re
import os
import sys

import streamlit as st
from dotenv import load_dotenv

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# ─── Streamlit Cloud Secrets 兼容 ───
# 本地用 .env，云端用 st.secrets，这里统一加载到环境变量
for _key in ("DASHSCOPE_API_KEY", "SUPABASE_URL", "SUPABASE_SECRET_KEY"):
    if _key not in os.environ:
        try:
            os.environ[_key] = st.secrets[_key]
        except (KeyError, FileNotFoundError):
            pass

from config import BAILIAN_MODELS, DEFAULT_MODEL, Y2K_COLORS
from utils.url_parser import parse_url
from core.bilibili_client import fetch_video_data
from core.analyzer import analyze_video_metadata
from core.supabase_client import (
    is_configured as sb_configured,
    save_analysis as sb_save,
    get_history as sb_history,
    get_history_count as sb_count,
    get_report_by_id as sb_report,
    get_stats as sb_stats,
)
from ui.style import inject_y2k_style, render_header
from ui.components import pixel_status, pixel_progress, render_cost_box, render_cover_preview


# ─── 页面配置 ───
st.set_page_config(
    page_title="BiliDecode - B站视频分析终端",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_y2k_style()
render_header()


# ─── 侧边栏：API Key 配置 ───
with st.sidebar:
    st.markdown(
        '<div class="y2k-sidebar-title">⚙ CONFIG</div>',
        unsafe_allow_html=True,
    )
    api_key_input = st.text_input(
        "百炼 API Key",
        value=os.getenv("DASHSCOPE_API_KEY", ""),
        type="password",
        help="在阿里云百炼控制台获取 API Key",
    )
    if api_key_input:
        os.environ["DASHSCOPE_API_KEY"] = api_key_input

    st.markdown("---")

    # Supabase 连接状态
    sb_ok = sb_configured()
    sb_icon = "✅" if sb_ok else "❌"
    sb_text = "Supabase 已连接" if sb_ok else "Supabase 未配置"
    st.markdown(
        f"<div style='font-family: VT323, monospace; font-size: 18px; "
        f"color: {Y2K_COLORS['accent_primary']};'>"
        f"{sb_icon} {sb_text}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-family: VT323, monospace; font-size: 18px; "
        "color: #00CED1;'>"
        "🔗 获取 API Key:<br>"
        "<a href='https://bailian.console.aliyun.com/' target='_blank'>"
        "百炼控制台</a><br><br>"
        "本项目仅采集B站公开元数据<br>"
        "不下载视频内容"
        "</div>",
        unsafe_allow_html=True,
    )


# ─── 主区域：API Key 状态提示 ───
_api_key_check = os.getenv("DASHSCOPE_API_KEY", "")
if not _api_key_check:
    st.markdown(
        """
        <div style="
            font-family: 'Press Start 2P', cursive;
            font-size: 11px;
            color: #FF6EC7;
            background: #1A0033;
            border: 3px solid #FF6EC7;
            box-shadow: 4px 4px 0 #000;
            padding: 14px 20px;
            margin-bottom: 20px;
            text-align: center;
        ">
            ⬅ 请在左侧 CONFIG 面板输入百炼 API Key ⬅
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════
#  Tab 导航
# ═══════════════════════════════════════════
tab_analyze, tab_history, tab_dashboard = st.tabs(
    ["🔍 分析", "📜 历史记录", "📊 仪表盘"]
)


# ═══════════════════════════════════════════
#  Tab 1: 分析
# ═══════════════════════════════════════════
with tab_analyze:
    st.markdown("### INPUT VIDEO URL")

    col1, col2 = st.columns([3, 1])

    with col1:
        url_input = st.text_input(
            "B站视频链接",
            placeholder="https://www.bilibili.com/video/BVxxxxxxxx",
            label_visibility="collapsed",
            key="url_input",
        )

    with col2:
        model_options = {key: info["label"] for key, info in BAILIAN_MODELS.items()}
        selected_model_label = st.selectbox(
            "模型",
            options=list(model_options.values()),
            index=0,
            label_visibility="collapsed",
        )
        selected_model = next(
            key for key, label in model_options.items() if label == selected_model_label
        )

    analyze_btn = st.button("START ANALYSIS", use_container_width=True)


    # ─── 报告拆分 ───
    def split_report_sections(report_text: str) -> list[tuple[str, str]]:
        pattern = r"(^|\n)(#{1,2}\s+[^#\n]+)"
        parts = re.split(pattern, report_text)

        sections = []
        current_title = ""
        current_content = ""

        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            if re.match(r"^#{1,2}\s+", part):
                if current_title:
                    sections.append((current_title, current_content.strip()))
                current_title = re.sub(r"^#{1,2}\s+", "", part)
                current_content = ""
            else:
                current_content += part + "\n"

        if current_title:
            sections.append((current_title, current_content.strip()))

        return sections


    # ─── 分析逻辑 ───
    if analyze_btn:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            pixel_status("ERROR: 请先在侧边栏配置百炼 API Key", "error")
            st.stop()

        if not url_input.strip():
            pixel_status("ERROR: 请输入B站视频链接", "error")
            st.stop()

        bvid = parse_url(url_input)
        if not bvid:
            pixel_status("ERROR: 无法解析BV号，请检查链接是否正确", "error")
            st.stop()

        pixel_status(f"BVID: {bvid}  MODEL: {selected_model}", "info")

        with st.status("分析进行中...", expanded=True) as status:
            st.write("📡 采集视频元数据...")
            pixel_progress("FETCHING DATA", 15)

            video_data = fetch_video_data(bvid)

            if not video_data.title:
                status.update(label="采集失败", state="error")
                pixel_status(
                    f"ERROR: {video_data.errors[0] if video_data.errors else '视频数据采集失败'}",
                    "error",
                )
                st.stop()

            st.write(f"✅ 视频标题：{video_data.title}")
            pixel_progress("DATA FETCHED", 30)

            st.write("💬 采集热门评论与弹幕...")
            pixel_progress("FETCHING COMMENTS", 50)

            st.write(f"🤖 调用 {selected_model} 分析中...")
            pixel_progress("AI ANALYSIS", 70)

            result = analyze_video_metadata(video_data, model=selected_model, api_key=api_key)

            if result.error:
                status.update(label="分析失败", state="error")
                pixel_status(f"ERROR: {result.error}", "error")
                st.stop()

            pixel_progress("ANALYSIS COMPLETE", 100)
            status.update(label="分析完成!", state="complete")

        # ─── 展示结果 ───
        st.markdown("---")

        if video_data.cover_url:
            st.markdown("#### COVER PREVIEW")
            render_cover_preview(video_data.cover_url, video_data.title)

        if video_data.errors:
            with st.expander("⚠ 数据采集异常记录", expanded=False):
                for err in video_data.errors:
                    st.markdown(f"- {err}")

        st.markdown("### 📋 ANALYSIS REPORT")

        sections = split_report_sections(result.text)

        if sections:
            for title, content in sections:
                with st.expander(title, expanded=(title == sections[0][0])):
                    st.markdown(content)
        else:
            st.markdown(result.text)

        st.markdown("---")
        render_cost_box(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost=result.estimated_cost,
            model=result.model,
        )

        # ─── 保存到 Supabase ───
        if sb_configured():
            saved = sb_save(video_data, result, video_url=url_input.strip())
            if saved:
                st.markdown(
                    f"<div style='font-family: VT323, monospace; font-size: 18px; "
                    f"color: {Y2K_COLORS['success']};'>"
                    f"✅ 分析记录已保存到 Supabase"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='font-family: VT323, monospace; font-size: 18px; "
                    f"color: {Y2K_COLORS['error']};'>"
                    f"⚠ Supabase 保存失败，不影响本次分析结果"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    elif not analyze_btn:
        st.markdown(
            """
            <div style='font-family: VT323, monospace; font-size: 18px; color: #00CED1;'>
            📺 在上方输入B站视频链接，选择模型后点击 START ANALYSIS 开始分析。<br>
            系统将采集视频公开元数据（标题、统计、评论、弹幕、封面等），<br>
            调用阿里百炼多模态大模型生成六维度结构化分析报告。<br><br>
            支持的链接格式：<br>
            • https://www.bilibili.com/video/BVxxxxxxxx<br>
            • https://b23.tv/xxxxxxx<br>
            • https://m.bilibili.com/video/BVxxxxxxxx
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════
#  Tab 2: 历史记录
# ═══════════════════════════════════════════
with tab_history:
    st.markdown("### 📜 ANALYSIS HISTORY")

    if not sb_configured():
        st.markdown(
            f"<div style='font-family: VT323, monospace; font-size: 20px; "
            f"color: {Y2K_COLORS['accent_secondary']}; "
            f"border: 2px solid {Y2K_COLORS['accent_secondary']}; "
            f"padding: 20px; text-align: center;'>"
            "⚠ Supabase 未配置<br>"
            "请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_SECRET_KEY"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        total = sb_count()
        st.markdown(
            f"<div style='font-family: VT323, monospace; font-size: 20px; "
            f"color: {Y2K_COLORS['accent_primary']}; margin-bottom: 15px;'>"
            f"共 {total} 条分析记录"
            f"</div>",
            unsafe_allow_html=True,
        )

        if total > 0:
            history = sb_history(limit=50)

            for record in history:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        title = record.get("title", "未知标题")
                        bvid = record.get("bvid", "")
                        up = record.get("up_name", "")
                        st.markdown(
                            f"**{title}**<br>"
                            f"<span style='color: {Y2K_COLORS['accent_primary']}; "
                            f"font-family: VT323, monospace; font-size: 18px;'>"
                            f"BV号: {bvid} | UP主: {up}"
                            f"</span>",
                            unsafe_allow_html=True,
                        )

                    with col2:
                        model = record.get("model_used", "")
                        cost = record.get("estimated_cost", 0) or 0
                        st.markdown(
                            f"<span style='font-family: VT323, monospace; "
                            f"font-size: 18px; color: {Y2K_COLORS['accent_secondary']};'>"
                            f"模型: {model}<br>费用: ¥{cost:.4f}"
                            f"</span>",
                            unsafe_allow_html=True,
                        )

                    with col3:
                        created = record.get("created_at", "")
                        date_str = created[:16].replace("T", " ") if created else ""
                        view_count = record.get("view_count", 0) or 0
                        st.markdown(
                            f"<span style='font-family: VT323, monospace; "
                            f"font-size: 18px; color: {Y2K_COLORS['accent_primary']};'>"
                            f"播放: {view_count:,}<br>{date_str}"
                            f"</span>",
                            unsafe_allow_html=True,
                        )

                    # 查看报告按钮
                    report_id = record.get("id", "")
                    if st.button("查看报告", key=f"btn_{report_id}"):
                        full_report = sb_report(report_id)
                        if full_report:
                            report_text = full_report.get("report_text", "")
                            if report_text:
                                sections = split_report_sections(report_text)
                                if sections:
                                    for s_title, s_content in sections:
                                        with st.expander(s_title, expanded=(s_title == sections[0][0])):
                                            st.markdown(s_content)
                                else:
                                    st.markdown(report_text)
                            else:
                                st.warning("报告内容为空")

                    st.markdown("---")
        else:
            st.markdown(
                f"<div style='font-family: VT323, monospace; font-size: 20px; "
                f"color: {Y2K_COLORS['accent_primary']}; text-align: center; "
                f"padding: 40px;'>"
                "暂无分析记录，去「分析」Tab 开始第一次分析吧！"
                f"</div>",
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════
#  Tab 3: 仪表盘
# ═══════════════════════════════════════════
with tab_dashboard:
    st.markdown("### 📊 DASHBOARD")

    if not sb_configured():
        st.markdown(
            f"<div style='font-family: VT323, monospace; font-size: 20px; "
            f"color: {Y2K_COLORS['accent_secondary']}; "
            f"border: 2px solid {Y2K_COLORS['accent_secondary']}; "
            f"padding: 20px; text-align: center;'>"
            "⚠ Supabase 未配置<br>"
            "请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_SECRET_KEY"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        stats = sb_stats()

        if stats.get("total", 0) == 0:
            st.markdown(
                f"<div style='font-family: VT323, monospace; font-size: 20px; "
                f"color: {Y2K_COLORS['accent_primary']}; text-align: center; "
                f"padding: 40px;'>"
                "暂无数据，去「分析」Tab 生成第一份报告吧！"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            # ─── 核心指标卡片 ───
            col1, col2, col3, col4 = st.columns(4)

            def metric_card(label: str, value: str, color: str):
                st.markdown(
                    f"<div style='border: 3px solid {color}; "
                    f"box-shadow: 4px 4px 0 #000; padding: 16px; "
                    f"background: {Y2K_COLORS['bg_main']}; text-align: center; "
                    f"margin-bottom: 10px;'>"
                    f"<div style='font-family: Press Start 2P, cursive; "
                    f"font-size: 10px; color: {color};'>{label}</div>"
                    f"<div style='font-family: VT323, monospace; "
                    f"font-size: 28px; color: #F0F0FF; margin-top: 8px;'>{value}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            with col1:
                metric_card("TOTAL", str(stats["total"]), Y2K_COLORS["accent_primary"])
            with col2:
                metric_card("COST ¥", f"{stats['total_cost']:.4f}", Y2K_COLORS["accent_secondary"])
            with col3:
                metric_card("IN TOKENS", f"{stats['total_input_tokens']:,}", Y2K_COLORS["success"])
            with col4:
                metric_card("OUT TOKENS", f"{stats['total_output_tokens']:,}", Y2K_COLORS["error"])

            st.markdown("---")

            # ─── Plotly 图表 ───
            try:
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots

                # 图表颜色
                PINK = Y2K_COLORS["accent_secondary"]
                CYAN = Y2K_COLORS["accent_primary"]
                GREEN = Y2K_COLORS["success"]
                BG = Y2K_COLORS["bg_main"]

                plotly_layout = dict(
                    paper_bgcolor=BG,
                    plot_bgcolor=BG,
                    font=dict(family="VT323, monospace", size=16, color="#F0F0FF"),
                    margin=dict(l=40, r=20, t=50, b=40),
                )

                col_left, col_right = st.columns(2)

                # ─── 左列：近7天分析趋势 ───
                with col_left:
                    st.markdown("#### 近7天分析趋势")
                    recent = stats.get("recent_7d", [])
                    if recent:
                        dates = [r["date"][5:] for r in recent]  # MM-DD
                        counts = [r["count"] for r in recent]

                        fig = go.Figure(data=go.Scatter(
                            x=dates,
                            y=counts,
                            mode="lines+markers",
                            line=dict(color=CYAN, width=3),
                            marker=dict(size=10, color=PINK, line=dict(width=2, color="#000")),
                            fill="tozeroy",
                            fillcolor="rgba(0, 206, 209, 0.1)",
                        ))
                        fig.update_layout(**plotly_layout, height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    # ─── 模型使用分布 ───
                    st.markdown("#### 模型使用分布")
                    model_dist = stats.get("model_distribution", {})
                    if model_dist:
                        colors = [PINK, CYAN, GREEN, Y2K_COLORS["error"]][:len(model_dist)]
                        fig2 = go.Figure(data=go.Pie(
                            labels=list(model_dist.keys()),
                            values=list(model_dist.values()),
                            marker=dict(colors=colors, line=dict(width=2, color="#000")),
                            textfont=dict(size=16, color="#FFF"),
                        ))
                        fig2.update_layout(**plotly_layout, height=300)
                        st.plotly_chart(fig2, use_container_width=True)

                # ─── 右列：Top5 播放量 ───
                with col_right:
                    st.markdown("#### Top 5 播放量视频")
                    top_viewed = stats.get("top_viewed", [])
                    if top_viewed:
                        titles = [t["title"][:15] + "..." if len(t["title"]) > 15 else t["title"]
                                  for t in top_viewed]
                        views = [t["view_count"] for t in top_viewed]

                        fig3 = go.Figure(data=go.Bar(
                            x=views,
                            y=titles,
                            orientation="h",
                            marker_color=PINK,
                            marker_line=dict(width=2, color="#000"),
                            text=[f"{v:,}" for v in views],
                            textposition="outside",
                            textfont=dict(color=CYAN, size=14),
                        ))
                        fig3.update_layout(
                            **plotly_layout,
                            height=350,
                            yaxis=dict(autorange="reversed"),
                            xaxis=dict(color=CYAN),
                        )
                        st.plotly_chart(fig3, use_container_width=True)

                    # ─── Token 消耗对比 ───
                    st.markdown("#### Token 消耗对比")
                    fig4 = go.Figure(data=[
                        go.Bar(
                            name="输入",
                            x=["Input"],
                            y=[stats["total_input_tokens"]],
                            marker_color=CYAN,
                            marker_line=dict(width=2, color="#000"),
                        ),
                        go.Bar(
                            name="输出",
                            x=["Output"],
                            y=[stats["total_output_tokens"]],
                            marker_color=PINK,
                            marker_line=dict(width=2, color="#000"),
                        ),
                    ])
                    fig4.update_layout(
                        **plotly_layout,
                        barmode="group",
                        height=250,
                        showlegend=True,
                        legend=dict(font=dict(color="#F0F0FF")),
                    )
                    st.plotly_chart(fig4, use_container_width=True)

            except ImportError:
                st.warning("图表功能需要 plotly 库，请运行: pip install plotly")
