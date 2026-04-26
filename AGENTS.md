# diwu-workflow

## 工作流规则

详细规则见 @.opencode/references/ 目录：
- @.opencode/references/judgments.md - 判断锚点集中管理
- @.opencode/references/states.md - 任务状态机与 acceptance 格式
- @.opencode/references/workflow.md - Session 启动、任务规划、实施、验证
- @.opencode/references/exceptions.md - 异常处理与 BLOCKED 判定
- @.opencode/references/templates.md - DECISION TRACE、BLOCKED、REVIEW 格式模板
- @.opencode/references/file-layout.md - .opencode/ 目录结构与归档规则
- @.opencode/references/constraints.md - 架构约束（五维约束设计）

## 核心原则

- 少即是多，克制且清晰：偏好简洁的设计和输出，排斥冗余
- 关注点分离原则：不同层次的问题应在各自的边界内解决，不跨层污染
- 具体胜于抽象：示例是规则的执行锚点，抽象描述只是参考；规则与示例冲突时以示例为准
- 引导顺序即优先级：元规则和解释框架必须在被解释内容之前出现；结构顺序本身传递优先级信息
- 程序性规则（固定步骤、状态机、目录结构）使用列表定义，可不附示例
- 判断性规则（分类、取舍、边界判定）必须提供示例锚点：正例、反例、边界例

## 项目上下文

- **仓库**：https://github.com/ssdiwu/diwu-workflow
- **本地路径**：/Users/diwu/Documents/codes/Githubs/diwu-workflow/
- **用途**：维护 Claude Code 插件，不是应用开发项目
- **opencode 版本**：/Users/diwu/Documents/codes/Githubs/opencode-diwu-workflow/

## 工作流

规则由 diwu-workflow 插件的 `tui.prompt.append` 事件在每次对话开始时注入（rules-index.md 精华摘要），无需手动引用。

**recording.md 更新规则**：每次 session 结束前必须主动更新 `.diwu/recording.md`，无论 dtask.json 是否有 InProgress 任务。Stop hook 只在有 InProgress 任务时触发提醒，插件维护类工作不在 dtask.json 管辖范围内，不能依赖 hook 提醒，必须主动写入。

**时间戳规则**：写入 Session 标题前必须先运行 `date '+%Y-%m-%d %H:%M:%S'` 获取真实时间，禁止手写日期或写"（续）"等占位符。
- ❌ `## Session 2026-02-26 （续）`
- ✅ 先运行 `date` → 得到 `2026-02-26 16:49:42` → 写 `## Session 2026-02-26 16:49:42`

- 正例：修改了 commands/ddemo.md 和 dprd.md，对话即将结束 → 主动写入 recording.md，记录改动内容和下一步
- 反例：改完文件后停下来等待 Stop hook 提醒 → 违规，Stop hook 只在有 InProgress 任务时触发
- 边界例：对话中途完成了一个小改动，但还有后续工作未完成 → 等所有工作完成后统一写入，不必每次改动都写

## 关键文件说明

| 路径 | 作用 |
|------|------|
| `opencode.json` | opencode 项目配置 |
| `.opencode/plugins/diwu-workflow.ts` | TypeScript 插件（hooks 重写） |
| `.opencode/commands/*.md` | 用户触发的命令（/dinit /dtask /dprd /dadr /ddoc /ddemo） |
| `.opencode/skills/*/SKILL.md` | 技能知识库（opencode 自动加载） |
| `.opencode/agents/*.md` | Agent 定义（Primary/Subagent） |
| `.opencode/references/*.md` | 参考文档（规则、模板、决策） |

## 发版规则

每次功能变更提交前，询问用户是否更新版本号（`opencode.json` 的 `version` 字段），将版本号更新包含在同一个 commit 中，避免单独提交。

## 常用操作

```bash
# 推送更新
git add . && git commit -m "..." && git push

# 验证 opencode 配置
opencode validate

# 测试插件加载
opencode doctor
```

## 规则引用说明

本项目使用 @.opencode/references/ 引用自动加载工作流规则。规则文件位于 `.opencode/references/` 目录，由 diwu-workflow 插件的 `tui.prompt.append` 事件在每次对话开始时注入。
