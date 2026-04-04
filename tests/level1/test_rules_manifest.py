"""Layer 1: rules-manifest.json 文件存在性测试"""
import json, pytest
from pathlib import Path


def test_rules_manifest_exists(project_root):
    """验证 rules-manifest.json 存在"""
    manifest_path = project_root / "assets" / "dinit" / "assets" / "rules-manifest.json"
    assert manifest_path.exists(), f"rules-manifest.json 不存在: {manifest_path}"


def test_rules_manifest_has_rules_field(project_root):
    """验证 rules-manifest.json 包含 rules 字段"""
    manifest_path = project_root / "assets" / "dinit" / "assets" / "rules-manifest.json"

    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)

    assert "rules" in data, "rules-manifest.json 缺少 rules 字段"
    assert isinstance(data["rules"], list), "rules 必须是数组"


def test_rules_manifest_files_exist(project_root):
    """验证 rules-manifest.json 中列出的文件全部存在于 assets/dinit/assets/rules/"""
    manifest_path = project_root / "assets" / "dinit" / "assets" / "rules-manifest.json"
    rules_dir = project_root / "assets" / "dinit" / "assets" / "rules"

    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)

    rules = data.get("rules", [])
    assert len(rules) > 0, "rules 数组不能为空"

    missing_files = []
    for rule_file in rules:
        rule_path = rules_dir / rule_file
        if not rule_path.exists():
            missing_files.append(rule_file)

    assert not missing_files, f"rules-manifest.json 中列出的文件不存在于 rules/ 目录: {missing_files}"
