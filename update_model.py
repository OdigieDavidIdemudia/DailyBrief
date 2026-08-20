with open('app/ai.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('gemini-1.5-flash', 'gemini-3.6-flash')
content = content.replace('gemini-2.5-flash', 'gemini-3.6-flash')

with open('app/ai.py', 'w', encoding='utf-8') as f:
    f.write(content)
