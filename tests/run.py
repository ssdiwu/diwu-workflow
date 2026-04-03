#!/usr/bin/env python3
"""分层测试 runner：支持 --layer 0|1|2|3|4|all"""
import argparse, subprocess, sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent.resolve()
LAYERS = ["level0", "level1", "level2", "level3", "level4"]


def run_tests(layers):
    if "all" in layers:
        targets = [str(TESTS_DIR / l) for l in LAYERS]
    else:
        targets = [str(TESTS_DIR / f"level{l}") for l in layers]

    if not targets:
        print("No valid layers specified", file=sys.stderr)
        sys.exit(1)

    cmd = ["python3", "-m", "pytest", "-v"] + targets
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="diwu-workflow 分层测试 runner")
    parser.add_argument("--layer", "-l", action="append", default=[],
                        choices=["0","1","2","3","4","all"],
                        help="指定运行层级（可多次使用）")
    args = parser.parse_args()

    if not args.layer:
        args.layer = ["all"]

    run_tests(args.layer)


if __name__ == "__main__":
    main()
