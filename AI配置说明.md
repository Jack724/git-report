# AI 配置说明

## 多平台架构简介

本项目采用**统一抽象 + 适配器架构**,支持多个 AI 平台无缝切换:
- ✅ OpenAI GPT (gpt-4o, gpt-4o-mini, gpt-3.5-turbo 等)
- ✅ Deepseek (deepseek-chat, deepseek-coder)
- ✅ 智谱 GLM (glm-4-plus, glm-4-flash 等)

**核心特性**:
- 🔄 **一键切换平台** - 在 GUI 中选择即可,无需修改代码
- 📊 **Token 用量统计** - 自动显示每次调用消耗的 Token 数
- 🧪 **测试连接功能** - 保存前可测试 API 配置是否正确
- 💾 **多平台共存** - 可同时配置多个平台,随时切换

---

## 配置方式

### 方式一: 使用 GUI 配置 (强烈推荐)

1. 启动程序后,点击主界面的 **"AI 设置"** 按钮
2. 在配置窗口中:
   - **选择 AI 平台**: 从下拉框选择 OpenAI GPT / Deepseek / 智谱 GLM
   - **填写配置信息**: 根据平台填写 API Key、Model 等
   - **测试连接** (可选): 点击"测试连接"按钮验证配置
   - **自定义 Prompt** (可选): 修改通用的 Prompt 模板
3. 点击 **"保存"** 按钮

![AI配置界面](https://via.placeholder.com/600x400?text=AI+Configuration+Dialog)

### 方式二: 手动编辑配置文件

编辑项目根目录的 `config.json` 文件:

```json
{
  "repo_path": "your/repo/path",
  "author_name": "Your Name",
  "author_email": "your@email.com",
  "ai": {
    "provider": "zhipu",
    "prompt": "你是一名资深技术主管...(完整 Prompt)",
    "configs": {
      "openai": {
        "api_key": "sk-xxx",
        "model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1"
      },
      "deepseek": {
        "api_key": "sk-xxx",
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com"
      },
      "zhipu": {
        "api_key": "your-api-key",
        "model": "glm-4-flash"
      }
    }
  }
}
```

**说明**:
- `provider`: 当前激活的平台 (`openai` | `deepseek` | `zhipu`)
- `prompt`: 通用的 Prompt 模板,必须包含 `{commit_log}` 占位符
- `configs`: 各平台的独立配置

---

## 平台配置详解

### 1. OpenAI GPT

**获取 API Key**: https://platform.openai.com/api-keys

**配置参数**:
- `api_key`: OpenAI API Key (必填)
- `model`: 模型名称 (必填)
  - 推荐: `gpt-4o-mini` (性价比高)
  - 可选: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`
- `base_url`: API 地址 (可选,默认 `https://api.openai.com/v1`)

**完整配置示例**:
```json
{
  "api_key": "sk-proj-xxxxxxxxxxxxx",
  "model": "gpt-4o-mini",
  "base_url": "https://api.openai.com/v1"
}
```

**使用第三方代理** (可选):
```json
{
  "api_key": "sk-xxx",
  "model": "gpt-4o-mini",
  "base_url": "https://your-proxy.com/v1"
}
```

---

### 2. Deepseek

**获取 API Key**: https://platform.deepseek.com/api_keys

**配置参数**:
- `api_key`: Deepseek API Key (必填)
- `model`: 模型名称 (必填)
  - 推荐: `deepseek-chat` (通用对话模型)
  - 可选: `deepseek-coder` (代码专用模型)
- `base_url`: API 地址 (可选,默认 `https://api.deepseek.com`)

**完整配置示例**:
```json
{
  "api_key": "sk-xxxxxxxxxxxxx",
  "model": "deepseek-chat",
  "base_url": "https://api.deepseek.com"
}
```

**特点**:
- ✅ 价格实惠,性价比高
- ✅ 中文支持优秀
- ✅ 兼容 OpenAI API 格式

---

### 3. 智谱 GLM

**获取 API Key**: https://open.bigmodel.cn/usercenter/apikeys

**配置参数**:
- `api_key`: 智谱 API Key (必填)
- `model`: 模型名称 (必填)
  - 推荐: `glm-4-flash` (快速响应)
  - 可选: `glm-4-plus`, `glm-4-air`, `glm-4`

**完整配置示例**:
```json
{
  "api_key": "your-api-key.xxxxxxxxxxxxx",
  "model": "glm-4-flash"
}
```

**特点**:
- ✅ 中文能力强
- ✅ 支持长上下文
- ✅ Base URL 已内置,无需填写

---

## Prompt 模板自定义

### 默认 Prompt 模板

```
你是一名资深技术主管,请根据以下 Git 提交记录生成一份简洁的中文工作报告。

要求:
1. 按功能模块或类型分组整理
2. 突出新增功能、修复问题、优化改进
3. 使用自然流畅的中文,避免逐条罗列
4. 控制在 300 字以内
5. 使用 Markdown 格式,包含标题和分组

提交记录:
{commit_log}

请生成工作报告:
```

### 自定义 Prompt 注意事项

1. **必须包含 `{commit_log}` 占位符** - 系统会替换为实际的提交记录
2. **建议使用 Markdown 格式** - 生成的报告会以 Markdown 渲染展示
3. **可调整报告风格** - 根据需求修改语气、详细程度、字数限制等

### Prompt 示例:简洁版

```
请将以下 Git 提交记录总结为 3-5 个要点,使用中文:

{commit_log}

要点:
```

### Prompt 示例:详细版

```
作为项目经理,请根据以下 Git 提交记录生成一份详细的项目进展报告。

报告要求:
- 分为"新增功能"、"Bug 修复"、"性能优化"、"文档更新"四个板块
- 每个板块列出具体的工作内容
- 突出技术亮点和创新点
- 预估每项工作的工作量(人/天)
- 使用 Markdown 表格展示

提交记录:
{commit_log}

请生成报告:
```

---

## 测试连接功能

在 AI 配置对话框中,每个平台都有**"测试连接"**按钮:

### 测试流程

1. 填写 API Key 和 Model
2. 点击"测试连接"按钮
3. 系统会发送一个简单的测试请求 (内容: "hi")
4. 显示测试结果:
   - ✅ **成功**: 绿色提示,显示平台名称
   - ❌ **失败**: 红色提示,显示错误信息

### 常见错误

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| `HTTP 401` | API Key 无效 | 检查 API Key 是否正确 |
| `HTTP 429` | 请求频率超限 | 稍后重试 |
| `HTTP 500` | 服务器错误 | 稍后重试或联系服务商 |
| `Connection timeout` | 网络问题 | 检查网络连接或代理设置 |
| `Invalid model` | 模型名称错误 | 检查模型名称拼写 |

---

## Token 用量统计

### 自动显示

报告生成成功后,状态栏会自动显示 Token 用量:

```
报告生成成功 (消耗 1234 tokens: 800 prompt + 434 completion)
```

**说明**:
- `total_tokens`: 总消耗 Token 数
- `prompt_tokens`: 输入 Prompt 的 Token 数
- `completion_tokens`: 模型生成内容的 Token 数

### 成本估算

不同平台的定价 (2025年1月参考):

| 平台 | 模型 | 输入价格 | 输出价格 | 备注 |
|------|------|----------|----------|------|
| OpenAI | gpt-4o-mini | $0.15/1M | $0.60/1M | 性价比最高 |
| OpenAI | gpt-4o | $5.00/1M | $15.00/1M | 能力最强 |
| Deepseek | deepseek-chat | ¥0.5/1M | ¥2.0/1M | 极致性价比 |
| 智谱 GLM | glm-4-flash | ¥0.1/1M | ¥0.1/1M | 中文优秀 |

**示例计算** (生成一份 300 字报告):
- 输入: ~800 tokens (提交记录 + Prompt)
- 输出: ~400 tokens (报告内容)
- 总计: ~1200 tokens

成本估算:
- OpenAI gpt-4o-mini: $0.0004 (约 ¥0.003)
- Deepseek: ¥0.001
- 智谱 GLM: ¥0.0001

---

## 故障排查

### 问题 1: 配置保存失败

**症状**: 点击"保存"后提示"配置保存失败"

**解决**:
1. 检查程序是否有写入权限
2. 检查 `config.json` 文件是否被占用
3. 尝试以管理员身份运行程序

### 问题 2: API 调用失败

**症状**: 生成报告时提示"API 请求失败"

**解决**:
1. 点击"测试连接"验证配置
2. 检查 API Key 是否正确
3. 检查网络连接
4. 查看平台 API 额度是否充足
5. 尝试切换到其他平台

### 问题 3: Prompt 不生效

**症状**: 生成的报告格式不符合预期

**解决**:
1. 确认 Prompt 中包含 `{commit_log}` 占位符
2. 尝试简化 Prompt,逐步调整
3. 不同平台对 Prompt 的理解可能不同,可针对平台优化

### 问题 4: Token 用量统计不显示

**症状**: 报告生成成功,但没有显示 Token 用量

**可能原因**:
- 某些平台 API 响应中不包含 `usage` 字段
- 网络不稳定导致响应不完整

**说明**: Token 统计是可选功能,不影响核心功能

---

## 平台切换

### 如何切换平台

1. **GUI 方式** (推荐):
   - 打开"AI 设置"
   - 从下拉框选择新平台
   - 填写该平台的配置
   - 保存

2. **配置文件方式**:
   - 编辑 `config.json`
   - 修改 `ai.provider` 为 `openai` / `deepseek` / `zhipu`
   - 确保对应平台的配置已填写

### 切换场景示例

**场景一**: 从智谱 GLM 切换到 Deepseek (降低成本)
```json
{
  "ai": {
    "provider": "deepseek",  // 改为 deepseek
    "configs": {
      "deepseek": {
        "api_key": "your-key",
        "model": "deepseek-chat"
      }
    }
  }
}
```

**场景二**: 从 gpt-3.5-turbo 升级到 gpt-4o (提升质量)
```json
{
  "ai": {
    "provider": "openai",
    "configs": {
      "openai": {
        "api_key": "sk-xxx",
        "model": "gpt-4o"  // 改为 gpt-4o
      }
    }
  }
}
```

---

## 最佳实践

### 1. 平台选择建议

| 使用场景 | 推荐平台 | 推荐模型 | 理由 |
|---------|---------|---------|------|
| 日常工作报告 | Deepseek | deepseek-chat | 性价比极高,中文优秀 |
| 重要项目总结 | OpenAI | gpt-4o | 质量最高,理解能力强 |
| 快速汇总 | 智谱 GLM | glm-4-flash | 响应快,成本低 |
| 代码相关报告 | Deepseek | deepseek-coder | 代码理解强 |

### 2. Prompt 优化技巧

- ✅ **明确输出格式**: 指定使用 Markdown、JSON 等
- ✅ **控制长度**: 设置字数限制,避免过长或过短
- ✅ **分类要求**: 指定按模块、类型、优先级分组
- ✅ **语气风格**: 正式/轻松、技术/业务、中文/英文
- ❌ 避免过于复杂的多步骤要求

### 3. 成本控制

- 💡 日常使用选择性价比高的模型 (Deepseek, GLM-4-flash)
- 💡 重要场合再使用高端模型 (GPT-4o)
- 💡 定期查看 Token 用量统计
- 💡 优化 Prompt,减少不必要的输入

### 4. 安全建议

- 🔒 API Key 不要提交到 Git 仓库
- 🔒 使用环境变量或配置文件管理密钥
- 🔒 定期轮换 API Key
- 🔒 设置 API 使用额度上限

---

## 常见问题 FAQ

**Q: 可以同时配置多个平台吗?**
A: 可以!在配置文件中可以同时填写 `openai`、`deepseek`、`zhipu` 的配置,通过 `provider` 切换即可。

**Q: 切换平台后需要重启程序吗?**
A: 不需要。保存配置后,下次生成报告时会自动使用新平台。

**Q: 如何添加自定义平台?**
A: 目前支持 OpenAI、Deepseek、智谱 GLM 三个平台。如需支持其他平台,请参考 `core/adapters/` 目录下的适配器实现,创建新的适配器类。

**Q: Token 统计不准确怎么办?**
A: Token 统计来自 API 响应,如有疑问请参考对应平台的官方文档或后台。

**Q: 报告质量不满意怎么办?**
A: 可以尝试:
1. 优化 Prompt 模板
2. 切换到更高端的模型
3. 调整提交记录的筛选条件

---

## 技术支持

- 📖 项目文档: [README.md](README.md)
- 🐛 问题反馈: GitHub Issues
- 💬 讨论交流: GitHub Discussions

**版本**: v1.2 (适配器架构)
**更新日期**: 2025-10-21
