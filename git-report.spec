# -*- mode: python ; coding: utf-8 -*-
"""
Git-Report PyInstaller 配置文件
用于将 Python 项目打包成 Windows 可执行文件
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 项目根目录
project_root = os.path.abspath('.')

# 收集 qfluentwidgets 的所有数据文件和子模块
qfluentwidgets_datas = collect_data_files('qfluentwidgets')
qfluentwidgets_hiddenimports = collect_submodules('qfluentwidgets')

# 收集 PySide6 插件和数据
pyside6_datas = collect_data_files('PySide6')

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        # 应用图标
        ('app_icon.ico', '.'),
        ('app_icon.png', '.'),
        # QSS 样式文件
        ('ui/themes/styles.qss', 'ui/themes'),
        # qfluentwidgets 资源
        *qfluentwidgets_datas,
        # PySide6 资源
        *pyside6_datas,
    ],
    hiddenimports=[
        # 工具模块
        'utils',
        'utils.resource_path',
        # 应用层
        'app',
        'app.bootstrap',
        'app.dependencies',
        'app.main',
        # 核心实体
        'core',
        'core.entities',
        'core.entities.repo_model',
        'core.entities.commit_model',
        'core.entities.ai_config_model',
        # 核心服务
        'core.services',
        'core.services.git_service',
        'core.services.repo_scanner',
        'core.services.formatter',
        # 基础设施
        'infrastructure',
        'infrastructure.config_manager',
        'infrastructure.logger',
        'infrastructure.ai_client',
        # AI 适配器
        'infrastructure.adapters',
        'infrastructure.adapters.base',
        'infrastructure.adapters.openai_adapter',
        'infrastructure.adapters.deepseek_adapter',
        'infrastructure.adapters.zhipu_adapter',
        # UI 主窗口
        'ui',
        'ui.main_window',
        # UI 对话框
        'ui.dialogs',
        'ui.dialogs.ai_config_dialog',
        'ui.dialogs.commit_log_dialog',
        'ui.dialogs.progress_dialog',
        'ui.dialogs.repo_config_dialog',
        'ui.dialogs.repo_detail_dialog',
        'ui.dialogs.repo_scan_dialog',
        # UI 组件
        'ui.widgets',
        'ui.widgets.date_range_picker',
        'ui.widgets.repo_list_widget',
        # UI 主题
        'ui.themes',
        'ui.themes.theme_manager',
        'ui.themes.icons',
        # qfluentwidgets 子模块
        *qfluentwidgets_hiddenimports,
        # GitPython 依赖
        'git',
        'git.repo',
        'git.repo.base',
        'git.cmd',
        'git.util',
        'git.objects',
        'git.objects.base',
        'git.objects.blob',
        'git.objects.commit',
        'git.objects.tree',
        'git.index',
        'git.config',
        # HTTP 请求库
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        # Markdown 处理
        'markdown2',
        # 日期处理
        'dateutil',
        'dateutil.parser',
        'dateutil.tz',
        # JSON 处理
        'json',
        'uuid',
        # 其他标准库
        'threading',
        'logging',
        'logging.handlers',
        'datetime',
        'collections',
        're',
    ],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'pytest',
        'setuptools',
        '_pytest',
        'unittest',
        'test',
        'tests',
        'distutils',

        # PySide6 冗余模块排除（减少约 270 MB）
        # WebEngine 浏览器引擎（193 MB - 最大的冗余）
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineQuick',

        # 3D 图形模块（14 MB）
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DExtras',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DRender',
        'PySide6.QtQuick3D',
        'PySide6.QtDataVisualization',
        'PySide6.QtGraphs',

        # 图表库（2 MB）
        'PySide6.QtCharts',

        # Designer 工具（11 MB）
        'PySide6.QtDesigner',
        'PySide6.QtUiTools',

        # 多媒体（1 MB）
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',

        # PDF 支持（5 MB）
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',

        # 其他不需要的模块（7 MB）
        'PySide6.QtLocation',
        'PySide6.QtSensors',
        'PySide6.QtTextToSpeech',
        'PySide6.QtSerialPort',
        'PySide6.QtSerialBus',
        'PySide6.QtNfc',
        'PySide6.QtBluetooth',
        'PySide6.QtRemoteObjects',
        'PySide6.QtScxml',
        'PySide6.QtPositioning',
        'PySide6.QtWebSockets',
    ],
    noarchive=False,
    optimize=2,  # 字节码优化 (0=无, 1=基础, 2=完全)
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GitReport',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用 UPX 压缩（需要安装 UPX）
    console=False,  # 不显示控制台窗口（GUI 应用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # Windows 应用图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GitReport',
)
