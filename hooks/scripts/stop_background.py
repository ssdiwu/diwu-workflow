import json, sys, os, subprocess

d = json.load(sys.stdin)
cwd = d.get('cwd', '.')
rec = os.path.join(cwd, '.claude/recording.md')

if not os.path.exists(os.path.dirname(rec)):
    sys.exit(0)

if not os.path.isdir(os.path.join(cwd, '.git')):
    sys.exit(0)

gs = subprocess.check_output(
    ['git', 'status', '--short'], cwd=cwd, stderr=subprocess.DEVNULL
).decode().strip()

if not gs:
    sys.exit(0)

now = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()
snap = '变更文件:\n' + gs
open(rec, 'a').write('\n## Session End ' + now + '\n\n' + snap + '\n')
