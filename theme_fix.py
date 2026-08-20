with open('static/downtime.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'bg-white': 'bg-surface',
    'bg-gray-50': 'bg-background',
    'text-gray-800': 'text-on-surface',
    'text-gray-500': 'text-secondary',
    'border-r': 'border-r border-outline-variant',
    'border-b': 'border-b border-outline-variant',
    'border-t': 'border-t border-outline-variant',
    'border ': 'border border-outline-variant ',
    'bg-indigo-100': 'bg-primary/20',
    'text-indigo-600': 'text-primary',
    'bg-indigo-600': 'bg-primary',
    'hover:bg-indigo-700': 'hover:bg-primary/90',
    'bg-blue-600': 'bg-primary',
    'hover:bg-blue-700': 'hover:bg-primary/90',
    'text-gray-900': 'text-on-surface',
    'bg-gray-300': 'bg-surface-container-high'
}

for old, new in replacements.items():
    content = content.replace(old, new)

content = content.replace('chat-magnitude { background: #f3f4f6; color: #1f2937; margin-right: auto; border-bottom-left-radius: 4px; border: 1px solid #e5e7eb; }',
                          'chat-magnitude { background: var(--color-surface-container); color: var(--color-on-surface); margin-right: auto; border-bottom-left-radius: 4px; border: 1px solid var(--color-outline-variant); }')
content = content.replace('chat-user { background: #3b82f6; color: white; margin-left: auto; border-bottom-right-radius: 4px; }',
                          'chat-user { background: var(--color-primary); color: var(--color-on-primary); margin-left: auto; border-bottom-right-radius: 4px; }')

content = content.replace('class="w-full border border-outline-variant  rounded-md p-2 text-sm"', 'class="w-full bg-surface-container border border-outline-variant rounded-md p-2 text-sm text-on-surface placeholder:text-secondary/50 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"')
content = content.replace('class="flex-1 border border-outline-variant  rounded-lg p-3 text-sm focus:ring-2 focus:ring-primary outline-none resize-none"', 'class="flex-1 bg-surface-container border border-outline-variant rounded-lg p-3 text-sm text-on-surface placeholder:text-secondary/50 focus:ring-2 focus:ring-primary outline-none resize-none transition-colors"')

with open('static/downtime.html', 'w', encoding='utf-8') as f:
    f.write(content)
