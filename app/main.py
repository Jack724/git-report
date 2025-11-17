"""
Git 提交记录智能报告生成器
应用程序主入口
"""
import sys
from app.bootstrap import create_application, initialize_logger, load_theme
from app.dependencies import container
from ui.main_window import MainWindow


def main():
    """程序主入口"""
    # 创建应用实例
    app = create_application()

    # 初始化日志
    logger = initialize_logger(container.get_config_manager())

    # 加载主题
    load_theme(app)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    logger.info("主窗口已显示")

    # 运行应用
    exit_code = app.exec()

    logger.info(f"应用程序退出, 退出码: {exit_code}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
