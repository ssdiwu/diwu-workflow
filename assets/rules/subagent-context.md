# 子代理上下文

> 本文件由 SubagentStart hook 注入，仅包含子代理执行任务所需的最小上下文。

## 启动仪式（强约束）

1. 读取 `.claude/recording.md`（关注 pending CR、历史阻塞）
2. 读取当前任务的 title、description、acceptance、steps

## 关键文件路径

```
.claude/
├── task.json          # 当前任务列表（只读，不写）
├── recording.md       # Session 进度记录
├── decisions.md       # 设计决策记录
└── checks/
    └── task_<id>_verify.sh  # 任务验证脚本
```

| 路径 | 用途 |
|------|------|
| `.claude/task.json` | 当前所有任务的状态和内容 |
| `.claude/recording.md` | Session 进度记录，含 pending CR 和历史阻塞 |
| `.claude/decisions.md` | 重大设计决策，供快速检索历史决策理由 |
| `.claude/checks/task_<id>_verify.sh` | 任务专属验证脚本 |

## task.json 结构

**字段说明**：

| 键名 | 含义 | 说明 |
|------|------|------|
| `id` | 任务编号 | 从 1 开始递增，永不复用 |
| `title` | 任务标题 | 一句话描述（动词开头） |
| `description` | 任务描述 | 背景 + 关键约束 |
| `status` | 任务状态 | 见下方状态定义 |
| `acceptance` | 验收条件 | Given/When/Then 格式数组 |
| `steps` | 实施步骤 | 关键步骤，含绝对路径 |
| `category` | 任务分类 | functional / ui / bugfix / refactor / infra |
| `blocked_by` | 前置任务 | （可选）阻塞依赖的任务 ID 数组 |

**状态定义**：

| 状态 | 含义 |
|------|------|
| InDraft | 草稿中，需人工确认后才可实施 |
| InSpec | 需求已锁定，可开始实施 |
| InProgress | 实施中 |
| InReview | 实现完成，等待验证 |
| Done | 已完成，验证通过 |
| Cancelled | 已取消 |

## 协调约束

- **不写 task.json**：状态更新由主代理负责，子代理只写自己的产出文件
- **结果传回主代理**：通过返回值传递，不直接修改共享状态
- **专业化分工**：
  - 探索类：只读文件/grep，不写任何文件，用 haiku
  - 验证类：只运行测试/检查 acceptance，不写代码
  - 实施类：只写代码，不做验收判断，继承主模型
