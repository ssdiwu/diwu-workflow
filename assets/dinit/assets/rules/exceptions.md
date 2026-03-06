# 异常处理

> **规则约束级别说明**：本文件定义异常处理的核心规则。除非特别标注 `[建议]`，否则都是必须遵守的约束。

## `<private>` 标签约定

用户用 `<private>...</private>` 包裹的内容（密码、密钥、个人敏感信息）不得写入 recording.md 和 task.json。该内容仅在当前对话上下文中使用，不得持久化。

## 需要停止并请求人工帮助的情况

1. **缺少环境配置**:API 密钥、数据库连接、外部服务账号
2. **外部依赖不可用**:第三方 API 宕机、需人工授权的 OAuth、付费服务
3. **验证无法进行**:需要真实用户账号、依赖未部署的外部系统、需特定硬件

## BLOCKED 判定

- **BLOCKED**：问题来自环境、凭据、权限、外部依赖不可用，任务本身需求不变。
- 结论输出统一使用 `DECISION TRACE`（见 templates.md），再输出 BLOCKED 模板。

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

## 阻塞恢复流程

### 环境阻塞恢复
1. 人工提供所需配置/权限
2. Agent 验证环境可用
3. 任务状态: InSpec → InProgress
4. 继续实施
