"""
仓库列表组件
显示和管理仓库列表
"""
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import PushButton
from ui.dialogs.repo_config_dialog import RepoConfigDialog
from ui.dialogs.repo_detail_dialog import RepoDetailDialog
from ui.dialogs.repo_scan_dialog import RepoScanDialog


class RepoItemWidget(QWidget):
    """单个仓库项组件"""

    # 信号定义
    toggled = Signal(str, bool)  # repo_id, enabled
    detail_clicked = Signal(str)  # repo_id
    edit_clicked = Signal(str)  # repo_id
    delete_clicked = Signal(str)  # repo_id

    def __init__(self, repo_config: dict, parent=None):
        """
        初始化仓库项

        Args:
            repo_config: 仓库配置字典
            parent: 父组件
        """
        super().__init__(parent)
        self.repo_config = repo_config
        self.repo_id = repo_config.get('id', '')

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # 启用复选框
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.setChecked(self.repo_config.get('enabled', True))
        self.enabled_checkbox.stateChanged.connect(self.on_toggle)
        layout.addWidget(self.enabled_checkbox)

        # 仓库名称
        name_label = QLabel(self.repo_config.get('name', '未知仓库'))
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        # 原始仓库名称（如果与配置名称不一致）
        original_name = self._get_original_repo_name()
        config_name = self.repo_config.get('name', '未知仓库')
        if original_name and original_name != config_name:
            original_label = QLabel(f"({original_name})")
            original_label.setStyleSheet("color: gray; margin-left: 5px;")
            layout.addWidget(original_label)

        layout.addStretch()

        # 详情按钮
        detail_btn = PushButton("详情")
        detail_btn.setFixedWidth(60)
        detail_btn.clicked.connect(lambda: self.detail_clicked.emit(self.repo_id))
        layout.addWidget(detail_btn)

        # 编辑按钮
        edit_btn = PushButton("编辑")
        edit_btn.setFixedWidth(60)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.repo_id))
        layout.addWidget(edit_btn)

        # 删除按钮
        delete_btn = PushButton("删除")
        delete_btn.setFixedWidth(60)
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.repo_id))
        layout.addWidget(delete_btn)

        self.setLayout(layout)

        # 设置边框
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("RepoItemWidget { border: 1px solid #ccc; border-radius: 3px; }")

    def setFrameStyle(self, style):
        """设置框架样式(兼容性)"""
        pass

    def _get_original_repo_name(self) -> str:
        """
        获取仓库的原始名称（目录名）

        Returns:
            原始仓库名称
        """
        repo_path = self.repo_config.get('path', '')
        if repo_path:
            return os.path.basename(repo_path)
        return ''

    def on_toggle(self, state):
        """复选框状态改变"""
        enabled = (state == Qt.Checked)
        self.toggled.emit(self.repo_id, enabled)


class RepoListWidget(QWidget):
    """仓库列表组件"""

    # 信号定义
    repos_changed = Signal()  # 仓库列表变化

    def __init__(self, config_manager, parent=None):
        """
        初始化仓库列表

        Args:
            config_manager: 配置管理器
            parent: 父组件
        """
        super().__init__(parent)
        self.config_manager = config_manager

        self.init_ui()
        self.load_repos()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 标题和添加按钮
        header_layout = QHBoxLayout()

        title_label = QLabel("仓库列表:")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        add_btn = PushButton("添加仓库")
        add_btn.clicked.connect(self.add_repo)
        header_layout.addWidget(add_btn)

        # 批量扫描按钮
        scan_btn = PushButton("批量扫描")
        scan_btn.clicked.connect(self.batch_scan_repos)
        header_layout.addWidget(scan_btn)

        layout.addLayout(header_layout)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)

        # 仓库列表容器
        self.repo_container = QWidget()
        self.repo_layout = QVBoxLayout()
        self.repo_layout.setSpacing(5)
        self.repo_container.setLayout(self.repo_layout)

        scroll_area.setWidget(self.repo_container)
        layout.addWidget(scroll_area)

        # 统计信息
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: gray;")
        layout.addWidget(self.stats_label)

        self.setLayout(layout)

    def load_repos(self):
        """加载仓库列表"""
        # 清空现有列表
        while self.repo_layout.count():
            item = self.repo_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 获取仓库列表
        repos = self.config_manager.get_repos()

        if not repos:
            # 显示空状态
            empty_label = QLabel("暂无仓库,点击上方「添加仓库」按钮添加")
            empty_label.setStyleSheet("color: gray; padding: 20px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.repo_layout.addWidget(empty_label)
            self.update_stats(0, 0)
            return

        # 添加仓库项
        for repo in repos:
            repo_item = RepoItemWidget(repo)
            repo_item.toggled.connect(self.on_repo_toggled)
            repo_item.detail_clicked.connect(self.show_repo_detail)
            repo_item.edit_clicked.connect(self.edit_repo)
            repo_item.delete_clicked.connect(self.delete_repo)
            self.repo_layout.addWidget(repo_item)

        # 添加弹性空间
        self.repo_layout.addStretch()

        # 更新统计
        enabled_count = sum(1 for r in repos if r.get('enabled', True))
        self.update_stats(len(repos), enabled_count)

    def update_stats(self, total: int, enabled: int):
        """
        更新统计信息

        Args:
            total: 总仓库数
            enabled: 已启用仓库数
        """
        self.stats_label.setText(f"总计: {total} 个仓库, 已启用: {enabled} 个")

    def add_repo(self):
        """添加仓库"""
        dialog = RepoConfigDialog(self)
        if dialog.exec_():
            config = dialog.get_config()
            # 添加到配置
            self.config_manager.add_repo(**config)
            self.config_manager.save_config()

            # 重新加载列表
            self.load_repos()
            self.repos_changed.emit()

    def batch_scan_repos(self):
        """批量扫描并添加仓库"""
        dialog = RepoScanDialog(self.config_manager, self)
        if dialog.exec_():
            # 扫描对话框会自动添加仓库到配置
            # 只需重新加载列表
            self.load_repos()
            self.repos_changed.emit()

    def edit_repo(self, repo_id: str):
        """
        编辑仓库

        Args:
            repo_id: 仓库ID
        """
        repo_config = self.config_manager.get_repo_by_id(repo_id)
        if not repo_config:
            QMessageBox.warning(self, "错误", "仓库不存在")
            return

        dialog = RepoConfigDialog(self, repo_config)
        if dialog.exec_():
            updated_config = dialog.get_config()
            # 更新配置
            self.config_manager.update_repo(repo_id, **updated_config)
            self.config_manager.save_config()

            # 重新加载列表
            self.load_repos()
            self.repos_changed.emit()

    def delete_repo(self, repo_id: str):
        """
        删除仓库

        Args:
            repo_id: 仓库ID
        """
        repo_config = self.config_manager.get_repo_by_id(repo_id)
        if not repo_config:
            return

        repo_name = repo_config.get('name', '未知仓库')

        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除仓库「{repo_name}」吗?\n此操作不可恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.config_manager.delete_repo(repo_id)
            self.config_manager.save_config()

            # 重新加载列表
            self.load_repos()
            self.repos_changed.emit()

    def show_repo_detail(self, repo_id: str):
        """
        显示仓库详情

        Args:
            repo_id: 仓库ID
        """
        repo_config = self.config_manager.get_repo_by_id(repo_id)
        if not repo_config:
            QMessageBox.warning(self, "错误", "仓库不存在")
            return

        dialog = RepoDetailDialog(self, repo_config)
        dialog.exec_()

    def on_repo_toggled(self, repo_id: str, enabled: bool):
        """
        仓库启用状态切换

        Args:
            repo_id: 仓库ID
            enabled: 是否启用
        """
        self.config_manager.toggle_repo(repo_id)
        self.config_manager.save_config()

        # 更新统计(不重新加载整个列表)
        repos = self.config_manager.get_repos()
        enabled_count = sum(1 for r in repos if r.get('enabled', True))
        self.update_stats(len(repos), enabled_count)

        self.repos_changed.emit()
