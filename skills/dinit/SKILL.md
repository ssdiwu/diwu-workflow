---
name: dinit
description: 项目初始化——创建 Claude Code Agent 工作流结构、同步规则与 Agent、支持刷新模式。触发场景：(1) 新项目首次初始化，(2) 已有项目更新工作流规则/Agent，(3) 从 v0.x 迁移到 v1.0。
---

# dinit

项目初始化与工作流结构分发知识库。定义模板资产如何从插件目录同步到用户项目的 `.claude/`。

---

## 阅读顺序

**执行前必读**：
1. `asset-sync.md` — 理解资产分发机制（rules/agents 如何发现、复制、冲突处理）
2. `refresh-protocol.md` — 如处于刷新模式（CLAUDE.md 已存在），必须先读此文件

**遇到问题时**：
- 刷新后 CLAUDE.md 格式异常 → `refresh-protocol.md` §章节插入规则
- agents 未更新 → `asset-sync.md` §agents 同步
- 旧版迁移失败 → `commands/dinit.md` Step 2
- 新增模板类型未生效 → `asset-sync.md` §扩展指南

## 核心原则

- **Source of Truth 是文件系统**：`rules-manifest.json` 决定 rules 列表，`agents/` 目录决定 agent 列表。不硬编码任何文件名。
- **刷新优先于重建**：已有项目的刷新是增量操作，不破坏用户自定义内容。
- **幂等性**：重复执行 `/dinit` 不应产生副作用（模板资产覆盖，用户跳过的文件不覆盖）。

## 触发时判断

| 条件 | 模式 | 执行路径 |
|------|------|---------|
| `.claude/CLAUDE.md` 不存在 | 初始化模式 | Step 0 → Step 1→7 完整流程 |
| `.claude/CLAUDE.md` 存在 | 刷新模式 | 执行 `refresh-protocol.md` |
| `.claude/rules/states.md` 存在 且 `task.md` 不存在 | 旧版迁移 + 刷新 | 先迁移再刷新 |

## 资产总览

`/dinit` 分发的资产分为两类：

### 可分发资产（每次刷新覆盖）

| 类型 | 源目录 | 目标目录 | 清单来源 |
|------|--------|---------|---------|
| rules | `assets/dinit/assets/rules/` | `.claude/rules/` | `rules-manifest.json` 的 `rules` 数组 |
| agents | `assets/dinit/assets/agents/` | `.claude/agents/` | 动态扫描 `*.md` |

### 项目配置文件（仅初始化创建，已存在则跳过）

| 文件 | 目标路径 | 跳过条件 |
|------|---------|---------|
| CLAUDE.md | `.claude/CLAUDE.md` | 已存在时进入刷新模式 |
| task.json | `.claude/task.json` | 始终覆盖（追加模式） |
| dsettings.json | `.claude/dsettings.json` | 已存在则跳过 |
| project-pitfalls.md | `.claude/project-pitfalls.md` | 已存在则跳过 |
| decisions.md | `.claude/decisions.md` | 可选，询问用户 |
