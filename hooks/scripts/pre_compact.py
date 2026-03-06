import json, sys, os, subprocess

d = json.load(sys.stdin)
cwd = d.get('cwd', '.')

tf = os.path.join(cwd, '.claude/task.json')
if not os.path.exists(tf):
    sys.exit(0)

data = json.load(open(tf))
ip = [t for t in data.get('tasks', []) if t['status'] == 'InProgress']

if not ip:
    sys.exit(0)

rec = os.path.join(cwd, '.claude/recording.md')
if not os.path.isdir(os.path.dirname(rec)):
    sys.exit(0)

try:
    diff = subprocess.check_output(
        ['git', 'diff', '--stat'], cwd=cwd, stderr=subprocess.DEVNULL
    ).decode().strip()
    cached = subprocess.check_output(
        ['git', 'diff', '--cached', '--stat'], cwd=cwd, stderr=subprocess.DEVNULL
    ).decode().strip()
    stat = '\n'.join(filter(None, [diff, cached]))
except Exception:
    stat = ''

now = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()
t = ip[0]
entry = (
    '\n---\n'
    '## [auto-compact] Task#' + str(t['id']) + ' 进度快照 ' + now + '\n\n'
    + '任务：' + t.get('title', '') + '\n'
)
if stat:
    entry += '\n```\n' + stat + '\n```\n'

open(rec, 'a').write(entry)
