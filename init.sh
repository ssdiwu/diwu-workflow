#!/bin/bash
set -e

echo "正在初始化 diwu-workflow..."

# 无 npm 依赖，跳过安装步骤
echo "纯 Markdown/JSON 项目，无需安装依赖。"

# 验证关键文件存在
echo "检查关键文件..."
for f in ".claude-plugin/plugin.json" ".claude-plugin/marketplace.json" "hooks/hooks.json"; do
    if [ -f "$f" ]; then
        echo "  ✓ $f"
    else
        echo "  ✗ $f 缺失" && exit 1
    fi
done

echo "环境已就绪。"
