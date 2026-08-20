with open('static/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Sidebar
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

# 2. Update renderBlueprints
# In renderBlueprints, there's a part where it builds the HTML for a blueprint.
# Let's find it.
replace_target = '<div class="flex items-center gap-2">'
# We want to add an assigned_by badge
assigned_by_html = """<div class="flex items-center gap-2">
                        ${bp.assigned_by ? `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200" title="Assigned by Unit Head"><span class="material-symbols-outlined text-[14px] mr-1">assignment_ind</span>Assigned</span>` : ''}"""

content = content.replace(replace_target, assigned_by_html)

with open('static/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
