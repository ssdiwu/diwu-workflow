from pathlib import Path
import json
import subprocess

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SCRIPT_PATH = PROJECT_ROOT / "hooks" / "scripts" / "user_prompt_submit.py"
CLAUDE_RULES = PROJECT_ROOT / ".claude" / "rules"
ASSET_CONSTRAINTS = PROJECT_ROOT / "assets" / "dinit" / "assets" / "rules" / "constraints.md"
CLAUDE_MD = PROJECT_ROOT / ".claude" / "CLAUDE.md"


def _run_script(cwd=None):
    env_input = json.dumps({"cwd": cwd or str(PROJECT_ROOT)})
    result = subprocess.run(
        ["python3", str(SCRIPT_PATH)],
        input=env_input,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_constraints_rule_is_generic():
    text = (CLAUDE_RULES / "constraints.md").read_text(encoding="utf-8")
    assert text.startswith("# 架构约束")
    assert "diwu-workflow 架构约束" not in text
    assert "State Machines" not in text
    assert "Data Ownership" not in text
    assert ".claude-plugin/plugin.json" not in text


def test_constraints_template_matches_project_rule():
    rule_text = (CLAUDE_RULES / "constraints.md").read_text(encoding="utf-8")
    asset_text = ASSET_CONSTRAINTS.read_text(encoding="utf-8")
    assert rule_text == asset_text


def test_constraints_moves_from_full_injection_to_index():
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "content += '\\n\\n# 架构约束" not in source
    assert "('constraints.md', '架构约束（五维约束设计）')" in source



def test_constraints_only_appears_in_index_output():
    result = _run_script()
    prompt = result["additionalSystemPrompt"]
    assert "- **constraints.md**: 架构约束（五维约束设计）" in prompt
    assert "## Constraints" not in prompt



def test_claude_md_keeps_plugin_specific_constraints():
    text = CLAUDE_MD.read_text(encoding="utf-8")
    assert "## 插件开发专属约束" in text
    assert "### 版本号语义化规则" in text
    assert "### 发版状态机" in text
    assert "### 跨平台路径约束" in text
    assert "### 并发约束" in text
    assert "### 数据所有权" in text
