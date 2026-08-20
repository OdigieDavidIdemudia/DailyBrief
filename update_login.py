with open('static/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = "if (res.ok && data.success) {\n            window.location.href = '/dashboard';"
replacement = """if (res.ok && data.success) {
            if (data.user && data.user.force_password_change) {
                window.location.href = '/change_password';
            } else {
                window.location.href = '/dashboard';
            }"""

content = content.replace(target, replacement)

with open('static/login.html', 'w', encoding='utf-8') as f:
    f.write(content)
