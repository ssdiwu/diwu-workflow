# diwu-workflow 接口层

- **定位**：diwu-workflow 插件的接口契约汇总文档，作为 Commands、Skills、Hooks 的索引参考
- **目标**：提供接口层全景视图，明确触发时机、权限边界和执行契约
- **版本**：0.8.0
- **创建**：2026-04-10
- **改写**：2026-04-10
- **状态**：当前主版本

---

## Commands（用户主动触发）

Commands 是用户通过 `/command-name` 触发的交互式工作流。文件位于 `commands/*.md`，格式为带 YAML frontmatter 的 Markdown。

### /dinit — 项目初始化

**文件**：`commands/dinit.md`
**触发**：`/dinit [项目描述（可选）]`
**allowed-tools**：`Read, Write, Edit, Bash, Glob`

核心步骤：
1. 收集项目信息（名称、技术栈、常用命令、关键目录）
2. 选择配置模式（精简 / 便携），检查 `~/.claude/rules/` 是否存在
3. 创建 `.claude/CLAUDE.md`、`AGENTS.md`、`.claude/task.json`、`init.sh`、`.claude/recording/`、`smoke.sh`
4. 可选：创建 `.claude/rules/constraints.md`、git 初始化
5. 验证清单逐项确认

**模板来源**：`${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/`

**负面约束**：
- 不覆盖已存在的 task.json（追加而非覆盖）
- 精简模式不复制规则内容，只引用路径

---

### /dtask — 任务规划

**文件**：`commands/dtask.md`
**触发**：`/dtask [功能描述（可选）]`
**allowed-tools**：`Read, Write, Edit, Glob`

核心步骤：
1. 接收功能描述（含上下文检查：参数是对话恢复还是功能描述）
2. 示范完整任务示例的思维粒度，澄清 3-4 个问题
3. 读取 `.doc/prd/README.md`、`.doc/demo/README.md` 获取文档上下文
4. 确定新任务 ID（task.json 最大 ID + archive 最大 ID + 1），生成任务写入 task.json
5. 质量检查（GWT 格式、可验证、自包含、垂直切片）
6. 三视角审查（仅 functional/ui 且 acceptance > 3 条时并行触发）
7. 写入后提示（列出任务、blocked_by 说明）

**负面约束**：
- 不生成中间 PRD markdown 文件
- 不自动将任务改为 InSpec
- ID 严禁复用

---

### /dprd — 产品需求文档

**文件**：`commands/dprd.md`
**触发**：`/dprd [full（可选）]`
**allowed-tools**：`Read, Write, Edit, Glob, Bash`

**模式**：
- 产品模式（默认）：§1 概述、§2 核心场景、§3 功能规格、§4 方案对比、§5 UI 与交互规格
- 完整模式（`/dprd full`）：追加 §6 技术方案、§7 数据模型、§8 边界条件与异常处理、§9 迁移路径

核心步骤：
1. 确认核心定位（问题/目标用户/核心场景）
2. 澄清需求（每次只问一个问题；Q1-Q6 产品模式，Q7-Q8 完整模式追加）
3. 检查已有 PRD（读取 `.doc/prd/README.md`）
4. 生成 PRD（含脊梁提炼、论证链设计、论证积木选取）
5. 写入 `.doc/prd/PRD-{kebab-case-title}.md`，更新 `.doc/prd/README.md` 索引
6. 交付前自检（智能引号、绝对路径、乱码检查）

**负面约束**：
- 不自动写入 task.json
- 不生成代码（PRD 是需求文档）

---

### /ddemo — 能力验证

**文件**：`commands/ddemo.md`
**触发**：`/ddemo [Demo 名称或描述（可选）]`
**allowed-tools**：`Read, Write, Glob, Bash`

核心步骤：
1. 获取输入（参数 / PRD Demo 需求清单 / 询问）
2. 两级门控（产品类型判断 → 能力 vs 功能判断）
3. 建立上下文 + 识别不确定性来源（四类：能力缺口/结果不可预期/方法未验证/集成风险）
4. 生成 Demo 规格（能力定义、核心验证资产、通过标准、依赖关系、边界映射）
5. 创建 Demo 目录结构 + 写入 `.doc/demo/DEMO-{kebab-case-name}-spec.md`
6. 更新 `.doc/demo/README.md` 索引

**不确定性分类**：能力缺口 / 结果不可预期 / 方法未验证 / 集成风险

**负面约束**：
- 不分析「哪些事需要 Demo」（`/dprd` 的职责）
- 不批量处理多个 Demo（每次只处理一个）
- 不写入 task.json

---

### /dadr — 架构决策

**文件**：`commands/dadr.md`
**触发**：`/dadr [决策描述（可选）]`
**allowed-tools**：`Read, Write, Glob, Bash`

核心步骤：
1. 接收决策描述，澄清备选方案、约束条件、核心取舍
2. 读取 `.doc/adr/README.md`（如存在），判断新建 vs 更新已有 ADR
3. 确定 ADR 编号（最大编号 + 1），生成并写入 `.doc/adr/ADR-NNN-kebab-case-title.md`
4. 更新 `.doc/adr/README.md` 索引

**ADR 文件格式**：`.doc/adr/ADR-NNN-kebab-case-title.md`（NNN 三位数字补零）

**特殊情况**：更新已有 ADR 状态（Proposed → Accepted）时，只修改 Status 行，不重新生成。

---

### /ddoc — 产品文档

**文件**：`commands/ddoc.md`
**触发**：`/ddoc [forward|reverse（可选）]`
**allowed-tools**：`Read, Write, Edit, Glob, Bash`

**正向模式（需求 → 文档）**：
- 六步设计法（找约束 → 定义原子 → 设计组合 → 划定边界 → 降级路径 → 同步策略）
- 输出到 `.doc/` 目录（领域驱动 或 分层结构）

**逆向模式（代码 → 文档）**：
- 读取代码库，按四层结构写文档（数据层/接口层/业务逻辑层/产品层）
- 自审清单（9 项）+ 两层完整性检查（结构检查 + 深度检查）
- 补充缺口，循环直到无缺口

**输出结构选择**：
- **领域驱动**（推荐，3 个以上业务域）：`constraints.md` + 各域文件
- **分层**（工具类/小项目）：`data.md` / `api.md` / `logic.md` / `product.md`

---

### /dcorr — 纠偏恢复

**文件**：`commands/dcorr.md`
**触发**：`/dcorr [偏航描述（可选）]`
**allowed-tools**：`Read, Glob, Bash`

**触发条件**（出现任一则启动）：
- 同一问题已被纠偏两次以上仍沿旧路径推进
- 同一前提被反复解释
- 输出越来越像通用套路，越来越不像当前任务
- 讨论越来越长，但下一步动作越来越模糊
- 已改动却拿不出运行态或输出层证据
- 开始同时引用多个目录、多个入口、多个"真相源"

**五步协议**：
1. 停止当前动作（六类停机检查）
2. 四行重写（当前目标/当前主线/当前现象/当前缺口）
3. 误判排查（六类泛化模式优先排除）
4. 入口重判（直接继续 / 先写最小规格 / 先探索验证）
5. 恢复执行（现象→判断→动作骨架，禁止直接宣称"已经搞定"）

**负面约束**：
- 不改变 task.json 状态（纠偏是过程修正）
- 不退化成为"全程运行总规范"或"所有任务都按排障处理"的手册

---

## Skills（Claude 自动加载）

Skills 是 Claude Code 在特定场景下自动激活的背景知识。文件位于 `skills/*/SKILL.md`。

### ddoc — 产品文档工具

**路径**：`skills/ddoc/SKILL.md`
**触发场景**：
1. 为已有产品还原/补全文档
2. 为新功能/模块编写产品文档
3. 用户说"写文档"、"还原文档"、"doc"、"产品文档"

**核心内容**：五约束维度定义与检验、两层完整性检查模板、六步设计法、正向/逆向模式详细步骤

---

### dprd — PRD 工具

**路径**：`skills/dprd/SKILL.md`
**触发场景**：
1. 讨论产品规划或功能设计
2. 进行需求分析或竞品调研
3. 设计迭代路径或优先级排序
4. 用户说"PRD"、"需求文档"、"竞品分析"、"产品规划"、"需求优先级"

**核心内容**：竞品分析方法、用户画像与场景分析、需求优先级（迭代层次方法论）、五维约束识别、方案对比方法论、非功能性需求分类

---

### ddemo — Demo 工具

**路径**：`skills/ddemo/SKILL.md`
**触发场景**：
1. 讨论技术可行性或方案选型
2. 评估某个实现的不确定性
3. 决定直接集成 vs 先做 Demo 验证
4. 分析能力复用或知识沉淀策略
5. 用户说"积木"、"Demo"、"能力验证"、"不确定性"

**核心内容**：产品分类（业务编排型/能力构建型）、三层积木模型、不确定性四分类、能力 vs 功能判断、资产形态四分类、能力库积累飞轮、五维约束设计

---

## Hooks（自动触发）

Hooks 配置在 `hooks/hooks.json`，通过 Claude Code settings.json 的 `hooks` 字段生效。

### 钩子总览

| 事件 | 触发时机 | 脚本 | 作用 |
|------|---------|------|------|
| `UserPromptSubmit` | 用户提交 prompt 前 | `user_prompt_submit.py` | 规则注入：mindset.md 全文 + rules 速查索引 |
| `SessionStart` | Session 启动时 | `session_start.py` | 将主 session ID 写入 `/tmp/.claude_main_session` |
| `TaskCreated` | 任务创建时 | `task_created_validate.py` | 验证新建任务的 ID 递增和格式合法性 |
| `PreToolUse` | 工具执行前（matcher: Edit/Write/Bash/Read/Grep/Glob） | `drift_detect_pre.py` + `pre_tool_use_bash.py` + `inject_errors_decisions.py` | drift 检测 + 任务提醒 + **近期踩坑/决策注入** |
| `SubagentStart` | 子代理启动时 | `subagent_start.py` | 注入最新 session 摘要 + InProgress 任务 title/acceptance/steps |
| `SubagentStop` | 子代理停止时 | `subagent_stop.py` | 主代理立即将进度写入 recording.md |
| `Stop` | 回合结束时 | `stop_blocking.py` | 任务调度阻断 + git status 快照 |
| `PostToolUse` | 工具执行后（matcher: Write/Edit） | `post_tool_json_validate.py` + `context_monitor.py` + `post_tool_reminder.py` | JSON 合法性验证 + context 监控 + **写后记录提醒** |
| `PreCompact` | 压缩上下文前 | `pre_compact.py` | checkpoint 写入 recording |
| `PostToolUseFailure` | 工具执行失败时 | `post_tool_use_failure.py` | **3-Strike 错误协议**（自动计数+分级提示：诊断/换方法/停手重想） |
| `TaskCompleted` | 任务完成时 | `task_completed.py` | 任务完成记录 |

### 关键钩子说明

#### PreToolUse（工具执行前）

**触发**：每次 Agent 执行 Edit/Write/Bash/Read/Grep/Glob 命令前
**matcher**：`Edit|Write|Bash|Read|Grep|Glob`
**行为**：
- `drift_detect_pre.py`：检测 drift 信号（edit_strek/pure_discussion/repetitive_loop/scope_drift）
- `pre_tool_use_bash.py`：读取 task.json，找 InProgress 任务，打印其 acceptance 到终端
- **`inject_errors_decisions.py`**：注入近期踩坑经验（recording/ 最近 3 个 session）+ 近期设计决策（decisions.md 最近 3 条），实现注意力操纵

#### Stop（回合结束）

**触发**：Agent 回合结束时
**行为**：
1. 读取 `.claude/settings.json` 工作流参数
2. InProgress 任务检查 → 存在则阻断
3. Review buffer 机制（`review_used >= review_limit` 时通知人工验收）
4. 可执行 InSpec 任务检查 → 存在则阻断
5. `has_substantial_work()` 判断（git status/近期 commit/InProgress/InReview）
6. `check_rec()` 判断（recording 最近 session 是否在 `recording_session_window` 内）

#### PostToolUse（Write/Edit 后）

**触发**：每次 Write 或 Edit 工具执行后
**matcher**：`Write` / `Edit`
**行为**：
- `post_tool_json_validate.py`：验证写入的 JSON 文件合法性
- `context_monitor.py`：通用 context 监控

---

## Plugin 元数据

**文件**：`.claude-plugin/plugin.json`

```json
{
  "name": "diwu-workflow",
  "version": "0.8.0",
  "description": "diwu 编码工作流套件：项目初始化、任务规划、产品需求文档、架构决策记录、产品文档、纠偏恢复。内置规则体系重构、纠偏机制、证据优先级与误判防护",
  "commands": [
    "./commands/dinit.md",
    "./commands/dtask.md",
    "./commands/dprd.md",
    "./commands/dadr.md",
    "./commands/ddoc.md",
    "./commands/ddemo.md",
    "./commands/dcorr.md"
  ],
  "skills": ["./skills/ddoc", "./skills/dprd", "./skills/ddemo"],
  "author": { "name": "ssdiwu" }
}
```

**命令数量**：7 个（dinit / dtask / dprd / dadr / ddoc / ddemo / dcorr）
**Skill 数量**：10 个（dtask / dsess / dcorr / dvfy / djug / drec / ddemo / dprd / ddoc / darc）
**Hook 事件数量**：11 个

---

## 安装

```
/plugin marketplace add ssdiwu/diwu-workflow
/plugin install diwu-workflow@ssdiwu
```

---

## 附录

### Commands frontmatter 摘要

| 命令 | argument-hint | allowed-tools | effort |
|------|--------------|---------------|--------|
| `/dinit` | [项目描述（可选）] | Read, Write, Edit, Bash, Glob | medium |
| `/dtask` | [功能描述（可选）] | Read, Write, Edit, Glob | high |
| `/dprd` | [full（可选）] | Read, Write, Edit, Glob, Bash | high |
| `/ddemo` | [Demo 名称或描述] | Read, Write, Glob, Bash | high |
| `/dadr` | [决策描述（可选）] | Read, Write, Glob, Bash | medium |
| `/ddoc` | [forward\|reverse（可选）] | Read, Write, Edit, Glob, Bash | high |
| `/dcorr` | [偏航描述（可选）] | Read, Glob, Bash | low |
