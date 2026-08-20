import os, glob

for filepath in glob.glob('static/*.html'):
    if filepath in ['static/login.html', 'static/change_password.html']:
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add Unit Head Link if not present
    if 'id="unit-head-link-container"' not in content:
        admin_link_pos = content.find('<div id="admin-link-container"')
        if admin_link_pos != -1:
            unit_head_html = '''<div id="unit-head-link-container" class="hidden">
                <a href="/unit_head" class="flex items-center gap-3 px-3 py-2 rounded-lg text-secondary hover:bg-surface-container transition-colors border-l-4 border-transparent">
                    <span class="material-symbols-outlined">supervisor_account</span>
                    Unit Head
                </a>
            </div>'''
            content = content[:admin_link_pos] + unit_head_html + '\n            ' + content[admin_link_pos:]
    
    # Add logic to unhide unit head link
    if "if (userData.user.role === 'admin') {" in content and "unit-head-link-container" not in content[content.find("userData.user.role === 'admin'"):content.find("userData.user.role === 'admin'")+300]:
        old_block = """if (userData.user.role === 'admin') {
                        const adminLink = document.getElementById('admin-link-container');
                        if (adminLink) adminLink.classList.remove('hidden');
                    }"""
        new_block = """if (userData.user.role === 'admin') {
                        const adminLink = document.getElementById('admin-link-container');
                        if (adminLink) adminLink.classList.remove('hidden');
                    }
                    if (userData.user.role === 'unit_head' || userData.user.role === 'admin') {
                        const uhLink = document.getElementById('unit-head-link-container');
                        if (uhLink) uhLink.classList.remove('hidden');
                    }"""
        content = content.replace(old_block, new_block)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated {filepath}')
