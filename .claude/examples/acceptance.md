# acceptance 示例

## 正例

### 示例 1：用户登录功能
```
Given 用户在 /login 页面输入 email="test@example.com" 和 password="Pass123!"
When 点击"登录"按钮
Then 页面跳转到 /dashboard 且 localStorage 中存在 key="auth_token" 且 token 有效期为 7 天
```

### 示例 2：邮件验证码发送
```
Given 新用户完成注册表单提交
When 系统调用 sendVerification(email)
Then Redis 中存在 key=verify:{email}，value=6位数字，TTL=600s
```

### 示例 3：API 错误处理
```
Given SMTP 服务不可用
When 调用 sendVerification()
Then 抛出 EmailServiceError 且不写入 Redis
```

## 反例

### 反例 1：主观描述（无法验证）
```
Given 用户登录
When 提交表单
Then 登录成功
```
**问题**：Given 没有具体页面和数据状态；Then 是主观描述，不是可断言的系统状态。

### 反例 2：缺少前置条件
```
When 点击提交按钮
Then 跳转到首页
```
**问题**：缺少 Given，不知道初始状态是什么。

### 反例 3：Then 子句过于抽象
```
Given 用户在注册页面
When 提交表单
Then 系统处理注册请求
```
**问题**：Then 无法转换为 `expect()` 断言，不知道"处理"的具体结果是什么。

## 边界例

### 边界例 1：多个 Then 子句（接近上限）
```
Given 用户在 /checkout 页面选择商品 A 和 B
When 点击"确认订单"
Then 订单状态为 pending 且库存扣减 2 件且发送确认邮件
```
**判断**：3 个 Then 子句，处于上限边界，可接受。如果再多一个应拆分。

### 边界例 2：infra 类任务的简化格式
```
构建产物不超过 500KB
```
**判断**：infra/refactor 类任务可使用简单描述，不强制 GWT 格式。

### 边界例 3：依赖外部状态的验证
```
Given 第三方支付接口返回 status=success
When 系统接收回调
Then 订单状态更新为 paid 且发送确认短信
```
**判断**：Given 依赖外部系统，需在验证脚本中 mock 或使用沙箱环境。
