"""Layer 1: hooks.json 事件完整性测试"""
import json, pytest
from pathlib import Path


REQUIRED_EVENTS = [
    "UserPromptSubmit",
    "SessionStart",
    "PreToolUse",
    "PostToolUse",
    "SubagentStart",
    "SubagentStop",
    "Stop",
    "PreCompact",
]


def test_hooks_json_exists(project_root):
    """验证 hooks.json 存在"""
    hooks_path = project_root / "hooks" / "hooks.json"
    assert hooks_path.exists(), f"hooks.json 不存在: {hooks_path}"


def test_hooks_has_required_events(project_root):
    """验证 hooks.json 包含全部 8 个必填事件"""
    hooks_path = project_root / "hooks" / "hooks.json"

    with open(hooks_path, encoding="utf-8") as f:
        data = json.load(f)

    assert "hooks" in data, "hooks.json 缺少 hooks 字段"
    hooks_events = data["hooks"]

    missing_events = [e for e in REQUIRED_EVENTS if e not in hooks_events]
    assert not missing_events, f"hooks.json 缺少必填事件: {missing_events}"


def test_hooks_events_have_non_empty_hooks_array(project_root):
    """验证每个事件的 hooks 数组非空"""
    hooks_path = project_root / "hooks" / "hooks.json"

    with open(hooks_path, encoding="utf-8") as f:
        data = json.load(f)

    hooks_events = data.get("hooks", {})

    for event_name in REQUIRED_EVENTS:
        assert event_name in hooks_events, f"缺少事件: {event_name}"
        event_config = hooks_events[event_name]

        # event_config 可以是数组（多个配置）或单个配置对象
        if isinstance(event_config, list):
            configs = event_config
        else:
            configs = [event_config]

        for config in configs:
            assert "hooks" in config, f"事件 {event_name} 的配置缺少 hooks 字段"
            assert isinstance(config["hooks"], list), f"事件 {event_name} 的 hooks 必须是数组"
            assert len(config["hooks"]) > 0, f"事件 {event_name} 的 hooks 数组不能为空"
