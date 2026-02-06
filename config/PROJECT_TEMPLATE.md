# 🚀 Antigravity 全自动项目开发模板 (P3 专用版)

> **使用说明**: 此模板用于指导 Antigravity 系统自动生成项目。在 Dashboard 创建新项目时，系统会基于此模板生成 PLAN.md。

---

## 0. 项目基础信息 (Project Meta)

**项目名称**: `{{PROJECT_NAME}}`

**根目录**: `projects/{{PROJECT_NAME}}/`

**核心目标**: [一句话描述项目的最终产出，例如：一个自动爬取小红书博主数据的系统]

---

## 1. 架构蓝图 (Architecture Blueprint)

Agent 必须严格按照以下结构进行开发，禁止在未经授权的路径创建文件。

### 标准文件结构

```
projects/{{PROJECT_NAME}}/
├── main.py                      # 入口模块 (负责调度与初始化)
├── core/
│   └── {{MODULE_NAME}}.py      # 核心业务 (核心算法或逻辑)
├── utils/
│   └── helpers.py              # 工具库 (通用工具，如网络请求、数据处理)
├── config/
│   └── settings.json           # 配置管理 (存储 API Keys、参数等)
├── tests/
│   └── test_{{MODULE_NAME}}.py # 测试套件 (集成与单元测试)
├── data/                        # 数据存储目录
├── PLAN.md                      # 项目需求文档 (本文件)
├── README.md                    # 项目文档 (自动生成)
└── requirements.txt             # 依赖列表 (自动生成)
```

### 授权路径

Agent 仅允许在以下路径创建文件:
- `main.py`
- `core/`
- `utils/`
- `config/`
- `tests/`
- `data/`

---

## 2. 核心逻辑要求 (Core Logic - "The Law")

这是 Agent 的执行准则，Vibe Check 将以此进行项目健康度评分。

### 初始化流程

- [ ] 启动时必须读取 `config/settings.json`
- [ ] 检查必要的运行环境（如 Playwright 浏览器是否安装）
- [ ] 初始化日志系统
- [ ] 验证必要的 API Keys 或凭证

### 业务逻辑

- [ ] [描述具体的业务逻辑步骤 1，例如：登录目标网站并获取 Cookie]
- [ ] [描述具体的业务逻辑步骤 2，例如：遍历博主主页获取所有笔记链接]
- [ ] [描述具体的业务逻辑步骤 3，例如：解析每篇笔记的标题、内容和互动数据]
- [ ] [描述异常处理要求，例如：网络超时需重试 3 次，使用指数退避策略]

### 数据隔离

- [ ] 采集的数据必须存储在项目内的 `data/` 文件夹下
- [ ] 每个任务应生成独立的时间戳文件（格式：`YYYYMMDD_HHMMSS_任务名.csv`）
- [ ] 禁止将数据写入项目外的路径

### 错误处理

- [ ] 所有网络请求必须包含超时设置
- [ ] 关键操作必须记录日志
- [ ] 异常必须被捕获并记录详细堆栈信息

---

## 3. 技术栈约束 (Tech Stack)

### 语言与版本

**语言**: Python 3.10+

**强制要求**:
- 优先使用 `pathlib.Path` (禁止使用 `os.path`)
- 所有函数必须包含类型注解 (Type Hinting)

### 必选库

```python
# 根据项目需求选择
requests>=2.31.0        # HTTP 请求
pandas>=2.0.0           # 数据处理
playwright>=1.40.0      # 浏览器自动化 (可选)
pytest>=7.4.0           # 测试框架
```

### 代码风格约束

#### 1. Docstrings (强制)

所有公共函数和类必须包含详细文档:

```python
def fetch_user_data(user_id: str) -> dict:
    """
    获取指定用户的详细信息
    
    Args:
        user_id: 用户的唯一标识符
    
    Returns:
        包含用户信息的字典，格式为 {'name': str, 'bio': str, ...}
    
    Raises:
        ValueError: 当 user_id 格式不正确时
        NetworkError: 当网络请求失败时
    """
    pass
```

#### 2. 类型注解 (强制)

核心函数必须有完整类型标注:

```python
from typing import List, Dict, Optional
from pathlib import Path

def process_data(
    input_file: Path,
    output_dir: Path,
    filters: Optional[List[str]] = None
) -> Dict[str, int]:
    """处理数据文件"""
    pass
```

#### 3. 性能监控 (推荐)

关键操作使用装饰器记录耗时:

```python
from antigravity.performance_monitor import track_performance

@track_performance
def expensive_operation():
    """耗时操作"""
    pass
```

#### 4. Pathlib 优先 (强制)

```python
# ✅ 正确
from pathlib import Path
data_dir = Path("data") / "output"
data_dir.mkdir(parents=True, exist_ok=True)

# ❌ 错误
import os
data_dir = os.path.join("data", "output")
os.makedirs(data_dir, exist_ok=True)
```

---

## 4. 交付与验证标准 (Definition of Done)

项目只有满足以下条件才算 **"Vibe Approved"** ✅

### 自动化测试

- [ ] 运行 `pytest tests/` 必须全量通过
- [ ] 测试覆盖率 > 70%
- [ ] 所有核心模块有对应测试文件

### Vibe Check 诊断

- [ ] 侧边栏诊断分数必须 **> 85分**
- [ ] 无 Critical 级别问题
- [ ] 所有 Warning 级别问题已处理或有明确说明

### 文档完备

- [ ] 已生成包含文件树的 `README.md`
- [ ] 已生成准确的 `requirements.txt`
- [ ] PLAN.md 所有检查项已完成
- [ ] 核心函数有详细注释

### 增量验证

- [ ] 修改 `utils` 模块后，系统能通过增量同步自动修复 `main` 模块的调用
- [ ] ChangeDetector 正确识别文件依赖关系
- [ ] Token 优化生效，仅发送变更部分

---

## 5. 快速启动指南 (Quick Start for User)

### 🚀 步骤 1: 发射项目

1. 打开 Antigravity Dashboard
   ```bash
   streamlit run antigravity/dashboard.py
   ```

2. 在侧边栏填写项目信息:
   - **项目名称**: 输入项目名称（如 `XHSMonitor`）
   - **文件结构**: 定义初始文件（如 `main.py`, `core/scraper.py`）
   - **业务文档**: 上传需求文档或直接编辑 PLAN.md

3. 点击 **"🔥 创建项目并启动"**

4. 系统自动:
   - 创建 `projects/{项目名}/` 目录
   - 生成 PLAN.md
   - 创建文件占位符
   - **自动聚焦到新项目**

### 📊 步骤 2: 监控进度

- **Token 进度条**: 实时显示上下文优化效果
- **审计日志**: 查看所有代码生成记录
- **性能指标**: 监控 API 调用耗时

### 🩺 步骤 3: 诊断健康度

1. 代码生成完成后，点击侧边栏 **"🩺 运行 Vibe Check"**
2. 查看健康度评分（目标 > 85分）
3. 查看发现的问题和改进建议
4. 根据建议优化代码

### 📄 步骤 4: 生成文档

1. 点击侧边栏 **"📄 生成文档"**
2. 自动生成:
   - `README.md` (含项目树和使用说明)
   - `requirements.txt` (扫描所有导入)

### 🔄 步骤 5: 增量迭代

1. 修改 `PLAN.md` 添加新需求
2. Monitor 自动检测变更（~3秒）
3. Auditor 仅生成变更部分代码
4. 重新运行 Vibe Check 验证

---

## 6. 常见问题 (FAQ)

### Q: 如何添加新的依赖库?

A: 在 `config/settings.json` 中添加，或直接在代码中导入，系统会自动检测并更新 `requirements.txt`。

### Q: Vibe Check 分数低于 85 怎么办?

A: 查看 Issues 和 Recommendations 面板，优先处理:
1. 添加缺失的 Docstrings
2. 补充类型注解
3. 添加单元测试
4. 优化 PLAN.md 描述

### Q: 如何切换到其他项目?

A: 在侧边栏的项目选择器中选择目标项目，系统会在 <1s 内完成切换。

### Q: 增量同步不生效怎么办?

A: 确保:
1. PLAN.md 已保存
2. Monitor 正在运行
3. 检查审计日志是否有错误

---

**模板版本**: P3 Phase 18  
**最后更新**: 2026-02-06  
**兼容系统**: Antigravity P3 Complete
