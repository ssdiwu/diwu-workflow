import json, sys, os, re

d = json.load(sys.stdin)
cwd = d.get('cwd', '.')
parts = []

# 1. recording/: extract latest session file
recording_dir = os.path.join(cwd, '.diwu', 'recording')
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
tp = os.path.join(cwd, '.diwu', 'dtask.json')
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
dp = os.path.join(cwd, '.diwu', 'decisions.md')
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

# Read dsettings.json for subagent configuration
settings_path = os.path.join(cwd, '.diwu', 'dsettings.json')
if os.path.exists(settings_path):
    try:
        settings = json.load(open(settings_path))
        concurrency = settings.get('subagent_concurrency', 3)
        explore_model = settings.get('subagent_explore_model', 'haiku')
        implement_model = settings.get('subagent_implement_model', 'inherit')
        parts.append(
            f'\n[diwu-ctx] 子代理约束：最多并行 {concurrency} 个；'
            f'探索类使用 {explore_model} 模型；'
            f'实施类使用 {"主模型" if implement_model == "inherit" else implement_model} 模型'
        )
    except Exception:
        pass

if parts:
    prompt = '\n\n'.join(parts)
    # Append skill index hint for subagent context
    prompt += '\n\n[diwu-ctx] Skill 索引：需任务管理→dtask | 需纠偏→dcorr | 需验证→dvfy | 写记录→drec | 阶段决策→djug'
    print(json.dumps({'additionalSystemPrompt': prompt}))
