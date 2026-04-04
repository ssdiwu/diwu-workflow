"""Layer 2 Hook 脚本单元测试: stop_blocking.py"""
import json, subprocess, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SCRIPT_PATH = PROJECT_ROOT / "hooks" / "scripts" / "stop_blocking.py"


def test_with_inprogress_task_outputs_task_info(tmp_path):
    """存在 InProgress 任务时输出包含 Task# 前缀和任务标题"""
    # 准备 .claude 目录和 task.json
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    task_file = claude_dir / "task.json"

    task_data = {
        "tasks": [
            {
                "id": 3,
                "title": "修复登录 bug",
                "description": "修复用户无法登录的问题",
                "acceptance": ["Given 用户输入正确密码 Then 登录成功"],
                "steps": ["1. 检查认证逻辑"],
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
    assert "Task#3" in result.stdout, f"期望输出包含 Task#3，实际输出: {result.stdout}"
    assert "修复登录 bug" in result.stdout, f"期望输出包含任务标题，实际输出: {result.stdout}"
    assert result.returncode == 0


def test_without_inprogress_task_no_output(tmp_path):
    """无 InProgress 任务时不生成 continue-here.md 文件"""
    # 准备 .claude 目录和 task.json（无 InProgress 任务）
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    task_file = claude_dir / "task.json"

    task_data = {
        "tasks": [
            {
                "id": 1,
                "title": "已完成的任务",
                "description": "描述",
                "acceptance": [],
                "steps": [],
                "status": "Done"
            },
            {
                "id": 2,
                "title": "待处理任务",
                "description": "描述",
                "acceptance": [],
                "steps": [],
                "status": "InSpec"
            }
        ]
    }
    task_file.write_text(json.dumps(task_data, ensure_ascii=False, indent=2))

    continue_here_file = claude_dir / "continue-here.md"

    # 执行脚本前文件不存在
    assert not continue_here_file.exists(), "测试前置条件：continue-here.md 不应存在"

    # 执行脚本
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True
    )

    # 验证无输出
    assert result.stdout.strip() == "", f"期望无输出，实际输出: {result.stdout}"
    assert result.returncode == 0


def test_no_task_json_exits_zero(tmp_path):
    """不存在 task.json 时 exit 0"""
    # 不创建 task.json

    # 执行脚本
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True
    )

    # 验证 exit 0
    assert result.returncode == 0
