# diwu-workflow for opencode

diwu 编码工作流套件 —— opencode 插件版本。让 AI 按确认的需求执行开发任务，而非自行发挥。

## 项目说明

这是 diwu-workflow 的 opencode 原生版本，提供完整的任务管理、文档生成和纠偏恢复工作流。

## 目录结构

```
opencode-diwu-workflow/
├── .opencode/
│   ├── agents/          # Agent 定义（11 个：3 核心 + 8 领域）
│   ├── commands/        # 自定义命令（7 个）
│   ├── plugins/         # TypeScript 插件（hooks 重写）
│   ├── references/      # 参考文档（10 个：规则、模板、决策记录）
│   ├── skills/          # 技能知识库（10 个）
│   └── state/           # 插件状态持久化（运行时生成）
├── .diwu/               # 工作流运行时数据（dtask.json, recording/ 等）
├── opencode.json        # opencode 项目配置
├── AGENTS.md            # 规则入口文件
├── install-global.sh    # 全局安装/更新脚本
└── README.md            # 本文件
```

## 组件说明

### Commands（7 个）

| 命令 | 用途 |
|------|------|
| `/dinit` | 初始化工作流结构（AGENTS.md / .diwu/ / .opencode/references/） |
| `/dtask` | 任务规划：将功能描述转化为 dtask.json 任务列表 |
| `/dprd` | 生成产品需求文档（PRD） |
| `/dadr` | 记录架构决策（ADR） |
| `/ddoc` | 产品文档工具（正向/逆向） |
| `/ddemo` | 不确定性功能点验证 |
| `/dcorr` | 纠偏恢复协议 |

### Skills（10 个）

| Skill | 类型 | 触发场景 |
|-------|------|---------|
| `dtask` | 规则 | 任务管理、状态机、GWT acceptance |
| `dsess` | 规则 | Session 生命周期、任务选择 |
| `dcorr` | 规则 | 退化信号检测、纠偏恢复 |
| `dvfy` | 规则 | 证据优先级、Done 判定 |
| `djug` | 规则 | 阶段边界决策、幅度判定 |
| `drec` | 规则 | Session 记录、踩坑经验 |
| `darc` | 规则 | 任务/Recording 归档 |
| `ddoc` | 工具 | 正向/逆向生成产品文档 |
| `dprd` | 工具 | PRD 方法论 |
| `ddemo` | 工具 | 不确定性功能点验证 |

### Agents（11 个）

**核心 Agent（3 个）**：

| Agent | 类型 | 用途 |
|-------|------|------|
| `build` | Primary | 全权限实施模式 |
| `plan` | Primary | 受限规划模式，编辑需确认 |
| `diwu-expert` | Subagent | diwu-workflow 工作流专家 |

**领域 Agent（8 个）**：

| Agent | 触发时机 |
|-------|---------|
| `verifier` | 独立验收验证（核心层） |
| `ui-designer` | UI/UX 设计决策 |
| `backend-architect` | 服务端架构 |
| `frontend-architect` | 前端架构 |
| `api-tester` | 测试策略 |
| `devops-architect` | 运维部署 |
| `performance-optimizer` | 性能问题 |
| `legal-compliance` | 法规要求 |

### Plugin

`.opencode/plugins/diwu-workflow.ts` - TypeScript 插件，实现以下 hooks：

- `event` - 事件监听（session.created / session.idle / tui.prompt.append）
- `experimental.chat.system.transform` - 规则注入 system prompt
- `tool.execute.before/after` - 工具调用守卫（退化检测、JSON 校验、上下文监控）
- `experimental.session.compacting` - Compact 保护（checkpoint 保存）
- `shell.env` - 环境变量注入

## 安装方法

### 全局安装（推荐）

全局安装后，plugin hooks 在所有项目中自动生效，同时提供 `diwu_init` 工具供新项目一键初始化。

```bash
# 1. 进入本仓库
cd /Users/diwu/Documents/codes/Githubs/opencode-diwu-workflow

# 2. 运行安装脚本
./install-global.sh
```

脚本会自动：
1. 复制 `diwu-workflow.ts` 到 `~/.config/opencode/plugins/`
2. 同步 `commands/skills/agents/references` 到 `~/.config/opencode/diwu-workflow/`
3. 在全局 `~/.config/opencode/opencode.json` 中注册插件

### 验证安装

```bash
# 方法 1：检查文件是否存在
ls ~/.config/opencode/plugins/diwu-workflow.ts

# 方法 2：启动 opencode 后问 AI
opencode
# > 你能执行 /dinit 命令吗？
# AI 能识别 = 已安装

# 方法 3：查看启动日志
# 若看到 [diwu-workflow] Plugin loaded. Project type: ... = 已加载
```

### 新项目初始化

进入任意新项目目录：

```bash
cd /path/to/your-new-project
opencode
```

对 AI 说：
> 运行 diwu_init

AI 会自动：
1. 复制 commands/skills/agents/references 到 `.opencode/`
2. 创建 `.diwu/` 目录结构（dtask.json, dsettings.json, recording/, checks/）
3. 更新项目的 `opencode.json`（注册 plugin、agents、commands、instructions）

### 项目级安装（不依赖全局）

```bash
./install-global.sh /path/to/your-project
```

直接把所有内容复制到指定项目，无需全局注册。

## 更新方法

修改本仓库的 plugin 或模板后，重新运行安装脚本即可同步到全局：

```bash
cd /Users/diwu/Documents/codes/Githubs/opencode-diwu-workflow
./install-global.sh
```

**更新策略**：

| 更新内容 | 生效方式 |
|---------|---------|
| Plugin hooks（逻辑修复） | `./install-global.sh` → 所有项目自动生效 |
| Commands/Skills/Agents 内容 | `./install-global.sh` + 各项目运行 `diwu_init` |
| References 规则文档 | `./install-global.sh` + 各项目运行 `diwu_init` |

## 使用方法

```bash
# 启动 opencode
opencode

# 初始化工作流
/dinit

# 规划任务
/dtask 实现用户登录功能

# 生成 PRD
/dprd

# 记录架构决策
/dadr 选择 WebSocket 而非短轮询

# 生成产品文档
/ddoc

# Demo 验证
/ddemo prompt-citation-stability

# 纠偏恢复
/dcorr
```

## 快速开始

### 新项目

```
/dinit          # 初始化工作流结构
/dprd           # 讨论方案，生成 PRD，识别 Demo 需求
/dadr           # 有架构决策时记录（可选）
/ddoc           # 基于 PRD 正向生成产品文档
/ddemo          # 对每个 Demo 需求生成落地方案
/dtask          # Demo 验证通过后，拆解集成任务列表
```

### 接手老项目

```
/ddoc           # 逆向还原现有代码的产品文档
/dprd           # 基于现有产品讨论新需求
/dadr           # 记录新的架构决策（可选）
/ddoc           # 正向补充新功能文档
/dtask          # 拆解新功能任务
```

## 与 Claude Code 版本的差异

| 维度 | Claude Code | opencode |
|------|-------------|----------|
| 插件格式 | Python hooks | TypeScript plugin |
| 状态持久化 | `.diwu/` + `.claude/` | `.diwu/`（统一） |
| Agent 架构 | explorer/implementer/verifier | build/plan/diwu-expert + 8 领域 |
| 配置格式 | plugin.json + marketplace.json | opencode.json |
| 规则注入 | UserPromptSubmit hook | `experimental.chat.system.transform` |
| Skills 加载 | 按需 Read | opencode 自动加载 `.opencode/skills/` |
| 安装方式 | `/plugin marketplace add` | `./install-global.sh` |
| 项目初始化 | `/dinit` | 对 AI 说"运行 diwu_init" |

## License

MIT
