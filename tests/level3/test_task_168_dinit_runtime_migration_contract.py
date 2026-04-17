from pathlib import Path
import json
import shutil
import subprocess
import tempfile

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
COMMAND_PATH = PROJECT_ROOT / "commands" / "dinit.md"
HERA_PROJECT_PATH = Path("/Users/diwu/Documents/codes/Hera/hera-backend-demos")

LEGACY_RUNTIME_ITEMS = [
    ".claude/task.json",
    ".claude/recording/",
    ".claude/decisions.md",
    ".claude/dsettings.json",
    ".claude/project-pitfalls.md",
    ".claude/archive/",
    ".claude/continue-here.md",
    ".claude/checks/",
]
NATIVE_CLAUDE_ITEMS = [
    ".claude/CLAUDE.md",
    "rules/",
    "agents/",
    "skills/",
]


def test_dinit_documents_generic_runtime_migration_contract():
    text = COMMAND_PATH.read_text(encoding="utf-8")
    for item in LEGACY_RUNTIME_ITEMS:
        assert item in text
    assert "迁移到 `.diwu/`" in text
    assert "创建 `.diwu/` 目录" in text or "创建 `.diwu/recording/` 目录" in text



def test_dinit_preserves_claude_native_mechanisms_during_migration():
    text = COMMAND_PATH.read_text(encoding="utf-8")
    for item in NATIVE_CLAUDE_ITEMS:
        assert item in text
    assert "保留 `.claude/CLAUDE.md`、`rules/`、`agents/`、`skills/` 等 Claude 原生机制目录不动" in text



def test_dinit_requires_actual_migration_not_just_prompting():
    text = COMMAND_PATH.read_text(encoding="utf-8")
    assert "执行自动迁移" in text
    assert "将上述旧运行时文件迁移到 `.diwu/`" in text



def test_dinit_can_migrate_existing_hera_project_runtime_to_diwu():
    assert HERA_PROJECT_PATH.exists(), HERA_PROJECT_PATH

    with tempfile.TemporaryDirectory(prefix="hera-dinit-migration-") as tmp:
        target = Path(tmp) / "hera-backend-demos"
        shutil.copytree(HERA_PROJECT_PATH, target)

        prompt = (
            f"你现在在已有项目 {target} 中工作。不要只解释，不要总结。必须实际执行文件修改。"
            f"先读取 {COMMAND_PATH}，把它当作唯一 canonical。"
            "然后按其中 Refresh Protocol 与 Step 2 旧运行时目录迁移规则，对当前项目执行刷新："
            "1) 创建 .diwu/ 及其 runtime 子目录；"
            "2) 将 .claude/task.json、.claude/recording/、.claude/decisions.md、.claude/dsettings.json、.claude/project-pitfalls.md、.claude/archive/、.claude/continue-here.md、.claude/checks/ 迁移到 .diwu/（若存在）；"
            "3) 保留 .claude/CLAUDE.md、.claude/rules/、.claude/agents/、.claude/skills/ 不动；"
            "4) 刷新 .claude/rules/constraints.md 为通用版；"
            "5) 不要碰 git；"
            "6) 完成后只输出 DONE。"
        )
        result = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--add-dir",
                str(PROJECT_ROOT),
                "--permission-mode",
                "bypassPermissions",
            ],
            cwd=target,
            capture_output=True,
            text=True,
            check=True,
        )

        assert "DONE" in result.stdout

        diwu_dir = target / ".diwu"
        assert diwu_dir.exists()
        for item in [
            "task.json",
            "recording",
            "decisions.md",
            "dsettings.json",
            "project-pitfalls.md",
            "archive",
            "continue-here.md",
            "checks",
        ]:
            assert (diwu_dir / item).exists(), item

        for item in [
            "task.json",
            "recording",
            "decisions.md",
            "dsettings.json",
            "project-pitfalls.md",
            "archive",
            "continue-here.md",
            "checks",
        ]:
            assert not (target / ".claude" / item).exists(), item

        for item in ["CLAUDE.md", "rules", "agents"]:
            assert (target / ".claude" / item).exists(), item

        task_data = json.loads((diwu_dir / "task.json").read_text(encoding="utf-8"))
        assert isinstance(task_data.get("tasks"), list)
        assert list((diwu_dir / "recording").glob("session-*.md"))

        constraints = (target / ".claude" / "rules" / "constraints.md").read_text(encoding="utf-8")
        assert constraints.startswith("# 架构约束")
        assert "State Machines" not in constraints
        assert "Data Ownership" not in constraints
        assert "diwu-workflow" not in constraints
