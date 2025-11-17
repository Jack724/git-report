"""
提交记录实体模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CommitRecord:
    """提交记录实体"""

    repo: str
    hash: str
    author: str
    date: datetime
    message: str
    category: Optional[str] = None

    def __post_init__(self):
        """验证数据"""
        if not self.repo:
            raise ValueError("仓库名称不能为空")
        if not self.hash:
            raise ValueError("提交哈希不能为空")
        if not self.author:
            raise ValueError("作者名称不能为空")
        if not isinstance(self.date, datetime):
            raise ValueError("日期必须是 datetime 类型")
        if not self.message:
            raise ValueError("提交消息不能为空")

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {
            "repo": self.repo,
            "hash": self.hash,
            "author": self.author,
            "date": self.date.isoformat(),
            "message": self.message
        }
        if self.category:
            result["category"] = self.category
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'CommitRecord':
        """从字典创建"""
        date = data.get("date")
        if isinstance(date, str):
            date = datetime.fromisoformat(date)

        return cls(
            repo=data.get("repo", ""),
            hash=data.get("hash", ""),
            author=data.get("author", ""),
            date=date,
            message=data.get("message", ""),
            category=data.get("category")
        )

    def get_short_hash(self, length: int = 7) -> str:
        """获取短哈希"""
        return self.hash[:length]

    def get_formatted_date(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取格式化日期"""
        return self.date.strftime(format)
