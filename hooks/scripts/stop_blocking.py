"""Stop hook (foreground dispatcher). Orchestrates 4 sub-modules:
stop_snapshot | stop_integrity | stop_archive_agg | stop_decision.
hooks.json registers THIS file only; sub-modules are internal imports."""
import json
import sys

TASK_JSON = '.diwu/task.json'
SETTINGS_PATH = '.diwu/dsettings.json'


def _load(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def main():
    data = _load(TASK_JSON, {'tasks': []})
    settings = _load(SETTINGS_PATH, {})
    tasks = data.get('tasks', [])

    # Sub-module 1: Integrity check
    from stop_integrity import check as integrity_check
    additional = integrity_check(settings, tasks)

    # Sub-module 2: Archive aggregation
    from stop_archive_agg import aggregate as archive_agg
    archived, archive_msg = archive_agg(settings)
    if archived and archive_msg:
        additional.append(('info', archive_msg))

    # Sub-module 3: Decision tree + notification
    from stop_decision import decide as run_decision
    should_continue, output = run_decision(
        tasks, settings, data, TASK_JSON, additional
    )

    # Sub-module 4: Snapshot (only if InProgress and continuing)
    if should_continue:
        ip_tasks = [t for t in tasks if t['status'] == 'InProgress']
        if ip_tasks:
            from stop_snapshot import write_inprogress_snapshot, get_git_diff_stat
            diff = get_git_diff_stat()
            write_inprogress_snapshot(ip_tasks, diff_stat=diff)

    print(json.dumps(output))
    sys.exit(0 if should_continue else 1)


if __name__ == '__main__':
    main()
