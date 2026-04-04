"""Layer 2 Hook 脚本单元测试: post_tool_json_validate.py"""
import json, subprocess, sys
from pathlib import Path


def test_invalid_json_file_outputs_validation_error(tmp_path):
    """传入含语法错误的 .json 文件路径时输出包含 JSON 校验失败"""
    # 创建含语法错误的 JSON 文件
    invalid_json = tmp_path / "bad.json"
    invalid_json.write_text('{"key": "value",}')  # 尾部逗号，JSON 语法错误

    # 构造 stdin 输入
    stdin_data = json.dumps({"tool_input": {"file_path": str(invalid_json)}})

    # 执行脚本
    result = subprocess.run(
        [sys.executable, "hooks/scripts/post_tool_json_validate.py"],
        input=stdin_data,
        capture_output=True,
        text=True
    )

    # 验证输出包含 JSON 校验失败信息
    assert "JSON 校验失败" in result.stdout or "校验失败" in result.stdout, \
        f"期望输出包含'JSON 校验失败'，实际输出: {result.stdout}"


def test_nonexistent_file_exits_zero(tmp_path):
    """传入不存在的文件路径时无输出且 exit 0"""
    # 构造 stdin 输入（文件不存在）
    stdin_data = json.dumps({"tool_input": {"file_path": "/nonexistent/file.json"}})

    # 执行脚本
    result = subprocess.run(
        [sys.executable, "hooks/scripts/post_tool_json_validate.py"],
        input=stdin_data,
        capture_output=True,
        text=True
    )

    # 验证无输出且 exit 0
    assert result.stdout.strip() == "", f"期望无输出，实际输出: {result.stdout}"
    assert result.stderr.strip() == "", f"期望无错误输出，实际输出: {result.stderr}"
    assert result.returncode == 0


def test_non_json_file_valid_json_content_exits_zero(tmp_path):
    """传入非 .json 文件但内容为有效 JSON 时无输出且 exit 0"""
    # 创建内容是有效 JSON 但扩展名不是 .json 的文件
    non_json_file = tmp_path / "data.txt"
    non_json_file.write_text('{"key": "value"}')

    # 构造 stdin 输入
    stdin_data = json.dumps({"tool_input": {"file_path": str(non_json_file)}})

    # 执行脚本
    result = subprocess.run(
        [sys.executable, "hooks/scripts/post_tool_json_validate.py"],
        input=stdin_data,
        capture_output=True,
        text=True
    )

    # 验证无输出且 exit 0（脚本只验证 JSON 语法，不检查扩展名）
    assert result.stdout.strip() == "", f"期望无输出，实际输出: {result.stdout}"
    assert result.stderr.strip() == "", f"期望无错误输出，实际输出: {result.stderr}"
    assert result.returncode == 0


def test_valid_json_file_exits_zero(tmp_path):
    """传入有效 .json 文件时无输出且 exit 0"""
    # 创建有效 JSON 文件
    valid_json = tmp_path / "valid.json"
    valid_json.write_text('{"key": "value"}')

    # 构造 stdin 输入
    stdin_data = json.dumps({"tool_input": {"file_path": str(valid_json)}})

    # 执行脚本
    result = subprocess.run(
        [sys.executable, "hooks/scripts/post_tool_json_validate.py"],
        input=stdin_data,
        capture_output=True,
        text=True
    )

    # 验证无输出且 exit 0
    assert result.stdout.strip() == "", f"期望无输出，实际输出: {result.stdout}"
    assert result.stderr.strip() == "", f"期望无错误输出，实际输出: {result.stderr}"
    assert result.returncode == 0
