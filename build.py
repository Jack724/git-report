#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Report Generator - 跨平台构建脚本
支持在 Windows CMD/PowerShell/Git Bash/Linux/macOS 中运行
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from datetime import datetime

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


def print_banner(text):
    """打印标题横幅"""
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def print_step(step, total, description):
    """打印步骤信息"""
    print(f"[{step}/{total}] {description}...")


def check_git_bash():
    """检测是否在 Git Bash 中运行 build.bat"""
    if os.name == 'nt' and 'MSYSTEM' in os.environ:
        return True
    return False


def warn_git_bash():
    """显示 Git Bash 警告"""
    print_banner("⚠️  Git Bash 环境检测")
    print("检测到您正在 Git Bash 环境中运行构建。")
    print()
    print("build.bat 无法在 Git Bash 中正确运行（批处理语法不兼容）。")
    print()
    print("✅ 推荐方式：")
    print("  1. 继续使用 Python 脚本（当前方式）: python build.py")
    print("  2. 或在 Windows 命令提示符（CMD）中运行: build.bat")
    print()
    print("按任意键继续使用 Python 构建...")
    try:
        input()
    except:
        pass
    print()


def clean_build_dirs():
    """清理旧的构建目录"""
    print_step(1, 6, "清理旧构建文件")

    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  ✓ 已删除 {dir_name}/ 目录")
            except Exception as e:
                print(f"  ⚠ 无法删除 {dir_name}/: {e}")
        else:
            print(f"  - {dir_name}/ 不存在，跳过")

    print("完成。")
    print()


def check_pyinstaller():
    """检查并安装 PyInstaller"""
    print_step(2, 6, "检查 PyInstaller")

    try:
        import PyInstaller
        print("  ✓ PyInstaller 已安装")
        print()
        return True
    except ImportError:
        print("  ✗ PyInstaller 未安装")
        print()
        print("正在安装 PyInstaller...")

        # 尝试使用 pip 安装
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                check=True,
                capture_output=True
            )
            print("  ✓ PyInstaller 安装成功")
            print()
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ✗ 安装失败: {e}")
            print()
            print("请手动安装 PyInstaller:")
            print("  pip install pyinstaller")
            print("  或")
            print("  uv pip install pyinstaller")
            return False


def run_pyinstaller():
    """运行 PyInstaller 构建"""
    print_step(3, 6, "构建应用程序（这可能需要几分钟）")

    if not os.path.exists('git-report.spec'):
        print("  ✗ 错误: 找不到 git-report.spec 文件")
        return False

    try:
        # 运行 PyInstaller
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "git-report.spec"],
            check=False,
            capture_output=False  # 显示输出
        )

        if result.returncode != 0:
            print()
            print("  ✗ 构建失败，请检查上面的错误信息")
            print()
            print("常见问题:")
            print("  - 缺少依赖: pip install -r requirements.txt")
            print("  - 导入错误: 检查 git-report.spec 中的 hiddenimports")
            print("  - 资源错误: 检查 git-report.spec 中的 datas")
            return False

        print()
        print("  ✓ 构建完成")
        print()
        return True

    except Exception as e:
        print(f"  ✗ 构建失败: {e}")
        return False


def run_cleanup():
    """运行清理脚本"""
    print_step(4, 7, "清理冗余文件（PySide6 模块）")

    if not os.path.exists("cleanup_dist.py"):
        print("  ⚠ 找不到 cleanup_dist.py")
        print("  跳过清理步骤，打包大小可能较大")
        print()
        return False

    try:
        # 运行清理脚本
        result = subprocess.run(
            [sys.executable, "cleanup_dist.py"],
            check=False,
            capture_output=False  # 显示输出
        )

        if result.returncode != 0:
            print()
            print("  ⚠ 清理脚本执行失败，但构建可以继续")
            print()
            return False

        print()
        print("  ✓ 清理完成")
        print()
        return True

    except Exception as e:
        print(f"  ⚠ 清理失败: {e}")
        print()
        return False


def create_data_dirs():
    """创建数据目录"""
    print_step(5, 7, "创建数据目录")

    base_dir = Path("dist/GitReport/data")
    subdirs = ["logs", "reports", "cache"]

    try:
        base_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建 {base_dir}/")

        for subdir in subdirs:
            (base_dir / subdir).mkdir(exist_ok=True)
            print(f"  ✓ 创建 {base_dir}/{subdir}/")

        print("数据目录创建完成。")
        print()
        return True

    except Exception as e:
        print(f"  ⚠ 创建目录失败: {e}")
        print()
        return False


def generate_version_info():
    """生成版本信息文件"""
    print_step(6, 7, "生成构建信息")

    try:
        version_file = Path("dist/GitReport/VERSION.txt")
        with version_file.open("w", encoding="utf-8") as f:
            f.write("Git Report Generator v1.0.0\n")
            f.write(f"构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"构建平台: {platform.system()} {platform.release()}\n")
            f.write(f"Python 版本: {sys.version.split()[0]}\n")

        print(f"  ✓ 版本信息已写入 {version_file}")
        print()
        return True

    except Exception as e:
        print(f"  ⚠ 生成版本信息失败: {e}")
        print()
        return False


def show_package_size():
    """显示打包后的大小"""
    print_step(7, 7, "统计打包大小")

    dist_dir = Path("dist/GitReport")
    if not dist_dir.exists():
        print("  ⚠ dist/GitReport 目录不存在")
        print()
        return

    try:
        total_size = 0
        for file in dist_dir.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size

        size_mb = total_size / (1024 * 1024)
        print(f"  打包大小: {size_mb:.1f} MB")
        print()

    except Exception as e:
        print(f"  ⚠ 计算大小失败: {e}")
        print()


def show_summary():
    """显示构建完成信息"""
    print_banner("✅ 构建完成")

    exe_name = "GitReport.exe" if os.name == 'nt' else "GitReport"

    print(f"输出目录: dist{os.sep}GitReport{os.sep}")
    print(f"主程序: dist{os.sep}GitReport{os.sep}{exe_name}")
    print()
    print("重要提示:")
    print("  1. 首次运行需配置 AI API Key")
    print("  2. 需要安装 Git 命令行工具")
    print("  3. data 文件夹用于存储配置、日志和报告")
    print()
    print("后续步骤:")
    print(f"  - 测试运行: cd dist{os.sep}GitReport && {exe_name}")
    print("  - 创建安装包: 使用 Inno Setup 或 NSIS")
    print()


def main():
    """主函数"""
    # 打印欢迎信息
    print_banner("Git Report Generator - 构建脚本")

    # 检测 Git Bash 环境
    if check_git_bash():
        warn_git_bash()

    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要 Python 3.8 或更高版本")
        print(f"当前版本: Python {sys.version.split()[0]}")
        sys.exit(1)

    print(f"Python 版本: {sys.version.split()[0]}")
    print(f"平台: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print()

    # 执行构建步骤
    try:
        # 1. 清理
        clean_build_dirs()

        # 2. 检查 PyInstaller
        if not check_pyinstaller():
            sys.exit(1)

        # 3. 运行 PyInstaller
        if not run_pyinstaller():
            sys.exit(1)

        # 4. 清理冗余文件
        run_cleanup()

        # 5. 创建数据目录
        create_data_dirs()

        # 6. 生成版本信息
        generate_version_info()

        # 7. 显示大小
        show_package_size()

        # 显示完成信息
        show_summary()

        # 等待用户按键（Windows 下）
        if os.name == 'nt':
            print("按任意键退出...")
            try:
                input()
            except:
                pass

        sys.exit(0)

    except KeyboardInterrupt:
        print()
        print("⚠️  构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ 构建失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
