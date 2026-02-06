# Antigravity 配置说明

## 📁 需要手动配置的文件

所有需要用户配置的文件都位于项目根目录,方便访问和修改。

### 1. PLAN.md (必需)
**位置**: `./PLAN.md`
**用途**: 定义 Agent 执行任务的"法律"和规则

**示例**:
```markdown
# 任务: 实现用户登录模块

## 目标文件
src/auth/login.py

## 核心逻辑
- 实现 login(username, password) 函数
- 验证用户凭据
- 返回 JWT token
- 处理登录失败情况

## 技术要求
- 使用 bcrypt 加密密码
- JWT token 有效期 24 小时
```

### 2. .env (可选)
**位置**: `./env.example` (复制为 `.env`)
**用途**: 存储敏感配置信息

**示例**:
```bash
DEEPSEEK_API_KEY=your_api_key_here
ACTIVE_MODE=executor
```

### 3. config/settings.json
**位置**: `./config/settings.json`
**用途**: 系统配置参数

**可配置项**:
- `RETRY_LIMIT`: 重试次数限制 (默认: 3)
- `TEMPERATURE`: AI 温度参数 (默认: 0.0)
- `IGNORE_PATTERNS`: 忽略的文件模式
- `PROTECTED_PATHS`: 受保护的路径

### 4. config/prompts.yaml
**位置**: `./config/prompts.yaml`
**用途**: AI 提示词配置

**可用模式**:
- `executor`: 执行模式 (默认) - 完整实现代码
- `auditor`: 审计模式 - 仅审查逻辑
- `reviewer`: 评审模式 - 代码质量建议

## 🚀 一键启动任务 (Web 面板)

启动系统后,访问 http://localhost:8501

在 **任务发射台** 模块中:
1. 输入目标文件名 (例如: `src/api/users.py`)
2. 编写任务计划 (会自动更新 PLAN.md)
3. 点击 "保存并一键启动"

系统将自动:
- ✅ 更新 PLAN.md
- ✅ 创建目标文件
- ✅ 创建测试文件
- ✅ 触发 Agent 接管
- ✅ 自动编写代码
- ✅ 运行测试并修复

## 📝 手动启动任务 (命令行)

如果不使用 Web 面板,也可以手动操作:

```bash
# 1. 编辑 PLAN.md
notepad PLAN.md

# 2. 创建目标文件
mkdir -p src/your_module
echo "" > src/your_module/logic.py

# 3. Monitor 会自动检测并启动接管
```

## ⚙️ 环境变量配置

**Windows (PowerShell)**:
```powershell
$env:DEEPSEEK_API_KEY="sk-xxx"
$env:ACTIVE_MODE="executor"
```

**Linux/macOS**:
```bash
export DEEPSEEK_API_KEY="sk-xxx"
export ACTIVE_MODE="executor"
```

## 🔧 高级配置

### 切换 AI 模式
编辑 `config/settings.json` 或设置环境变量:
```bash
$env:ACTIVE_MODE="auditor"  # 切换到审计模式
```

### 自定义忽略模式
编辑 `config/settings.json`:
```json
{
  "IGNORE_PATTERNS": [
    "**/__pycache__/**",
    "**/custom_ignore/**"
  ]
}
```

### 调整重试限制
```json
{
  "RETRY_LIMIT": 5  // 增加到 5 次重试
}
```

## 📚 更多信息

- 完整文档: `README.md`
- 架构说明: 查看 walkthrough 文档
- 问题排查: README.md 第 5 节
