# Rules Index（精华摘要）

> 详细见各原文件。本文件供 UserPromptSubmit hook 注入。

## 1. 状态权限（core-states.md）

| 状态 | 主代理可改 | 子代理 |
|------|-----------|--------|
| InDraft | title/description/acceptance/steps/status | 只读 |
| InSpec~Done | status | 只读 |

转移：InDraft→InSpec（人工确认）→InProgress→InReview→Done

- BLOCKED：缺凭据/外部不可用；CHANGE REQUEST：acceptance 矛盾/不可实现；mock 可验证→CONTINUE
- InReview→Done 需人工：改了 API/字段契约，或单任务 >2000 行；其余自审 Done
- blocked_by 写入：前置未 Done 且当前依赖其输出→写；前置已 Done 或仅调用关系→不写

## 2. Session 启动仪式（core-workflow.md）

Step 1-3 串行，Step 4 可选：
1. Preflight：运行 smoke.sh；检查 pending CR；git status
2. 上下文恢复：读 recording.md（统计 session 数）；读 task.json；读 decisions.md；git log -20
3. 任务选择：优先恢复 InProgress；否则选 InSpec（查 blocked_by）；禁选 InDraft；超前上限5
4. 环境初始化（可选）：运行 init.sh；基线失败先修复

提交：Done 时提交；超前任务标 InReview 立即提交（最多5次）。格式：`[Task#N] 标题 - completed`

## 3. DECISION TRACE 强制触发（templates.md）

8个场景必须先输出 DECISION TRACE：任务选择、CR/BLOCKED判定、并行与串行、大幅度修改判定、blocked_by写入、循环依赖识别、InProgress→InSpec、InReview→Done。

```
DECISION TRACE
结论: [BLOCKED|CHANGE REQUEST|CONTINUE|REVIEW|SKIP]
规则命中: - [规则条目]
证据: - [状态/日志/git diff]
排除项: - [为何不是其他结论]
下一步: - [立即执行的动作]
```

## 4. 归档触发（file-layout.md + templates.md）

- task.json Done/Cancelled >20条 → 归档到 task_archive_YYYY-MM.json
- recording.md session >5条 → 最旧的移入 recording_archive/YYYY-MM-DD.md

## 5. recording.md Session 格式（templates.md）

时间戳必须运行 `date '+%Y-%m-%d %H:%M:%S'` 获取，禁止手写：

```markdown
---
## Session 2026-02-17 14:30:22
### 上下文恢复
- 上次任务: Task#N (状态) / Git: clean / 待批准 CR: 无
### Task#N: 标题 → Done
**实施内容**: ... **验收验证**: - [x] 条目(证据) **提交**: abc123f
### 下一步: Task#N+1
---
```

## 6. 目录结构（file-layout.md）

```
.claude/  task.json / recording.md / decisions.md / checks/smoke.sh + task_<id>_verify.sh
.doc/adr/ ADR-NNN-*.md
```

规则文件由插件 hook 注入，不在项目 .claude/ 中。

## 7. subagent 约束（core-workflow.md + templates.md）

- 并发数最多 3；子代理禁止写 task.json
- 探索/搜索类用 haiku（只读）；实施类继承主模型
- 并行：问题域不相交 + 无共享写文件（同时满足）
- 串行：后一步依赖前一步输出，或需积累上下文
- 子代理启动仪式：读 recording.md → 读 task → 读 decisions.md
