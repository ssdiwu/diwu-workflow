---
description: 将功能描述转化为 task.json 任务列表，支持澄清问题、质量检查、三视角审查
argument-hint: [功能描述（可选）]
allowed-tools: Read, Write, Edit, Glob
---

# /dplan — 任务规划

## Step 1：接收功能描述

若用户已在命令参数中描述功能，直接进入 Step 2。否则询问用户想要实现什么功能。

## Step 2：澄清问题

根据功能描述，提出 3-4 个聚焦问题（每次只问一个维度，推断合理选项供用户选择）：
- **目标**：这个功能解决什么问题？
- **核心操作**：用户的关键操作有哪些？
- **边界**：明确不做什么？
- **成功标准**：怎么算完成？
- **具体例子**：能举一个典型操作的完整例子吗？（用来直接推导 Given/When/Then）

## Step 3：确定新任务 ID

写入前必须：
1. 读取 `.claude/task.json` 中所有任务的最大 `id`
2. 用 glob 匹配读取 `.claude/task_archive*.json` 中所有任务的最大 `id`
3. 取两者最大值 + 1 作为新任务起始 id（严禁 id 复用）

## Step 4：生成并写入任务

根据澄清结果生成任务列表，追加到 `.claude/task.json`。

每个任务必须包含所有字段：
```json
{
  "id": 1,
  "description": "动词开头的一句话描述",
  "status": "InDraft",
  "acceptance": ["Given ... When ... Then ..."],
  "steps": ["实施步骤"],
  "category": "functional | ui | bugfix | refactor | infra",
  "blocked_by": []
}
```

边界情况：
- `.claude/task.json` 不存在：创建 `{"tasks": []}` 再追加
- `.claude/` 目录不存在：先创建目录
- 存在明显技术未知量：先生成 `category: infra` 的 Spike 任务（acceptance 为"输出调研结论文档"），再生成依赖它的实施任务

## Step 5：任务质量检查

逐条检查每个新生成的任务：
- acceptance 是否使用 Given/When/Then 格式（functional/ui/bugfix 类必须）
- acceptance 是否可验证（无"works correctly"等模糊描述）
- steps 是否自包含（外部凭据有来源路径，无隐式上下文依赖）
- 粒度是否合理（预估是否超过 2000 行，如是提示拆分）
- 是否垂直切片（端到端打通，非按技术层横切）

发现问题时：列出具体问题 + 建议修正，等用户确认后继续。

## Step 6：三视角审查（仅对复杂任务触发）

触发条件：category 为 functional/ui 且 acceptance 超过 3 条，或存在多个 blocked_by。

从三个视角审查：
- **开发视角**：步骤是否清晰可执行？有无技术风险？
- **QA 视角**：acceptance 是否覆盖边界条件和异常路径？
- **业务视角**：这个任务交付后，用户能感知到价值吗？

输出补充建议，用户确认后更新 acceptance/steps。

## Step 7：写入后提示

1. 列出已写入的任务（id + description）
2. 若存在 blocked_by 引用，提示：前置任务也是 InDraft，需人工先将其确认为 InSpec，依赖关系才生效
3. 提示用户：确认需求后，告知 Agent 将任务状态改为 InSpec 即可开始实施

## 不做的事

- 不生成中间 PRD markdown 文件
- 不自动将任务改为 InSpec
