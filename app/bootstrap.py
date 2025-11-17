"""
应用程序引导模块
负责应用初始化和配置加载
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon


def create_application() -> QApplication:
    """
    创建并配置 QApplication 实例

    Returns:
        配置好的 QApplication 实例
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Git 提交记录智能报告生成器")

    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app_icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    return app


def initialize_logger(config_manager):
    """
    初始化日志系统

    Args:
        config_manager: 配置管理器实例
    """
    from infrastructure.logger import get_logger

    logger = get_logger()
    log_level = config_manager.get("log_level", "INFO")
    logger.set_level(log_level)
    logger.info("应用程序启动")

    return logger


def load_theme(app: QApplication):
    """
    加载应用主题

    Args:
        app: QApplication 实例
    """
    from ui.themes.theme_manager import ThemeManager
    ThemeManager.load_theme(app)
