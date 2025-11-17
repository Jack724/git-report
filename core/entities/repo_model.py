"""
仓库实体模型
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RepoConfig:
    """仓库配置实体"""

    name: str
    path: str
    type: str = "local"
    enabled: bool = True

    def __post_init__(self):
        """验证数据"""
        if not self.name:
            raise ValueError("仓库名称不能为空")
        if not self.path:
            raise ValueError("仓库路径不能为空")
        if self.type not in ["local", "remote"]:
            raise ValueError(f"无效的仓库类型: {self.type}")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.name,
            "path": self.path,
            "type": self.type,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RepoConfig':
        """从字典创建"""
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            type=data.get("type", "local"),
            enabled=data.get("enabled", True)
        )


@dataclass
class AuthorConfig:
    """作者配置实体"""

    name: str
    email: Optional[str] = None

    def __post_init__(self):
        """验证数据"""
        if not self.name:
            raise ValueError("作者名称不能为空")

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {"name": self.name}
        if self.email:
            result["email"] = self.email
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'AuthorConfig':
        """从字典创建"""
        return cls(
            name=data.get("name", ""),
            email=data.get("email")
        )
