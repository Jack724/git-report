"""
日志系统模块
提供统一的日志记录功能
"""
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from utils.resource_path import get_data_path


class AppLogger:
    """应用日志管理器"""

    _instance = None
    _logger = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化日志系统"""
        if self._logger is not None:
            return

        # 创建日志目录（支持打包环境）
        log_dir = get_data_path("logs")

        # 创建logger
        self._logger = logging.getLogger("git-report")
        self._logger.setLevel(logging.DEBUG)  # 设置最低级别,后续通过handler控制

        # 避免重复添加handler
        if self._logger.handlers:
            return

        # 按日期命名的日志文件
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{today}.log")

        # 文件处理器 - 详细日志
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=7,  # 保留7个备份
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # 控制台处理器 - 只显示INFO及以上
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        # 添加处理器
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

        # 记录启动
        self._logger.info("=" * 50)
        self._logger.info("Git报告生成器启动")
        self._logger.info(f"日志文件: {log_file}")
        self._logger.info("=" * 50)

    def set_level(self, level: str):
        """
        设置日志级别

        Args:
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }

        log_level = level_map.get(level.upper(), logging.INFO)

        # 更新所有处理器的级别（包括文件和控制台）
        for handler in self._logger.handlers:
            handler.setLevel(log_level)

        self._logger.info(f"日志级别已设置为: {level}")

    def get_logger(self):
        """获取logger实例"""
        return self._logger

    def debug(self, message: str):
        """调试日志"""
        self._logger.debug(message)

    def info(self, message: str):
        """信息日志"""
        self._logger.info(message)

    def warning(self, message: str):
        """警告日志"""
        self._logger.warning(message)

    def error(self, message: str, exc_info=False):
        """错误日志"""
        self._logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info=False):
        """严重错误日志"""
        self._logger.critical(message, exc_info=exc_info)


# 全局日志实例
logger = AppLogger()


def get_logger():
    """获取全局日志实例"""
    return logger
