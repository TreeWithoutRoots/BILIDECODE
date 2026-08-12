"""BiliDecode 配置常量"""

# ─── 百炼 API ───
BAILIAN_API_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

BAILIAN_MODELS = {
    "qwen3-vl-plus": {
        "label": "qwen3-vl-plus (推荐·多模态)",
        "multimodal": True,
        "input_price": 1.0,      # 元/百万tokens (≤32K)
        "output_price": 10.0,    # 元/百万tokens
        "max_tokens": 4096,
        "temperature": 0.7,
        "context_length": 262144,
    },
    "qwen-plus": {
        "label": "qwen-plus (低成本·纯文本)",
        "multimodal": False,
        "input_price": 0.8,
        "output_price": 2.0,
        "max_tokens": 4096,
        "temperature": 0.7,
        "context_length": 131072,
    },
}

DEFAULT_MODEL = "qwen3-vl-plus"

# ─── B站 API 端点 ───
BILIBILI_API = {
    "video_info": "https://api.bilibili.com/x/web-interface/view",
    "video_tags": "https://api.bilibili.com/x/tag/archive/tags",
    "comments": "https://api.bilibili.com/x/v2/reply",
    "danmaku": "https://comment.bilibili.com/{cid}.xml",
    "owner_info": "https://api.bilibili.com/x/space/acc/info",
    "owner_stat": "https://api.bilibili.com/x/relation/stat",
}

BILIBILI_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bilibili.com",
}

# ─── 请求参数 ───
REQUEST_TIMEOUT = 10          # 秒
REQUEST_INTERVAL = 0.5        # 请求间隔（秒）
MAX_RETRIES = 2               # API 调用失败重试次数
RETRY_DELAY = 3               # 重试间隔（秒）

# ─── 数据采集参数 ───
HOT_COMMENT_LIMIT = 20        # 热评数量
DANMAKU_LIMIT = 50            # 高频弹幕数量

# ─── Y2K 配色 ───
Y2K_COLORS = {
    "bg_main": "#1A0033",      # 深紫蓝主背景
    "bg_card": "#F0F0F0",      # 卡片背景
    "accent_primary": "#00CED1",  # 暗青色
    "accent_secondary": "#FF6EC7", # 霓虹粉
    "text_main": "#000000",    # 纯黑文字
    "success": "#00FF41",      # 像素绿
    "error": "#FF0040",        # 警示红
    "border": "#000000",       # 纯黑边框
}

Y2K_FONTS = {
    "title": "'Press Start 2P', cursive",
    "body": "'VT323', monospace",
}

# ─── Google Fonts ───
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Press+Start+2P&family=VT323&display=swap"
)
