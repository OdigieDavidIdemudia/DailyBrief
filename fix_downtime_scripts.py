import re

with open('static/downtime.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'<script>\s*let todayLogs = \[\];.*?</script>', '', content, flags=re.DOTALL)

bad_auth = """        // Setup initial UI
        document.addEventListener('DOMContentLoaded', () => {
            const cookies = document.cookie.split(';');
            const sessionCookie = cookies.find(c => c.trim().startsWith('tholder_session_token='));
            if (!sessionCookie) {
                window.location.href = '/login';
                return;
            }
            
            try {
                const tokenValue = sessionCookie.split('=')[1].replace('mock:', '');
                const emailStr = atob(tokenValue).split('|')[1];
                username = emailStr.split('@')[0];
                const parts = username.split('.');
                const formattedName = parts.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
                
                document.getElementById('user-name').textContent = formattedName;
                document.getElementById('user-avatar').textContent = formattedName.charAt(0);
            } catch (e) {
                console.error("Auth parsing failed", e);
            }"""

good_auth = """        // Setup initial UI
        document.addEventListener('DOMContentLoaded', async () => {
            try {
                const res = await fetch('/api/auth/me');
                if (!res.ok) throw new Error('Not logged in');
                const data = await res.json();
                
                const emailStr = data.user.email;
                username = emailStr.split('@')[0];
                const parts = username.split('.');
                const formattedName = parts.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
                
                const userNameEl = document.getElementById('user-name') || document.querySelector('.user-name');
                const userAvatarEl = document.getElementById('user-avatar') || document.querySelector('.user-avatar');
                if (userNameEl) userNameEl.textContent = formattedName;
                if (userAvatarEl) userAvatarEl.textContent = formattedName.charAt(0);
            } catch (e) {
                console.error("Auth fetching failed", e);
            }"""

content = content.replace(bad_auth, good_auth)

with open('static/downtime.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed script issues in downtime.html')
