# 决策记录

## DEC-001 2026-02-27 引入 decisions.md 分层记忆
**背景**：recording.md 混合了 session 流水和设计决策，Agent 恢复上下文时需要扫描全文才能找到"为什么这样设计"
**决策**：新增 .diwu/decisions.md 专门记录设计决策，recording.md 只记录 session 流水
**备选方案**：继续用 recording.md 混合记录 / 用 /dadr 记录所有决策
**理由**：recording.md 回答"发生了什么"，decisions.md 回答"为什么这样设计"，两者检索意图不同；/dadr 是项目级架构决策（给人看），decisions.md 是工作流级设计选择（给 Agent 用）

## DEC-002 2026-02-27 归档触发接入执行流程
**背景**：归档规则定义在 file-layout.md，但 workflow.md Session 启动流程没有显式触发，导致 recording.md 超过阈值后从未被归档
**决策**：在 workflow.md 上下文恢复步骤中加入显式归档检查（recording.md 超5条、dtask.json 超20条）
**备选方案**：依赖 Agent 自觉读 file-layout.md 并执行归档
**理由**：规则必须接入执行路径才会被执行；被动文档不等于主动触发

## DEC-003 2026-02-27 SessionStart hook 去除 recording.md 快照，Stop 快照改为条件触发
**背景**：SessionStart 和 Stop 都无条件写快照，导致 recording.md 充满"无进行中任务"噪音，短会话频繁开关时尤为严重
**决策**：SessionStart 只保留 session ID 写入（SubagentStop 需要），移除 recording.md 快照；Stop 快照改为条件触发（有活跃任务才写）
**备选方案**：保留所有快照 / 完全移除所有快照
**理由**：Stop 拦截 hook 已覆盖"确保 recording.md 有记录"的职责；快照的唯一剩余价值是任务状态变化追踪，无活跃任务时无需追踪

## DEC-004 2026-02-28 规则来源迁移：静态文件 → 插件 UserPromptSubmit hook 注入
**背景**：~/.diwu/rules/ 和 assets/dinit/assets/rules/ 存在两份副本，修改时需同步两处，存在漂移风险。同时 lessons.md（Agent 错误模式记录）需要一个可靠的强制注入机制。另发现：~/.diwu/rules/*.md 被 Claude Code 自动加载，@rules/ import 本就冗余。
**决策**：新增 UserPromptSubmit hook（非 SessionStart，后者不支持 additionalSystemPrompt），读取插件 assets/rules/*.md 注入；检测 .diwu/lessons.md 追加注入；删除 ~/.diwu/rules/*.md 五个文件（避免自动加载与 hook 注入双重重复）；删除 CLAUDE.md 中 @rules/ 五行冗余引用。
**备选方案**：A. sync 脚本（仍是两份，需手动触发）；B. SessionStart + CLAUDE_ENV_FILE（不支持 additionalSystemPrompt）；C. 保持现状（接受漂移）
**理由**：UserPromptSubmit 每轮注入，比 SessionStart 更可靠；additionalSystemPrompt 已有 SubagentStop 先例；~/.diwu/rules/ 自动加载机制发现使得"保留备份"会造成双重注入，必须删除源文件；已知边界：注入内容不传递给 subagent
