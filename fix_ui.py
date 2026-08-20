import os

with open('static/downtime.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix date and time pickers
content = content.replace('id="f-start_date" class="w-full border border-outline-variant rounded-md p-2 text-sm" placeholder="e.g. 05-07-2026"', 'type="date" id="f-start_date" class="w-full border border-outline-variant rounded-md p-2 text-sm"')
content = content.replace('id="f-start_time" class="w-full border border-outline-variant rounded-md p-2 text-sm" placeholder="e.g. 14:00"', 'type="time" id="f-start_time" class="w-full border border-outline-variant rounded-md p-2 text-sm"')
content = content.replace('id="f-end_date" class="w-full border border-outline-variant rounded-md p-2 text-sm" placeholder="e.g. 05-07-2026"', 'type="date" id="f-end_date" class="w-full border border-outline-variant rounded-md p-2 text-sm"')
content = content.replace('id="f-end_time" class="w-full border border-outline-variant rounded-md p-2 text-sm" placeholder="e.g. 15:30"', 'type="time" id="f-end_time" class="w-full border border-outline-variant rounded-md p-2 text-sm"')

# Also replace if they already had type="text"
content = content.replace('type="text" id="f-start_date"', 'type="date" id="f-start_date"')
content = content.replace('type="text" id="f-start_time"', 'type="time" id="f-start_time"')
content = content.replace('type="text" id="f-end_date"', 'type="date" id="f-end_date"')
content = content.replace('type="text" id="f-end_time"', 'type="time" id="f-end_time"')

# 2. Fix Javascript crash for reported_by
content = content.replace("reported_by: (document.getElementById('user-name') || document.querySelector('.user-name')).textContent,", "reported_by: window.username || 'Idemudia',")
# Ensure username is stored globally
content = content.replace("username = emailStr.split('@')[0];", "window.username = emailStr.split('@')[0];")

with open('static/downtime.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 3. Fix app/downtime_report.py PermissionError on Vercel
with open('app/downtime_report.py', 'r', encoding='utf-8') as f:
    rep_content = f.read()

rep_content = rep_content.replace('out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "reports"))', 'out_dir = "/tmp"')
with open('app/downtime_report.py', 'w', encoding='utf-8') as f:
    f.write(rep_content)

print("Fixes applied.")
