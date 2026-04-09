---
description: 初始化项目的 Claude Code Agent 工作流结构，创建 CLAUDE.md、task.json、recording/ 目录、init.sh、smoke.sh
argument-hint: [项目描述（可选）]
allowed-tools: Read, Write, Edit, Bash, Glob
effort: medium
---

# /dinit — 项目初始化

## Step 0：刷新检测

检查 `.claude/CLAUDE.md` 是否已存在：
- **已存在** → 刷新模式：跳过 Step 4-6 的骨架创建，只执行 Step 1（收集信息）和 Step 1.5（代码库扫描），然后更新 `.claude/CLAUDE.md` 并确保项目符合最新规范
- **不存在** → 初始化模式：执行完整流程（Step 1 → Step 1.5 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6 → Step 7）

**刷新模式的章节补充逻辑**：

1. **检测「工作流规则」章节**：
   - 搜索 CLAUDE.md 中是否存在 `## 工作流规则` 标题
   - 如果不存在，在 `## 核心原则` 之前插入以下内容：
   ```markdown
   ## 工作流规则

   详细规则见 @rules/ 目录：
   - @rules/README.md - 规则速查索引
   - @rules/mindset.md - Agent 心智模型与行为准则
   - @rules/judgments.md - 判断锚点集中管理
   - @rules/workflow.md - Session 启动、任务规划、实施、验证
   - @rules/verification.md - 验证要求与运行态验证
   - @rules/correction.md - 执行偏差自动修正
   - @rules/pitfalls.md - 高频误判表（Layer 1 泛化模式）
   - @rules/session.md - Session 记录格式与上下文管理
   - @rules/task.md - 任务状态机与 task.json 结构
   - @rules/exceptions.md - 异常处理与 BLOCKED 判定
   - @rules/templates.md - 格式模板与可调参数
   - @rules/constraints.md - 架构约束（五维约束设计）

   ```

2. **检测「规则引用说明」章节**：
   - 搜索 CLAUDE.md 中是否存在 `## 规则引用说明` 标题
   - 如果不存在，在文件末尾追加以下内容：
   ```markdown

   ## 规则引用说明

   本项目使用 @rules/ 引用自动加载工作流规则。规则文件位于 `.claude/rules/` 目录，由 UserPromptSubmit hook 在每次对话开始时注入。
   ```

3. **更新「项目结构」章节**：
   - 用 Step 1.5 的扫描结果替换 `<!-- SCAN_RESULT_PLACEHOLDER -->` 占位符或更新现有内容

4. **迁移 recording.md 到 recording/ 目录**：
   - 检查 `.claude/recording.md` 是否存在
   - 如果存在，执行迁移：
     - 读取 recording.md 内容，按 `## Session YYYY-MM-DD HH:MM:SS` 分隔符识别所有 session
     - 创建 `.claude/recording/` 目录
     - 将每个 session 写入独立文件 `recording/session-YYYY-MM-DD-HHMMSS.md`（时间戳从 session 标题提取并转换为文件名格式）
     - 迁移完成后将原 recording.md 重命名为 `recording.md.backup`

5. **同步规则文件**：
   - 清理旧文件：删除 `.claude/rules/` 下的旧版规则文件（如存在）
   - 读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/rules-manifest.json`，按 `rules` 列表复制文件到 `.claude/rules/`，覆盖旧版本
   - 确保项目使用最新的规则文件

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

## Step 2：旧版迁移检测（复制 rules 之前执行）

检测项目是否使用旧版 diwu-workflow（v0.x）：

1. **检测旧版标志**：
   - 检查 `.claude/rules/states.md` 是否存在
   - 检查 `.claude/rules/task.md` 是否**不存在**
   - 两个条件同时满足 → 检测到旧版

2. **如检测到旧版，执行迁移**：
   a. **更新 CLAUDE.md 引用**：搜索 CLAUDE.md 中所有 `@rules/states.md` 引用，替换为 `@rules/task.md`
   b. **合并 dsettings 新字段**：读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/settings.json.template`（或 `dsettings.json.template`，以实际存在的文件名为准），将其中的新字段合并到用户项目的 `.claude/settings.json`（或 `.claude/dsettings.json`）。合并规则：不覆盖已有值，只追加缺失字段（如 `drift_detection`、`pitfalls`、`commit_enhanced`、`checkpoint_min_steps`、`checkpoint_min_lines`）
   c. **复制新 rules 文件**：读取 `rules-manifest.json`，将 13 个新规则文件复制到 `.claude/rules/`（覆盖旧版）
   d. **备份旧 states.md**：将 `.claude/rules/states.md` 重命名为 `.claude/rules/states.md.backup`
   e. **输出迁移报告**：
      ```
      === 旧版迁移报告 (v0.x → v1.0) ===
      - CLAUDE.md 引用更新: N 处 states.md → task.md
      - settings 合并: 追加 X 个新字段
      - rules 文件: 已更新至 12 个（v1.0 规则集）
      - 旧 states.md: 已备份为 states.md.backup
      ```

3. **如未检测到旧版**：跳过此步骤，直接进入 Step 3

## Step 3：复制规则文件

读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/rules-manifest.json`，按 `rules` 列表将规则文件复制到 `.claude/rules/`（覆盖旧版本）。

## Step 4：创建项目文件

### .claude/CLAUDE.md
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/claude-md-portable.template`，填入项目信息，写入 `.claude/CLAUDE.md`（保留 `@rules/` 引用，不展开）。**不得**创建 `.claude/assets/rules/` 或其他子目录。

### AGENTS.md（项目根目录）
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/agents-md.template` 写入项目根目录。

### .claude/task.json
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/task.json.template`。若用户已有需求，填充初始任务（status: InDraft）；否则保持 tasks 数组为空。
若填充初始任务，字段语义遵循：`title` = 一句话任务标题（做什么），`description` = 背景与关键约束（为什么做、边界是什么）。

### init.sh（项目根目录）
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/init.sh.template`，根据技术栈定制安装命令和 dev server 命令，执行 `chmod +x init.sh`。

### .claude/recording/
创建 `.claude/recording/` 目录（用于存储 session 记录文件）。

### .claude/lessons.md
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/lessons.md.template` 写入。

### .claude/dsettings.json
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/dsettings.json.template` 写入。若 `.claude/dsettings.json` 已存在则跳过。优先使用 `dsettings.json` 作为 v1.0 命名空间。

### .claude/project-pitfalls.md
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/project-pitfalls.md.template` 写入 `.claude/project-pitfalls.md`。若已存在则跳过（不覆盖用户已有内容）。此文件用于记录项目级高频误判表，由 Stop hook 的归档聚合逻辑持续填充。

### .claude/decisions.md（可选）
询问用户是否需要创建决策记录文件（有明确设计方向或技术选型的项目推荐）。如需要，读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/decisions.md.template` 写入。

### .claude/checks/smoke.sh
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/smoke.sh.template`，根据技术栈定制，执行 `chmod +x .claude/checks/smoke.sh`。

### .claude/agents/
创建 `.claude/agents/` 目录，将 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/agents/` 下的文件逐一复制：
- `explorer.md` — 只读探索代理（permissionMode: plan）
- `implementer.md` — 实施代理（permissionMode: acceptEdits）

## Step 5：可选 — 架构约束

询问用户是否需要 `.claude/rules/constraints.md`（架构复杂的项目推荐）。

如需要，读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/references/constraint-template.md`，引导用户用五维框架（业务/时序/跨平台/并发/感知）定义约束。

## Step 6：Git 初始化（如需要）

若当前目录不是 git 仓库，参考上述步骤初始化 git 仓库并创建初始提交。

## Step 7：验证清单

确认以下文件均已创建：
- [ ] `.claude/CLAUDE.md` 已填充项目信息
- [ ] `.claude/CLAUDE.md` 的「项目结构」章节包含扫描结果（非默认占位符）
- [ ] `.claude/CLAUDE.md` 包含「工作流规则」章节，规则索引列出 13 个文件（含 mindset.md、verification.md、correction.md、pitfalls.md、session.md、task.md，不含 states.md）
- [ ] `.claude/rules/` 下有 13 个 rules 文件（README.md, mindset.md, judgments.md, workflow.md, verification.md, correction.md, pitfalls.md, session.md, task.md, exceptions.md, templates.md, constraints.md, file-layout.md）
- [ ] `.claude/rules/` 下不存在 states.md 或 file-layout.md（已替换为新版规则集）
- [ ] `.claude/rules/states.md.backup` 仅在检测到旧版时存在（正常初始化不应存在）
- [ ] 项目根目录有 `AGENTS.md`
- [ ] `.claude/task.json` 是有效 JSON
- [ ] `init.sh` 可执行
- [ ] `.claude/recording/` 目录存在
- [ ] `.claude/recording.md` 不存在（已迁移为 recording/ 目录）或已重命名为 `recording.md.backup`
- [ ] `.claude/lessons.md` 存在
- [ ] `.claude/settings.json` 或 `.claude/dsettings.json` 存在且 JSON 合法
- [ ] `.claude/project-pitfalls.md` 存在（从模板初始化）
- [ ] `.claude/checks/smoke.sh` 可执行
- [ ] `.claude/agents/explorer.md` 和 `implementer.md` 存在
- [ ] （可选）`.claude/decisions.md`
