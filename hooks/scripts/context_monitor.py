"""Context Monitor: tool call counting, readonly detection, threshold gating → checkpoint."""
import json, sys, os, subprocess, time
from datetime import datetime

SID_FILE = '/tmp/.claude_main_session'
SETTINGS = '.diwu/dsettings.json'
CACHE = '/tmp/diwu_ctx_config_cache'
DEFAULTS = {'warning': 30, 'critical': 50, 'delay': 10}
RD_TOOLS = {'Read', 'Grep', 'Glob', 'LSP'}
WR_TOOLS = {'Write', 'Edit', 'Bash', 'NotebookEdit'}


def _cfg():
    if not os.path.exists(SETTINGS):
        return DEFAULTS
    mt = os.path.getmtime(SETTINGS)
    if os.path.exists(CACHE):
        try:
            c = json.load(open(CACHE))
            if c.get('mt') == mt:
                return c.get('c', DEFAULTS)
        except Exception:
            pass
    try:
        s = json.load(open(SETTINGS))
        r = {k: s.get(f'context_monitor_{k}', v) for k, v in DEFAULTS.items()}
        open(CACHE, 'w').write(json.dumps({'mt': mt, 'c': r}))
        return r
    except Exception:
        return DEFAULTS


def _rc(path, d=0):
    try: return int(open(path).read().strip()) if os.path.exists(path) else d
    except Exception: return d


def _wc(path):
    v = _rc(path, 0) + 1; open(path, 'w').write(str(v)); return v


def checkpoint():
    try:
        ip = [t for t in json.load(open('.diwu/task.json')).get('tasks', []) if t.get('status') == 'InProgress']
        ds = subprocess.run(['git', 'diff', '--stat'], capture_output=True, text=True).stdout.strip()
        dt = datetime.fromtimestamp(time.time())
        rd = '.diwu/recording'; os.makedirs(rd, exist_ok=True)
        sf = os.path.join(rd, f'session-{dt.strftime("%Y-%m-%d-%H%M%S")}.md')
        with open(sf, 'w') as f:
            f.write(f'## Session {dt.strftime("%Y-%m-%d %H:%M:%S")}\n\n### [Auto Checkpoint]\n\n')
            for t in ip: f.write(f"**Task#{t['id']}**: {t['title']} (InProgress)\n")
            if ds: f.write(f'\n**未提交变更**:\n```\n{ds}\n```\n')
            f.write('\n')
    except Exception:
        pass


# --- Main ---
try:
    ev = json.load(sys.stdin); tool = ev.get('toolName', '')
except Exception:
    tool = ''

if not os.path.exists(SID_FILE):
    sys.exit(0)
sid = open(SID_FILE).read().strip()
if not sid:
    sys.exit(0)

cf = _cfg()
cnt_path = f'/tmp/diwu_ctx{sid}'
cnt = _wc(cnt_path)

# Readonly guard
ro_f = f'/tmp/diwu_ctx{sid}_readonly'
ro_wf = f'/tmp/diwu_ctx{sid}_readonly_warned'
if tool in RD_TOOLS:
    rc = _wc(ro_f)
elif tool in WR_TOOLS:
    for f in (ro_f, ro_wf):
        try: os.remove(f)
        except OSError: pass
    rc = 0
else:
    rc = _rc(ro_f)

if rc >= 15 and not os.path.exists(ro_wf):
    open(ro_wf, 'w').write('1')
    print(json.dumps({'decision': 'block',
        'reason': f'🔍 Analysis Paralysis Guard: 连续只读操作已达 {rc} 次。\n\n建议：\n1. 停止探索，基于已有信息做决策\n2. 如需更多信息，明确下一步要验证什么\n3. 优先实施而非继续调研（→ /dcorr）'}))
    sys.exit(0)

# Threshold checks (priority order)
crit_f = f'/tmp/diwu_ctx{sid}_critical'
crit_ts = f'/tmp/diwu_ctx{sid}_critical_ts'
warn_f = f'/tmp/diwu_ctx{sid}_warned'

if cnt >= cf['critical'] + cf['delay'] and os.path.exists(crit_ts):
    try:
        if datetime.fromtimestamp(os.path.getmtime('.diwu/recording')) < datetime.fromtimestamp(float(open(crit_ts).read())):
            checkpoint()
    except Exception:
        pass

if cnt >= cf['critical'] and not os.path.exists(crit_f):
    open(crit_f, 'w').write('1'); open(crit_ts, 'w').write(str(time.time()))
    print(json.dumps({'decision': 'block',
        'reason': f'⚠️ CRITICAL: Context 使用量已达临界值（工具调用 {cnt} 次）。\n\n立即更新 recording/（→ drecord skill），然后评估是否需要结束 session。'}))
    sys.exit(0)

if cnt >= cf['warning'] and not os.path.exists(warn_f):
    open(warn_f, 'w').write('1')
    print(json.dumps({'decision': 'block',
        'reason': f'⚡ WARNING: Context 使用量较高（工具调用 {cnt} 次）。\n\n1. 确认 recording/ 已记录（→ drecord）\n2. 当前任务能否在本轮完成？不能则拆分\n3. 避免大量只读探索，优先实施'}))
    sys.exit(0)

sys.exit(0)
