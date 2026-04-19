"""Stop hook: recording + task.json status integrity check.

Checks:
1. Latest session file for required ### 本次踩坑 field.
2. task.json status vs recent git activity (stale InProgress/InDraft detection).

Returns list of (level, message) tuples for the caller to act on.
"""
import json
import os
import re
import subprocess
import time


def check(settings, tasks):
    """Check latest session for pitfall field + task status consistency.

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

    # Check 1: pitfall field
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

    # Check 2: task.json status vs git activity
    _check_task_status_sync(tasks, results)

    return results


def _check_task_status_sync(tasks, results):
    """Detect stale InProgress/InDraft tasks when recent git activity exists.

    If there are uncommitted changes or recent commits but tasks remain
    InProgress/InDraft, remind the agent to update task.json status.
    """
    try:
        # Check for uncommitted changes
        diff_stat = subprocess.run(
            ['git', 'diff', '--stat'], capture_output=True, text=True, timeout=5
        )
        has_uncommitted = bool(diff_stat.stdout.strip())

        # Check recent commit time
        log = subprocess.run(
            ['git', 'log', '-1', '--format=%ct'],
            capture_output=True, text=True, timeout=5
        )
        try:
            last_commit_ts = int(log.stdout.strip())
            seconds_since_commit = time.time() - last_commit_ts
        except (ValueError, TypeError):
            seconds_since_commit = 999999

        if not has_uncommitted and seconds_since_commit > 300:
            return  # No recent activity, skip

        # Find stale tasks
        stale = [
            t for t in tasks
            if t['status'] in ('InProgress', 'InDraft')
            and t.get('id', 0) > 0
        ]

        if stale:
            hints = ', '.join(f"#{t['id']}({t['status']})" for t in stale[:8])
            count = len(stale)
            extra = f" (+{count-8} more)" if count > 8 else ""
            results.append(('warning',
                f'[TASK_SYNC] 检测到最近有 git 活动，但仍有 {count} 个任务未更新状态：'
                f'{hints}{extra}。'
                f'如已完成实施，请及时将对应 task 标记为 Done/InReview。'))
    except Exception:
        pass  # Non-critical check, never block on failure
