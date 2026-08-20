import glob

html_files = glob.glob('static/*.html')
nav_link = """            <a href="/downtime" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors">
                <span class="material-icons text-xl text-gray-500">report_problem</span>
                <span class="font-medium">Downtime Register</span>
            </a>
            <a href="/configure\""""

for file in html_files:
    if file.endswith('downtime.html'): continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'Downtime Register' not in content:
        content = content.replace('<a href="/configure"', nav_link)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
