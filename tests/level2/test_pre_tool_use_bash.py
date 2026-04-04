"""Layer 2 Hook 脚本单元测试: pre_tool_use_bash.py"""
import json, os, subprocess, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SCRIPT_PATH = PROJECT_ROOT / "hooks" / "scripts" / "pre_tool_use_bash.py"


def test_with_inprogress_task_outputs_task_info(tmp_path):
    """有 InProgress 任务时输出包含 Task# 前缀和任务标题"""
    # 准备 .claude 目录和 task.json
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    task_file = claude_dir / "task.json"

    task_data = {
        "tasks": [
            {
                "id": 5,
                "title": "实现用户登录功能",
                "description": "完成登录 API",
                "acceptance": ["Given x When y Then z"],
                "steps": ["1. 实现登录"],
                "status": "InProgress"
            }
        ]
    }
    task_file.write_text(json.dumps(task_data, ensure_ascii=False, indent=2))

    # 执行脚本
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True
    )

    # 验证输出包含 Task# 和任务标题
    assert "Task#5" in result.stdout, f"期望输出包含 Task#5，实际输出: {result.stdout}"
    assert "实现用户登录功能" in result.stdout, f"期望输出包含任务标题，实际输出: {result.stdout}"
    assert result.returncode == 0


def test_without_inprogress_task_no_output(tmp_path):
    """无 InProgress 任务时无输出且 exit 0"""
    # 准备 .claude 目录和 task.json（全部是 InSpec 状态）
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    task_file = claude_dir / "task.json"

    task_data = {
        "tasks": [
            {
                "id": 1,
                "title": "任务 A",
                "description": "描述",
                "acceptance": [],
                "steps": [],
                "status": "InSpec"
            }
        ]
    }
    task_file.write_text(json.dumps(task_data, ensure_ascii=False, indent=2))

    # 执行脚本
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True
    )

    # 验证无输出且 exit 0
    assert result.stdout.strip() == "", f"期望无输出，实际输出: {result.stdout}"
    assert result.stderr.strip() == "", f"期望无错误输出，实际输出: {result.stderr}"
    assert result.returncode == 0
