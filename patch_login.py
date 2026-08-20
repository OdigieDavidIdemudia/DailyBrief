import os
import re

CSS_VARS = """
    <style>
        :root {
          --color-primary: #1e35d0;
          --color-background: #f8f9ff;
          --color-on-surface: #0b1c30;
          --color-secondary: #5b5f64;
          --color-surface-container-lowest: #ffffff;
          --color-surface-container-low: #eff4ff;
          --color-surface-container: #e5eeff;
          --color-surface-container-high: #dce9ff;
          --color-surface-container-highest: #d3e4fe;
          --color-surface-bright: #f8f9ff;
          --color-outline-variant: #c5c5d8;
          --color-error: #ba1a1a;
        }
        .dark {
          --color-primary: #aac7ff;
          --color-background: #0b1c30;
          --color-on-surface: #e2e2e9;
          --color-secondary: #c4c6d0;
          --color-surface-container-lowest: #0f141f;
          --color-surface-container-low: #1a202c;
          --color-surface-container: #212936;
          --color-surface-container-high: #2a3441;
          --color-surface-container-highest: #333f4f;
          --color-surface-bright: #374151;
          --color-outline-variant: #44474e;
          --color-error: #ffb4ab;
        }
        body { font-family: 'Inter', sans-serif; }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
    </style>
    <script>
        if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        function toggleDarkMode() {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        }
    </script>
"""

TAILWIND_CONFIG = """
    <script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
              "primary": "var(--color-primary)",
              "background": "var(--color-background)",
              "on-surface": "var(--color-on-surface)",
              "secondary": "var(--color-secondary)",
              "surface-container-lowest": "var(--color-surface-container-lowest)",
              "surface-container-low": "var(--color-surface-container-low)",
              "surface-container": "var(--color-surface-container)",
              "surface-container-high": "var(--color-surface-container-high)",
              "surface-container-highest": "var(--color-surface-container-highest)",
              "surface-bright": "var(--color-surface-bright)",
              "outline-variant": "var(--color-outline-variant)",
              "error": "var(--color-error)"
            }
          }
        }
      }
    </script>
"""

filepath = 'static/login.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace hardcoded colors with tailwind semantic classes
content = content.replace('bg-[#f8f9ff]', 'bg-background')
content = content.replace('bg-white', 'bg-surface-container-lowest')
content = content.replace('text-[#0b1c30]', 'text-on-surface')
content = content.replace('border-[#c5c5d8]', 'border-outline-variant')
content = content.replace('text-[#5b5f64]', 'text-secondary')
content = content.replace('bg-[#1e35d0]', 'bg-primary')
content = content.replace('bg-[#e5eeff]', 'bg-surface-container')
content = content.replace('text-[#1e35d0]', 'text-primary')

# Focus states
content = content.replace('focus:ring-[#1e35d0]/20', 'focus:ring-primary/20')
content = content.replace('focus:border-[#1e35d0]', 'focus:border-primary')
content = content.replace('placeholder:text-[#5b5f64]/40', 'placeholder:text-secondary/40')
content = content.replace('text-[#1e35d0]/70', 'text-primary/70')

# Replace <style> block
content = re.sub(r'<style>.*?</style>', CSS_VARS.strip() + '\\n' + TAILWIND_CONFIG.strip(), content, flags=re.DOTALL)

# Insert toggle button
if 'dark_mode' not in content:
    toggle_html = '''
    <!-- Dark Mode Toggle -->
    <div class="fixed top-4 right-4 z-50">
        <button onclick="toggleDarkMode()" class="text-secondary hover:text-primary transition-colors p-2 rounded-full bg-surface-container-lowest shadow-md flex items-center justify-center cursor-pointer">
            <span class="material-symbols-outlined">dark_mode</span>
        </button>
    </div>
    '''
    content = content.replace('<body class="', '<body class="')
    content = re.sub(r'(<body.*?>)', r'\\1' + '\\n' + toggle_html, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

