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

## Step 2：选择配置模式

检查 `~/.claude/rules/` 是否存在：
- 存在 → 默认推荐**精简模式**（引用全局规则，不复制）
- 不存在 → 默认推荐**便携模式**（规则内嵌，项目自包含）

询问用户确认模式选择。

## Step 3：创建项目文件

### .claude/CLAUDE.md
- **精简模式**：读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/claude-md-minimal.template`，填入项目信息
- **便携模式**：读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/claude-md-portable.template`，将 `[RULES:filename.md]` 占位符替换为 `assets/rules/` 对应文件内容

### AGENTS.md（项目根目录）
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/agents-md.template` 写入项目根目录。

### .claude/task.json
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/task.json.template`。若用户已有需求，填充初始任务（status: InDraft）；否则保持 tasks 数组为空。

### init.sh（项目根目录）
读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/init.sh.template`，根据技术栈定制安装命令和 dev server 命令，执行 `chmod +x init.sh`。

### .claude/recording.md
写入初始内容：
```markdown
# Session 记录

(Sessions will be recorded here)
```

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
- [ ] 项目根目录有 `AGENTS.md`
- [ ] `.claude/task.json` 是有效 JSON
- [ ] `init.sh` 可执行
- [ ] `.claude/recording.md` 存在
- [ ] `.claude/checks/smoke.sh` 可执行
- [ ] （可选）`.claude/rules/constraints.md`
