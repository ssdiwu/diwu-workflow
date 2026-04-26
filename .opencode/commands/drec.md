---
description: 快速记录 Session 踩坑经验或生成 recording 草稿，支持四段式格式和最低合法答案
argument-hint: [session 描述（可选）]
allowed-tools: Read, Write, Edit, Bash
---

# /drec — Session 记录

快速触发 Session 记录，按照 drec skill 规范输出 recording 草稿。

## 触发方式

- `/drec` — 生成当前 session 的 recording 模板
- `/drec 本次修复了登录 bug` — 带描述生成 recording

## 执行步骤

### Step 1：获取时间戳

运行命令获取真实时间：
```bash
date '+%Y-%m-%d %H:%M:%S'
```

### Step 2：生成 recording 草稿

根据当前对话上下文，按以下格式生成 recording 内容：

```markdown
## Session YYYY-MM-DD HH:MM:SS

### Task#N: [标题] → [状态]
**实施内容**: 
- [工作项1]
- [工作项2]

**验收验证**: 
- [x] [acceptance] ([验证方法])

**提交**: commit [hash]（如有）

### 下一步: [计划]

### 本次踩坑/经验
- [类别] 现象描述 → 根因分析 → 错误判断 → 正确做法
```

**类别标签**：`环境漂移` / `数据缺口` / `读层现象` / `路由护栏契约` / `验证误读` / `分层未拆清` / `其他`

### Step 3：写入文件

写入路径：`.diwu/recording/session-YYYY-MM-DD-HHMMSS.md`

**禁止 YAML front matter**：文件第一行必须是 `## Session ...`，不能以 `---` 开头。

### Step 4：最低合法答案（无显著误判时）

```markdown
### 本次踩坑/经验

本轮无显著误判，实施路径符合预期。
```

## 四段式格式示例

```markdown
- [环境漂移] 本地测试通过但 CI 超时 → CI 环境缺少代理配置 → 误判为代码性能问题 → 应先检查 CI 环境变量
- [验证误读] 单元测试全部 PASS 但功能不工作 → mock 了关键依赖 → 误判为已完成 → 应补充集成测试
```

## Checkpoint 格式（大任务中途）

```markdown
### Checkpoint @ 步骤3/8
进度: 完成 auth 模块重构，payment 模块进行中
已修改: src/auth.ts(+120/-80)
下一步: 步骤4 payment 模块重构
回滚方式: git checkout -- src/auth.ts
```

## 不做的事

- 不修改 dtask.json（状态更新由 workflow 负责）
- 不自动提交代码
