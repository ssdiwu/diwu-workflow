# 格式模板与参数

## BLOCKED 格式

```
BLOCKED - 需要人工介入

当前任务: Task#3 - 邮件验证码发送
任务描述: 用户注册后需要验证邮箱，SMTP 不可用时必须返回明确错误而非静默失败

已完成的工作:
- src/services/email.ts 的 sendVerification() 函数已实现
- 单元测试通过（mock SMTP，3/3 passed）

阻塞原因:
- 调用 sendVerification() 时 SMTP_HOST 环境变量未设置
- 已确认 .env.example 中有该字段，但 .env 中缺失
- 无法在本地验证真实邮件发送，acceptance 条件 #1 无法证据化

需人工帮助:
1. 在 .env 中配置 SMTP_HOST、SMTP_PORT、SMTP_USER、SMTP_PASS
2. 或提供测试用 SMTP 服务（如 Mailtrap）凭据，见 doc/runbook.md §2.1

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

等待验收: Task#10
已超前完成: Task#11, Task#12, Task#13 (3/3)

请验收 Task#10:
- 通过 → 可继续超前实施 Task#14-16
- 失败 → 需评估 Task#11-13 的影响并修复
```

## REVIEW 请求格式

```
REVIEW - 请求人工审查

Task#5: 用户权限中间件
修改范围: src/middleware/auth.ts（新增 89 行），src/routes/api.ts（修改 3 处），tests/middleware/auth.test.ts（新增 67 行）

验收验证:
- [x] Given 未登录用户访问 /api/profile When 发送 GET 请求 Then 返回 401 + {"error":"Unauthorized"} — auth.test.ts:23 passed
- [x] Given 携带有效 JWT 的请求 When 中间件验证 Then req.user 被注入用户对象 — auth.test.ts:45 passed
- [x] Given 过期 JWT When 中间件验证 Then 返回 401 + {"error":"Token expired"} — auth.test.ts:67 passed

等待: 人工确认后将标记为 Done
```

## recording.md Session 格式

```markdown
---
## Session 2026-02-17 14:30:22

### 上下文恢复
- 上次任务: Task#1 (InProgress)
- Git 状态: clean
- 待批准 CR: 无

### Task#1: 用户登录功能 → Done

**实施内容**:
- 完成 src/auth/login.ts 核心逻辑
- 添加错误处理和 token 存储
- 添加单元测试

**验收验证** (自动化):
- [x] 输入正确密码后跳转首页 (npm test passed)
- [x] 错误密码显示提示 (npm test passed)
- [x] 登录状态保持 7 天 (手动验证通过)

**验证方法**: 运行 .claude/checks/task_1_verify.sh

**提交**: commit abc123f

### 下一步
Task#2: 密码重置功能

---
```

## Change Request 记录格式

```markdown
---
## Session 2026-02-18 10:00:35

### Task#2: 密码重置 → BLOCKED

**Change Request #2**:
- **原因**: 发现邮件服务依赖不稳定
- **建议**: 增加"手机验证码重置"作为备选方案
- **详细修改**:
  - [删除] "通过邮件发送重置链接"
  - [新增] "通过手机验证码验证身份"
  - [新增] "支持邮件和手机两种方式"
- **影响**: acceptance 需新增 2 条,预计额外 1 天工作量
- **状态**: pending

**需人工介入**:
请批准 CR#2,或提供稳定的邮件服务配置

---
```

## 可调参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 超前上限 | 5 | 最多同时超前实施的任务数 |
| 归档阈值 | 20 | task.json 中 Done/Cancelled 任务超过此数触发归档 |
| 子代理并发数 | 3 | 0=禁用子代理，1=串行子代理，N≥2=最多N个并发子代理 |

**子代理并发数读取优先级**（从高到低）：
1. 项目 `.claude/CLAUDE.md` 中的「子代理并发数」字段
2. 本文件可调参数表（默认 3）

## 验证脚本模板

**task_\<id\>_verify.sh**：
```bash
#!/bin/bash
npm run build || exit 1
npm test -- <test-file> || exit 1
echo "Task#N 验证通过"
exit 0
```

**smoke.sh**：
```bash
#!/bin/bash
[ -d "node_modules" ] || npm install
npm run build || exit 1
npm run lint || exit 1
echo "基线验证通过"
exit 0
```
