# 文件布局

> **规则约束级别说明**：本文件定义文件组织的核心规则。除非特别标注 `[建议]`，否则都是必须遵守的约束。

## .diwu/ 目录结构

```
.diwu/
├── CLAUDE.md                      # 全局 Agent 配置入口
├── dsettings.json                  # 可调参数配置
├── dtask.json                      # 当前任务列表
├── recording/                     # Session 进度记录目录
│   └── session-YYYY-MM-DD-HHMMSS.md  # 单个 session 记录文件
├── decisions.md                   # 设计决策记录（可选，有重大决策时创建）
├── archive/                       # 归档目录
│   ├── task_archive_YYYY-MM.json     # 归档任务（按月）
│   └── recording_archive_YYYY-MM.tar.gz  # 归档 session 文件（按月）
├── checks/                        # 验证脚本目录
│   ├── smoke.sh
│   └── task_<id>_verify.sh
└── init.sh                        # 环境初始化脚本（可选）
```

> 规则文件由插件 UserPromptSubmit hook 注入，不在项目 .diwu/ 目录中。

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
| `.diwu/CLAUDE.md` | 全局配置、个人偏好、规则索引 | 共同维护 |
| `.diwu/dsettings.json` | 可调参数配置（review_limit、归档阈值、子代理并发数等） | 人工设置，Agent 读取 |
| `.diwu/dtask.json` | 当前所有任务的状态和内容 | Agent 读写 |
| `.diwu/recording/` | Session 进度记录目录，每个 session 一个独立文件 | Agent 写 |
| `.diwu/decisions.md` | 重大设计决策记录（影响范围 ≥2 模块，或引入新约束），供 Agent 快速检索历史决策理由 | Agent 写 |
| `.diwu/archive/task_archive_YYYY-MM.json` | 按月归档的 Done/Cancelled 任务，保留 id 序列 | Agent 写 |
| `.diwu/checks/smoke.sh` | 基线环境验证，session 启动时运行 | Agent 提供方案，人工确认后实施 |
| `.diwu/checks/task_<id>_verify.sh` | 任务专属验证脚本，id 对应 dtask.json | Agent 创建并执行 |
| `.diwu/init.sh` | 开发环境初始化，session 启动时按需运行 | 讨论后由 Agent 实施 |

## 归档触发条件

- **archive/task_archive_YYYY-MM.json**：`dtask.json` 中 Done/Cancelled 任务超过归档阈值时触发（阈值见 dsettings.json `task_archive_threshold`，默认 20）
- **archive/recording_archive_YYYY-MM.tar.gz**：`recording/` 目录中 session 文件数量超过归档阈值时触发（阈值见 dsettings.json `recording_archive_threshold`，默认 50），归档时保留最近 N 天的文件（N 见 dsettings.json `recording_retention_days`，默认 30）

## 归档执行步骤

**dtask.json 归档**：
1. 将 Done/Cancelled 任务移到 archive/task_archive_YYYY-MM.json（当前月份）
2. 保留 id 序列（新任务继续递增）
3. 在 recording/ 目录中记录归档操作

**recording/ 归档**：
1. 查找 `recording/` 中修改时间超过保留期的 session 文件（`find .diwu/recording/ -name "session-*.md" -mtime +N`，N 为保留天数）
2. 按月分组，打包为 `archive/recording_archive_YYYY-MM.tar.gz`
3. 删除已归档的原始文件
4. 在当前 session 文件中记录归档操作（归档文件数量、时间范围）

## 查找历史

- 最近任务：查 dtask.json
- 历史任务：查 archive/task_archive_YYYY-MM.json（按月，grep 搜索）
- 最近进度：`ls -t recording/ | head -5` 查看最新 5 个 session 文件
- 搜索历史：`grep -r "关键词" recording/` 在所有 session 中搜索
- 历史决策：查 decisions.md（设计方向、方案选择、边界定义）

## Session 文件管理

recording/ 目录中的 session 文件按时间戳命名（session-YYYY-MM-DD-HHMMSS.md），建议定期清理超过保留期的文件（保留天数见 dsettings.json `recording_retention_days`，默认 30 天）。清理命令示例：

```bash
find .diwu/recording/ -name "session-*.md" -mtime +30 -delete
```
