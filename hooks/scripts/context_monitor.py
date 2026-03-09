import json, sys, os

# 读取 PostToolUse 事件数据获取工具名
tool_name = ''
try:
    event = json.load(sys.stdin)
    tool_name = event.get('toolName', '')
except:
    pass

# 用 session_id 作为稳定标识（由 session_start.py 写入 /tmp/.claude_main_session）
sid_file = '/tmp/.claude_main_session'
if not os.path.exists(sid_file):
    sys.exit(0)
sid = open(sid_file).read().strip()
if not sid:
    sys.exit(0)
counter_file = f'/tmp/diwu_ctx_{sid}'
warn_file = f'/tmp/diwu_ctx_{sid}_warned'
crit_file = f'/tmp/diwu_ctx_{sid}_critical'
readonly_file = f'/tmp/diwu_ctx_{sid}_readonly'
readonly_warn_file = f'/tmp/diwu_ctx_{sid}_readonly_warned'

WARNING_THRESHOLD = 100
CRITICAL_THRESHOLD = 150

# 递增计数器
count = 1
if os.path.exists(counter_file):
    try:
        count = int(open(counter_file).read().strip()) + 1
    except (ValueError, OSError):
        count = 1
open(counter_file, 'w').write(str(count))

# 只读连击检测
readonly_tools = {'Read', 'Grep', 'Glob', 'LSP'}
write_tools = {'Write', 'Edit', 'Bash', 'NotebookEdit'}
readonly_count = 0
if os.path.exists(readonly_file):
    try:
        readonly_count = int(open(readonly_file).read().strip())
    except:
        readonly_count = 0

if tool_name in readonly_tools:
    readonly_count += 1
    open(readonly_file, 'w').write(str(readonly_count))
elif tool_name in write_tools:
    if os.path.exists(readonly_file):
        os.remove(readonly_file)
    if os.path.exists(readonly_warn_file):
        os.remove(readonly_warn_file)
    readonly_count = 0

if readonly_count >= 15 and not os.path.exists(readonly_warn_file):
    open(readonly_warn_file, 'w').write('1')
    print(json.dumps({
        'decision': 'block',
        'reason': (
            '🔍 Analysis Paralysis Guard: 连续只读操作已达 ' + str(readonly_count) + ' 次。\n\n'
            '建议：\n'
            '1. 停止探索，基于已有信息做决策\n'
            '2. 如需更多信息，明确下一步要验证什么\n'
            '3. 优先实施而非继续调研'
        )
    }))
    sys.exit(0)

# CRITICAL 检查（优先级高于 WARNING）
if count >= CRITICAL_THRESHOLD and not os.path.exists(crit_file):
    open(crit_file, 'w').write('1')
    print(json.dumps({
        'decision': 'block',
        'reason': (
            '⚠️ CRITICAL: Context 使用量已达临界值（工具调用 ' + str(count) + ' 次）。\n\n'
            '必须立即执行：\n'
            '1. 立即写入 recording.md，记录当前进度和未完成工作\n'
            '2. 未完成的任务保持 InProgress\n'
            '3. 评估是否需要结束当前 session 并在新 session 中继续'
        )
    }))
    sys.exit(0)

# WARNING 检查
if count >= WARNING_THRESHOLD and not os.path.exists(warn_file):
    open(warn_file, 'w').write('1')
    print(json.dumps({
        'decision': 'block',
        'reason': (
            '⚡ WARNING: Context 使用量较高（工具调用 ' + str(count) + ' 次）。\n\n'
            '建议：\n'
            '1. 确认 recording.md 已记录当前进度\n'
            '2. 当前任务能否在本轮完成？不能则考虑拆分\n'
            '3. 避免大量只读探索，优先完成已开始的工作'
        )
    }))
    sys.exit(0)
