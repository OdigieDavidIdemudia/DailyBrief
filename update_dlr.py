with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('priority=blueprint.priority if blueprint else "Standard"', 'priority=blueprint.priority if blueprint else "Standard",\n                assigned_by=blueprint.assigned_by if blueprint else None')
content = content.replace('priority=blueprint.priority,\n                    # assigned_by is not here', 'priority=blueprint.priority,\n                    assigned_by=blueprint.assigned_by,\n')
content = content.replace('priority=blueprint.priority,', 'priority=blueprint.priority,\n                    assigned_by=blueprint.assigned_by,')


with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
