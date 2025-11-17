"""
仓库扫描对话框
批量扫描并添加Git仓库
"""
import os
from typing import List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem, QSpinBox,
    QFileDialog, QMessageBox, QLineEdit, QProgressBar, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal
from core.services.repo_scanner import RepoScanner, RepoInfo


class ScanThread(QThread):
    """后台扫描线程"""
    progress = Signal(int, int)  # repos_found, dirs_scanned
    finished = Signal(list)  # List[RepoInfo]
    error = Signal(str)

    def __init__(self, root_path: str, max_depth: int):
        super().__init__()
        self.root_path = root_path
        self.max_depth = max_depth
        self.scanner = RepoScanner()

    def run(self):
        """执行扫描"""
        try:
            # 定期更新进度
            import time
            last_update = time.time()

            repos = self.scanner.scan_directory(self.root_path, self.max_depth)

            # 发送最终进度
            repos_count, dirs_count = self.scanner.get_progress()
            self.progress.emit(repos_count, dirs_count)

            self.finished.emit(repos)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        """停止扫描"""
        self.scanner.stop()


class RepoScanDialog(QDialog):
    """仓库扫描对话框"""

    def __init__(self, config_manager, parent=None):
        """
        初始化对话框

        Args:
            config_manager: 配置管理器
            parent: 父窗口
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.scan_thread = None
        self.scanned_repos = []  # 扫描到的所有仓库
        self.repo_items = {}  # path -> QTreeWidgetItem 映射

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("批量添加Git仓库")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # === 扫描配置区域 ===
        config_group = QHBoxLayout()

        # 扫描目录
        config_group.addWidget(QLabel("扫描目录:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("选择要扫描的父目录...")
        config_group.addWidget(self.path_input)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_directory)
        config_group.addWidget(browse_btn)

        # 扫描深度
        config_group.addWidget(QLabel("扫描深度:"))
        self.depth_spin = QSpinBox()
        self.depth_spin.setMinimum(1)
        self.depth_spin.setMaximum(10)
        self.depth_spin.setValue(3)
        self.depth_spin.setSuffix(" 层")
        config_group.addWidget(self.depth_spin)

        # 开始扫描按钮
        self.scan_btn = QPushButton("开始扫描")
        self.scan_btn.clicked.connect(self.start_scan)
        config_group.addWidget(self.scan_btn)

        # 停止扫描按钮
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        config_group.addWidget(self.stop_btn)

        layout.addLayout(config_group)

        # === 进度条 ===
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("就绪")
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

        # === 结果标题和操作按钮 ===
        result_header = QHBoxLayout()
        self.result_label = QLabel("找到的仓库:")
        result_header.addWidget(self.result_label)
        result_header.addStretch()

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setEnabled(False)
        result_header.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        self.deselect_all_btn.setEnabled(False)
        result_header.addWidget(self.deselect_all_btn)

        layout.addLayout(result_header)

        # === 树形结果展示 ===
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["仓库", "路径", "作者信息", "状态"])
        self.tree_widget.setColumnWidth(0, 200)
        self.tree_widget.setColumnWidth(1, 300)
        self.tree_widget.setColumnWidth(2, 200)
        self.tree_widget.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.tree_widget)

        # === 统计信息 ===
        self.stats_label = QLabel("已选中: 0 个仓库")
        layout.addWidget(self.stats_label)

        # === 底部按钮 ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.add_btn = QPushButton("添加选中仓库")
        self.add_btn.clicked.connect(self.add_selected_repos)
        self.add_btn.setEnabled(False)
        button_layout.addWidget(self.add_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_directory(self):
        """浏览选择目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择要扫描的父目录",
            self.path_input.text() or os.path.expanduser("~")
        )

        if directory:
            self.path_input.setText(directory)

    def start_scan(self):
        """开始扫描"""
        root_path = self.path_input.text().strip()

        if not root_path:
            QMessageBox.warning(self, "输入错误", "请选择要扫描的目录")
            return

        if not os.path.exists(root_path):
            QMessageBox.warning(self, "路径错误", f"目录不存在: {root_path}")
            return

        # 清空之前的结果
        self.tree_widget.clear()
        self.scanned_repos = []
        self.repo_items = {}

        # 禁用控件
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.path_input.setEnabled(False)
        self.depth_spin.setEnabled(False)

        # 创建并启动扫描线程
        max_depth = self.depth_spin.value()
        self.scan_thread = ScanThread(root_path, max_depth)
        self.scan_thread.progress.connect(self.on_scan_progress)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.start()

        self.progress_label.setText("正在扫描...")

    def stop_scan(self):
        """停止扫描"""
        if self.scan_thread:
            self.scan_thread.stop()
            self.progress_label.setText("正在停止...")

    def on_scan_progress(self, repos_found: int, dirs_scanned: int):
        """扫描进度更新"""
        self.progress_label.setText(f"正在扫描... 已找到 {repos_found} 个仓库, 已扫描 {dirs_scanned} 个目录")

    def on_scan_finished(self, repos: List[RepoInfo]):
        """扫描完成"""
        self.scanned_repos = repos

        # 恢复控件
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.path_input.setEnabled(True)
        self.depth_spin.setEnabled(True)

        if not repos:
            self.progress_label.setText("未找到任何 Git 仓库")
            QMessageBox.information(self, "扫描完成", "未找到任何 Git 仓库")
            return

        # 获取已添加的仓库路径
        existing_repos = self.config_manager.get_repos()
        existing_paths = set(os.path.normpath(r['path']).lower() for r in existing_repos)

        # 按目录分组
        repos_by_parent = {}
        for repo in repos:
            parent = repo.parent_path
            if parent not in repos_by_parent:
                repos_by_parent[parent] = []
            repos_by_parent[parent].append(repo)

        # 构建树形结构
        for parent_path in sorted(repos_by_parent.keys()):
            parent_item = QTreeWidgetItem(self.tree_widget)
            parent_item.setText(0, parent_path)
            parent_item.setExpanded(True)
            parent_item.setFlags(parent_item.flags() & ~Qt.ItemIsUserCheckable)

            for repo in sorted(repos_by_parent[parent_path], key=lambda r: r.name):
                # 检查是否已添加
                normalized_path = os.path.normpath(repo.path).lower()
                is_added = normalized_path in existing_paths

                # 创建仓库项
                repo_item = QTreeWidgetItem(parent_item)
                repo_item.setText(0, repo.name)
                repo_item.setText(1, repo.path)

                # 作者信息
                author_info = ""
                if repo.author_name or repo.author_email:
                    author_info = f"{repo.author_name} <{repo.author_email}>"
                repo_item.setText(2, author_info)

                # 状态
                if is_added:
                    repo_item.setText(3, "已添加")
                    repo_item.setCheckState(0, Qt.Unchecked)
                    repo_item.setFlags(repo_item.flags() & ~Qt.ItemIsEnabled)
                    # 灰色显示
                    for col in range(4):
                        repo_item.setForeground(col, Qt.gray)
                else:
                    repo_item.setText(3, "")
                    repo_item.setCheckState(0, Qt.Checked)  # 默认选中

                # 保存映射
                self.repo_items[repo.path] = repo_item

        # 更新统计
        new_count = len([r for r in repos if os.path.normpath(r.path).lower() not in existing_paths])
        added_count = len(repos) - new_count

        self.result_label.setText(f"找到的仓库 ({len(repos)} 个, 已添加 {added_count} 个):")
        self.progress_label.setText(f"扫描完成,找到 {len(repos)} 个仓库")

        # 启用按钮
        self.select_all_btn.setEnabled(True)
        self.deselect_all_btn.setEnabled(True)
        self.add_btn.setEnabled(True)

        # 更新选中统计
        self.update_selection_stats()

    def on_scan_error(self, error_msg: str):
        """扫描出错"""
        # 恢复控件
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.path_input.setEnabled(True)
        self.depth_spin.setEnabled(True)

        self.progress_label.setText(f"扫描失败: {error_msg}")
        QMessageBox.critical(self, "扫描失败", f"扫描目录时出错:\n{error_msg}")

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """树形项改变时更新统计"""
        if column == 0:  # 复选框列
            self.update_selection_stats()

    def update_selection_stats(self):
        """更新选中统计"""
        selected_count = 0

        for repo in self.scanned_repos:
            item = self.repo_items.get(repo.path)
            if item and item.checkState(0) == Qt.Checked:
                selected_count += 1

        self.stats_label.setText(f"已选中: {selected_count} 个仓库")

    def select_all(self):
        """全选"""
        for repo in self.scanned_repos:
            item = self.repo_items.get(repo.path)
            if item and (item.flags() & Qt.ItemIsEnabled):
                item.setCheckState(0, Qt.Checked)

    def deselect_all(self):
        """取消全选"""
        for repo in self.scanned_repos:
            item = self.repo_items.get(repo.path)
            if item and (item.flags() & Qt.ItemIsEnabled):
                item.setCheckState(0, Qt.Unchecked)

    def add_selected_repos(self):
        """添加选中的仓库"""
        # 获取选中的仓库
        selected_repos = []
        for repo in self.scanned_repos:
            item = self.repo_items.get(repo.path)
            if item and item.checkState(0) == Qt.Checked:
                selected_repos.append(repo)

        if not selected_repos:
            QMessageBox.warning(self, "未选择", "请至少选择一个仓库")
            return

        # 批量添加
        added_count = 0
        for repo in selected_repos:
            try:
                self.config_manager.add_repo(
                    name=repo.name,
                    path=repo.path,
                    author_name=repo.author_name,
                    author_email=repo.author_email,
                    enabled=True
                )
                added_count += 1
            except Exception as e:
                print(f"添加仓库失败 ({repo.path}): {e}")

        # 保存配置
        if added_count > 0:
            self.config_manager.save_config()

        # 显示结果
        if added_count == len(selected_repos):
            QMessageBox.information(self, "成功", f"成功添加 {added_count} 个仓库")
            self.accept()
        else:
            failed_count = len(selected_repos) - added_count
            QMessageBox.warning(
                self,
                "部分成功",
                f"成功添加 {added_count} 个仓库\n失败 {failed_count} 个"
            )
            if added_count > 0:
                self.accept()
