import glob

bad_link = """            <a href="/downtime" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors">
                <span class="material-icons text-xl text-gray-500">report_problem</span>
                <span class="font-medium">Downtime Register</span>
            </a>"""

correct_link = """            <a href="/downtime" class="flex items-center gap-3 px-3 py-2 rounded-lg text-secondary hover:bg-surface-container transition-colors border-l-4 border-transparent">
                <span class="material-symbols-outlined">report</span>
                Downtime Register
            </a>"""

for file in glob.glob('static/*.html'):
    if 'downtime.html' in file:
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if bad_link in content:
        print(f'Fixing sidebar in {file}...')
        content = content.replace(bad_link, correct_link)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
