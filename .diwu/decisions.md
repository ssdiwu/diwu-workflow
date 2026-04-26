# 设计决策记录

## 格式

每个决策记录包含：
- **日期**：决策日期
- **决策**：具体决策内容
- **背景**：为什么需要这个决策
- **选项**：考虑过的选项
- **选择**：最终选择的方案
- **理由**：选择的理由
- **影响**：决策的影响

## 决策记录

### 2026-03-20: 从 Claude Code 迁移到 opencode

**决策**：将 diwu-workflow 从 Claude Code 插件转换为 opencode 原生格式
**背景**：需要验证 opencode 的插件架构，同时保持双平台兼容
**选项**：
1. 完全迁移到 opencode
2. 保持 Claude Code 版本，opencode 版本作为实验
3. 双平台兼容，新建目录验证
**选择**：选项 3 - 双平台兼容，新建目录验证
**理由**：
- 保留原 Claude Code 版本作为稳定版本
- 在新目录验证 opencode 版本的可行性
- 避免影响现有用户的使用
**影响**：
- 创建 `/Users/diwu/Documents/codes/Githubs/opencode-diwu-workflow`
- 需要维护两个版本的代码
- 可以并行测试两个平台的功能

### 2026-03-20: TypeScript 插件重写

**决策**：将 Python hooks 重写为 TypeScript 插件
**背景**：opencode 使用 TypeScript 插件系统，不支持 Python hooks
**选项**：
1. 全部重写为 TypeScript
2. 核心 hooks 重写，次要的简化
3. 利用 Claude Code 兼容层
**选择**：选项 1 - 全部重写为 TypeScript
**理由**：
- 最干净的实现方式
- 完全适配 opencode 的 Plugin 系统
- 避免兼容性问题
**影响**：
- 需要学习 opencode 的 Plugin API
- 需要将 Python 逻辑转换为 TypeScript
- 可能需要调整状态持久化方式

### 2026-03-20: Agent 架构重新设计

**决策**：利用 opencode 的 Primary/Subagent 双层架构重新设计 agents
**背景**：opencode 的 agent 系统与 Claude Code 不同
**选项**：
1. 直接迁移 + 调整格式
2. 重新设计 agent 架构
3. 先保持现有两个 agent
**选择**：选项 2 - 重新设计 agent 架构
**理由**：
- opencode 支持更灵活的 Primary/Subagent 架构
- 可以设计更专业的 agent 角色
- 提供更好的权限控制
**影响**：
- 创建 3 个 agent：build、plan、diwu-expert
- build 和 plan 作为 Primary agents（Tab 切换）
- diwu-expert 作为 Subagent（@调用）
- 提供更细粒度的权限控制

### 2026-03-20: 状态持久化使用 .opencode/state/

**决策**：使用 .opencode/state/ 目录存储临时状态
**背景**：原系统使用 /tmp/ 目录，跨平台兼容性差
**选项**：
1. 使用 .opencode/state/ 目录
2. 继续使用 /tmp/ 目录
3. 混合方案：持久化用项目目录，临时用 /tmp/
**选择**：选项 1 - 使用 .opencode/state/ 目录
**理由**：
- 项目级状态存储，便于清理和版本控制
- 跨平台兼容性好
- 符合 opencode 的最佳实践
**影响**：
- 需要修改 TypeScript 插件中的状态读写逻辑
- 需要创建 .opencode/state/ 目录
- 状态文件不会被 Git 跟踪（需要 .gitignore）

### 2026-03-20: 配置格式统一为 JSON

**决策**：将配置格式从 YAML + JSON 统一为 JSON/JSONC
**背景**：opencode 使用 JSON/JSONC 配置格式
**选项**：
1. 统一为 JSON/JSONC
2. 保持 YAML + JSON
3. 支持多种格式
**选择**：选项 1 - 统一为 JSON/JSONC
**理由**：
- opencode 原生支持 JSON/JSONC
- 配置格式更简洁
- 避免格式转换问题
**影响**：
- 需要将 dsettings.json 转换为 opencode.json 格式
- 需要调整配置读取逻辑
- 配置文件更易读和维护
