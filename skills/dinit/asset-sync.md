# Asset Sync Protocol — 资产分发协议

> 定义 `/dinit` 如何发现、复制和同步可分发资产（rules、agents）到用户项目。

## 资产类型总览

| 类型 | 源目录 | 目标目录 | 清单来源 | 冲突策略 |
|------|--------|---------|---------|---------|
| rules | `${PLUGIN}/assets/dinit/assets/rules/` | `.claude/rules/` | `rules-manifest.json` | 覆盖旧版本 |
| agents | `${PLUGIN}/assets/dinit/assets/agents/` | `.claude/agents/` | 动态扫描 `*.md` | 覆盖旧版本 |

其中 `${PLUGIN}` = `${CLAUDE_PLUGIN_ROOT}` 或插件根目录的绝对路径。

## Rules 同步

### 发现方式

读取 `assets/dinit/assets/rules-manifest.json`，取 `rules` 数组：

```json
{
  "version": 2,
  "rules": [
    "README.md", "mindset.md", "judgments.md", "workflow.md",
    "verification.md", "correction.md", "pitfalls.md", "session.md",
    "task.md", "exceptions.md", "templates.md", "constraints.md",
    "file-layout.md"
  ]
}
```

### 同步步骤

1. **清理孤立文件**：遍历 `.claude/rules/` 下现有文件，删除不在 `rules` 数组中的文件（如旧的 `states.md`）
2. **逐个复制**：按 `rules` 数组顺序，从源目录复制到 `.claude/rules/`（覆盖同名旧版本）
3. **验证数量**：确认 `.claude/rules/` 下的 `.md` 文件数量等于 `rules` 数组长度

### 为什么用 manifest 而非动态扫描？

- Rules 有严格的排序语义（README.md 必须在前作为索引）
- Rules 有版本字段（`version: 2`），需要显式清单保证跨版本一致性
- 未来可能需要 per-file 元数据（如 deprecated 标记）

## Agents 同步

### 发现方式

动态扫描 `${PLUGIN}/assets/dinit/assets/agents/` 下所有 `.md` 文件：

```bash
ls "${PLUGIN}/assets/dinit/assets/agents/"*.md
```

当前结果：`explorer.md`, `implementer.md`, `verifier.md`

### 同步步骤

1. 创建 `.claude/agents/` 目录（如不存在）：`mkdir -p .claude/agents/`
2. 逐个复制：对每个 `*.md` 文件，从源目录复制到 `.claude/agents/`（覆盖同名旧版本）
3. 输出结果：列出文件名和总数

### 为什么用动态扫描而非 manifest？

- Agents 是扁平列表，无排序依赖
- 新增 agent 时只需在 `agents/` 目录放一个 `.md` 文件，零配置成本
- 符合"约定优于配置"原则：目录即清单

### Agent 文件格式要求

每个 agent 模板必须满足：

1. YAML frontmatter 包含 `name` 字段（Claude Code 加载必需）
2. frontmatter 包含 `description` 字段
3. 推荐包含：`permissionMode` / `memory` / `maxTurns` / `tools` / `model`
4. 文件编码为 UTF-8

不符合格式的文件会被 Claude Code 跳过不加载，但 `/dinit` 仍会复制（由运行时验证发现）

## CLAUDE.md 规则列表动态生成

### 问题背景

`claude-md-portable.template` 中的 `@rules/` 引用列表需要与 `rules-manifest.json` 保持一致。三处维护同一份列表容易漂移。

### 解决方案

在 template 的规则列表上方保留默认列表（作为 fallback 和可读性），但在 `/dinit` 执行时动态替换：

1. 读取 `rules-manifest.json` 的 `rules` 数组
2. 对每项生成 `- @rules/{filename} - {描述}` 行
3. 替换 template 中 `<!-- RULES_PLACEHOLDER -->` 到 `<!-- END_RULES_PLACEHOLDER -->` 之间的内容
4. 如果锚点不存在，则在 `## 工作流规则` 章节下追加生成的列表

### Template 锚点格式

```markdown
## 工作流规则

<!-- RULES_PLACEHOLDER: 以下列表由 dinit 根据 rules-manifest.json 动态生成，请勿手动编辑 -->
详细规则见 @rules/ 目录：
- @rules/README.md - 规则速查索引
- ...（默认列表作为 fallback）
<!-- END_RULES_PLACEHOLDER -->
```

## 冲突策略统一说明

| 场景 | 策略 | 原因 |
|------|------|------|
| rules 文件已存在 | 覆盖 | 规则是插件提供的，用户不应直接修改 |
| agent 文件已存在 | 覆盖 | agent 定义是插件提供的，用户定制通过 description 调整 |
| dsettings.json 已存在 | **跳过** | 用户可能已调整参数，不覆盖 |
| project-pitfalls.md 已存在 | **跳过** | 用户/Stop hook 可能已填充内容 |
| decisions.md 已存在 | **跳过** | 用户的设计决策记录 |
| CLAUDE.md 已存在 | **增量更新** | 只增补标准章节，不覆盖自定义内容 |

## 扩展指南：新增资产类型

未来如果需要分发更多资产类型（如 hooks 配置、templates 等）：

1. 在 `assets/dinit/assets/` 下新建子目录（如 `hooks/`）
2. 在本协议中新增一行资产类型表
3. 在 `commands/dinit.md` 的 Step 3 中添加对应的同步逻辑
4. 如果需要显式清单（类似 rules），考虑升级 `rules-manifest.json` 为通用的 `asset-manifest.json`

不需要改任何已有代码——这就是动态扫描 + 表驱动设计的优势。
