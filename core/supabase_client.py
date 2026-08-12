"""Supabase 客户端模块 —— 分析历史保存与统计查询"""

import os
from datetime import datetime
from typing import Any

from supabase import create_client, Client

from core.bilibili_client import VideoData
from core.analyzer import AnalysisResult


# ─── 初始化客户端（懒加载） ───
_client: Client | None = None


def get_client() -> Client | None:
    """获取 Supabase 客户端实例，未配置则返回 None"""
    global _client
    if _client is not None:
        return _client

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SECRET_KEY", "")

    if not url or not key:
        return None

    _client = create_client(url, key)
    return _client


def is_configured() -> bool:
    """检查 Supabase 是否已配置"""
    return get_client() is not None


# ─── 保存分析记录 ───
def save_analysis(
    video_data: VideoData,
    result: AnalysisResult,
    video_url: str = "",
) -> bool:
    """
    将一次分析结果保存到 Supabase。
    返回 True 表示成功，False 表示失败或未配置。
    """
    client = get_client()
    if client is None:
        return False

    row = {
        "bvid": video_data.bvid,
        "title": video_data.title,
        "video_url": video_url,
        "up_name": video_data.owner_name,
        "cover_url": video_data.cover_url,
        "view_count": video_data.stat_view,
        "like_count": video_data.stat_like,
        "coin_count": video_data.stat_coin,
        "favorite_count": video_data.stat_favorite,
        "report_text": result.text,
        "model_used": result.model,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "estimated_cost": result.estimated_cost,
    }

    try:
        client.table("analysis_history").insert(row).execute()
        return True
    except Exception:
        return False


# ─── 查询历史记录 ───
def get_history(limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
    """
    获取分析历史列表（按时间倒序）。
    返回字典列表，每条包含 id/bvid/title/up_name/view_count/model_used/created_at 等字段。
    """
    client = get_client()
    if client is None:
        return []

    try:
        resp = (
            client.table("analysis_history")
            .select(
                "id, bvid, title, up_name, cover_url, view_count, "
                "like_count, model_used, estimated_cost, created_at"
            )
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return resp.data
    except Exception:
        return []


def get_history_count() -> int:
    """获取历史记录总数"""
    client = get_client()
    if client is None:
        return 0
    try:
        resp = (
            client.table("analysis_history")
            .select("id", count="exact")
            .execute()
        )
        return resp.count or 0
    except Exception:
        return 0


def get_report_by_id(report_id: str) -> dict[str, Any] | None:
    """根据 ID 获取完整的分析报告"""
    client = get_client()
    if client is None:
        return None
    try:
        resp = (
            client.table("analysis_history")
            .select("*")
            .eq("id", report_id)
            .single()
            .execute()
        )
        return resp.data
    except Exception:
        return None


# ─── 统计数据 ───
def get_stats() -> dict[str, Any]:
    """
    获取仪表盘统计数据。
    返回:
    {
        "total": 总分析次数,
        "total_cost": 总费用,
        "total_input_tokens": 总输入token,
        "total_output_tokens": 总输出token,
        "model_distribution": {模型名: 次数},
        "recent_7d": [{date: "YYYY-MM-DD", count: N}, ...],  # 近7天每日分析量
        "top_viewed": [{title, view_count, bvid}, ...],  # Top5播放量
    }
    """
    client = get_client()
    if client is None:
        return {}

    stats: dict[str, Any] = {
        "total": 0,
        "total_cost": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "model_distribution": {},
        "recent_7d": [],
        "top_viewed": [],
    }

    try:
        # 全部数据
        resp = (
            client.table("analysis_history")
            .select("model_used, estimated_cost, input_tokens, output_tokens, "
                    "title, view_count, bvid, created_at")
            .order("created_at", desc=True)
            .limit(500)
            .execute()
        )
        rows = resp.data

        stats["total"] = len(rows)
        stats["total_cost"] = sum(r.get("estimated_cost", 0) or 0 for r in rows)
        stats["total_input_tokens"] = sum(r.get("input_tokens", 0) or 0 for r in rows)
        stats["total_output_tokens"] = sum(r.get("output_tokens", 0) or 0 for r in rows)

        # 模型分布
        model_dist: dict[str, int] = {}
        for r in rows:
            m = r.get("model_used", "unknown")
            model_dist[m] = model_dist.get(m, 0) + 1
        stats["model_distribution"] = model_dist

        # 近7天每日分析量
        now = datetime.now()
        date_counts: dict[str, int] = {}
        for i in range(6, -1, -1):
            d = now.replace(day=now.day - i)
            date_counts[d.strftime("%Y-%m-%d")] = 0

        for r in rows:
            created = r.get("created_at", "")
            if created:
                day = created[:10]
                if day in date_counts:
                    date_counts[day] += 1

        stats["recent_7d"] = [
            {"date": k, "count": v} for k, v in date_counts.items()
        ]

        # Top5 播放量
        sorted_by_views = sorted(
            rows,
            key=lambda x: x.get("view_count", 0) or 0,
            reverse=True,
        )[:5]
        stats["top_viewed"] = [
            {
                "title": r.get("title", "未知"),
                "view_count": r.get("view_count", 0) or 0,
                "bvid": r.get("bvid", ""),
            }
            for r in sorted_by_views
        ]

    except Exception:
        pass

    return stats
