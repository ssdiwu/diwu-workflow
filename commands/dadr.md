---
description: 记录架构决策（ADR），输出到 .doc/adr/ 目录
argument-hint: [决策描述（可选）]
allowed-tools: Read, Write, Glob, Bash
---

# /dadr — 架构决策记录

## Step 1：接收决策描述

若用户已在命令参数中描述决策，直接进入 Step 2。否则询问用户正在面临什么架构决策。

## Step 2：澄清问题

提出 2-3 个问题，聚焦：
- 考虑过哪些备选方案？
- 有哪些约束条件（时间、团队能力、现有技术栈）？
- 各方案的核心取舍是什么？

## Step 3：确定 ADR 编号

检查 `.doc/adr/` 目录下已有文件，取最大编号 + 1。`.doc/adr/` 不存在时先创建目录。

## Step 4：生成并写入 ADR

文件命名：`.doc/adr/ADR-NNN-kebab-case-title.md`（NNN 三位数字补零）

ADR 格式：
```markdown
# ADR-NNN: [标题]

**Status**: Proposed

**Date**: YYYY-MM-DD

## Context
[为什么需要做这个决策，背景和约束]

## Options Considered
- **Option A**: [描述] — 优点 / 缺点
- **Option B**: [描述] — 优点 / 缺点

## Decision
[选择了什么，以及核心原因]

## Consequences
- ✅ [正面影响]
- ⚠️ [需要注意的取舍或风险]
```

## Step 5：写入后提示

- 显示生成的文件路径
- 提示：如需关联到某个任务，可在 task.json 对应任务的 steps 中注明 "参见 .doc/adr/ADR-NNN"

## 边界情况

更新已有 ADR 状态（如 Proposed → Accepted）：找到对应文件，只修改 Status 行。
