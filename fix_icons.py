with open('static/downtime.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<span class="material-icons">', '<span class="material-symbols-outlined">')
content = content.replace('<span class="material-icons text-sm">', '<span class="material-symbols-outlined text-sm">')
content = content.replace('<span class="material-icons text-5xl mb-2 text-secondary">', '<span class="material-symbols-outlined text-5xl mb-2 text-secondary">')
content = content.replace('<span class="material-icons text-xl text-gray-500">', '<span class="material-symbols-outlined text-xl text-secondary">')

with open('static/downtime.html', 'w', encoding='utf-8') as f:
    f.write(content)
