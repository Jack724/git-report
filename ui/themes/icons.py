"""
图标定义
使用Unicode Emoji和符号
"""


class Icons:
    """图标常量"""

    # 文件和文件夹
    FOLDER = "📁"
    FILE = "📄"
    SEARCH = "🔍"
    ADD = "➕"
    REMOVE = "➖"
    DELETE = "🗑️"
    EDIT = "✏️"
    SAVE = "💾"

    # 状态
    SUCCESS = "✓"
    WARNING = "⚠"
    ERROR = "✗"
    INFO = "ℹ️"
    SETTINGS = "⚙️"

    # 操作
    REPORT = "📊"
    GENERATE = "🚀"
    DOWNLOAD = "⬇️"
    UPLOAD = "⬆️"
    REFRESH = "🔄"
    COPY = "📋"

    # AI相关
    AI = "🤖"
    BRAIN = "🧠"
    SPARK = "✨"

    # Git相关
    GIT = "🔧"
    REPO = "📦"
    COMMIT = "📝"
    BRANCH = "🌿"

    # 其他
    CLOCK = "🕐"
    CALENDAR = "📅"
    USER = "👤"
    EMAIL = "📧"
    LINK = "🔗"
    STAR = "⭐"
    HEART = "❤️"
    LIGHTNING = "⚡"


def add_icon(text: str, icon: str) -> str:
    """
    为文本添加图标

    Args:
        text: 文本内容
        icon: 图标

    Returns:
        带图标的文本
    """
    return f"{icon} {text}"
