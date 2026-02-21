# diwu-workflow

[![GitHub Stars](https://img.shields.io/github/stars/ssdiwu/diwu-workflow?style=social)](https://github.com/ssdiwu/diwu-workflow/stargazers)
[![GitHub License](https://img.shields.io/github/license/ssdiwu/diwu-workflow)](https://github.com/ssdiwu/diwu-workflow/blob/main/LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-orange)](https://github.com/ssdiwu/diwu-workflow)

diwu 编码工作流套件 — Claude Code 插件。提供项目初始化、任务规划、架构决策记录、产品文档四个工具，通过 Commands 主动触发，通过 Skills 自动激活，通过 Hooks 防止目标漂移。

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
| `/dplan` | 将功能描述拆解为任务列表 | 规划功能、分解需求 |
| `/dadr` | 记录架构决策（ADR） | 技术选型、不可逆约束 |
| `/ddoc` | 产品文档（正向/逆向两种模式） | 写文档、还原文档 |

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

### Session 生命周期

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

### /dplan 任务规划流程

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

---

## Hooks

| Hook | 触发时机 | 作用 |
|------|---------|------|
| `PreToolUse` (Bash) | 每次执行 Bash 前 | 输出当前 InProgress 任务的 acceptance 条件，防止目标漂移 |
| `Stop` | 回合结束时 | 检查是否有未完成任务（InReview > 5 时豁免），防止遗漏 |

---

## 仓库结构

```
diwu-workflow/
├── .claude-plugin/
│   ├── plugin.json          # 插件描述
│   └── marketplace.json     # 市场索引
├── commands/                # 用户主动触发（/dinit 等）
│   ├── dinit.md
│   ├── dplan.md
│   ├── dadr.md
│   └── ddoc.md
├── skills/                  # Claude 自动加载的背景知识
│   ├── diwu-init/
│   ├── diwu-plan/
│   ├── diwu-adr/
│   └── diwu-doc/
└── hooks/
    └── hooks.json
```

---

## License

MIT
