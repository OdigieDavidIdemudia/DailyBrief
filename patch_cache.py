import os

files_to_patch = ['static/configure.html', 'static/dashboard.html', 'static/unit_head.html']

for file_path in files_to_patch:
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    new_text = text.replace("fetch('/api/blueprints')", "fetch('/api/blueprints?_t=' + new Date().getTime(), { cache: 'no-store' })")
    new_text = new_text.replace("fetch('/api/auth/me')", "fetch('/api/auth/me?_t=' + new Date().getTime(), { cache: 'no-store' })")
    new_text = new_text.replace("fetch('/api/settings/telegram')", "fetch('/api/settings/telegram?_t=' + new Date().getTime(), { cache: 'no-store' })")
    new_text = new_text.replace("fetch('/api/unit/tasks')", "fetch('/api/unit/tasks?_t=' + new Date().getTime(), { cache: 'no-store' })")
    new_text = new_text.replace("fetch(`/api/unit/tasks?user_id=${userId}`)", "fetch(`/api/unit/tasks?user_id=${userId}&_t=` + new Date().getTime(), { cache: 'no-store' })")
    new_text = new_text.replace("fetch('/api/unit/members')", "fetch('/api/unit/members?_t=' + new Date().getTime(), { cache: 'no-store' })")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
        
print('Patched successfully!')
