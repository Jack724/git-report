"""
AI 适配器模块
提供统一的 AI 接口抽象和多平台适配器实现
"""

from infrastructure.adapters.base import BaseAdapter
from infrastructure.adapters.openai_adapter import OpenAIAdapter
from infrastructure.adapters.deepseek_adapter import DeepseekAdapter
from infrastructure.adapters.zhipu_adapter import ZhipuAdapter

__all__ = [
    'BaseAdapter',
    'OpenAIAdapter',
    'DeepseekAdapter',
    'ZhipuAdapter',
]
