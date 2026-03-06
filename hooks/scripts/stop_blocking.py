import json, sys, os, platform


def notify(msg):
    if platform.system() == 'Darwin':
        os.system(
            'osascript -e \'display notification "' + msg
            + '" with title "diwu-workflow" sound name "Glass"\' 2>/dev/null'
        )
    else:
        os.system('notify-send "diwu-workflow" "' + msg + '" 2>/dev/null')
    if os.path.exists('/dev/tty'):
        open('/dev/tty', 'w').write('\a')
    else:
        os.system('osascript -e "beep" 2>/dev/null')


def mk(prefix, t):
    return (
        prefix + '\n\n'
        + 'Task#' + str(t['id']) + ': ' + t.get('title', t.get('description', '')) + '\n'
        + '任务描述：' + t.get('description', '') + '\n\n'
        + '验收条件：\n'
        + '\n'.join('  - ' + a for a in t.get('acceptance', [])) + '\n\n'
        + '实施步骤：\n'
        + '\n'.join('  ' + str(i + 1) + '. ' + s for i, s in enumerate(t.get('steps', []))) + '\n\n'
        + '按 core-workflow.md 流程执行。'
    )


f = '.claude/task.json'
data = json.load(open(f)) if os.path.exists(f) else {}

sf = '.claude/settings.json'
settings = json.load(open(sf)) if os.path.exists(sf) else {}

tasks = data.get('tasks', [])
done_ids = {t['id'] for t in tasks if t['status'] == 'Done'}
is_unblocked = lambda t: all(bid in done_ids for bid in t.get('blocked_by', []))

ip = [t for t in tasks if t['status'] == 'InProgress']
rev = [t for t in tasks if t['status'] == 'InReview']
nx = [t for t in tasks if t['status'] == 'InSpec' and is_unblocked(t)]

if ip:
    print(json.dumps({'decision': 'block', 'reason': mk('继续完成当前任务：', ip[0])}))
    sys.exit(0)

if rev:
    rlim = settings.get('review_limit', data.get('review_limit', 5))
    rused = data.get('review_used', 0)
    if rused >= rlim:
        notify('InReview 任务已达 ' + str(len(rev)) + ' 个，请人工验收后继续')
        sys.exit(0)
    elif nx:
        data['review_used'] = rused + 1
        open(f, 'w').write(json.dumps(data, indent=2, ensure_ascii=False))
        print(json.dumps({
            'decision': 'block',
            'reason': mk(
                '继续执行下一个任务 (review buffer ' + str(rused + 1) + '/' + str(rlim) + ')：',
                nx[0]
            )
        }))
        sys.exit(0)
else:
    if 'review_used' in data and data['review_used'] > 0:
        data['review_used'] = 0
        open(f, 'w').write(json.dumps(data, indent=2, ensure_ascii=False))

if nx:
    print(json.dumps({'decision': 'block', 'reason': mk('继续执行下一个任务：', nx[0])}))
    sys.exit(0)
