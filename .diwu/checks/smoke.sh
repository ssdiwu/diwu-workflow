#!/bin/bash

# opencode-diwu-workflow 冒烟测试
# 用于验证项目配置和基本功能

set -e

echo "=== opencode-diwu-workflow 冒烟测试 ==="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果
PASSED=0
FAILED=0

# 测试函数
test_check() {
    local name=$1
    local command=$2
    
    echo -n "测试 $name ... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ 失败${NC}"
        ((FAILED++))
    fi
}

echo "1. 检查配置文件"
test_check "opencode.json 存在" "test -f opencode.json"
test_check "AGENTS.md 存在" "test -f AGENTS.md"
test_check "README.md 存在" "test -f README.md"

echo ""
echo "2. 检查 .opencode 目录结构"
test_check ".opencode 目录存在" "test -d .opencode"
test_check ".opencode/agents 目录存在" "test -d .opencode/agents"
test_check ".opencode/commands 目录存在" "test -d .opencode/commands"
test_check ".opencode/plugins 目录存在" "test -d .opencode/plugins"
test_check ".opencode/references 目录存在" "test -d .opencode/references"
test_check ".opencode/skills 目录存在" "test -d .opencode/skills"

echo ""
echo "3. 检查关键文件"
test_check "diwu-workflow.ts 存在" "test -f .opencode/plugins/diwu-workflow.ts"
test_check "dinit.md 存在" "test -f .opencode/commands/dinit.md"
test_check "dtask.md 存在" "test -f .opencode/commands/dtask.md"
test_check "dprd.md 存在" "test -f .opencode/commands/dprd.md"
test_check "dadr.md 存在" "test -f .opencode/commands/dadr.md"
test_check "ddoc.md 存在" "test -f .opencode/commands/ddoc.md"
test_check "ddemo.md 存在" "test -f .opencode/commands/ddemo.md"

echo ""
echo "4. 检查 Skills"
test_check "ddoc SKILL.md 存在" "test -f .opencode/skills/ddoc/SKILL.md"
test_check "dprd SKILL.md 存在" "test -f .opencode/skills/dprd/SKILL.md"
test_check "ddemo SKILL.md 存在" "test -f .opencode/skills/ddemo/SKILL.md"

echo ""
echo "5. 检查 Agents"
test_check "build.md 存在" "test -f .opencode/agents/build.md"
test_check "plan.md 存在" "test -f .opencode/agents/plan.md"
test_check "diwu-expert.md 存在" "test -f .opencode/agents/diwu-expert.md"

echo ""
echo "6. 检查 References"
test_check "constraints.md 存在" "test -f .opencode/references/constraints.md"
test_check "states.md 存在" "test -f .opencode/references/states.md"
test_check "workflow.md 存在" "test -f .opencode/references/workflow.md"
test_check "judgments.md 存在" "test -f .opencode/references/judgments.md"
test_check "templates.md 存在" "test -f .opencode/references/templates.md"
test_check "exceptions.md 存在" "test -f .opencode/references/exceptions.md"
test_check "file-layout.md 存在" "test -f .opencode/references/file-layout.md"

echo ""
echo "7. 检查 Claude Code 兼容文件"
test_check ".claude/CLAUDE.md 存在" "test -f .claude/CLAUDE.md"
test_check ".claude/task.json 存在" "test -f .claude/task.json"
test_check ".claude/settings.json 存在" "test -f .claude/settings.json"
test_check ".claude/lessons.md 存在" "test -f .claude/lessons.md"
test_check ".claude/decisions.md 存在" "test -f .claude/decisions.md"
test_check ".claude/recording 目录存在" "test -d .claude/recording"
test_check ".claude/checks 目录存在" "test -d .claude/checks"

echo ""
echo "8. 检查 JSON 语法"
test_check "opencode.json 语法正确" "python3 -m json.tool opencode.json"
test_check ".claude/task.json 语法正确" "python3 -m json.tool .claude/task.json"
test_check ".claude/settings.json 语法正确" "python3 -m json.tool .claude/settings.json"

echo ""
echo "9. 检查 opencode 配置"
if command -v opencode &> /dev/null; then
    test_check "opencode debug config 成功" "opencode debug config"
    test_check "opencode debug skill 成功" "opencode debug skill"
else
    echo -e "${YELLOW}⚠ opencode 未安装，跳过配置检查${NC}"
fi

echo ""
echo "=== 测试结果 ==="
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 有 $FAILED 个测试失败${NC}"
    exit 1
fi
