"""Stop hook: archive aggregation.

When recording/ session count exceeds threshold, extract pitfall records
from soon-to-be-archived sessions and append to project-pitfalls.md.
"""
import json
import os
import re
import subprocess
from collections import defaultdict


def aggregate(settings):
    """Check and perform archive aggregation if threshold exceeded.

    Args:
        settings: dsettings dict

    Returns:
        (performed: bool, message: str) tuple
    """
    # Check switch: skip aggregation if disabled
    if not settings.get('pitfalls', {}).get('archive_aggregate', True):
        return 0, ''

    rec_dir = '.diwu/recording'
    pitfalls_path = '.diwu/project-pitfalls.md'
    threshold = settings.get('recording_archive_threshold', 50)

    if not os.path.isdir(rec_dir):
        return False, ''

    try:
        files = [
            os.path.join(rec_dir, f) for f in os.listdir(rec_dir)
            if f.startswith('session-') and f.endswith('.md')
        ]
    except Exception:
        return False, ''

    if len(files) <= threshold:
        return False, ''

    files.sort(key=os.path.getmtime)
    to_archive = files[:len(files) - threshold]
    if not to_archive:
        return False, ''

    pitfall_pattern = re.compile(
        r'###\s*本次踩坑\s*\n(.*?)(?=\n### |\n---|\Z)', re.DOTALL
    )
    categories = defaultdict(list)

    for fpath in to_archive:
        try:
            content = open(fpath, 'r', encoding='utf-8').read()
        except Exception:
            continue
        matches = pitfall_pattern.findall(content)
        for m in matches:
            cat_match = re.search(
                r'(?:##\s+|\*\*)([^#\n*]+?)(?:\*\*|\s*\n)', m.strip()
            )
            category = cat_match.group(1).strip()[:30] if cat_match else '未分类'
            categories[category].append(m.strip())

    if not categories:
        return False, ''

    try:
        now = subprocess.check_output(
            ['date', '+%Y-%m-%d %H:%M:%S'], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        now = ''

    lines = ['', f'> 归档聚合时间: {now}', f'> 来源: {len(to_archive)} 个 session 文件', '']
    for cat, items in categories.items():
        lines.append(f'### {cat}（归档聚合）')
        lines.append('')
        for item in items:
            lines.append(f'- {item.replace(chr(10), " ")[:200]}')
        lines.append('')

    mode = 'a' if os.path.exists(pitfalls_path) else 'w'
    try:
        with open(pitfalls_path, mode, encoding='utf-8') as pf:
            pf.write('\n'.join(lines))
        return True, (
            f'[ARCHIVE_AGGREGATE] 已归档聚合 {len(to_archive)} 个 session 的踩坑'
            f'记录到 project-pitfalls.md（{len(categories)} 个类别）。'
        )
    except Exception as e:
        return False, f'[ARCHIVE_AGGREGATE] 写入失败: {e}'
