with open('static/configure.html', 'r', encoding='utf-8') as f:
    content = f.read()

sidebar_addition = """
                if (user.role === 'unit_head') {
                    const unitHeadLink = document.createElement('a');
                    unitHeadLink.href = '/unit_head';
                    unitHeadLink.className = 'flex items-center gap-3 px-3 py-2 rounded-lg text-secondary hover:bg-surface-container hover:text-on-surface transition-colors mb-2';
                    unitHeadLink.innerHTML = '<span class="material-symbols-outlined text-[20px]">groups</span><span class="font-medium text-sm">Unit Head</span>';
                    navLinks.appendChild(unitHeadLink);
                }
"""

content = content.replace("if (user.role === 'admin') {", sidebar_addition + "                if (user.role === 'admin') {")

with open('static/configure.html', 'w', encoding='utf-8') as f:
    f.write(content)
