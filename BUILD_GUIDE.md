# 打包构建指南

## 📦 构建应用程序

### 使用 Python 构建脚本

**支持所有环境**（Windows CMD、PowerShell、Git Bash、Linux、macOS）：

```bash
python build.py
```

### 构建流程

脚本会自动执行以下步骤：

1. **清理旧构建** - 删除 `dist/` 和 `build/` 目录
2. **检查 PyInstaller** - 自动安装（如果缺失）
3. **运行打包** - 使用 PyInstaller 打包应用
4. **创建数据目录** - 生成 `data/logs/`、`data/reports/`、`data/cache/`
5. **生成版本信息** - 创建 `VERSION.txt`
6. **显示统计** - 显示打包大小

### 构建输出

构建完成后：

```
dist/GitReport/
├── GitReport.exe          # 主程序（Windows）
├── _internal/             # 依赖库和资源
├── data/                  # 数据目录
│   ├── logs/              # 日志
│   ├── reports/           # 报告
│   └── cache/             # 缓存
└── VERSION.txt            # 版本信息
```

### 首次运行

```bash
cd dist/GitReport
./GitReport.exe           # Windows
./GitReport               # Linux/macOS
```

## 🔧 构建脚本特性

### 环境检测

- ✅ 自动检测运行环境（Git Bash、CMD、PowerShell 等）
- ✅ Git Bash 环境下显示友好提示
- ✅ 检测 Python 版本（需要 3.8+）

### 智能处理

- ✅ 自动安装 PyInstaller（如果缺失）
- ✅ 跨平台路径处理
- ✅ 详细的进度提示
- ✅ 完善的错误处理

### 输出信息

- ✅ 显示构建平台信息
- ✅ 统计打包大小
- ✅ 生成版本信息文件

## ❓ 常见问题

### Q: 在 Git Bash 中运行报错？

**A**: `build.py` 完全支持 Git Bash，直接运行即可：

```bash
python build.py
```

### Q: 缺少 PyInstaller？

**A**: 脚本会自动安装。如果自动安装失败，手动安装：

```bash
pip install pyinstaller
# 或
uv pip install pyinstaller
```

### Q: 构建失败？

**A**: 检查以下几点：

1. Python 版本 >= 3.8
2. 依赖已安装：`pip install -r requirements.txt`
3. 检查错误信息中的提示

### Q: 打包后程序无法运行？

**A**: 可能原因：

1. 缺少系统依赖（如 Visual C++ 运行库）
2. 杀毒软件误报（添加信任）
3. 查看错误日志：`data/logs/`

## 🎯 构建选项

### 开发模式

开发时可以直接运行源代码：

```bash
python main.py
# 或
uv run python main.py
```

### 发布模式

准备发布时使用构建脚本：

```bash
python build.py
```

## 📝 技术说明

### 为什么使用 Python 脚本？

1. **跨平台兼容** - 一份脚本支持所有平台
2. **更好的错误处理** - Python 异常机制
3. **易于维护** - 代码可读性高
4. **统一体验** - 所有用户使用相同流程
5. **无需额外工具** - 项目已有 Python 环境

### 为什么不用批处理？

- ❌ Windows 专用，不跨平台
- ❌ Git Bash 语法不兼容
- ❌ 错误处理能力弱
- ❌ 可读性和维护性差

## 📚 相关文档

- [README.md](README.md) - 项目主文档
- [快速开始.md](快速开始.md) - 快速入门指南
- [git-report.spec](git-report.spec) - PyInstaller 配置

---

**最后更新**：2025-11-14
**支持平台**：Windows、Linux、macOS、Git Bash
