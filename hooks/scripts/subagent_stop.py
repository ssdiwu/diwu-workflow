import json, sys, os, subprocess

d = json.load(sys.stdin)
sid = d.get('session_id', '')
main = open('/tmp/.claude_main_session').read().strip() if os.path.exists('/tmp/.claude_main_session') else ''

if sid != main or not sid:
    sys.exit(0)

tf = '.diwu/dtask.json'
if not os.path.exists(tf):
    sys.exit(0)

tasks = json.load(open(tf)).get('tasks', [])
t = next((x for x in tasks if x['status'] == 'InProgress'), None)

if not t:
    sys.exit(0)

now = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()
prompt = (
    '子代理已完成，请立即将当前进度写入 recording/ 目录的新 session 文件。'
    '时间戳直接使用：' + now + '（禁止伪造）。'
    '任务：Task#' + str(t['id']) + ' ' + t.get('title', t.get('description', '')) + '。'
    '任务描述：' + t.get('description', '') + '。'
    '格式遵循 templates.md Session 格式。只写 recording/ 目录，完成后停止。'
)
print(json.dumps({'continue': True, 'additionalSystemPrompt': prompt}))
