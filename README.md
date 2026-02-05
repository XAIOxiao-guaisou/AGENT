# Antigravity 部署与最佳实践指南

本指南将帮助你将 Antigravity 自修正编码监管系统部署到你的开发环境中，并提供最佳实践建议。

## 1. 核心架构回顾

Antigravity 由以下四个核心组件构成，旨在实现“Vibe Coding, Logic Auditing”：

1.  **Sheriff-1 Auditor (审计官)**: 位于 `antigravity/auditor.py`。它使用 DeepSeek-R1 模型，根据 `PLAN.md` 严格审计代码逻辑。它具备“幻觉检测”能力，能识别空壳代码。
2.  **Monitor (监视器)**: 位于 `antigravity/monitor.py`。实时监控文件变动，具备 **3秒防抖 (Debounce)** 和 **循环防御 (Loop Prevention)** 机制，防止 API 滥用和死循环。
3.  **Circuit Breaker (熔断器)**: 当同一文件连续验证失败超过 3 次，系统会自动停止审计并进入“手动模式”，保护你的 Token 额度。
4.  **Auto-Rollback (自动回滚)**: 位于 `antigravity/test_runner.py`。当检测到毁灭性错误（测试全挂）时，自动执行 `git stash save` 回滚代码。

## 2. 环境部署

### 2.1 依赖安装

确保你的 Python 环境安装了以下库：

```bash
pip install requests watchdog plyer
```

-   `requests`: 用于调用 DeepSeek API。
-   `watchdog`: 用于文件系统监控。
-   `plyer`: 用于跨平台系统通知（支持 Windows/macOS/Linux）。

### 2.2 虚拟环境 (Virtual Environment)

建议在虚拟环境中运行 Antigravity，以避免污染全局 Python 环境。

**创建并激活 (Windows):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**创建并激活 (macOS/Linux):**

```bash
python3 -m venv venv
source venv/bin/activate
```

**安装依赖:**

```bash
pip install -r requirements.txt
```

### 2.3 Git 环境

Antigravity 强依赖 Git 进行差异分析 (`git diff`) 和回滚 (`git stash`)。
**必须确保：**
1.  你的项目已经是一个 Git 仓库 (`git init`)。
2.  `git` 命令在系统 PATH 中可用。
3.  建议在根目录配置 `.gitignore`，忽略临时文件。

### 2.3 API Key 配置

你需要设置环境变量 `DEEPSEEK_API_KEY`。

**PowerShell (当前环境):**
注意：你刚才的尝试中有语法错误（使用了 `-` 而不是 `=`）。正确命令如下：
```powershell
$env:DEEPSEEK_API_KEY="sk-your-actual-api-key-here"
```

**永久生效 (Windows):**
在“编辑系统环境变量”中添加用户变量 `DEEPSEEK_API_KEY`。

## 3. 启动与使用

### 3.1 启动监管者

在项目根目录下运行：

```bash
# 确保在根目录
python -m antigravity.monitor
```

控制台显示 `Antigravity Monitor started...` 即表示启动成功。

### 3.2 启动 Web 监控面板 (New)

Antigravity 现在配备了基于 Streamlit 的可视化仪表盘。

```bash
streamlit run antigravity/dashboard.py
```

访问浏览器显示的 URL (通常是 `http://localhost:8501`) 即可查看实时审计日志和任务状态。

### 3.3 🚀 极速上手：Antigravity 工作流 (Step-by-Step)

不要被复杂的架构吓到，实际使用只需简单的 **"三步走"**：

#### Step 1: 制定法律 (Write the Plan)
Auditor 需要依据来判断代码是否合格。
打开 `PLAN.md`，用自然语言写下你当前的任务要求。
> **PLAN.md 示例**:
> "实现一个 `calculate_total` 函数。如果是 VIP 用户，打 8 折。必须处理价格为负数的异常情况。"

#### Step 2: 沉浸编码 (Just Code)
打开你的代码编辑器 (VS Code/Cursor等)，开始写代码。
*   你可以写得很随意 ("Vibe Coding")。
*   **但请注意**：每当按下 `Ctrl+S` 保存文件后，Antigravity 就会在后台苏醒。

#### Step 3: 接受审判 (Audit & Fix)
保存文件 3 秒后，观察 Monitor 或 Web 面板：
*   ✅ **绿灯 (PASS)**: 恭喜，你的逻辑严密，继续写下一个功能。
*   🔴 **红灯 (CRITICAL)**:
    1.  你的代码文件顶部会被自动插入一行 `# FIXME: DeepSeek Auditor...`。
    2.  打开项目根目录的 `VIBE_FIX.md`，查看 DeepSeek 给出的具体修改建议。
    3.  **修改代码** 并再次保存。
    4.  重复此过程，直到变回绿灯。

#### (可选) Step 4: 毁灭性打击 (Auto-Rollback)
如果你引入了导致项目崩溃的代码（所有测试全挂），Antigravity 会自动执行 `git stash`，把你回滚到上一次的安全状态。
**此时请查看控制台的红色警报，冷静下来，重新思考你的代码。**

## 4. 最佳实践与避坑

### 💡 避免“幻觉循环”
Auditor 会通过检测文件头部的 `# FIXME` 签名来避免重复审计。
**操作建议**: 在修复代码时，**请务必手动删除或保留该注释**（系统在通过后不会自动删除，需人工确认）。

### 💡 智能测试映射
系统的 `test_runner.py` 使用启发式规则查找测试文件：
*   `src/auth.py` -> `tests/test_auth.py`
*   `src/core/login.py` -> `tests/core/test_login.py`
**操作建议**: 保持良好的单元测试命名习惯，确保 Antigravity 能找到对应的测试进行增量验证。

### 💡 熔断恢复
如果触发了“手动模式 (Manual Mode)”（控制台红色警报）：
1.  检查 `VIBE_FIX.md`，DeepSeek 可能发现了根本性的逻辑漏洞。
2.  手动修复代码。
3.  重启 `monitor.py` 进程以重置计数器。

## 5. 常见问题排查

-   **ImportError**: 运行脚本时请确保根目录在 PYTHONPATH 中，或者使用 `python -m antigravity.monitor` 方式运行。
-   **Win10Toast/Plyer 报错**: 如果系统不支持通知，Antigravity 会自动降级为控制台红色文字报警，不影响核心功能。
-   **API 401 错误**: 检查 `DEEPSEEK_API_KEY` 是否正确设置。

---
**Enjoy your safe Vibe Coding!** 🚀
