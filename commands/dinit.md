---
name: dinit
description: 初始化项目的 Claude Code Agent 工作流结构，创建 CLAUDE.md、task.json、recording/ 目录、init.sh、smoke.sh，同步 rules 与 agents
argument-hint: [项目描述（可选）]
allowed-tools: Read, Write, Edit, Bash, Glob
effort: medium
---

# /dinit — 项目初始化

> 详细操作协议见 `skills/dinit/SKILL.md`（Refresh Protocol / Asset Sync Protocol）

## Step 0：模式检测

检查 `.claude/CLAUDE.md` 是否已存在：
- **已存在** → **刷新模式**：执行 `skills/dinit/refresh-protocol.md` 定义的 Refresh Protocol（章节补充 + recording 迁移 + 资产同步）
- **不存在** → **初始化模式**：执行 Step 1 → 7 完整流程

## Step 1：收集项目信息

询问用户（上下文已有的跳过）：
- **项目名称**和**1-2 句描述**
- **技术栈**：语言、框架、数据库
- **常用命令**：dev、build、lint、test
- **关键目录**：项目结构概览

**示例（填写完整的项目信息）**：
- 项目名称：diwu-workflow
- 描述：Claude Code 插件仓库，提供 diwu 编码工作流套件
- 技术栈：Node.js，无框架，无数据库
- 常用命令：`npm run lint`（lint），`npm test`（test），无 dev server
- 关键目录：`commands/`（用户命令），`assets/`（模板文件），`skills/`（技能文件）

收集到的信息要达到这个粒度才能生成有效的 CLAUDE.md 和 smoke.sh。

## Step 1.5：代码库扫描

从 `.claude/dsettings.json` 读取 `subagent_concurrency` 参数（默认 3），使用子代理并行扫描代码库：

**扫描任务**（并行执行）：
1. **目录结构扫描**：识别主要目录层级、文件分布、模块组织方式
2. **技术栈检测**：识别 package.json / requirements.txt / go.mod 等配置文件，提取依赖和工具链信息
3. **关键文件识别**：定位 README、配置文件、入口文件、测试目录

**扫描结果整合**：
- 将扫描结果整合为结构化的项目结构描述
- 补充 Step 1 收集的信息（如用户未提供关键目录，用扫描结果填充）
- 用于填充 `.claude/CLAUDE.md` 的「项目结构」章节

## Step 2：旧版迁移检测（复制资产之前执行）

检测项目是否使用旧版 diwu-workflow（v0.x）：

1. **检测旧版标志**：
   - 检查 `.claude/rules/states.md` 是否存在
   - 检查 `.claude/rules/task.md` 是否**不存在**
   - 两个条件同时满足 → 检测到旧版

2. **如检测到旧版，执行迁移**：
   a. **更新 CLAUDE.md 引用**：搜索所有 `@rules/states.md` → 替换为 `@rules/task.md`
   b. **合并 dsettings 新字段**：读取 `dsettings.json.template`，合并到用户项目的 `.claude/dsettings.json`（不覆盖已有值，只追加缺失字段）
   c. **备份旧 states.md**：重命名为 `states.md.backup`
   d. 输出迁移报告（引用更新数、合并字段数、备份状态）

3. **如未检测到旧版**：跳过此步骤，直接进入 Step 3

## Step 3：同步可分发资产

> 详细规则见 `skills/dinit/asset-sync.md`

按以下类别，从模板目录复制到项目目录（**覆盖旧版本**，确保用户拿到最新定义）：

| 资产类型 | 源目录 | 目标目录 | 清单来源 |
|---------|--------|---------|---------|
| rules | `${PLUGIN}/assets/dinit/assets/rules/` | `.claude/rules/` | `rules-manifest.json` 的 `rules` 数组 |
| agents | `${PLUGIN}/assets/dinit/assets/agents/` | `.claude/agents/` | 动态扫描 `*.md` |

**操作步骤**：

### 3a. 同步 Rules
1. 清理孤立文件：删除 `.claude/rules/` 下不在 `rules-manifest.json` `rules` 数组中的文件
2. 读取 `${PLUGIN}/assets/dinit/assets/rules-manifest.json`
3. 按 `rules` 数组逐一复制到 `.claude/rules/`
4. 输出：已同步的规则文件数量和名称

### 3b. 同步 Agents
1. 创建 `.claude/agents/` 目录（如不存在）
2. 动态扫描 `${PLUGIN}/assets/dinit/assets/agents/` 下所有 `.md` 文件
3. 逐一复制到 `.claude/agents/`（覆盖旧版本）
4. 输出：已复制的 agent 文件名及数量

## Step 4：创建项目配置文件

### 4.1 .claude/CLAUDE.md
读取 `${PLUGIN}/assets/dinit/assets/claude-md-portable.template`，执行以下填充后写入 `.claude/CLAUDE.md`：
- 填入项目信息占位符（名称/描述/技术栈/命令/目录）
- 替换 `<!-- SCAN_RESULT_PLACEHOLDER -->` 为 Step 1.5 的扫描结果
- 替换 `<!-- RULES_PLACEHOLDER -->` 到 `<!-- END_RULES_PLACEHOLDER -->` 之间的内容为根据 `rules-manifest.json` 动态生成的 `@rules/` 列表（详见 `asset-sync.md` §CLAUDE.md 规则列表动态生成）

**不得**创建 `.claude/assets/rules/` 或其他子目录。

### 4.2 AGENTS.md（项目根目录）
读取 `${PLUGIN}/assets/dinit/assets/agents-md.template` 写入项目根目录。

### 4.3 .claude/task.json
读取 `${PLUGIN}/assets/dinit/assets/task.json.template`。若用户已有需求，填充初始任务（status: InDraft）；否则保持 tasks 数组为空。
字段语义：`title` = 一句话任务标题，`description` = 背景与关键约束。

### 4.4 init.sh（项目根目录）
读取 `${PLUGIN}/assets/dinit/assets/init.sh.template`，根据技术栈定制安装命令和 dev server 命令，执行 `chmod +x init.sh`。

### 4.5 .claude/recording/
创建 `.claude/recording/` 目录（用于存储 session 记录文件）。

### 4.6 .claude/lessons.md
读取 `${PLUGIN}/assets/dinit/assets/lessons.md.template` 写入。

### 4.7 .claude/dsettings.json
读取 `${PLUGIN}/assets/dinit/assets/dsettings.json.template` 写入。若已存在则跳过（不覆盖用户已有配置）。

### 4.8 .claude/project-pitfalls.md
读取 `${PLUGIN}/assets/dinit/assets/project-pitfalls.md.template` 写入。若已存在则跳过（不覆盖用户已有内容）。由 Stop hook 归档聚合逻辑持续填充。

### 4.9 .claude/decisions.md（可选）
询问用户是否需要创建决策记录文件（有明确设计方向或技术选型的项目推荐）。如需要，读取模板写入。

### 4.10 .claude/checks/smoke.sh
读取 `${PLUGIN}/assets/dinit/assets/smoke.sh.template`，根据技术栈定制，执行 `chmod +x .claude/checks/smoke.sh`。

## Step 5：可选 — 架构约束

询问用户是否需要 `.claude/rules/constraints.md`（架构复杂的项目推荐）。
如需要，读取 `${PLUGIN}/assets/dinit/references/constraint-template.md`，引导用户用五维框架定义约束。

## Step 6：Git 初始化（如需要）

若当前目录不是 git 仓库，初始化 git 仓库并创建初始提交。

## Step 7：验证清单

确认以下文件均已创建（数量来自运行时扫描，非硬编码）：

**基础文件**：
- [ ] `.claude/CLAUDE.md` 已填充项目信息，包含「工作流规则」章节
- [ ] `.claude/CLAUDE.md` 的「项目结构」章节包含扫描结果（非默认占位符）
- [ ] 项目根目录有 `AGENTS.md`
- [ ] `.claude/task.json` 是有效 JSON
- [ ] `init.sh` 可执行
- [ ] `.claude/recording/` 目录存在
- [ ] `.claude/recording.md` 不存在（已迁移为 recording/ 目录）或已重命名为 `.recording.md.backup`

**Rules（N = rules-manifest.json.rules.length）**：
- [ ] `.claude/rules/` 下有 N 个 rules 文件
- [ ] `.claude/rules/` 下不存在 `states.md`（已替换为新版规则集）
- [ ] `.claude/rules/states.md.backup` 仅在检测到旧版时存在

**Agents（M = agents/ 目录下 *.md 数量）**：
- [ ] `.claude/agents/` 目录存在且包含 M 个 agent 文件

**可选文件**：
- [ ] `.claude/lessons.md` 存在
- [ ] `.claude/dsettings.json` 存在且 JSON 合法
- [ ] `.claude/project-pitfalls.md` 存在
- [ ] `.claude/checks/smoke.sh` 可执行
- [ ] （可选）`.claude/decisions.md`
