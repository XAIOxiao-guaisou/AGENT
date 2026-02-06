# Antigravity 🚀

**AI-Powered Autonomous Code Guardian & Project Executor**

Antigravity 是一个基于 DeepSeek API 的智能代码守护系统,能够自动监控、审计、修复代码,并支持项目级多文件接管与全量测试验证。

---

## 🌟 核心特性

### P0: 基础架构 ✅
- **实时文件监控**: 基于 watchdog 的文件变动检测
- **智能代码审计**: DeepSeek API 驱动的代码分析
- **自动修复**: 检测到问题自动生成修复代码
- **多模式支持**: executor / project_executor 双模式
- **状态管理**: 完整的审计日志和状态追踪

### P1: 项目级接管 ✅
- **多文件协议**: 支持 `FILE:` 和 `DELETE:` 标记的多文件输出
- **项目级同步**: 基于 PLAN.md 的全项目重构能力
- **全量测试验证**: pytest 集成,自动运行测试并解析失败文件
- **失败驱动修复**: 测试失败后自动触发二次修复
- **Dashboard 项目发射台**: Web UI 支持多文件输入和文档上传

### P2: 上下文优化 ✅
- **依赖分析器**: AST 解析 import 语句,构建双向依赖图
- **智能上下文管理**: tiktoken 集成,骨架化算法减少 65% token
- **变更检测器**: MD5 哈希快照,增量同步决策
- **性能监控器**: 装饰器模式追踪执行时间和成功率

### P3: 深度集成 ✅
- **手术级精准上下文**: 依赖分析 + Token 优化 = 73% token 减少
- **三层智能决策**:
  - 0 变更 = 不触发 API (防误触)
  - ≤3 变更 = 增量修复 (手术级)
  - >3 变更 = 全量重构 (架构级)
- **失败驱动优先级**: 测试失败文件强制完整内容
- **实时性能可视化**: Dashboard 展示 Token 使用、耗时统计

---

## 📊 性能指标

| 指标 | P1 (暴力) | P2 (组件) | P3 (集成) | 提升 |
|------|-----------|-----------|-----------|------|
| Token 使用 | 12000+ | 4500 | 3200 | **73% ↓** |
| API 调用 (无变更) | 1 次 | 1 次 | 0 次 | **100% ↓** |
| 上下文精准度 | 20% | 60% | 100% | **5x ↑** |
| 大型项目支持 | ❌ | ⚠️ | ✅ | **100+ 文件** |

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/XAIOxiao-guaisou/AGENT.git
cd AGENT

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env 文件,填入你的 DEEPSEEK_API_KEY
```

### 2. 配置 PLAN.md

创建或编辑 `PLAN.md` 文件,描述你的项目需求:

```markdown
# 项目目标

构建一个用户认证系统

## 核心功能

1. 用户注册 (src/auth/register.py)
2. 用户登录 (src/auth/login.py)
3. Token 验证 (src/auth/token.py)

## 技术栈

- FastAPI
- JWT
- SQLAlchemy
```

### 3. 启动系统

```bash
# 方式 1: 启动 Monitor (自动监控文件变动)
python start_monitor.py

# 方式 2: 启动 Dashboard (Web UI)
python start_dashboard.py
# 访问 http://localhost:8501

# 方式 3: 一键启动 (Monitor + Dashboard)
python start_all.py
```

---

## 📖 使用指南

### 单文件审计模式 (Executor)

适用于修改单个文件:

```bash
# Monitor 会自动检测文件变动并触发审计
# 或手动触发:
python -c "from antigravity.auditor import Auditor; Auditor('.').audit_and_fix('src/main.py')"
```

### 项目级接管模式 (Project Executor)

适用于多文件重构:

1. **编辑 PLAN.md**: 描述项目需求
2. **触发同步**: 
   - Dashboard: 点击"🔥 启动项目级开发"
   - 或修改 PLAN.md 保存 (Monitor 自动检测)
3. **自动执行**:
   - P3 智能决策 (0/增量/全量)
   - 依赖分析获取最小上下文
   - Token 优化 (骨架化)
   - 生成/修改多个文件
   - 运行全量测试
   - 失败自动修复

---

## 🎯 P3 智能决策示例

### 场景 1: 零变更 (防误触)

```
用户按 Ctrl+S,但文件未变更
→ 📊 Change Summary: 0 changes
→ ✅ No physical changes detected, skipping API call
→ API 调用: 0 次
```

### 场景 2: 小变更 (增量修复)

```
用户修改 src/auth.py 中的一个函数
→ 📊 Change Summary: 1 changes (1 modified)
→ � Incremental sync mode (1 ≤ 3 changes)
→ 🧠 Dependency analysis: 1 targets → 3 relevant files
→ 📊 Context optimized: 3/3 files, 850 tokens
→ ✅ Incremental sync complete: 2 files fixed
→ Token 使用: 850 (vs 全量 12000+)
```

### 场景 3: 大变更 (全量重构)

```
用户修改 PLAN.md 要求迁移到 FastAPI
→ 📊 Change Summary: 15 changes
→ 🌐 Full sync mode (15 > 3 changes)
→ 🧠 Dependency analysis: 15 targets → 18 relevant files
→ 📊 Context optimized: 15/18 files, 11200 tokens
→ ✅ Full sync complete: Modified 15 files
→ 🧪 Full integration test
→ 失败自动修复 (Round 2: 4200 tokens)
```

---

## 🛠️ 配置说明

### config/settings.json

```json
{
  "DEEPSEEK_API_KEY": "your-api-key",
  "TEMPERATURE": 0.0,
  "MAX_TOKENS": 16384,
  "INCREMENTAL_THRESHOLD": 3,
  "PROTECTED_PATHS": [".git", ".env", "venv"],
  "IGNORE_PATTERNS": [".git", "__pycache__", "node_modules"],
  "WATCH_EXTENSIONS": [".py", ".js", ".tsx", ".ts", ".md"]
}
```

### config/prompts.yaml

```yaml
modes:
  executor:
    system_prompt: "You are a code executor..."
    temperature: 0.0
    max_tokens: 4096
  
  project_executor:
    system_prompt: "You are a project-level executor..."
    temperature: 0.0
    max_tokens: 16384

default_mode: executor
```

---

## 📊 Dashboard 功能

访问 `http://localhost:8501` 查看:

### 系统控制
- AI 模式切换 (executor / project_executor)
- 环境依赖检查
- 系统状态监控

### 任务发射台
- 单文件任务快速启动
- 目标文件输入
- 任务描述

### 项目发射台 (P1)
- 多文件路径输入
- 业务文档上传 (.txt/.md)
- PLAN 模板管理
- 批量文件创建

### 性能监控 (P3)
- Token 使用进度条
- 性能统计卡片 (操作数/调用数/总耗时)
- 最慢操作排行 (Top 5)
- 最近执行时间线 (成功率追踪)

### 审计日志
- 实时审计记录
- 文件变动历史
- 状态追踪

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_auditor.py

# 查看覆盖率
pytest --cov=antigravity tests/
```

---

## 📁 项目结构

```
AGENT/
├── antigravity/              # 核心模块
│   ├── auditor.py           # 代码审计器 (P0 + P1 + P3)
│   ├── monitor.py           # 文件监控器 (P0 + P1 + P3)
│   ├── dashboard.py         # Web Dashboard (P1 + P3)
│   ├── state_manager.py     # 状态管理 (P0)
│   ├── test_runner.py       # 测试运行器 (P1)
│   ├── dependency_analyzer.py    # 依赖分析器 (P2)
│   ├── context_manager.py        # 上下文管理器 (P2)
│   ├── change_detector.py        # 变更检测器 (P2)
│   ├── performance_monitor.py    # 性能监控器 (P2)
│   ├── config.py            # 配置加载
│   ├── utils.py             # 工具函数
│   ├── notifier.py          # 通知系统
│   └── env_checker.py       # 环境检查
├── config/
│   ├── settings.json        # 系统配置
│   └── prompts.yaml         # Prompt 配置
├── tests/                   # 测试文件
├── PLAN.md                  # 项目计划 (用户编辑)
├── start_monitor.py         # 启动 Monitor
├── start_dashboard.py       # 启动 Dashboard
├── start_all.py             # 一键启动
├── requirements.txt         # Python 依赖
└── README.md               # 本文件
```

---

## 🔧 高级功能

### 1. 依赖分析 (P2)

```python
from antigravity.dependency_analyzer import DependencyAnalyzer

analyzer = DependencyAnalyzer(".")
analyzer.build_dependency_graph(["src/main.py"])

# 获取最小上下文
minimal = analyzer.get_minimal_context("src/main.py", max_depth=2)
print(f"Relevant files: {minimal}")

# 导出依赖图
analyzer.export_graph("dependency_graph.json")
```

### 2. Token 优化 (P2)

```python
from antigravity.context_manager import ContextManager

manager = ContextManager(max_tokens=16384)

# 骨架化代码
skeleton = manager._skeletonize(code)
print(f"Original: {manager.count_tokens(code)} tokens")
print(f"Skeleton: {manager.count_tokens(skeleton)} tokens")

# 优化上下文
optimized = manager.optimize_context(
    files_dict,
    priority_files=["main.py"],
    reserve_tokens=4096
)
```

### 3. 性能监控 (P2)

```python
from antigravity.performance_monitor import perf_monitor

@perf_monitor.measure("my_operation")
def my_function():
    # Your code here
    pass

# 查看报告
print(perf_monitor.report())

# 导出 JSON
perf_monitor.export_report("performance.json")
```

---

## 🐛 故障排查

### 问题 1: API 调用失败

```bash
# 检查 API Key
cat .env | grep DEEPSEEK_API_KEY

# 测试 API 连接
python -c "from antigravity.auditor import Auditor; print(Auditor('.')._call_deepseek('test'))"
```

### 问题 2: 测试失败

```bash
# 查看详细日志
pytest tests/ -v

# 查看 vibe_audit.log
tail -f vibe_audit.log
```

### 问题 3: Dashboard 无法访问

```bash
# 检查端口占用
netstat -ano | findstr :8501

# 重启 Dashboard
python start_dashboard.py
```

---

## 📚 文档

- [P1 完整总结](https://github.com/XAIOxiao-guaisou/AGENT/blob/master/docs/p1_complete_summary.md)
- [P2 完整总结](https://github.com/XAIOxiao-guaisou/AGENT/blob/master/docs/p2_complete_summary.md)
- [P3 完整总结](https://github.com/XAIOxiao-guaisou/AGENT/blob/master/docs/p3_complete_summary.md)
- [任务发射台指南](https://github.com/XAIOxiao-guaisou/AGENT/blob/master/docs/task_launcher_guide.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 强大的 AI API
- [Streamlit](https://streamlit.io/) - 优雅的 Dashboard 框架
- [watchdog](https://github.com/gorakhargosh/watchdog) - 文件监控库
- [tiktoken](https://github.com/openai/tiktoken) - Token 计数工具

---

## 📞 联系方式

- GitHub: [@XAIOxiao-guaisou](https://github.com/XAIOxiao-guaisou)
- Issues: [GitHub Issues](https://github.com/XAIOxiao-guaisou/AGENT/issues)

---

**Antigravity - 让 AI 成为你的代码守护者!** 🚀
