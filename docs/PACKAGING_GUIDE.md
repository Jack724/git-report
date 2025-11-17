# Git-Report 打包指南

## 📦 打包成 Windows 可执行文件（EXE）

本项目已配置好 PyInstaller 打包环境，可以一键打包成独立的 Windows 应用程序。

## 🚀 快速开始

### 方式 1: 使用构建脚本（推荐）

```bash
# 直接运行构建脚本
build.bat
```

脚本会自动：
1. 清理旧的构建文件
2. 检查并安装 PyInstaller
3. 执行打包
4. 创建数据目录结构
5. 生成构建信息

### 方式 2: 手动打包

```bash
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 执行打包
pyinstaller git-report.spec

# 3. 创建数据目录
mkdir dist\GitReport\data
mkdir dist\GitReport\data\logs
mkdir dist\GitReport\data\reports
mkdir dist\GitReport\data\cache
```

## 📂 打包输出

打包完成后，在 `dist/GitReport/` 目录下会生成以下文件：

```
dist/GitReport/
├── GitReport.exe          # 主程序（约 150-200 MB）
├── app_icon.ico           # 应用图标
├── app_icon.png
├── ui/
│   └── themes/
│       └── styles.qss     # UI 样式文件
├── data/                  # 数据目录（运行时创建）
│   ├── config.json       # 配置文件
│   ├── logs/             # 日志目录
│   ├── reports/          # 报告输出目录
│   └── cache/            # 缓存目录
├── PySide6/              # Qt 库
├── _internal/            # PyInstaller 内部文件
└── [其他依赖库和 DLL]
```

## ⚙️ 技术说明

### 打包配置

项目使用 **文件夹模式**打包（而非单文件模式），原因：
- GitPython 需要调用系统 Git 命令
- 数据目录需要持久化
- 文件夹模式启动更快
- 便于调试和问题排查

### 关键组件

1. **资源路径处理**: `utils/resource_path.py`
   - 自动适配开发环境和打包环境
   - 处理图标、样式等静态资源
   - 处理配置、日志等动态数据

2. **PyInstaller 配置**: `git-report.spec`
   - 定义打包入口、资源、依赖
   - 配置隐藏导入（hidden imports）
   - 排除不需要的模块以减小体积

3. **构建脚本**: `build.bat`
   - 自动化构建流程
   - 环境检查和准备
   - 后处理和验证

### 已修改的文件

为支持打包，以下文件已修改：

1. **pyproject.toml** - 修复依赖（PyQt5 → PySide6）
2. **main.py** - 使用资源路径工具
3. **infrastructure/logger.py** - 使用数据路径工具
4. **infrastructure/config_manager.py** - 使用数据路径工具
5. **ui/main_window.py** - 使用资源路径工具

## ✅ 测试清单

打包完成后，需要测试以下功能：

### 基础功能
- [ ] 程序能否正常启动
- [ ] 窗口图标是否正确显示
- [ ] Fluent Design 主题是否正常
- [ ] 界面布局是否正确

### 核心功能
- [ ] 添加和扫描 Git 仓库
- [ ] 拉取提交记录
- [ ] 选择日期范围
- [ ] 筛选作者
- [ ] 查看提交日志

### AI 功能
- [ ] AI 配置对话框
- [ ] 测试 AI 连接
- [ ] 生成报告
- [ ] 导出报告

### 数据持久化
- [ ] 配置文件保存和加载
- [ ] 日志文件正常写入
- [ ] 报告文件正常导出
- [ ] 缓存功能正常

### 异常处理
- [ ] 无 Git 环境时的提示
- [ ] 网络异常时的处理
- [ ] API 错误时的提示
- [ ] 配置文件损坏时的恢复

## ⚠️ 重要注意事项

### 1. Git 依赖

**打包后的程序仍需要系统安装 Git！**

- 程序使用 GitPython 库，它依赖系统的 Git 命令
- 请确保目标系统安装了 Git 并配置在 PATH 中
- 下载 Git: https://git-scm.com/download/win

### 2. 数据目录

- 配置、日志、报告存储在 `data/` 目录
- 该目录位于 exe 文件同级
- 首次运行会自动创建必要的子目录
- 避免将程序安装到 Program Files（权限问题）

### 3. 首次运行

- 需要配置 AI API Key
- 需要添加 Git 仓库
- 需要配置作者信息

### 4. 文件大小

- 打包后约 150-200 MB（包含完整的 Qt 库）
- 可以使用 UPX 压缩减小体积（build.bat 已启用）
- 不建议使用单文件模式（会更大且启动慢）

## 🎯 创建安装程序（可选）

使用 Inno Setup 创建专业的安装包：

### 1. 安装 Inno Setup
下载地址: https://jrsoftware.org/isdl.php

### 2. 创建安装脚本

创建 `installer.iss` 文件：

```iss
[Setup]
AppName=Git提交记录智能报告生成器
AppVersion=1.0.0
AppPublisher=Your Name
DefaultDirName={autopf}\GitReport
DefaultGroupName=GitReport
OutputDir=installer
OutputBaseFilename=GitReport-Setup-v1.0.0
Compression=lzma2
SolidCompression=yes
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\GitReport.exe
PrivilegesRequired=lowest

[Files]
Source: "dist\GitReport\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Git报告生成器"; Filename: "{app}\GitReport.exe"
Name: "{autodesktop}\Git报告生成器"; Filename: "{app}\GitReport.exe"

[Run]
Filename: "{app}\GitReport.exe"; Description: "启动程序"; Flags: postinstall nowait skipifsilent
```

### 3. 编译安装程序

```bash
# 使用 Inno Setup Compiler 编译 installer.iss
# 或使用命令行
iscc installer.iss
```

生成的安装包位于 `installer/` 目录。

## 🔧 常见问题

### Q1: ModuleNotFoundError

**问题**: 打包后运行提示某个模块找不到

**解决**: 在 `git-report.spec` 的 `hiddenimports` 中添加该模块

### Q2: 资源文件找不到

**问题**: 图标或样式文件找不到

**解决**:
1. 检查 `git-report.spec` 的 `datas` 配置
2. 确保使用了 `get_resource_path()` 函数

### Q3: GitPython 报错

**问题**: 提示找不到 Git 命令

**解决**:
1. 确保系统安装了 Git
2. 检查 Git 是否在 PATH 中
3. 尝试重启程序

### Q4: 程序启动慢

**问题**: 打包后程序启动需要几秒钟

**解决**:
- 这是正常现象（文件夹模式）
- 单文件模式会更慢
- 可以考虑添加启动画面

### Q5: 文件体积大

**问题**: 打包后的程序很大

**解决**:
- 确保 UPX 压缩已启用（spec 文件中）
- 排除不需要的模块（excludes 配置）
- 考虑使用虚拟环境打包（只包含需要的依赖）

## 📊 打包优化建议

### 1. 使用虚拟环境

```bash
# 创建干净的虚拟环境
python -m venv venv_pack
venv_pack\Scripts\activate

# 只安装必要的依赖
pip install -r requirements.txt
pip install pyinstaller

# 在虚拟环境中打包
pyinstaller git-report.spec
```

### 2. 启用 UPX 压缩

```bash
# 下载 UPX: https://upx.github.io/
# 将 upx.exe 放到 PATH 中
# git-report.spec 中已启用 upx=True
```

### 3. 排除测试代码

确保 spec 文件中排除了测试相关模块：
```python
excludes=[
    'pytest', 'unittest', 'test', 'tests', ...
]
```

## 📝 发布清单

发布前检查：

- [ ] 更新版本号（pyproject.toml, git-report.spec, VERSION.txt）
- [ ] 完整测试所有功能
- [ ] 准备 README_CN.md
- [ ] 准备 AI配置说明.md
- [ ] 准备快速开始.md
- [ ] 测试安装程序（如果有）
- [ ] 在干净的 Windows 环境测试
- [ ] 准备发布说明（更新日志）

## 🔗 相关文档

- [项目 README](../README_CN.md)
- [AI 配置说明](../AI配置说明.md)
- [快速开始](../快速开始.md)
- [架构重构文档](./REFACTORING_SUMMARY.md)

## 💡 技术支持

如遇到打包问题，请检查：

1. Python 版本（需要 3.8+）
2. 依赖是否完整安装
3. PyInstaller 版本（建议最新版）
4. 系统环境（Windows 10/11 64位）
5. 日志文件（查看详细错误信息）

---

**打包脚本创建时间**: 2025-11-04
**最后更新**: 2025-11-04
**PyInstaller 版本**: 6.0+
**Python 版本**: 3.8+
