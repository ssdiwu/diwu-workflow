#!/usr/bin/env python3
"""PreToolUse: inject recent errors & decisions before each tool call.

Two-tier mode:
- Tier1: Always output light reminder (~100 chars) pointing to files
- Tier2: Only when conditions met, extract and inject actual content
"""

import json, os, sys, re

CTX_PREFIX = '/tmp/diwu_ctx_'
RECORDING_DIR = '.diwu/recording'
DECISIONS_FILE = '.diwu/decisions.md'
SETTINGS_FILE = '.diwu/dsettings.json'
MAX_SESSIONS = 3
MAX_DECISIONS = 3
MAX_CHARS_PER_SECTION = 800

PITFALL_PATTERN = re.compile(
    r'###\s*本次踩坑[\/]?经验\s*\n(.*?)(?=\n### |\n---|\Z)',
    re.DOTALL
)
BULLET_PATTERN = re.compile(r'- \[([^\]]+)\]\s*(.+)')
# Session timestamp pattern for detecting new sessions
SESSION_TS_PATTERN = re.compile(r'^## Session (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')


def _ctx_path():
    return CTX_PREFIX + str(os.getpid())


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


def _tier1_reminder():
    """Always output a lightweight reminder pointing to source files."""
    parts = []
    if os.path.exists(RECORDING_DIR):
        parts.append('[diwu-ctx] 近期有踩坑记录，详见 .diwu/recording/ 最新 session 的「本次踩坑/经验」段落')
    if os.path.exists(DECISIONS_FILE):
        parts.append('[diwu-ctx] 有设计决策记录，详见 .diwu/decisions.md')
    if parts:
        return '\n'.join(parts)
    return ''


def _should_inject_tier2(ctx):
    """Check if Tier2 (full content injection) should trigger."""
    # Condition 1: Same tool failed 2+ times (check error tracking)
    errtrack_path = CTX_PREFIX + str(os.getpid()) + '_errtrack'
    err_data = _load(errtrack_path)
    tool_errs = errdata.get('tool_errors', {})
    for tool, count in tool_errs.items():
        if count >= 2:
            return True, f'工具 {tool} 连续失败 {count} 次'

    # Condition 2: Drift was recently detected
    drift_detected = ctx.get('_last_drift_time', 0)
    if drift_detected and (os.time() - drift_detected < 300):  # within 5 min
        return True, '近期检测到退化信号'

    # Condition 3: New session file detected since last injection
    last_session_ts = ctx.get('_last_injected_session_ts', '')
    if os.path.exists(RECORDING_DIR):
        try:
            sessions = sorted(
                [f for f in os.listdir(RECORDING_DIR)
                 if f.startswith('session-') and f.endswith('.md')],
                key=lambda f: os.path.getmtime(os.path.join(RECORDING_DIR, f)),
                reverse=True
            )
            if sessions:
                latest = sessions[0]
                # Extract timestamp from filename or content
                rp = os.path.join(RECORDING_DIR, latest)
                rc = open(rp).read()
                ts_match = SESSION_TS_PATTERN.search(rc)
                if ts_match and ts_match.group(1) != last_session_ts:
                    return True, f'发现新 session 文件: {latest}'
        except Exception:
            pass

    return False, ''


def _extract_pitfalls(recording_dir, max_sessions):
    """Scan recent session files for ### 本次踩坑/经验 sections."""
    if not os.path.exists(recording_dir):
        return ''

    files = sorted(
        [f for f in os.listdir(recording_dir)
         if f.startswith('session-') and f.endswith('.md')],
        key=lambda f: os.path.getmtime(os.path.join(recording_dir, f)),
        reverse=True
    )[:max_sessions]

    results = []
    for fname in files:
        try:
            content = open(os.path.join(recording_dir, fname)).read()
        except Exception:
            continue

        match = PITFALL_PATTERN.search(content)
        if not match:
            continue

        section = match.group(1).strip()
        if '无显著误判' in section and '符合预期' in section:
            continue

        bullets = BULLET_PATTERN.findall(section)
        for cat, text in bullets:
            clean = text.strip()
            if len(clean) > 120:
                clean = clean[:117] + '...'
            results.append(f'- [{cat}] {clean}')

    if not results:
        return ''

    header = '[diwu-ctx] 近期踩坑经验（最近 %d 个 Session）\n' % min(len(files), max_sessions)
    body = '\n'.join(results)
    total = header + body
    if len(total) > MAX_CHARS_PER_SECTION:
        total = total[:MAX_CHARS_PER_SECTION - 12] + '...(truncated)'
    return total


def _extract_decisions(decisions_path, max_decisions):
    """Extract recent DEC-NNN entries from decisions.md."""
    if not os.path.exists(decisions_path):
        return ''

    try:
        dc = open(decisions_path).read()
    except Exception:
        return ''

    decs = re.split(r'(?=^## DEC-)', dc, flags=re.MULTILINE)
    decs = [x for x in decs if x.strip().startswith('## DEC-')]
    if not decs:
        return ''

    recent = decs[-max_decisions:]
    lines = []
    for entry in recent:
        entry = entry.strip()
        first_line = entry.split('\n')[0]
        lines.append(first_line)

        decision_m = re.search(r'\*\*决策\*\*[：:]\s*(.+)', entry)
        rationale_m = re.search(r'\*\*理由\*\*[：:]\s*(.+)', entry)

        if decision_m:
            d_text = decision_m.group(1).strip()
            if len(d_text) > 100:
                d_text = d_text[:97] + '...'
            lines.append('  **决策**: ' + d_text)
        if rationale_m:
            r_text = rationale_m.group(1).strip()
            if len(r_text) > 80:
                r_text = r_text[:77] + '...'
            lines.append('  **理由**: ' + r_text)
        lines.append('')

    header = '[diwu-ctx] 近期设计决策\n'
    body = '\n'.join(lines).strip()
    total = header + body
    if len(total) > MAX_CHARS_PER_SECTION:
        total = total[:MAX_CHARS_PER_SECTION - 12] + '...(truncated)'
    return total


def main():
    settings = _load(SETTINGS_FILE)
    if settings.get('error_injection', {}).get('enabled') == False:
        sys.exit(0)

    cfg = settings.get('error_injection', {})
    max_s = cfg.get('max_sessions', MAX_SESSIONS)
    max_d = cfg.get('max_decisions', MAX_DECISIONS)

    # Tier1: always inject light reminder
    tier1 = _tier1_reminder()

    # Tier2: check conditions
    ctx = _load(_ctx_path())
    should_tier2, reason = _should_inject_tier2(ctx)

    parts = []
    if tier1:
        parts.append(tier1)

    if should_tier2:
        error_text = _extract_pitfalls(RECORDING_DIR, max_s)
        if error_text:
            parts.append(error_text)

        dec_text = _extract_decisions(DECISIONS_FILE, max_d)
        if dec_text:
            parts.append(dec_text)

        # Update last injected session timestamp
        if os.path.exists(RECORDING_DIR):
            try:
                sessions = sorted(
                    [f for f in os.listdir(RECORDING_DIR)
                     if f.startswith('session-') and f.endswith('.md')],
                    key=lambda f: os.path.getmtime(os.path.join(RECORDING_DIR, f)),
                    reverse=True
                )
                if sessions:
                    rp = os.path.join(RECORDING_DIR, sessions[0])
                    rc = open(rp).read()
                    ts_match = SESSION_TS_PATTERN.search(rc)
                    if ts_match:
                        ctx['_last_injected_session_ts'] = ts_match.group(1)
                        _save(_ctx_path(), ctx)
            except Exception:
                pass

    if parts:
        print(json.dumps({
            'continue': True,
            'additionalSystemPrompt': '\n\n'.join(parts)
        }))

    sys.exit(0)


if __name__ == '__main__':
    main()
