"""
Git 服务模块
负责从 Git 仓库提取提交记录
"""
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from git import Repo, GitCommandError


@dataclass
class CommitRecord:
    """提交记录数据类"""
    hash: str
    author: str
    email: str
    date: datetime
    message: str
    repo_name: str = ""  # 仓库名称
    repo_path: str = ""  # 仓库路径


class GitService:
    """Git 服务类"""

    def __init__(self, repo_path: str, repo_name: str = ""):
        """
        初始化 Git 服务

        Args:
            repo_path: Git 仓库路径
            repo_name: 仓库名称(可选)

        Raises:
            ValueError: 如果路径不是有效的 Git 仓库
        """
        self.repo_path = repo_path
        self.repo_name = repo_name or os.path.basename(repo_path)
        self._validate_repo()

    def _validate_repo(self) -> None:
        """
        验证仓库路径有效性

        Raises:
            ValueError: 如果路径不是有效的 Git 仓库
        """
        if not os.path.exists(self.repo_path):
            raise ValueError(f"仓库路径不存在: {self.repo_path}")

        if not os.path.isdir(self.repo_path):
            raise ValueError(f"路径不是目录: {self.repo_path}")

        try:
            Repo(self.repo_path)
        except Exception as e:
            raise ValueError(f"不是有效的 Git 仓库: {self.repo_path}, 错误: {e}")

    def get_commits(
        self,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CommitRecord]:
        """
        获取提交记录

        Args:
            author_name: 作者姓名(可选)
            author_email: 作者邮箱(可选)
            start_date: 开始日期(可选)
            end_date: 结束日期(可选)

        Returns:
            提交记录列表

        Raises:
            GitCommandError: Git 命令执行失败
        """
        try:
            repo = Repo(self.repo_path)
            commits = []

            # 检查仓库是否有提交
            try:
                repo.head.commit
            except Exception:
                # 空仓库,没有提交
                return commits

            # 构建 git log 参数
            kwargs = {}
            if start_date and end_date:
                kwargs['after'] = start_date.strftime('%Y-%m-%d')
                kwargs['before'] = end_date.strftime('%Y-%m-%d')
            elif start_date:
                kwargs['after'] = start_date.strftime('%Y-%m-%d')
            elif end_date:
                kwargs['before'] = end_date.strftime('%Y-%m-%d')

            # 获取所有提交
            for commit in repo.iter_commits(**kwargs):
                # 过滤作者
                if author_name and commit.author.name != author_name:
                    continue
                if author_email and commit.author.email != author_email:
                    continue

                # 创建提交记录
                record = CommitRecord(
                    hash=commit.hexsha,
                    author=commit.author.name,
                    email=commit.author.email,
                    date=datetime.fromtimestamp(commit.committed_date),
                    message=commit.message.strip(),
                    repo_name=self.repo_name,
                    repo_path=self.repo_path
                )
                commits.append(record)

            return commits

        except GitCommandError as e:
            raise GitCommandError(f"获取提交记录失败: {e}")

    def get_authors(self) -> List[tuple]:
        """
        获取仓库中所有作者信息

        Returns:
            作者列表 [(name, email), ...]
        """
        try:
            repo = Repo(self.repo_path)
            authors = set()

            for commit in repo.iter_commits():
                authors.add((commit.author.name, commit.author.email))

            return sorted(list(authors))

        except Exception as e:
            print(f"获取作者列表失败: {e}")
            return []
