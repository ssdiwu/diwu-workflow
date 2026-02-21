---
name: dplan
description: 将功能描述转化为 diwu 工作流的 task.json 任务列表。触发场景：规划功能、分解需求、新建任务、plan feature、breakdown tasks。
user-invocable: true
---

# diwu-plan Skill

## 定位

这是 `core-workflow.md` 中"任务规划"章节的自动化实现。输出直接写入项目 `.claude/task.json`（InDraft 状态），不生成中间 markdown 文件。

---

## 执行流程

### Step 1：接收功能描述

用户描述想要实现的功能。

### Step 2：澄清问题

根据功能描述，向用户提出 3-4 个问题，聚焦以下维度：

- **目标**：这个功能解决什么问题？
- **核心操作**：用户的关键操作有哪些？
- **边界**：明确不做什么？
- **成功标准**：怎么算完成？
- **具体例子**：能举一个典型操作的完整例子吗？（用来直接推导 Given/When/Then）

根据用户描述推断合理选项供用户选择。

### Step 3：生成并写入任务

根据回答生成任务列表，追加到 `.claude/task.json`。

### Step 4：任务质量检查（生成后自动执行）

逐条检查每个新生成的任务：

- acceptance 是否使用 Given/When/Then 格式（functional/ui/bugfix 类必须）
- acceptance 是否可验证（无模糊描述如"works correctly"）
- steps 是否自包含（外部凭据有来源路径，无隐式上下文依赖）
- 粒度估算是否合理（是否可能超过 2000 行，如是则提示拆分）
- 是否符合垂直切片（端到端打通，而非按技术层横切）

发现问题时：列出具体问题 + 建议修正，等用户确认后再进入 Step 5。

### Step 5：三视角审查（仅对复杂任务触发）

触发条件：任务 category 为 functional/ui 且 acceptance 超过 3 条，或存在多个 blocked_by。

从三个视角逐一审查：

- **开发视角**：步骤是否清晰可执行？有无技术风险？
- **QA 视角**：acceptance 是否覆盖边界条件和异常路径？
- **业务视角**：这个任务交付后，用户能感知到价值吗？

输出：每个视角的补充建议（如有），用户确认后更新 acceptance/steps。

---

## ID 管理规则

写入前必须：

1. 读取 `.claude/task.json` 中所有任务的最大 `id`
2. 用 glob 匹配读取 `.claude/task_archive*.json` 中所有任务的最大 `id`
3. 取两者最大值 + 1 作为新任务起始 id
4. 严禁 id 复用

---

## 输出格式

每个任务必须包含所有字段：

```json
{
  "id": 1,
  "description": "动词开头的一句话描述",
  "status": "InDraft",
  "acceptance": ["点击按钮后显示确认弹窗（好例子）"],
  "steps": ["实施步骤"],
  "category": "functional | ui | bugfix | refactor | infra",
  "blocked_by": []
}
```

---

## 任务粒度规则

- 预估修改 < 2000 行，否则继续拆分
- 验收条件必须可验证，禁止模糊描述（"works correctly" 是坏例子）
- 每个任务应端到端打通一个功能切片（UI→逻辑→数据），而不是按技术层横切
- 依赖顺序：schema → backend → UI
- `blocked_by` 只在有真实阻塞关系时使用

---

## 边界情况

- `.claude/task.json` 不存在：创建 `{"tasks": []}` 再追加
- `.claude/` 目录不存在：先创建目录
- 某个任务存在明显技术未知量（不确定能否实现）：先生成一个 `category: infra` 的 Spike 任务，acceptance 为"输出调研结论文档"，再生成依赖它的实施任务（`blocked_by: [spike_id]`）

---

## 写入后提示

1. 列出已写入的任务（id + description）
2. 若存在 `blocked_by` 引用，提示：前置任务也是 InDraft，需人工先将其确认为 InSpec，依赖关系才生效
3. 提示用户：确认需求后，告知 Agent 将任务状态改为 InSpec 即可开始实施

---

## 不做的事

- 不生成中间 PRD markdown 文件
- 不自动将任务改为 InSpec
- 不引入 AGENTS.md / learnings 机制

---

## 完整示例

**用户输入**：我想做一个笔记标签功能，可以给笔记打标签、按标签筛选。

**澄清问题**：

1. 标签的创建方式？
   A. 输入时自动创建新标签
   B. 先在标签管理页创建，再关联
   C. 两种都支持

2. 筛选逻辑？
   A. 选中多个标签时取交集（AND）
   B. 选中多个标签时取并集（OR）

3. 标签数据存储？
   A. 存在现有数据库，新增 tags 表
   B. 存在笔记字段里（JSON 数组）

**用户回答**：1A 2B 3A

**写入 task.json**：

```json
{
  "tasks": [
    {
      "id": 5,
      "description": "创建 tags 表和笔记-标签关联表",
      "status": "InDraft",
      "acceptance": [
        "tags 表包含 id、name、created_at 字段",
        "note_tags 关联表包含 note_id、tag_id 字段",
        "migration 脚本可无错执行"
      ],
      "steps": ["编写 migration 文件", "运行 migration 验证"],
      "category": "infra",
      "blocked_by": []
    },
    {
      "id": 6,
      "description": "实现标签 CRUD API",
      "status": "InDraft",
      "acceptance": [
        "POST /tags 创建标签，返回 201 和新标签数据",
        "GET /tags 返回所有标签列表",
        "DELETE /tags/:id 删除标签，同时清除关联关系"
      ],
      "steps": ["实现 tags controller", "实现 note-tag 关联接口"],
      "category": "functional",
      "blocked_by": [5]
    },
    {
      "id": 7,
      "description": "实现笔记标签 UI：打标签和按标签筛选",
      "status": "InDraft",
      "acceptance": [
        "笔记编辑页可输入标签名，回车后自动创建并关联",
        "笔记列表页顶部显示标签筛选栏",
        "选中多个标签时取并集展示笔记"
      ],
      "steps": ["标签输入组件", "标签筛选栏组件", "列表筛选逻辑"],
      "category": "ui",
      "blocked_by": [6]
    }
  ]
}
```

**写入后提示**：

已写入 3 个任务：
- Task#5：创建 tags 表和笔记-标签关联表
- Task#6：实现标签 CRUD API（blocked_by Task#5）
- Task#7：实现笔记标签 UI（blocked_by Task#6）

注意：Task#6 和 Task#7 的前置任务也是 InDraft 状态，需人工先将 Task#5 确认为 InSpec，依赖关系才生效。

确认需求后，告知 Agent 将任务状态改为 InSpec 即可开始实施。
