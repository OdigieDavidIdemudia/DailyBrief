import re

with open('static/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

generate_fetch_old = """
            try {
                const res = await fetch('/api/generate-handover-draft', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        included_tasks: selectedTasks,
                        is_update: isUpdate,
                        team_members: "",
                        duration: durationText
                    })
                });
"""

generate_fetch_new = """
            try {
                const reportType = document.querySelector('input[name="reportType"]:checked').value;
                let apiUrl, payload;
                
                if (reportType === 'subsidiary') {
                    const subName = document.getElementById('subsidiary-name').value.trim();
                    if (!subName) {
                        alert("Please enter a Subsidiary Name.");
                        document.getElementById('handover-config-view').classList.remove('hidden');
                        document.getElementById('btn-generate-draft').classList.remove('hidden');
                        document.getElementById('handover-loading-view').classList.add('hidden');
                        return;
                    }
                    apiUrl = '/api/generate-subsidiary-draft';
                    payload = {
                        included_tasks: selectedTasks,
                        subsidiary_name: subName
                    };
                } else {
                    apiUrl = '/api/generate-handover-draft';
                    payload = {
                        included_tasks: selectedTasks,
                        is_update: isUpdate,
                        team_members: "",
                        duration: durationText
                    };
                }
                
                const res = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
"""

export_fetch_old = """
                const res = await fetch('/api/export-handover', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        is_update: isUpdate,
                        location: location,
                        date_str: todayStr,
                        duration: durationText,
                        ai_data: editedData
                    })
                });
"""

export_fetch_new = """
                const reportType = document.querySelector('input[name="reportType"]:checked').value;
                let apiUrl, payload;
                
                if (reportType === 'subsidiary') {
                    apiUrl = '/api/export-subsidiary-report';
                    payload = {
                        subsidiary_name: document.getElementById('subsidiary-name').value.trim() || 'Unknown',
                        date_str: todayStr,
                        ai_data: editedData
                    };
                } else {
                    apiUrl = '/api/export-handover';
                    payload = {
                        is_update: isUpdate,
                        location: location,
                        date_str: todayStr,
                        duration: durationText,
                        ai_data: editedData
                    };
                }
                
                const res = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
"""

# Try basic replace, stripping spaces to be safe
def normalize(s):
    return re.sub(r'\s+', '', s)

idx = normalize(html).find(normalize(generate_fetch_old))
if idx != -1:
    # Use re.sub to match ignoring whitespace
    # A bit complicated, so we'll just write a script that iterates and drops lines
    pass

import tempfile
# safer way: since we know the structure, let's just find the line "const res = await fetch('/api/generate-handover-draft', {"
lines = html.splitlines()

# 1. Replace Generate Fetch
for i in range(len(lines)):
    if "const res = await fetch('/api/generate-handover-draft', {" in lines[i]:
        # Delete down to "});"
        end = i
        while "});" not in lines[end]:
            end += 1
        lines[i:end+1] = generate_fetch_new.strip('\n').split('\n')
        break

# 2. Replace Export Fetch
for i in range(len(lines)):
    if "const res = await fetch('/api/export-handover', {" in lines[i]:
        end = i
        while "});" not in lines[end]:
            end += 1
        lines[i:end+1] = export_fetch_new.strip('\n').split('\n')
        break

with open('static/dashboard.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Dashboard JS updated successfully')
