"""
依赖注入容器
管理全局服务实例
"""
from infrastructure.config_manager import ConfigManager
from infrastructure.logger import get_logger
from core.services.git_service import GitService
from core.services.formatter import DataFormatter
from infrastructure.ai_client import AiClientFactory


class ServiceContainer:
    """服务容器 - 单例模式管理全局依赖"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # 基础服务
            self.config_manager = ConfigManager()
            self.logger = get_logger()

            # 领域服务
            self.git_service = GitService()
            self.formatter = DataFormatter()

            # AI 客户端工厂
            self.ai_client_factory = AiClientFactory()

            self._initialized = True

    def get_config_manager(self) -> ConfigManager:
        """获取配置管理器"""
        return self.config_manager

    def get_logger(self):
        """获取日志实例"""
        return self.logger

    def get_git_service(self) -> GitService:
        """获取 Git 服务"""
        return self.git_service

    def get_formatter(self) -> DataFormatter:
        """获取数据格式化器"""
        return self.formatter

    def get_ai_client_factory(self) -> AiClientFactory:
        """获取 AI 客户端工厂"""
        return self.ai_client_factory


# 全局容器实例
container = ServiceContainer()
