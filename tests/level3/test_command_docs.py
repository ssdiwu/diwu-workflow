"""level3: 命令文档格式验证测试"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
COMMANDS_DIR = PROJECT_ROOT / "commands"


def _get_command_files():
    return list(COMMANDS_DIR.glob("*.md"))


class TestCommandFrontmatter:
    """验收条件 1: commands/*.md 每个文件包含 YAML frontmatter 且有 description 字段"""

    def test_all_command_files_have_frontmatter(self):
        """所有命令文件包含 YAML frontmatter"""
        errors = []
        for cmd_file in _get_command_files():
            content = cmd_file.read_text()
            # 检查是否有 --- 包围的 frontmatter
            if not re.match(r"^---\n", content, re.MULTILINE):
                errors.append(f"{cmd_file.name}: 缺少 YAML frontmatter (--- 开头)")
            elif content.count("---") < 2:
                errors.append(f"{cmd_file.name}: YAML frontmatter 未正确闭合")
        assert not errors, "\n".join(errors)

    def test_frontmatter_has_description(self):
        """每个 frontmatter 包含 description 字段"""
        errors = []
        for cmd_file in _get_command_files():
            content = cmd_file.read_text()
            # 提取 frontmatter（第一个 --- 到第二个 --- 之间的内容）
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)
            if not match:
                errors.append(f"{cmd_file.name}: 无法解析 frontmatter")
                continue
            frontmatter = match.group(1)
            if not re.search(r"^description:", frontmatter, re.MULTILINE):
                errors.append(f"{cmd_file.name}: frontmatter 缺少 description 字段")
        assert not errors, "\n".join(errors)


class TestCommandNoExecutableCode:
    """验收条件 2: commands/*.md 不包含可执行代码块"""

    def test_no_executable_code_blocks(self):
        """检测未标注示例的可执行代码块 (python/node/bash)"""
        errors = []
        for cmd_file in _get_command_files():
            content = cmd_file.read_text()
            lines = content.split("\n")

            in_code_block = False
            code_block_start = 0
            code_block_lang = ""

            for i, line in enumerate(lines, 1):
                if line.strip().startswith("```"):
                    if not in_code_block:
                        # 代码块开始
                        in_code_block = True
                        code_block_start = i
                        code_block_lang = line.strip()[3:].lower()
                    else:
                        # 代码块结束
                        in_code_block = False
                        code_block_lang = ""
                elif in_code_block:
                    # 在代码块内，检查是否有 python/node/bash 等但未标注示例
                    # 只有非空行才检查
                    stripped = line.strip()
                    if stripped and code_block_lang in ("python", "node", "bash", "sh", "shell", "zsh"):
                        # 检查前一行或当前行是否有 "示例" 字样（允许的）
                        prev_line = lines[code_block_start - 1] if code_block_start > 0 else ""
                        # 如果代码块语言本身不是示例，且当前行不是空行（注释或空白）
                        if "示例" not in prev_line and "example" not in prev_line.lower():
                            errors.append(
                                f"{cmd_file.name}:{i}: 代码块可能为可执行代码 (语言={code_block_lang})"
                            )
                            break  # 每个文件只报一个错
        assert not errors, "\n".join(errors)


class TestCommandNoOldReferences:
    """验收条件 3: commands/*.md 无遗留旧引用"""

    def test_no_core_states_or_workflow_refs(self):
        """搜索 core-states.md 或 core-workflow.md 应为 0 命中"""
        old_refs = ["core-states.md", "core-workflow.md"]
        errors = []

        for cmd_file in _get_command_files():
            content = cmd_file.read_text()
            for ref in old_refs:
                if ref in content:
                    errors.append(f"{cmd_file.name}: 包含旧引用 {ref}")
        assert not errors, "\n".join(errors)
