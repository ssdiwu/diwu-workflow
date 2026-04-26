import type { Plugin } from "@opencode-ai/plugin"
import * as fs from "fs/promises"
import * as path from "path"
import { execSync } from "child_process"

// ============ 配置常量（默认值，可被 dsettings.json 覆盖）=========
const STATE_DIR = ".opencode/state"
const RULES_DIR = ".opencode/references"
const RECORDING_DIR = ".diwu/recording"
const TASK_JSON = ".diwu/dtask.json"
const SETTINGS_JSON = ".diwu/dsettings.json"

const DEFAULT_SETTINGS: Record<string, any> = {
  context_monitor_warning: 30,
  context_monitor_critical: 50,
  context_monitor_delay: 10,
  readonly_threshold: 15,
  review_limit: 5,
}

// 运行时 settings 缓存
let cachedSettings: Record<string, any> | null = null
let settingsDir: string | null = null

// ============ 辅助函数 ============

function getSetting(key: string, defaultValue?: any): any {
  if (cachedSettings && key in cachedSettings) {
    return cachedSettings[key]
  }
  if (key in DEFAULT_SETTINGS) {
    return DEFAULT_SETTINGS[key]
  }
  return defaultValue
}

async function loadSettings(directory: string): Promise<void> {
  try {
    const content = await fs.readFile(path.join(directory, SETTINGS_JSON), "utf-8")
    cachedSettings = JSON.parse(content)
    settingsDir = directory
  } catch {
    cachedSettings = {}
    settingsDir = directory
  }
}

async function readState(directory: string, filename: string): Promise<string | null> {
  try {
    const content = await fs.readFile(path.join(directory, STATE_DIR, filename), "utf-8")
    return content.trim()
  } catch {
    return null
  }
}

async function writeState(directory: string, filename: string, content: string): Promise<void> {
  const statePath = path.join(directory, STATE_DIR, filename)
  await fs.mkdir(path.dirname(statePath), { recursive: true })
  await fs.writeFile(statePath, content, "utf-8")
}

async function readFileSafe(directory: string, relativePath: string): Promise<string> {
  try {
    return await fs.readFile(path.join(directory, relativePath), "utf-8")
  } catch {
    return ""
  }
}

async function readTaskJson(directory: string): Promise<any> {
  try {
    const content = await fs.readFile(path.join(directory, TASK_JSON), "utf-8")
    return JSON.parse(content)
  } catch {
    return null
  }
}

async function getInProgressTaskSummary(directory: string): Promise<string | null> {
  const taskJson = await readTaskJson(directory)
  if (!taskJson?.tasks) return null
  const inProgressTask = taskJson.tasks.find((t: any) => t.status === "InProgress")
  if (!inProgressTask) return null
  const acceptance = inProgressTask.acceptance
    ? `\n验收条件:\n${inProgressTask.acceptance.map((a: string) => `- ${a}`).join("\n")}`
    : ""
  const steps = inProgressTask.steps
    ? `\n步骤:\n${inProgressTask.steps.map((s: string, i: number) => `${i + 1}. ${s}`).join("\n")}`
    : ""
  return `当前任务: ${inProgressTask.title}\n描述: ${inProgressTask.description}${acceptance}${steps}`
}

async function updateContextCounter(directory: string, toolName: string): Promise<{
  counter: number
  shouldWarn: boolean
  shouldCritical: boolean
  blockReason?: string
  readonlyCount?: number
}> {
  // 如果目录变了，重新加载 settings
  if (settingsDir !== directory) {
    await loadSettings(directory)
  }

  const contextWarning = getSetting("context_monitor_warning", 30)
  const contextCritical = getSetting("context_monitor_critical", 50)
  const readonlyThreshold = getSetting("readonly_threshold", 15)

  const counterStr = await readState(directory, "context-counter")
  const counter = counterStr ? parseInt(counterStr, 10) + 1 : 1
  await writeState(directory, "context-counter", counter.toString())

  const warned = await readState(directory, "context-warned")
  const critical = await readState(directory, "context-critical")

  const readonlyTools = ["Read", "Grep", "Glob"]
  const isReadonly = readonlyTools.includes(toolName)

  let readonlyCount = 0
  if (isReadonly) {
    const readonlyStr = await readState(directory, "context-readonly")
    readonlyCount = readonlyStr ? parseInt(readonlyStr, 10) + 1 : 1
    await writeState(directory, "context-readonly", readonlyCount.toString())
  } else {
    await writeState(directory, "context-readonly", "0")
    try {
      await fs.unlink(path.join(directory, STATE_DIR, "context-readonly-warned"))
    } catch {}
  }

  // CRITICAL 检查
  if (counter >= contextCritical && !critical) {
    await writeState(directory, "context-critical", "true")
    await writeState(directory, "context-critical-ts", Date.now().toString())
    await saveSessionCheckpoint(directory)
    return {
      counter,
      shouldWarn: false,
      shouldCritical: true,
      blockReason: `上下文已达 ${counter} 次工具调用（CRITICAL 阈值 ${contextCritical}）。已自动保存 checkpoint，建议开始新 session 继续。`,
      readonlyCount
    }
  }

  // WARNING 检查
  if (counter >= contextWarning && !warned) {
    await writeState(directory, "context-warned", "true")
    return { counter, shouldWarn: true, shouldCritical: false, readonlyCount }
  }

  return { counter, shouldWarn: false, shouldCritical: false, readonlyCount }
}

async function saveSessionCheckpoint(directory: string): Promise<void> {
  const timestamp = Date.now()
  const sessionFile = path.join(directory, RECORDING_DIR, `session-${timestamp}.md`)
  await fs.mkdir(path.join(directory, RECORDING_DIR), { recursive: true })
  const taskSummary = await getInProgressTaskSummary(directory)
  let gitDiff = ""
  try {
    gitDiff = execSync("git diff --stat", { cwd: directory, encoding: "utf-8" })
  } catch {
    gitDiff = "(无法获取 git diff)"
  }
  const content = `# Session Checkpoint - ${new Date(timestamp).toISOString()}\n\n## 当前任务\n${taskSummary || "无 InProgress 任务"}\n\n## Git Diff 统计\n\`\`\`\n${gitDiff}\n\`\`\`\n\n## 上下文状态\n- 工具调用次数: ${await readState(directory, "context-counter") || 0}\n- 状态: CRITICAL\n`
  await fs.writeFile(sessionFile, content, "utf-8")
}

async function validateJsonFile(filePath: string): Promise<{ valid: boolean; error?: string }> {
  try {
    const content = await fs.readFile(filePath, "utf-8")
    JSON.parse(content)
    return { valid: true }
  } catch (error: any) {
    return { valid: false, error: error.message }
  }
}

async function loadEnvFile(directory: string): Promise<Record<string, string>> {
  const envPath = path.join(directory, ".diwu/env")
  try {
    const content = await fs.readFile(envPath, "utf-8")
    const env: Record<string, string> = {}
    for (const line of content.split("\n")) {
      const trimmed = line.trim()
      if (!trimmed || trimmed.startsWith("#")) continue
      const eqIndex = trimmed.indexOf("=")
      if (eqIndex > 0) {
        const key = trimmed.slice(0, eqIndex).trim()
        const value = trimmed.slice(eqIndex + 1).trim()
        env[key] = value
      }
    }
    return env
  } catch {
    return {}
  }
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath)
    return true
  } catch {
    return false
  }
}

// 缓存规则索引，避免每次对话都读文件
let rulesIndexCache: { dir: string; content: string; ts: number } | null = null
const RULES_CACHE_TTL = 30000 // 30 秒

async function getRulesIndex(directory: string): Promise<string> {
  // 检查缓存
  if (rulesIndexCache && rulesIndexCache.dir === directory && Date.now() - rulesIndexCache.ts < RULES_CACHE_TTL) {
    return rulesIndexCache.content
  }

  const parts: string[] = []
  parts.push("## diwu-workflow 规则索引")

  const lessons = await readFileSafe(directory, ".diwu/lessons.md")
  if (lessons) {
    parts.push(`### 历史错误模式\n${lessons.slice(0, 1500)}`)
  }

  const requiredRules = [
    "constraints.md", "states.md", "workflow.md",
    "judgments.md", "templates.md", "exceptions.md", "file-layout.md"
  ]
  const missingRules: string[] = []
  for (const rule of requiredRules) {
    const exists = await fileExists(path.join(directory, RULES_DIR, rule))
    if (!exists) missingRules.push(rule)
  }

  if (missingRules.length > 0) {
    parts.push(`### 缺失规则文件\n以下规则文件不存在，请运行 /dinit 初始化：\n${missingRules.map(r => `- ${r}`).join("\n")}`)
  }

  const content = parts.join("\n\n")
  rulesIndexCache = { dir: directory, content, ts: Date.now() }
  return content
}

// ============ 主插件导出 ============

export const DiwuWorkflow: Plugin = async ({ project, client, $, directory, worktree }) => {
  await fs.mkdir(path.join(directory, STATE_DIR), { recursive: true })
  await loadSettings(directory)

  return {
    // ============ 事件监听 ============
    event: async ({ event }: any) => {
      const type = event?.type

      // Session 创建
      if (type === "session.created") {
        const sessionId = event?.session?.id || "unknown"
        await writeState(directory, "session-main", sessionId)
        const isSubagent = event?.session?.parentID != null
        if (isSubagent && client?.app?.log) {
          await client.app.log({ body: { service: "diwu-workflow", level: "info", message: `Subagent session created: ${sessionId}` } })
        }
      }

      // Session 空闲（调度器逻辑）
      if (type === "session.idle") {
        const taskJson = await readTaskJson(directory)
        if (!taskJson?.tasks) return
        const tasks = taskJson.tasks
        const inProgressTask = tasks.find((t: any) => t.status === "InProgress")

        if (inProgressTask) {
          const continueHere = `# 断点恢复 - ${new Date().toISOString()}\n\n## 当前任务\n**标题**: ${inProgressTask.title}\n**描述**: ${inProgressTask.description}\n\n## 进度\n${inProgressTask.progress || "无进度记录"}\n\n## 下一步\n${inProgressTask.nextSteps || "继续实施"}\n`
          await fs.writeFile(path.join(directory, ".diwu/continue-here.md"), continueHere, "utf-8")
          await saveSessionCheckpoint(directory)
          if (client?.app?.log) {
            await client.app.log({ body: { service: "diwu-workflow", level: "warn", message: `任务 "${inProgressTask.title}" 仍在进行中。已生成断点恢复文件。` } })
          }
        }

        const inReviewTasks = tasks.filter((t: any) => t.status === "InReview")
        if (inReviewTasks.length > 0) {
          const reviewLimit = getSetting("review_limit", 5)
          const reviewUsedStr = await readState(directory, "review-used")
          const reviewUsed = reviewUsedStr ? parseInt(reviewUsedStr, 10) : 0
          if (reviewUsed < reviewLimit) {
            await writeState(directory, "review-used", (reviewUsed + 1).toString())
            const nextInSpec = tasks.find((t: any) => t.status === "InSpec")
            if (nextInSpec && client?.app?.log) {
              await client.app.log({ body: { service: "diwu-workflow", level: "info", message: `有 ${inReviewTasks.length} 个任务在 InReview。推荐开始: "${nextInSpec.title}"` } })
            }
          }
        }

        const executableInSpec = tasks.find((t: any) => {
          if (t.status !== "InSpec") return false
          if (!t.blocked_by || t.blocked_by.length === 0) return true
          return t.blocked_by.every((depId: string) => {
            const dep = tasks.find((t2: any) => t2.id === depId)
            return dep?.status === "Done"
          })
        })
        if (executableInSpec && client?.app?.log) {
          await client.app.log({ body: { service: "diwu-workflow", level: "info", message: `有可执行的任务: "${executableInSpec.title}"` } })
        }
      }

      // TUI 输入追加（记录日志）
      if (type === "tui.prompt.append") {
        const input = event?.prompt?.input
        if (input && client?.app?.log) {
          await client.app.log({ body: { service: "diwu-workflow", level: "debug", message: `User input: ${input.slice(0, 100)}` } })
        }
      }
    },

    // ============ System Prompt 注入 ==========
    "experimental.chat.system.transform": async (input: any, output: any) => {
      const rulesIndex = await getRulesIndex(directory)
      if (rulesIndex) {
        output.system = output.system || []
        output.system.push(rulesIndex)
      }
    },

    // ============ 环境变量注入 ============
    "shell.env": async (input: any, output: any) => {
      const env = await loadEnvFile(directory)
      if (Object.keys(env).length > 0) {
        output.env = { ...output.env, ...env }
      }
    },

    // ============ 工具调用前 ==========
    "tool.execute.before": async (input: any, output: any) => {
      const toolName = input?.tool
      // Bash 命令前记录当前任务（日志）
      if (toolName === "bash" || toolName === "Bash") {
        const taskSummary = await getInProgressTaskSummary(directory)
        if (taskSummary && client?.app?.log) {
          await client.app.log({ body: { service: "diwu-workflow", level: "debug", message: `[工作焦点] ${taskSummary.slice(0, 200)}` } })
        }
      }
    },

    // ============ 工具调用后 ============
    "tool.execute.after": async (input: any, output: any) => {
      const toolName = input?.tool
      const args = input?.args

      // 1. JSON 文件写入后校验
      if ((toolName === "write" || toolName === "Write" || toolName === "edit" || toolName === "Edit") && args?.filePath) {
        const filePath = args.filePath
        if (filePath.endsWith(".json")) {
          const validation = await validateJsonFile(filePath)
          if (!validation.valid) {
            output.output = `[diwu-workflow] ⚠️ JSON 校验失败: ${validation.error}\n文件: ${filePath}\n\n${output.output || ""}`
          }
        }
      }

      // 2. 上下文监控
      const contextResult = await updateContextCounter(directory, toolName)
      const contextWarning = getSetting("context_monitor_warning", 30)
      const contextCritical = getSetting("context_monitor_critical", 50)
      const readonlyThreshold = getSetting("readonly_threshold", 15)

      if (contextResult.shouldCritical) {
        output.output = `[diwu-workflow] 🛑 ${contextResult.blockReason}\n\n${output.output || ""}`
      } else if (contextResult.shouldWarn) {
        output.output = `[diwu-workflow] ⚠️ 上下文警告：已进行 ${contextResult.counter} 次工具调用（阈值 ${contextWarning}）\n\n${output.output || ""}`
      }

      // 3. 只读连击检测
      if (contextResult.readonlyCount && contextResult.readonlyCount >= readonlyThreshold) {
        const readonlyWarned = await readState(directory, "context-readonly-warned")
        if (!readonlyWarned) {
          await writeState(directory, "context-readonly-warned", "true")
          output.output = `[diwu-workflow] 🛑 连续 ${contextResult.readonlyCount} 次只读操作（Analysis Paralysis）。请开始实施或明确下一步行动。\n\n${output.output || ""}`
        }
      }
    },

    // ============ Compact 保护 ==========
    "experimental.session.compacting": async (input: any, output: any) => {
      await saveSessionCheckpoint(directory)
      const taskSummary = await getInProgressTaskSummary(directory)
      if (taskSummary) {
        output.context = output.context || []
        output.context.push(`## 当前任务（compact 前）\n${taskSummary}`)
      }
    },
  }
}
