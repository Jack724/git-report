"""
仓库详情对话框
显示仓库基本信息和最近提交
"""
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from core.services.git_service import GitService


class RepoDetailDialog(QDialog):
    """仓库详情对话框"""

    def __init__(self, parent=None, repo_config: dict = None):
        """
        初始化对话框

        Args:
            parent: 父窗口
            repo_config: 仓库配置字典
        """
        super().__init__(parent)
        self.repo_config = repo_config or {}

        self.init_ui()
        self.load_details()

    def init_ui(self):
        """初始化UI"""
        repo_name = self.repo_config.get('name', '未知仓库')
        self.setWindowTitle(f"仓库详情 - {repo_name}")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()

        # 基本信息组
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()

        self.name_label = QLabel()
        info_layout.addRow("仓库名称:", self.name_label)

        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        info_layout.addRow("仓库路径:", self.path_label)

        self.author_name_label = QLabel()
        info_layout.addRow("作者名称:", self.author_name_label)

        self.author_email_label = QLabel()
        info_layout.addRow("作者邮箱:", self.author_email_label)

        self.enabled_label = QLabel()
        info_layout.addRow("状态:", self.enabled_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 最近提交组
        commits_group = QGroupBox("最近提交 (最近7天)")
        commits_layout = QVBoxLayout()

        self.commits_text = QTextEdit()
        self.commits_text.setReadOnly(True)
        self.commits_text.setMinimumHeight(250)
        commits_layout.addWidget(self.commits_text)

        commits_group.setLayout(commits_layout)
        layout.addWidget(commits_group)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_details(self):
        """加载仓库详情"""
        # 加载基本信息
        self.name_label.setText(self.repo_config.get('name', '-'))
        self.path_label.setText(self.repo_config.get('path', '-'))

        author_name = self.repo_config.get('author_name', '')
        self.author_name_label.setText(author_name if author_name else '(未设置)')

        author_email = self.repo_config.get('author_email', '')
        self.author_email_label.setText(author_email if author_email else '(未设置)')

        enabled = self.repo_config.get('enabled', True)
        self.enabled_label.setText("已启用" if enabled else "未启用")

        # 加载最近提交
        self.load_recent_commits()

    def load_recent_commits(self):
        """加载最近提交记录"""
        try:
            repo_path = self.repo_config.get('path', '')
            if not repo_path:
                self.commits_text.setPlainText("仓库路径未配置")
                return

            # 创建 GitService
            git_service = GitService(repo_path)

            # 获取最近7天的提交
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            author_name = self.repo_config.get('author_name')
            author_email = self.repo_config.get('author_email')

            commits = git_service.get_commits(
                author_name=author_name if author_name else None,
                author_email=author_email if author_email else None,
                start_date=start_date,
                end_date=end_date
            )

            # 限制显示最多5条
            commits = commits[:5]

            if not commits:
                self.commits_text.setPlainText("最近7天没有提交记录")
                return

            # 格式化显示
            lines = []
            lines.append(f"共找到 {len(commits)} 条提交 (显示最新5条):\n")

            for commit in commits:
                date_str = commit.date.strftime('%Y-%m-%d %H:%M')
                message = commit.message.split('\n')[0]  # 只显示第一行
                if len(message) > 60:
                    message = message[:60] + '...'

                lines.append(f"[{date_str}]")
                lines.append(f"  {commit.author} <{commit.email}>")
                lines.append(f"  {message}")
                lines.append(f"  Hash: {commit.hash[:8]}")
                lines.append("")

            self.commits_text.setPlainText('\n'.join(lines))

        except Exception as e:
            self.commits_text.setPlainText(f"加载提交记录失败: {str(e)}")
