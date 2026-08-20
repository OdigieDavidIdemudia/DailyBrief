import os
import re

def patch_on_primary(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add --color-on-primary to :root
    content = re.sub(r'(--color-primary: #1e35d0;)', r'\1\n          --color-on-primary: #ffffff;', content)
    
    # Add --color-on-primary to .dark
    content = re.sub(r'(--color-primary: #aac7ff;)', r'\1\n          --color-on-primary: #0b1c30;', content)
    
    # Add on-primary to tailwind-config
    content = re.sub(r'("primary": "var\(--color-primary\)",)', r'\1\n              "on-primary": "var(--color-on-primary)",', content)

    # Replace bg-primary text-white with bg-primary text-on-primary
    content = content.replace('bg-primary text-white', 'bg-primary text-on-primary')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

files = ['static/dashboard.html', 'static/login.html', 'static/configure.html']
for f in files:
    patch_on_primary(f)
