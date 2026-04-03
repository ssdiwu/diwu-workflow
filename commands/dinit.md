---
description: 初始化项目的 Claude Code Agent 工作流结构，创建 CLAUDE.md、task.json、recording/ 目录、init.sh、smoke.sh
argument-hint: [项目描述（可选）]
allowed-tools: Read, Write, Edit, Bash, Glob
effort: medium
---

# /dinit — 项目初始化

## Step 0：刷新检测

检查 `.claude/CLAUDE.md` 是否已存在：
- **已存在** → 刷新模式：跳过 Step 2-3 的骨架创建，只执行 Step 1（收集信息）和 Step 1.5（代码库扫描），然后更新 `.claude/CLAUDE.md` 并确保项目符合最新规范
- **不存在** → 初始化模式：执行完整流程（Step 1 → Step 1.5 → Step 2 → Step 3 → ...）

**刷新模式的章节补充逻辑**：

1. **检测「工作流规则」章节**：
   - 搜索 CLAUDE.md 中是否存在 `## 工作流规则` 标题
   - 如果不存在，在 `## 核心原则` 之前插入以下内容：
   ```markdown
   ## 工作流规则

   详细规则见 @rules/ 目录：
   - @rules/README.md - 规则速查索引
   - @rules/judgments.md - 判断锚点集中管理
   - @rules/states.md - 任务状态机与 acceptance 格式
   - @rules/workflow.md - Session 启动、任务规划、实施、验证
   - @rules/exceptions.md - 异常处理与 BLOCKED 判定
   - @rules/templates.md - DECISION TRACE、BLOCKED、REVIEW 格式模板
   - @rules/file-layout.md - .claude/ 目录结构与归档规则
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
   - 清理旧文件：删除 `.claude/rules/core-states.md` 和 `.claude/rules/core-workflow.md`（如存在）
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

从 `.claude/settings.json` 读取 `subagent_concurrency` 参数（默认 3），使用子代理并行扫描代码库：

**扫描任务**（并行执行）：
1. **目录结构扫描**：识别主要目录层级、文件分布、模块组织方式
2. **技术栈检测**：识别 package.json / requirements.txt / go.mod 等配置文件，提取依赖和工具链信息
3. **关键文件识别**：定位 README、配置文件、入口文件、测试目录

**扫描结果整合**：
- 将扫描结果整合为结构化的项目结构描述
- 补充 Step 1 收集的信息（如用户未提供关键目录，用扫描结果填充）
- 用于填充 `.claude/CLAUDE.md` 的「项目结构」章节

## Step 2：复制规则文件

读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/rules-manifest.json`，按 `rules` 列表将规则文件复制到 `.claude/rules/`（覆盖旧版本）。

## Step 3：创建项目文件

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

### .claude/settings.json
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/settings.json.template` 写入。若已存在则跳过。

### .claude/decisions.md（可选）
询问用户是否需要创建决策记录文件（有明确设计方向或技术选型的项目推荐）。如需要，读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/decisions.md.template` 写入。

### .claude/checks/smoke.sh
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/smoke.sh.template`，根据技术栈定制，执行 `chmod +x .claude/checks/smoke.sh`。

### .claude/agents/
创建 `.claude/agents/` 目录，将 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/agents/` 下的文件逐一复制：
- `explorer.md` — 只读探索代理（permissionMode: plan）
- `implementer.md` — 实施代理（permissionMode: acceptEdits）

## Step 4：可选 — 架构约束

询问用户是否需要 `.claude/rules/constraints.md`（架构复杂的项目推荐）。

如需要，读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/references/constraint-template.md`，引导用户用五维框架（业务/时序/跨平台/并发/感知）定义约束。

## Step 5：Git 初始化（如需要）

若当前目录不是 git 仓库：
```bash
git init
git add .
git commit -m "Initial project setup with Claude Code workflow"
```

## Step 6：验证清单

确认以下文件均已创建：
- [ ] `.claude/CLAUDE.md` 已填充项目信息
- [ ] `.claude/CLAUDE.md` 的「项目结构」章节包含扫描结果（非默认占位符）
- [ ] `.claude/rules/` 下有 8 个 rules 文件（README.md, judgments.md, states.md, workflow.md, exceptions.md, templates.md, file-layout.md, constraints.md）
- [ ] `.claude/rules/` 下不存在 core-states.md 和 core-workflow.md（已清理）
- [ ] 项目根目录有 `AGENTS.md`
- [ ] `.claude/task.json` 是有效 JSON
- [ ] `init.sh` 可执行
- [ ] `.claude/recording/` 目录存在
- [ ] `.claude/recording.md` 不存在（已迁移为 recording/ 目录）或已重命名为 `recording.md.backup`
- [ ] `.claude/lessons.md` 存在
- [ ] `.claude/settings.json` 存在且 JSON 合法
- [ ] `.claude/checks/smoke.sh` 可执行
- [ ] `.claude/agents/explorer.md` 和 `implementer.md` 存在
- [ ] （可选）`.claude/decisions.md`
