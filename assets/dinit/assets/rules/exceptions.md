# 异常处理

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

### 案例：SMTP 凭据缺失
- 场景：acceptance 要求发邮件，代码实现完成，但 `.env` 缺少 SMTP 配置。
- 结论：`BLOCKED`。理由是实现路径成立，阻塞来自环境配置，不是需求定义错误。

### 案例：acceptance 互相矛盾
- 场景：同一任务同时要求“无需登录可访问”和“必须 JWT 验证后返回数据”。
- 结论：`CHANGE REQUEST`。理由是规则冲突，必须先修改需求再继续实施。

### 案例：外部服务宕机但可 mock 验证
- 场景：第三方服务临时不可用，但关键 acceptance 可由 mock/录制回放完成证据化验证。
- 结论：`CONTINUE`（不进入 BLOCKED）。仅当 acceptance 无法证据化时才升级为 BLOCKED。

## 阻塞时的规则

**禁止**:
- 提交 git commit
- 将 `.claude/task.json` 状态设为 Done
- 假装任务已完成

**必须**:
- 在 `.claude/recording.md` 中记录当前进度和阻塞原因
- 将 `.claude/task.json` 任务状态退回 **InSpec**(不是 InDraft)
- 输出阻塞信息,说明需要人工做什么
- 停止任务,等待人工介入

## 阻塞信息格式

环境/依赖问题时先输出 `DECISION TRACE`，再输出 BLOCKED 格式。完整格式见 templates.md。

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

## 回退处理

### 触发条件
阻塞任务验收失败,已超前完成的任务可能受影响。

**验收通过**：阻塞任务 → Done，超前任务逐个 InReview → Done，recording.md 记录解除。
**验收失败**：人工决定回退方式，Agent 执行并重新验证超前任务：
- `revert`：超前任务已 push 到远端，需要撤销公开提交
- `reset --soft`：超前任务只在本地，保留代码改动但撤销 commit，便于修改后重新提交
- `修改`：超前任务代码仍然有效，只需调整以适配阻塞任务的新实现
