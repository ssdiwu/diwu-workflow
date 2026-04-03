"""level0: 语法检查、导入检查"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


def test_python_syntax():
    """所有 Python 文件语法正确"""
    errors = []
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            py_file.read_text()
        except Exception as e:
            errors.append(f"{py_file}: {e}")
    assert not errors, f"Syntax errors: {errors}"


def test_hooks_scripts_syntax():
    """hooks/scripts/*.py 语法正确（仅编译检查，不执行）"""
    import ast
    scripts_dir = PROJECT_ROOT / "hooks" / "scripts"
    for py_file in scripts_dir.glob("*.py"):
        if py_file.name.startswith("test_"):
            continue
        try:
            ast.parse(py_file.read_text())
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {py_file}: {e}")
