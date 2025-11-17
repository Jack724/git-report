"""
Git 仓库扫描器模块
自动扫描目录下的所有 Git 仓库
"""
import os
from dataclasses import dataclass
from typing import List, Tuple
from git import Repo


@dataclass
class RepoInfo:
    """仓库信息数据类"""
    name: str           # 仓库名称(目录名)
    path: str           # 仓库完整路径
    author_name: str    # 从 git config 读取的作者名
    author_email: str   # 从 git config 读取的作者邮箱
    depth: int          # 相对于扫描根目录的深度
    parent_path: str    # 父目录路径


class RepoScanner:
    """Git 仓库扫描器"""

    def __init__(self):
        """初始化扫描器"""
        self.repos_found = []
        self.dirs_scanned = 0
        self.stopped = False

    def scan_directory(self, root_path: str, max_depth: int = 3) -> List[RepoInfo]:
        """
        扫描目录,查找所有 Git 仓库

        Args:
            root_path: 根目录路径
            max_depth: 最大扫描深度(默认3层)

        Returns:
            仓库信息列表
        """
        if not os.path.exists(root_path):
            raise ValueError(f"路径不存在: {root_path}")

        if not os.path.isdir(root_path):
            raise ValueError(f"路径不是目录: {root_path}")

        # 重置状态
        self.repos_found = []
        self.dirs_scanned = 0
        self.stopped = False

        # 开始递归扫描
        self._scan_recursive(root_path, 0, max_depth, root_path)

        return self.repos_found

    def stop(self):
        """停止扫描"""
        self.stopped = True

    def _is_git_repo(self, path: str) -> bool:
        """
        判断是否为 Git 仓库

        Args:
            path: 目录路径

        Returns:
            是否为 Git 仓库
        """
        git_dir = os.path.join(path, '.git')
        return os.path.isdir(git_dir)

    def _get_repo_author_info(self, repo_path: str) -> Tuple[str, str]:
        """
        从 git config 读取作者信息

        Args:
            repo_path: 仓库路径

        Returns:
            (author_name, author_email) 元组
        """
        try:
            repo = Repo(repo_path)
            reader = repo.config_reader()

            # 尝试读取 user.name 和 user.email
            name = reader.get_value("user", "name", default="")
            email = reader.get_value("user", "email", default="")

            return (name, email)
        except Exception as e:
            # 如果读取失败,返回空字符串
            print(f"读取 git config 失败 ({repo_path}): {e}")
            return ("", "")

    def _scan_recursive(self, path: str, current_depth: int, max_depth: int, root_path: str):
        """
        递归扫描目录

        Args:
            path: 当前扫描路径
            current_depth: 当前深度
            max_depth: 最大深度
            root_path: 根目录路径(用于计算相对深度)
        """
        # 检查是否已停止
        if self.stopped:
            return

        # 检查深度限制
        if current_depth > max_depth:
            return

        try:
            # 检查当前目录是否为 Git 仓库
            if self._is_git_repo(path):
                # 读取作者信息
                author_name, author_email = self._get_repo_author_info(path)

                # 创建仓库信息
                repo_info = RepoInfo(
                    name=os.path.basename(path),
                    path=path,
                    author_name=author_name,
                    author_email=author_email,
                    depth=current_depth,
                    parent_path=os.path.dirname(path)
                )

                self.repos_found.append(repo_info)

                # 找到 Git 仓库后,不再继续扫描其子目录
                return

            # 扫描子目录
            self.dirs_scanned += 1

            try:
                items = os.listdir(path)
            except PermissionError:
                # 跳过无权限的目录
                print(f"跳过无权限目录: {path}")
                return

            for item in items:
                # 检查是否已停止
                if self.stopped:
                    return

                subpath = os.path.join(path, item)

                # 跳过符号链接(避免死循环)
                if os.path.islink(subpath):
                    continue

                # 只处理目录
                if os.path.isdir(subpath):
                    # 跳过隐藏目录(除了扫描根目录)
                    if item.startswith('.') and subpath != root_path:
                        continue

                    # 递归扫描
                    self._scan_recursive(subpath, current_depth + 1, max_depth, root_path)

        except Exception as e:
            # 记录错误但继续扫描
            print(f"扫描目录出错 ({path}): {e}")

    def get_progress(self) -> Tuple[int, int]:
        """
        获取扫描进度

        Returns:
            (已找到的仓库数, 已扫描的目录数)
        """
        return (len(self.repos_found), self.dirs_scanned)
