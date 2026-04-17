from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
PLUGIN_JSON = PROJECT_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = PROJECT_ROOT / ".claude-plugin" / "marketplace.json"
CLAUDE_MD = PROJECT_ROOT / ".claude" / "CLAUDE.md"


def test_task_169_versions_are_synced_to_0_8_0():
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    marketplace = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))

    assert plugin["version"] == "0.8.0"
    assert marketplace["plugins"][0]["version"] == "0.8.0"



def test_task_169_claude_md_version_reference_matches_plugin():
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    text = CLAUDE_MD.read_text(encoding="utf-8")

    assert f"插件版本 {plugin['version']}" in text
    assert "插件版本 0.7.10" not in text
