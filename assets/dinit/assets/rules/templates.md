# 格式模板与参数

## BLOCKED 格式

```
BLOCKED - 需要人工介入

当前任务: Task#N - [任务标题]
任务描述: [背景与关键约束]

已完成的工作:
- [已实现的部分]

阻塞原因:
- [具体阻塞原因]
- [环境/依赖缺失详情]

需人工帮助:
1. [具体操作步骤]
2. [配置/凭据来源]

解除阻塞后:
- 任务将从 InSpec 恢复到 InProgress
```

## CHANGE REQUEST 格式

```
CHANGE REQUEST - 需要修改需求

当前任务: Task#N - [任务标题]
任务描述: [背景与关键约束]
当前状态: InSpec (保持)

已完成的工作:
- [已实现的部分]

发现的问题:
- [原 acceptance 为什么无法实现]

建议修改:
- acceptance 修改:
  - [删除] "xxx"
  - [新增] "yyy"
  - [修改] "zzz" → "www"

影响评估:
- 预计额外工作量: [X 小时/天]
- 影响其他任务: [是/否]

等待批准:
- 人工批准后,将更新 task.json 并继续实施
```

## PENDING REVIEW 格式

```
PENDING REVIEW - 超前实施已达上限

等待验收: Task#N
已超前完成: Task#X, Task#Y, Task#Z (N/5)

请验收 Task#N:
- 通过 → 可继续超前实施
- 失败 → 需评估已超前任务的影响并修复
```

## REVIEW 请求格式

```
REVIEW - 请求人工审查

Task#N: [任务标题]
修改范围: [文件路径（行数变更）]

验收验证:
- [x] [acceptance 条目] — [验证方法/测试结果]

等待: 人工确认后将标记为 Done
```

## DECISION TRACE 格式（判断过程模板）

以下场景必须先输出 DECISION TRACE：任务选择、CR/BLOCKED 判定、并行与串行选择、大幅度修改判定、blocked_by 写入判定、循环依赖识别、InProgress→InSpec 判定、InReview→Done 判定。

```
DECISION TRACE

结论: [BLOCKED | CHANGE REQUEST | CONTINUE | REVIEW | SKIP]

规则命中:
- [命中的规则条目，例如 core-workflow.md §任务选择策略]

证据:
- [task.json 状态、blocked_by 明细、测试日志、git diff --stat、配置检查结果]

排除项:
- [为什么不是其他结论；例如“非需求矛盾，故不是 CHANGE REQUEST”]

下一步:
- [立即执行的动作；例如“输出 BLOCKED 模板并等待人工配置”]
```

## recording.md Session 格式

```markdown
---
## Session YYYY-MM-DD HH:MM:SS

### Task#N: [任务标题] → [状态]

**实施内容**:
- [完成的工作]

**验收验证**:
- [x] [acceptance 条目] ([验证方法])

**提交**: commit [hash]

### 下一步
[下一步计划]

---
```

## Change Request 记录格式

```markdown
---
## Session YYYY-MM-DD HH:MM:SS

### Task#N: [任务标题] → BLOCKED

**Change Request #N**:
- **原因**: [发现的问题]
- **建议**: [修改建议]
- **影响**: [影响评估]
- **状态**: pending

**需人工介入**:
[具体需求]

---
```

## 可调参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 超前上限 | 5 | 最多同时超前实施的任务数 |
| task.json 归档阈值 | 20 | task.json 中 Done/Cancelled 任务超过此数触发归档 |
| recording.md 归档阈值 | 10 | recording.md 中 session 数超过此数触发归档 |
| 子代理并发数 | 3 | 0=禁用子代理，1=串行子代理，N≥2=最多N个并发子代理 |
| 探索/搜索类子代理模型 | haiku | 只读操作，降低成本 |
| 实施类子代理模型 | 继承主模型 | 写代码保持主模型质量 |
