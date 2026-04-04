"""Layer 1: marketplace.json 结构完整性测试"""
import json, pytest
from pathlib import Path


def test_marketplace_json_exists(project_root):
    """验证 marketplace.json 存在"""
    marketplace_path = project_root / ".claude-plugin" / "marketplace.json"
    assert marketplace_path.exists(), f"marketplace.json 不存在: {marketplace_path}"


def test_marketplace_has_plugins_array(project_root):
    """验证 marketplace.json 包含 plugins 数组"""
    marketplace_path = project_root / ".claude-plugin" / "marketplace.json"

    with open(marketplace_path, encoding="utf-8") as f:
        data = json.load(f)

    assert "plugins" in data, "marketplace.json 缺少 plugins 字段"
    assert isinstance(data["plugins"], list), "plugins 必须是数组"


def test_marketplace_plugins_have_required_fields(project_root):
    """验证 plugins 数组至少一个条目包含 name/description/source"""
    marketplace_path = project_root / ".claude-plugin" / "marketplace.json"

    with open(marketplace_path, encoding="utf-8") as f:
        data = json.load(f)

    plugins = data.get("plugins", [])
    assert len(plugins) > 0, "plugins 数组不能为空"

    # 找到第一个条目，验证它有 name/description/source
    first_plugin = plugins[0]
    required_fields = ["name", "description", "source"]
    for field in required_fields:
        assert field in first_plugin, f"plugins[0] 缺少必填字段: {field}"
        assert first_plugin[field], f"plugins[0] 字段 '{field}' 不能为空"
