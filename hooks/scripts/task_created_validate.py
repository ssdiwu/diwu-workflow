"""TaskCreated: validate new task fields, GWT format, and blocked_by cycle detection.

GWT check supports both English (Given/When/Then) and Chinese (给定/当/则).
Cycle detection uses DFS with visited set.
"""
import json, sys

TASK_JSON_PATH = ".diwu/task.json"
REQUIRED_FIELDS = ["id", "title", "description", "acceptance", "steps", "category", "status"]
# English or Chinese GWT keywords
GWT_PATTERNS = [
    ("Given", "给定"),  # Given or 给定
    ("When", "当"),     # When or 当
    ("Then", "则"),     # Then or 则
]
GWT_CATEGORIES = ["functional", "ui", "bugfix"]


def _load(p):
    if os.path.exists(p):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _has_gwt_keywords(text):
    """Check if text contains GWT pattern (English or Chinese)."""
    found = 0
    for en, zh in GWT_PATTERNS:
        if en in text or zh in text:
            found += 1
    return found >= 2  # at least 2 of 3 keyword pairs


def validate_required_fields(task):
    tid = task.get("id")
    missing = [f for f in REQUIRED_FIELDS if not task.get(f)]
    if missing:
        print(f"[diwu] Task#{tid} 必填字段缺失: {missing}", file=sys.stderr)
        return False
    return True


def validate_gwt_format(task):
    tid = task.get("id")
    category = task.get("category", "")
    if category not in GWT_CATEGORIES:
        return True

    acceptance = task.get("acceptance", [])
    if not isinstance(acceptance, list):
        print(f"[diwu] Task#{tid} acceptance 必须为数组", file=sys.stderr)
        return False

    for i, item in enumerate(acceptance):
        if not isinstance(item, str):
            continue
        if not _has_gwt_keywords(item):
            print(f"[diwu] Task#{tid} acceptance[{i}] 缺少 Given/When/Then（或中文 给定/当/则）关键词", file=sys.stderr)
            return False
    return True


def detect_cycle(task_id, blocked_by, tasks_map, visited=None, stack=None):
    if visited is None:
        visited = set()
    if stack is None:
        stack = []
    if task_id in stack:
        idx = stack.index(task_id)
        return stack[idx:] + [task_id]
    if task_id in visited:
        return None
    visited.add(task_id)
    stack.append(task_id)
    for dep_id in blocked_by.get(task_id, []):
        cycle = detect_cycle(dep_id, blocked_by, tasks_map, visited, stack)
        if cycle:
            return cycle
    stack.pop()
    return None


def validate_blocked_by_cycle(task):
    tid = task.get("id")
    blocked_by_new = task.get("blocked_by", [])
    if not blocked_by_new:
        return True

    all_blocked_by = {}
    try:
        data = _load(TASK_JSON_PATH)
        for t in data.get("tasks", []):
            if t.get("id") != tid:
                all_blocked_by[t["id"]] = t.get("blocked_by", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[diwu] task.json 解析失败: {e}", file=sys.stderr)
        return False

    all_blocked_by[tid] = blocked_by_new
    cycle = detect_cycle(tid, all_blocked_by, None)
    if cycle:
        print(f"[diwu] Task#{tid} blocked_by 循环依赖检测失败: {cycle}", file=sys.stderr)
        return False
    return True


def main():
    data = json.load(sys.stdin)
    task = data.get("task")
    if not task:
        print("[diwu] 缺少 task 对象", file=sys.stderr)
        sys.exit(1)

    if not validate_required_fields(task):
        sys.exit(1)
    if not validate_gwt_format(task):
        sys.exit(1)
    if not validate_blocked_by_cycle(task):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
