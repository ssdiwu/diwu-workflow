# 任务状态机

## task.json 结构

```json
{
  "tasks": [
    {
      "id": 3,
      "title": "实现邮件验证码发送",
      "description": "用户注册后需要验证邮箱。调用 SMTP 服务发送 6 位验证码，验证码有效期 10 分钟，存储在 Redis 中；SMTP 不可用时必须返回明确错误而非静默失败。",
      "status": "InDraft",
      "acceptance": [
        "Given 新用户完成注册表单提交 When 系统调用 sendVerification(email) Then Redis 中存在 key=verify:{email}，value=6位数字，TTL=600s",
        "Given SMTP 服务不可用 When 调用 sendVerification() Then 抛出 EmailServiceError，不写入 Redis",
        "Given 同一邮箱 10 分钟内重复请求 When 调用 sendVerification() Then 覆盖旧验证码，重置 TTL"
      ],
      "steps": [
        "1. 在 /absolute/path/to/project/src/services/email.ts 实现 sendVerification(email: string): Promise<void>",
        "2. 在 /absolute/path/to/project/src/lib/redis.ts 添加 setVerifyCode(email, code, ttl) 方法",
        "3. 凭据见 /absolute/path/to/project/doc/runbook.md §2.1（SMTP 配置）",
        "4. 运行 /absolute/path/to/project/.claude/checks/task_3_verify.sh 验证"
      ],
      "category": "functional",
      "blocked_by": [2]
    }
  ]
}
```

**字段说明**:

| 键名 | 中文含义 | 类型 | 说明 |
|------|---------|------|------|
| `id` | 任务编号 | 数字 | 从 1 开始递增，永不复用 |
| `title` | 任务标题 | 字符串 | 一句话描述任务做什么（动词开头） |
| `description` | 任务描述 | 字符串 | 背景 + 关键约束（为什么做、边界是什么） |
| `status` | 任务状态 | 字符串 | 见下方状态定义章节 |
| `acceptance` | 验收条件 | 数组 | Given/When/Then 格式的验收场景，见下方 acceptance 格式规范 |
| `steps` | 实施步骤 | 数组 | 实施过程的关键步骤，必须写绝对路径 |
| `category` | 任务分类 | 字符串 | 见下方任务分类说明 |
| `blocked_by` | 前置任务 | 数组 | (可选) 见下方 blocked_by 规范章节 |

**任务分类说明**:

| 分类值 | 中文含义 | 适用场景 |
|--------|---------|---------|
| `functional` | 功能开发 | 新增业务功能、API、核心逻辑 |
| `ui` | 界面开发 | 页面、组件、交互、样式 |
| `bugfix` | 缺陷修复 | 修复已知 bug |
| `refactor` | 重构 | 不改变行为的代码结构优化 |
| `infra` | 基础设施 | 构建、部署、配置、脚本 |

**acceptance 格式规范（Given/When/Then）**:

`functional`、`ui`、`bugfix` 类任务**必须**使用 GWT 格式，`infra`、`refactor` 类任务**可选**。

格式：`"Given [前置条件] When [用户动作] Then [预期结果]"`
- 多个条件或结果用"且"连接：`"Then 页面跳转到首页且显示欢迎语"`
- 单条 acceptance 中"且"超过 3 个时，应拆分为多条
- `infra`/`refactor` 任务可使用简单描述：`"构建产物不超过 500KB"`

**好的示例**（可证据化，每个 Then 子句 = 一个 `expect()` 断言）：
```
Given 用户在 /login 页面输入正确的 email+password
When 点击提交按钮
Then 跳转到 /dashboard，localStorage 中存在 auth_token，有效期 7 天
```

**坏的示例**（无法验证）：
```
Given 用户登录
When 提交表单
Then 登录成功
```

坏在哪里：Given 没有具体页面和数据状态；Then 是主观描述，不是可断言的系统状态。

**Then 子句自检**：能否直接写成 `expect(actual).toBe(expected)` 或 `assert actual == expected`？不能则需要细化。

---

## 状态定义

| 状态 | 含义 |
|------|------|
| InDraft | 需求草稿中，Agent 可修改任务标题、任务描述、验收条件、实施步骤 |
| InSpec | 需求已确认，锁定（Agent 只能修改 status 字段） |
| InProgress | 实施中，Agent 正在实现 |
| InReview | 验证中，实现完成，等待验证 |
| Done | 已完成，验证通过 |
| Cancelled | 已取消，任务不再需要 |

## 状态转移表

| 当前状态 | 事件 | 新状态 | 规则 |
|---------|------|--------|------|
| InDraft | 人工确认需求 | InSpec | Agent 不可再修改 title/description/acceptance/steps |
| InDraft | 需求取消 | Cancelled | - |
| InSpec | Agent 开始实施 | InProgress | - |
| InSpec | 发现需求问题 | (保持 InSpec) | 提交 Change Request，等人工批准 |
| InProgress | 实现完成，准备验证 | InReview | - |
| InProgress | 遇到阻塞 | InSpec | 退回，记录阻塞原因 |
| InProgress | 需求取消 | Cancelled | - |
| InReview | acceptance 全部通过（小幅度修改） | Done | Agent 自审 |
| InReview | acceptance 全部通过（大幅度修改） | Done | 需人工确认 |
| InReview | 验证失败，需返工 | InProgress | - |
| InReview | 需求取消 | Cancelled | - |
| Done | (终态，不可转移) | — | - |
| Cancelled | 需求重新激活 | InSpec | 重新激活后直接锁定 |

**非法转移一律忽略**。例如 Done 状态下收到任何事件，保持 Done 不变。

## 状态判断锚点

### 判断锚点：InProgress → InSpec（真实阻塞）
- 正例：缺少凭据、外部授权或关键环境配置，导致 acceptance 无法继续验证。结论：退回 InSpec，并输出 BLOCKED。
- 反例：单元测试失败由当前代码缺陷引起。结论：保持 InProgress 修复，不得伪装成阻塞。
- 边界例：第三方接口偶发超时，但 acceptance 可通过 mock 或替代验证完成。结论：保持 InProgress，记录风险并继续。
- 结论输出：使用 `DECISION TRACE` 记录阻塞证据、不可继续的原因和下一步动作。

### 判断锚点：InReview → Done 是否需人工确认
- 正例：存在 API/字段契约变更，或单任务改动超过 2000 行。结论：先输出 REVIEW，人工确认后再 Done。
- 反例：小幅度修改且 acceptance 全部通过。结论：可自审后直接 Done。
- 边界例：改动行数未超 2000，但字段默认值变化会影响调用方行为。结论：按大幅度处理，走人工确认。
- 结论输出：使用 `DECISION TRACE` 记录契约变化证据、改动规模和最终状态决策。

## blocked_by 规范

### 语义
表示**阻塞关系**：前置任务未完成，当前任务无法开始。

### 修改权限
InDraft 自由修改；InSpec 可改但需在 recording.md 记录原因；InProgress 及之后只能通过 Change Request。

### 何时使用
前置任务未完成（InSpec/InProgress/InReview）且当前任务依赖其输出时使用。前置任务已 Done 或仅是代码调用关系时不使用。

### 判断锚点：blocked_by 何时不该写
- 正例（应该写）：Task#9 依赖 Task#8 生成的迁移文件，Task#8 未 Done。结论：写入 `blocked_by=[8]`。
- 反例（不该写）：当前任务只是调用已稳定函数，且前置任务已 Done。结论：不写 blocked_by，在 description 说明即可。
- 边界例：前置任务为 InReview，当前任务只依赖其稳定接口。结论：可不写 blocked_by，但需在 description 明确假设；若接口仍可能变动则写入。
- 结论输出：使用 `DECISION TRACE` 记录依赖关系、前置状态和是否写入 blocked_by。

### 合法性检查

Agent 修改 blocked_by 时必须验证：
1. **无循环依赖**：不存在 A→B→C→A 的循环
2. **状态合理**：
   - ✅ InSpec/InProgress/InReview
   - ⚠️ InDraft → 警告并提示先确认前置任务
   - ❌ Done → 提示在任务描述中说明即可
   - ❌ Cancelled → 拒绝

### 判断锚点：循环依赖识别
- 正例：新增依赖后形成 A→B→C→A。结论：拒绝写入并提示重排任务顺序。
- 反例：依赖链为 A→B→C（无回边）。结论：允许写入。
- 边界例：A→B 与 B→A 藏在不同描述中。结论：仍按循环处理并拒绝写入。
- 结论输出：使用 `DECISION TRACE` 记录完整依赖链和合法性检查结果。

### 自动清理

当 blocked_by 中的任务变为 Done：
- Agent 自动从 blocked_by 中移除该 ID
- 在 recording.md 记录："Task#10 阻塞解除：Task#8 已完成"
