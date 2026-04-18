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

# --- 核心层：精简不变量提取（~55行） ---
core = """## diwu-workflow 核心不变量

### 三唯一框架
进入任务前确认：唯一主线目录、唯一运行入口、canonical（规范真相源）。未确认前不默认当前目录/旧脚本就是主线。

### 现象→判断→动作骨架
所有规则都是这条链的具体实例。违反此链的规则是空壳。
现象（看到了什么事实）→ 判断（得出什么结论，依据什么）→ 动作（下一步具体做什么，怎样验证）

### 不确定性门控
| 路径 | 条件 |
|------|------|
| 直接做 | 改动小 + 结果可预期 + 差异一句话说清 |
| 先写最小规格 | 结果不能说清 / 依赖外部 / 需稳定格式 / 需交接 |
| 先探索验证 | 外部依赖多 / 落点不清 / 回滚成本高 |

### 证据优先级摘要
L1 运行态 > L2 调用链 > L3 自动化断言 > L4 表面观察 > L5 间接推断。默认 L1-3 主判，仅 L5 不可宣称完成。
"""
content += core

# --- Skill 索引 + 参考文件速查（提醒模式，不塞内容） ---
index_items = [
    ('dtask (Skill)', '需任务管理？→ dtask skill — 状态机/GWT/task.json/提交规范'),
    ('dsess (Skill)', '需 Session 管理？→ dsess skill — 启动/结束/任务选择/continuous_mode'),
    ('dcorr (Skill)', '需纠偏？→ /dcorr 或 dcorr skill — 退化信号/四行重写/止损'),
    ('dverify (Skill)', '需验收判定？→ dverify skill — L1-L5证据/Done门槛/四问'),
    ('djudge (Skill)', '需阶段决策？→ djudge skill — 幅度判定/并行vs串行/超前实施'),
    ('drecord (Skill)', '写记录？→ drecord skill — session格式/踩坑四段式/时间戳'),
    ('rules/exceptions.md', '异常处理与 BLOCKED 判定（Read on demand）'),
    ('rules/templates.md', 'BLOCKED/REVIEW/DECISION TRACE 格式模板（Read on demand）'),
    ('rules/constraints.md', '五维约束设计方法论（Read on demand）'),
]

index_lines = ['\n## Skill 与文件索引（按需加载）', '']
for name, desc in index_items:
    index_lines.append(f'- **{name}**: {desc}')
index_lines.append('')
index_lines.append('> 规则详细内容已迁移为 Skill 按需加载，不再全量注入。需要时激活对应 Skill 或 Read 参考文件。')
content += '\n' + '\n'.join(index_lines)

print(json.dumps({'additionalSystemPrompt': content}))
