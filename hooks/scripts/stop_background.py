import json, sys, os, subprocess, time

d = json.load(sys.stdin)
cwd = d.get('cwd', '.')
recording_dir = os.path.join(cwd, '.claude/recording')

if not os.path.exists(os.path.dirname(recording_dir)):
    sys.exit(0)

if not os.path.isdir(os.path.join(cwd, '.git')):
    sys.exit(0)

# Dedup: skip if any session file was modified within session window
sf = os.path.join(cwd, '.claude/dsettings.json')
settings = json.load(open(sf)) if os.path.exists(sf) else {}
window = settings.get('recording_session_window', 600)

latest_mtime = 0
if os.path.exists(recording_dir):
    for f in os.listdir(recording_dir):
        if f.startswith('session-') and f.endswith('.md'):
            fpath = os.path.join(recording_dir, f)
            latest_mtime = max(latest_mtime, os.path.getmtime(fpath))

if latest_mtime > 0 and time.time() - latest_mtime < window:
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
filename = now.replace(' ', '-').replace(':', '')
os.makedirs(recording_dir, exist_ok=True)
session_file = os.path.join(recording_dir, f'session-{filename}.md')
open(session_file, 'w').write(f'## Session {now}\n\n[auto] 变更快照\n```\n{diff}\n```\n')
