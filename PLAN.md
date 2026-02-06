# Antigravity Project - PLAN.md

---

## 0. 项目基础信息 (Project Meta)

**项目名称**: Antigravity

**根目录**: `d:\桌面\AGENT\`

**核心目标**: 一个基于 AI 的全自动代码生成与项目管理系统,实现从需求文档到可运行代码的端到端自动化交付。

---

## 1. 架构蓝图 (Architecture Blueprint)

Agent 必须严格按照以下结构进行开发,禁止在未经授权的路径创建文件。

### 核心模块结构

```
antigravity/
├── main.py                      # 入口模块 (负责调度与初始化)
├── core/
│   ├── auditor.py              # 核心业务: AI 代码审计与生成
│   ├── monitor.py              # 核心业务: 文件监控与自动触发
│   └── change_detector.py      # 核心业务: 增量变更检测
├── utils/
│   ├── helpers.py              # 工具库: 通用工具函数
│   └── token_counter.py        # 工具库: Token 计数与优化
├── config/
│   └── settings.json           # 配置管理: API Keys、参数等
├── p3_state_manager.py         # P3: 多项目状态管理
├── p3_root_detector.py         # P3: 动态项目根目录检测
├── vibe_check.py               # P3 Phase 18: 项目健康诊断
├── doc_generator.py            # P3 Phase 18: 自动文档生成
├── performance_monitor.py      # 性能监控与优化
├── dashboard.py                # Streamlit Dashboard UI
└── tests/
    ├── test_auditor.py         # 测试套件: 审计模块测试
    ├── test_monitor.py         # 测试套件: 监控模块测试
    └── test_p3_state.py        # 测试套件: P3 状态管理测试
```

### 项目目录结构

```
projects/
├── {PROJECT_NAME}/
│   ├── PLAN.md                 # 项目需求文档
│   ├── .antigravity_state.json # 项目状态文件
│   ├── main.py                 # 项目入口
│   ├── core/                   # 项目核心逻辑
│   ├── utils/                  # 项目工具库
│   ├── config/                 # 项目配置
│   ├── tests/                  # 项目测试
│   ├── data/                   # 项目数据存储
│   ├── README.md               # 自动生成的项目文档
│   └── requirements.txt        # 自动生成的依赖列表
```

---

## 2. 核心逻辑要求 (Core Logic - "The Law")

这是 Agent 的执行准则,Vibe Check 将以此进行项目健康度评分。

### 初始化流程

- [x] 启动时必须读取 `config/settings.json`
- [x] 检查必要的运行环境 (DeepSeek API Key)
- [x] 初始化 P3StateManager 进行多项目状态管理
- [x] 启动 PerformanceMonitor 记录性能指标

### 业务逻辑

#### Monitor 模块 (文件监控)
- [x] 使用 `watchdog` 监控 `projects/` 目录下的所有 PLAN.md 文件
- [x] 检测到 PLAN.md 变更后,触发项目级同步
- [x] 使用 P3RootDetector 动态检测项目根目录
- [x] 每个项目维护独立的 `.antigravity_state.json`

#### Auditor 模块 (AI 代码生成)
- [x] 读取 PLAN.md 提取需求
- [x] 使用 ChangeDetector 进行增量分析
- [x] 调用 DeepSeek API 生成代码
- [x] 实现智能 Token 优化 (仅发送变更部分)
- [x] 生成的代码必须包含详细 Docstrings
- [x] 核心函数必须有类型注解

#### 异常处理
- [x] 网络请求失败需重试 3 次 (指数退避)
- [x] API 调用失败记录到审计日志
- [x] 文件写入失败触发回滚机制
- [x] 所有异常必须记录到 P3StateManager

### 数据隔离

- [x] 每个项目的状态存储在 `projects/{name}/.antigravity_state.json`
- [x] 全局项目注册表存储在 `.antigravity_global.json`
- [x] 审计日志按项目隔离,互不干扰
- [x] 性能快照按项目独立记录

---

## 3. 技术栈约束 (Tech Stack)

### 语言与版本
- **Python**: 3.10+
- **优先使用**: Pathlib (禁止使用 `os.path`)
- **类型系统**: 强制使用 Type Hinting

### 必选库

```python
# 核心依赖
streamlit>=1.28.0          # Dashboard UI
watchdog>=3.0.0            # 文件监控
requests>=2.31.0           # HTTP 请求
pathlib                    # 路径操作 (内置)

# AI 集成
openai>=1.0.0              # DeepSeek API 客户端

# 数据处理
pandas>=2.0.0              # 数据分析 (可选)

# 测试框架
pytest>=7.4.0              # 单元测试
pytest-cov>=4.1.0          # 测试覆盖率
```

### 代码风格约束

#### 强制要求
1. **Docstrings**: 所有公共函数/类必须包含详细文档
   ```python
   def example_function(param: str) -> bool:
       """
       Brief description.
       
       Args:
           param: Parameter description
       
       Returns:
           Return value description
       """
   ```

2. **类型注解**: 核心函数必须有完整类型标注
   ```python
   from typing import Dict, List, Optional
   
   def process_data(data: List[Dict]) -> Optional[str]:
       pass
   ```

3. **性能监控**: 关键操作必须使用装饰器记录耗时
   ```python
   from antigravity.performance_monitor import track_performance
   
   @track_performance
   def expensive_operation():
       pass
   ```

4. **Pathlib 优先**: 禁止使用 `os.path`
   ```python
   # ✅ 正确
   from pathlib import Path
   project_root = Path("projects") / project_name
   
   # ❌ 错误
   import os
   project_root = os.path.join("projects", project_name)
   ```

---

## 4. 交付与验证标准 (Definition of Done)

项目只有满足以下条件才算 **"Vibe Approved"**:

### 自动化测试
- [ ] 运行 `pytest tests/` 必须全量通过
- [ ] 测试覆盖率 > 70%
- [ ] 所有核心模块有对应测试文件

### Vibe Check 诊断
- [x] 侧边栏诊断分数必须 > 85分 (当前: Phase 18 完成)
- [x] 无 Critical 级别问题
- [x] 所有 Recommendations 已处理

### 文档完备
- [x] 已生成包含文件树的 `README.md`
- [x] 已生成准确的 `requirements.txt`
- [x] PLAN.md 遵循标准模板
- [x] 所有模块有详细注释

### 增量验证
- [x] 修改 `utils` 模块后,系统能通过增量同步自动修复 `main` 模块的调用
- [x] ChangeDetector 正确识别文件依赖关系
- [x] Token 优化生效,仅发送变更部分

### P3 多项目隔离
- [x] 每个项目有独立的 `.antigravity_state.json`
- [x] 项目间状态完全隔离
- [x] Dashboard 可无缝切换项目 (<1s)
- [x] 性能监控按项目独立记录

---

## 5. 快速启动指南 (Quick Start for User)

### 🚀 发射项目

1. **打开 Dashboard**
   ```bash
   streamlit run antigravity/dashboard.py
   ```

2. **创建新项目**
   - 在侧边栏输入项目名称
   - 定义文件结构 (如 `main.py`, `core/logic.py`)
   - 上传业务需求文档 (可选)
   - 点击 **"🔥 创建项目并启动"**

3. **自动聚焦**
   - 项目创建后自动切换到新项目
   - Dashboard 显示项目信息
   - Monitor 自动检测并开始生成代码

### 📊 监控进度

- **Token 进度条**: 实时显示上下文优化效果
- **审计日志**: 查看所有代码生成记录
- **性能指标**: 监控 API 调用耗时和 Token 使用

### 🩺 诊断项目健康度

1. 在侧边栏点击 **"🩺 运行 Vibe Check"**
2. 查看健康度评分 (0-100分)
3. 查看发现的问题和改进建议
4. 根据建议优化项目

### 📄 生成项目文档

1. 在侧边栏点击 **"📄 生成文档"**
2. 自动生成 `README.md` (含项目树)
3. 自动生成 `requirements.txt` (扫描导入)
4. 文档保存在项目根目录

### 🔄 增量更新

1. 修改 `PLAN.md` 添加新需求
2. Monitor 自动检测变更
3. ChangeDetector 分析影响范围
4. Auditor 仅生成变更部分代码
5. Token 优化自动生效

---

## 6. P3 Phase 16-18 完成状态

### Phase 16: 项目隔离 & 动态路径 ✅
- [x] P3StateManager 实现全局/本地状态分离
- [x] P3RootDetector 动态检测项目根目录
- [x] 多项目状态完全隔离
- [x] 向后兼容 Legacy 模式

### Phase 17: 多项目看板 ✅
- [x] Dashboard 项目选择器
- [x] 项目状态指示器 (🟢🟡🔴)
- [x] 项目级性能监控
- [x] 快速项目切换 (<1s)

### Phase 18: Vibe 抛光 ✅
- [x] Vibe Check 混合诊断系统
- [x] 自动文档生成 (README + requirements)
- [x] 脚手架自动聚焦
- [x] LRU 缓存性能优化
- [x] Dashboard 快速操作工具箱

---

## 7. 下一步计划 (Future Roadmap)

### 短期优化
- [ ] 添加更多 AI 驱动的代码质量建议
- [ ] 实现可视化依赖关系图
- [ ] 支持自动代码格式化 (Black, isort)
- [ ] 添加 Git 集成 (自动提交)

### 中期目标
- [ ] 支持多种 AI 模型 (GPT-4, Claude, Gemini)
- [ ] 实现代码审查自动化
- [ ] 添加性能基准测试
- [ ] 支持 Docker 容器化部署

### 长期愿景
- [ ] 完整的 CI/CD 集成
- [ ] 云端项目协作
- [ ] 插件系统支持
- [ ] 多语言支持 (JavaScript, Go, Rust)

---

**最后更新**: 2026-02-06  
**当前版本**: P3 Phase 18 Complete  
**项目状态**: 🟢 Vibe Approved