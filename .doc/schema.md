# diwu-workflow 文档类型 Schema

- **定位**：PRD/Demo/ADR/Doc 四类文档的 README 索引格式定义
- **目标**：命令间传递信息的通用货币——README 索引行
- **版本**：0.8.0
- **创建**：2026-04-10
- **改写**：2026-04-10
- **状态**：当前主版本

---

## 最小公约数

所有 README 索引行必须包含以下三列：

| 列名 | 格式 | 说明 |
|-----|------|------|
| `文件` | 相对路径或文件名 | 文件的可寻址标识 |
| `摘要` | 一句话 | 命令间传递的核心信息，供下游命令决定是否精读 |
| `状态` | 见各类型定义 | 当前状态，统一用英文枚举 |

---

## PRD（/dprd 输出）

**文件命名**：`PRD-{kebab-case}.md`
**README 路径**：`.doc/prd/README.md`

| 列名 | 格式 | 说明 |
|-----|------|------|
| `文件` | `PRD-{kebab-case}.md` | - |
| `摘要` | 一句话功能描述 | - |
| `demos` | `demo-id1, demo-id2` 或 `-` | 对应 `/ddemo` 的输入参数，kebab-case |
| `状态` | `draft \| review \| approved` | - |

**README 示例行**：
```
| PRD-ai-meeting-citation.md | AI 回复引用历史会议记录，支持点击查看原文 | demo-prompt-citation | draft |
```

**下游消费**：`/ddemo` 读取 `demos` 列，逐项执行；`/dtask` 读取 `摘要` 列了解功能背景。

---

## Demo（/ddemo 输出）

**文件命名**：`DEMO-{kebab-case}-prd.md`
**README 路径**：`.doc/demo/README.md`

| 列名 | 格式 | 说明 |
|-----|------|------|
| `文件` | `DEMO-{kebab-case}-prd.md` | - |
| `摘要` | 验证什么不确定性（一句话） | - |
| `通过标准` | `指标 > 阈值`，多条用 `;` 分隔 | 量化标准，供 `/dtask` acceptance 引用 |
| `状态` | `pending \| passed \| failed` | - |

**README 示例行**：
```
| DEMO-prompt-citation-prd.md | Prompt 能否稳定输出引用标记格式 | 准确率 > 90%; 幻觉率 < 5% | pending |
```

**下游消费**：`/dtask` 读取 `通过标准` 列，作为集成任务 acceptance 的量化依据。

---

## ADR（/dadr 输出）

**文件命名**：`ADR-NNN-{kebab-case}.md`（NNN 三位数字补零）
**README 路径**：`.doc/adr/README.md`

| 列名 | 格式 | 说明 |
|-----|------|------|
| `编号` | `ADR-NNN` | - |
| `标题` | 决策标题 | - |
| `状态` | `Proposed \| Accepted \| Deprecated \| Superseded` | - |
| `摘要` | 一句话决策摘要 | 供 `/dprd` Q5 快速判断是否需要精读 |

**README 示例行**：
```
| ADR-001 | 消息通知使用 WebSocket | Accepted | 峰值 3000 QPS 超短轮询承载上限，团队有 Socket.io 经验 |
```

**下游消费**：`/dprd` Q5 读取 `摘要` 列，了解已有架构决策，避免重复设计。

---

## Doc（/ddoc 输出）

**文件命名**：`{domain}.md`（领域驱动）或 `{layer}.md`（分层）
**README 路径**：`.doc/README.md`

| 列名 | 格式 | 说明 |
|-----|------|------|
| `文件` | 文件名 | - |
| `覆盖范围` | 一句话，含关键词 | 供下游命令判断是否需要精读 |
| `最后更新` | `YYYY-MM-DD` | - |

**README 示例行**：
```
| auth.md | 认证域：JWT 结构、登录流、权限模型 | 2026-02-26 |
```

**下游消费**：`/dprd` Q5、`/ddemo` Step 2 读取 `覆盖范围` 列，定向读取相关文件。

---

## 命令间接口契约

| 上游命令 | 输出字段 | 下游命令 | 消费方式 |
|---------|---------|---------|---------|
| `/dprd` | PRD README `demos` 列 | `/ddemo` | 读取 demo_id 列表，逐项执行 |
| `/ddemo` | Demo README `通过标准` 列 | `/dtask` | 引用为 acceptance 量化标准 |
| `/dadr` | ADR README `编号 + 摘要` 列 | `/dprd` | Q5 读取，了解已有架构决策 |
| `/ddoc` | .doc/README `覆盖范围` 列 | `/dprd` `/ddemo` | Q5/Step 2 读取，了解现有系统能力 |

**备注**：`/dcorr` 是独立工具，不参与生产链——它按纠偏协议恢复偏航状态，不产出 PRD/Demo/ADR/Doc 四类文档。
