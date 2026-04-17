from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
HOOKS_DIR = PROJECT_ROOT / "hooks" / "scripts"
TASK_JSON_PATH = PROJECT_ROOT / ".claude" / "task.json"

RUNTIME_TARGETS = [
    "task.json",
    "recording",
    "decisions.md",
    "dsettings.json",
    "project-pitfalls.md",
    "archive",
]

EXPECTED_DIWU_FILES = {
    "task_completed.py": [".diwu/dsettings.json", ".diwu/task.json", ".diwu/recording/", ".diwu/decisions.md"],
    "pre_tool_use_bash.py": [".diwu/task.json"],
    "stop_blocking.py": [".diwu/recording", ".diwu/project-pitfalls.md", ".diwu/task.json", ".diwu/dsettings.json"],
    "context_monitor.py": [".diwu/dsettings.json", ".diwu/recording", ".diwu/task.json"],
    "inject_errors_decisions.py": [".diwu/recording", ".diwu/decisions.md", ".diwu/dsettings.json"],
    "stop_background.py": [".diwu/recording", ".diwu/dsettings.json"],
    "pre_compact.py": [".diwu/task.json", ".diwu/recording"],
    "drift_detect_pre.py": [".diwu/task.json", ".diwu/dsettings.json"],
    "post_tool_use_failure.py": [".diwu/dsettings.json"],
    "post_tool_reminder.py": [".diwu/dsettings.json", ".diwu/decisions.md"],
    "subagent_stop.py": [".diwu/task.json"],
    "task_created_validate.py": [".diwu/task.json"],
}


def test_runtime_paths_move_to_diwu_in_hook_scripts():
    for name, expected_paths in EXPECTED_DIWU_FILES.items():
        text = (HOOKS_DIR / name).read_text(encoding="utf-8")
        for expected in expected_paths:
            assert expected in text, f"{name} 缺少 {expected}"


def test_hook_scripts_no_longer_reference_claude_runtime_paths():
    offenders = []
    for path in HOOKS_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for target in RUNTIME_TARGETS:
            needle = f".claude/{target}"
            if needle in text:
                offenders.append(f"{path.name}: {needle}")
    assert offenders == [], "仍有 .claude 运行时路径残留: " + ", ".join(offenders)


def test_task_created_validate_uses_relative_diwu_task_path():
    text = (HOOKS_DIR / "task_created_validate.py").read_text(encoding="utf-8")
    assert 'TASK_JSON_PATH = ".diwu/task.json"' in text
    assert "/Users/diwu/Documents/codes/Githubs/diwu-workflow/.claude/task.json" not in text


def test_hook_scripts_py_compile():
    files = [str(p) for p in HOOKS_DIR.glob("*.py")]
    subprocess.run(["python3", "-m", "py_compile", *files], check=True, cwd=PROJECT_ROOT)
