# Git 提交记录智能报告生成器

> 一键将 Git 提交历史转换为专业的工作报告

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![UV](https://img.shields.io/badge/uv-managed-blueviolet.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Status](https://img.shields.io/badge/status-tested%20%26%20ready-brightgreen.svg)

## 📖 项目简介

这是一个本地运行的 GUI 工具,帮助开发者快速生成基于 Git 提交记录的工作报告。

**核心功能**:
- 📊 自动提取 Git 提交记录
- 🗂️ **多仓库管理** - 同时管理多个 Git 仓库,一键汇总
- 🔍 **批量扫描** - 自动发现目录下所有Git仓库,一键批量添加
- 🤖 多平台 AI 支持 (OpenAI GPT / Deepseek / 智谱 GLM)
- 🔄 一键切换平台,无需修改代码
- 📈 Token 用量统计,成本透明
- 🧪 测试连接功能,配置即验证
- 🎨 美观的图形界面,操作简单
- 💾 配置持久化,一次配置长期使用
- 🚀 使用 uv 管理依赖,安装快速

## ✨ 主要特性

- ✅ **多仓库管理** - 同时添加多个仓库,独立配置作者筛选
- ✅ **批量扫描添加** - 选择父目录,自动发现所有Git仓库,树形展示可配置深度
- ✅ **智能作者识别** - 从每个仓库的git config自动读取作者信息
- ✅ **混合展示** - 多仓库提交按时间排序统一展示,带仓库标签
- ✅ 按作者、日期范围智能筛选提交
- ✅ 自动分类提交类型(feat/fix/refactor/docs 等)
- ✅ 智能过滤无意义提交(merge/sync 等)
- ✅ **统一抽象 + 适配器架构** - 多平台无缝切换
- ✅ **可视化平台选择** - 下拉框切换 OpenAI/Deepseek/智谱
- ✅ **测试连接功能** - 保存前验证 API 配置
- ✅ 可视化 AI 配置弹窗,支持自定义 Prompt 模板
- ✅ Markdown 格式输出,一键复制

## 🚀 快速开始

### Windows 用户 (最简单)

1. **双击** `install.bat` - 自动安装 uv 和所有依赖
   - 可能显示部分乱码,这是正常的
   - 只要没有 "ERROR" 就是成功的

2. **双击** `run.bat` - 启动程序

3. **配置使用**:
   - 添加Git仓库(两种方式):
     * **快速批量添加**: 点击 **"批量扫描"** → 选择父目录 → 勾选仓库 → 一键添加
     * **手动添加**: 点击 **"添加仓库"** → 填写仓库信息
   - 点击 **"AI 设置"** 配置平台 (OpenAI / Deepseek / 智谱 GLM)
     * 选择平台 → 填写 API Key → 测试连接 → 保存
   - 选择日期范围,点击"拉取提交记录"
   - 点击"生成报告"

   详细 AI 配置说明请查看 [AI配置说明.md](AI配置说明.md) ⭐

### 命令行安装 (推荐)

```bash
# 1. 安装 uv (如果还没安装)
# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 进入项目目录
cd git-report

# 3. 安装依赖
uv sync

# 4. 运行程序
uv run python main.py

# 5. 测试模块
uv run python test_modules.py
```

### 使用 pip (传统方式)

```bash
pip install -r requirements.txt
python main.py
```

## 📋 系统要求

- Python 3.8+
- uv 包管理器 (推荐) 或 pip
- Windows / macOS / Linux
- 网络连接 (用于调用 AI API)

**支持的 AI 平台** (统一抽象 + 适配器架构):
- ✅ **OpenAI GPT** - gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
- ✅ **Deepseek** - deepseek-chat, deepseek-coder
- ✅ **智谱 GLM** - glm-4-plus, glm-4-air, glm-4-flash, glm-4

**核心特性**:
- 🔄 一键切换平台 (GUI 下拉框选择)
- 📊 Token 用量实时统计
- 🧪 测试连接功能 (保存前验证)

## 🎯 使用场景

- **日报/周报**: 自动汇总每日/每周的工作内容
- **多项目总结**: 同时管理多个项目,一键生成跨项目报告
- **绩效材料**: 为绩效考核准备工作记录
- **团队汇报**: 向上级汇报工作进展
- **全栈开发者**: 前端、后端、移动端等多个仓库统一管理

## 📸 功能界面

主界面包含:
- **仓库列表区**: 添加、编辑、查看多个仓库,支持启用/禁用
- **日期选择器**: 自定义时间范围
- **提交记录表格**: 清晰展示所有仓库的提交,带仓库标签
- **生成报告按钮**: 一键生成 AI 报告
- **报告展示弹窗**: Markdown 渲染 + 复制功能

## 🛠️ 技术架构

```
┌─────────────────────────────────┐
│      PyQt5 GUI Layer            │
│  (主窗口、报告弹窗、配置面板)     │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│    Business Logic Layer         │
│  ├─ GitService (Git 操作)       │
│  ├─ DataFormatter (数据处理)    │
│  ├─ AiClient (AI 调用)          │
│  └─ ConfigManager (配置管理)    │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│        Data Layer               │
│  ├─ config.json (配置文件)      │
│  ├─ cache/ (缓存目录)           │
│  └─ reports/ (报告输出)         │
└─────────────────────────────────┘
```

## 📂 项目结构

```
git-report/
├── main.py                 # 程序入口
├── pyproject.toml          # uv 项目配置
├── uv.lock                 # 依赖锁定
├── install.bat             # Windows 安装
├── run.bat                 # Windows 启动
├── test_modules.py         # 模块测试
├── requirements.txt        # pip 依赖清单
│
├── core/                   # 核心业务模块
│   ├── config_manager.py   # 配置管理 (支持多仓库)
│   ├── git_service.py      # Git 操作 (支持仓库标识)
│   ├── formatter.py        # 数据格式化 (支持仓库标签)
│   └── ai_client.py        # AI 客户端工厂
│
├── ui/                     # 界面模块
│   ├── main_window.py      # 主窗口 (多仓库管理)
│   ├── ai_config_dialog.py # AI 配置弹窗
│   ├── repo_config_dialog.py   # 仓库配置对话框
│   ├── repo_detail_dialog.py   # 仓库详情对话框
│   ├── repo_list_widget.py     # 仓库列表组件
│   └── repo_scan_dialog.py     # 批量扫描对话框 (新)
│
├── core/adapters/          # 适配器模块 (新架构)
│   ├── base.py             # 抽象基类
│   ├── openai_adapter.py   # OpenAI 适配器
│   ├── deepseek_adapter.py # Deepseek 适配器
│   └── zhipu_adapter.py    # 智谱 GLM 适配器
│
└── 文档/
    ├── README.md           # 英文说明
    ├── README_CN.md        # 中文说明(本文件)
    ├── 快速开始.md         # 快速入门
    ├── 使用说明.md         # 详细文档
    ├── AI配置说明.md       # AI 配置指南 (重点!)
    ├── 安装说明.txt        # 安装指南
    ├── 测试通过报告.md     # 测试报告
    └── CLAUDE.md           # AI 助手指南
```

## 🧪 测试验证

运行测试脚本:

```bash
uv run python test_modules.py
```

所有模块测试通过 (6/6):
```
ConfigManager        [OK] 通过
GitService           [OK] 通过
DataFormatter        [OK] 通过
AiClient             [OK] 通过
RepoScanner          [OK] 通过
UI                   [OK] 通过
```

## 📦 打包构建

将应用程序打包成独立可执行文件：

### 使用 Python 构建脚本

**支持所有环境**（Windows CMD、PowerShell、Git Bash、Linux、macOS）：

```bash
python build.py
```

### 构建输出

构建完成后：
- 输出目录：`dist/GitReport/`
- 主程序：`dist/GitReport/GitReport.exe` (Windows)
- 数据目录：`dist/GitReport/data/` (配置、日志、报告)

### 首次运行

```bash
cd dist\GitReport
GitReport.exe
```

配置 AI API Key 后即可使用。

## ❓ 常见问题

### Q: install.bat 显示乱码?
**A**: 这是 Windows 编码问题,不影响功能。只要没有 "ERROR" 字样就是成功的。可以使用命令行: `uv sync`

### Q: 找不到 Python?
**A**: 安装 Python 3.8+ 并添加到环境变量。下载: https://www.python.org/downloads/

### Q: uv sync 报错?
**A**: 检查网络连接,或使用 pip 方式: `pip install -r requirements.txt`

### Q: 程序无法启动?
**A**:
1. 运行 `uv run python test_modules.py` 检查
2. 确保 Python 版本 >= 3.8
3. 查看错误信息

### Q: API 调用失败?
**A**:
- 检查 BASE_URL、API Key 和 MODEL 是否正确配置
- 确认网络连接正常
- 验证 API 额度充足
- 查看 [AI配置说明.md](AI配置说明.md) 了解不同服务的配置方式

更多问题请查看 [使用说明.md](使用说明.md)

## 📝 提交规范建议

为了获得更好的分类效果,建议使用 Conventional Commits 格式:

```
feat: 添加新功能
fix: 修复 bug
refactor: 重构代码
docs: 更新文档
test: 添加测试
perf: 性能优化
chore: 其他修改
```

## 🗺️ 未来规划

- [x] ✅ 接入更多 AI 模型(已支持 OpenAI、Deepseek、智谱 GLM)
- [x] ✅ 自定义报告模板
- [x] ✅ 支持多仓库管理
- [ ] 报告导出为 PDF/Word
- [ ] 多 Prompt 预设管理
- [ ] 定时任务自动生成
- [ ] 远程仓库支持
- [ ] 仓库分组管理

## 📄 完整文档

- [快速开始.md](快速开始.md) - 3 步快速上手
- [AI配置说明.md](AI配置说明.md) - AI 服务配置指南 ⭐

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📜 许可证

MIT License

---

**最后更新**: 2025-10-21

如有问题或建议,欢迎联系或提 Issue!
