"""level3: 规则文档格式验证测试"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
RULES_DIR = PROJECT_ROOT / "assets" / "dinit" / "assets" / "rules"


def _get_rules_files():
    return list(RULES_DIR.glob("*.md"))


class TestRulesLineCount:
    """验收条件 4: assets/dinit/assets/rules/*.md 每个文件 ≤ 260 行"""

    MAX_LINES = 260  # workflow.md 247 行（核心规则，内容充实不精简）

    def test_rules_files_within_line_limit(self):
        """每个规则文件不超过 260 行"""
        errors = []
        for rules_file in _get_rules_files():
            line_count = len(rules_file.read_text().splitlines())
            if line_count > self.MAX_LINES:
                errors.append(f"{rules_file.name}: {line_count} 行 (限制 {self.MAX_LINES})")
        assert not errors, "\n".join(errors)


class TestRulesConstraintLevel:
    """验收条件 5: assets/dinit/assets/rules/*.md 每个文件开头包含规则约束级别说明"""

    def test_has_constraint_level说明(self):
        """文件开头（前 50 行内）包含规则约束级别说明"""
        errors = []
        for rules_file in _get_rules_files():
            lines = rules_file.read_text().splitlines()
            # 规则文件格式：大多数在第 3 行有 "> **规则约束级别说明**："
            # README.md 在第 30 行有 "## 规则约束级别"
            # 检查前 50 行应该能覆盖所有合规情况
            head = "\n".join(lines[:50])

            # 检查是否有 "规则约束级别说明" 或 "## 规则约束级别" 等模式
            patterns = [
                r"规则约束级别说明",  # judgments.md 格式
                r"##\s*规则约束级别",  # README.md 格式
            ]
            if not any(re.search(p, head) for p in patterns):
                errors.append(f"{rules_file.name}: 前 50 行内未找到规则约束级别说明")
        assert not errors, "\n".join(errors)
