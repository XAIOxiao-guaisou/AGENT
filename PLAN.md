# 🚀 Antigravity 全自动项目开发模板 (P3 专用版)

---

## 0. 项目基础信息 (Project Meta)

**项目名称**: `{{PROJECT_NAME}}`

**根目录**: `projects/{{PROJECT_NAME}}/`

**核心目标**: [用一句话描述项目的最终产出，例如：一个自动爬取小红书博主数据的系统]

---

## 1. 架构蓝图 (Architecture Blueprint)

Agent 必须严格按照以下结构进行开发，禁止在未经授权的路径创建文件。

### 标准文件结构

```
projects/{{PROJECT_NAME}}/
├── main.py                          # 入口模块 (负责调度与初始化)
├── core/
│   └── {{MODULE_NAME}}.py          # 核心业务 (核心算法或逻辑)
├── utils/
│   └── helpers.py                  # 工具库 (通用工具，如网络请求、数据处理)
├── config/
│   └── settings.json               # 配置管理 (存储 API Keys、参数等)
├── tests/
│   └── test_{{MODULE_NAME}}.py     # 测试套件 (集成与单元测试)
├── data/                           # 数据存储目录
├── PLAN.md                         # 项目需求文档 (本文件)
├── README.md                       # 项目文档 (自动生成)
└── requirements.txt                # 依赖列表 (自动生成)
```

---

## 2. 核心逻辑要求 (Core Logic - "The Law")

这是 Agent 的执行准则，Vibe Check 将以此进行项目健康度评分。

### 初始化流程

- [ ] 启动时必须读取 `config/settings.json`
- [ ] 检查必要的运行环境（如 Playwright 浏览器是否安装）
- [ ] 初始化日志系统
- [ ] 验证必要的 API Keys 和配置参数

### 业务逻辑

- [ ] [描述具体的业务逻辑步骤 1]
- [ ] [描述具体的业务逻辑步骤 2]
- [ ] [描述具体的业务逻辑步骤 3]
- [ ] [描述异常处理要求，例如：网络超时需重试 3 次，使用指数退避策略]

### 数据隔离

- [ ] 采集的数据必须存储在项目内的 `data/` 文件夹下
- [ ] 每个任务应生成独立的时间戳文件
- [ ] 数据文件命名规范：`{task_name}_{timestamp}.{format}`

---

## 3. 技术栈约束 (Tech Stack)

### 语言与版本

**语言**: Python 3.10+

**强制要求**:
- 优先使用 `Pathlib` (禁止使用 `os.path`)
- 所有函数必须包含 Type Hinting

### 必选库

```python
# 根据项目需求选择合适的库
requests      # HTTP 请求
pandas        # 数据处理
playwright    # 浏览器自动化
asyncio       # 异步编程
# ... 按需添加
```

### 代码风格约束

1. **Docstrings**: 所有公共函数/类必须包含详细文档
   ```python
   def example_function(param: str) -> bool:
       """
       功能描述
       
       Args:
           param: 参数说明
       
       Returns:
           返回值说明
       """
   ```

2. **类型注解**: 核心函数必须有完整类型标注
   ```python
   from typing import Dict, List, Optional
   
   def process_data(data: List[Dict]) -> Optional[str]:
       pass
   ```

3. **性能监控**: 关键操作必须使用 PerfMonitor 装饰器记录耗时
   ```python
   from antigravity.performance_monitor import track_performance
   
   @track_performance
   def expensive_operation():
       pass
   ```

---

## 4. 交付与验证标准 (Definition of Done)

项目只有满足以下条件才算 **"Vibe Approved"**:

### ✅ 自动化测试
- [ ] 运行 `pytest tests/` 必须全量通过
- [ ] 测试覆盖率 > 70%
- [ ] 所有核心模块有对应测试文件

### ✅ Vibe Check 诊断
- [ ] 侧边栏诊断分数必须 > 85分
- [ ] 无 Critical 级别问题
- [ ] 所有 Recommendations 已处理或记录

### ✅ 文档完备
- [ ] 已生成包含文件树的 `README.md`
- [ ] 已生成准确的 `requirements.txt`
- [ ] 所有核心函数有详细注释

### ✅ 增量验证
- [ ] 在修改 `utils` 模块后，系统能通过增量同步自动修复 `main` 模块的调用
- [ ] ChangeDetector 正确识别文件依赖关系
- [ ] Token 优化生效，仅发送变更部分

---

## 5. 快速启动指南 (Quick Start for User)

### 🚀 发射项目

1. 在 Dashboard 侧边栏输入项目名称
2. 定义文件结构（或使用默认模板）
3. 上传业务需求文档（可选）
4. 点击 **"🔥 创建项目并启动"**
5. 系统自动聚焦到新项目

### 📊 监控进度

- **审计日志**: 实时查看代码生成记录
- **Token 进度条**: 确保上下文优化正常
- **性能指标**: 监控 API 调用耗时

### 🩺 诊断项目健康度

1. 代码生成后，点击侧边栏 **"🩺 运行 Vibe Check"**
2. 查看健康度评分（0-100分）
3. 查看发现的问题和改进建议
4. 根据建议优化代码

### 📄 打包交付

1. 点击侧边栏 **"📄 生成文档"**
2. 自动生成 `README.md`（含项目树）
3. 自动生成 `requirements.txt`（扫描导入）
4. 项目完成，可交付使用

---

## 📝 使用说明

**此文件是项目的灵魂**，Agent 将严格按照此文件的要求进行开发。

### 如何使用此模板

1. 将 `{{PROJECT_NAME}}` 替换为实际项目名称
2. 将 `{{MODULE_NAME}}` 替换为核心模块名称
3. 在"核心逻辑要求"中填写具体的业务逻辑
4. 在"技术栈约束"中选择合适的库
5. 保存文件后，Monitor 会自动检测并触发 Agent 接管

### 重要提示

- ✅ 修改此文件后，系统会自动触发项目级同步
- ✅ 使用增量更新时，仅需修改变更部分
- ✅ 所有 `[ ]` 检查项完成后，运行 Vibe Check 验证
- ✅ 达到 85 分以上即可获得 "Vibe Approved" 认证

---

**模板版本**: P3 Phase 18  
**最后更新**: 2026-02-06  
**状态**: 🟢 Ready for Use
