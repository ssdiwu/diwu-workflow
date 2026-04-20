# Spike: Claude Code agents/*.md 配置机制与能力边界

> Task#47 调研产物。基于官方文档 (https://code.claude.com/docs/en/sub-agents) 和项目已有文档 (.doc/subagents.md, .doc/permissions.md, .doc/memory.md) 整理。

---

## 1. agents/*.md 文件格式

Subagent 是带 YAML frontmatter 的 Markdown 文件。frontmatter 定义元数据和配置，body 是 system prompt。

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code...
```

Subagent 只接收自己的 system prompt + 基础环境信息（工作目录等），**不继承**主对话的完整 system prompt 和对话历史。

---

## 2. Frontmatter 字段完整列表

| 字段 | 必需 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | 是 | string | — | 唯一标识符，小写字母 + 连字符 |
| `description` | 是 | string | — | Claude 据此决定何时委派；含 "Use proactively" 可鼓励主动委派 |
| `tools` | 否 | string (逗号分隔) | 继承所有 | 允许的工具列表（allowlist） |
| `disallowedTools` | 否 | string (逗号分隔) | 无 | 拒绝的工具列表（denylist），从继承/指定列表中移除 |
| `model` | 否 | string | `inherit` | `sonnet` / `opus` / `haiku` / `inherit` |
| `permissionMode` | 否 | string | 继承父级 | `default` / `acceptEdits` / `dontAsk` / `bypassPermissions` / `plan` |
| `maxTurns` | 否 | number | 无限制 | 子代理停止前的最大 agentic turns 数 |
| `skills` | 否 | string[] (YAML list) | 无 | 启动时注入的 skills 列表（完整内容注入，不从父对话继承） |
| `mcpServers` | 否 | string[] 或 object | 无 | 可用的 MCP 服务器（服务器名引用或内联配置） |
| `hooks` | 否 | object (YAML) | 无 | 子代理专属的生命周期 hooks |
| `memory` | 否 | string | 无 | 持久内存范围：`user` / `project` / `local` |
| `background` | 否 | boolean | `false` | 设为 `true` 始终作为后台任务运行 |
| `isolation` | 否 | string | 无 | 设为 `worktree` 在临时 git worktree 中隔离运行 |

---

## 3. permissionMode 各模式效果

| 模式 | 行为 | 典型用途 |
|------|------|---------|
| `default` | 标准权限检查，敏感操作弹出确认 | 通用 |
| `acceptEdits` | 自动接受文件编辑（Edit/Write），Bash 仍需确认 | 实施类子代理 |
| `dontAsk` | 自动拒绝所有权限提示；但 `tools` 中显式列出的工具仍可用 | 只读探索 + 少量受控操作 |
| `bypassPermissions` | 跳过所有权限检查 | 仅限隔离环境（容器/VM） |
| `plan` | 只读探索模式，不可修改文件或执行命令 | 规划阶段的代码分析 |

**关键约束**：
- 若父级使用 `bypassPermissions`，子代理无法覆盖为更严格模式（父级权限优先）
- `bypassPermissions` 有安全风险，managed-settings 可通过 `disableBypassPermissionsMode: "disable"` 彻底禁用

**对 diwu-workflow 的意义**：
- 探索类子代理建议用 `plan` 模式（只读，与 `tools: Read, Grep, Glob` 配合）
- 实施类子代理建议用 `acceptEdits`（自动接受文件编辑，减少交互中断）

---

## 4. memory 持久化机制

### 支持范围

| 范围 | 存储路径 | 适用场景 | 是否提交 git |
|------|---------|---------|-------------|
| `user` | `~/.claude/agent-memory/<name>/` | 跨项目通用知识 | 否（用户本地） |
| `project` | `.claude/agent-memory/<name>/` | 项目特定知识，团队共享 | 是 |
| `local` | `.claude/agent-memory-local/<name>/` | 项目特定知识，个人使用 | 否（应 gitignore） |

### 机制细节

启用 `memory` 后，Claude Code 自动：
1. 在 system prompt 中注入读写内存目录的说明
2. 注入 `MEMORY.md` 的前 200 行内容
3. 自动启用 Read/Write/Edit 工具（即使 `tools` 未列出）

**结论：memory 支持 project 级别持久化**，路径为 `.claude/agent-memory/<name>/`，可提交到 git 与团队共享。这是三个范围中唯一适合团队协作的选项。

### 使用建议

- 推荐默认使用 `user` 范围，知识跨项目复用
- 在 system prompt 中明确要求子代理：
  - 工作前查阅记忆："Review your memory for patterns you've seen before."
  - 完成后更新记忆："Save what you learned to your memory."
- `MEMORY.md` 超过 200 行后只有前 200 行自动加载，需子代理自行维护简洁性

---

## 5. maxTurns 行为

- `maxTurns` 设定子代理的最大 agentic turns 数
- 到达上限后子代理**自动停止**，返回当前结果给主代理
- 不会给子代理施加"在限制内完成任务"的压力，只是简单截断
- CLI 模式下可通过 `claude -p --max-turns 3` 设定（用于自动化场景）
- 未设置时无限制（受 context window 容量和自动压缩约束）

**对 diwu-workflow 的意义**：
- 探索类子代理建议设 `maxTurns: 20`（避免无限探索浪费 token）
- 实施类子代理不建议设限（任务复杂度不可预期，截断可能导致半成品）

---

## 6. description 与主动委派（Proactive Delegation）

### 委派决策机制

Claude 根据以下因素决定是否委派给子代理：
1. 用户请求中的任务描述
2. 子代理的 `description` 字段
3. 当前对话上下文

### "Use proactively" 效果

在 description 中包含 "Use proactively" 或类似表述（如 "Use immediately after..."），**鼓励** Claude 在匹配任务出现时主动委派，而非等待用户显式要求。

```yaml
# 主动委派（Claude 看到代码变更后自动触发）
description: Expert code review specialist. Use immediately after writing or modifying code.

# 被动委派（仅在用户明确要求时触发）
description: Reviews code for quality and best practices.
```

### 验证结论

- description **确实影响**主代理的委派决策
- 含 "proactively" / "immediately" 等词时，Claude 会在合适时机自动委派
- 不含这些词时，仅在用户显式提及子代理名称或用途时触发
- description 模糊或多个子代理 description 重叠可能导致错误委派

### 显式调用

无论 description 如何，用户始终可以显式要求使用特定子代理：
```
Use the code-reviewer subagent to review the authentication module
```

---

## 7. 其他关键字段补充说明

### tools 与 disallowedTools

- `tools` 为 allowlist，省略则继承主对话所有工具（含 MCP 工具）
- `disallowedTools` 为 denylist，从继承列表中移除
- 两者可组合使用：`tools` 定义基线，`disallowedTools` 排除特定项
- `Agent(agent_type)` 语法可限制子代理可生成的子代理类型（仅 `claude --agent` 主线程模式有效，普通子代理不可嵌套生成子代理）

### model

| 值 | 行为 |
|----|------|
| `inherit` | 使用主对话相同模型（默认） |
| `haiku` | 低延迟低成本，适合只读探索 |
| `sonnet` | 平衡能力与速度 |
| `opus` | 最强推理能力，适合架构设计和复杂任务 |

环境变量 `CLAUDE_CODE_SUBAGENT_MODEL` 可全局覆盖子代理模型。

### skills

- 完整内容注入到子代理 context（不是按需加载）
- 子代理**不继承**父对话的 skills，必须显式列出
- 与 skill 的 `context: fork` 是反向操作：前者由子代理控制 system prompt 并加载 skill 内容，后者由 skill 控制并指定运行在哪个子代理中

### background

- `true` 时子代理与主对话并发运行
- 启动前 Claude Code 预先获取所有需要的工具权限
- 后台子代理**不支持 MCP 工具**，也无法向用户提问
- 权限不足时后台子代理会失败，可 resume 到前台重试

### isolation

- 设为 `worktree` 时在临时 git worktree 中运行，获得仓库的隔离副本
- 子代理无变更时 worktree 自动清理
- 适合并行修改同一代码库的不同区域

### hooks（子代理专属）

- 在 frontmatter 中定义的 hooks 仅在该子代理活跃期间生效
- 支持所有 hook 事件（PreToolUse, PostToolUse, Stop 等）
- frontmatter 中的 `Stop` hook 会自动转为 `SubagentStop` 事件
- 项目 settings.json 中可通过 `SubagentStart` / `SubagentStop` 监听子代理生命周期

---

## 8. 作用域与优先级

| 位置 | 作用域 | 优先级 | 创建方式 |
|------|--------|--------|---------|
| `--agents` CLI 标志 | 当前会话 | 1（最高） | 启动时传 JSON |
| `.claude/agents/` | 当前项目 | 2 | `/agents` 命令或手动创建文件 |
| `~/.claude/agents/` | 所有项目 | 3 | `/agents` 命令或手动创建文件 |
| 插件 `agents/` 目录 | 启用插件处 | 4（最低） | 插件安装 |

同名时高优先级覆盖低优先级。

---

## 9. 关键限制

| 限制 | 说明 |
|------|------|
| 不可嵌套 | 子代理不可生成其他子代理（`Agent(type)` 仅 `claude --agent` 主线程有效） |
| 不继承历史 | 子代理不继承父对话历史，仅接收 system prompt + 环境信息 |
| 不继承 skills | 必须在 `skills` 字段显式列出 |
| 后台不支持 MCP | 后台子代理无法使用 MCP 工具 |
| 后台不可交互 | 后台子代理无法向用户提问（AskUserQuestion 会失败） |
| 手动添加需重启 | 手动创建的文件需重启会话或 `/agents` 命令加载 |

---

## 10. 对 diwu-workflow 的使用建议（已采纳）

### 当前方案：通过插件默认路径 `agents/` 统一分发全部 Agent（v0.10.2 起）

diwu-workflow 将 10 个 Agent（3 核心 + 7 领域）统一放在插件根目录的 `agents/` 下，使用 **默认路径自动发现**（plugin.json 不声明 agents 字段）。优先级为 5（最低），会被用户或项目的同名子代理覆盖。

**关键变更**：
- v0.10.2 前：核心 agent 通过 `/dinit` 分发到 `.claude/agents/`（优先级 3），领域 agent 在根目录 `agents/` 但未被加载
- v0.10.2+：全部 10 个 agent 统一在插件 `agents/`，通过默认路径自动发现（不声明 agents 字段）
- `/dinit` 不再负责 agents 分发，彻底移除相关逻辑

### 推荐子代理设计（v0.10.2 已实施）

> **注意**：以下为 v0.10.2 前的设计。v0.10.2 起，全部 Agent 统一在插件 `agents/` 目录，通过默认路径自动发现。permissionMode 在插件 agent 中不被支持（见上方第 10 节说明）。

| 子代理 | model | tools | memory | 用途 |
|--------|-------|-------|--------|------|
| `explorer` | `haiku` | `Read, Grep, Glob, LSP, WebSearch, WebFetch` | 无 | 只读探索/搜索 |
| `implementer` | `inherit` | 继承所有 + LSP | 无 | 实施类，继承主模型 |
| `verifier` | `haiku` | `Read, Grep, Glob, Bash` | 无 | 独立验收验证 |
| `ui-designer` | `sonnet` | `Read, Grep, Glob, Bash` | 无 | UI/UX 设计专家 |
| `frontend-architect` | `sonnet` | `Read, Grep, Glob, Bash` | 无 | 前端架构专家 |
| `backend-architect` | `sonnet` | `Read, Grep, Glob, Bash` | 无 | 后端架构专家 |
| `api-tester` | `sonnet` | `Read, Grep, Glob, Bash` | 无 | API 测试专家 |
| `devops-architect` | `sonnet` | `Read, Grep, Glob, Bash` | 无 | DevOps 架构专家 |
| `performance-optimizer` | `sonnet` | `Read, Grep, Glob, Bash` | 无 | 性能优化专家 |
| `legal-compliance` | `sonnet` | `Read, Grep, Glob, Bash` | 无 | 法律合规专家 |

### 与现有规则的兼容性

- `workflow.md` 中的子代理策略（Coordinator Pattern、启动仪式、并行/串行条件）可通过 system prompt 注入
- 但需注意：子代理**不继承** CLAUDE.md 和 rules 中的所有规则。如需子代理遵守特定规则，必须在其 system prompt 或 `skills` 中显式包含
- `settings.json` 中的 `subagent_concurrency`、`subagent_explore_model`、`subagent_implement_model` 参数目前由规则文本指导主代理行为，与 agents/*.md 的 `model` 字段是不同机制

### 注意事项

1. **skills 注入成本**：每个 skill 完整注入到子代理 context，过多/过大的 skills 会消耗 context window
2. **memory 持久化决策**：如果要团队共享子代理学到的知识，用 `project` 范围；但这会增加 git 仓库大小
3. **proactive delegation 风险**：description 中写 "Use proactively" 可能导致不期望的自动委派，建议对实施类子代理不使用主动委派
4. **maxTurns 是截断不是收敛**：子代理不会因为 maxTurns 即将到达而加速完成，只是简单停止

### 下一步

1. 决定是否将子代理纳入 diwu-workflow 插件（在 `agents/` 目录下提供默认子代理）
2. 如纳入，需要设计 system prompt，将 Coordinator Pattern 和启动仪式规则写入 prompt
3. 评估 `memory` 机制是否适合替代当前 `recording.md` 的部分职责
