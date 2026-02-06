# ==================== 中文版 ====================

# Antigravity - AI 驱动的自修正编码监管系统

> **"Vibe Coding, Logic Auditing"** - 随心编码,逻辑审计

Antigravity 是一个基于 DeepSeek-R1 的智能代码监管系统,通过文件系统事件总线实现自动化的代码审计、生成和修复。

## 🌟 核心特性

- **🤖 AI Agent 接管**: 根据 PLAN.md 自动编写完整代码
- **🔍 智能审计**: 实时检测代码逻辑问题和幻觉代码
- **🔄 自动修复**: 测试失败时自动迭代修复直至通过
- **🚀 一键启动**: Web 面板一键创建任务并触发 Agent
- **📊 实时监控**: Streamlit 可视化面板实时查看进度
- **🛡️ 熔断保护**: 连续失败自动进入手动模式,保护 Token
- **⚡ 并行启动**: 一条命令同时启动监控和面板

## 📦 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

复制 `.env.example` 为 `.env` 并填入您的 DeepSeek API 密钥:

```bash
cp .env.example .env
# 编辑 .env 文件,填入 DEEPSEEK_API_KEY
```

### 3. 一键启动

```bash
python start_all.py
```

系统将自动启动:
- 📡 Monitor Agent (后台文件监控)
- 🌐 Web Dashboard (http://localhost:8501)

## 🚀 使用方法

### 方式一: Web 面板 (推荐)

1. 访问 http://localhost:8501
2. 滚动到 **"任务发射台"** 部分
3. 填写:
   - 目标文件名: `src/your_module.py`
   - 任务简称: 例如 "用户登录模块"
   - 计划详情: 在右侧编辑器中描述需求
4. 点击 **"🔥 保存并启动"**
5. 在 "Recent Audits" 查看实时进度

### 方式二: 手动触发

1. 编辑 `PLAN.md` 描述任务需求
2. 创建目标文件: `echo "" > src/your_module.py`
3. Monitor 自动检测并启动 Agent 接管

## 🏗️ 核心架构

### 四大核心组件

1. **StateManager** (`antigravity/state_manager.py`)
   - 集中式状态管理
   - 线程安全的文件锁
   - 原子写入操作

2. **Auditor** (`antigravity/auditor.py`)
   - AI 代码审计和生成
   - 支持 3 种模式: executor/auditor/reviewer
   - 外部化提示词配置

3. **Monitor** (`antigravity/monitor.py`)
   - 实时文件监控
   - 智能忽略模式过滤
   - 按需环境检查

4. **Dashboard** (`antigravity/dashboard.py`)
   - Streamlit 可视化面板
   - 任务发射台
   - 实时审计日志

### 文件系统事件总线

| 事件 | 触发条件 | Agent 响应 |
|------|---------|-----------|
| PLAN.md 修改 | 保存 PLAN.md | 触发环境检查 |
| 新文件创建 | src/ 下创建 .py 文件 | 触发代码生成 |
| 测试失败 | 测试运行失败 | 自动修复代码 |

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
DEEPSEEK_API_KEY=sk-xxx        # DeepSeek API 密钥 (必需)
ACTIVE_MODE=executor            # AI 模式: executor/auditor/reviewer
TEMPERATURE=0.0                 # 温度参数: 0.0-1.0
RETRY_LIMIT=3                   # 重试次数限制
```

### AI 模式说明

- **executor** (默认): 完整实现代码
- **auditor**: 仅审查逻辑,不修改代码
- **reviewer**: 提供代码质量建议

### 配置文件

- `config/settings.json`: 系统设置 (忽略模式、保护路径等)
- `config/prompts.yaml`: AI 提示词配置
- `PLAN.md`: 任务计划模板

详细配置说明请查看 `CONFIG_GUIDE.md`

## 🛡️ 安全机制

### 熔断器 (Circuit Breaker)

同一文件连续失败 3 次后自动进入手动模式,防止:
- Token 滥用
- 无限循环
- API 费用失控

### 防抖机制 (Debounce)

文件保存后 3 秒才触发审计,避免:
- 频繁 API 调用
- 编辑过程中误触发

### 自动回滚 (Auto-Rollback)

检测到毁灭性错误时自动执行 `git stash`,保护代码安全。

## 📁 项目结构

```
AGENT/
├── antigravity/              # 核心模块
│   ├── auditor.py           # AI 审计和代码生成
│   ├── monitor.py           # 文件监控
│   ├── dashboard.py         # Web 可视化面板
│   ├── state_manager.py     # 状态管理
│   ├── config.py            # 配置加载
│   ├── test_runner.py       # 测试运行器
│   └── env_checker.py       # 环境检查
├── config/                   # 配置文件
│   ├── settings.json        # 系统设置
│   └── prompts.yaml         # AI 提示词
├── tests/                    # 测试文件
├── PLAN.md                   # 任务计划模板
├── CONFIG_GUIDE.md          # 配置指南
├── .env.example             # 环境变量模板
├── start_all.py             # 并行启动脚本
└── requirements.txt         # Python 依赖
```

## 🔧 常见问题

### Q: Agent 没有响应?

**检查**:
1. Monitor 是否运行? (查看终端)
2. 文件是否在 `src/` 目录下?
3. PLAN.md 是否已保存?

**解决**: 重启系统 `python start_all.py`

### Q: API 401 错误?

**检查**: `DEEPSEEK_API_KEY` 是否正确配置

```bash
# Windows PowerShell
echo $env:DEEPSEEK_API_KEY

# Linux/macOS
echo $DEEPSEEK_API_KEY
```

### Q: 如何切换 AI 模式?

**方法一**: 修改 `.env` 文件
```bash
ACTIVE_MODE=auditor
```

**方法二**: 设置环境变量
```bash
$env:ACTIVE_MODE="reviewer"
```

## 📚 文档

- `README.md` - 本文档 (快速开始)
- `CONFIG_GUIDE.md` - 详细配置指南
- `task_launcher_guide.md` - 任务发射台使用指南
- `walkthrough.md` - 架构优化实施过程

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

---

**Enjoy your safe Vibe Coding!** 🚀

---

# ==================== English Version ====================

# Antigravity - AI-Powered Self-Correcting Code Supervision System

> **"Vibe Coding, Logic Auditing"** - Code freely, audit logically

Antigravity is an intelligent code supervision system powered by DeepSeek-R1, implementing automated code auditing, generation, and fixing through a file system event bus.

## 🌟 Core Features

- **🤖 AI Agent Takeover**: Automatically write complete code based on PLAN.md
- **🔍 Smart Auditing**: Real-time detection of logic issues and hallucinated code
- **🔄 Auto-Fix**: Automatically iterate fixes until tests pass
- **🚀 One-Click Launch**: Web panel for one-click task creation and agent trigger
- **📊 Real-time Monitoring**: Streamlit visualization dashboard for live progress
- **🛡️ Circuit Breaker**: Auto manual mode on consecutive failures to protect tokens
- **⚡ Parallel Startup**: Single command to start both monitor and dashboard

## 📦 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Copy `.env.example` to `.env` and fill in your DeepSeek API key:

```bash
cp .env.example .env
# Edit .env file and add DEEPSEEK_API_KEY
```

### 3. One-Click Startup

```bash
python start_all.py
```

The system will automatically start:
- 📡 Monitor Agent (background file monitoring)
- 🌐 Web Dashboard (http://localhost:8501)

## 🚀 Usage

### Method 1: Web Panel (Recommended)

1. Visit http://localhost:8501
2. Scroll to **"Task Launcher"** section
3. Fill in:
   - Target file: `src/your_module.py`
   - Task name: e.g., "User Login Module"
   - Plan details: Describe requirements in the right editor
4. Click **"🔥 Save and Launch"**
5. View real-time progress in "Recent Audits"

### Method 2: Manual Trigger

1. Edit `PLAN.md` to describe task requirements
2. Create target file: `echo "" > src/your_module.py`
3. Monitor auto-detects and starts agent takeover

## 🏗️ Core Architecture

### Four Core Components

1. **StateManager** (`antigravity/state_manager.py`)
   - Centralized state management
   - Thread-safe file locking
   - Atomic write operations

2. **Auditor** (`antigravity/auditor.py`)
   - AI code auditing and generation
   - 3 modes: executor/auditor/reviewer
   - Externalized prompt configuration

3. **Monitor** (`antigravity/monitor.py`)
   - Real-time file monitoring
   - Smart ignore pattern filtering
   - On-demand environment checks

4. **Dashboard** (`antigravity/dashboard.py`)
   - Streamlit visualization panel
   - Task launcher
   - Real-time audit logs

### File System Event Bus

| Event | Trigger | Agent Response |
|-------|---------|----------------|
| PLAN.md modified | Save PLAN.md | Trigger env check |
| New file created | Create .py in src/ | Trigger code generation |
| Test failed | Test run fails | Auto-fix code |

## ⚙️ Configuration

### Environment Variables (.env)

```bash
DEEPSEEK_API_KEY=sk-xxx        # DeepSeek API key (required)
ACTIVE_MODE=executor            # AI mode: executor/auditor/reviewer
TEMPERATURE=0.0                 # Temperature: 0.0-1.0
RETRY_LIMIT=3                   # Retry limit
```

### AI Mode Explanation

- **executor** (default): Full code implementation
- **auditor**: Logic review only, no code modification
- **reviewer**: Code quality suggestions

### Configuration Files

- `config/settings.json`: System settings (ignore patterns, protected paths, etc.)
- `config/prompts.yaml`: AI prompt configuration
- `PLAN.md`: Task plan template

See `CONFIG_GUIDE.md` for detailed configuration instructions

## 🛡️ Safety Mechanisms

### Circuit Breaker

Auto manual mode after 3 consecutive failures on the same file to prevent:
- Token abuse
- Infinite loops
- API cost overruns

### Debounce Mechanism

3-second delay after file save before triggering audit to avoid:
- Frequent API calls
- Accidental triggers during editing

### Auto-Rollback

Automatically executes `git stash` on catastrophic errors to protect code safety.

## 📁 Project Structure

```
AGENT/
├── antigravity/              # Core modules
│   ├── auditor.py           # AI auditing and code generation
│   ├── monitor.py           # File monitoring
│   ├── dashboard.py         # Web visualization panel
│   ├── state_manager.py     # State management
│   ├── config.py            # Configuration loading
│   ├── test_runner.py       # Test runner
│   └── env_checker.py       # Environment checker
├── config/                   # Configuration files
│   ├── settings.json        # System settings
│   └── prompts.yaml         # AI prompts
├── tests/                    # Test files
├── PLAN.md                   # Task plan template
├── CONFIG_GUIDE.md          # Configuration guide
├── .env.example             # Environment variable template
├── start_all.py             # Parallel startup script
└── requirements.txt         # Python dependencies
```

## � FAQ

### Q: Agent not responding?

**Check**:
1. Is Monitor running? (check terminal)
2. Is file in `src/` directory?
3. Is PLAN.md saved?

**Solution**: Restart system with `python start_all.py`

### Q: API 401 error?

**Check**: Is `DEEPSEEK_API_KEY` correctly configured?

```bash
# Windows PowerShell
echo $env:DEEPSEEK_API_KEY

# Linux/macOS
echo $DEEPSEEK_API_KEY
```

### Q: How to switch AI mode?

**Method 1**: Modify `.env` file
```bash
ACTIVE_MODE=auditor
```

**Method 2**: Set environment variable
```bash
$env:ACTIVE_MODE="reviewer"
```

## 📚 Documentation

- `README.md` - This document (quick start)
- `CONFIG_GUIDE.md` - Detailed configuration guide
- `task_launcher_guide.md` - Task launcher usage guide
- `walkthrough.md` - Architecture optimization walkthrough

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

---

**Enjoy your safe Vibe Coding!** 🚀
