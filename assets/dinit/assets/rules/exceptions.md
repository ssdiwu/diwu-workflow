# 异常处理

> **规则约束级别说明**：本文件定义异常处理的核心规则。除非特别标注 `[建议]`，否则都是必须遵守的约束。

## `<private>` 标签约定

用户用 `<private>...</private>` 包裹的内容（密码、密钥、个人敏感信息）不得写入 recording.md 和 task.json。该内容仅在当前对话上下文中使用，不得持久化。

## 需要停止并请求人工帮助的情况

1. **缺少环境配置**:API 密钥、数据库连接、外部服务账号
2. **外部依赖不可用**:第三方 API 宕机、需人工授权的 OAuth、付费服务
3. **验证无法进行**:需要真实用户账号、依赖未部署的外部系统、需特定硬件
4. **需求存在问题**:发现原 acceptance 无法实现或存在矛盾

## 二选一判定：BLOCKED vs CHANGE REQUEST

- **BLOCKED**：问题来自环境、凭据、权限、外部依赖不可用，任务本身需求不变。
- **CHANGE REQUEST**：问题来自 acceptance 不可实现、互相矛盾、边界定义错误，需要改需求。
- 结论输出统一使用 `DECISION TRACE`（见 templates.md），再输出对应 BLOCKED 或 CHANGE REQUEST 模板。

### 判断锚点：CR 与 BLOCKED 分界
- 正例：代码实现路径正确，但缺少环境变量、账号权限或外部依赖暂不可用。结论：`BLOCKED`。
- 反例：acceptance 自相矛盾或在当前约束下不可实现。结论：`CHANGE REQUEST`。
- 边界例：外部服务宕机但 acceptance 可通过 mock/回放证据化验证。结论：`CONTINUE`，不升级为 BLOCKED。
- 结论输出：使用 `DECISION TRACE` 记录命中规则、证据和排除项，再输出对应模板。

## 阻塞时的规则

**禁止**:
- 提交 git commit
- 将 `.claude/task.json` 状态设为 Done
- 假装任务已完成

**必须**:
- 在 `.claude/recording.md` 中记录当前进度和阻塞原因
- 将 `.claude/task.json` 任务状态退回 **InSpec**(不是 InDraft)
- 输出 DECISION TRACE 后输出 BLOCKED 模板（见 templates.md），说明需要人工做什么
- 停止任务,等待人工介入

## Change Request 流程

当发现需求存在问题时,不使用 BLOCKED,而是提交 Change Request。

### 触发条件
- 发现原 acceptance 无法实现
  - 例：acceptance 要求"发送邮件验证码"，但项目无 SMTP 依赖且无法添加
- 发现 acceptance 存在矛盾
  - 例：acceptance 同时要求"无需登录可访问"和"需要 JWT 验证才能返回数据"

### CR 编号规则
CR 编号使用全局递增(跨任务连续),方便追踪。

### 输出说明
先输出 `DECISION TRACE`，再使用 CHANGE REQUEST 格式（见 templates.md）输出，最后按 Change Request 记录格式追加到 recording.md。

## 阻塞恢复流程

### 环境阻塞恢复
1. 人工提供所需配置/权限
2. Agent 验证环境可用
3. 任务状态: InSpec → InProgress
4. 继续实施

### 需求变更恢复
1. 人工批准 Change Request
2. Agent 更新 task.json 中的 acceptance
3. 在 recording.md 记录 CR approved
4. 任务状态保持 InSpec → InProgress
5. 按新 acceptance 继续实施
