# Refresh Protocol — 刷新模式操作手册

> 当 `.claude/CLAUDE.md` 已存在时，`/dinit` 进入刷新模式。本协议定义增量更新的完整步骤。

## 前置条件

- `.claude/CLAUDE.md` 存在（否则应走初始化模式）
- `${CLAUDE_PLUGIN_ROOT}` 指向插件根目录

## 操作步骤

### 1. 检测并插入「工作流规则」章节

**目的**：确保 CLAUDE.md 包含规则索引，使 @rules/ 引用可用。

**操作**：
1. 读取 `.claude/CLAUDE.md`
2. 搜索是否存在 `## 工作流规则` 标题
3. 如果不存在，在 `## 核心原则` 之前插入：

```markdown
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
```

**注意**：上述列表中的规则文件名和数量应来自 `rules-manifest.json` 的 `rules` 数组，不应硬编码。如果 manifest 中有新增规则文件，此处也应同步更新。

### 2. 检测并插入「规则引用说明」章节

**目的**：确保 CLAUDE.md 末尾有规则引用说明，解释 @rules/ 的加载机制。

**操作**：
1. 搜索是否存在 `## 规则引用说明` 标题
2. 如果不存在，在文件末尾追加：

```markdown

## 规则引用说明

本项目使用 @rules/ 引用自动加载工作流规则。规则文件位于 `.claude/rules/` 目录，由 UserPromptSubmit hook 在每次对话开始时注入。
```

### 3. 更新「项目结构」章节

**目的**：将代码库扫描结果写入 CLAUDE.md，保持项目结构信息最新。

**操作**：
1. 用 Step 1.5 的扫描结果替换 `<!-- SCAN_RESULT_PLACEHOLDER -->` 占位符
2. 如果占位符不存在但「项目结构」章节内容明显过旧（如缺少当前存在的目录），替换整个章节内容

### 4. 迁移 recording.md 到 recording/ 目录

**目的**：将旧版单文件 session 记录迁移为多文件目录结构。

**操作**：
1. 检查 `.claude/recording.md` 是否存在
2. 如果存在：
   - 读取内容，按 `## Session YYYY-MM-DD HH:MM:SS` 分隔符识别所有 session
   - 创建 `.claude/recording/` 目录（如不存在）
   - 将每个 session 写入独立文件 `recording/session-YYYY-MM-DD-HHMMSS.md`
   - 迁移完成后将原 `recording.md` 重命名为 `recording.md.backup`
3. 如果不存在，跳过

### 5. 同步规则文件

**目的**：确保项目使用最新的规则文件。

**操作**（详见 `asset-sync.md` §rules 同步）：
1. 清理旧文件：删除 `.claude/rules/` 下不在 `rules-manifest.json` 中的文件
2. 读取 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/rules-manifest.json`
3. 按 `rules` 数组逐一复制到 `.claude/rules/`（覆盖旧版本）
4. 输出结果：列出已同步的规则文件数量和名称

### 6. 同步项目级 Agent

**目的**：确保项目使用最新的 agent 定义（含新增的 verifier 等）。

**操作**（详见 `asset-sync.md` §agents 同步）：
1. 创建 `.claude/agents/` 目录（如不存在）
2. 动态扫描 `${CLAUDE_PLUGIN_ROOT}/assets/dinit/assets/agents/` 下所有 `.md` 文件
3. 将每个模板文件复制到 `.claude/agents/`（覆盖旧版本）
4. 输出结果：列出已复制的 agent 文件名及数量

## 输出格式示例

刷新完成后输出：

```
=== 刷新结果 ===

Step 0 检测：
- .claude/CLAUDE.md 已存在 → 刷新模式

Step 1（已跳过）：项目信息已在 CLAUDE.md 中，无需重复收集

Step 1.5 代码库扫描：...（扫描摘要）

Step 2（旧版迁移检测）：未检测到旧版 → 跳过

Step 3（CLAUDE.md 更新）：
- ✅ "工作流规则" 章节 → 已存在
- ✅ "规则引用说明" 章节 → 已存在
- ✅ "项目结构" 功能域表格 → 数量与扫描一致，无需更新
- ✅ "技术栈" 章节 → 已用扫描结果补充（前端 React/Vite、Malli、Aero、aleph 等关键依赖）

Step 4（可选）：...

最终状态确认：
- .claude/rules/ 13 个文件，无备份残留
- .claude/recording/ 目录存在
- .claude/CLAUDE.md 技术栈已更新
- .claude/agents/ 3 个文件（explorer, implementer, verifier）
```

## 刷新模式的边界

**不做的事**：
- 不重新收集项目信息（除非用户主动要求更新）
- 不覆盖用户在 CLAUDE.md 中的自定义章节（只增补标准章节）
- 不修改 `.claude/task.json` 中的任务数据
- 不重新生成 `init.sh` 或 `smoke.sh`
