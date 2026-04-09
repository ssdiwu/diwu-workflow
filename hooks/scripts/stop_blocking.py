import json, sys, os, platform, subprocess, re
from collections import defaultdict


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


# ============================================================
# 完整性检查：检测最近 session 是否包含「本次踩坑」字段
# ============================================================
def integrity_check(settings, tasks, additional_prompts):
    """检查最近 recording 文件是否包含 ### 本次踩坑 段落。

    追加提示到 additional_prompts 列表。
    策略：有 InProgress/InReview 任务 → block 提示；纯问答/无任务 → warning。
    """
    rec_dir = os.path.join(os.path.dirname('.claude/task.json' if os.path.exists('.claude/task.json') else '.'), 'recording') \
        if os.path.exists('.claude') else '.claude/recording'
    # 规范化路径
    rec_dir = '.claude/recording'

    if not os.path.isdir(rec_dir):
        return

    # 找到最新的 recording 文件
    try:
        files = [
            os.path.join(rec_dir, f) for f in os.listdir(rec_dir)
            if f.startswith('session-') and f.endswith('.md')
        ]
        if not files:
            return
        latest = max(files, key=os.path.getmtime)
    except Exception:
        return

    try:
        content = open(latest, 'r', encoding='utf-8').read()
    except Exception:
        return

    has_pitfall = bool(re.search(r'###\s*本次踩坑', content))

    # 判断是否有活跃任务
    active_tasks = [t for t in tasks if t['status'] in ('InProgress', 'InReview')]

    if not has_pitfall and active_tasks:
        # 有活跃任务但缺少踩坑记录 → block 提示
        hint = (
            '[INTEGRITY_CHECK] 最近 session 缺少「### 本次踩坑」字段。\n'
            '当前有 ' + str(len(active_tasks)) + ' 个活跃任务（'
            + ', '.join('#' + str(t['id']) for t in active_tasks)
            + '），请在 recording 中补充本次踩坑经验后再继续。'
        )
        additional_prompts.append(('block', hint))
    elif not has_pitfall and not active_tasks:
        # 无活跃任务 → 仅 warning
        hint = (
            '[INTEGRITY_CHECK] 最近 session 缺少「### 本次踩坑」字段。（warning）'
        )
        additional_prompts.append(('warning', hint))


# ============================================================
# 归档聚合：从即将归档的 session 中提取踩坑，聚类写入 project-pitfalls.md
# ============================================================
def archive_aggregate(settings, tasks):
    """检查 recording/ 数量是否超阈值，超则提取踩坑聚类追加到 project-pitfalls.md。

    返回 (should_warn, message) 元组。
    """
    rec_dir = '.claude/recording'
    pitfalls_path = '.claude/project-pitfalls.md'

    threshold = settings.get('recording_archive_threshold', 50)

    if not os.path.isdir(rec_dir):
        return False, ''

    try:
        files = [
            os.path.join(rec_dir, f) for f in os.listdir(rec_dir)
            if f.startswith('session-') and f.endswith('.md')
        ]
    except Exception:
        return False, ''

    if len(files) <= threshold:
        return False, ''

    # 按修改时间排序，确定即将归档的文件（最旧的 N 个）
    files.sort(key=os.path.getmtime)
    to_archive_count = len(files) - threshold
    to_archive = files[:to_archive_count]

    if not to_archive:
        return False, ''

    # 正则提取每个文件的 ### 本次踩坑 段落
    pitfall_pattern = re.compile(
        r'###\s*本次踩坑\s*\n(.*?)(?=\n### |\n---|\Z)',
        re.DOTALL
    )

    categories = defaultdict(list)  # category -> [content]

    for fpath in to_archive:
        try:
            content = open(fpath, 'r', encoding='utf-8').read()
        except Exception:
            continue
        matches = pitfall_pattern.findall(content)
        for m in matches:
            # 尝试从内容中推断类别（简单启发式：取第一个 ## 或 ** 加粗标题）
            cat_match = re.search(r'(?:##\s+|\*\*)([^#\n*]+?)(?:\*\*|\s*\n)', m.strip())
            category = cat_match.group(1).strip()[:30] if cat_match else '未分类'
            categories[category].append(m.strip())

    if not categories:
        return False, ''

    # 追加写入 project-pitfalls.md
    try:
        now = subprocess.check_output(
            ['date', '+%Y-%m-%d %H:%M:%S'], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        now = ''

    aggregated_lines = [
        '',
        '> 归档聚合时间: ' + now,
        '> 来源: ' + str(to_archive_count) + ' 个 session 文件',
        '',
    ]

    for category, items in categories.items():
        aggregated_lines.append('### ' + category + '（归档聚合）')
        aggregated_lines.append('')
        for item in items:
            aggregated_lines.append('- ' + item.replace('\n', ' ')[:200])
        aggregated_lines.append('')

    mode = 'a' if os.path.exists(pitfalls_path) else 'w'
    try:
        with open(pitfalls_path, mode, encoding='utf-8') as pf:
            pf.write('\n'.join(aggregated_lines))
        msg = (
            '[ARCHIVE_AGGREGATE] 已归档聚合 ' + str(to_archive_count)
            + ' 个 session 的踩坑记录到 project-pitfalls.md（'
            + str(len(categories)) + ' 个类别）。'
        )
        return True, msg
    except Exception as e:
        return False, '[ARCHIVE_AGGREGATE] 写入失败: ' + str(e)


# ============================================================
# 主逻辑
# ============================================================

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

# 收集完整性检查和归档聚合的附加信息
additional_prompts = []

# 1. 完整性检查
integrity_check(settings, tasks, additional_prompts)

# 2. 归档聚合
archived, archive_msg = archive_aggregate(settings, tasks)
if archived:
    additional_prompts.append(('info', archive_msg))

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
    lines.append('Task#' + str(t['id']) + ': ' + t.get('title', '') + ' -> InProgress')
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

    # 合并附加提示到断点恢复 prompt
    base_prompt = mk('继续完成当前任务：', ip[0])
    for level, hint in additional_prompts:
        if level == 'block':
            base_prompt += '\n\n⚠ ' + hint
        elif level in ('warning', 'info'):
            base_prompt += '\n\nℹ ' + hint

    print(json.dumps({'continue': True, 'additionalSystemPrompt': base_prompt}))
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
            print(json.dumps({'continue': True, 'additionalSystemPrompt': summary}))
            sys.exit(0)
        data['review_used'] = rused + 1
        open(f, 'w').write(json.dumps(data, indent=2, ensure_ascii=False))

        base_prompt = mk(
            '继续执行下一个任务 (review buffer ' + str(rused + 1) + '/' + str(rlim) + ')：',
            nx[0]
        )
        for level, hint in additional_prompts:
            if level == 'block':
                base_prompt += '\n\n⚠ ' + hint
            elif level in ('warning', 'info'):
                base_prompt += '\n\nℹ ' + hint

        print(json.dumps({
            'continue': True,
            'additionalSystemPrompt': base_prompt
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
        print(json.dumps({'continue': True, 'additionalSystemPrompt': summary}))
        sys.exit(0)

    base_prompt = mk('继续执行下一个任务：', nx[0])
    for level, hint in additional_prompts:
        if level == 'block':
            base_prompt += '\n\n⚠ ' + hint
        elif level in ('warning', 'info'):
            base_prompt += '\n\nℹ ' + hint

    print(json.dumps({'continue': True, 'additionalSystemPrompt': base_prompt}))
    sys.exit(0)
