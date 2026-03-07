import json, sys, os, subprocess, time

d = json.load(sys.stdin)
cwd = d.get('cwd', '.')
rec = os.path.join(cwd, '.claude/recording.md')

if not os.path.exists(os.path.dirname(rec)):
    sys.exit(0)

if not os.path.isdir(os.path.join(cwd, '.git')):
    sys.exit(0)

# Dedup: skip if recording.md was modified within session window
sf = os.path.join(cwd, '.claude/settings.json')
settings = json.load(open(sf)) if os.path.exists(sf) else {}
window = settings.get('recording_session_window', 600)

if os.path.exists(rec) and time.time() - os.path.getmtime(rec) < window:
    sys.exit(0)

# git diff --stat HEAD: only tracked file changes (no untracked/pid/log noise)
try:
    diff = subprocess.check_output(
        ['git', 'diff', '--stat', 'HEAD'], cwd=cwd, stderr=subprocess.DEVNULL
    ).decode().strip()
except subprocess.CalledProcessError:
    diff = subprocess.check_output(
        ['git', 'diff', '--stat'], cwd=cwd, stderr=subprocess.DEVNULL
    ).decode().strip()

if not diff:
    sys.exit(0)

now = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()
open(rec, 'a').write('\n[auto] 变更快照 ' + now + '\n```\n' + diff + '\n```\n')
