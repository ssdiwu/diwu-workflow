# Agent 错误模式记录

## 格式

每个条目包含：
- **日期**：错误发生日期
- **场景**：什么操作导致的错误
- **错误**：具体错误描述
- **修复**：如何修复
- **教训**：避免类似错误的规则

## 错误记录

### 2026-03-20: opencode 配置验证失败

**场景**：运行 `opencode debug config` 验证配置
**错误**：`Unrecognized key: "diwu-workflow"`
**修复**：移除 opencode.json 中的自定义字段，将配置移到插件中
**教训**：opencode 配置只支持标准字段，自定义字段需要放在插件或单独文件中

### 2026-03-20: TypeScript 插件语法错误

**场景**：使用 `npx tsc` 检查插件语法
**错误**：`Cannot find module '@opencode-ai/plugin'`
**修复**：在 .opencode 目录下运行 `npm install` 安装依赖
**教训**：TypeScript 插件需要正确的模块解析配置，确保依赖已安装

### 2026-03-20: Skills 未被加载

**场景**：运行 `opencode debug skill` 检查技能
**错误**：diwu-workflow 的 skills 未出现在列表中
**修复**：在 opencode.json 的 instructions 中添加 `.opencode/skills/*/SKILL.md`
**教训**：opencode 需要明确指定 skills 路径，不会自动发现 .opencode/skills/

## 预防规则

1. **配置验证**：修改 opencode.json 后立即运行 `opencode debug config` 验证
2. **依赖检查**：创建或修改 TypeScript 插件后运行 `npm install` 安装依赖
3. **Skills 测试**：添加新 skill 后运行 `opencode debug skill` 确认加载
4. **语法检查**：使用 `npx tsc --noEmit` 检查 TypeScript 语法
