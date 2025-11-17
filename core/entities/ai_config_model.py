"""
AI 配置实体模型
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AiConfig:
    """AI 配置实体"""

    provider: str
    api_key: str
    model: Optional[str] = None
    base_url: Optional[str] = None
    system_prompt: str = ""
    user_prompt: str = ""
    report_example: str = ""
    use_example: bool = False
    temperature: float = 0.7
    prompt_template: str = ""

    def __post_init__(self):
        """验证数据"""
        valid_providers = ["openai", "deepseek", "zhipu"]
        if self.provider not in valid_providers:
            raise ValueError(f"无效的 AI 提供商: {self.provider}, 支持: {valid_providers}")

        if not self.api_key:
            raise ValueError("API Key 不能为空")

        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError("Temperature 必须在 0.0-2.0 之间")

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {
            "provider": self.provider,
            "api_key": self.api_key,
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "report_example": self.report_example,
            "use_example": self.use_example,
            "temperature": self.temperature,
            "prompt_template": self.prompt_template
        }

        if self.model:
            result["model"] = self.model
        if self.base_url:
            result["base_url"] = self.base_url

        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'AiConfig':
        """从字典创建"""
        return cls(
            provider=data.get("provider", ""),
            api_key=data.get("api_key", ""),
            model=data.get("model"),
            base_url=data.get("base_url"),
            system_prompt=data.get("system_prompt", ""),
            user_prompt=data.get("user_prompt", ""),
            report_example=data.get("report_example", ""),
            use_example=data.get("use_example", False),
            temperature=data.get("temperature", 0.7),
            prompt_template=data.get("prompt_template", "")
        )

    def get_display_name(self) -> str:
        """获取显示名称"""
        provider_names = {
            "openai": "OpenAI GPT",
            "deepseek": "Deepseek Chat",
            "zhipu": "智谱 GLM"
        }
        return provider_names.get(self.provider, self.provider)
