from pathlib import Path
import json
import subprocess

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SCRIPT_PATH = PROJECT_ROOT / "hooks" / "scripts" / "user_prompt_submit.py"
MINDSET_PATH = PROJECT_ROOT / ".claude" / "rules" / "mindset.md"


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


def test_mindset_requires_project_pitfalls_preload():
    text = MINDSET_PATH.read_text(encoding="utf-8")
    assert "### 误判表预加载（必须执行）" in text
    assert ".diwu/project-pitfalls.md" in text
    assert "使用 Read 工具读取其完整内容" in text


def test_user_prompt_submit_lists_project_pitfalls_in_rfs():
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "('project-pitfalls.md', '项目高频误判表（Layer 2）')" in text
    assert "if name == 'project-pitfalls.md':" in text
    assert "os.path.join(cwd, '.diwu', name)" in text


def test_project_pitfalls_appears_in_index_when_file_exists(tmp_path):
    rules_dir = tmp_path / ".claude" / "rules"
    diwu_dir = tmp_path / ".diwu"
    rules_dir.mkdir(parents=True)
    diwu_dir.mkdir(parents=True)

    (rules_dir / "mindset.md").write_text("mindset", encoding="utf-8")
    for name in [
        "README.md",
        "constraints.md",
        "judgments.md",
        "task.md",
        "workflow.md",
        "session.md",
        "verification.md",
        "correction.md",
        "pitfalls.md",
        "exceptions.md",
        "templates.md",
        "file-layout.md",
    ]:
        (rules_dir / name).write_text(name, encoding="utf-8")
    (diwu_dir / "project-pitfalls.md").write_text("pitfall", encoding="utf-8")

    result = _run_script(str(tmp_path))
    prompt = result["additionalSystemPrompt"]
    assert "- **project-pitfalls.md**: 项目高频误判表（Layer 2）" in prompt
    assert "缺少以下规则文件：project-pitfalls.md" not in prompt
