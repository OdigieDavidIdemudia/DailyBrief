import os

filepath = 'static/unit_head.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the raw admin link with the hidden container version + unit head link
old_admin_link = '''            <a href="/admin" class="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 text-primary font-medium border-l-4 border-primary">
                <span class="material-symbols-outlined">admin_panel_settings</span>
                Admin Panel
            </a>'''

new_admin_link = '''            <div id="admin-link-container" class="hidden">
                <a href="/admin" class="flex items-center gap-3 px-3 py-2 rounded-lg text-secondary hover:bg-surface-container transition-colors border-l-4 border-transparent">
                    <span class="material-symbols-outlined">admin_panel_settings</span>
                    Admin Panel
                </a>
            </div>
            <div id="unit-head-link-container" class="hidden">
                <a href="/unit_head" class="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 text-primary font-medium border-l-4 border-primary">
                    <span class="material-symbols-outlined">supervisor_account</span>
                    Unit Head
                </a>
            </div>'''

if old_admin_link in content:
    content = content.replace(old_admin_link, new_admin_link)
    print('Replaced links in unit_head.html')
else:
    print('Could not find old_admin_link in unit_head.html')

# Also add the JS logic to unhide them
js_add = '''
                if (userData.user.role === 'admin') {
                    const adminLink = document.getElementById('admin-link-container');
                    if (adminLink) adminLink.classList.remove('hidden');
                }
                if (userData.user.role === 'unit_head' || userData.user.role === 'admin') {
                    const uhLink = document.getElementById('unit-head-link-container');
                    if (uhLink) uhLink.classList.remove('hidden');
                }'''

if 'admin-link-container' not in content[content.find("userData.user.role !== 'unit_head'"):content.find("userData.user.role !== 'unit_head'")+300]:
    old_js = '''                if (userData.user.role !== 'unit_head' && userData.user.role !== 'admin') {
                    alert("Unauthorized access. Redirecting to dashboard.");
                    window.location.href = '/dashboard';
                    return;
                }'''
    content = content.replace(old_js, old_js + js_add)
    print('Replaced JS in unit_head.html')
else:
    print('JS already present in unit_head.html')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
