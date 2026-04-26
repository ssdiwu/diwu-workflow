#!/bin/bash

# opencode-diwu-workflow 初始化脚本
# 用于安装依赖和验证环境

set -e

echo "=== opencode-diwu-workflow 初始化 ==="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Node.js
echo "1. 检查 Node.js"
if command -v node &> /dev/null; then
    echo -e "   ${GREEN}✓${NC} Node.js $(node --version)"
else
    echo -e "   ${RED}✗${NC} Node.js 未安装"
    echo "   请安装 Node.js: https://nodejs.org/"
    exit 1
fi

# 检查 npm
echo "2. 检查 npm"
if command -v npm &> /dev/null; then
    echo -e "   ${GREEN}✓${NC} npm $(npm --version)"
else
    echo -e "   ${RED}✗${NC} npm 未安装"
    exit 1
fi

# 检查 opencode
echo "3. 检查 opencode"
if command -v opencode &> /dev/null; then
    echo -e "   ${GREEN}✓${NC} opencode $(opencode --version)"
else
    echo -e "   ${YELLOW}⚠${NC} opencode 未安装"
    echo "   安装 opencode: brew install opencode"
fi

# 安装依赖
echo ""
echo "4. 安装依赖"
if [ -f ".opencode/package.json" ]; then
    echo "   安装 .opencode 依赖..."
    cd .opencode && npm install && cd ..
    echo -e "   ${GREEN}✓${NC} 依赖安装完成"
else
    echo -e "   ${YELLOW}⚠${NC} .opencode/package.json 不存在"
fi

# 验证配置
echo ""
echo "5. 验证配置"
if command -v opencode &> /dev/null; then
    echo "   运行 opencode debug config..."
    if opencode debug config > /dev/null 2>&1; then
        echo -e "   ${GREEN}✓${NC} opencode 配置验证通过"
    else
        echo -e "   ${RED}✗${NC} opencode 配置验证失败"
        echo "   运行 'opencode debug config' 查看错误详情"
    fi
else
    echo -e "   ${YELLOW}⚠${NC} opencode 未安装，跳过配置验证"
fi

# 运行冒烟测试
echo ""
echo "6. 运行冒烟测试"
if [ -f ".claude/checks/smoke.sh" ]; then
    echo "   运行 .claude/checks/smoke.sh..."
    if .claude/checks/smoke.sh; then
        echo -e "   ${GREEN}✓${NC} 冒烟测试通过"
    else
        echo -e "   ${RED}✗${NC} 冒烟测试失败"
    fi
else
    echo -e "   ${YELLOW}⚠${NC} .claude/checks/smoke.sh 不存在"
fi

echo ""
echo "=== 初始化完成 ==="
echo ""
echo "下一步："
echo "1. 启动 opencode: opencode"
echo "2. 测试命令: /dinit, /dtask, /dprd, /dadr, /ddoc, /ddemo"
echo "3. 查看文档: README.md, PROJECT.md"
echo ""
