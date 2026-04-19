"""Archive detection for Stop hook — pure detection, no execution.

Checks two tracks:
1. Task archive: Done/Cancelled count vs task_archive_threshold
2. Recording archive: file count OR file age vs thresholds

Returns (level, message) tuples — never modifies files.
"""

import json
import os
import time
from pathlib import Path
from typing import List, Tuple


def _load_settings() -> dict:
    """Load dsettings.json with safe defaults."""
    settings_path = Path(".diwu/dsettings.json")
    defaults = {
        "task_archive_threshold": 20,
        "recording_archive_threshold": 50,
        "recording_retention_days": 30,
    }
    if not settings_path.exists():
        return defaults
    try:
        with open(settings_path, "r") as f:
            s = json.load(f)
        return {**defaults, **s}
    except (json.JSONDecodeError, OSError):
        return defaults


def check_task_archive(settings: dict, tasks: list) -> Tuple[bool, int, int, str]:
    """Check if task archive is needed.

    Returns:
        (needs_archive, done_cancelled_count, threshold, message)
    """
    threshold = settings.get("task_archive_threshold", 20)
    done_count = sum(
        1 for t in tasks if t.get("status") in ("Done", "Cancelled")
    )
    needs = done_count >= threshold
    msg = (
        f"[ARCHIVE_CHECK] Task archive warning: "
        f"{done_count} terminal tasks (threshold {threshold}). "
        f"Run /darc to archive."
        if needs
        else ""
    )
    return (needs, done_count, threshold, msg)


def check_recording_archive(settings: dict) -> Tuple[bool, int, int, int, int, str]:
    """Check if recording archive is needed (dual-condition OR).

    Conditions (either triggers):
    A: file count >= recording_archive_threshold
    B: any file older than recording_retention_days

    Returns:
        (needs_archive, total_files, files_to_archive_by_age,
         count_threshold, days_threshold, message)
    """
    rec_dir = Path(".diwu/recording/")
    count_thresh = settings.get("recording_archive_threshold", 50)
    days_thresh = settings.get("recording_retention_days", 30)

    if not rec_dir.exists():
        return (False, 0, 0, count_thresh, days_thresh, "")

    # Collect session files (skip non-md, skip archives)
    session_files = [
        f for f in rec_dir.iterdir()
        if f.is_file() and f.suffix == ".md" and not f.name.startswith(".")
    ]
    total = len(session_files)

    # Condition A: count threshold
    count_trigger = total >= count_thresh

    # Condition B: age threshold
    now = time.time()
    age_sec = days_thresh * 86400
    old_files = [f for f in session_files if (now - f.stat().st_mtime) > age_sec]
    age_trigger = len(old_files) > 0

    needs = count_trigger or age_trigger

    detail_parts = []
    if count_trigger:
        detail_parts.append(f"{total} files (threshold {count_thresh})")
    if age_trigger:
        detail_parts.append(f"{len(old_files)} files older than {days_thresh}d")

    msg = (
        f"[ARCHIVE_CHECK] Recording archive warning: {' + '.join(detail_parts)}. "
        f"Run /darc to archive."
        if needs
        else ""
    )

    return (needs, total, len(old_files), count_thresh, days_thresh, msg)


def check(settings: dict = None, tasks: list = None) -> List[Tuple[str, str]]:
    """Main entry point — returns [(level, message)] list.

    Args:
        settings: dsettings dict (None = auto-load)
        tasks: task list (None = auto-load from .diwu/dtask.json)

    Returns:
        List of (level, message) tuples. Level is 'info' or 'warning'.
        Empty list = no action needed.
    """
    if settings is None:
        settings = _load_settings()

    results = []

    # Track 1: Task archive
    if tasks is None:
        task_path = Path(".diwu/dtask.json")
        if task_path.exists():
            try:
                with open(task_path, "r") as f:
                    tasks_data = json.load(f)
                tasks = tasks_data.get("tasks", [])
            except (json.JSONDecodeError, OSError):
                tasks = []
        else:
            tasks = []

    needs_tc, count, thresh, tc_msg = check_task_archive(settings, tasks)
    if needs_tc and tc_msg:
        results.append(("info", tc_msg))

    # Track 2: Recording archive
    needs_rc, total, old_cnt, ct, dt, rc_msg = check_recording_archive(settings)
    if needs_rc and rc_msg:
        results.append(("info", rc_msg))

    return results
