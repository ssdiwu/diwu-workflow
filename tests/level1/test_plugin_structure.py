"""Layer 1: plugin.json 必填字段完整性测试"""
import json, pytest
from pathlib import Path


def test_plugin_json_required_fields_exist(project_root):
    """验证 plugin.json 必填字段存在"""
    plugin_path = project_root / ".claude-plugin" / "plugin.json"
    assert plugin_path.exists(), f"plugin.json 不存在: {plugin_path}"

    with open(plugin_path, encoding="utf-8") as f:
        data = json.load(f)

    required_fields = ["name", "version", "description", "commands", "skills"]
    for field in required_fields:
        assert field in data, f"plugin.json 缺少必填字段: {field}"


def test_plugin_json_required_fields_non_empty(project_root):
    """验证 plugin.json 必填字段非空"""
    plugin_path = project_root / ".claude-plugin" / "plugin.json"

    with open(plugin_path, encoding="utf-8") as f:
        data = json.load(f)

    required_fields = ["name", "version", "description", "commands", "skills"]
    for field in required_fields:
        value = data[field]
        assert value, f"plugin.json 字段 '{field}' 不能为空"
        if isinstance(value, str):
            assert value.strip(), f"plugin.json 字段 '{field}' 不能为空白字符串"
        elif isinstance(value, list):
            assert len(value) > 0, f"plugin.json 字段 '{field}' 数组不能为空"


def test_plugin_commands_paths_exist(project_root):
    """验证 plugin.json 中 commands 引用路径实际存在"""
    plugin_path = project_root / ".claude-plugin" / "plugin.json"

    with open(plugin_path, encoding="utf-8") as f:
        data = json.load(f)

    commands = data.get("commands", [])
    assert isinstance(commands, list), "commands 必须是数组"

    for cmd in commands:
        # cmd 格式: "./commands/dinit.md" 或 {"path": "./commands/dinit.md"}
        if isinstance(cmd, dict):
            cmd_path = cmd.get("path", "")
        else:
            cmd_path = cmd

        # 去掉开头的 ./
        if cmd_path.startswith("./"):
            cmd_path = cmd_path[2:]

        full_path = project_root / cmd_path
        assert full_path.exists(), f"plugin.json 中引用的 commands 文件不存在: {cmd_path}"


def test_plugin_skills_paths_exist(project_root):
    """验证 plugin.json 中 skills 引用路径实际存在"""
    plugin_path = project_root / ".claude-plugin" / "plugin.json"

    with open(plugin_path, encoding="utf-8") as f:
        data = json.load(f)

    skills = data.get("skills", [])
    assert isinstance(skills, list), "skills 必须是数组"

    for skill in skills:
        # skill 格式: "./skills/ddoc" 或 {"path": "./skills/ddoc"}
        if isinstance(skill, dict):
            skill_path = skill.get("path", "")
        else:
            skill_path = skill

        # 去掉开头的 ./
        if skill_path.startswith("./"):
            skill_path = skill_path[2:]

        full_path = project_root / skill_path
        assert full_path.exists(), f"plugin.json 中引用的 skills 目录不存在: {skill_path}"
