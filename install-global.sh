#!/bin/bash
set -e

# ============================================================
# diwu-workflow 全局安装/更新脚本
# ============================================================
# 用法:
#   ./install-global.sh              # 安装/更新到全局
#   ./install-global.sh /path/to/project  # 安装/更新到指定项目
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_PLUGIN="$SCRIPT_DIR/.opencode/plugins/diwu-workflow.ts"
SOURCE_TEMPLATE="$SCRIPT_DIR/.opencode"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 目标目录
if [ -n "$1" ]; then
    TARGET_DIR="$1"
    MODE="project"
    echo -e "${YELLOW}▶ 项目级安装模式: $TARGET_DIR${NC}"
else
    TARGET_DIR="$HOME/.config/opencode"
    MODE="global"
    echo -e "${YELLOW}▶ 全局安装模式${NC}"
fi

# 检查源文件
if [ ! -f "$SOURCE_PLUGIN" ]; then
    echo -e "${RED}✗ 错误: 未找到 plugin 源文件${NC}"
    exit 1
fi

# 创建目标目录
mkdir -p "$TARGET_DIR/plugins"

# 1. 复制 plugin 文件
echo ""
echo "[1/3] 同步 Plugin 文件..."
cp "$SOURCE_PLUGIN" "$TARGET_DIR/plugins/diwu-workflow.ts"
echo -e "${GREEN}  ✓${NC} plugin → $TARGET_DIR/plugins/"

# 2. 复制模板
echo ""
echo "[2/3] 同步模板文件..."

if [ "$MODE" = "global" ]; then
    TARGET_TEMPLATE="$TARGET_DIR/diwu-workflow"
    mkdir -p "$TARGET_TEMPLATE"
    for dir in commands skills agents references; do
        if [ -d "$SOURCE_TEMPLATE/$dir" ]; then
            mkdir -p "$TARGET_TEMPLATE/$dir"
            cp -r "$SOURCE_TEMPLATE/$dir"/* "$TARGET_TEMPLATE/$dir/"
            count=$(find "$TARGET_TEMPLATE/$dir" -type f | wc -l | tr -d ' ')
            echo -e "${GREEN}  ✓${NC} $dir/ ($count 个文件)"
        fi
    done
else
    TARGET_OPENCODE="$TARGET_DIR/.opencode"
    mkdir -p "$TARGET_OPENCODE"
    for dir in commands skills agents references; do
        if [ -d "$SOURCE_TEMPLATE/$dir" ]; then
            mkdir -p "$TARGET_OPENCODE/$dir"
            cp -r "$SOURCE_TEMPLATE/$dir"/* "$TARGET_OPENCODE/$dir/"
            count=$(find "$TARGET_OPENCODE/$dir" -type f | wc -l | tr -d ' ')
            echo -e "${GREEN}  ✓${NC} .opencode/$dir/ ($count 个文件)"
        fi
    done
    
    # 创建 .diwu/
    echo ""
    echo "[2.5/3] 创建 .diwu/ 运行时目录..."
    mkdir -p "$TARGET_DIR/.diwu"/{checks,recording,archive}
    [ ! -f "$TARGET_DIR/.diwu/dtask.json" ] && echo '{"tasks": []}' > "$TARGET_DIR/.diwu/dtask.json"
    [ ! -f "$TARGET_DIR/.diwu/dsettings.json" ] && echo '{"review_limit":5,"task_archive_threshold":20}' > "$TARGET_DIR/.diwu/dsettings.json"
    [ ! -f "$TARGET_DIR/.diwu/decisions.md" ] && echo "# 决策记录" > "$TARGET_DIR/.diwu/decisions.md"
    [ ! -f "$TARGET_DIR/.diwu/lessons.md" ] && echo "# 踩坑经验" > "$TARGET_DIR/.diwu/lessons.md"
    echo -e "${GREEN}  ✓${NC} .diwu/ 已创建"
fi

# 3. 更新 opencode.json
echo ""
echo "[3/3] 更新 opencode.json..."

CONFIG_FILE="$TARGET_DIR/opencode.json"
[ ! -f "$CONFIG_FILE" ] && echo '{"$schema": "https://opencode.ai/config.json"}' > "$CONFIG_FILE"

# 用 Node.js 修改 JSON（opencode 环境一定有 Node/Bun）
node -e "
const fs = require('fs');
const path = '$CONFIG_FILE';
let config = JSON.parse(fs.readFileSync(path, 'utf8'));

if ('$MODE' === 'project') {
    // instructions
    config.instructions = config.instructions || [];
    if (!Array.isArray(config.instructions)) config.instructions = [config.instructions];
    ['AGENTS.md', '.opencode/references/*.md', '.opencode/skills/*/SKILL.md'].forEach(i => {
        if (!config.instructions.includes(i)) config.instructions.push(i);
    });
    
    // agents
    config.agent = config.agent || {};
    const agents = {
        build: { mode: 'primary', description: '全权限实施模式', permission: { edit: 'allow', bash: 'allow' } },
        plan: { mode: 'primary', description: '受限规划模式', permission: { edit: 'ask', bash: 'ask' } },
        'diwu-expert': { mode: 'subagent', description: '工作流专家', permission: { edit: 'deny', bash: 'ask' } },
        verifier: { mode: 'subagent', description: '验收验证专家', permission: { edit: 'deny', bash: 'ask' } },
        'ui-designer': { mode: 'subagent', description: 'UI/UX专家', permission: { edit: 'deny', bash: 'ask' } },
        'backend-architect': { mode: 'subagent', description: '后端架构专家', permission: { edit: 'deny', bash: 'ask' } },
        'frontend-architect': { mode: 'subagent', description: '前端架构专家', permission: { edit: 'deny', bash: 'ask' } },
        'api-tester': { mode: 'subagent', description: '测试策略专家', permission: { edit: 'deny', bash: 'ask' } },
        'devops-architect': { mode: 'subagent', description: '运维部署专家', permission: { edit: 'deny', bash: 'ask' } },
        'performance-optimizer': { mode: 'subagent', description: '性能优化专家', permission: { edit: 'deny', bash: 'ask' } },
        'legal-compliance': { mode: 'subagent', description: '法规合规专家', permission: { edit: 'deny', bash: 'ask' } }
    };
    Object.entries(agents).forEach(([k, v]) => { if (!config.agent[k]) config.agent[k] = v; });
    
    // commands
    config.command = config.command || {};
    const cmds = {
        dinit: { template: '初始化 diwu-workflow', description: '创建 AGENTS.md、.diwu/ 等完整工作流结构' },
        dtask: { template: '任务规划', description: '将功能描述转化为 dtask.json 任务列表' },
        dprd: { template: '产品需求文档', description: '生成 PRD' },
        dadr: { template: '架构决策记录', description: '记录 ADR' },
        ddoc: { template: '产品文档', description: '正向和逆向两种模式' },
        ddemo: { template: 'Demo 能力规格', description: '不确定性隔离验证' },
        dcorr: { template: '纠偏恢复协议', description: '回到目标/主线/现象/验证锚点' },
        drec: { template: 'Session 记录', description: '快速记录踩坑经验或生成 recording 草稿' },
        dsess: { template: 'Session 启动', description: '手动触发 Session 启动流程' },
        djug: { template: '判断决策', description: '阶段边界决策锚点' },
        dvfy: { template: '验证规则', description: '验证证据优先级和 Done 判定' },
        darc: { template: '归档管理', description: 'Task 和 Recording 双轨归档' }
    };
    Object.entries(cmds).forEach(([k, v]) => { if (!config.command[k]) config.command[k] = v; });
}

fs.writeFileSync(path, JSON.stringify(config, null, 2));
console.log('  ✓ opencode.json 已更新');
"

# 完成
echo ""
echo -e "${GREEN}========================================${NC}"
if [ "$MODE" = "global" ]; then
    echo -e "${GREEN}✓ 全局安装/更新完成${NC}"
    echo ""
    echo "新项目初始化:"
    echo "  cd /path/to/project && opencode"
    echo "  # 对 AI 说: 运行 diwu_init"
else
    echo -e "${GREEN}✓ 项目级安装/更新完成${NC}"
    echo "  项目: $TARGET_DIR"
    echo "  启动: cd $TARGET_DIR && opencode"
fi
echo -e "${GREEN}========================================${NC}"
