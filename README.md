# diwu-workflow

diwu 编码工作流套件 — Claude Code 插件

## 包含的 Commands

| 命令 | 作用 |
|------|------|
| `/dinit` | 初始化项目工作流结构（CLAUDE.md / task.json / recording.md） |
| `/dplan` | 将功能描述拆解为 task.json 任务列表 |
| `/dadr` | 记录架构决策（ADR），技术选型或重大设计决策 |
| `/ddoc` | 产品文档工具，正向（需求→文档）或逆向（代码→文档） |

## 包含的 Skills

Skills 与 Commands 一一对应，Claude 识别到相关场景时自动加载为背景知识：

| Skill | 自动触发场景 |
|-------|------------|
| `dinit` | 新建项目、初始化工作流、创建 CLAUDE.md |
| `dplan` | 规划功能、分解需求、新建任务 |
| `dadr` | 技术选型、架构决策、不可逆约束 |
| `ddoc` | 写文档、还原文档、产品文档 |

## 包含的 Hooks

| Hook | 触发时机 | 作用 |
|------|---------|------|
| `PreToolUse` (Bash) | 每次执行 Bash 前 | 输出当前 InProgress 任务的 acceptance 条件，防止目标漂移 |
| `Stop` | 回合结束时 | 检查是否有未完成任务（InReview 超过 5 个时豁免），防止遗漏 |

## 安装

```
/plugin marketplace add ssdiwu/diwu-workflow
/plugin install diwu-workflow@diwu-workflow
```

## 使用

安装后，Commands 通过 `/dinit`、`/dplan`、`/dadr`、`/ddoc` 主动触发；Skills 由 Claude 根据上下文自动加载。
