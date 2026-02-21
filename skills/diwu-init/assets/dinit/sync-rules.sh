#!/bin/bash
set -e
cp ~/.claude/rules/*.md assets/rules/
git add assets/rules/
git diff --cached --quiet && echo "No changes." && exit 0
git commit -m "sync rules from ~/.claude/rules"
git push
