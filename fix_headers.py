with open('static/downtime.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<h1 class="text-xl font-semibold hidden md:block">Dashboard</h1>', '<h1 class="text-xl font-semibold hidden md:block">Downtime Register</h1>')
content = content.replace('<h1 class="text-xl font-semibold md:hidden">Daily BRIEF</h1>', '<h1 class="text-xl font-semibold md:hidden">Downtime Register</h1>')

with open('static/downtime.html', 'w', encoding='utf-8') as f:
    f.write(content)
