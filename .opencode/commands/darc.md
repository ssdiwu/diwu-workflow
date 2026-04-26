---
description: 手动触发归档——Task 归档和 Recording 物理归档的双轨操作
argument-hint: [可选：强制归档]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# /darc — 归档管理

手动执行 Task 和 Recording 的归档操作。也可查看归档状态而不执行。

## 触发方式

- `/darc` — 检查归档状态，提示是否需要归档
- `/darc 执行` — 强制执行归档（忽略阈值检查）

## 归档双轨总览

| 轨道 | 触发条件 | 阈值（dsettings.json） | 产物位置 |
|------|---------|----------------------|----------|
| Task 归档 | Done/Cancelled 数 ≥ threshold | `task_archive_threshold`（默认 20） | `.diwu/archive/task_archive_YYYY-MM.json` |
| Recording 归档 | 文件数 ≥ threshold 或 年龄 > days | `recording_archive_threshold`（默认 50）<br>`recording_retention_days`（默认 30） | `.diwu/archive/recording_YYYY-MM-DD.md` |

## 执行步骤

### Step 1：检查状态

1. 读取 `.diwu/dtask.json`，统计 Done/Cancelled 任务数
2. 列出 `.diwu/recording/` 文件数和最旧文件修改时间
3. 对比阈值，输出归档建议

### Step 2：Task 归档（如触发）

1. 读取 `.diwu/dtask.json`，筛选 status=Done/Cancelled 的任务
2. 写入 `.diwu/archive/task_archive_YYYY-MM.json`
3. 从 `dtask.json` 中移除已归档任务（保留活跃任务）

### Step 3：Recording 归档（如触发）

1. 列出 `.diwu/recording/` 所有 session 文件
2. 按时间排序，将最旧的 N-threshold 个文件内容追加到 `.diwu/archive/recording_YYYY-MM-DD.md`
3. 删除已归档的源文件（保留最新 threshold 个）

### Step 4：踩坑聚合（必做）

1. 扫描归档的 recording + 剩余 recording 中所有 `### 本次踩坑/经验` 段落
2. 按类别聚类（验证误读/分层未拆清/环境漂移/路由护栏契约等）
3. 追加写入 `.diwu/project-pitfalls.md`
4. **来源必须写具体 session 文件名**（如 `session-2026-04-18-213522.md`）

## 验证清单

- [ ] dtask.json 中无残留的 Done/Cancelled 任务（超出阈值部分）
- [ ] recording/ 文件数 < threshold
- [ ] archive/ 产物可读且 JSON/MD 合法
- [ ] project-pitfalls.md 已更新（如有踩坑数据）

## 不做的事

- 不自动归档（需用户确认或手动触发）
- 不修改活跃任务（InDraft/InSpec/InProgress/InReview）
- 不复用任务 ID（归档后 ID 继续递增）
