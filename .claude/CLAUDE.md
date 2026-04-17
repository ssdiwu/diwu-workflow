# diwu-workflow

## 工作流规则

详细规则见 @rules/ 目录：
- @rules/README.md - 规则速查索引
- @rules/mindset.md - 上位心智层（三唯一框架、五问开工、不确定性门控）【独立注入】
- @rules/judgments.md - 判断锚点集中管理（四段式：启动/实施/验收/纠偏）
- @rules/task.md - 任务状态机与 acceptance 格式、blocked_by、提交规范
- @rules/workflow.md - 任务规划、实施、验证
- @rules/session.md - Session 生命周期管理
- @rules/verification.md - 证据优先级体系（L1-L5）
- @rules/correction.md - 纠偏体系（退化信号→四行重写→止损序列）
- @rules/pitfalls.md - 误判防护（三层：泛化/项目/接口）
- @rules/exceptions.md - 异常处理与 BLOCKED 判定
- @rules/templates.md - 格式模板与可调参数
- @rules/constraints.md - 架构约束（五维约束设计）

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

## 工作流

规则由 diwu-workflow 插件的 UserPromptSubmit hook 在每次对话开始时注入（`rules-index.md` 精华摘要），无需手动引用。

**recording.md 更新规则**：每次 session 结束前必须主动更新 `.claude/recording.md`，无论 task.json 是否有 InProgress 任务。Stop hook 只在有 InProgress 任务时触发提醒，插件维护类工作不在 task.json 管辖范围内，不能依赖 hook 提醒，必须主动写入。

**时间戳规则**：写入 Session 标题前必须先运行 `date '+%Y-%m-%d %H:%M:%S'` 获取真实时间，禁止手写日期或写"（续）"等占位符。
- ❌ `## Session 2026-02-26 （续）`
- ✅ 先运行 `date` → 得到 `2026-02-26 16:49:42` → 写 `## Session 2026-02-26 16:49:42`

- 正例：修改了 commands/ddemo.md 和 dprd.md，对话即将结束 → 主动写入 recording.md，记录改动内容和下一步
- 反例：改完文件后停下来等待 Stop hook 提醒 → 违规，Stop hook 只在有 InProgress 任务时触发
- 边界例：对话中途完成了一个小改动，但还有后续工作未完成 → 等所有工作完成后统一写入，不必每次改动都写


## 项目结构

| 目录 | 说明 |
|------|------|
| `.claude/` | Claude Code 配置（rules、agents 3 个、recording、task.json） |
| `.claude-plugin/` | 插件元数据（plugin.json、marketplace.json） |
| `commands/` | 7 个用户命令（/dinit /dtask /dprd /dadr /ddoc /ddemo /dcorr） |
| `skills/` | 3 个 Skill（dprd、ddemo、ddoc） |
| `hooks/` | Claude Code 钩子配置（16 个 Python 脚本） |
| `.doc/` | 文档目录（ADR、PRD、Demo、指南） |
| `assets/dinit/assets/` | /dinit 模板资源 |
| `tests/` | pytest 测试套件（level0-4 四级） |
| `configs/` | 配置文件存储 |

## 关键文件说明

| 路径 | 作用 |
|------|------|
| `.claude-plugin/plugin.json` | 插件版本 0.8.0，元数据定义 |
| `.claude-plugin/marketplace.json` | 市场索引 |
| `hooks/hooks.json` | 11 个钩子事件配置 |
| `commands/*.md` | 各命令的行为描述（仅描述，无实现代码） |
| `skills/*/SKILL.md` | Skill 框架知识（Claude 自动加载） |
| `assets/dinit/assets/` | /dinit 模板文件 |
| `pytest.ini` | pytest 配置 |

## 发版规则

每次功能变更提交前，询问用户是否更新版本号，将版本号更新包含在同一个 commit 中，避免单独提交。

**版本号同步约束**：`.claude-plugin/plugin.json` 和 `.claude-plugin/marketplace.json` 的 `version` 字段必须保持一致。更新 version 时两个文件同时修改，验证方式：`python3 -m json.tool .claude-plugin/plugin.json && python3 -m json.tool .claude-plugin/marketplace.json`

**CLAUDE.md 版本引用**：`关键文件说明`章节中的版本号（如"插件版本 0.7.x"）也需同步更新。虽然 `.claude/` 在 gitignore 中不会同步到远程，但本地 working copy 中应保持与实际版本一致。

## 插件开发专属约束

> 以下约束仅适用于 diwu-workflow 插件本身的开发维护，不通过 /dinit 分发给用户项目。

### 版本号语义化规则

| 版本号 | 适用场景 | 示例 |
|-------|---------|------|
| **X.Y.Z** | 初始开发 | `0.1.0` |
| **主版本（X）** | 破坏性变更：命令参数格式变化、删除已有命令、API 契约变更 | `0.8.0` |
| **次版本（Y）** | 新增功能：新增命令、新增选项、新增行为（向后兼容） | `0.2.0` |
| **修订号（Z）** | bug 修复：行为修正，不影响 API | `0.1.1` |

- 每次功能变更 commit 必须同时更新 version，version 更新包含在同一 commit 中
- 版本号只增不减；主版本变更表示破坏性变更

### 发版状态机

| Current State | Event            | New State  |
|---------------|------------------|------------|
| dev           | 提交含 version++ | published  |
| published     | 发现 bug         | dev        |
| published     | 直接修改内容无版本号 | invalid（禁止）|

### 跨平台路径约束

`hooks.json` 中的路径引用必须兼容 macOS/Linux，禁止使用 Windows 路径分隔符（`\`）。

### 并发约束

插件文件为静态资源，无并发写入场景；多 session 同时使用同一插件时以磁盘文件版本为准。

### 数据所有权

- Source of Truth: `.claude-plugin/plugin.json`（版本、命令列表、元数据）
- 生成产物链: `assets/dinit/assets/*.template` → 用户项目 `.diwu/`（通过 /dinit）
- 冲突策略: 模板文件只写，用户项目文件不覆盖已存在内容（除非用户明确要求）

### 插件降级行为

| Dependency          | Failure                          | Fallback                               | User Perception              |
|---------------------|----------------------------------|----------------------------------------|----------------------------|
| 插件缓存             | cache 目录不存在                  | /dinit 报错提示重新安装插件             | 明确报错，不静默失败          |
| Python3             | smoke.sh 中 python3 不可用       | JSON 校验跳过，打印警告                 | 校验弱化，功能不受影响        |

## 重要约定

- `.claude/` 目录内容不 commit、不 push；recording/ 是本项目工作记录，不同步到远程
- `tests/` 目录为本地开发测试，不 commit、不 push

## 常用操作

```bash
# 推送更新
git add . && git commit -m "..." && git push

# 验证插件 JSON 合法性
python3 -m json.tool .claude-plugin/plugin.json
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool hooks/hooks.json
```

## 规则引用说明

本项目使用 @rules/ 引用自动加载工作流规则。规则文件位于 `.claude/rules/` 目录，由 UserPromptSubmit hook 在每次对话开始时注入。
