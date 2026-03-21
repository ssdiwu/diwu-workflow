# session_record 示例

## 正例

### 示例 1：完整的任务实施记录
```markdown
---
## Session 2026-03-15 14:23:10

### Task#5: 实现用户登录接口 → Done

**实施内容**:
- 在 /absolute/path/to/src/routes/auth.ts 实现 POST /api/login
- 使用 bcrypt 验证密码，jsonwebtoken 生成 token
- token 有效期设为 7 天

**验收验证**:
- [x] Given 用户提交正确的 email+password When POST /api/login Then 返回 200 且 body 包含 token 字段 (运行 curl 测试通过)
- [x] Given 用户提交错误密码 When POST /api/login Then 返回 401 且错误信息为'密码错误' (单元测试通过)

**提交**: commit a3f2b91

### 下一步
Task#6: 实现用户个人资料页面

---
```

### 示例 2：超前实施记录
```markdown
---
## Session 2026-03-16 09:15:42

### Task#21: 实现订单详情页面 → InReview (超前实施 3/5)

**实施内容**:
- Task#21 blocked_by Task#20 (InReview)
- 超前实施：假设 Task#20 的 API 接口稳定
- 实现订单详情页面组件和路由

**验收验证**:
- [x] Given 用户访问 /order/123 When 页面加载 Then 显示订单详情 (浏览器测试通过)

**提交**: commit b7e4c22

**注意**: Task#20 验收通过后需确认 API 接口无变化

### 下一步
等待 Task#20 验收，或继续超前实施 Task#22 (当前 3/5)

---
```

### 示例 3：阻塞记录
```markdown
---
## Session 2026-03-17 16:30:55

### Task#8: 集成支付接口 → InSpec (BLOCKED)

**已完成的工作**:
- 实现支付请求封装函数
- 编写单元测试框架

**阻塞原因**:
- 缺少支付平台的 API 密钥
- 需要人工在支付平台后台生成密钥并配置到 .env

**需人工帮助**:
1. 登录支付平台后台 https://pay.example.com
2. 生成 API 密钥
3. 将密钥写入 /absolute/path/to/.env 的 PAYMENT_API_KEY 字段

**解除阻塞后**:
- 任务将从 InSpec 恢复到 InProgress

### 下一步
等待人工配置密钥

---
```

## 反例

### 反例 1：缺少时间戳
```markdown
## Session 2026-03-15 （续）

### Task#5: 实现用户登录接口 → Done
```
**问题**：时间戳不完整，应运行 `date '+%Y-%m-%d %H:%M:%S'` 获取真实时间。

### 反例 2：验收验证缺少证据
```markdown
**验收验证**:
- [x] 登录功能正常
- [x] 错误处理正确
```
**问题**：验收条目不符合 GWT 格式，且缺少验证方法（如何验证的？）。

### 反例 3：下一步过于模糊
```markdown
### 下一步
继续开发
```
**问题**：下一步应明确具体任务编号或工作内容。

## 边界例

### 边界例 1：无实质性工作的 session
```markdown
## Session 2026-03-18 10:05:20

### 讨论
与用户讨论 Task#10 的实现方案，确定使用 Redis 缓存。

### 下一步
Task#10: 实现缓存层
```
**判断**：有实质性讨论和方案决策，应写入 session 文件。

### 边界例 2：只读文件无修改
用户问："Task#5 的状态是什么？"，Agent 读取 task.json 后回答。
**判断**：无实质性工作（无 task 状态变化、无 git commit、无文件修改、无重要决策），不写入 session 文件。

### 边界例 3：插件维护工作
修改了 commands/ddemo.md 和 dprd.md，对话即将结束。
**判断**：有文件修改，必须主动写入 recording.md，不能依赖 Stop hook（Stop hook 只在有 InProgress 任务时触发）。
