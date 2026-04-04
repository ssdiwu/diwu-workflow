"""level0: JSON 语法合法性测试"""
import json
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

EXCLUDE_DIRS = {"node_modules", ".git", "archive", "__pycache__", ".pytest_cache"}


def discover_json_files(root: Path) -> list[Path]:
    """发现项目中所有 .json 文件（排除目录）"""
    return [p for p in root.rglob("*.json") if not (EXCLUDE_DIRS & set(p.parts))]


JSON_FILES = discover_json_files(PROJECT_ROOT)


@pytest.mark.parametrize("json_path", JSON_FILES)
def test_json_syntax(json_path):
    """验证单个 JSON 文件语法合法"""
    with open(json_path, encoding="utf-8") as f:
        content = f.read()
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        pytest.fail(f"JSON 语法错误 in {json_path}: {e.msg} (行 {e.lineno}, 列 {e.colno})")
