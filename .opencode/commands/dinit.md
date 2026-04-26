---
description: 初始化项目的 diwu-workflow 工作流结构，创建 .diwu/ 目录、AGENTS.md、references/ 规则文件
argument-hint: [项目描述（可选）]
allowed-tools: Read, Write, Edit, Bash, Glob
---

# /dinit — 项目初始化

## Step 0：刷新检测

检查 `.diwu/dtask.json` 是否已存在：
- **已存在** → 刷新模式：跳过 Step 2-3 的骨架创建，只执行 Step 1（收集信息）和 Step 1.5（代码库扫描），然后更新 `AGENTS.md` 并确保项目符合最新规范
- **不存在** → 初始化模式：执行完整流程（Step 1 → Step 1.5 → Step 2 → Step 3 → ...）

**刷新模式的章节补充逻辑**：

1. **检测「工作流规则」章节**：
   - 搜索 AGENTS.md 中是否存在 `## 工作流规则` 标题
   - 如果不存在，在 `## 核心原则` 之前插入以下内容：
   ```markdown
   ## 工作流规则

   详细规则见 @.opencode/references/ 目录：
   - @.opencode/references/README.md - 规则速查索引
   - @.opencode/references/judgments.md - 判断锚点集中管理
   - @.opencode/references/states.md - 任务状态机与 acceptance 格式
   - @.opencode/references/workflow.md - Session 启动、任务规划、实施、验证
   - @.opencode/references/exceptions.md - 异常处理与 BLOCKED 判定
   - @.opencode/references/templates.md - DECISION TRACE、BLOCKED、REVIEW 格式模板
   - @.opencode/references/file-layout.md - .diwu/ 目录结构与归档规则
   - @.opencode/references/constraints.md - 架构约束（五维约束设计）

   ```

2. **检测「规则引用说明」章节**：
   - 搜索 AGENTS.md 中是否存在 `## 规则引用说明` 标题
   - 如果不存在，在文件末尾追加以下内容：
   ```markdown

   ## 规则引用说明

   本项目使用 @.opencode/references/ 引用自动加载工作流规则。规则文件位于 `.opencode/references/` 目录，由 diwu-workflow 插件的 `experimental.chat.system.transform` hook 在每次对话开始时注入。
   ```

3. **更新「项目结构」章节**：
   - 用 Step 1.5 的扫描结果替换 `<!-- SCAN_RESULT_PLACEHOLDER -->` 占位符或更新现有内容

4. **迁移 recording.md 到 recording/ 目录**：
   - 检查 `.diwu/recording.md` 是否存在
   - 如果存在，执行迁移：
     - 读取 recording.md 内容，按 `## Session YYYY-MM-DD HH:MM:SS` 分隔符识别所有 session
     - 创建 `.diwu/recording/` 目录
     - 将每个 session 写入独立文件 `recording/session-YYYY-MM-DD-HHMMSS.md`（时间戳从 session 标题提取并转换为文件名格式）
     - 迁移完成后将原 recording.md 重命名为 `recording.md.backup`

5. **同步规则文件**（仅初始化模式）：
   - 清理旧文件：删除 `.opencode/references/core-states.md` 和 `.opencode/references/core-workflow.md`（如存在）
   - 确保 `.opencode/references/` 下有 8 个核心规则文件：
     - README.md
     - judgments.md
     - states.md
     - workflow.md
     - exceptions.md
     - templates.md
     - file-layout.md
     - constraints.md
   - 如果缺失，从 diwu-workflow 插件模板复制

## Step 1：收集项目信息

询问用户（上下文已有的跳过）：
- **项目名称**和**1-2 句描述**
- **技术栈**：语言、框架、数据库
- **常用命令**：dev、build、lint、test
- **关键目录**：项目结构概览

**示例（填写完整的项目信息）**：
- 项目名称：my-project
- 描述：一个 Web 应用，提供用户管理和数据分析功能
- 技术栈：Node.js + React + PostgreSQL
- 常用命令：`npm run dev`（dev），`npm run build`（build），`npm test`（test）
- 关键目录：`src/`（源码），`tests/`（测试），`docs/`（文档）

收集到的信息要达到这个粒度才能生成有效的 AGENTS.md 和 smoke.sh。

## Step 1.5：代码库扫描

从 `.diwu/dsettings.json` 读取 `subagent_concurrency` 参数（默认 3），使用子代理并行扫描代码库：

**扫描任务**（并行执行）：
1. **目录结构扫描**：识别主要目录层级、文件分布、模块组织方式
2. **技术栈检测**：识别 package.json / requirements.txt / go.mod 等配置文件，提取依赖和工具链信息
3. **关键文件识别**：定位 README、配置文件、入口文件、测试目录

**扫描结果整合**：
- 将扫描结果整合为结构化的项目结构描述
- 补充 Step 1 收集的信息（如用户未提供关键目录，用扫描结果填充）
- 用于填充 AGENTS.md 的「项目结构」章节

## Step 2：复制规则文件（初始化模式）

确保 `.opencode/references/` 下有 8 个核心规则文件：
- README.md
- judgments.md
- states.md
- workflow.md
- exceptions.md
- templates.md
- file-layout.md
- constraints.md

> 规则来源：diwu-workflow 插件内置模板，或用户自定义。

## Step 3：创建项目文件

### AGENTS.md（项目根目录）
读取 diwu-workflow 插件模板 `agents-md.template`，填入项目信息，写入项目根目录。

### .diwu/dtask.json
创建 `{"tasks": []}`。若用户已有需求，填充初始任务（status: InDraft）；否则保持 tasks 数组为空。
若填充初始任务，字段语义遵循：`title` = 一句话任务标题（做什么），`description` = 背景与关键约束（为什么做、边界是什么）。

### init.sh（项目根目录）
根据技术栈定制安装命令和 dev server 命令，执行 `chmod +x init.sh`。

### .diwu/recording/
创建 `.diwu/recording/` 目录（用于存储 session 记录文件）。

### .diwu/lessons.md
创建空文件或读取模板写入。

### .diwu/dsettings.json
创建默认设置文件。若已存在则跳过。

默认参数：
```json
{
  "review_limit": 5,
  "task_archive_threshold": 20,
  "recording_archive_threshold": 50,
  "recording_retention_days": 30,
  "context_monitor_warning": 30,
  "context_monitor_critical": 50,
  "context_monitor_delay": 10,
  "continuous_mode": true,
  "subagent_concurrency": 3,
  "drift_detection": {"enabled": true}
}
```

### .diwu/decisions.md（可选）
询问用户是否需要创建决策记录文件（有明确设计方向或技术选型的项目推荐）。

### .diwu/checks/smoke.sh
根据技术栈定制，执行 `chmod +x .diwu/checks/smoke.sh`。

默认内容：
```bash
#!/bin/bash
set -e

echo "=== Smoke Test ==="

# JSON 合法性检查
for file in .diwu/dtask.json .diwu/dsettings.json; do
  if [ -f "$file" ]; then
    python3 -m json.tool "$file" > /dev/null && echo "✓ $file"
  fi
done

echo "=== All checks passed ==="
```

## Step 4：可选 — 架构约束

询问用户是否需要 `.opencode/references/constraints.md`（架构复杂的项目推荐）。

如需要，引导用户用五维框架（业务/时序/跨平台/并发/感知）定义约束。

## Step 5：Git 初始化（如需要）

若当前目录不是 git 仓库：
```bash
git init
git add .
git commit -m "Initial project setup with diwu-workflow"
```

## Step 6：验证清单

确认以下文件均已创建：
- [ ] `AGENTS.md` 已填充项目信息
- [ ] `AGENTS.md` 的「项目结构」章节包含扫描结果（非默认占位符）
- [ ] `.opencode/references/` 下有 8 个规则文件（README.md, judgments.md, states.md, workflow.md, exceptions.md, templates.md, file-layout.md, constraints.md）
- [ ] `.opencode/references/` 下不存在 core-states.md 和 core-workflow.md（已清理）
- [ ] `.diwu/dtask.json` 是有效 JSON
- [ ] `init.sh` 可执行
- [ ] `.diwu/recording/` 目录存在
- [ ] `.diwu/recording.md` 不存在（已迁移为 recording/ 目录）或已重命名为 `recording.md.backup`
- [ ] `.diwu/lessons.md` 存在
- [ ] `.diwu/dsettings.json` 存在且 JSON 合法
- [ ] `.diwu/checks/smoke.sh` 可执行
- [ ] （可选）`.diwu/decisions.md`
