"""
主题管理器
负责加载和应用 QFluentWidgets 主题
"""
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from qfluentwidgets import setTheme, Theme, setThemeColor
from infrastructure.logger import get_logger

logger = get_logger()


class ThemeManager:
    """主题管理器"""

    @staticmethod
    def load_theme(app: QApplication):
        """
        加载并应用 Fluent Design 主题

        Args:
            app: QApplication实例
        """
        try:
            # 应用浅色主题
            setTheme(Theme.LIGHT)

            # 设置主题色（紫色系，与原来的UI风格一致）
            setThemeColor('#898AC4')

            logger.info("已加载 Fluent Design 主题")
            return True

        except Exception as e:
            logger.error(f"加载主题失败: {e}", exc_info=True)
            return False

    @staticmethod
    def apply_card_style(widget):
        """
        为widget应用卡片样式

        Args:
            widget: QWidget实例
        """
        widget.setObjectName("card")
        # 触发样式更新
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    @staticmethod
    def apply_model_label_style(label):
        """
        为AI模型标签应用特殊样式

        Args:
            label: QLabel实例
        """
        label.setObjectName("modelLabel")
        label.setCursor(QCursor(Qt.PointingHandCursor))
        label.style().unpolish(label)
        label.style().polish(label)

    @staticmethod
    def apply_warning_label_style(label):
        """
        为警告标签应用特殊样式

        Args:
            label: QLabel实例
        """
        label.setObjectName("warningLabel")
        label.style().unpolish(label)
        label.style().polish(label)

    @staticmethod
    def apply_secondary_button_style(button):
        """
        为次要按钮应用样式

        Args:
            button: QPushButton实例
        """
        button.setObjectName("secondaryButton")
        button.style().unpolish(button)
        button.style().polish(button)

    @staticmethod
    def apply_danger_button_style(button):
        """
        为危险按钮应用样式

        Args:
            button: QPushButton实例
        """
        button.setObjectName("dangerButton")
        button.style().unpolish(button)
        button.style().polish(button)
