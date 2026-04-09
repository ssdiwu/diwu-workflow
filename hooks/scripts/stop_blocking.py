import json, sys, os, platform, subprocess


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
        + '按 workflow.md 流程执行。'
    )


f = '.claude/task.json'
data = json.load(open(f)) if os.path.exists(f) else {}

sf = '.claude/settings.json'
settings = json.load(open(sf)) if os.path.exists(sf) else {}
continuous_mode = settings.get('continuous_mode', True)

tasks = data.get('tasks', [])
done_ids = {t['id'] for t in tasks if t['status'] == 'Done'}
is_unblocked = lambda t: all(bid in done_ids for bid in t.get('blocked_by', []))

ip = [t for t in tasks if t['status'] == 'InProgress']
rev = [t for t in tasks if t['status'] == 'InReview']
nx = [t for t in tasks if t['status'] == 'InSpec' and is_unblocked(t)]

if ip:
    # --- 断点恢复文件生成 ---
    t = ip[0]
    ch = os.path.join(os.path.dirname(f), 'continue-here.md')
    try:
        diff_stat = subprocess.check_output(
            ['git', 'diff', '--stat'], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        diff_stat = ''
    try:
        now = subprocess.check_output(
            ['date', '+%Y-%m-%d %H:%M:%S'], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        now = ''
    lines = ['# 断点恢复', '', '> 生成时间: ' + now, '> 恢复后自动删除', '']
    lines.append('## 当前位置')
    lines.append('Task#' + str(t['id']) + ': ' + t.get('title', '') + ' → InProgress')
    lines.append('')
    acc = t.get('acceptance', [])
    if acc:
        lines.append('## 验收条件')
        for a in acc:
            lines.append('- [ ] ' + a)
        lines.append('')
    steps = t.get('steps', [])
    if steps:
        lines.append('## 实施步骤')
        for s in steps:
            lines.append('- ' + s)
        lines.append('')
    if diff_stat:
        lines.append('## 未提交变更')
        lines.append('```')
        lines.append(diff_stat)
        lines.append('```')
        lines.append('')
    lines.append('## 恢复后第一步')
    lines.append('继续实施 Task#' + str(t['id']) + '，从上次中断处恢复。')
    lines.append('')
    with open(ch, 'w') as cf:
        cf.write('\n'.join(lines))

    print(json.dumps({'decision': 'block', 'reason': mk('继续完成当前任务：', ip[0])}))
    sys.exit(0)

if rev:
    rlim = settings.get('review_limit', data.get('review_limit', 5))
    rused = data.get('review_used', 0)
    if rused >= rlim:
        notify('InReview 任务已达 ' + str(len(rev)) + ' 个，请人工验收后继续')
        sys.exit(0)
    elif nx:
        if not continuous_mode:
            # continuous_mode=false: 不自动续跑，停止等待人工介入
            done_tasks = [t for t in tasks if t['status'] == 'Done']
            remaining = [t for t in tasks if t['status'] not in ('Done', 'Cancelled')]
            summary = (
                'CONTINUOUS_MODE_COMPLETE - continuous_mode 已关闭\n'
                '已完成: ' + str(len(done_tasks)) + ' 个任务\n'
                '下一任务: Task#' + str(nx[0]['id']) + ' ' + nx[0].get('title', '') + ' (InSpec)\n'
                '剩余: ' + ', '.join('#' + str(t['id']) + '(' + t['status'] + ')' for t in remaining)
            )
            print(json.dumps({'decision': 'block', 'reason': summary}))
            sys.exit(0)
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
    if not continuous_mode:
        # continuous_mode=false: 不自动续跑，输出完成摘要
        done_tasks = [t for t in tasks if t['status'] == 'Done']
        remaining = [t for t in tasks if t['status'] not in ('Done', 'Cancelled')]
        summary = (
            'CONTINUOUS_MODE_COMPLETE - continuous_mode 已关闭\n'
            '已完成: ' + str(len(done_tasks)) + ' 个任务\n'
            '下一任务: Task#' + str(nx[0]['id']) + ' ' + nx[0].get('title', '') + ' (InSpec)\n'
            '剩余: ' + ', '.join('#' + str(t['id']) + '(' + t['status'] + ')' for t in remaining)
        )
        print(json.dumps({'decision': 'block', 'reason': summary}))
        sys.exit(0)
    print(json.dumps({'decision': 'block', 'reason': mk('继续执行下一个任务：', nx[0])}))
    sys.exit(0)
