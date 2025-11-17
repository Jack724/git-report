"""
数据格式化模块
负责对提交记录进行分类和格式化
"""
import re
from typing import List, Dict
from collections import defaultdict
from core.services.git_service import CommitRecord


class DataFormatter:
    """数据格式化器"""

    # 提交类型映射
    COMMIT_TYPES = {
        'feat': '新功能',
        'fix': '修复',
        'refactor': '重构',
        'docs': '文档',
        'test': '测试',
        'chore': '杂项',
        'style': '样式',
        'perf': '性能优化'
    }

    # 需要过滤的噪声提交关键词
    NOISE_KEYWORDS = [
        'merge', 'sync', 'update readme', 'update version',
        'bump version', 'initial commit', 'wip'
    ]

    def __init__(self):
        """初始化格式化器"""
        pass

    def classify_commit(self, message: str) -> str:
        """
        分类提交类型

        Args:
            message: 提交消息

        Returns:
            提交类型(feat/fix/other)
        """
        message_lower = message.lower().strip()

        # 检查是否符合 Conventional Commits 格式
        # 格式: type(scope): description 或 type: description
        match = re.match(r'^(\w+)(\(.+?\))?:\s*(.+)', message)
        if match:
            commit_type = match.group(1).lower()
            if commit_type in self.COMMIT_TYPES:
                return commit_type

        # 简单的关键词匹配
        if any(keyword in message_lower for keyword in ['feat', 'feature', '新增', '添加']):
            return 'feat'
        elif any(keyword in message_lower for keyword in ['fix', 'bug', '修复', '修正']):
            return 'fix'
        elif any(keyword in message_lower for keyword in ['refactor', '重构']):
            return 'refactor'
        elif any(keyword in message_lower for keyword in ['docs', 'doc', '文档']):
            return 'docs'
        elif any(keyword in message_lower for keyword in ['test', '测试']):
            return 'test'
        elif any(keyword in message_lower for keyword in ['perf', 'performance', '性能']):
            return 'perf'

        return 'other'

    def is_noise_commit(self, message: str) -> bool:
        """
        判断是否为噪声提交

        Args:
            message: 提交消息

        Returns:
            是否为噪声提交
        """
        message_lower = message.lower().strip()
        return any(keyword in message_lower for keyword in self.NOISE_KEYWORDS)

    def format_commits(self, commits: List[CommitRecord], filter_noise: bool = True) -> str:
        """
        格式化提交记录为文本摘要

        Args:
            commits: 提交记录列表
            filter_noise: 是否过滤噪声提交

        Returns:
            格式化后的文本摘要
        """
        if not commits:
            return "没有找到提交记录"

        # 过滤噪声提交
        if filter_noise:
            commits = [c for c in commits if not self.is_noise_commit(c.message)]

        if not commits:
            return "过滤噪声后没有有效提交记录"

        # 按类型分组
        grouped = defaultdict(list)
        for commit in commits:
            commit_type = self.classify_commit(commit.message)
            grouped[commit_type].append(commit)

        # 统计信息
        summary_lines = ["【提交统计】"]
        summary_lines.append(f"总计: {len(commits)} 个提交")

        # 统计涉及的仓库
        repos = set(c.repo_name for c in commits if c.repo_name)
        if repos:
            summary_lines.append(f"涉及仓库: {len(repos)} 个 ({', '.join(sorted(repos))})")

        for commit_type, type_commits in sorted(grouped.items()):
            type_name = self.COMMIT_TYPES.get(commit_type, '其他')
            summary_lines.append(f"{type_name}({commit_type}): {len(type_commits)} 个")

        # 详细提交记录
        summary_lines.append("\n【详细提交记录】")

        # 按类型输出
        for commit_type in ['feat', 'fix', 'refactor', 'docs', 'perf', 'test', 'other']:
            if commit_type not in grouped:
                continue

            type_name = self.COMMIT_TYPES.get(commit_type, '其他')
            summary_lines.append(f"\n## {type_name}")

            for commit in grouped[commit_type]:
                # 格式: [日期] [仓库] 作者: 消息
                date_str = commit.date.strftime('%Y-%m-%d')
                # 清理提交消息(去掉 type: 前缀)
                clean_message = re.sub(r'^\w+(\(.+?\))?:\s*', '', commit.message)
                # 只取第一行
                clean_message = clean_message.split('\n')[0]
                # 包含仓库名称(如果有)
                repo_tag = f"[{commit.repo_name}] " if commit.repo_name else ""
                summary_lines.append(f"[{date_str}] {repo_tag}{commit.author}: {clean_message}")

        return '\n'.join(summary_lines)

    def get_statistics(self, commits: List[CommitRecord]) -> Dict[str, int]:
        """
        获取提交统计信息

        Args:
            commits: 提交记录列表

        Returns:
            统计字典 {type: count}
        """
        stats = defaultdict(int)
        for commit in commits:
            if not self.is_noise_commit(commit.message):
                commit_type = self.classify_commit(commit.message)
                stats[commit_type] += 1

        return dict(stats)
