"""
AI 客户端模块
负责调用大模型 API 生成报告
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from infrastructure.config_manager import ConfigManager
    from infrastructure.adapters.base import BaseAdapter


class AiClient:
    """AI 客户端基类 (向后兼容,已废弃)"""

    def generate_report(self, commit_summary: str) -> str:
        """
        生成报告

        Args:
            commit_summary: 提交摘要

        Returns:
            生成的报告文本
        """
        raise NotImplementedError


class AiClientFactory:
    """AI 客户端工厂"""

    ADAPTERS = {
        'openai': ('infrastructure.adapters.openai_adapter', 'OpenAIAdapter'),
        'deepseek': ('infrastructure.adapters.deepseek_adapter', 'DeepseekAdapter'),
        'zhipu': ('infrastructure.adapters.zhipu_adapter', 'ZhipuAdapter'),
    }

    @staticmethod
    def create(config_manager: 'ConfigManager') -> 'BaseAdapter':
        """
        根据配置创建 AI 适配器

        Args:
            config_manager: 配置管理器

        Returns:
            AI 适配器实例

        Raises:
            ValueError: 配置错误或不支持的平台
        """
        from infrastructure.config_manager import ConfigManager

        # 获取当前选中的平台
        provider = config_manager.get('ai.provider', 'openai')

        # 获取 System Prompt 和 User Prompt
        system_prompt = config_manager.get('ai.system_prompt', ConfigManager.DEFAULT_SYSTEM_PROMPT)
        user_prompt = config_manager.get('ai.user_prompt', ConfigManager.DEFAULT_USER_PROMPT)

        # 向后兼容: 如果没有 system_prompt/user_prompt，使用旧的 prompt
        if not user_prompt:
            user_prompt = config_manager.get('ai.prompt', ConfigManager.DEFAULT_PROMPT)

        # 获取报告示例和启用状态
        report_example = config_manager.get('ai.report_example', '')
        use_example = config_manager.get('ai.use_example', False)

        # 获取 temperature 参数
        temperature = config_manager.get('ai.temperature', 0.7)

        # 获取平台特定配置
        provider_config = config_manager.get(f'ai.configs.{provider}', {})

        if not provider_config:
            raise ValueError(
                f"未找到 {provider} 的配置信息。\n"
                f"请点击 'AI 设置' 按钮配置 {provider} 平台的 API Key 和模型。"
            )

        # 检查是否为支持的平台
        if provider not in AiClientFactory.ADAPTERS:
            supported = ', '.join(AiClientFactory.ADAPTERS.keys())
            raise ValueError(f"不支持的 AI 平台: {provider}。支持的平台: {supported}")

        # 动态导入适配器类
        module_path, class_name = AiClientFactory.ADAPTERS[provider]

        try:
            module = __import__(module_path, fromlist=[class_name])
            adapter_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"无法加载 {provider} 适配器: {str(e)}")

        # 创建适配器实例
        try:
            return adapter_class(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                report_example=report_example,
                use_example=use_example,
                temperature=temperature,
                **provider_config
            )
        except TypeError as e:
            raise ValueError(f"创建 {provider} 适配器失败,配置参数错误: {str(e)}")
