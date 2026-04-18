"""Stop hook: recording integrity check.

Checks the latest session file for required ### 本次踩坑 field.
Returns list of (level, message) tuples for the caller to act on.
"""
import json
import os
import re


def check(settings, tasks):
    """Check latest session for pitfall field.

    Args:
        settings: dsettings dict
        tasks: task list from task.json

    Returns:
        list of (level, hint_string) tuples. Levels: 'block', 'warning', None
    """
    rec_dir = '.diwu/recording'
    results = []

    if not os.path.isdir(rec_dir):
        return results

    try:
        files = [
            os.path.join(rec_dir, f) for f in os.listdir(rec_dir)
            if f.startswith('session-') and f.endswith('.md')
        ]
        if not files:
            return results
        latest = max(files, key=os.path.getmtime)
    except Exception:
        return results

    try:
        content = open(latest, 'r', encoding='utf-8').read()
    except Exception:
        return results

    has_pitfall = bool(re.search(r'###\s*本次踩坑', content))
    active_tasks = [t for t in tasks if t['status'] in ('InProgress', 'InReview')]

    if not has_pitfall and active_tasks:
        hints = ', '.join('#' + str(t['id']) for t in active_tasks)
        results.append(('block',
            f'[INTEGRITY_CHECK] 最近 session 缺少「### 本次踩坑」字段。'
            f'当前有 {len(active_tasks)} 个活跃任务（{hints}），'
            f'请在 recording 中补充本次踩坑经验后再继续。（→ drecord skill）'))
    elif not has_pitfall and not active_tasks:
        results.append(('warning',
            '[INTEGRITY_CHECK] 最近 session 缺少「### 本次踩坑」字段。(warning)'))

    return results
