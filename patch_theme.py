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
            },
            "borderRadius": {
              "DEFAULT": "0.25rem",
              "lg": "0.5rem",
              "xl": "0.75rem",
              "full": "9999px"
            },
            "spacing": {
              "xl": "40px",
              "margin-mobile": "16px",
              "base": "4px",
              "lg": "24px",
              "md": "16px",
              "xs": "4px",
              "sm": "8px",
              "gutter": "24px",
              "margin-desktop": "48px"
            }
          }
        }
      }
    </script>
"""

TOGGLE_BTN_DESKTOP = """
                <button onclick="toggleDarkMode()" class="text-secondary hover:text-primary transition-colors p-1 rounded hover:bg-surface-container flex items-center justify-center cursor-pointer ml-2">
                    <span class="material-symbols-outlined">dark_mode</span>
                </button>
"""

def patch_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Replace <script id="tailwind-config">...
    content = re.sub(r'<script id="tailwind-config">.*?</script>', TAILWIND_CONFIG.strip(), content, flags=re.DOTALL)
    
    # 2. Add CSS_VARS right before tailwind-config or </head>
    if 'function toggleDarkMode()' not in content:
        content = re.sub(r'<style>.*?</style>', CSS_VARS.strip(), content, flags=re.DOTALL)
    
    # 3. Insert toggle button in desktop nav
    if 'dark_mode' not in content:
        content = content.replace('<button id="logout-btn"', TOGGLE_BTN_DESKTOP + '\n                <button id="logout-btn"')
        content = content.replace('<button id="logout-btn-mobile"', TOGGLE_BTN_DESKTOP + '\n                <button id="logout-btn-mobile"')
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for f in ['static/dashboard.html', 'static/configure.html']:
    patch_file(f)
