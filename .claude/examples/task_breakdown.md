# task_breakdown 示例

## 正例

### 示例 1：用户注册功能拆分
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "实现邮箱格式校验",
      "description": "用户注册时需要校验邮箱格式。使用正则表达式验证，不合法时返回明确错误信息。",
      "acceptance": [
        "Given 用户输入 email='test@example.com' When 调用 validateEmail() Then 返回 true",
        "Given 用户输入 email='invalid' When 调用 validateEmail() Then 返回 false 且错误信息为'邮箱格式不正确'"
      ],
      "steps": [
        "1. 在 /absolute/path/to/src/utils/validator.ts 实现 validateEmail(email: string): boolean",
        "2. 运行 /absolute/path/to/.claude/checks/task_1_verify.sh 验证"
      ],
      "category": "functional",
      "status": "InDraft"
    },
    {
      "id": 2,
      "title": "实现邮件验证码发送",
      "description": "用户注册后需要验证邮箱。调用 SMTP 服务发送 6 位验证码，验证码有效期 10 分钟，存储在 Redis 中。",
      "acceptance": [
        "Given 新用户完成注册表单提交 When 系统调用 sendVerification(email) Then Redis 中存在 key=verify:{email}，value=6位数字，TTL=600s"
      ],
      "steps": [
        "1. 在 /absolute/path/to/src/services/email.ts 实现 sendVerification()",
        "2. 凭据见 /absolute/path/to/doc/runbook.md §2.1"
      ],
      "category": "functional",
      "blocked_by": [1],
      "status": "InDraft"
    }
  ]
}
```

### 示例 2：任务粒度适中
```json
{
  "id": 5,
  "title": "实现用户登录接口",
  "description": "提供 POST /api/login 接口，验证用户名密码，返回 JWT token。",
  "acceptance": [
    "Given 用户提交正确的 email+password When POST /api/login Then 返回 200 且 body 包含 token 字段"
  ],
  "steps": [
    "1. 在 /absolute/path/to/src/routes/auth.ts 实现 POST /api/login",
    "2. 使用 bcrypt 验证密码",
    "3. 使用 jsonwebtoken 生成 token"
  ],
  "category": "functional",
  "status": "InDraft"
}
```

## 反例

### 反例 1：任务粒度过大
```json
{
  "id": 10,
  "title": "实现完整的用户系统",
  "description": "包括注册、登录、找回密码、个人资料管理等功能。",
  "acceptance": ["用户系统功能完整"],
  "category": "functional",
  "status": "InDraft"
}
```
**问题**：任务范围过大，无法预估工作量，acceptance 过于抽象，应拆分为多个独立任务。

### 反例 2：acceptance 缺失 GWT 格式
```json
{
  "id": 11,
  "title": "实现邮件发送",
  "acceptance": ["邮件能发送成功"],
  "category": "functional",
  "status": "InDraft"
}
```
**问题**：acceptance 不符合 Given/When/Then 格式，无法验证。

### 反例 3：steps 使用相对路径
```json
{
  "id": 12,
  "title": "添加日志功能",
  "steps": [
    "1. 在 src/utils/logger.ts 实现日志函数",
    "2. 运行 checks/verify.sh"
  ],
  "category": "infra",
  "status": "InDraft"
}
```
**问题**：steps 使用相对路径，应使用绝对路径确保可执行。

## 边界例

### 边界例 1：blocked_by 引用 InReview 任务
```json
{
  "id": 20,
  "title": "实现订单列表页面",
  "blocked_by": [19],
  "status": "InSpec"
}
```
其中 Task#19 状态为 InReview。
**判断**：如果超前计数未达上限，可超前实施 Task#20；达到上限则跳过。

### 边界例 2：infra 类任务的简化 acceptance
```json
{
  "id": 25,
  "title": "优化构建产物大小",
  "acceptance": ["构建产物不超过 500KB"],
  "category": "infra",
  "status": "InDraft"
}
```
**判断**：infra/refactor 类任务可使用简单描述，不强制 GWT 格式。

### 边界例 3：任务改动接近 2000 行
```json
{
  "id": 30,
  "title": "重构用户模块",
  "description": "预计改动 1800 行代码，不改变 API 接口。",
  "category": "refactor",
  "status": "InDraft"
}
```
**判断**：接近 2000 行边界，如果实际改动超过 2000 行或涉及 API 变更，需走人工确认流程。
