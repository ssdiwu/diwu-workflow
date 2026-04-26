# diwu-workflow 项目高频误判表 (Layer 2)

> 本文件由归档聚合自动生成（/darc 归档时从 recording 踩坑经验中提取）。
> 手动维护优先：如发现新的项目特有误判模式，直接在此追加。

## 更新记录

| 日期 | 归档批次 | 新增条目 |
|------|----------|----------|
| 2026-04-20 | Task 归档 42 个 + Recording 归档 83 个（保留最新 20） | 54 条（30 个 session） |

## 验证误读

| # | 现象 → 根因 → 正确做法 | 来源 Session |
|---|---------------------------|-------------|
| 1 | 新写测试时，正则对 JSON 字符串需单独处理（直接对 `str(pj)` 做正则会匹配到 JSON 语法字符 `[`），应从 JSON 对象提取字段后再正则 | session-2026-04-11-003355.md |
| 2 | 文件存在 ≠ 功能生效。agents 文件都在但 `claude agents` 列不出 → 应先跑实际加载命令验证，而非仅检查文件是否存在 → 正确做法：用 `claude agents` 作为 agents 生效的 L1 证据 | session-2026-04-14-161449.md |
| 3 | 仅凭 frontmatter 结构看起来正确就认为 verifier 可加载 → 根因是把静态文件检查当成运行态证据 → 错误判断：在插件级文件上反复调字段而未先重跑 `claude agents` 验证 → 正确做法：优先用 `claude agents` 作为 Agent 加载的 L1 证据，再回头调整文件层配置 | session-2026-04-14-184011.md |
| 4 | `/dinit` 刷新报告里"文件都在"不等于内容已经同步 → 根因是刷新检查偏向存在性和章节完整性，没有做模板内容差异校验 → 错误判断：把目录齐全当成规则已刷新 → 正确做法：刷新时要对比规则文件内容或版本标识，再下结论 | session-2026-04-16-143055.md |
| 5 | 先前只验证了相关实现存在，但没单独断言最终 prompt 中不再含 lessons 文案 → 容易把"代码看起来没了"误判成"输出层已经没了" → 正确做法是补一条直接检查 `additionalSystemPrompt` 的测试，再用 pytest 验证。 | session-2026-04-17-161852.md |
| 6 | 直接跑现有 level3 测试会提前命中 163/164/166 的未来要求 → 误把"总测试失败"当成"Task#162 未完成" → 正确做法是给当前任务补独立测试文件，只验证本任务 acceptance。 | session-2026-04-17-162710.md |
| 7 | 看到项目规则文件已是通用版就容易误判 Task#163 已完成 → 实际缺口在 `/dinit` 模板仍残留旧插件专属版本 → 正确做法是用任务级测试同时校验项目规则、模板、注入脚本和 CLAUDE.md 四处一致性。 | session-2026-04-17-164558.md |
| 8 | 只看 git commit message 容易误判 task.json 已经同步为 Done → 之前提交里 task.json 未必真的随任务一起落盘 → 正确做法是先直接读取 task.json 核对状态，再进入下一任务。 | session-2026-04-17-170612.md |
| 9 | 只验证路径替换容易误判 `/dinit` 迁移能力已经完整落地 → 真实缺口是"旧运行时目录存在时的迁移检测提示"没有可观测证据 → 正确做法是把该场景写进命令文档并新增任务级测试断言，拿到 L3 证据后再 Done。 | session-2026-04-17-171901.md |
| 10 | 迁移完成后首次测试失败 → 根因不是迁移动作本身，而是旧 `.claude/checks/` 也属于运行时目录且 `.diwu/task.json` 原本就含坏 JSON → 容易误判为"迁移破坏了数据" → 正确做法是先把任务级测试与当前目录设计对齐，再用 `json.tool` 区分历史脏数据和本次迁移问题。 | session-2026-04-17-172950.md |
| 11 | `claude -p "/dinit ..."` 返回"已刷新"并不等于真实执行了迁移链路 → 根因是把命令回复文本误当成文件系统结果 → 错误判断是"文档契约测试通过就足以 Done" → 正确做法是增加临时副本实测，用 `.diwu/` 产物、旧路径消失、constraints 通用化三类可观测事实做验收。 | session-2026-04-17-182722.md |
| 12 | 只改三处显式 version 字段后测试仍失败 → 根因是仓内还有 `.doc/` 与 `README.md` 的活动版本引用被 `tests/level1/test_version_sync.py` 扫描 → 错误判断是"版本号任务只需改配置文件" → 正确做法是先跑全量版本同步测试，再按失败清单一次性收齐所有活动文档引用。 | session-2026-04-17-183044.md |
| 13 | 只改配置文件中的 version 字段会误判"版本任务已完成" → 根因是活动文档也被版本同步测试扫描 → 错误判断是把版本号任务当成纯配置变更 → 正确做法是以 `tests/level1/test_version_sync.py` 的失败清单为准，收齐所有活动文档中的版本引用后再 Done。 | session-2026-04-17-183258.md |
| 14 | git add 文件到 .gitignore 后不会自动从已跟踪文件中移除 → 根因是 .gitignore 只影响未跟踪文件，已 commit 的文件需手动 `git rm --cached` → 错误判断是"加了 .gitignore 就够了" → 正确做法是 `git rm --cached <path>` + commit 才能真正从远端清除 | session-2026-04-18-001018.md |
| 15 | 测试 1 failed / 68 passed 时误以为只需修代码 → 实际是本地 CLAUDE.md 版本引用未同步 → 应先看具体失败断言再定位根因，而非凭直觉猜测 | session-2026-04-14-213511.md |
| 16 | 以为 Hook 已经是主要注入路径 → 实际 CLAUDE.md 的 @rules/ 引用才是 1509 行加载的真凶 → Hook 的精简设计被上层完全绕过 → 排查问题时应追踪完整注入链而非假设某层生效 | session-2026-04-18-160344.md |
| 17 | Task#171 产出文件在 .claude/ 目录下被 gitignore 拦截 → 符合预期（本地运行时产物不提交），但需注意 commit 时只 add 非排除目录 | session-2026-04-18-202315.md |
| 18 | CLAUDEMD @rules/ 测试误匹配自身描述行 → 根因是测试匹配了包含"行为铁律"的行本身 → 排除含 Push/行为铁律 关键字的行后修复 | session-2026-04-18-210137.md |
| 19 | context_monitor.py 模块级 sys.exit(0) 导致 import 崩溃 → 用 exec(code, dict) 绕过模块级代码执行 | session-2026-04-18-213522.md |
| 20 | stop_snapshot.py 第49行 {diff_stat} 非 f-string → 字面量输出 → 修复为 f-string | session-2026-04-18-213522.md |
| 21 | _has_gwt_keywords 是大小写敏感的子串匹配（非正则），GIVEN/WHEN/THEN 大写不匹配 → 测试对齐实际行为 | session-2026-04-18-213522.md |
| 22 | index_items 条目带 `rules/` 前缀但 rules_files 是纯文件名 → 需 `replace('rules/', '')` 再比较 | session-2026-04-18-213522.md |
| 23 | stop_snapshot.py 用 `.diwu/recording`（无尾部斜杠）非 `.diwu/recording/` | session-2026-04-18-213522.md |
| 24 | stop_decision.py 所有运行时路径通过参数传入（TASK_JSON, SETTINGS_PATH），无硬编码 | session-2026-04-18-213522.md |
| 25 | stop_archive_agg.py archive 路径动态构建（`os.path.join(archive_dir, "archive")`）非硬编码 `.diwu/archive/` | session-2026-04-18-213522.md |
| 26 | file-layout.md / workflow.md / session.md / pitfalls.md / templates.md / verification.md 资产模板是**配置层描述**，不含 `.diwu/` 运行时路径；运行时路径仅在 CLAUDE.md 模板中 | session-2026-04-18-213522.md |
| 27 | explorer/implementer Agent 不出现在 `claude agents` 输出 → 初步怀疑文件缺失或路径错误 → 实际是 frontmatter 缺少 `name` 必填字段 → Claude Code Agent 加载要求 name 字段存在，缺省静默跳过而非报错。应在 agent 模板和测试中强化此约束。 | session-2026-04-19-202053.md |
| 28 | sed 替换带引号路径时吃掉引号 → 多次修复 context_monitor.py 等文件的 open() 参数 → 正确做法：sed replacement 中显式保留引号或改用 Edit 工具精确替换 | session-2026-04-18-213522.md |

## 分层未拆清

| # | 现象 → 根因 → 正确做法 | 来源 Session |
|---|---------------------------|-------------|
| 1 | 完成 hook 脚本后才做 README 同步检查 → 应在方案设计阶段就把"所有层级 README 同步"列入实施步骤 | session-2026-04-10-194532.md |
| 2 | 审计前以为 inject_errors_decisions.py 有 B3 PID bug → 实际该脚本的 `_ctx_path()` 定义了但 main() 根本没调用它（纯读取逻辑无需状态持久化） → 不要看到 PID 就默认是 bug，需确认代码路径是否真的执行到 | session-2026-04-10-232559.md |
| 3 | 发现 17 个测试失败时，先区分是「代码 bug」还是「测试自身 bug」，再分别定位——代码本身无问题，测试断言/路径/条件过期才是根因 | session-2026-04-11-003355.md |
| 4 | README Hooks 表检测找了反引号格式但实际表头无反引号——匹配规则必须基于实际 DOM 结构，不能假设格式 | session-2026-04-11-003355.md |
| 5 | 一开始把 verifier 按"核心层"直接等同于"插件级"部署 → 根因是把职责分层和部署分层混为一谈 → 错误判断：认为核心能力应和 7 个领域专家一起放在根目录 `agents/` → 正确做法：核心层与部署层分开建模；verifier 虽属于核心层，但因依赖 `.claude/task.json` 与项目状态机，应部署在 `.claude/agents/` | session-2026-04-14-184011.md |
| 6 | 5 个审查代理中 4 个同时发现 assets 模板与 .claude 规则文件不同步的问题（settings.json 残留），但直到所有代理完成前没有统一汇总 → 根因：未在子代理启动时明确指定"只报告问题、不修复"，导致修复动作分散在主 agent 后续处理中 → 正确做法：审查类子代理只报告发现，修复由主 agent 统一处理；或者在发现根因相同的问题时立即中止冗余审查 | session-2026-04-10-005323.md |
| 7 | 一开始只改了本地 `.claude/rules/templates.md`（gitignore 文件），遗漏了 `/dinit` 模板源 `assets/dinit/assets/rules/templates.md` → 根因是把"本地工作副本"和"分发源文件"混为一谈 → 错误判断：改了本地就以为完成了 → 正确做法：涉及 rules/ 文件修改时，必须同步检查 `assets/dinit/assets/rules/` | session-2026-04-16-143055.md |
| 8 | 容易把 `project-pitfalls.md` 当成 rules 目录里的普通规则文件处理 → 实际它属于 `.diwu/` 运行时文件，不该走 `.claude/rules/` 的存在性检查 → 正确做法是为该条目单独判定存在路径，并用任务级测试覆盖运行态索引输出。 | session-2026-04-17-165731.md |
| 9 | 初版方案将 task 内容嵌入 recording → 用户指出会增加 token 消耗且不支持多任务并行 → 改为独立 tasks/{id}.json 文件方案 | session-2026-04-18-160344.md |
| 10 | Edit tool 的 old_string 匹配失败（templates.md 大段替换）→ 多次尝试精确匹配均失败 → 根因是工具对特殊字符或不可见空白敏感 → 改用 python 脚本基于位置(start/end index)替换成功。大段文本替换优先用脚本工具。 | session-2026-04-19-202053.md |
| 11 | 大批量实施后忘记回写 task.json 状态 → 导致后续 session 重复排查已完成任务 → 根因是缺少自动化检测机制 → 解决：在 stop_integrity.py 增加 git 活动 vs task.json 状态一致性检查，Stop 每轮自动提醒。应在所有工作流项目中引入此模式。 | session-2026-04-19-212043.md |
| 12 | task_created_validate.py 重构时意图保留 `if stack.pop()` 但实际 `return True` 后无法执行到 pop → 正确逻辑是 return True 后无需 pop（已 return 的函数不会继续） → 修正后 14 个测试全绿。函数内提前 return 时不需要手动 pop/backtrack。 | session-2026-04-19-213554.md |
| 13 | 初始将文件命名为 .diwu/dtask（无扩展名）→ 用户纠正为 .diwu/dtask.json → 应在命名决策时确认文件类型约定（JSON 文件保留 .json 后缀） | session-2026-04-18-213522.md |

## 环境漂移

| # | 现象 → 根因 → 正确做法 | 来源 Session |
|---|---------------------------|-------------|
| 1 | 目录路径写 .claude/ 而非 .diwu/ → 被仓库中大量残留旧口径文档误导 → 误判为运行态路径正确 → 应先核实目录现状再设计方案，不能仅依赖规则文件 | session-2026-04-18-145431.md |
| 2 | python 命令不存在需用 python3 → macOS 默认无 python alias → 统一使用 python3 | session-2026-04-18-210137.md |
| 3 | subagent_start.py 含 3 处 .claude/ 旧路径（Task#165 迁移遗漏）→ 该文件在 Task#165 批量替换时可能因当时内容不同而未被 grep 命中 → 跨任务修改后应做全量 grep 验证而非仅检查目标文件列表。 | session-2026-04-18-213522.md |

## 路由护栏契约

| # | 现象 → 根因 → 正确做法 | 来源 Session |
|---|---------------------------|-------------|
| 1 | Claude Code 插件的 plugin.json 中每个组件（commands/skills/agents/hooks）都需要显式声明，不会自动扫描子目录 → 遗漏任何组件字段等于该组件不存在 | session-2026-04-14-161449.md |
| 2 | Task#191 Skills symlink 设计三易其稿： 1. 初版（已提交）：目录级 symlink `.agents/skills/` → `../../skills/`（整个 skills/ 目录） → 问题：用户自定义 skill 写入插件目录，污染代码库 2. 二版（本次 session 初修）：文件级 symlink `{name}_SKILL.md` → `../../skills/{name}/SKILL.md`（单个文件）→ 问题：维护成本高，每个 skill 一个 symlink 3. 终版（用户确认）：直接硬链接，skills 内容直接放在 `.agents/skills/<name>/SKILL.md`，与插件目录解耦。优点：无 symlink 维护负担、无跨平台兼容问题、用户自定义 skill 与插件 skill 隔离。 | session-2026-04-18-213522.md |

## 架构认知

| # | 现象 → 根因 → 正确做法 | 来源 Session |
|---|---------------------------|-------------|
| 1 | v2 注入架构大幅简化了 user_prompt_submit.py：全文注入 → 核心不变量内联 + 9 元组索引，测试必须跟随架构变更重写断言而非微调旧断言 | session-2026-04-18-213522.md |

## 使用方式

1. **开工前必查**：出现异常时先对照本表，排除已知误判
2. **持续积累**：每次 session 结束时如有新踩坑，按四段式格式记录
3. **归档时自动聚合**：`/darc` 执行归档时自动扫描 recording 并追加到此文件

## 与 Layer 1 泛化模式的映射

| Layer 2 类别 | 对应 Layer 1 泛化模式 |
|-------------|----------------------|
| 验证误读 | L1-5 验证误读 |
| 分层未拆清 | L1-6 分层未拆清 |
| 环境漂移 | L1-1 环境漂移 |
| 路由护栏契约 | L1-4 路由/护栏/契约 |
