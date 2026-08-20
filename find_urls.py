import json
import re

with open('C:/Users/DELL/.gemini/antigravity/brain/c8ea4954-9d75-4efc-851f-a1f40f6123c1/.system_generated/logs/transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if 'tool_calls' in data:
            for tc in data['tool_calls']:
                # Also check view_file outputs
                if tc['name'] == 'default_api:view_file' and 'output' in tc.get('result', {}):
                    out = tc['result']['output']
                    if 'generate_handover_content' in out:
                        print('Found original ai.py!')
                        urls = re.findall(r'https?://[^\s\"\']+', out)
                        for u in urls:
                            print(u)
                        exit(0)
