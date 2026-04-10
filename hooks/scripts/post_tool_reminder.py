#!/usr/bin/env python3
"""PostToolUse: lightweight reminder to update error/decision records
after Write/Edit operations.

Checks error buffer from post_tool_use_failure.py for unresolved
failures (strike >= 2) and prompts recording.

Non-blocking. Fires on Write/Edit only (not Bash/Read to avoid noise).
Uses sessionId from event data for cross-process state sharing.
"""

import json, os, sys

ERRTRACK_PREFIX = '/tmp/diwu_errtrack_'
SETTINGS_FILE = '.claude/dsettings.json'


def _errtrack_path(session_id):
    """Return error buffer path using sessionId."""
    sid = session_id or ''
    return ERRTRACK_PREFIX + sid if sid else ''


def _load(p):
    if os.path.exists(p):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _get_event_data():
    try:
        raw = sys.stdin.read()
        if not raw:
            return {}
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}


def main():
    settings = _load(SETTINGS_FILE)
    if settings.get('recording_reminder', {}).get('enabled') == False:
        sys.exit(0)

    event = _get_event_data()
    session_id = event.get('session_id', event.get('sessionId', ''))
    reminders = []

    # Check error buffer for unresolved failures (strike >= 2)
    err_file = _errtrack_path(session_id)
    if err_file and os.path.exists(err_file):
        try:
            err_data = json.load(open(err_file))
            unresolved = [e for e in err_data.get('errors', []) if e.get('strike', 0) >= 2]
            if unresolved:
                tools_seen = list(set(e['tool'] for e in unresolved[-5:]))
                reminders.append(
                    '[RECORDING] 有 %d 个未解决的工具失败 (%s)。'
                    '如已解决，请记录根因到 ### 本次踩坑/经验。'
                    % (len(unresolved), ', '.join(tools_seen))
                )
        except Exception:
            pass

    # Always append lightweight hint
    reminders.append(
        '[RECORDING-HINT] 如做了设计决策或发现踩坑，请记录：'
        '决策 → .claude/decisions.md，踩坑 → session ### 本次踩坑/经验'
    )

    print(json.dumps({
        'continue': True,
        'additionalSystemPrompt': '\n'.join(reminders)
    }))
    sys.exit(0)


if __name__ == '__main__':
    main()
