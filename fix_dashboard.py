import sys

with open('static/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = "const todayStr = new Date().toISOString().split('T')[0];"
replacement = target + "\n                const durationText = document.getElementById('handover-duration') ? document.getElementById('handover-duration').value.trim() : \"\";"

if target in html:
    html = html.replace(target, replacement)
    with open('static/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed.")
else:
    print("Target not found.")
