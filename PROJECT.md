# opencode-diwu-workflow

## 项目信息

- **项目名称**：opencode-diwu-workflow
- **描述**：diwu 编码工作流套件 —— opencode 原生插件版本
- **技术栈**：TypeScript + Markdown
- **用途**：维护 opencode 插件，提供任务管理、文档生成和纠偏恢复工作流

## 项目结构

```
opencode-diwu-workflow/
├── .opencode/                    # opencode 核心配置目录
│   ├── agents/                   # Agent 定义（11 个）
│   │   ├── build.md             # 全权限实施模式
│   │   ├── plan.md              # 受限规划模式
│   │   ├── diwu-expert.md       # 工作流专家
│   │   ├── verifier.md          # 独立验收代理
│   │   ├── ui-designer.md       # UI/UX 设计
│   │   ├── backend-architect.md # 后端架构
│   │   ├── frontend-architect.md # 前端架构
│   │   ├── api-tester.md        # 测试策略
│   │   ├── devops-architect.md  # 运维部署
│   │   ├── performance-optimizer.md # 性能优化
│   │   └── legal-compliance.md  # 法规合规
│   ├── commands/                 # 自定义命令（7 个）
│   │   ├── dinit.md             # 项目初始化
│   │   ├── dtask.md             # 任务规划
│   │   ├── dprd.md              # 产品需求文档
│   │   ├── dadr.md              # 架构决策记录
│   │   ├── ddoc.md              # 产品文档
│   │   ├── ddemo.md             # Demo 能力规格
│   │   └── dcorr.md             # 纠偏恢复协议
│   ├── plugins/                  # TypeScript 插件
│   │   └── diwu-workflow.ts     # 核心插件（hooks 重写）
│   ├── references/               # 参考文档（10 个）
│   │   ├── constraints.md       # 架构约束
│   │   ├── states.md            # 任务状态机
│   │   ├── workflow.md          # 工作流规则
│   │   ├── exceptions.md        # 异常处理
│   │   ├── templates.md         # 格式模板
│   │   ├── file-layout.md       # 目录结构
│   │   ├── judgments.md         # 判断锚点
│   │   ├── decisions.md         # 历史决策
│   │   ├── lessons.md           # 踩坑经验
│   │   └── README.md            # 规则索引
│   ├── skills/                   # 技能知识库（10 个）
│   │   ├── dtask/               # 任务管理
│   │   ├── dsess/               # Session 生命周期
│   │   ├── dcorr/               # 纠偏恢复
│   │   ├── dvfy/                # 验证规则
│   │   ├── djug/                # 判断决策
│   │   ├── drec/                # 记录规范
│   │   ├── darc/                # 归档规则
│   │   ├── ddoc/                # 产品文档工具
│   │   ├── dprd/                # 产品需求分析
│   │   └── ddemo/               # 能力验证方法论
│   └── state/                    # 插件状态持久化
├── .diwu/                        # 工作流运行时数据
│   ├── dtask.json                 # 任务列表
│   ├── recording/                # Session 记录
│   ├── decisions.md              # 设计决策
│   ├── lessons.md                # 踩坑经验
│   ├── dsettings.json             # 可调参数
│   ├── checks/                   # 验证脚本
│   └── archive/                  # 归档数据
├── opencode.json                 # opencode 项目配置
├── AGENTS.md                     # 规则入口文件
└── README.md                     # 项目说明
```

## 核心组件

### 1. 插件（.opencode/plugins/diwu-workflow.ts）

TypeScript 插件，实现以下 hooks：
- `event` - 事件监听（session.created / session.idle / tui.prompt.append）
- `experimental.chat.system.transform` - 将 rules-index 注入 system prompt
- `tool.execute.before` - 退化检测、任务提醒
- `tool.execute.after` - JSON 校验、上下文监控、3-Strike 错误协议
- `experimental.session.compacting` - Compact 保护（checkpoint 保存）

### 2. 命令（.opencode/commands/）

7 个用户触发的命令：
- `/dinit` - 初始化工作流结构
- `/dtask` - 任务规划
- `/dprd` - 产品需求文档
- `/dadr` - 架构决策记录
- `/ddoc` - 产品文档
- `/ddemo` - Demo 能力规格
- `/dcorr` - 纠偏恢复协议

### 3. 技能（.opencode/skills/）

10 个自动加载的技能：
- `dtask` - 任务管理核心方法论
- `dsess` - Session 生命周期管理
- `dcorr` - 纠偏与误判排查
- `dvfy` - 验证规则与证据优先级
- `djug` - 判断决策方法论
- `drec` - 记录规范与踩坑经验
- `darc` - 归档规则
- `ddoc` - 产品文档工具（正向/逆向）
- `dprd` - 产品需求分析方法论
- `ddemo` - 积木式能力验证方法论

### 4. 代理（.opencode/agents/）

11 个代理定义：
- `build` - 全权限实施模式
- `plan` - 受限规划模式
- `diwu-expert` - 工作流专家
- `verifier` - 独立验收验证
- `ui-designer` - UI/UX 设计
- `backend-architect` - 后端架构
- `frontend-architect` - 前端架构
- `api-tester` - 测试策略
- `devops-architect` - 运维部署
- `performance-optimizer` - 性能优化
- `legal-compliance` - 法规合规

## 工作流

### 任务管理

状态机：InDraft → InSpec → InProgress → InReview → Done

- InDraft - 需求草稿，Agent 可修改
- InSpec - 需求锁定，Agent 只能改状态
- InProgress - 实施中
- InReview - 验证中
- Done - 完成

### 文档生成

支持多种文档类型：
- PRD - 产品需求文档
- ADR - 架构决策记录
- 产品文档 - 四层结构（数据/接口/业务/产品）
- Demo 规格 - 能力验证单元

## 与 Claude Code 版本的差异

| 维度 | Claude Code | opencode |
|------|-------------|----------|
| 插件格式 | Python hooks | TypeScript plugin |
| 状态持久化 | `.diwu/` + `.claude/` | `.diwu/`（统一） |
| Agent 架构 | 3 核心 + 7 领域 | 3 核心 + 7 领域（命名不同） |
| 配置格式 | plugin.json + marketplace.json | opencode.json |
| 规则注入 | UserPromptSubmit hook | `experimental.chat.system.transform` |
| Skills 加载 | 按需 Read | opencode 自动加载 `.opencode/skills/` |
| 项目入口 | `CLAUDE.md` | `AGENTS.md` |

## 使用方法

```bash
# 启动 opencode
opencode

# 使用命令
/dinit          # 初始化工作流
/dtask          # 规划任务
/dprd           # 生成 PRD
/dadr           # 记录架构决策
/ddoc           # 生成产品文档
/ddemo          # 创建 Demo 规格
/dcorr          # 纠偏恢复

# 自动触发的技能
"帮我写一个 PRD"           # 触发 dprd 技能
"这个功能需要做 Demo 吗？"  # 触发 ddemo 技能
"帮我整理代码库文档"        # 触发 ddoc 技能
```

## 状态持久化

使用 `.diwu/` 目录存储运行时数据：
- dtask.json - 任务列表
- recording/ - Session 记录文件
- decisions.md - 设计决策
- lessons.md - 踩坑经验
- dsettings.json - 可调参数
- checks/ - 验证脚本
- archive/ - 归档数据

插件内部状态使用 `.opencode/state/` 目录：
- session-main - 主 session ID
- context-counter - 上下文工具调用计数
- context-warned - 是否已警告
- context-critical - 是否已临界
- review-used - review 计数

## 参考文档

详见 `.opencode/references/` 目录：
- states.md - 任务状态机与 acceptance 格式
- workflow.md - Session 启动、任务规划、实施、验证
- judgments.md - 判断锚点集中管理
- exceptions.md - 异常处理与 BLOCKED 判定
- templates.md - 格式模板
- file-layout.md - .diwu/ 目录结构与归档规则
- constraints.md - 架构约束（五维约束设计）
