import json, sys

data = json.load(sys.stdin)
path = data.get('tool_input', {}).get('file_path', '')

if not path.endswith('.json'):
    sys.exit(0)

try:
    with open(path) as f:
        json.loads(f.read())
except json.JSONDecodeError as e:
    print(f'[diwu] JSON 校验失败: {path}\n  {e}')
except FileNotFoundError:
    pass
