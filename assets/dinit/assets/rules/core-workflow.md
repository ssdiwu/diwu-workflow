# Session 工作流

## Session 启动（必须按顺序执行）

每个新 session 必须先完成以下步骤，然后才能开始实现任务：

### 1. Preflight 检查
- 运行 `.claude/checks/smoke.sh`（如存在），验证基线环境
- 检查 recording.md 中是否有 pending Change Requests
- 运行 `git status`，确认工作区状态

### 2. 上下文恢复
- 读取 `.claude/recording.md`，了解上一个 session 的工作和注意事项
  - 统计完整 session 记录数（`## Session YYYY-MM-DD HH:MM:SS` 格式，不含 Start/End 快照）
  - 超过 5 条时，立即执行 recording.md 归档（见 file-layout.md 归档执行步骤）
- 检查 `.claude/task.json` 中 Done/Cancelled 任务数，超过 20 条时执行 task.json 归档
- 读取 `.claude/decisions.md`（如存在），了解历史设计决策
- 运行 `git log --oneline -20`，了解最近的代码变更历史

### 3. 任务选择策略
- 读取 `.claude/task.json`，了解所有任务的当前状态
- **优先恢复** `status: "InProgress"` 的任务（中断的任务）
- 否则选择第一个 `status: "InSpec"` 的任务，并检查 blocked_by：
  - **blocked_by 为空或不存在** → 无阻塞，可开始
  - **blocked_by 全部 Done** → 阻塞已解除，可开始
  - **blocked_by 存在 InReview 且超前<5** → 可超前实施（标记为超前）
    - 超前完成的任务标记为 **InReview**，立即创建 git commit
    - recording.md 记录："Task#N (blocked_by Task#M, 超前 X/5, commit: abc123)"
    - 完成第 5 个超前任务后输出 PENDING REVIEW，等待阻塞任务验收
  - **其他情况** → 跳过，选择下一个任务
- **禁止选择** `status: "InDraft"` 的任务（需人工先确认）
- 选择优先级：无 blocked_by 的任务优先，基础功能优先

### 判断锚点：任务选择与超前实施
- 正例：Task#21 为 InSpec，`blocked_by=[20]`；Task#20 为 InReview，当前超前计数 2/5。结论：可超前实施 Task#21，完成后标记 InReview 并提交，计数更新为 3/5。
- 反例：Task#21 为 InSpec，`blocked_by=[20]`；Task#20 为 InProgress，或当前已超前 5/5。结论：跳过 Task#21，选择下一个可执行任务。
- 边界例：`blocked_by=[18,20]`，其中 Task#18 已 Done、Task#20 为 InReview，当前超前 4/5。结论：先清理已 Done 依赖，再允许超前至 5/5；达到上限后输出 PENDING REVIEW。
- 结论输出：使用 `DECISION TRACE` 记录 task.json 状态、blocked_by 明细和超前计数。

### 4. 环境初始化（可选）
- 运行 `.claude/init.sh` 启动开发环境（如需要）
- 运行项目的基线测试（build/lint），确认系统处于正常状态
- 如果基线测试失败，优先修复，然后再开始新任务

### 判断锚点：基线失败时先修基线还是继续
- 正例：`smoke.sh` 中定义的 build 或 lint 失败。结论：先修复基线，再开始新任务。
- 反例：明知 build/lint 失败仍直接将任务设为 InProgress 并继续开发。结论：违规。
- 边界例：失败项来自不在 `smoke.sh` 范围内的可选集成测试。结论：可记录风险后继续，但不得声称“基线通过”。
- 结论输出：使用 `DECISION TRACE` 记录失败命令、日志证据、继续或暂停的理由。

---

## 任务规划

### 触发条件
- 用户在讨论想法、需求、功能设计
- `.claude/task.json` 为空或用户明确要求分解任务
- 用户描述了一个较大的功能，需要拆分为可执行步骤

### 分解流程

**需求精炼（任务描述模糊时触发）**：
- 每次只问一个问题，理解目的、约束、成功标准
- 提出 2-3 个方案并给出推荐，获得确认后再写 task.json

**草案阶段（InDraft）**：
1. **提炼**：从讨论中识别可执行的功能点
2. **拆分**：每个任务一句话可描述、一个 session 可完成
3. **定义验收**：为每个任务明确验收条件（可验证的标准）
4. **排序**：识别依赖关系，基础功能排前面
5. **展示**：展示分解结果，包含任务标题（title）、任务描述（description）、验收条件、实施步骤
6. **写入**：写入 `.claude/task.json`，状态为 `InDraft`

**锁定阶段（InSpec）**：
- **确认**：等人工确认后，Agent 将状态改为 `InSpec`
- **锁定**：从此刻起，Agent 只能修改 status 字段
- **变更**：如需修改需求，走 Change Request 流程

**SDD 规范驱动开发**：
- `.doc/` 存在时，实施前必须先补充或更新对应规范文档，不可先实施后补文档
- 架构决策同步记录到 `.doc/adr/`（调用 `/diwu-adr`）

### 任务粒度标准
- 预估修改代码 < 2000 行（超过则继续拆分）
- 有明确的验收标准（`acceptance` 字段，GWT 格式，可证据化验证）
- 有清晰的实施步骤（`steps` 字段）
- 不依赖未完成的其他任务，或依赖已在 blocked_by 字段中标注

### task.json 写入规则
- 新任务状态一律为 `InDraft`
- ID 递增，不复用已有 ID
- category 可选值：functional / ui / bugfix / refactor / infra
- 如果 `.claude/task.json` 已有任务，新任务追加到列表末尾
- 必须包含 `acceptance` 字段（验收条件数组，GWT 格式，格式规范与示例见 core-states.md）
- 如有依赖关系，使用 `blocked_by` 字段标注（可选）

- steps 必须自包含：外部系统凭据写明来源文件路径（如"凭据见 `/absolute/path/to/project/doc/runbook.md §1.1`"），代码路径写绝对路径，不依赖会话上下文

---

## 任务实施

InSpec → InProgress → InReview → Done 完整流程：

1. 将选定任务状态改为 `InProgress`
2. 仔细阅读任务的任务描述、验收条件、实施步骤
3. 按照项目既有的代码模式实现功能（如有测试框架，建议顺序：先写验收测试框架 → 单元测试 → 实现）
4. 文件路径修改后必须 grep 验证无残留再继续
5. 实现完成后，按本文件"验证要求"章节进行验证
6. 验证通过后，将状态改为 `InReview`
7. 根据分层审查规则：
   - 小幅度修改：Agent 自审后标记 Done
   - 大幅度修改：输出 REVIEW 请求，等待人工确认

**大幅度修改判定**：满足以下任一条件即为大幅度修改：修改了原有 API 规范或字段定义；单次任务修改代码行数超过 2000 行。其余 Agent 自审即可。

### 判断锚点：大幅度修改判定
- 正例：接口响应字段发生变更，或单任务代码改动超过 2000 行。结论：大幅度修改，必须输出 REVIEW 请求并等待人工确认。
- 反例：只修复内部实现 bug，API/字段不变，改动 120 行。结论：小幅度修改，可自审后 Done。
- 边界例：改动 600 行但跨多个核心模块并引入兼容层。结论：若 API/字段无变化可按小幅度执行；只要契约变化即强制按大幅度处理。
- 结论输出：使用 `DECISION TRACE` 记录 API 变更证据与 `git diff --stat` 数据。

**自审原则**：只实现了 acceptance 要求的，不多不少；没有引入技术债或安全问题。
- ❌ 顺手重构了周边函数、添加了未要求的日志、提取了"以后可能用到"的工具函数

**Change Request 流程**（执行 InSpec 任务时发现需求问题）：
1. **创建 CR**：在 recording.md 中记录 Change Request
2. **保持状态**：任务状态保持 InSpec（不退回 InDraft）
3. **停止实施**：输出 CHANGE_REQUEST 信息，等待批准
4. **批准后**：更新 task.json 中的验收条件，继续实施

### 提交规范

**提交时机**：只有任务状态到达 Done 时才提交；超前任务完成时标记 InReview 并立即提交（最多 5 次），阻塞解除后标记 Done。

**commit message 格式**：
- 常规：`[Task#N] 任务标题 - completed`
- 超前：`[Task#N] 任务标题 - completed (超前实施 X/5, blocked_by Task#M)`

**提交内容**：代码变更 + `.claude/task.json` + `.claude/recording.md`，同一个 commit。

**force push**：执行前必须先 `git fetch origin` 并确认远端无未合并变更，有差异须先与用户确认。

### 子代理策略

**并行条件**（同时满足才可并行）：
- 问题域不相交（不读写同一业务模块）
  - ✓ 子代理A 实现 `src/auth/`，子代理B 实现 `src/payment/`（不同域）
  - ❌ 两个子代理都需要修改 `src/models/user.ts`（共享写文件）
- 无共享写文件（子代理永远不写 task.json，只写自己的产出文件）

**串行条件**（满足任一则串行）：
- 后一步依赖前一步的输出
- 需要积累上下文的实施类任务

### 判断锚点：并行与串行选择
- 正例：子代理 A 仅修改 `src/auth/`，子代理 B 仅修改 `src/payment/`，无共享写文件。结论：可并行。
- 反例：两个子代理都要修改 `src/models/user.ts` 或同一迁移文件。结论：必须串行。
- 边界例：代码目录不同，但都依赖同一个生成产物（如 `openapi.json`）。结论：先串行生成共享产物，再并行执行剩余步骤。
- 结论输出：使用 `DECISION TRACE` 记录模块边界、共享写文件检查结果和执行顺序。

**Coordinator Pattern**：task.json 的状态更新始终由主代理负责，子代理通过返回值把结果传回主代理。

**启动仪式**（所有子代理，强约束）：
1. 读取 `.claude/recording.md`（关注 pending CR、历史阻塞、回退记录）
2. 读取相关 task 的 title、description、acceptance、steps

**子代理并发数**：读取优先级与行为定义见 templates.md 可调参数。

---

## 验证要求

**核心原则**：**未验证 = 未完成**。所有 acceptance 条件逐条验证通过后才能标记 InReview，验证方法和结果记录在 recording.md。

### 1. 自动化验证（推荐）
脚本位置：`.claude/checks/task_<id>_verify.sh`，返回 0 成功 / 非0 失败。模板见 templates.md。

### 2. 手动验证（不可自动化时）
场景：实机测试、UI 交互、需要真实账号。Agent 提供步骤清单 → 人工执行反馈 PASS/FAIL → Agent 标记状态。

### 3. 人工审查（大幅度修改）
Agent 完成实现和验证后输出 REVIEW 请求，等待人工确认。

### 基线验证（smoke.sh）
位置：`.claude/checks/smoke.sh`，验证基线环境（依赖/构建/lint）。模板见 templates.md。

### 测试分层
- 大幅度修改：浏览器测试工具（Playwright/Puppeteer MCP）验证功能和 UI
- 小幅度修改：lint/build/单元测试

### 验证失败处理
验证失败时任务状态保持 InProgress，修复后重新验证。

---

## Session 结束

在 session 结束前（包括 context window 接近上限时）：

1. 确保所有代码变更已提交
2. 更新 `.claude/recording.md`，记录本次 session：
   - Session 时间戳（运行 `date '+%Y-%m-%d %H:%M:%S'` 获取真实时间，禁止伪造）
     - ❌ `## Session 2026-02-26 （续）` — 手写占位符，违规
     - ✅ 先运行 `date` → 得到 `2026-02-26 16:49:42` → 写 `## Session 2026-02-26 16:49:42`
   - 处理的任务及状态
   - 验收验证结果
   - Change Request（如有）
   - 下次应该做什么
3. 如有重大设计决策，追加到 `.claude/decisions.md`（文件不存在时创建）：
   ```markdown
   ## DEC-NNN YYYY-MM-DD 决策标题
   **背景**：[触发这个决策的问题]
   **决策**：[选择了什么]
   **备选方案**：[考虑过但未选的]
   **理由**：[为什么选这个]
   ```
4. 确保 `.claude/task.json` 反映最新的任务状态

### 判断锚点：何时写 decisions.md
- 正例：从多个方案中选定设计方向（如"引入 README 索引层"代替全量 glob 扫描）。结论：写 decisions.md。
- 反例：记录本次 session 做了什么、下一步计划。结论：写 recording.md，不写 decisions.md。
- 边界例：重构某命令的定位（如"/ddemo 从分析报告改为落地文档生成器"）。结论：写 decisions.md（定位变更是设计决策）。

### Context Window 管理
- context window 会在接近上限时自动压缩，允许无限期继续工作
- 不要因为 token 预算担忧而提前停止任务
- 始终保持最大程度的自主性，完整完成任务

归档触发条件与执行步骤见 `file-layout.md`。
