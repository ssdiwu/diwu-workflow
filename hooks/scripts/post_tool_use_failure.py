#!/usr/bin/env python3
"""PostToolUseFailure: capture tool failures, track attempts,
prompt error logging following 3-strike protocol.

State: /tmp/diwu_errtrack_<sessionId> — JSON {errors: [...]}
Uses sessionId from event data for cross-process state sharing
within the same Claude Code session.

Strike protocol (inspired by planning-with-files):
  Attempt 1: Diagnose & Fix → identify root cause
  Attempt 2: Alternative Approach → different tool/method
  Attempt 3+: Broader Rethink → escalate or question assumptions

Non-blocking: uses additionalSystemPrompt only, never decision:block.
"""

import json, os, sys, time

ERRTRACK_PREFIX = '/tmp/diwu_errtrack_'
SETTINGS_FILE = '.diwu/dsettings.json'
STRIKE_LIMIT = 3
COOLDOWN_SEC = 60

STRIKE_MESSAGES = {
    1: "[ERROR-TRACK] Tool '{tool}' failed (attempt {strike}/{limit}). "
       "Diagnose root cause. If this reveals a recurring pitfall, "
       "log it in ### 本次踩坑/经验 format: "
       "- [category] phenomenon -> root cause -> wrong judgment -> correct action",

    2: "[ERROR-TRACK] Tool '{tool}' failed again (attempt {strike}/{limit}). "
       "First approach did not work. Try a fundamentally different approach "
       "(different tool, different file, different strategy).",

    3: "[ERROR-TRACK] Tool '{tool}' failed ({strike}/{limit} strikes). "
       "Stop and rethink broadly. Consider: fundamental misunderstanding? "
       "Wrong file? Wrong approach? Escalate to user if stuck.",
}


def _errtrack_path(session_id):
    """Return state file path using sessionId for cross-process sharing."""
    sid = session_id or str(os.getpid())
    return ERRTRACK_PREFIX + sid


def _load(p):
    if os.path.exists(p):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(p, d):
    try:
        with open(p, 'w') as f:
            json.dump(d, f)
    except Exception:
        pass


def _get_event_data():
    """Parse stdin JSON for tool failure event."""
    try:
        raw = sys.stdin.read()
        if not raw:
            return {}
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}


def _track_failure(ctx, tool_name, error_msg):
    """Update error tracking state, return strike count.

    Uses cooldown window: same tool failing within COOLDOWN_SEC increments
    the strike count; different tool or expired window resets to 1.
    """
    errors = ctx.get('errors', [])
    now = time.time()

    # Find last error for this tool
    last_strike = 0
    for e in reversed(errors):
        if e.get('tool') == tool_name:
            last_strike = e.get('strike', 0)
            break

    # Check if within cooldown window
    last_err_for_tool = None
    for e in reversed(errors):
        if e.get('tool') == tool_name:
            last_err_for_tool = e
            break

    if last_err_for_tool and (now - last_err_for_tool.get('ts', 0)) < COOLDOWN_SEC:
        strike = last_strike + 1
    else:
        strike = 1  # new sequence

    # Append tracking entry
    errors.append({
        'tool': tool_name,
        'error': (error_msg or '')[:200],
        'ts': now,
        'strike': strike,
    })

    # Keep bounded
    ctx['errors'] = errors[-20:]
    return strike


def main():
    settings = _load(SETTINGS_FILE)
    if settings.get('error_tracking', {}).get('enabled') == False:
        sys.exit(0)

    cfg = settings.get('error_tracking', {})
    limit = cfg.get('strike_limit', STRIKE_LIMIT)
    cooldown = cfg.get('cooldown_sec', COOLDOWN_SEC)

    event = _get_event_data()
    session_id = event.get('sessionId', event.get('session_id', ''))
    tool_name = event.get('toolName', event.get('tool_name', ''))
    error_msg = event.get('error', event.get('message', ''))

    if not tool_name:
        sys.exit(0)

    err_path = _errtrack_path(session_id)
    ctx = _load(err_path)
    strike = _track_failure(ctx, tool_name, error_msg)
    _save(err_path, ctx)

    # Get message (cap at strike limit for message lookup)
    msg_key = min(strike, limit)
    msg_template = STRIKE_MESSAGES.get(msg_key, STRIKE_MESSAGES[limit])
    message = msg_template.format(tool=tool_name, strike=strike, limit=limit)

    print(json.dumps({
        'continue': True,
        'additionalSystemPrompt': message
    }))
    sys.exit(0)


if __name__ == '__main__':
    main()
