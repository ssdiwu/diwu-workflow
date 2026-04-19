---
name: dinit
description: 初始化项目的 Claude Code Agent 工作流结构，创建 CLAUDE.md、.diwu/dtask.json、.diwu/recording/、init.sh、.diwu/checks/smoke.sh，同步 rules 与 agents
argument-hint: [项目描述（可选）]
allowed-tools: Read, Write, Edit, Bash, Glob
effort: medium
---

# /dinit — 项目初始化

## 核心原则

- **Source of Truth 是文件系统**：`rules-manifest.json` 决定 rules 列表，`agents/` 目录决定 agent 列表。不硬编码任何文件名。
- **刷新优先于重建**：已有项目的刷新是增量操作，不破坏用户自定义内容。
- **幂等性**：重复执行 `/dinit` 不应产生副作用（模板资产覆盖，用户跳过的文件不覆盖）。

## Step 0：模式检测

检查 `.claude/CLAUDE.md` 是否已存在：
- **已存在** → **刷新模式**：执行以下 Refresh Protocol
- **不存在** → **初始化模式**：执行 Step 1 → 7 完整流程

---

### Refresh Protocol（刷新模式）

当 `.claude/CLAUDE.md` 已存在时，按以下步骤增量更新：

#### 1. 检测并升级为 v2 格式

搜索 CLAUDE.md 中是否存在 `@rules/` 引用或旧版「工作流规则」章节（含 `@rules/` 列表）。如果存在：

**执行 v2 升级**：将整个 CLAUDE.md 替换为 v2 精简格式，包含：
- 核心原则段（5 条元规则）
- 上位心智层精简版（三唯一框架 + 不确定性门控 + P-J-A 骨架 + 证据摘要）
- Skill/文件索引表（6 个 skill + 4 个参考文件）
- 行为铁律段（recording 更新 + 时间戳 + 禁止推送目录）
- 项目上下文和项目结构（保留用户自定义内容）

> **v2 格式特征**：无任何 `@rules/` 引用、总行数 ≤ 120 行、包含 Skill 索引表。

如已是 v2 格式（无 `@rules/` 且含 Skill 索引），跳过此步。

#### 2. 检测并插入/更新 Skill 索引表

搜索是否存在 `## Skill 索引` 标题。如不存在或格式不完整，插入/更新为标准 v2 索引表。

#### 3. 更新「项目结构」章节

用 Step 1.5 的扫描结果替换 `<!-- SCAN_RESULT_PLACEHOLDER -->` 占位符或更新现有内容。

#### 4. 迁移 recording.md 到 recording/ 目录

检查 `.claude/recording.md` 是否存在。如果存在：
- 读取内容，按 `## Session YYYY-MM-DD HH:MM:SS` 分隔符识别所有 session
- 创建 `.diwu/recording/` 目录（如不存在）
- 将每个 session 写入独立文件 `recording/session-YYYY-MM-DD-HHMMSS.md`
- 迁移完成后将原 `recording.md` 重命名为 `recording.md.backup`

#### 5. 同步 Rules

详见下方 Step 3a（初始化模式和刷新模式共用同一套同步逻辑）。

#### 6. 同步 Agents

详见下方 Step 3b（初始化模式和刷新模式共用同一套同步逻辑）。

#### 7. 同步 Skills

详见下方 Step 3c（初始化模式和刷新模式共用同一套同步逻辑）。

**刷新模式不做的事**：
- 不重新收集项目信息（除非用户主动要求更新）
- 不覆盖用户在 CLAUDE.md 中的自定义章节（只增补标准章节）
- 不修改 `.diwu/dtask.json` 中的任务数据
- 不重新生成 `init.sh` 或 `smoke.sh`
- 不要求用户手动清理旧版本规则文件；刷新时应自动识别并覆盖标准资产

---

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

从 `.diwu/dsettings.json` 读取 `subagent_concurrency` 参数（默认 3），使用子代理并行扫描代码库：

**扫描任务**（并行执行）：
1. **目录结构扫描**：识别主要目录层级、文件分布、模块组织方式
2. **技术栈检测**：识别 package.json / requirements.txt / go.mod 等配置文件，提取依赖和工具链信息
3. **关键文件识别**：定位 README、配置文件、入口文件、测试目录

**扫描结果整合**：
- 将扫描结果整合为结构化的项目结构描述
- 补充 Step 1 收集的信息（如用户未提供关键目录，用扫描结果填充）
- 用于填充 `.claude/CLAUDE.md` 的「项目结构」章节

## Step 2：旧版迁移检测（复制资产之前执行）

检测项目是否使用旧版 diwu-workflow（v0.x）或旧运行时目录结构：

1. **检测旧版标志**：
   - 检查 `.claude/rules/states.md` 是否存在
   - 检查 `.claude/rules/task.md` 是否**不存在**
   - 两个条件同时满足 → 检测到旧版

2. **检测旧运行时目录迁移需求**：
   - 检查 `.diwu/dtask.json`、`.claude/recording/`、`.claude/decisions.md`、`.claude/dsettings.json`、`.claude/project-pitfalls.md`、`.claude/archive/`、`.claude/continue-here.md`、`.claude/checks/` 是否存在任一旧运行时文件
   - 检查 `.diwu/` 是否**不存在**
   - 两个条件同时满足 → 输出迁移指引或执行自动迁移：将上述旧运行时文件迁移到 `.diwu/`，保留 `.claude/CLAUDE.md`、`rules/`、`agents/`、`skills/` 等 Claude 原生机制目录不动

3. **如检测到旧版，执行迁移**：
   a. **更新 CLAUDE.md 引用**：搜索所有 `@rules/states.md` → 替换为 `@rules/task.md`
   b. **合并 dsettings 新字段**：读取 `dsettings.json.template`，合并到用户项目的 `.diwu/dsettings.json`（不覆盖已有值，只追加缺失字段）
   c. **备份旧 states.md**：重命名为 `states.md.backup`
   d. 输出迁移报告（引用更新数、合并字段数、备份状态）

4. **如未检测到旧版和旧运行时结构**：跳过此步骤，直接进入 Step 3

## Step 3：同步可分发资产

按以下类别，从模板目录同步到项目目录（先比较内容，再按需写入/覆盖；rules 仍保留孤立文件清理）：

| 资产类型 | 源目录 | 目标目录 | 清单来源 | 冲突策略 |
|---------|--------|---------|---------|---------|
| rules | `${PLUGIN}/assets/dinit/assets/rules/` | `.claude/rules/` | `rules-manifest.json` 的 `rules` 数组 | 按需写入/覆盖 |
| agents | `${PLUGIN}/assets/dinit/assets/agents/` | `.claude/agents/` | 动态扫描 `*.md` | 按需写入/覆盖 |
| skills | `${PLUGIN}/skills/` | `.agents/skills/` | 动态扫描 `*/SKILL.md` | 按需写入/覆盖 |

其中 `${PLUGIN}` = `${CLAUDE_PLUGIN_ROOT}` 或插件根目录绝对路径。

### 3a. 同步 Rules

1. 清理孤立文件：删除 `.claude/rules/` 下不在 `rules-manifest.json` `rules` 数组中的文件（如旧的 `states.md`）
2. 读取 `${PLUGIN}/assets/dinit/assets/rules-manifest.json`
3. 按 `rules` 数组逐一比较源文件与目标文件内容：
   - 目标不存在 → 写入，标记 `NEW`
   - 目标存在且内容一致 → 跳过，标记 `SAME`
   - 目标存在且内容不同 → 用源文件覆盖，标记 `UPDATED`
4. 输出：已同步的规则文件数量、名称和状态（`NEW` / `SAME` / `UPDATED`）

**为什么 rules 用 manifest 而非动态扫描？** — Rules 有严格排序语义和版本字段，需要显式清单保证一致性。

### 3b. 同步 Agents

1. 创建 `.claude/agents/` 目录（如不存在）
2. 动态扫描 `${PLUGIN}/assets/dinit/assets/agents/` 下所有 `.md` 文件
3. 逐一比较源文件与目标文件内容：
   - 目标不存在 → 写入，标记 `NEW`
   - 目标存在且内容一致 → 跳过，标记 `SAME`
   - 目标存在且内容不同 → 用源文件覆盖，标记 `UPDATED`
4. 输出：已复制的 agent 文件名、数量和状态

**为什么 agents 用动态扫描？** — Agents 是扁平列表无排序依赖，目录即清单。新增 agent 只需放一个 `.md` 文件，零配置成本。

### 3c. 同步 Skills

将 Skills 分发到 `.agents/skills/`，供非 Claude Code 的 AI IDE（Cursor/Windsurf/Copilot 等）通过 `.agents/` 约定自动发现和消费。

1. 创建 `.agents/skills/` **普通目录**（如不存在）
2. 动态扫描 `${PLUGIN}/skills/` 下所有含 `SKILL.md` 的子目录
3. 为每个 skill 创建**独立目录级 symlink**：`ln -s ../../skills/{name} .agents/skills/{name}`
   - 目标已存在且指向正确 → 跳过（幂等）
   - 不是 symlink 或目标错误 → 删除后重新创建
4. 冲突策略：用户在 `.agents/skills/` 中放置的自定义 skill 目录（非 symlink）不会被覆盖；仅管理插件拥有的 `{name}` 目录级 symlink
5. 输出：已同步的 skill 目录数、新增/跳过/更新的数量

**为什么用目录级 per-skill symlink？**
- 用户可在 `.agents/skills/` 中自由添加自定义 skill 目录（不污染插件 `skills/` 目录）
- 插件 skill 通过 symlink 只读引用，skill 目录内所有文件（SKILL.md + 未来扩展）均自动可见
- 新增插件 skill 需重新执行 `/dinit` 同步（显式操作，避免意外注入）

## Step 4：创建项目配置文件

### 4.1 .claude/CLAUDE.md
读取 `${PLUGIN}/assets/dinit/assets/claude-md-portable.template`，执行以下填充后写入 `.claude/CLAUDE.md`：
- 填入项目信息占位符（名称/描述/技术栈/命令/目录）
- 替换 `<!-- SCAN_RESULT_PLACEHOLDER -->` 为 Step 1.5 的扫描结果
- 替换 `<!-- RULES_PLACEHOLDER -->` 到 `<!-- END_RULES_PLACEHOLDER -->` 之间的内容为根据 `rules-manifest.json` 动态生成的 `@rules/` 列表

**不得**创建 `.claude/assets/rules/` 或其他子目录。

### 4.2 AGENTS.md（项目根目录）
读取 `${PLUGIN}/assets/dinit/assets/agents-md.template` 写入项目根目录。

### 4.3 .diwu/dtask.json
读取 `${PLUGIN}/assets/dinit/assets/task.json.template`。若用户已有需求，填充初始任务（status: InDraft）；否则保持 tasks 数组为空。
字段语义：`title` = 一句话任务标题，`description` = 背景与关键约束。

### 4.4 init.sh（项目根目录）
读取 `${PLUGIN}/assets/dinit/assets/init.sh.template`，根据技术栈定制安装命令和 dev server 命令，执行 `chmod +x init.sh`。

### 4.5 .diwu/recording/
创建 `.diwu/recording/` 目录（用于存储 session 记录文件）。

### 4.6 .diwu/archive/
创建 `.diwu/archive/` 目录，用于 task 与 recording 归档产物存放。

### 4.7 .diwu/continue-here.md（可选）
创建 `.diwu/continue-here.md` 作为会话续接文件。默认不预填内容；仅在需要跨 session 交接时由 Agent 写入。

### 4.7 .diwu/dsettings.json
读取 `${PLUGIN}/assets/dinit/assets/dsettings.json.template` 写入。若已存在则跳过（不覆盖用户已有配置）。

### 4.8 .diwu/project-pitfalls.md
读取 `${PLUGIN}/assets/dinit/assets/project-pitfalls.md.template` 写入。若已存在则跳过（不覆盖用户已有内容）。由 Stop hook 归档聚合逻辑持续填充。

### 4.9 .diwu/decisions.md（可选）
询问用户是否需要创建决策记录文件（有明确设计方向或技术选型的项目推荐）。如需要，读取模板写入。

### 4.10 .diwu/checks/smoke.sh
读取 `${PLUGIN}/assets/dinit/assets/smoke.sh.template`，根据技术栈定制，执行 `chmod +x .diwu/checks/smoke.sh`。

## Step 5：可选 — 架构约束

询问用户是否需要 `.claude/rules/constraints.md`（架构复杂的项目推荐）。
如需要，读取 `${PLUGIN}/assets/dinit/references/constraint-template.md`，引导用户用五维框架定义约束。

## Step 6：Git 初始化（如需要）

若当前目录不是 git 仓库，初始化 git 仓库并创建初始提交。

## Step 7：验证清单

确认以下文件均已创建（数量来自运行时扫描，非硬编码）：

**基础文件（v2 格式验证）**：
- [ ] `.claude/CLAUDE.md` 已填充项目信息，包含核心原则 + Skill 索引表
- [ ] `.claude/CLAUDE.md` **不包含任何 `@rules/` 引用**（grep 零匹配）
- [ ] `.claude/CLAUDE.md` 总行数 ≤ 120 行
- [ ] `.claude/CLAUDE.md` 包含 `## Skill 索引` 或等效 skill 列表
- [ ] `.claude/CLAUDE.md` 的「项目结构」章节包含扫描结果（非默认占位符）
- [ ] 项目根目录有 `AGENTS.md`
- [ ] `.diwu/dtask.json` 是有效 JSON
- [ ] `init.sh` 可执行
- [ ] `.diwu/recording/` 目录存在
- [ ] `.claude/recording.md` 不存在（已迁移为 recording/ 目录）或已重命名为 `.recording.md.backup`

**Rules（N = rules-manifest.json.rules.length）**：
- [ ] `.claude/rules/` 下有 N 个 rules 文件
- [ ] `.claude/rules/` 下不存在 `states.md`（已替换为新版规则集）
- [ ] `.claude/rules/states.md.backup` 仅在检测到旧版时存在
- [ ] 刷新时能识别并覆盖内容变化的标准 rules 文件（例如 `templates.md`）

**Agents（M = agents/ 目录下 *.md 数量）**：
- [ ] `.claude/agents/` 目录存在且包含 M 个 agent 文件
- [ ] 刷新时能识别并覆盖内容变化的标准 agent 文件

**Skills（K = skills/ 下含 SKILL.md 的子目录数）**：
- [ ] `.agents/skills/` 目录存在且包含 K 个目录级 symlink（名称 `{name}`）
- [ ] 每个 symlink 目标为 `../../skills/{name}` 且目标内含 `SKILL.md`
- [ ] 刷新时能识别并更新指向错误的 symlink

**可选文件**：
- [ ] `.diwu/dsettings.json` 存在且 JSON 合法
- [ ] `.diwu/project-pitfalls.md` 存在
- [ ] `.diwu/checks/smoke.sh` 可执行
- [ ] `.diwu/archive/` 目录存在（归档产物存放位置）
- [ ] `.diwu/archive/` 目录存在
- [ ] （可选）`.diwu/continue-here.md`
- [ ] （可选）`.diwu/decisions.md`
