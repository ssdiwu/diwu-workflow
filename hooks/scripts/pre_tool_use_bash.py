import json, sys, os

f = '.claude/task.json'
if not os.path.exists(f):
    sys.exit(0)

d = json.load(open(f))
t = next((x for x in d['tasks'] if x['status'] == 'InProgress'), None)

if t:
    desc = t.get('title', t.get('description', ''))
    msg = '[diwu] Task#' + str(t['id']) + ': ' + desc
    if t.get('description'):
        msg += '\n  说明: ' + t['description']
    msg += '\n' + '\n'.join('  - ' + a for a in t.get('acceptance', []))
    print(msg)
