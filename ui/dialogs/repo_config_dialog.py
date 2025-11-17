"""
仓库配置对话框
用于添加和编辑仓库配置
"""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from core.services.git_service import GitService


class RepoConfigDialog(QDialog):
    """仓库配置对话框"""

    def __init__(self, parent=None, repo_config: dict = None):
        """
        初始化对话框

        Args:
            parent: 父窗口
            repo_config: 仓库配置字典(编辑模式), None 表示新建模式
        """
        super().__init__(parent)
        self.repo_config = repo_config
        self.is_edit_mode = repo_config is not None

        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化UI"""
        title = "编辑仓库" if self.is_edit_mode else "添加仓库"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # 表单布局
        form_layout = QFormLayout()

        # 仓库名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: Git-Report 主项目")
        form_layout.addRow("仓库名称:", self.name_input)

        # 仓库路径
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("选择 Git 仓库目录...")
        path_layout.addWidget(self.path_input)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_repo_path)
        path_layout.addWidget(browse_btn)

        form_layout.addRow("仓库路径:", path_layout)

        # 作者名称
        self.author_name_input = QLineEdit()
        self.author_name_input.setPlaceholderText("筛选此作者的提交(可选)")
        form_layout.addRow("作者名称:", self.author_name_input)

        # 作者邮箱
        self.author_email_input = QLineEdit()
        self.author_email_input.setPlaceholderText("筛选此邮箱的提交(可选)")
        form_layout.addRow("作者邮箱:", self.author_email_input)

        # 启用状态
        self.enabled_checkbox = QCheckBox("启用此仓库")
        self.enabled_checkbox.setChecked(True)
        form_layout.addRow("状态:", self.enabled_checkbox)

        layout.addLayout(form_layout)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_config(self):
        """加载配置到界面"""
        if self.repo_config:
            self.name_input.setText(self.repo_config.get('name', ''))
            self.path_input.setText(self.repo_config.get('path', ''))
            self.author_name_input.setText(self.repo_config.get('author_name', ''))
            self.author_email_input.setText(self.repo_config.get('author_email', ''))
            self.enabled_checkbox.setChecked(self.repo_config.get('enabled', True))

    def browse_repo_path(self):
        """浏览选择仓库路径"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择 Git 仓库目录",
            self.path_input.text() or os.path.expanduser("~")
        )

        if directory:
            self.path_input.setText(directory)
            # 如果名称为空,使用目录名作为默认名称
            if not self.name_input.text():
                self.name_input.setText(os.path.basename(directory))

    def validate_and_accept(self):
        """验证输入并接受"""
        # 验证必填字段
        name = self.name_input.text().strip()
        path = self.path_input.text().strip()

        if not name:
            QMessageBox.warning(self, "输入错误", "请输入仓库名称")
            self.name_input.setFocus()
            return

        if not path:
            QMessageBox.warning(self, "输入错误", "请选择仓库路径")
            self.path_input.setFocus()
            return

        # 验证路径存在
        if not os.path.exists(path):
            QMessageBox.warning(self, "路径错误", f"路径不存在: {path}")
            return

        if not os.path.isdir(path):
            QMessageBox.warning(self, "路径错误", f"路径不是目录: {path}")
            return

        # 验证是否为有效的 Git 仓库
        try:
            GitService(path)
        except ValueError as e:
            QMessageBox.warning(self, "Git 仓库错误", str(e))
            return

        self.accept()

    def get_config(self) -> dict:
        """
        获取配置

        Returns:
            配置字典
        """
        return {
            'name': self.name_input.text().strip(),
            'path': self.path_input.text().strip(),
            'author_name': self.author_name_input.text().strip(),
            'author_email': self.author_email_input.text().strip(),
            'enabled': self.enabled_checkbox.isChecked()
        }
