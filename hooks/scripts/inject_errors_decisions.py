#!/usr/bin/env python3
"""PreToolUse: inject recent errors & decisions before each tool call.

Extracts ### 本次踩坑/经验 from recent session files and
## DEC-NNN entries from decisions.md, injects as additionalSystemPrompt.
Non-blocking (exit code always 0). Follows drift_detect_pre.py patterns.

Inspired by planning-with-files (OthmanAdi) PreToolUse attention manipulation:
"Context Window = RAM, Filesystem = Disk — anything important gets written to disk,
 and re-injected before every action."
"""

import json, os, sys, re

CTX_PREFIX = '/tmp/diwu_ctx_'
RECORDING_DIR = '.diwu/recording'
DECISIONS_FILE = '.diwu/decisions.md'
SETTINGS_FILE = '.diwu/dsettings.json'
MAX_SESSIONS = 3
MAX_DECISIONS = 3
MAX_CHARS_PER_SECTION = 800

# Same pattern as session.md Stop hook validation
PITFALL_PATTERN = re.compile(
    r'###\s*本次踩坑[\/]?经验\s*\n(.*?)(?=\n### |\n---|\Z)',
    re.DOTALL
)
# Extract individual bullet entries: - [category] text
BULLET_PATTERN = re.compile(r'- \[([^\]]+)\]\s*(.+)')


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


def _extract_pitfalls(recording_dir, max_sessions):
    """Scan recent session files for ### 本次踩坑/经验 sections.

    Returns formatted error summary string, or '' if none found.
    """
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
        # Skip minimal valid answer (no real pitfalls)
        if '无显著误判' in section and '符合预期' in section:
            continue

        # Extract bullet entries
        bullets = BULLET_PATTERN.findall(section)
        for cat, text in bullets:
            clean = text.strip()
            # Truncate long entries
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
    """Extract recent DEC-NNN entries from decisions.md.

    Reuses same split logic as subagent_start.py line 44.
    """
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
        # Extract title line
        first_line = entry.split('\n')[0]
        lines.append(first_line)

        # Try to extract **决策** and **理由** one-liners
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
        lines.append('')  # blank separator

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

    parts = []

    error_text = _extract_pitfalls(RECORDING_DIR, max_s)
    if error_text:
        parts.append(error_text)

    dec_text = _extract_decisions(DECISIONS_FILE, max_d)
    if dec_text:
        parts.append(dec_text)

    if parts:
        print(json.dumps({
            'continue': True,
            'additionalSystemPrompt': '\n\n'.join(parts)
        }))

    sys.exit(0)


if __name__ == '__main__':
    main()
