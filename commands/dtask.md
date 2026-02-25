---
description: 将功能描述转化为 task.json 任务列表，支持澄清问题、质量检查、三视角审查
argument-hint: [功能描述（可选）]
allowed-tools: Read, Write, Edit, Glob
---

# /dtask — 任务规划

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

每个任务必须包含所有字段，参考以下示例的思维粒度：

```json
{
  "id": 3,
  "title": "实现邮件验证码发送",
  "category": "functional",
  "status": "InDraft",
  "description": "用户注册后需要验证邮箱。调用 SMTP 服务发送 6 位验证码，验证码有效期 10 分钟，存储在 Redis 中。",
  "acceptance": [
    "Given 新用户完成注册表单提交 When 系统调用 sendVerification(email) Then Redis 中存在 key=verify:{email}，value=6位数字，TTL=600s",
    "Given SMTP 服务不可用 When 调用 sendVerification() Then 抛出 EmailServiceError，不写入 Redis",
    "Given 同一邮箱 10 分钟内重复请求 When 调用 sendVerification() Then 覆盖旧验证码，重置 TTL"
  ],
  "steps": [
    "1. 在 src/services/email.ts 实现 sendVerification(email: string): Promise<void>",
    "2. 在 src/lib/redis.ts 添加 setVerifyCode(email, code, ttl) 方法",
    "3. 凭据见 doc/runbook.md §2.1（SMTP 配置）",
    "4. 运行 .claude/checks/task_3_verify.sh 验证"
  ],
  "blocked_by": [2]
}
```

示例中的思维粒度要点：
- `acceptance` 的 Given 有具体函数名/页面路径，Then 有可断言的系统状态（key 名、TTL 值、错误类型）
- `steps` 有具体文件路径，不依赖隐式上下文
- `description` 说明背景（为什么）+ 技术约束（怎么做），不只是功能描述

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

**acceptance 坏→好对比**：
- ❌ `Given 用户登录 When 提交表单 Then 登录成功`（Then 无法断言，Given 无具体状态）
- ✓ `Given 新用户完成注册表单提交 When 系统调用 sendVerification(email) Then Redis 中存在 key=verify:{email}，value=6位数字，TTL=600s`

发现问题时：列出具体问题 + 建议修正，等用户确认后继续。

## Step 6：三视角审查（仅对复杂任务触发）

触发条件：category 为 functional/ui 且 acceptance 超过 3 条，或存在多个 blocked_by。

从三个视角审查，按子代理策略（见 core-workflow.md）派发并行审查：
- 子代理 A：**开发视角** — 步骤是否清晰可执行？有无技术风险？
- 子代理 B：**QA 视角** — acceptance 是否覆盖边界条件和异常路径？
- 子代理 C：**业务视角** — 这个任务交付后，用户能感知到价值吗？

三个子代理完成后，主代理汇总冲突点，输出补充建议，用户确认后更新 acceptance/steps。

## Step 7：写入后提示

1. 列出已写入的任务（id + description）
2. 若存在 blocked_by 引用，提示：前置任务也是 InDraft，需人工先将其确认为 InSpec，依赖关系才生效
3. 提示用户：确认需求后，告知 Agent 将任务状态改为 InSpec 即可开始实施

## 不做的事

- 不生成中间 PRD markdown 文件
- 不自动将任务改为 InSpec
