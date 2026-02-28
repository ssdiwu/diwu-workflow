---
description: 初始化项目的 Claude Code Agent 工作流结构，创建 CLAUDE.md、task.json、recording.md、init.sh、smoke.sh
argument-hint: [项目描述（可选）]
allowed-tools: Read, Write, Edit, Bash, Glob
---

# /dinit — 项目初始化

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

## Step 2：复制规则文件

将 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/rules/` 下的五个文件逐一复制到 `.claude/rules/`：`core-states.md`、`core-workflow.md`、`exceptions.md`、`templates.md`、`file-layout.md`。

> 规则来源唯一：插件 `assets/dinit/assets/rules/`。

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

### .claude/recording.md
写入初始内容：
```markdown
# Session 记录

(Sessions will be recorded here)
```

### .claude/lessons.md
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/lessons.md.template` 写入。

### .claude/decisions.md（可选）
询问用户是否需要创建决策记录文件（有明确设计方向或技术选型的项目推荐）。如需要，读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/decisions.md.template` 写入。

### .claude/checks/smoke.sh
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/smoke.sh.template`，根据技术栈定制，执行 `chmod +x .claude/checks/smoke.sh`。

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
- [ ] 便携模式：`.claude/rules/` 下有五个 rules 文件
- [ ] 项目根目录有 `AGENTS.md`
- [ ] `.claude/task.json` 是有效 JSON
- [ ] `init.sh` 可执行
- [ ] `.claude/recording.md` 存在
- [ ] `.claude/lessons.md` 存在
- [ ] `.claude/checks/smoke.sh` 可执行
- [ ] （可选）`.claude/decisions.md`
- [ ] （可选）`.claude/rules/constraints.md`
