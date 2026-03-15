import json, sys, os, subprocess, time, re
from datetime import datetime

# 读取 PostToolUse 事件数据获取工具名
tool_name = ''
try:
    event = json.load(sys.stdin)
    tool_name = event.get('toolName', '')
except:
    pass

# 用 session_id 作为稳定标识
sid_file = '/tmp/.claude_main_session'
if not os.path.exists(sid_file):
    sys.exit(0)
sid = open(sid_file).read().strip()
if not sid:
    sys.exit(0)

counter_file = f'/tmp/diwu_ctx_{sid}'
warn_file = f'/tmp/diwu_ctx_{sid}_warned'
crit_file = f'/tmp/diwu_ctx_{sid}_critical'
crit_ts_file = f'/tmp/diwu_ctx_{sid}_critical_ts'
readonly_file = f'/tmp/diwu_ctx_{sid}_readonly'
readonly_warn_file = f'/tmp/diwu_ctx_{sid}_readonly_warned'
config_cache_file = f'/tmp/diwu_ctx_{sid}_config_cache'

# 配置读取（带 mtime 缓存）
def load_config():
    settings_path = '.claude/settings.json'
    if not os.path.exists(settings_path):
        return {'warning': 30, 'critical': 50, 'delay': 10, 'session_window': 600}

    settings_mtime = os.path.getmtime(settings_path)
    if os.path.exists(config_cache_file):
        try:
            cache = json.load(open(config_cache_file))
            if cache.get('mtime') == settings_mtime:
                return cache.get('config', {})
        except:
            pass

    try:
        settings = json.load(open(settings_path))
        config = {
            'warning': settings.get('context_monitor_warning', 30),
            'critical': settings.get('context_monitor_critical', 50),
            'delay': settings.get('context_monitor_delay', 10),
            'session_window': settings.get('recording_session_window', 600)
        }
        open(config_cache_file, 'w').write(json.dumps({'mtime': settings_mtime, 'config': config}))
        return config
    except:
        return {'warning': 30, 'critical': 50, 'delay': 10, 'session_window': 600}

config = load_config()
WARNING_THRESHOLD = config['warning']
CRITICAL_THRESHOLD = config['critical']
DELAY_THRESHOLD = config['delay']
SESSION_WINDOW = config['session_window']

# 递增计数器
count = 1
if os.path.exists(counter_file):
    try:
        count = int(open(counter_file).read().strip()) + 1
    except:
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

# B 逻辑：CRITICAL+DELAY 检查
if count >= CRITICAL_THRESHOLD + DELAY_THRESHOLD and os.path.exists(crit_ts_file):
    try:
        critical_ts = float(open(crit_ts_file).read().strip())
        recording_dir = '.claude/recording'
        latest_mtime = 0
        if os.path.exists(recording_dir):
            for f in os.listdir(recording_dir):
                if f.startswith('session-') and f.endswith('.md'):
                    fpath = os.path.join(recording_dir, f)
                    latest_mtime = max(latest_mtime, os.path.getmtime(fpath))

        if latest_mtime < critical_ts:
            # recording/ 未更新，自动写入 checkpoint
            def write_checkpoint():
                try:
                    # 读取 InProgress 任务
                    task_json = json.load(open('.claude/task.json'))
                    in_progress = [t for t in task_json.get('tasks', []) if t.get('status') == 'InProgress']

                    # git diff --stat
                    diff_stat = subprocess.run(['git', 'diff', '--stat'], capture_output=True, text=True).stdout.strip()

                    # 生成新的 session 文件
                    now = time.time()
                    current_time = datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                    filename = datetime.fromtimestamp(now).strftime('%Y-%m-%d-%H%M%S')

                    recording_dir = '.claude/recording'
                    os.makedirs(recording_dir, exist_ok=True)
                    session_file = os.path.join(recording_dir, f'session-{filename}.md')

                    with open(session_file, 'w') as f:
                        f.write(f'## Session {current_time}\n\n')
                        f.write('### [Auto Checkpoint]\n\n')
                        if in_progress:
                            for task in in_progress:
                                f.write(f"**Task#{task['id']}**: {task['title']} (InProgress)\n")
                        if diff_stat:
                            f.write(f'\n**未提交变更**:\n```\n{diff_stat}\n```\n')
                        f.write('\n')
                except Exception as e:
                    pass

            write_checkpoint()
    except:
        pass

# A 逻辑：CRITICAL 检查（优先级高于 WARNING）
if count >= CRITICAL_THRESHOLD and not os.path.exists(crit_file):
    open(crit_file, 'w').write('1')
    open(crit_ts_file, 'w').write(str(time.time()))
    print(json.dumps({
        'decision': 'block',
        'reason': (
            '⚠️ CRITICAL: Context 使用量已达临界值（工具调用 ' + str(count) + ' 次）。\n\n'
            '立即更新 recording/，记录：\n'
            '1. 当前任务状态和已完成的工作\n'
            '2. 关键决策和下一步计划\n'
            '3. 未完成的任务保持 InProgress\n\n'
            '然后评估是否需要结束当前 session 并在新 session 中继续。'
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
            '1. 确认 recording/ 已记录当前进度\n'
            '2. 当前任务能否在本轮完成？不能则考虑拆分\n'
            '3. 避免大量只读探索，优先完成已开始的工作'
        )
    }))
    sys.exit(0)
