import json, sys, os, re

d = json.load(sys.stdin)
cwd = d.get('cwd', '.')
parts = []

# 1. recording/: extract latest session file
recording_dir = os.path.join(cwd, '.claude', 'recording')
if os.path.exists(recording_dir):
    session_files = [f for f in os.listdir(recording_dir) if f.startswith('session-') and f.endswith('.md')]
    if session_files:
        latest = sorted(session_files)[-1]
        rp = os.path.join(recording_dir, latest)
        rc = open(rp).read()
        text = rc.rstrip().rstrip('-').strip()
        if len(text) > 1500:
            text = text[:1500] + '...(truncated)'
        parts.append('# 最近 Session 记录\n' + text)

# 2. task.json: InProgress tasks
tp = os.path.join(cwd, '.claude', 'task.json')
if os.path.exists(tp):
    tasks = json.load(open(tp)).get('tasks', [])
    for t in tasks:
        if t.get('status') == 'InProgress':
            lines = ['# 当前 InProgress 任务']
            lines.append('Task#' + str(t['id']) + ': ' + t.get('title', ''))
            acc = t.get('acceptance', [])
            if acc:
                lines.append('验收条件:')
                for a in acc:
                    lines.append('- ' + a)
            steps = t.get('steps', [])
            if steps:
                lines.append('实施步骤:')
                for s in steps:
                    lines.append('- ' + s)
            parts.append('\n'.join(lines))

# 3. decisions.md: last 3 decisions
dp = os.path.join(cwd, '.claude', 'decisions.md')
if os.path.exists(dp):
    dc = open(dp).read()
    decs = re.split(r'(?=^## DEC-)', dc, flags=re.MULTILINE)
    decs = [x for x in decs if x.strip().startswith('## DEC-')]
    if decs:
        recent = decs[-3:]
        text = '\n'.join(x.strip() for x in recent)
        if len(text) > 1000:
            text = text[:1000] + '...(truncated)'
        parts.append('# 近期设计决策\n' + text)

if parts:
    prompt = '\n\n'.join(parts)
    print(json.dumps({'additionalSystemPrompt': prompt}))
