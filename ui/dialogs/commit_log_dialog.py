"""
提交日志查看对话框
按不同维度展示提交记录
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QTabWidget, QWidget, QFileDialog, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from qfluentwidgets import PushButton, PrimaryPushButton, TextBrowser, MessageBox, InfoBar, InfoBarPosition
from typing import List
from collections import defaultdict
from infrastructure.logger import get_logger
from core.services.git_service import CommitRecord
from core.services.formatter import DataFormatter

logger = get_logger()


class CommitLogDialog(QDialog):
    """提交日志查看对话框"""

    def __init__(self, commits: List[CommitRecord], parent=None):
        """
        初始化对话框

        Args:
            commits: 提交记录列表
            parent: 父窗口
        """
        super().__init__(parent)
        self.commits = commits
        self.formatter = DataFormatter()

        # 生成三种不同视图的日志
        self.log_by_type = self.generate_by_type()
        self.log_by_repo = self.generate_by_repo()
        self.log_by_timeline = self.generate_by_timeline()

        self.init_ui()

    def generate_by_type(self) -> str:
        """
        按 Conventional Commits 类型分类展示

        Returns:
            格式化后的日志文本
        """
        if not self.commits:
            return "暂无提交记录"

        lines = ["【按提交类型分类】\n"]

        # 按类型分组
        grouped = defaultdict(list)
        for commit in self.commits:
            commit_type = self.formatter.classify_commit(commit.message)
            grouped[commit_type].append(commit)

        # 统计信息
        lines.append(f"总提交数: {len(self.commits)} 条\n")

        # 按预定义顺序输出各类型
        type_order = ['feat', 'fix', 'refactor', 'docs', 'perf', 'test', 'chore', 'style', 'other']
        for commit_type in type_order:
            if commit_type not in grouped:
                continue

            type_name = self.formatter.COMMIT_TYPES.get(commit_type, '其他')
            commits_of_type = grouped[commit_type]
            lines.append(f"\n{'='*70}")
            lines.append(f"## {type_name} ({commit_type}) - {len(commits_of_type)} 条")
            lines.append('='*70 + '\n')

            for commit in commits_of_type:
                date_str = commit.date.strftime('%Y-%m-%d %H:%M:%S')
                repo_tag = f"[{commit.repo_name}] " if commit.repo_name else ""
                lines.append(f"📅 {date_str}")
                lines.append(f"📦 {repo_tag}作者: {commit.author} <{commit.email}>")
                lines.append(f"💬 {commit.message}")
                lines.append(f"🔗 {commit.hash[:8]}")
                lines.append("")

        return '\n'.join(lines)

    def generate_by_repo(self) -> str:
        """
        按仓库分组展示

        Returns:
            格式化后的日志文本
        """
        if not self.commits:
            return "暂无提交记录"

        lines = ["【按仓库分组】\n"]

        # 按仓库分组
        grouped = defaultdict(list)
        for commit in self.commits:
            repo_name = commit.repo_name or "未知仓库"
            grouped[repo_name].append(commit)

        lines.append(f"总提交数: {len(self.commits)} 条")
        lines.append(f"涉及仓库: {len(grouped)} 个\n")

        # 按仓库名称排序输出
        for repo_name in sorted(grouped.keys()):
            commits_in_repo = grouped[repo_name]
            lines.append(f"\n{'='*70}")
            lines.append(f"## 仓库: {repo_name} - {len(commits_in_repo)} 条提交")
            lines.append('='*70 + '\n')

            # 仓库内按日期降序排序
            commits_in_repo.sort(key=lambda c: c.date, reverse=True)

            for commit in commits_in_repo:
                date_str = commit.date.strftime('%Y-%m-%d %H:%M:%S')
                commit_type = self.formatter.classify_commit(commit.message)
                type_name = self.formatter.COMMIT_TYPES.get(commit_type, '其他')

                lines.append(f"📅 {date_str} | 🏷️  {type_name}")
                lines.append(f"👤 {commit.author} <{commit.email}>")
                lines.append(f"💬 {commit.message}")
                lines.append(f"🔗 {commit.hash[:8]}")
                lines.append("")

        return '\n'.join(lines)

    def generate_by_timeline(self) -> str:
        """
        按时间线展示（时间降序）

        Returns:
            格式化后的日志文本
        """
        if not self.commits:
            return "暂无提交记录"

        lines = ["【按时间线排序】\n"]

        # 按日期降序排序
        sorted_commits = sorted(self.commits, key=lambda c: c.date, reverse=True)

        lines.append(f"总提交数: {len(self.commits)} 条")

        # 获取日期范围
        if sorted_commits:
            latest = sorted_commits[0].date
            earliest = sorted_commits[-1].date
            lines.append(f"时间范围: {earliest.strftime('%Y-%m-%d')} 至 {latest.strftime('%Y-%m-%d')}\n")

        # 按日期分组
        by_date = defaultdict(list)
        for commit in sorted_commits:
            date_key = commit.date.strftime('%Y-%m-%d')
            by_date[date_key].append(commit)

        # 按日期输出
        for date_key in sorted(by_date.keys(), reverse=True):
            commits_on_date = by_date[date_key]
            lines.append(f"\n{'='*70}")
            lines.append(f"## 📅 {date_key} ({self._get_weekday(date_key)}) - {len(commits_on_date)} 条提交")
            lines.append('='*70 + '\n')

            for commit in commits_on_date:
                time_str = commit.date.strftime('%H:%M:%S')
                commit_type = self.formatter.classify_commit(commit.message)
                type_name = self.formatter.COMMIT_TYPES.get(commit_type, '其他')
                repo_tag = f"[{commit.repo_name}] " if commit.repo_name else ""

                lines.append(f"⏰ {time_str} | 🏷️  {type_name} | 📦 {repo_tag}{commit.author}")
                lines.append(f"💬 {commit.message}")
                lines.append(f"🔗 {commit.hash[:8]}")
                lines.append("")

        return '\n'.join(lines)

    def _get_weekday(self, date_str: str) -> str:
        """获取星期几"""
        from datetime import datetime
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return weekdays[date_obj.weekday()]
        except:
            return ""

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("查看提交日志详情")
        self.resize(950, 750)

        layout = QVBoxLayout()

        # 创建Tab Widget
        self.tab_widget = QTabWidget()

        # === Tab 1: 按类型展示 ===
        type_tab = QWidget()
        type_layout = QVBoxLayout()

        self.type_browser = TextBrowser()
        self.type_browser.setFont(QFont("Consolas", 9))
        self.type_browser.setPlainText(self.log_by_type)
        type_layout.addWidget(self.type_browser)

        type_tab.setLayout(type_layout)
        self.tab_widget.addTab(type_tab, "🏷️  按类型")

        # === Tab 2: 按仓库展示 ===
        repo_tab = QWidget()
        repo_layout = QVBoxLayout()

        self.repo_browser = TextBrowser()
        self.repo_browser.setFont(QFont("Consolas", 9))
        self.repo_browser.setPlainText(self.log_by_repo)
        repo_layout.addWidget(self.repo_browser)

        repo_tab.setLayout(repo_layout)
        self.tab_widget.addTab(repo_tab, "📦 按仓库")

        # === Tab 3: 按时间线展示 ===
        timeline_tab = QWidget()
        timeline_layout = QVBoxLayout()

        self.timeline_browser = TextBrowser()
        self.timeline_browser.setFont(QFont("Consolas", 9))
        self.timeline_browser.setPlainText(self.log_by_timeline)
        timeline_layout.addWidget(self.timeline_browser)

        timeline_tab.setLayout(timeline_layout)
        self.tab_widget.addTab(timeline_tab, "📅 按时间线")

        layout.addWidget(self.tab_widget)

        # === 按钮区域 ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 复制全部按钮
        self.copy_btn = PushButton("📋 复制当前视图")
        self.copy_btn.clicked.connect(self.copy_all)
        button_layout.addWidget(self.copy_btn)

        # 导出按钮
        self.export_btn = PushButton("💾 导出为文件")
        self.export_btn.clicked.connect(self.export_to_file)
        button_layout.addWidget(self.export_btn)

        # 关闭按钮
        self.close_btn = PrimaryPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def copy_all(self):
        """复制当前视图内容到剪贴板"""
        current_index = self.tab_widget.currentIndex()

        if current_index == 0:
            content = self.log_by_type
            log_type = "按类型分类"
        elif current_index == 1:
            content = self.log_by_repo
            log_type = "按仓库分组"
        else:
            content = self.log_by_timeline
            log_type = "按时间线"

        clipboard = QApplication.clipboard()
        clipboard.setText(content)

        logger.info(f"已复制{log_type}视图到剪贴板")
        InfoBar.success(
            title="成功",
            content=f"{log_type}视图已复制到剪贴板",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def export_to_file(self):
        """导出当前视图日志到文件"""
        current_index = self.tab_widget.currentIndex()

        if current_index == 0:
            content = self.log_by_type
            default_name = "提交日志-按类型.txt"
        elif current_index == 1:
            content = self.log_by_repo
            default_name = "提交日志-按仓库.txt"
        else:
            content = self.log_by_timeline
            default_name = "提交日志-按时间线.txt"

        # 打开保存文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出日志文件",
            default_name,
            "文本文件 (*.txt);;所有文件 (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"日志已导出到: {file_path}")
                InfoBar.success(
                    title="成功",
                    content=f"日志已成功导出",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            except Exception as e:
                logger.error(f"导出日志失败: {e}", exc_info=True)
                MessageBox("错误", f"导出失败: {str(e)}", self).exec()
