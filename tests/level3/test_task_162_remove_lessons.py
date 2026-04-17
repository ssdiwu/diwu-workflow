import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SCRIPT_PATH = PROJECT_ROOT / "hooks" / "scripts" / "user_prompt_submit.py"
ASSETS = PROJECT_ROOT / "assets" / "dinit" / "assets"
DINIT_PATH = PROJECT_ROOT / "commands" / "dinit.md"


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


def test_user_prompt_submit_no_longer_reads_lessons():
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "lessons.md" not in text
    assert "Agent 错误模式记录" not in text


def test_dinit_no_longer_mentions_lessons_template():
    text = DINIT_PATH.read_text(encoding="utf-8")
    assert "lessons.md.template" not in text
    assert ".claude/lessons.md" not in text


def test_lessons_template_deleted():
    assert not (ASSETS / "lessons.md.template").exists()


def test_user_prompt_submit_output_excludes_lessons_strings():
    result = _run_script()
    prompt = result["additionalSystemPrompt"]
    assert "Agent 错误模式记录" not in prompt
    assert "lessons" not in prompt.lower()
