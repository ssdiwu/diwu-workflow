# diwu-workflow 架构约束

> **规则约束级别说明**：本文件定义架构约束的核心规则。除非特别标注 `[建议]`，否则都是必须遵守的约束。

## Constraints

| Dimension    | Constraint                                                                                       | Verification                                                     |
|--------------|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| Business     | 插件命令（commands/*.md）只描述行为，不包含实现逻辑；实现逻辑在 skills/ 或 assets/ 中            | commands/ 文件内无可执行代码，仅有 Markdown 指令                  |
| Temporal     | plugin.json 的 version 字段必须在功能变更提交时同步更新，不得事后单独提交；版本号遵循语义化版本规范（X.Y.Z）：X=主版本（破坏性变更），Y=次版本（新增功能），Z=修订号（bug修复） | 每个功能 commit 的 diff 包含 plugin.json version 变更；版本号格式符合 semver |
| Cross-platform | hooks.json 中的路径引用必须兼容 macOS/Linux；禁止使用 Windows 路径分隔符                       | 路径中无 `\` 分隔符                                              |
| Concurrency  | 插件文件为静态资源，无并发写入场景；多 session 同时使用同一插件时以磁盘文件版本为准              | 无运行时状态，无需并发控制                                        |
| Perception   | smoke.sh 验证 JSON 合法性；所有 JSON 文件必须通过 `python3 -m json.tool` 校验                  | smoke.sh 全部 check 通过，exit 0                                  |

## State Machines

插件文件发版状态机：

| Current State | Event            | New State  |
|---------------|------------------|------------|
| dev           | 提交含 version++ | published  |
| published     | 发现 bug         | dev        |
| published     | 直接修改内容无版本号 | invalid（禁止）|

## Boundaries

| Type     | Internal                               | External                         | Crossing Method          |
|----------|----------------------------------------|----------------------------------|--------------------------|
| Domain   | commands/, assets/, skills/, hooks/    | Claude Code 宿主环境             | plugin.json 描述注册       |
| Platform | .claude-plugin/ 插件描述               | 用户的 ~/.claude/ 目录            | 插件安装机制               |
| Data     | assets/dinit/assets/（模板源文件）      | 用户项目的 .claude/（生成产物）    | /dinit 命令触发复制        |

## Degradation Paths

| Dependency          | Failure                          | Fallback                               | User Perception              |
|---------------------|----------------------------------|----------------------------------------|------------------------------|
| 插件缓存             | cache 目录不存在                  | /dinit 报错提示重新安装插件             | 明确报错，不静默失败          |
| Python3             | smoke.sh 中 python3 不可用       | JSON 校验跳过，打印警告                 | 校验弱化，功能不受影响        |

## Data Ownership

Source of Truth: `.claude-plugin/plugin.json`（版本、命令列表、元数据）
生成产物链: `assets/dinit/assets/*.template` → 用户项目 `.claude/`（通过 /dinit）
冲突策略: 模板文件只写，用户项目文件不覆盖已存在内容（除非用户明确要求）

## 五维约束设计参考

基于产品特性，在设计阶段识别以下五个维度的约束：

| 维度 | 判断问题 | 例子 |
|-----|---------|------|
| **业务约束** | 100 年后还成立吗？ | 「原始录音不可变，摘要可重新生成」 |
| **时序约束** | 有没有执行路径可以绕过这个规则？ | 「停止录音后同一 session 不可恢复」 |
| **跨端约束** | 如果两个端定义不同，这是 bug 吗？ | 「CardType 在所有端完全一致」 |
| **并发约束** | 两个线程同时做这件事会出问题吗？ | 「状态机事件串行处理」 |
| **感知约束** | 超过这个阈值，用户会注意到吗？ | 「音频源切换 < 100ms」 |

使用方式：新增功能模块时，逐行过上表，把命中的约束写入本文件的 Constraints 表。
