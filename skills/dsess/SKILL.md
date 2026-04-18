---
name: dsess
description: Session 生命周期管理——启动（Preflight 5 步）、上下文恢复、归档检查、任务选择、持续运行模式、Session 结束协议。触发场景：(1) Session 启动或结束，(2) 选择下一个任务，(3) 判断是否续跑，(4) 归档旧任务，(5) 用户说"session"、"启动"、"下一步"、"续跑"、"归档"。注意：写 recording 记录用 drecord skill。
---

# diwu-session

Session 生命周期管理：从启动到结束的完整协议。

---

## Session 启动（必须按顺序执行）

**执行顺序约束**：Step 1-4 串行（Preflight 失败则停止）；Step 5 可选；Step 2/3 的 task.json 读取可合并。

### 1. Preflight 检查

**基线验证**：运行 smoke.sh（如存在），验证基线环境。

**三唯一确认**：
- 唯一主线目录：本轮任务唯一允许承接主要实现和验收的目录
- 唯一运行入口：本轮要验证主链是否真的经过的实际启动/调用入口
- 唯一 canonical：当前必须以其为准的说明、接口或规则文件

**5 问开工检查**：
1. 这件事能不能直接做，还是先探索/先验证/先写最小规格？
2. 本次唯一主线目录、唯一运行入口、唯一 canonical 是什么？
3. 当前最可能先判断错的地方是什么？
4. 进入实施前最少要拿到哪些判别依据？
5. 完成后用哪类高等级证据判断结果成立？

**误判表预加载**：进入实施前先看当前现象是否落在历史高频误判中（project-pitfalls.md 或 exceptions.md）。

**其他检查**：git status 确认工作区状态；recording/ 最新 session 中是否有未解决阻塞记录。

### 2. 上下文恢复
- **优先**读取 continue-here.md（如存在），读完后删除
- 否则读取最新 1-2 个 session 文件
- 读取 decisions.md（如存在）
- 运行 git log --oneline -20

### 3. 归档检查
- 统计 task.json 中 Done/Cancelled 任务数量
- 超过阈值（默认 20）时触发归档
- 更新 task.json 只保留活跃任务

### 4. 任务选择策略
- **优先恢复** InProgress 任务
- 否则选第一个 InSpec 任务，检查 blocked_by：
  - 为空/不存在 / 全部 Done → 可开始
  - 存在 InReview 且超前未达上限 → 可超前（标记 InReview + 立即 commit）
  - 达到超前上限 → 输出 PENDING REVIEW
- **禁止**选择 InDraft 任务

### 5. 环境初始化（可选）
- 运行 init.sh（如存在）
- 运行基线测试（build/lint），失败则先修复

---

## 持续运行模式（continuous_mode）

| 模式 | 行为 |
|------|------|
| `true`（默认） | 任务 Done 后自动选择下一个可执行任务继续 |
| `false` | 每完成一个任务即停止，输出完成摘要等待人工介入 |

**关闭时仍续跑的例外**：当前任务 InProgress（断点恢复优先） / 存在未提交变更（防丢失）

**关闭时停止边界**：Done（小幅度）→ 停止+摘要；Done（大幅度）→ REVIEW；PENDING REVIEW；BLOCKED；无更多任务 → CONTINUOUS_MODE_COMPLETE

**超前实施回退方式**：revert（已 push）/ reset --soft（仅本地）/ 修改（代码仍有效）

---

## Session 结束

在 session 结束前（含 context window 接近上限时）：

1. 确保所有代码变更已提交
2. 写入 recording/session 文件（必须运行 date 获取真实时间戳），记录 Session 标题、处理的任务及状态、验收验证结果、下次应该做什么
3. 如有重大设计决策，追加到 decisions.md
4. 确保 task.json 反映最新状态

> **详细 recording 格式和踩坑记录格式见 drecord skill**

### continuous_mode=false 时的 Session 结束变体

**正常停止**（Done 且无 InProgress）：执行标准步骤 1-4，不自动选下一任务，输出摘要。
**开启后恢复**（false→true）：下次 Stop hook 触发时恢复自动续跑，无需重启 session。

### Context Window 管理
- context window 接近上限时会自动压缩，允许无限期继续工作
- 不要因 token 预算担忧而提前停止任务
- 始终保持最大程度的自主性
