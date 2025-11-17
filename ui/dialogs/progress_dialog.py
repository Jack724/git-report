"""
进度对话框
显示操作进度
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from qfluentwidgets import BodyLabel, SubtitleLabel, PushButton, ProgressBar


class ProgressDialog(QDialog):
    """进度对话框"""

    def __init__(self, parent=None):
        """
        初始化对话框

        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.cancelled = False
        self.auto_close_timer = None

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("进度")
        self.setModal(False)  # 非模态,用户可以看到主窗口
        self.setMinimumWidth(450)
        self.setMinimumHeight(180)

        # 禁止关闭按钮
        self.setWindowFlags(
            Qt.Dialog |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint
        )

        layout = QVBoxLayout()
        layout.setSpacing(16)

        # 标题
        self.title_label = SubtitleLabel("正在处理...")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # 进度条
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 当前步骤
        self.step_label = BodyLabel("准备中...")
        self.step_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.step_label)

        # 添加一些间距
        layout.addStretch()

        # 取消按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = PushButton("取消")
        self.cancel_btn.clicked.connect(self.on_cancel)
        self.cancel_btn.setFixedWidth(100)
        button_layout.addWidget(self.cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def start(self):
        """开始进度显示"""
        self.cancelled = False
        self.progress_bar.setValue(0)
        self.step_label.setText("准备中...")
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("取消")
        self.show()

    def update_progress(self, progress: int, step_text: str):
        """
        更新进度

        Args:
            progress: 进度百分比(0-100)
            step_text: 当前步骤描述
        """
        self.progress_bar.setValue(progress)
        self.step_label.setText(step_text)

    def set_success(self, message: str = "操作成功!"):
        """
        设置成功状态

        Args:
            message: 成功消息
        """
        self.progress_bar.setValue(100)
        self.step_label.setText(message)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("完成")

        # 2秒后自动关闭
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.timeout.connect(self.accept)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.start(2000)  # 2秒

    def set_error(self, error_message: str):
        """
        设置错误状态

        Args:
            error_message: 错误消息
        """
        self.step_label.setText(f"错误: {error_message}")
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("关闭")

    def on_cancel(self):
        """取消按钮点击"""
        if self.cancel_btn.text() == "取消":
            self.cancelled = True
            self.step_label.setText("正在取消...")
            self.cancel_btn.setEnabled(False)
        else:
            # "完成" 或 "关闭" 状态
            self.reject()

    def is_cancelled(self) -> bool:
        """
        检查是否已取消

        Returns:
            是否已取消
        """
        return self.cancelled

    def closeEvent(self, event):
        """关闭事件(禁止直接关闭)"""
        if self.cancel_btn.isEnabled() and self.cancel_btn.text() == "取消":
            # 如果进度正在进行,点击关闭按钮相当于取消
            self.on_cancel()
            event.ignore()
        else:
            # 已完成或出错,允许关闭
            if self.auto_close_timer:
                self.auto_close_timer.stop()
            event.accept()
