"""
主窗口 UI 模块
"""
import os
import time
import threading
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QTableWidget, QTableWidgetItem, QDialog,
    QHeaderView, QApplication, QStatusBar, QLabel
)
from PySide6.QtCore import Qt, QDate, QThread, Signal
from PySide6.QtGui import QFont, QCursor, QIcon
from qfluentwidgets import (
    PushButton, PrimaryPushButton, BodyLabel, SubtitleLabel,
    MessageBox, InfoBar, InfoBarPosition, TextBrowser
)
import markdown2

from infrastructure.config_manager import ConfigManager
from core.services.git_service import GitService, CommitRecord
from core.services.formatter import DataFormatter
from infrastructure.ai_client import AiClientFactory
from infrastructure.logger import get_logger
from ui.dialogs.ai_config_dialog import AIConfigDialog
from ui.widgets.repo_list_widget import RepoListWidget
from ui.widgets.date_range_picker import DateRangePickerWidget
from ui.themes.theme_manager import ThemeManager
from ui.themes.icons import Icons
from ui.dialogs.progress_dialog import ProgressDialog
from ui.dialogs.commit_log_dialog import CommitLogDialog
from utils.resource_path import get_resource_path

logger = get_logger()


class ReportDialog(QDialog):
    """报告展示对话框"""

    def __init__(self, report_text: str, parent=None):
        super().__init__(parent)
        self.report_text = report_text
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("生成的工作报告")
        self.resize(700, 600)

        layout = QVBoxLayout()

        # 报告显示区域
        self.text_browser = TextBrowser()
        self.text_browser.setFont(QFont("Microsoft YaHei", 10))

        # 转换 Markdown 为 HTML
        # 处理换行符：在单个换行符后添加两个空格以强制换行
        processed_text = self.report_text.replace('\n', '  \n')
        html_content = markdown2.markdown(processed_text)
        self.text_browser.setHtml(html_content)

        layout.addWidget(self.text_browser)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.copy_btn = PushButton("复制报告")
        self.copy_btn.clicked.connect(self.copy_report)
        btn_layout.addWidget(self.copy_btn)

        self.close_btn = PrimaryPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def copy_report(self):
        """复制报告到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.report_text)
        InfoBar.success(
            title="成功",
            content="报告已复制到剪贴板",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )


class FetchCommitsThread(QThread):
    """拉取提交记录的后台线程"""
    finished = Signal(list, list)  # all_commits, failed_repos
    error = Signal(str)
    progress_updated = Signal(int, str)  # 进度百分比, 步骤描述

    def __init__(self, config_manager, start_datetime, end_datetime):
        super().__init__()
        self.config_manager = config_manager
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    def run(self):
        """执行拉取操作"""
        try:
            # 获取所有已启用的仓库
            enabled_repos = self.config_manager.get_enabled_repos()

            if not enabled_repos:
                self.error.emit("请先添加并启用至少一个仓库")
                return

            self.progress_updated.emit(10, f"准备拉取 {len(enabled_repos)} 个仓库...")
            time.sleep(0.3)

            # 汇总所有仓库的提交
            all_commits = []
            failed_repos = []

            # 计算每个仓库的进度占比
            progress_per_repo = 80 / len(enabled_repos)  # 10%-90%之间分配给各仓库

            for idx, repo in enumerate(enabled_repos):
                repo_name = repo.get('name', '未知仓库')
                repo_path = repo.get('path', '')
                author_name = repo.get('author_name') or None
                author_email = repo.get('author_email') or None

                # 更新进度
                current_progress = 10 + int(idx * progress_per_repo)
                self.progress_updated.emit(current_progress, f"正在拉取: {repo_name}...")

                try:
                    # 创建 GitService
                    git_service = GitService(repo_path, repo_name)

                    # 拉取该仓库的提交
                    commits = git_service.get_commits(
                        author_name=author_name,
                        author_email=author_email,
                        start_date=self.start_datetime,
                        end_date=self.end_datetime
                    )

                    all_commits.extend(commits)
                    logger.info(f"仓库 {repo_name} 拉取成功: {len(commits)} 条提交")

                except Exception as e:
                    error_msg = f"{repo_name}: {str(e)}"
                    failed_repos.append(error_msg)
                    logger.error(f"仓库 {repo_name} 拉取失败: {e}")

            # 排序
            self.progress_updated.emit(90, "正在排序提交记录...")
            all_commits.sort(key=lambda c: c.date, reverse=True)
            time.sleep(0.2)

            self.progress_updated.emit(100, "完成!")
            self.finished.emit(all_commits, failed_repos)

        except Exception as e:
            logger.error(f"拉取提交记录失败: {e}", exc_info=True)
            self.error.emit(str(e))


class GenerateReportThread(QThread):
    """生成报告的后台线程"""
    finished = Signal(str)
    error = Signal(str)
    progress_updated = Signal(int, str)  # 进度百分比, 步骤描述

    def __init__(self, ai_client, commit_summary):
        super().__init__()
        self.ai_client = ai_client
        self.commit_summary = commit_summary
        self.current_progress = 0
        self.max_progress = 88  # 最大模拟到88%,避免到达90%前AI还没响应
        self.timer_running = False
        self.timer_thread = None

    def _simulate_progress(self):
        """定时器回调:模拟进度增长"""
        while self.timer_running and self.current_progress < self.max_progress:
            time.sleep(0.5)  # 每0.5秒更新一次
            if self.timer_running:  # 再次检查，确保在sleep期间没有被停止
                self.current_progress += 1
                self.progress_updated.emit(self.current_progress, "等待AI响应中...")

    def _start_progress_timer(self):
        """启动进度模拟定时器"""
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self._simulate_progress, daemon=True)
        self.timer_thread.start()

    def _stop_progress_timer(self):
        """停止进度模拟定时器"""
        self.timer_running = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1)  # 等待线程结束，最多1秒
            self.timer_thread = None

    def run(self):
        """执行报告生成"""
        try:
            self.progress_updated.emit(40, "正在调用AI API...")
            time.sleep(0.5)  # 让用户能看到进度更新

            # 启动进度模拟定时器(每0.5秒增加1%)
            self.current_progress = 60
            self.progress_updated.emit(60, "等待AI响应中...")
            self._start_progress_timer()

            # 调用AI生成报告(耗时操作)
            report = self.ai_client.generate_report(self.commit_summary)

            # 停止进度模拟
            self._stop_progress_timer()

            self.progress_updated.emit(90, "处理响应数据...")
            time.sleep(0.3)

            self.finished.emit(report)
        except Exception as e:
            # 发生错误时也要停止定时器
            self._stop_progress_timer()
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.commits = []
        self.last_generated_report = None  # 保存最近生成的报告
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Git 提交记录智能报告生成器")
        self.resize(1000, 700)

        # 设置窗口图标（支持打包环境）
        icon_path = get_resource_path('app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # === 仓库列表区域 ===
        self.repo_list_widget = RepoListWidget(self.config_manager)
        self.repo_list_widget.repos_changed.connect(self.on_repos_changed)
        main_layout.addWidget(self.repo_list_widget, stretch=1)

        # === 配置信息区域（统一样式的可点击标签）===
        config_layout = QVBoxLayout()

        # 日期范围选择器
        self.date_range_picker = DateRangePickerWidget(self)
        config_layout.addWidget(self.date_range_picker)

        # AI 配置标签（可点击）
        self.ai_config_label = QLabel()
        self.ai_config_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.ai_config_label.setStyleSheet("""
            QLabel {
                padding: 8px 12px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
                color: #333;
            }
            QLabel:hover {
                background-color: #e8e8e8;
                border-color: #999;
            }
        """)
        self.ai_config_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.ai_config_label.mousePressEvent = lambda e: self.open_ai_config()
        config_layout.addWidget(self.ai_config_label)

        # 提交记录标签（可点击）
        self.commits_label = QLabel()
        self.commits_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.commits_label.setStyleSheet("""
            QLabel {
                padding: 8px 12px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
                color: #333;
            }
            QLabel:hover {
                background-color: #e8e8e8;
                border-color: #999;
            }
            QLabel[enabled="false"] {
                color: #999;
            }
            QLabel[enabled="false"]:hover {
                background-color: #f5f5f5;
                border-color: #ddd;
            }
        """)
        self.commits_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.commits_label.mousePressEvent = lambda e: self.view_commit_log_from_label()
        config_layout.addWidget(self.commits_label)

        # 报告查看标签（可点击）
        self.report_view_label = QLabel()
        self.report_view_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.report_view_label.setStyleSheet("""
            QLabel {
                padding: 8px 12px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
                color: #333;
            }
            QLabel:hover {
                background-color: #e8e8e8;
                border-color: #999;
            }
            QLabel[enabled="false"] {
                color: #999;
            }
            QLabel[enabled="false"]:hover {
                background-color: #f5f5f5;
                border-color: #ddd;
            }
        """)
        self.report_view_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.report_view_label.mousePressEvent = lambda e: self.view_last_report()
        config_layout.addWidget(self.report_view_label)

        main_layout.addLayout(config_layout)

        # === 底部操作按钮（水平居中）===
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addStretch()

        # 拉取提交记录按钮
        self.fetch_btn = PushButton("拉取提交记录")
        self.fetch_btn.clicked.connect(self.fetch_commits)
        bottom_btn_layout.addWidget(self.fetch_btn)

        # 两按钮之间的间距
        bottom_btn_layout.addSpacing(20)

        # 生成报告按钮 (使用 PrimaryPushButton 突出主要操作)
        self.generate_btn = PrimaryPushButton("生成报告")
        self.generate_btn.clicked.connect(self.generate_report)
        self.generate_btn.setEnabled(False)
        bottom_btn_layout.addWidget(self.generate_btn)

        bottom_btn_layout.addStretch()
        main_layout.addLayout(bottom_btn_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 更新显示
        self.update_ai_config_display()
        self.update_commits_display()
        self.update_report_view_display()

        self.status_bar.showMessage("就绪")

    def load_config(self):
        """加载配置(多仓库模式下无需加载单仓库配置)"""
        pass

    def on_repos_changed(self):
        """仓库列表变化时的回调"""
        # 可以在这里添加额外的逻辑,例如清空当前的提交记录
        pass

    def open_ai_config(self):
        """打开 AI 配置对话框"""
        dialog = AIConfigDialog(self.config_manager, self)
        if dialog.exec_():
            # 更新AI配置显示
            self.update_ai_config_display()

    def update_ai_config_display(self):
        """更新AI配置显示"""
        try:
            provider = self.config_manager.get('ai.provider', 'openai')
            model = self.config_manager.get(f'ai.configs.{provider}.model', '')
            api_key = self.config_manager.get(f'ai.configs.{provider}.api_key', '')

            # 平台名称映射
            provider_names = {
                'openai': 'OpenAI GPT',
                'deepseek': 'Deepseek',
                'zhipu': '智谱 GLM'
            }
            provider_name = provider_names.get(provider, provider)

            if api_key:
                # 已配置
                text = f"⚙️ AI配置: {provider_name} / {model}"
                self.ai_config_label.setToolTip(f"当前AI模型: {provider_name}\n模型: {model}\n点击修改配置")
            else:
                # 未配置
                text = "⚙️ AI配置: 未配置"
                self.ai_config_label.setToolTip("点击配置AI服务")

            self.ai_config_label.setText(text)
            logger.info(f"AI配置显示已更新: {text}")

        except Exception as e:
            logger.error(f"更新AI配置显示失败: {e}")
            self.ai_config_label.setText("⚙️ AI配置: 配置错误")


    def fetch_commits(self):
        """拉取多个仓库的提交记录"""
        # 获取所有已启用的仓库
        enabled_repos = self.config_manager.get_enabled_repos()

        if not enabled_repos:
            MessageBox("警告", "请先添加并启用至少一个仓库", self).exec()
            return

        try:
            self.fetch_btn.setEnabled(False)

            # 创建并显示进度对话框
            self.fetch_progress_dialog = ProgressDialog(self)
            self.fetch_progress_dialog.setWindowTitle("拉取提交记录")
            self.fetch_progress_dialog.start()
            self.fetch_progress_dialog.update_progress(0, "准备拉取...")

            # 获取日期范围
            start_date, end_date = self.date_range_picker.get_date_range_python()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())

            # 在后台线程拉取
            self.fetch_thread = FetchCommitsThread(
                self.config_manager,
                start_datetime,
                end_datetime
            )
            self.fetch_thread.finished.connect(self.on_fetch_finished)
            self.fetch_thread.error.connect(self.on_fetch_error)
            self.fetch_thread.progress_updated.connect(self.on_fetch_progress_updated)
            self.fetch_thread.start()

        except Exception as e:
            if hasattr(self, 'fetch_progress_dialog') and self.fetch_progress_dialog:
                self.fetch_progress_dialog.close()

            logger.error(f"拉取提交记录失败: {e}", exc_info=True)
            MessageBox("错误", f"拉取提交记录失败: {str(e)}", self).exec()
            self.status_bar.showMessage("拉取失败", 3000)
            self.fetch_btn.setEnabled(True)

    def on_fetch_progress_updated(self, progress: int, step_text: str):
        """更新拉取进度"""
        if hasattr(self, 'fetch_progress_dialog') and self.fetch_progress_dialog:
            self.fetch_progress_dialog.update_progress(progress, step_text)

    def on_fetch_finished(self, all_commits: list, failed_repos: list):
        """拉取完成"""
        self.commits = all_commits

        # 更新提交记录显示
        self.update_commits_display()

        # 更新进度对话框为成功状态
        if hasattr(self, 'fetch_progress_dialog') and self.fetch_progress_dialog:
            success_msg = f"成功拉取 {len(all_commits)} 条提交记录!"
            self.fetch_progress_dialog.update_progress(100, success_msg)
            self.fetch_progress_dialog.set_success(success_msg)

        self.status_bar.showMessage(f"拉取成功: {len(all_commits)} 条提交记录", 3000)
        self.fetch_btn.setEnabled(True)

        # 显示结果
        if failed_repos:
            msg = f"成功拉取 {len(all_commits)} 条提交记录\n\n失败的仓库 ({len(failed_repos)} 个):\n" + "\n".join(failed_repos)
            MessageBox("部分拉取失败", msg, self).exec()

    def on_fetch_error(self, error_msg: str):
        """拉取失败"""
        logger.error(f"拉取提交记录失败: {error_msg}")

        # 更新进度对话框为错误状态
        if hasattr(self, 'fetch_progress_dialog') and self.fetch_progress_dialog:
            self.fetch_progress_dialog.set_error(error_msg)

        self.status_bar.showMessage("拉取失败", 3000)
        self.fetch_btn.setEnabled(True)
        MessageBox("错误", f"拉取提交记录失败: {error_msg}", self).exec()

    def update_commits_display(self):
        """更新提交记录显示"""
        commit_count = len(self.commits)

        # 更新提交记录标签
        if commit_count > 0:
            text = f"📋 提交记录: {commit_count} 条"
            self.commits_label.setToolTip(f"共 {commit_count} 条提交记录\n点击查看详情")
            self.commits_label.setProperty("enabled", "true")
            self.commits_label.setCursor(QCursor(Qt.PointingHandCursor))
        else:
            text = "📋 提交记录: 暂无数据"
            self.commits_label.setToolTip("暂无提交记录")
            self.commits_label.setProperty("enabled", "false")
            self.commits_label.setCursor(QCursor(Qt.ArrowCursor))

        self.commits_label.setText(text)
        # 强制刷新样式
        self.commits_label.style().unpolish(self.commits_label)
        self.commits_label.style().polish(self.commits_label)

        # 启用/禁用生成报告按钮
        self.generate_btn.setEnabled(commit_count > 0)

    def update_report_view_display(self):
        """更新报告查看标签显示"""
        if self.last_generated_report:
            # 有报告可查看
            self.report_view_label.setText("📄 最近报告: 已生成 | 点击查看")
            self.report_view_label.setToolTip("点击查看最近生成的报告")
            self.report_view_label.setProperty("enabled", "true")
            self.report_view_label.setCursor(QCursor(Qt.PointingHandCursor))
        else:
            # 没有报告
            self.report_view_label.setText("📄 最近报告: 暂无")
            self.report_view_label.setToolTip("暂无已生成的报告")
            self.report_view_label.setProperty("enabled", "false")
            self.report_view_label.setCursor(QCursor(Qt.ArrowCursor))

        # 强制刷新样式
        self.report_view_label.style().unpolish(self.report_view_label)
        self.report_view_label.style().polish(self.report_view_label)

    def view_commit_log_from_label(self):
        """从标签点击查看提交日志"""
        if len(self.commits) > 0:
            self.view_commit_log()

    def view_last_report(self):
        """查看最近生成的报告"""
        if not self.last_generated_report:
            MessageBox("提示", "暂无已生成的报告", self).exec()
            return

        # 显示报告对话框
        dialog = ReportDialog(self.last_generated_report, self)
        dialog.exec()

    def view_commit_log(self):
        """查看提交日志详情"""
        if not self.commits:
            MessageBox("提示", "暂无提交记录", self).exec()
            return

        try:
            logger.info(f"打开提交日志对话框, 共{len(self.commits)}条记录")

            # 直接传递 commits 列表到对话框
            dialog = CommitLogDialog(self.commits, self)
            dialog.exec_()

        except Exception as e:
            logger.error(f"打开提交日志对话框失败: {e}", exc_info=True)
            MessageBox("错误", f"查看日志失败: {str(e)}", self).exec()

    def generate_report(self):
        """生成报告"""
        if not self.commits:
            MessageBox("警告", "没有提交记录", self).exec()
            return

        # 检查 AI 配置
        try:
            self.generate_btn.setEnabled(False)

            # 创建并显示进度对话框
            self.progress_dialog = ProgressDialog(self)
            self.progress_dialog.start()
            self.progress_dialog.update_progress(0, "准备生成报告...")

            # 格式化提交记录
            self.progress_dialog.update_progress(10, "正在格式化提交记录...")
            formatter = DataFormatter()
            commit_summary = formatter.format_commits(self.commits)
            logger.info(f"格式化完成, 提交记录长度: {len(commit_summary)}字符")

            # 创建 AI 客户端
            self.progress_dialog.update_progress(20, "正在创建AI客户端...")
            ai_client = AiClientFactory.create(self.config_manager)

            # 在后台线程生成报告
            self.progress_dialog.update_progress(30, "准备调用AI...")
            self.report_thread = GenerateReportThread(ai_client, commit_summary)
            self.report_thread.finished.connect(self.on_report_generated)
            self.report_thread.error.connect(self.on_report_error)
            self.report_thread.progress_updated.connect(self.on_progress_updated)
            self.report_thread.start()

        except ValueError as e:
            # 配置错误(例如未配置 API Key)
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()

            w = MessageBox("配置错误", f"{str(e)}\n\n是否现在配置?", self)
            if w.exec():
                self.open_ai_config()
            self.status_bar.showMessage("未配置", 3000)
            self.generate_btn.setEnabled(True)
        except Exception as e:
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()

            logger.error(f"生成报告失败: {e}", exc_info=True)
            MessageBox("错误", f"生成报告失败: {str(e)}", self).exec()
            self.status_bar.showMessage("生成失败", 3000)
            self.generate_btn.setEnabled(True)

    def on_progress_updated(self, progress: int, step_text: str):
        """更新进度"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.update_progress(progress, step_text)

    def on_report_generated(self, report: str):
        """报告生成完成"""
        # 保存报告到实例变量
        self.last_generated_report = report

        # 更新报告查看标签显示
        self.update_report_view_display()

        # 获取 Token 用量统计（仅用于日志和状态栏）
        if hasattr(self.report_thread, 'ai_client'):
            usage = self.report_thread.ai_client.get_token_usage()
            if usage and 'total_tokens' in usage:
                total = usage.get('total_tokens', 0)
                prompt = usage.get('prompt_tokens', 0)
                completion = usage.get('completion_tokens', 0)
                logger.info(f"报告生成成功 - Token使用: {total} (prompt={prompt}, completion={completion})")
                self.status_bar.showMessage(
                    f"报告生成成功 (消耗 {total} tokens: {prompt} prompt + {completion} completion)",
                    5000
                )
            else:
                self.status_bar.showMessage("报告生成成功", 3000)
        else:
            self.status_bar.showMessage("报告生成成功", 3000)

        # 更新进度对话框为成功状态
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.update_progress(100, "报告生成成功!")
            self.progress_dialog.set_success("报告生成成功!")

        self.generate_btn.setEnabled(True)

        # 显示报告对话框
        dialog = ReportDialog(report, self)
        dialog.exec()

    def on_report_error(self, error_msg: str):
        """报告生成失败"""
        logger.error(f"报告生成失败: {error_msg}")

        # 更新进度对话框为错误状态
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.set_error(error_msg)

        self.status_bar.showMessage("生成失败", 3000)
        self.generate_btn.setEnabled(True)
        MessageBox("错误", f"生成报告失败: {error_msg}", self).exec()
