#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理打包后的冗余文件
在 PyInstaller 打包后运行此脚本以删除不需要的 PySide6 模块
这些模块在 git-report.spec 的 excludes 列表中，但 PyInstaller 仍然会打包二进制文件
"""

import os
import sys
import shutil
import glob
from pathlib import Path

# 设置 UTF-8 编码输出（避免 Git Bash 中的编码问题）
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def get_size(path):
    """计算文件或目录大小（字节）"""
    if os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        return sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, _, filenames in os.walk(path)
            for filename in filenames
        )
    return 0


def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def remove_items(dist_dir, patterns, category_name=""):
    """删除匹配模式的文件和目录"""
    total_saved = 0
    removed_count = 0
    skipped = []

    if category_name:
        print(f"\n{'='*70}")
        print(f"清理: {category_name}")
        print(f"{'='*70}")

    for pattern in patterns:
        full_pattern = os.path.join(dist_dir, pattern)
        matches = glob.glob(full_pattern, recursive=True)

        if not matches:
            print(f"[SKIP] 未找到: {pattern}")
            skipped.append(pattern)
            continue

        for match in matches:
            # 跳过已删除的文件
            if not os.path.exists(match):
                continue

            size = get_size(match)
            relative_path = os.path.relpath(match, dist_dir)

            try:
                if os.path.isfile(match):
                    os.remove(match)
                    print(f"[OK] 删除文件: {relative_path} ({format_size(size)})")
                elif os.path.isdir(match):
                    shutil.rmtree(match)
                    print(f"[OK] 删除目录: {relative_path}/ ({format_size(size)})")

                total_saved += size
                removed_count += 1
            except Exception as e:
                print(f"[ERROR] 删除失败: {relative_path} - {e}")
                skipped.append(pattern)

    return removed_count, total_saved, skipped


def main():
    """主函数"""
    dist_dir = "dist/GitReport/_internal"

    # 检查目录是否存在
    if not os.path.exists(dist_dir):
        print(f"错误: 找不到目录 {dist_dir}")
        print("请先运行 build.py 进行打包")
        return 1

    print("="*70)
    print("Git Report - 打包文件清理工具")
    print("="*70)
    print(f"\n目标目录: {dist_dir}")

    # 计算清理前的大小
    print("\n正在计算清理前的大小...")
    size_before = get_size("dist/GitReport")
    print(f"清理前总大小: {format_size(size_before)}")

    # 1. WebEngine 浏览器引擎 (~194 MB - 最大的冗余)
    webengine_patterns = [
        "PySide6/Qt6WebEngineCore.dll",
        "PySide6/Qt6WebEngineWidgets.dll",
        "PySide6/Qt6WebEngineQuick.dll",
        "PySide6/Qt6WebEngineQuickDelegatesQml.dll",
        "PySide6/QtWebEngineProcess.exe",
        "PySide6/QtWebEngineCore.pyi",
        "PySide6/QtWebEngineWidgets.pyi",
        "PySide6/QtWebEngineQuick.pyi",
        "PySide6/qml/QtWebEngine",
        "PySide6/resources",  # WebEngine 资源
    ]

    # 2. 3D 模块 (~35-40 MB)
    qt3d_patterns = [
        "PySide6/Qt63DAnimation.dll",
        "PySide6/Qt63DCore.dll",
        "PySide6/Qt63DExtras.dll",
        "PySide6/Qt63DInput.dll",
        "PySide6/Qt63DLogic.dll",
        "PySide6/Qt63DRender.dll",
        "PySide6/Qt6Quick3D.dll",
        "PySide6/Qt6Quick3DAssetImport.dll",
        "PySide6/Qt6Quick3DAssetUtils.dll",
        "PySide6/Qt6Quick3DEffects.dll",
        "PySide6/Qt6Quick3DHelpers.dll",
        "PySide6/Qt6Quick3DHelpersImpl.dll",
        "PySide6/Qt6Quick3DIblBaker.dll",
        "PySide6/Qt6Quick3DParticles.dll",
        "PySide6/Qt6Quick3DParticleEffects.dll",
        "PySide6/Qt6Quick3DRuntimeRender.dll",
        "PySide6/Qt6Quick3DUtils.dll",
        "PySide6/Qt6DataVisualization.dll",
        "PySide6/Qt6Graphs.dll",
        "PySide6/qml/QtQuick3D",
        "PySide6/qml/QtCharts",
        "PySide6/qml/QtDataVisualization",
        "PySide6/qml/QtGraphs",
    ]

    # 3. Designer 工具 (~7.5 MB)
    designer_patterns = [
        "PySide6/Qt6Designer.dll",
        "PySide6/Qt6DesignerComponents.dll",
        "PySide6/Qt6QmlCompiler.dll",
        "PySide6/designer.exe",
        "PySide6/plugins/designer",
    ]

    # 4. PDF 支持 (~5 MB)
    pdf_patterns = [
        "PySide6/Qt6Pdf.dll",
        "PySide6/Qt6PdfWidgets.dll",
    ]

    # 5. Charts 图表 (~2 MB)
    charts_patterns = [
        "PySide6/Qt6Charts.dll",
    ]

    # 6. Multimedia 多媒体 (~1 MB)
    multimedia_patterns = [
        "PySide6/Qt6Multimedia.dll",
        "PySide6/Qt6MultimediaWidgets.dll",
        "PySide6/plugins/multimedia",
    ]

    # 7. 其他不需要的模块 (~20 MB)
    other_patterns = [
        "PySide6/Qt6Location.dll",
        "PySide6/Qt6Sensors.dll",
        "PySide6/Qt6TextToSpeech.dll",
        "PySide6/Qt6SerialPort.dll",
        "PySide6/Qt6SerialBus.dll",
        "PySide6/Qt6Nfc.dll",
        "PySide6/Qt6Bluetooth.dll",
        "PySide6/Qt6RemoteObjects.dll",
        "PySide6/Qt6Scxml.dll",
        "PySide6/Qt6Positioning.dll",
        "PySide6/Qt6WebSockets.dll",
    ]

    # 8. 不需要的插件目录
    plugin_patterns = [
        "PySide6/plugins/sqldrivers",  # 数据库驱动
        "PySide6/plugins/assetimporters",  # 3D 资源导入
        "PySide6/plugins/sceneparsers",  # 3D 场景解析
        "PySide6/plugins/renderers",  # 3D 渲染器
        "PySide6/plugins/qmltooling",  # QML 工具
        "PySide6/plugins/canbus",  # CAN 总线
        "PySide6/plugins/geoservices",  # 地理服务
        "PySide6/plugins/position",  # 定位服务
        "PySide6/plugins/texttospeech",  # 语音合成
        "PySide6/plugins/sensors",  # 传感器
        "PySide6/plugins/networkinformation",  # 网络信息
    ]

    # 9. QML 虚拟键盘和未使用的主题 (~7 MB)
    qml_patterns = [
        "PySide6/qml/QtQuick/VirtualKeyboard",  # 虚拟键盘 (~4.8 MB)
        "PySide6/qml/QtQuick/Controls/Material",  # 未使用的主题
        "PySide6/qml/QtQuick/Controls/Windows",
        "PySide6/qml/QtQuick/Controls/Fusion",
        "PySide6/qml/QtQuick/Controls/Universal",
        "PySide6/qml/QtQuick/Controls/Imagine",
        "PySide6/qml/QtQuick/Controls/iOS",
        "PySide6/qml/QtQuick/Controls/macOS",
    ]

    # 执行清理
    total_removed = 0
    total_saved = 0

    categories = [
        (webengine_patterns, "WebEngine 浏览器引擎 (~194 MB)"),
        (qt3d_patterns, "3D 图形模块 (~35-40 MB)"),
        (designer_patterns, "Designer 工具 (~7.5 MB)"),
        (pdf_patterns, "PDF 支持 (~5 MB)"),
        (charts_patterns, "图表库 (~2 MB)"),
        (multimedia_patterns, "多媒体模块 (~1 MB)"),
        (other_patterns, "其他未使用模块 (~20 MB)"),
        (plugin_patterns, "不需要的插件"),
        (qml_patterns, "QML 虚拟键盘和主题 (~7 MB)"),
    ]

    for patterns, category_name in categories:
        count, saved, _ = remove_items(dist_dir, patterns, category_name)
        total_removed += count
        total_saved += saved

    # 计算清理后的大小
    print(f"\n{'='*70}")
    print("正在计算清理后的大小...")
    size_after = get_size("dist/GitReport")

    # 显示总结
    print(f"\n{'='*70}")
    print("清理完成")
    print(f"{'='*70}")
    print(f"清理前大小:   {format_size(size_before)}")
    print(f"清理后大小:   {format_size(size_after)}")
    print(f"节省空间:     {format_size(total_saved)} ({total_saved / size_before * 100:.1f}%)")
    print(f"删除项目数:   {total_removed}")
    print(f"{'='*70}")

    # 如果清理后仍然很大，给出警告
    if size_after > 300 * 1024 * 1024:  # 300 MB
        print("\n⚠️  警告: 清理后的大小仍然超过 300 MB")
        print("可能还有其他大文件未被清理。请检查:")
        print("  - dist/GitReport/_internal/PySide6/ 目录")
        print("  - 查找大于 10 MB 的文件")

    return 0


if __name__ == "__main__":
    exit(main())
