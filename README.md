# diwu-workflow

[![GitHub Stars](https://img.shields.io/github/stars/ssdiwu/diwu-workflow?style=social)](https://github.com/ssdiwu/diwu-workflow/stargazers)
[![GitHub License](https://img.shields.io/github/license/ssdiwu/diwu-workflow)](https://github.com/ssdiwu/diwu-workflow/blob/main/LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-orange)](https://github.com/ssdiwu/diwu-workflow)

diwu 编码工作流套件 — Claude Code 插件。提供项目初始化、任务规划、产品需求文档、架构决策记录、产品文档五个工具，通过 Commands 主动触发，通过 Skills 自动激活，通过 Hooks 防止目标漂移。

## 设计理念

AI 擅长执行，不擅长决策。diwu-workflow 的核心主张是：**人负责决策，AI 负责操作**。

工作流基于四个规范驱动开发的实践：

- **BDD**（行为驱动）：所有任务的验收条件用 Given/When/Then 格式写死，Agent 按此实现，不得自行解释需求
- **TDD**（测试驱动）：验证先于完成——未通过验收条件的任务不允许标记 Done，不允许提交 commit
- **SDD**（规范驱动）：产品文档（`/ddoc`）和架构决策（`/dadr`）在实施前落地，代码跟着规范走，不是规范跟着代码补
- **DDD**（领域驱动）：`/ddoc` 按功能域组织文档（`auth.md` / `billing.md` / …），每个任务只需加载对应域的文档，而不是整个代码库——遵循关注点分离原则，让 AI 读最少的上下文完成当前任务，同时降低跨域污染的风险

在此之上，用**强约束状态机**控制任务流转：

```
InDraft（草稿）→ InSpec（已锁定）→ InProgress（实施中）→ InReview（待验证）→ Done（完成）
```

状态机是一种编程思路：系统在任意时刻只能处于**一个明确的状态**，且只有满足特定条件才能转移到下一个状态，所有不合法的转移直接被忽略。用在 AI 工作流上，好处是：AI 无法通过「自行判断」跳过某个状态——它不能在需求还是草稿时就开始写代码，不能在验证没过时提交 commit，也不能在遇到阻塞时假装任务完成。每个状态的边界由规则定义，不依赖 AI 的自我约束。

每一步的推进条件和禁止行为都有明确规则。Agent 遇到阻塞不能假装完成，遇到需求问题不能自行变更，需求未确认（InDraft）不能开始实施。**所有需要判断的决策节点，都由人来把关**——Agent 负责的是把确认过的事情做完、做对。

---

## 安装

```
/plugin marketplace add ssdiwu/diwu-workflow
/plugin install diwu-workflow@ssdiwu
```

## 使用

| 命令 | 作用 | 自动触发场景 |
|------|------|------------|
| `/dinit` | 初始化项目工作流结构 | 新建项目、创建 CLAUDE.md |
| `/dprd` | 生成产品需求文档（PRD） | 写 PRD、产品方案 |
| `/dadr` | 记录架构决策（ADR） | 技术选型、不可逆约束 |
| `/ddoc` | 产品文档（正向/逆向两种模式） | 写文档、还原文档 |
| `/dtask` | 将功能描述拆解为任务列表 | 规划功能、分解需求 |

---

## 典型工作流

### 新需求

```
/dprd          # 与产品讨论方案，生成 PRD
/dadr          # 有架构决策时记录（可选）
/ddoc          # 基于 PRD 正向生成产品文档
/dtask         # 将方案拆解为可执行任务列表
```

> 示例：要做一个「消息通知」功能 → 先 `/dprd` 讨论推送方式和触发条件，确定用 WebSocket 还是轮询时用 `/dadr` 记录决策，方案通过后 `/ddoc` 写产品文档，最后 `/dtask` 拆出具体任务。

### 已有项目

```
/ddoc          # 逆向还原现有代码的产品文档
/dprd          # 基于现有产品讨论新需求
/dadr          # 记录新的架构决策（可选）
/ddoc          # 正向补充新功能文档
/dtask         # 拆解新功能任务
```

> 示例：接手一个老项目 → 先 `/ddoc`（逆向模式）从代码还原文档，再用 `/dprd` 讨论要加的新功能，后续流程同「新需求」。

---

## 核心工作流

### 任务状态机

```mermaid
stateDiagram-v2
    [*] --> InDraft: 创建任务
    InDraft --> InSpec: 人工确认需求
    InDraft --> Cancelled: 需求取消

    InSpec --> InProgress: Agent 开始实施
    InSpec --> InSpec: 发现问题，提交 CR

    InProgress --> InReview: 实现完成
    InProgress --> InSpec: 遇到阻塞，退回
    InProgress --> Cancelled: 需求取消

    InReview --> Done: 验证通过
    InReview --> InProgress: 验证失败，返工
    InReview --> Cancelled: 需求取消

    Done --> [*]
    Cancelled --> InSpec: 重新激活

    note right of InDraft
        可修改：
        - 任务描述
        - 验收条件
        - 实施步骤
        - blocked_by
    end note

    note right of InSpec
        已锁定，仅可修改：
        - status 字段
        - blocked_by（需记录）
    end note
```

#### 状态说明

| 状态 | 含义 | 谁可以操作 |
|------|------|-----------|
| `InDraft` | 需求草稿中，任务描述、验收条件、实施步骤均可自由修改 | 人工 + Agent |
| `InSpec` | 需求已确认并锁定，只有 `status` 字段可以修改 | 人工确认后由 Agent 推进 |
| `InProgress` | 实施中，Agent 正在按验收条件编写代码 | Agent |
| `InReview` | 实现完成，等待验证通过 | Agent 自审或人工确认 |
| `Done` | 验证通过，终态 | — |
| `Cancelled` | 已取消；可重新激活为 `InSpec` | 人工 |

**关键约束**：`InDraft` 任务 Agent 不会主动执行，必须由人工确认为 `InSpec` 后才会开始实施。

#### 状态转移规则

| 当前状态 | 触发事件 | 新状态 |
|---------|---------|--------|
| `InDraft` | 人工确认需求 | `InSpec` |
| `InSpec` | Agent 开始实施 | `InProgress` |
| `InSpec` | 发现需求问题 | 保持 `InSpec`，提交 Change Request |
| `InProgress` | 实现完成，准备验证 | `InReview` |
| `InProgress` | 遇到阻塞（缺环境/需求矛盾） | 退回 `InSpec`，输出 BLOCKED |
| `InReview` | 小幅修改，Agent 自审通过 | `Done` |
| `InReview` | 大幅修改（改 API 规范或 > 2000 行），人工确认 | `Done` |
| `InReview` | 验证失败 | 退回 `InProgress` |
| `Cancelled` | 需求重新激活 | `InSpec` |

#### task.json 字段说明

任务存储在 `.claude/task.json`，每个任务包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | 数字 | 从 1 递增，永不复用 |
| `description` | 字符串 | 动词开头的一句话任务描述 |
| `status` | 字符串 | 见上方状态说明 |
| `acceptance` | 数组 | 验收条件，功能/UI/修复类必须用 `Given … When … Then …` 格式 |
| `steps` | 数组 | 实施步骤，须自包含（含外部凭据路径、绝对路径） |
| `category` | 字符串 | 见下方分类说明 |
| `blocked_by` | 数组 | 前置任务 ID 列表；前置任务全部 Done 后当前任务才可开始 |

`category` 可选值：

| 值 | 含义 | acceptance 格式要求 |
|----|------|-------------------|
| `functional` | 新增业务功能、API、核心逻辑 | 必须 Given/When/Then |
| `ui` | 页面、组件、交互、样式 | 必须 Given/When/Then |
| `bugfix` | 修复已知 bug | 必须 Given/When/Then |
| `refactor` | 不改变行为的代码结构优化 | 可用简单描述 |
| `infra` | 构建、部署、配置、脚本 | 可用简单描述 |

`acceptance` 示例：
```
"Given 用户已登录 When 点击退出按钮 Then 清除 token 并跳转登录页"
```

### Session 生命周期

每次启动 Agent 时，工作流强制按以下顺序执行，不允许跳过：

1. **Preflight 检查**：运行 `.claude/checks/smoke.sh`（若存在）验证基线环境；检查 `recording.md` 是否有待处理的 Change Request；执行 `git status` 确认工作区干净。
2. **上下文恢复**：读取 `recording.md` 了解上次进度，`git log -20` 了解最近代码变更。
3. **任务选择**：优先恢复 `InProgress` 任务（中断续作）；否则选第一个无阻塞的 `InSpec` 任务；`InDraft` 任务一律跳过，必须先由人工确认。
4. **实施与验证**：按 `acceptance` 条件实现，完成后逐条验证——**未验证 = 未完成**，验证通过才能标记 `InReview`。
5. **提交时机**：只有任务到达 `Done` 时才创建 git commit，内容包含代码变更 + `task.json` + `recording.md` 三者合一。

```mermaid
flowchart TD
    Start([Session 启动]) --> Preflight[1. Preflight 检查]
    Preflight --> Smoke{smoke.sh 存在?}
    Smoke -->|是| RunSmoke[运行基线验证]
    Smoke -->|否| CheckCR[检查 CR]
    RunSmoke --> CheckCR

    CheckCR --> GitStatus[git status]
    GitStatus --> Context[2. 上下文恢复]
    Context --> ReadRecording[读取 recording.md]
    ReadRecording --> GitLog[git log -20]
    GitLog --> SelectTask[3. 选择任务]

    SelectTask --> ReadTasks[读取 task.json]
    ReadTasks --> CheckInProgress{存在 InProgress?}

    CheckInProgress -->|是| ResumeTask[恢复中断任务]
    CheckInProgress -->|否| FindInSpec[查找 InSpec 任务]

    FindInSpec --> CheckBlocked{检查 blocked_by}
    CheckBlocked -->|无阻塞| CanStart[可开始]
    CheckBlocked -->|全部 Done| CanStart
    CheckBlocked -->|有 InReview 且超前<5| CanAdvance[可超前实施]
    CheckBlocked -->|其他| SkipTask[跳过，选择下一个]
    SkipTask --> FindInSpec

    CanStart --> Implement[4. 实施任务]
    CanAdvance --> Implement
    ResumeTask --> Implement

    Implement --> SetInProgress[状态 → InProgress]
    SetInProgress --> CodeImpl[按验收条件实现]
    CodeImpl --> Verify[验证 acceptance]

    Verify --> VerifyOK{验证通过?}
    VerifyOK -->|否| Blocked{遇到阻塞?}
    Blocked -->|是| SetInSpec[状态 → InSpec，输出 BLOCKED]
    Blocked -->|否| CodeImpl

    VerifyOK -->|是| SetInReview[状态 → InReview]
    SetInReview --> CheckScope{修改幅度}
    CheckScope -->|小幅度| AgentReview[Agent 自审 → Done]
    CheckScope -->|大幅度| HumanReview[请求人工确认 → Done]

    AgentReview --> End
    HumanReview --> End
    SetInSpec --> End([Session 结束])
```

### /dtask 任务规划流程

```mermaid
flowchart TD
    A[接收功能描述] --> B[澄清问题<br/>目标 / 边界 / 成功标准]
    B --> C[确定新任务 ID<br/>task.json + archive 取最大值+1]
    C --> D[生成任务列表<br/>写入 .claude/task.json]
    D --> E[质量检查<br/>GWT格式 / 可验证 / 垂直切片]
    E --> F{复杂任务?}
    F -->|functional/ui 且 acceptance>3| G[三视角审查<br/>开发 / QA / 业务]
    F -->|否| H[写入后提示]
    G --> H
```

### /ddoc 文档工作流

```mermaid
flowchart TD
    A[选择模式] --> B{正向 or 逆向?}

    B -->|正向：需求→文档| C[六步设计法]
    C --> C1[找约束：五维度]
    C1 --> C2[定义原子]
    C2 --> C3[设计组合]
    C3 --> C4[划定边界]
    C4 --> C5[降级路径]
    C5 --> C6[同步策略]
    C6 --> Out[输出到 .doc/]

    B -->|逆向：代码→文档| D[读取代码库]
    D --> E[AI1：写文档 + 自审]
    E --> F[两层完整性检查]
    F --> G{有缺口?}
    G -->|是| H[逆向 Spec 验证]
    H --> E
    G -->|否| Out
```

### 异常处理

工作流内置三种异常机制，用于处理实施过程中的意外情况。

#### BLOCKED — 遇到阻塞时

当 Agent 遇到以下情况时，会**停止任务**并输出 BLOCKED 信息，等待人工介入：

- 缺少环境配置（API 密钥、数据库连接）
- 外部依赖不可用（第三方服务宕机、需人工授权）
- 验证无法进行（需真实账号、依赖未部署的外部系统）
- 需求存在矛盾或无法实现

BLOCKED 时的行为约束：
- 任务状态退回 `InSpec`（不是 Done，不是 InProgress）
- **禁止**创建 git commit
- **禁止**将任务标记为 Done
- 在 `recording.md` 记录阻塞原因和已完成的工作

人工介入（提供配置/权限/需求修订）后，Agent 从 `InSpec` 恢复继续实施。

#### Change Request — 发现需求问题时

当执行 `InSpec` 任务时发现验收条件无法实现或存在矛盾，Agent 会提交 Change Request，而不是强行实施：

1. 任务状态**保持** `InSpec`（不退回 InDraft）
2. 输出 CR 说明：原因、建议的 acceptance 修改、影响评估
3. 等待人工批准
4. 批准后更新 `task.json` 中的 acceptance，继续实施

CR 与 BLOCKED 的区别：BLOCKED 是环境/依赖问题，CR 是需求本身的问题。

#### 超前实施 — 前置任务还在 InReview 时

当前任务被某个 `InReview` 状态的任务阻塞时，Agent 可以超前执行后续任务，而不是空等：

- 允许最多超前 5 个任务
- 超前任务完成时标记 `InReview` 并立即创建 commit（标注为超前实施）
- 超前 5 个后暂停，等待阻塞任务验收通过
- 若阻塞任务验收失败，评估受影响的超前任务并协商回退方式（`git revert` / 保留修改 / `git reset`）

---

## Hooks

| Hook | 触发时机 | 作用 |
|------|---------|------|
| `PreToolUse` (Bash) | 每次执行 Bash 前 | 输出当前 InProgress 任务的 acceptance 条件，防止目标漂移 |
| `Stop` | 回合结束时 | 四分支任务循环：① 有 InProgress → block 继续当前任务；② InReview 积压 > 5 → 放行并通知人工验收；③ 有未阻塞的 InSpec → block 投喂下一任务；④ 全部完成 → 放行并通知完工。通知支持 macOS（系统通知+铃声）、Linux（notify-send）、终端铃声保底 |

---

## 仓库结构

```
diwu-workflow/
├── .claude-plugin/
│   ├── plugin.json          # 插件描述
│   └── marketplace.json     # 市场索引
├── commands/                # 用户主动触发（/dinit 等）
│   ├── dinit.md
│   ├── dtask.md
│   ├── dprd.md
│   ├── dadr.md
│   └── ddoc.md
├── skills/                  # Claude 自动加载的背景知识
│   └── diwu-doc/
├── assets/
│   └── dinit/               # /dinit 依赖的模板与规则
│       └── assets/
│           ├── *.template   # CLAUDE.md / task.json 等模板
│           └── rules/       # core-states / core-workflow 等规则文件
└── hooks/
    ├── hooks.json
    └── scripts/
```

---

## License

MIT
