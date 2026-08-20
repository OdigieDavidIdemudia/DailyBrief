with open('static/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace('Login - Daily BRIEF', 'Change Password - Daily BRIEF')
new_content = new_content.replace('Welcome Back', 'Change Password')
new_content = new_content.replace('Sign in to continue to Daily BRIEF.', 'Please set a new password to continue.')

form_start = new_content.find('<form')
form_end = new_content.find('</form>') + 7

form_html = """<form id="change-password-form" class="space-y-4" onsubmit="handleChangePassword(event)">
    <div class="space-y-1.5">
        <label for="new_password" class="block text-sm font-medium text-on-surface">New Password</label>
        <input type="password" id="new_password" required
            class="w-full h-11 px-4 bg-surface-bright border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-on-surface" 
            placeholder="Enter new password">
    </div>
    <div class="space-y-1.5">
        <label for="confirm_password" class="block text-sm font-medium text-on-surface">Confirm Password</label>
        <input type="password" id="confirm_password" required
            class="w-full h-11 px-4 bg-surface-bright border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-on-surface" 
            placeholder="Confirm new password">
    </div>
    <div id="error-message" class="hidden p-3 rounded-lg bg-red-50 text-red-600 text-sm border border-red-100"></div>
    <button type="submit" id="submit-btn" 
        class="w-full h-11 rounded-lg font-bold bg-primary text-on-primary hover:bg-primary/90 hover:shadow-md transition-all flex items-center justify-center gap-2">
        <span>Update Password</span>
        <span class="material-symbols-outlined text-[20px]">arrow_forward</span>
    </button>
</form>"""

new_content = new_content[:form_start] + form_html + new_content[form_end:]

script_start = new_content.find('<script>')
script_end = new_content.find('</script>', script_start) + 9

script_html = """<script>
async function handleChangePassword(e) {
    e.preventDefault();
    const new_password = document.getElementById('new_password').value;
    const confirm_password = document.getElementById('confirm_password').value;
    const errorEl = document.getElementById('error-message');
    const submitBtn = document.getElementById('submit-btn');
    
    if (new_password !== confirm_password) {
        errorEl.textContent = 'Passwords do not match';
        errorEl.classList.remove('hidden');
        return;
    }
    
    errorEl.classList.add('hidden');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="material-symbols-outlined animate-spin text-[20px]">progress_activity</span><span>Updating...</span>';
    
    try {
        const res = await fetch('/api/auth/change_password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ new_password: new_password })
        });
        
        const data = await res.json();
        if (res.ok && data.success) {
            window.location.href = '/dashboard';
        } else {
            throw new Error(data.detail || data.error || 'Failed to update password');
        }
    } catch(err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove('hidden');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>Update Password</span><span class="material-symbols-outlined text-[20px]">arrow_forward</span>';
    }
}
</script>"""

new_content = new_content[:script_start] + script_html + new_content[script_end:]

with open('static/change_password.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Created change_password.html')
