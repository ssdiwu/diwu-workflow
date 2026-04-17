import json, sys, os

home = os.path.expanduser('~')
ip = os.path.join(home, '.claude', 'plugins', 'installed_plugins.json')
pdata = json.load(open(ip)) if os.path.exists(ip) else {}
entries = pdata.get('plugins', {}).get('diwu-workflow@ssdiwu', [])
root = (entries[0].get('installPath', '') if entries else '') or os.environ.get('CLAUDE_PLUGIN_ROOT', '')

if not root:
    sys.exit(0)

d = json.load(sys.stdin)
content = ''
cwd = d.get('cwd', '.')

# --- 独立注入层：全量加载的高优先级文件 ---

# mindset.md — 上位心智层（独立注入，控制 token 并支持按需加载）
mp = os.path.join(cwd, '.claude', 'rules', 'mindset.md')
mc = open(mp).read().strip() if os.path.exists(mp) else ''
if mc:
    content += '\n\n# 上位心智层\n\n' + mc

# --- rfs 批量注入层：精简索引模式（仅注入速查摘要，不全量加载） ---
# mindset.md 已在上方独立注入，此处不重复
rfs = [
    ('README.md', '规则速查索引'),
    ('constraints.md', '架构约束（五维约束设计）'),
    ('judgments.md', '判断锚点（四段式：启动/实施/验收/纠偏）'),
    ('task.md', '任务状态机、acceptance 格式、task.json 结构'),
    ('workflow.md', '任务规划、实施、验证'),
    ('session.md', 'Session 生命周期管理'),
    ('verification.md', '证据优先级体系（L1-L5）'),
    ('correction.md', '纠偏体系（退化信号→止损动作）'),
    ('pitfalls.md', '误判防护（三层：泛化/项目/接口）'),
    ('exceptions.md', '异常处理与 BLOCKED 判定'),
    ('templates.md', '格式模板与可调参数'),
    ('file-layout.md', '.claude/ 目录结构与归档规则'),
]
rd = os.path.join(cwd, '.claude', 'rules')

# 检查 rfs 文件是否存在
existing_rfs = [(name, desc) for name, desc in rfs if os.path.exists(os.path.join(rd, name))]
missing_rfs = [name for name, _ in rfs if not os.path.exists(os.path.join(rd, name))]

if existing_rfs:
    index_lines = ['# 规则文件速查索引', '']
    for name, desc in existing_rfs:
        index_lines.append(f'- **{name}**: {desc}')
    index_lines.append('')
    index_lines.append('> 详细内容请按需查阅 .claude/rules/ 下对应文件。')
    content += '\n\n' + '\n'.join(index_lines)

if missing_rfs:
    content += '\n\n⚠️ 项目未初始化：.claude/rules/ 缺少以下规则文件：' + ', '.join(missing_rfs) + '。请运行 /dinit 完成项目初始化。'

print(json.dumps({'additionalSystemPrompt': content}))
