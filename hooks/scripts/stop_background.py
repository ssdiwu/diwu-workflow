"""Stop hook (background): lightweight InProgress snapshot via shared module.

Delegates snapshot writing to stop_snapshot.py (shared with stop_blocking.py).
Deduplicates session window logic to avoid redundant writes.
"""
import json
import os
import subprocess
import sys
import time

from stop_snapshot import write_inprogress_snapshot, get_git_diff_stat


def main():
    d = json.load(sys.stdin)
    cwd = d.get('cwd', '.')
    rec_dir = os.path.join(cwd, '.diwu/recording')

    if not os.path.exists(os.path.dirname(rec_dir)):
        sys.exit(0)
    if not os.path.isdir(os.path.join(cwd, '.git')):
        sys.exit(0)

    # Dedup: skip if recent session exists within window
    sf = os.path.join(cwd, '.diwu/dsettings.json')
    settings = json.load(open(sf)) if os.path.exists(sf) else {}
    window = settings.get('snapshot_dedup_sec', 600)

    latest_mtime = 0
    if os.path.exists(rec_dir):
        for f in os.listdir(rec_dir):
            if f.startswith('session-') and f.endswith('.md'):
                fpath = os.path.join(rec_dir, f)
                latest_mtime = max(latest_mtime, os.path.getmtime(fpath))

    if latest_mtime > 0 and time.time() - latest_mtime < window:
        sys.exit(0)

    # Load tasks and filter InProgress
    tf = os.path.join(cwd, '.diwu/dtask.json')
    try:
        data = json.load(open(tf))
    except Exception:
        sys.exit(0)

    ip = [t for t in data.get('tasks', []) if t['status'] == 'InProgress']
    if not ip:
        sys.exit(0)

    diff = get_git_diff_stat()
    write_inprogress_snapshot(ip, recording_dir=rec_dir, diff_stat=diff)


if __name__ == '__main__':
    main()
