---
description: 记录架构决策（ADR），输出到 .doc/adr/ 目录
argument-hint: [决策描述（可选）]
allowed-tools: Read, Write, Glob, Bash
---

# /dadr — 架构决策记录

## Step 1：接收决策描述

若用户已在命令参数中描述决策，直接进入 Step 2。否则询问用户正在面临什么架构决策。

## Step 2：澄清问题

提出 2-3 个问题，聚焦：
- 考虑过哪些备选方案？
- 有哪些约束条件（时间、团队能力、现有技术栈）？
- 各方案的核心取舍是什么？

## Step 3：确定 ADR 编号

检查 `.doc/adr/` 目录下已有文件，取最大编号 + 1。`.doc/adr/` 不存在时先创建目录。

## Step 4：生成并写入 ADR

文件命名：`.doc/adr/ADR-NNN-kebab-case-title.md`（NNN 三位数字补零）

ADR 格式参考以下示例的思维粒度：

```markdown
# ADR-001: 消息通知使用 WebSocket 而非短轮询

**Status**: Accepted
**Date**: 2026-02-25

## Context
用户消息通知需要近实时推送（产品要求延迟 < 2s）。当前 DAU 5 万，峰值并发 3000。
团队有 Socket.io 使用经验，服务器为单机 Node.js，暂无 Redis。
短轮询（1s 间隔）在峰值会产生 3000 QPS 额外负载，超出当前服务器承载上限。

## Options Considered
- **WebSocket (Socket.io)**: 长连接，服务端主动推送 — 延迟 < 200ms、服务端负载低 / 需处理断线重连，单机连接数上限约 1 万
- **短轮询 (1s interval)**: 客户端定时请求 — 实现简单 / 峰值 3000 QPS 额外负载，延迟最高 1s，不满足产品要求

## Decision
选择 WebSocket。3000 QPS 额外负载在当前架构下不可接受，且团队有 Socket.io 经验可控风险。

## Consequences
- ✅ 推送延迟 < 200ms，满足产品 SLA
- ⚠️ 单机连接数上限约 1 万，DAU 超过 3 万时需引入 Redis Adapter 做横向扩展
```

示例中的思维粒度要点：
- Context 有具体数字（DAU、并发、延迟阈值、QPS），不是"系统需要通知功能"
- Options 的缺点是具体的技术风险和触发条件，不是"复杂度高"
- Consequences 的 ⚠️ 有触发条件（DAU 超过 3 万）和解决路径（Redis Adapter）

## Step 5：写入后提示

- 显示生成的文件路径
- 提示：如需关联到某个任务，可在 task.json 对应任务的 steps 中注明 "参见 .doc/adr/ADR-NNN"

## 边界情况

更新已有 ADR 状态（如 Proposed → Accepted）：找到对应文件，只修改 Status 行。
