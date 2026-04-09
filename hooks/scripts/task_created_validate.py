import json, sys

TASK_JSON_PATH = "/Users/diwu/Documents/codes/Githubs/diwu-workflow/.claude/task.json"
REQUIRED_FIELDS = ["id", "title", "description", "acceptance", "steps", "category", "status"]
GWT_KEYWORDS = ["Given", "When", "Then"]
GWT_CATEGORIES = ["functional", "ui", "bugfix"]


def validate_required_fields(task):
    task_id = task.get("id")
    missing = [f for f in REQUIRED_FIELDS if not task.get(f)]
    if missing:
        print(f"[diwu] Task#{task_id} 必填字段缺失: {missing}", file=sys.stderr)
        return False
    return True


def validate_gwt_format(task):
    task_id = task.get("id")
    category = task.get("category", "")
    if category not in GWT_CATEGORIES:
        return True

    acceptance = task.get("acceptance", [])
    if not isinstance(acceptance, list):
        print(f"[diwu] Task#{task_id} acceptance 必须为数组", file=sys.stderr)
        return False

    for i, item in enumerate(acceptance):
        if not isinstance(item, str):
            continue
        if not all(kw in item for kw in GWT_KEYWORDS):
            print(f"[diwu] Task#{task_id} acceptance[{i}] 缺少 Given/When/Then 关键词", file=sys.stderr)
            return False
    return True


def detect_cycle(task_id, blocked_by, tasks_map, visited=None, stack=None):
    if visited is None:
        visited = set()
    if stack is None:
        stack = []

    if task_id in stack:
        cycle_start = stack.index(task_id)
        cycle_chain = stack[cycle_start:] + [task_id]
        return cycle_chain

    if task_id in visited:
        return None

    visited.add(task_id)
    stack.append(task_id)

    deps = blocked_by.get(task_id, [])
    for dep_id in deps:
        cycle = detect_cycle(dep_id, blocked_by, tasks_map, visited, stack)
        if cycle:
            return cycle

    stack.pop()
    return None


def validate_blocked_by_cycle(task):
    task_id = task.get("id")
    blocked_by_new = task.get("blocked_by", [])

    if not blocked_by_new:
        return True

    blocked_by = {}
    try:
        with open(TASK_JSON_PATH) as f:
            data = json.load(f)
            for t in data.get("tasks", []):
                tid = t.get("id")
                if tid != task_id:
                    blocked_by[tid] = t.get("blocked_by", [])
    except FileNotFoundError:
        pass
    except json.JSONDecodeError as e:
        print(f"[diwu] task.json 解析失败: {e}", file=sys.stderr)
        return False

    blocked_by[task_id] = blocked_by_new

    cycle = detect_cycle(task_id, blocked_by, None)
    if cycle:
        print(f"[diwu] Task#{task_id} blocked_by 循环依赖检测失败: {cycle}", file=sys.stderr)
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
