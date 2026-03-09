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

lp = os.path.join(cwd, '.claude', 'lessons.md')
lc = open(lp).read().strip() if os.path.exists(lp) else ''
if lc:
    content += '\n\n# Agent 错误模式记录\n\n' + lc

cp = os.path.join(cwd, '.claude', 'rules', 'constraints.md')
cc = open(cp).read().strip() if os.path.exists(cp) else ''
if cc:
    content += '\n\n# 架构约束\n\n' + cc

rfs = ['core-states.md', 'core-workflow.md', 'exceptions.md', 'templates.md', 'file-layout.md']
rd = os.path.join(cwd, '.claude', 'rules')
missing = not all(os.path.exists(os.path.join(rd, f)) for f in rfs)
if missing:
    content += '\n\n⚠️ 项目未初始化：.claude/rules/ 缺少规则文件。请运行 /dinit 完成项目初始化。'

print(json.dumps({'additionalSystemPrompt': content}))
