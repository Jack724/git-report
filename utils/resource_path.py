"""
资源路径处理工具
支持开发环境和 PyInstaller 打包环境
"""
import os
import sys


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径（静态资源：图标、样式等）

    在开发环境中，从项目根目录获取资源
    在打包环境中，从 PyInstaller 临时目录获取资源

    Args:
        relative_path: 相对于项目根目录的路径

    Returns:
        资源文件的绝对路径

    Example:
        >>> icon_path = get_resource_path('app_icon.ico')
        >>> styles_path = get_resource_path('ui/themes/styles.qss')
    """
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境：使用项目根目录
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_data_path(relative_path=""):
    """
    获取数据目录路径（动态数据：配置、日志、报告等）

    开发环境：使用项目根目录下的 data/
    打包环境：使用可执行文件所在目录的 data/

    这样确保：
    1. 配置文件可以持久化保存
    2. 日志文件可以正常写入
    3. 报告文件可以正常导出
    4. 避免权限问题（不写入 Program Files）

    Args:
        relative_path: 相对于数据目录的路径（可选）

    Returns:
        数据文件的绝对路径

    Example:
        >>> config_path = get_data_path("config.json")
        >>> log_dir = get_data_path("logs")
        >>> data_dir = get_data_path()  # 只获取 data 目录本身
    """
    if getattr(sys, 'frozen', False):
        # 打包环境：使用可执行文件所在目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境：使用项目根目录
        base_path = os.path.abspath(".")

    data_dir = os.path.join(base_path, "data")

    # 确保 data 目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 如果指定了相对路径，返回完整路径
    if relative_path:
        full_path = os.path.join(data_dir, relative_path)
        # 如果是目录路径，确保目录存在
        if not os.path.splitext(relative_path)[1]:  # 没有文件扩展名，判断为目录
            if not os.path.exists(full_path):
                os.makedirs(full_path)
        return full_path

    return data_dir


def is_frozen():
    """
    检查程序是否在打包环境中运行

    Returns:
        bool: True 表示打包环境，False 表示开发环境

    Example:
        >>> if is_frozen():
        >>>     print("Running in packaged mode")
        >>> else:
        >>>     print("Running in development mode")
    """
    return getattr(sys, 'frozen', False)
