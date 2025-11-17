"""
AI 配置弹窗模块
支持多平台选择、动态配置界面、测试连接功能
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox, QGroupBox, QFormLayout,
    QComboBox, QStackedWidget, QWidget, QSlider, QDoubleSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from infrastructure.config_manager import ConfigManager


class TestConnectionThread(QThread):
    """测试连接的后台线程"""
    finished = Signal(bool, str)  # (成功, 消息)

    def __init__(self, adapter):
        super().__init__()
        self.adapter = adapter

    def run(self):
        """执行连接测试"""
        try:
            success, message = self.adapter.test_connection()
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"测试失败: {str(e)}")


class AIConfigDialog(QDialog):
    """AI 配置对话框 - 支持多平台"""

    PROVIDERS = {
        'openai': 'OpenAI GPT',
        'deepseek': 'Deepseek',
        'zhipu': '智谱 GLM'
    }

    MODELS = {
        'openai': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'deepseek': ['deepseek-chat', 'deepseek-coder'],
        'zhipu': ['glm-4-plus', 'glm-4-air', 'glm-4-flash', 'glm-4']
    }

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_provider = config_manager.get('ai.provider', 'openai')
        self.test_thread = None
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("AI 平台配置")
        self.resize(750, 700)

        main_layout = QVBoxLayout()

        # === 平台选择区域 ===
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("选择 AI 平台:"))

        self.provider_combo = QComboBox()
        for key, name in self.PROVIDERS.items():
            self.provider_combo.addItem(name, key)
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()

        main_layout.addLayout(provider_layout)

        # === 平台配置区域 (使用 StackedWidget 动态切换) ===
        self.config_stack = QStackedWidget()

        # 创建三个平台的配置页面
        self.openai_page = self.create_openai_config_page()
        self.deepseek_page = self.create_deepseek_config_page()
        self.zhipu_page = self.create_zhipu_config_page()

        self.config_stack.addWidget(self.openai_page)
        self.config_stack.addWidget(self.deepseek_page)
        self.config_stack.addWidget(self.zhipu_page)

        main_layout.addWidget(self.config_stack)

        # === System Prompt 区域 ===
        system_prompt_group = QGroupBox("System Prompt (角色定义)")
        system_prompt_layout = QVBoxLayout()

        system_desc_label = QLabel(
            "提示: 定义 AI 的角色和能力，例如'你是一名资深技术主管...'"
        )
        system_desc_label.setWordWrap(True)
        system_desc_label.setStyleSheet("color: #666; font-size: 12px;")
        system_prompt_layout.addWidget(system_desc_label)

        self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setPlaceholderText("输入 System Prompt...")
        self.system_prompt_input.setFont(QFont("Consolas", 10))
        self.system_prompt_input.setMinimumHeight(100)
        system_prompt_layout.addWidget(self.system_prompt_input)

        reset_system_btn = QPushButton("恢复默认 System Prompt")
        reset_system_btn.clicked.connect(self.reset_system_prompt)
        system_prompt_layout.addWidget(reset_system_btn)

        system_prompt_group.setLayout(system_prompt_layout)
        main_layout.addWidget(system_prompt_group)

        # === User Prompt 区域 ===
        user_prompt_group = QGroupBox("User Prompt (任务说明)")
        user_prompt_layout = QVBoxLayout()

        user_desc_label = QLabel(
            "提示: 描述具体任务要求。使用 {commit_log} 作为占位符(必需), {example} 作为示例占位符(可选)"
        )
        user_desc_label.setWordWrap(True)
        user_desc_label.setStyleSheet("color: #666; font-size: 12px;")
        user_prompt_layout.addWidget(user_desc_label)

        self.user_prompt_input = QTextEdit()
        self.user_prompt_input.setPlaceholderText("输入 User Prompt 模板...")
        self.user_prompt_input.setFont(QFont("Consolas", 10))
        self.user_prompt_input.setMinimumHeight(150)
        user_prompt_layout.addWidget(self.user_prompt_input)

        reset_user_btn = QPushButton("恢复默认 User Prompt")
        reset_user_btn.clicked.connect(self.reset_user_prompt)
        user_prompt_layout.addWidget(reset_user_btn)

        user_prompt_group.setLayout(user_prompt_layout)
        main_layout.addWidget(user_prompt_group)

        # === 高级参数区域 ===
        advanced_group = QGroupBox("高级参数")
        advanced_layout = QVBoxLayout()

        # Temperature 说明
        temp_desc = QLabel(
            "Temperature: 控制生成文本的随机性。值越低越确定（更一致），值越高越随机（更有创意）。"
        )
        temp_desc.setWordWrap(True)
        temp_desc.setStyleSheet("color: #666; font-size: 12px;")
        advanced_layout.addWidget(temp_desc)

        # Temperature 滑块 + 数字输入框
        temp_control_layout = QHBoxLayout()
        temp_control_layout.addWidget(QLabel("Temperature:"))

        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setMinimum(0)
        self.temperature_slider.setMaximum(200)  # 0-200 对应 0.0-2.0
        self.temperature_slider.setValue(70)  # 默认 0.7
        self.temperature_slider.valueChanged.connect(self.on_temperature_slider_changed)
        temp_control_layout.addWidget(self.temperature_slider, 1)

        self.temperature_spinbox = QDoubleSpinBox()
        self.temperature_spinbox.setMinimum(0.0)
        self.temperature_spinbox.setMaximum(2.0)
        self.temperature_spinbox.setSingleStep(0.1)
        self.temperature_spinbox.setDecimals(2)
        self.temperature_spinbox.setValue(0.7)
        self.temperature_spinbox.valueChanged.connect(self.on_temperature_spinbox_changed)
        temp_control_layout.addWidget(self.temperature_spinbox)

        advanced_layout.addLayout(temp_control_layout)
        advanced_group.setLayout(advanced_layout)
        main_layout.addWidget(advanced_group)

        # === 报告示例区域 ===
        example_group = QGroupBox("报告示例 (可选)")
        example_layout = QVBoxLayout()

        # 启用示例复选框
        self.use_example_checkbox = QCheckBox("启用示例数据")
        self.use_example_checkbox.setChecked(False)
        example_layout.addWidget(self.use_example_checkbox)

        example_desc_label = QLabel(
            "提示: 勾选后，AI 会按照示例的格式生成报告。可以随时编辑示例内容，保存后生效。"
        )
        example_desc_label.setWordWrap(True)
        example_desc_label.setStyleSheet("color: #666; font-size: 12px;")
        example_layout.addWidget(example_desc_label)

        self.example_input = QTextEdit()
        self.example_input.setPlaceholderText(
            "示例:\n\n## 本周工作总结\n\n### 功能开发\n- 完成了用户认证模块的开发\n- 实现了数据导出功能\n\n### 问题修复\n- 修复了登录页面的显示bug\n- 解决了数据同步延迟问题"
        )
        self.example_input.setFont(QFont("Consolas", 10))
        self.example_input.setMinimumHeight(150)
        example_layout.addWidget(self.example_input)

        clear_example_btn = QPushButton("清空示例")
        clear_example_btn.clicked.connect(lambda: self.example_input.clear())
        self.clear_example_btn = clear_example_btn
        example_layout.addWidget(clear_example_btn)

        example_group.setLayout(example_layout)
        main_layout.addWidget(example_group)

        # === 按钮区 ===
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_config)
        self.save_btn.setDefault(True)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def create_openai_config_page(self) -> QWidget:
        """创建 OpenAI 配置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        config_group = QGroupBox("OpenAI 配置")
        form_layout = QFormLayout()

        # API Key
        self.openai_api_key = QLineEdit()
        self.openai_api_key.setEchoMode(QLineEdit.Password)
        self.openai_api_key.setPlaceholderText("输入 OpenAI API Key")
        form_layout.addRow("API Key:", self.openai_api_key)

        # Model
        self.openai_model = QComboBox()
        self.openai_model.setEditable(True)
        self.openai_model.addItems(self.MODELS['openai'])
        form_layout.addRow("模型:", self.openai_model)

        # Base URL
        self.openai_base_url = QLineEdit()
        self.openai_base_url.setPlaceholderText("可选,留空使用默认 https://api.openai.com/v1")
        form_layout.addRow("Base URL:", self.openai_base_url)

        config_group.setLayout(form_layout)
        layout.addWidget(config_group)

        # 测试连接按钮
        test_layout = QHBoxLayout()
        self.openai_test_btn = QPushButton("测试连接")
        self.openai_test_btn.clicked.connect(lambda: self.test_connection('openai'))
        test_layout.addWidget(self.openai_test_btn)

        self.openai_status_label = QLabel("状态: 未测试")
        self.openai_status_label.setStyleSheet("color: #666;")
        test_layout.addWidget(self.openai_status_label)
        test_layout.addStretch()

        layout.addLayout(test_layout)
        layout.addStretch()

        return page

    def create_deepseek_config_page(self) -> QWidget:
        """创建 Deepseek 配置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        config_group = QGroupBox("Deepseek 配置")
        form_layout = QFormLayout()

        # API Key
        self.deepseek_api_key = QLineEdit()
        self.deepseek_api_key.setEchoMode(QLineEdit.Password)
        self.deepseek_api_key.setPlaceholderText("输入 Deepseek API Key")
        form_layout.addRow("API Key:", self.deepseek_api_key)

        # Model
        self.deepseek_model = QComboBox()
        self.deepseek_model.setEditable(True)
        self.deepseek_model.addItems(self.MODELS['deepseek'])
        form_layout.addRow("模型:", self.deepseek_model)

        # Base URL
        self.deepseek_base_url = QLineEdit()
        self.deepseek_base_url.setPlaceholderText("可选,留空使用默认 https://api.deepseek.com")
        form_layout.addRow("Base URL:", self.deepseek_base_url)

        config_group.setLayout(form_layout)
        layout.addWidget(config_group)

        # 测试连接按钮
        test_layout = QHBoxLayout()
        self.deepseek_test_btn = QPushButton("测试连接")
        self.deepseek_test_btn.clicked.connect(lambda: self.test_connection('deepseek'))
        test_layout.addWidget(self.deepseek_test_btn)

        self.deepseek_status_label = QLabel("状态: 未测试")
        self.deepseek_status_label.setStyleSheet("color: #666;")
        test_layout.addWidget(self.deepseek_status_label)
        test_layout.addStretch()

        layout.addLayout(test_layout)
        layout.addStretch()

        return page

    def create_zhipu_config_page(self) -> QWidget:
        """创建智谱 GLM 配置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        config_group = QGroupBox("智谱 GLM 配置")
        form_layout = QFormLayout()

        # API Key
        self.zhipu_api_key = QLineEdit()
        self.zhipu_api_key.setEchoMode(QLineEdit.Password)
        self.zhipu_api_key.setPlaceholderText("输入智谱 API Key")
        form_layout.addRow("API Key:", self.zhipu_api_key)

        # Model
        self.zhipu_model = QComboBox()
        self.zhipu_model.setEditable(True)
        self.zhipu_model.addItems(self.MODELS['zhipu'])
        form_layout.addRow("模型:", self.zhipu_model)

        config_group.setLayout(form_layout)
        layout.addWidget(config_group)

        # 测试连接按钮
        test_layout = QHBoxLayout()
        self.zhipu_test_btn = QPushButton("测试连接")
        self.zhipu_test_btn.clicked.connect(lambda: self.test_connection('zhipu'))
        test_layout.addWidget(self.zhipu_test_btn)

        self.zhipu_status_label = QLabel("状态: 未测试")
        self.zhipu_status_label.setStyleSheet("color: #666;")
        test_layout.addWidget(self.zhipu_status_label)
        test_layout.addStretch()

        layout.addLayout(test_layout)
        layout.addStretch()

        return page

    def on_provider_changed(self, index):
        """平台切换"""
        provider_key = self.provider_combo.itemData(index)
        self.current_provider = provider_key
        self.config_stack.setCurrentIndex(index)

    def load_config(self):
        """加载配置"""
        # 加载当前选中的平台
        provider = self.config_manager.get('ai.provider', 'openai')
        for i in range(self.provider_combo.count()):
            if self.provider_combo.itemData(i) == provider:
                self.provider_combo.setCurrentIndex(i)
                break

        # 加载各平台配置
        self._load_openai_config()
        self._load_deepseek_config()
        self._load_zhipu_config()

        # 加载 System Prompt
        system_prompt = self.config_manager.get('ai.system_prompt', ConfigManager.DEFAULT_SYSTEM_PROMPT)
        self.system_prompt_input.setPlainText(system_prompt)

        # 加载 User Prompt
        user_prompt = self.config_manager.get('ai.user_prompt', ConfigManager.DEFAULT_USER_PROMPT)
        self.user_prompt_input.setPlainText(user_prompt)

        # 加载 Temperature
        temperature = self.config_manager.get('ai.temperature', 0.7)
        self.temperature_spinbox.setValue(temperature)
        self.temperature_slider.setValue(int(temperature * 100))

        # 加载报告示例和启用状态
        use_example = self.config_manager.get('ai.use_example', False)
        self.use_example_checkbox.setChecked(use_example)

        report_example = self.config_manager.get('ai.report_example', '')
        self.example_input.setPlainText(report_example)

    def _load_openai_config(self):
        """加载 OpenAI 配置"""
        config = self.config_manager.get('ai.configs.openai', {})
        self.openai_api_key.setText(config.get('api_key', ''))
        self.openai_model.setCurrentText(config.get('model', 'gpt-4o-mini'))
        self.openai_base_url.setText(config.get('base_url', ''))

    def _load_deepseek_config(self):
        """加载 Deepseek 配置"""
        config = self.config_manager.get('ai.configs.deepseek', {})
        self.deepseek_api_key.setText(config.get('api_key', ''))
        self.deepseek_model.setCurrentText(config.get('model', 'deepseek-chat'))
        self.deepseek_base_url.setText(config.get('base_url', ''))

    def _load_zhipu_config(self):
        """加载智谱 GLM 配置"""
        config = self.config_manager.get('ai.configs.zhipu', {})
        self.zhipu_api_key.setText(config.get('api_key', ''))
        self.zhipu_model.setCurrentText(config.get('model', 'glm-4-flash'))

    def reset_system_prompt(self):
        """重置 System Prompt 为默认值"""
        reply = QMessageBox.question(
            self,
            "确认重置",
            "确定要恢复默认 System Prompt 吗?当前内容将被覆盖。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.system_prompt_input.setPlainText(ConfigManager.DEFAULT_SYSTEM_PROMPT)

    def reset_user_prompt(self):
        """重置 User Prompt 为默认值"""
        reply = QMessageBox.question(
            self,
            "确认重置",
            "确定要恢复默认 User Prompt 模板吗?当前内容将被覆盖。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.user_prompt_input.setPlainText(ConfigManager.DEFAULT_USER_PROMPT)

    def on_temperature_slider_changed(self, value: int):
        """Temperature 滑块变化时更新数字输入框"""
        # 暂时阻止 spinbox 的信号，避免循环触发
        self.temperature_spinbox.blockSignals(True)
        self.temperature_spinbox.setValue(value / 100.0)
        self.temperature_spinbox.blockSignals(False)

    def on_temperature_spinbox_changed(self, value: float):
        """Temperature 数字输入框变化时更新滑块"""
        # 暂时阻止 slider 的信号，避免循环触发
        self.temperature_slider.blockSignals(True)
        self.temperature_slider.setValue(int(value * 100))
        self.temperature_slider.blockSignals(False)

    def test_connection(self, provider: str):
        """测试连接"""
        # 获取对应平台的配置
        config = self._get_provider_config(provider)

        if not config.get('api_key'):
            QMessageBox.warning(self, "警告", "请先填写 API Key")
            return

        # 创建临时适配器测试连接
        try:
            from infrastructure.ai_client import AiClientFactory

            # 临时创建配置
            temp_config_manager = ConfigManager("temp_test_config.json")
            temp_config_manager.set('ai.provider', provider)
            temp_config_manager.set(f'ai.configs.{provider}', config)
            temp_config_manager.set('ai.system_prompt', "你是一个AI助手")
            temp_config_manager.set('ai.user_prompt', "测试连接")

            adapter = AiClientFactory.create(temp_config_manager)

            # 更新状态
            status_label = self._get_status_label(provider)
            test_btn = self._get_test_button(provider)
            status_label.setText("状态: 测试中...")
            status_label.setStyleSheet("color: #FF9800;")
            test_btn.setEnabled(False)

            # 在后台线程测试
            self.test_thread = TestConnectionThread(adapter)
            self.test_thread.finished.connect(
                lambda success, msg: self.on_test_finished(provider, success, msg)
            )
            self.test_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建测试客户端失败: {str(e)}")

    def on_test_finished(self, provider: str, success: bool, message: str):
        """测试完成"""
        status_label = self._get_status_label(provider)
        test_btn = self._get_test_button(provider)

        if success:
            status_label.setText(f"状态: ✓ {message}")
            status_label.setStyleSheet("color: #4CAF50;")
            QMessageBox.information(self, "成功", message)
        else:
            status_label.setText(f"状态: ✗ 连接失败")
            status_label.setStyleSheet("color: #F44336;")
            QMessageBox.warning(self, "失败", message)

        test_btn.setEnabled(True)

    def _get_provider_config(self, provider: str) -> dict:
        """获取平台配置"""
        if provider == 'openai':
            config = {
                'api_key': self.openai_api_key.text().strip(),
                'model': self.openai_model.currentText().strip(),
            }
            base_url = self.openai_base_url.text().strip()
            if base_url:
                config['base_url'] = base_url
            return config
        elif provider == 'deepseek':
            config = {
                'api_key': self.deepseek_api_key.text().strip(),
                'model': self.deepseek_model.currentText().strip(),
            }
            base_url = self.deepseek_base_url.text().strip()
            if base_url:
                config['base_url'] = base_url
            return config
        elif provider == 'zhipu':
            return {
                'api_key': self.zhipu_api_key.text().strip(),
                'model': self.zhipu_model.currentText().strip(),
            }
        return {}

    def _get_status_label(self, provider: str) -> QLabel:
        """获取状态标签"""
        if provider == 'openai':
            return self.openai_status_label
        elif provider == 'deepseek':
            return self.deepseek_status_label
        elif provider == 'zhipu':
            return self.zhipu_status_label

    def _get_test_button(self, provider: str) -> QPushButton:
        """获取测试按钮"""
        if provider == 'openai':
            return self.openai_test_btn
        elif provider == 'deepseek':
            return self.deepseek_test_btn
        elif provider == 'zhipu':
            return self.zhipu_test_btn

    def validate_config(self) -> bool:
        """验证配置"""
        # 验证 User Prompt（需要包含 {commit_log} 占位符）
        user_prompt = self.user_prompt_input.toPlainText().strip()
        if not user_prompt:
            QMessageBox.warning(self, "验证失败", "User Prompt 模板不能为空")
            return False

        if '{commit_log}' not in user_prompt:
            reply = QMessageBox.question(
                self,
                "警告",
                "User Prompt 模板中没有找到 {commit_log} 占位符,这可能导致无法正确生成报告。\n\n是否仍要保存?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return False

        # 验证当前平台配置
        config = self._get_provider_config(self.current_provider)
        if not config.get('api_key'):
            QMessageBox.warning(
                self,
                "验证失败",
                f"{self.PROVIDERS[self.current_provider]} 的 API Key 不能为空"
            )
            return False

        return True

    def save_config(self):
        """保存配置"""
        if not self.validate_config():
            return

        # 保存当前选中的平台
        self.config_manager.set('ai.provider', self.current_provider)

        # 保存各平台配置
        self.config_manager.set('ai.configs.openai', self._get_provider_config('openai'))
        self.config_manager.set('ai.configs.deepseek', self._get_provider_config('deepseek'))
        self.config_manager.set('ai.configs.zhipu', self._get_provider_config('zhipu'))

        # 保存 System Prompt
        self.config_manager.set('ai.system_prompt', self.system_prompt_input.toPlainText().strip())

        # 保存 User Prompt
        self.config_manager.set('ai.user_prompt', self.user_prompt_input.toPlainText().strip())

        # 保存旧版 prompt 用于向后兼容
        self.config_manager.set('ai.prompt', self.user_prompt_input.toPlainText().strip())

        # 保存 Temperature
        self.config_manager.set('ai.temperature', self.temperature_spinbox.value())

        # 保存报告示例和启用状态
        self.config_manager.set('ai.use_example', self.use_example_checkbox.isChecked())
        self.config_manager.set('ai.report_example', self.example_input.toPlainText().strip())

        # 持久化到文件
        if self.config_manager.save_config():
            QMessageBox.information(
                self,
                "成功",
                f"AI 配置已保存\n当前平台: {self.PROVIDERS[self.current_provider]}"
            )
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "配置保存失败")
