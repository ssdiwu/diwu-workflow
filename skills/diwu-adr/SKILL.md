---
name: dadr
description: 记录架构决策（Architecture Decision Record）。触发场景：做重大技术选型、架构模式选择、API 设计决策、发现不可逆约束、选择一个方案而放弃另一个可行方案时。
user-invocable: true
---

diwu 工作流中记录架构决策的工具，输出保存到 `.doc/adr/` 目录。

## 执行流程

**Step 1**：用户描述正在面临的决策。

**Step 2**：Agent 提出 2-3 个澄清问题，聚焦：
- 考虑过哪些备选方案？
- 有哪些约束条件（时间、团队能力、现有技术栈）？
- 各方案的核心取舍是什么？

**Step 3**：生成 ADR 并写入文件。

## ADR 格式

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

## ID 管理规则

- 写入前检查 `.doc/adr/` 目录下已有文件，取最大编号 +1
- 文件命名：`.doc/adr/ADR-NNN-kebab-case-title.md`（NNN 三位数字补零）

## 边界情况

- `.doc/adr/` 不存在：创建目录再写入
- 更新已有 ADR 状态（如 Proposed → Accepted）：找到对应文件，只修改 Status 行

## 写入后提示

- 显示文件路径
- 提示：如需关联到某个任务，可在 task.json 对应任务的 steps 中注明 "参见 .doc/adr/ADR-NNN"
