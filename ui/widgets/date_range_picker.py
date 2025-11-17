"""
现代日期范围选择器组件
使用单日历 + 双击选择模式，提供流畅的用户体验
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCalendarWidget, QPushButton, QFrame, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, QDate, Signal, QPoint
from PySide6.QtGui import QTextCharFormat, QColor, QCursor


class ModernDateRangePanel(QWidget):
    """现代日期范围选择面板（单日历 + 快捷选择）"""

    date_range_changed = Signal(QDate, QDate)

    def __init__(self, start_date: QDate, end_date: QDate, parent=None):
        """
        初始化日期范围选择面板

        Args:
            start_date: 初始开始日期
            end_date: 初始结束日期
            parent: 父组件
        """
        super().__init__(parent)

        # 当前选择的日期范围
        self.start_date = start_date
        self.end_date = end_date

        # 临时选择状态（用于双击选择）
        self.temp_start_date = start_date
        self.temp_end_date = end_date
        self.selection_mode = "START"  # "START" or "END"

        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # 快捷选择按钮组
        self.quick_buttons = QButtonGroup(self)
        self.custom_radio = None  # 自定义选项的单选按钮

        self.init_ui()

        # 连接信号
        self.calendar.clicked.connect(self.on_date_clicked)

        # 初始化显示
        self.update_range_highlight()
        self.update_range_label()

    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # === 左侧：快捷选择区域 ===
        quick_panel = self._create_quick_panel()
        main_layout.addWidget(quick_panel)

        # === 右侧：日历区域 ===
        calendar_panel = self._create_calendar_panel()
        main_layout.addWidget(calendar_panel)

        self.setLayout(main_layout)

    def _create_quick_panel(self):
        """创建快捷选择面板"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # 标题
        title = QLabel("快捷选择")
        title.setStyleSheet("font-weight: bold; font-size: 13px; color: #333; padding-bottom: 4px;")
        layout.addWidget(title)

        # 快捷选项列表
        quick_options = [
            ("最近7天", 7),
            ("最近30天", 30),
            ("本月", "this_month"),
            ("上月", "last_month"),
            ("最近3个月", 90),
            ("最近6个月", 180),
        ]

        for text, value in quick_options:
            radio = QRadioButton(text)
            radio.setStyleSheet("""
                QRadioButton {
                    padding: 4px 8px;
                    font-size: 13px;
                }
                QRadioButton:hover {
                    background-color: #e6f7ff;
                    border-radius: 4px;
                }
            """)
            if isinstance(value, int):
                radio.clicked.connect(lambda checked, days=value: self.set_quick_range(days))
            elif value == "this_month":
                radio.clicked.connect(lambda checked: self.set_this_month())
            elif value == "last_month":
                radio.clicked.connect(lambda checked: self.set_last_month())

            self.quick_buttons.addButton(radio)
            layout.addWidget(radio)

        # 自定义选项
        self.custom_radio = QRadioButton("自定义")
        self.custom_radio.setStyleSheet("""
            QRadioButton {
                padding: 4px 8px;
                font-size: 13px;
            }
        """)
        self.custom_radio.setChecked(True)  # 默认选中自定义
        self.quick_buttons.addButton(self.custom_radio)
        layout.addWidget(self.custom_radio)

        layout.addStretch()
        panel.setLayout(layout)
        panel.setFixedWidth(130)

        return panel

    def _create_calendar_panel(self):
        """创建日历面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 日历控件
        layout.addWidget(self.calendar)

        # 范围信息标签
        self.range_label = QLabel()
        self.range_label.setAlignment(Qt.AlignCenter)
        self.range_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 6px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.range_label)

        # 提示标签
        hint_label = QLabel("提示：点击两次选择日期范围")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(hint_label)

        panel.setLayout(layout)
        return panel

    def on_date_clicked(self, date: QDate):
        """日期被点击"""
        # 切换到自定义模式
        if self.custom_radio:
            self.custom_radio.setChecked(True)

        if self.selection_mode == "START":
            # 选择开始日期
            self.temp_start_date = date
            self.temp_end_date = date
            self.selection_mode = "END"
        else:
            # 选择结束日期
            if date >= self.temp_start_date:
                self.temp_end_date = date
            else:
                # 如果选择的日期早于开始日期，交换
                self.temp_end_date = self.temp_start_date
                self.temp_start_date = date
            self.selection_mode = "START"

        # 更新显示
        self.update_range_highlight()
        self.update_range_label()

        # 发出信号
        self.date_range_changed.emit(self.temp_start_date, self.temp_end_date)

    def update_range_highlight(self):
        """更新日期范围的高亮显示"""
        start = self.temp_start_date
        end = self.temp_end_date
        today = QDate.currentDate()

        # 清除所有格式
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        # 今天的格式（橙色边框）
        today_format = QTextCharFormat()
        today_format.setBackground(QColor("#fff3e0"))
        today_format.setForeground(QColor("#ff9800"))

        # 范围内日期的格式（浅蓝色背景）
        range_format = QTextCharFormat()
        range_format.setBackground(QColor("#e6f7ff"))

        # 选中日期的格式（蓝色背景）
        selected_format = QTextCharFormat()
        selected_format.setBackground(QColor("#1890ff"))
        selected_format.setForeground(QColor("#ffffff"))

        # 高亮范围内的日期
        current = start
        while current <= end:
            if current == start or current == end:
                # 开始和结束日期使用选中样式
                self.calendar.setDateTextFormat(current, selected_format)
            elif current == today:
                # 今天使用特殊样式
                self.calendar.setDateTextFormat(current, today_format)
            else:
                # 范围内其他日期
                self.calendar.setDateTextFormat(current, range_format)
            current = current.addDays(1)

        # 今天不在范围内时，也标记出来
        if today < start or today > end:
            self.calendar.setDateTextFormat(today, today_format)

    def update_range_label(self):
        """更新日期范围显示标签"""
        days = self.temp_start_date.daysTo(self.temp_end_date) + 1

        mode_text = "开始日期" if self.selection_mode == "END" else "完成选择"
        self.range_label.setText(
            f"📅 {self.temp_start_date.toString('yyyy-MM-dd')} 至 "
            f"{self.temp_end_date.toString('yyyy-MM-dd')} (共 {days} 天)  |  {mode_text}"
        )

    def set_quick_range(self, days: int):
        """设置最近N天"""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-(days - 1))

        self.temp_start_date = start_date
        self.temp_end_date = end_date
        self.selection_mode = "START"

        self.update_range_highlight()
        self.update_range_label()
        self.date_range_changed.emit(start_date, end_date)

    def set_this_month(self):
        """设置为本月"""
        today = QDate.currentDate()
        start_date = QDate(today.year(), today.month(), 1)
        end_date = today

        self.temp_start_date = start_date
        self.temp_end_date = end_date
        self.selection_mode = "START"

        self.update_range_highlight()
        self.update_range_label()
        self.date_range_changed.emit(start_date, end_date)

    def set_last_month(self):
        """设置为上月"""
        today = QDate.currentDate()
        first_day_this_month = QDate(today.year(), today.month(), 1)
        last_day_last_month = first_day_this_month.addDays(-1)
        first_day_last_month = QDate(
            last_day_last_month.year(),
            last_day_last_month.month(),
            1
        )

        self.temp_start_date = first_day_last_month
        self.temp_end_date = last_day_last_month
        self.selection_mode = "START"

        self.update_range_highlight()
        self.update_range_label()
        self.date_range_changed.emit(first_day_last_month, last_day_last_month)

    def get_date_range(self):
        """获取选择的日期范围"""
        return self.temp_start_date, self.temp_end_date


class DateRangeDropdown(QFrame):
    """日期范围下拉面板容器"""

    accepted = Signal()
    rejected = Signal()

    def __init__(self, start_date: QDate, end_date: QDate, parent=None):
        """
        初始化下拉面板

        Args:
            start_date: 初始开始日期
            end_date: 初始结束日期
            parent: 父组件
        """
        super().__init__(parent)

        # 设置为弹出窗口
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # 保存日期范围
        self.start_date = start_date
        self.end_date = end_date

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 设置样式
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #d9d9d9;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 日期范围选择面板
        self.date_panel = ModernDateRangePanel(
            self.start_date,
            self.end_date,
            self
        )
        self.date_panel.date_range_changed.connect(self.on_date_range_changed)
        layout.addWidget(self.date_panel)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedWidth(80)
        cancel_btn.clicked.connect(self.on_cancel)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                background-color: #f5f5f5;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("确定")
        ok_btn.setFixedWidth(80)
        ok_btn.clicked.connect(self.on_accept)
        ok_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_date_range_changed(self, start_date: QDate, end_date: QDate):
        """日期范围改变"""
        self.start_date = start_date
        self.end_date = end_date

    def on_accept(self):
        """确定按钮点击"""
        self.accepted.emit()
        self.close()

    def on_cancel(self):
        """取消按钮点击"""
        self.rejected.emit()
        self.close()

    def show_below(self, widget: QWidget):
        """显示在指定控件下方"""
        # 计算位置
        pos = widget.mapToGlobal(QPoint(0, widget.height() + 4))
        self.move(pos)

        # 调整大小
        self.adjustSize()

        # 显示
        self.show()

    def get_date_range(self):
        """获取选择的日期范围"""
        return self.start_date, self.end_date


class DateRangePickerWidget(QWidget):
    """日期范围选择器主控件（点击展开下拉面板）"""

    # 信号：当日期范围改变时发出 (start_date: QDate, end_date: QDate)
    date_range_changed = Signal(QDate, QDate)

    def __init__(self, parent=None):
        """
        初始化日期范围选择器

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        # 当前选择的日期范围
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-6)  # 默认最近7天
        self.start_date = start_date
        self.end_date = end_date

        # 下拉面板
        self.dropdown = None

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 显示当前选择的日期范围（可点击）
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_label.setStyleSheet("""
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
        self.date_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.date_label.mousePressEvent = lambda event: self.show_dropdown()
        self.update_date_label()
        layout.addWidget(self.date_label)

        self.setLayout(layout)

    def update_date_label(self):
        """更新日期标签显示"""
        days = self.start_date.daysTo(self.end_date) + 1
        self.date_label.setText(
            f"📅 {self.start_date.toString('yyyy-MM-dd')} 至 "
            f"{self.end_date.toString('yyyy-MM-dd')} (共 {days} 天) ▼"
        )

    def show_dropdown(self):
        """显示下拉面板"""
        # 创建新的下拉面板
        self.dropdown = DateRangeDropdown(
            self.start_date,
            self.end_date,
            self
        )

        # 连接信号
        self.dropdown.accepted.connect(self.on_dropdown_accepted)
        self.dropdown.rejected.connect(self.on_dropdown_rejected)

        # 显示在控件下方
        self.dropdown.show_below(self.date_label)

    def on_dropdown_accepted(self):
        """下拉面板确认"""
        if self.dropdown:
            # 获取选择的日期范围
            new_start, new_end = self.dropdown.get_date_range()

            # 更新日期范围
            self.start_date = new_start
            self.end_date = new_end

            # 更新显示
            self.update_date_label()

            # 发出信号
            self.date_range_changed.emit(self.start_date, self.end_date)

    def on_dropdown_rejected(self):
        """下拉面板取消"""
        pass  # 不做任何操作，保持原来的日期范围

    def get_date_range(self):
        """获取选择的日期范围（QDate格式）"""
        return self.start_date, self.end_date

    def get_date_range_python(self):
        """获取选择的日期范围（Python date格式）"""
        return self.start_date.toPython(), self.end_date.toPython()
