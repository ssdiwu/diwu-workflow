"""Shared InProgress snapshot writer for Stop hooks.

Used by both stop_blocking.py (foreground) and stop_background.py (background).
Writes task summary + git diff to recording/ session file.
"""
import json, os, subprocess, time
from datetime import datetime


def write_inprogress_snapshot(tasks, recording_dir='.diwu/recording', diff_stat=None):
    """Write InProgress task snapshot to a new session file.

    Args:
        tasks: list of task dicts with status InProgress
        recording_dir: path to recording directory
        diff_stat: optional pre-computed git diff --stat string
    Returns:
        path to created session file, or None on failure
    """
    if not tasks:
        return None

    try:
        now = time.time()
        dt = datetime.fromtimestamp(now)
        ts = dt.strftime('%Y-%m-%d %H:%M:%S')
        filename = dt.strftime('%Y-%m-%d-%H%M%S')
        os.makedirs(recording_dir, exist_ok=True)
        session_file = os.path.join(recording_dir, f'session-{filename}.md')

        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(f'## Session {ts}\n\n')
            f.write('### [InProgress Snapshot]\n\n')
            for t in tasks:
                f.write(f"**Task#{t['id']}**: {t['title']} (InProgress)\n")
                acc = t.get('acceptance', [])
                if acc:
                    f.write('\n验收条件:\n')
                    for a in acc:
                        f.write(f'- [ ] {a}\n')
                steps = t.get('steps', [])
                if steps:
                    f.write('\n实施步骤:\n')
                    for s in steps:
                        f.write(f'- {s}\n')
                f.write('\n')

            if diff_stat:
                f.write(f'\n**未提交变更**:\n```\n{diff_stat}\n```\n')

        return session_file
    except Exception:
        return None


def get_git_diff_stat():
    """Run git diff --stat and return output string."""
    try:
        return subprocess.run(
            ['git', 'diff', '--stat'], capture_output=True, text=True
        ).stdout.strip()
    except Exception:
        return ''
