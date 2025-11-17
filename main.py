"""
Git 提交记录智能报告生成器
主入口文件
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow
from ui.themes.theme_manager import ThemeManager
from infrastructure.logger import get_logger
from utils.resource_path import get_resource_path

# 初始化日志
logger = get_logger()


def main():
    """程序主入口"""
    from infrastructure.config_manager import ConfigManager

    logger.info("应用程序启动")

    app = QApplication(sys.argv)
    app.setApplicationName("Git 提交记录智能报告生成器")

    # 设置应用图标（支持打包环境）
    icon_path = get_resource_path('app_icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 加载配置
    config = ConfigManager()
    log_level = config.get("log_level", "INFO")

    # 设置日志级别
    logger.set_level(log_level)

    # 加载主题
    ThemeManager.load_theme(app)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    logger.info("主窗口已显示")

    exit_code = app.exec()

    logger.info(f"应用程序退出, 退出码: {exit_code}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
