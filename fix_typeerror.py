with open('static/downtime.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("document.getElementById('user-name').textContent", "(document.getElementById('user-name') || document.querySelector('.user-name')).textContent")

with open('static/downtime.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed TypeError')
