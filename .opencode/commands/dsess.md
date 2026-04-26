---
description: 手动触发 Session 启动流程（Preflight 检查、上下文恢复、归档检查、任务选择）
argument-hint: [可选：指定任务 ID 恢复]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# /dsess — Session 启动

手动执行 Session 生命周期启动流程，通常由 plugin 自动触发，也可手动调用。

## 触发方式

- `/dsess` — 执行完整启动流程
- `/dsess 任务ID` — 直接恢复指定 InProgress 任务

## 执行步骤

### Step 1：Preflight 检查

1. **基线验证**：运行 `.diwu/checks/smoke.sh`（如存在）
2. **三唯一确认**：
   - 唯一主线目录：本轮任务主要实现目录
   - 唯一运行入口：验证主链的启动/调用入口
   - 唯一 canonical：当前必须以其为准的规则文件
3. **5 问开工检查**：
   - 这件事能不能直接做，还是先探索/先验证/先写最小规格？
   - 本次唯一主线目录、唯一运行入口、唯一 canonical 是什么？
   - 当前最可能先判断错的地方是什么？
   - 进入实施前最少要拿到哪些判别依据？
   - 完成后用哪类高等级证据判断结果成立？
4. **误判表预加载**：检查 `.diwu/project-pitfalls.md`（如存在）
5. **git status**：确认工作区状态

### Step 2：上下文恢复

1. **优先**读取 `.diwu/continue-here.md`（如存在），读完后删除
2. 否则读取 `.diwu/recording/` 最新 1-2 个 session 文件
3. 读取 `.diwu/decisions.md`（如存在）
4. 运行 `git log --oneline -20`

### Step 3：归档检查

1. 统计 `.diwu/dtask.json` 中 Done/Cancelled 任务数量
2. 超过 `task_archive_threshold`（默认 20）时提示归档
3. 统计 `.diwu/recording/` 文件数，超过阈值提示归档

### Step 4：任务选择

1. **优先恢复** InProgress 任务
2. 否则选第一个 InSpec 任务，检查 `blocked_by`：
   - 为空/全部 Done → 可开始
   - 存在 InReview 且超前未达上限 → 可超前
3. **禁止**选择 InDraft 任务

### Step 5：环境初始化（可选）

1. 运行 `init.sh`（如存在）
2. 运行 build/lint 基线测试

## 持续运行模式

| 模式 | 行为 |
|------|------|
| `true` | 任务 Done 后自动选择下一个可执行任务 |
| `false` | 每完成一个任务即停止，等待人工介入 |

## 输出

- 当前任务状态摘要
- 推荐开始的任务（如有）
- 任何需要人工确认的事项
