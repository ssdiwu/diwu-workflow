# 文件布局

## .claude/ 目录结构

```
.claude/
├── CLAUDE.md                      # 全局 Agent 配置入口
├── task.json                      # 当前任务列表
├── task_archive_YYYY-MM.json      # 归档任务（归档后生成）
├── recording.md                   # Session 进度记录
├── decisions.md                   # 设计决策记录（可选，有重大决策时创建）
├── recording_archive/             # 归档记录目录（归档后生成）
│   └── YYYY-MM-DD.md
├── checks/                        # 验证脚本目录
│   ├── smoke.sh
│   └── task_<id>_verify.sh
└── init.sh                        # 环境初始化脚本（可选）
```

> 规则文件由插件 UserPromptSubmit hook 注入，不在项目 .claude/ 目录中。

## .doc/ 目录结构（SDD 规范产物）

```
.doc/
├── [domain 或分层文件]   # 见 /diwu-doc
└── adr/                  # 架构决策记录，见 /diwu-adr
    └── ADR-NNN-kebab-case-title.md
```

## 文件说明

| 路径 | 用途 | 读写方 |
|------|------|--------|
| `.claude/CLAUDE.md` | 全局配置、个人偏好、规则索引 | 共同维护 |
| `.claude/task.json` | 当前所有任务的状态和内容 | Agent 读写 |
| `.claude/task_archive_YYYY-MM.json` | 按月归档的 Done/Cancelled 任务，保留 id 序列 | Agent 写 |
| `.claude/recording.md` | Session 进度记录，每次追加 | Agent 写 |
| `.claude/decisions.md` | 重大设计决策记录（影响范围 ≥2 模块，或引入新约束），供 Agent 快速检索历史决策理由 | Agent 写 |
| `.claude/recording_archive/YYYY-MM-DD.md` | 按天归档的历史 session 记录 | Agent 写 |
| `.claude/checks/smoke.sh` | 基线环境验证，session 启动时运行 | Agent 提供方案，人工确认后实施 |
| `.claude/checks/task_<id>_verify.sh` | 任务专属验证脚本，id 对应 task.json | Agent 创建并执行 |
| `.claude/init.sh` | 开发环境初始化，session 启动时按需运行 | 讨论后由 Agent 实施 |

## 归档触发条件

- **task_archive_YYYY-MM.json**：`task.json` 中 Done/Cancelled 任务超过归档阈值时触发（阈值见 templates.md 可调参数）
- **recording_archive/YYYY-MM-DD.md**：recording.md 中 session 数超过归档阈值时自动触发，无需人工确认，按天归档（阈值见 templates.md 可调参数）

## 归档执行步骤

**task.json 归档**：
1. 将 Done/Cancelled 任务移到 task_archive_YYYY-MM.json（当前月份）
2. 保留 id 序列（新任务继续递增）
3. 在 recording.md 记录归档操作

**recording.md 归档**：
1. 将最旧的 session 移入 recording_archive/YYYY-MM-DD.md（按天）
2. recording.md 始终保留最近 5 条 session
3. 无需人工确认，session 启动时自动执行

## 查找历史

- 最近任务：查 task.json
- 历史任务：查 task_archive_YYYY-MM.json（按月，grep 搜索）
- 最近进度：查 recording.md
- 历史进度：查 recording_archive/YYYY-MM-DD.md
- 历史决策：查 decisions.md（设计方向、方案选择、边界定义）
