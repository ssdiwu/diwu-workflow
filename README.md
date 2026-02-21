# diwu-workflow

diwu 编码工作流套件 — Claude Code 插件

## 包含的 Skills

| Skill | 触发场景 |
|-------|---------|
| `diwu-init` | 初始化项目工作流结构（CLAUDE.md / task.json / recording.md） |
| `diwu-plan` | 将功能描述拆解为 task.json 任务列表 |
| `diwu-adr` | 记录架构决策（ADR），技术选型或重大设计决策 |
| `diwu-doc` | 产品文档工具，正向（需求→文档）或逆向（代码→文档） |

## 包含的 Hooks

| Hook | 触发时机 | 作用 |
|------|---------|------|
| `PreToolUse` (Bash) | 每次执行 Bash 前 | 输出当前 InProgress 任务的 acceptance 条件，防止目标漂移 |
| `Stop` | 回合结束时 | 检查是否有未完成任务，防止遗漏 |

## 安装

```bash
/plugin marketplace add <your-github-username>/diwu-workflow
/plugin install diwu-workflow@diwu-workflow
```

## 使用

安装后，skills 会根据上下文自动激活，也可通过 `/diwu-init`、`/diwu-plan`、`/diwu-adr`、`/diwu-doc` 直接调用。
