import json, sys

data = json.load(sys.stdin)
path = data.get('tool_input', {}).get('file_path', '')

try:
    with open(path) as f:
        json.loads(f.read())
except json.JSONDecodeError as e:
    print(json.dumps({
        'continue': True,
        'additionalSystemPrompt': f'[diwu] JSON 校验失败: {path}\n  {e}'
    }))
    sys.exit(1)
except FileNotFoundError:
    pass
