import re
import os

def patch_admin():
    with open('static/admin.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add unit_head option to role select
    html = html.replace(
        '<option value="admin">Admin</option>',
        '<option value="admin">Admin</option>\n                            <option value="unit_head">Unit Head</option>'
    )

    # 2. Add Tabs UI (Users | Teams) right above the users table
    tabs_html = """
                <!-- Tabs -->
                <div class="flex gap-4 border-b border-outline-variant mb-6">
                    <button id="tab-users" onclick="switchTab('users')" class="py-2 px-4 border-b-2 border-primary text-primary font-semibold transition-colors">Users</button>
                    <button id="tab-teams" onclick="switchTab('teams')" class="py-2 px-4 border-b-2 border-transparent text-secondary hover:text-on-surface font-semibold transition-colors">Teams</button>
                </div>

                <div id="users-view">
    """
    if '<!-- Tabs -->' not in html:
        html = html.replace('<div class="bg-surface-container-lowest border border-outline-variant rounded-2xl shadow-sm overflow-hidden">', tabs_html + '<div class="bg-surface-container-lowest border border-outline-variant rounded-2xl shadow-sm overflow-hidden">', 1)

    # 3. Add Teams View (table & create button)
    teams_view_html = """
                </div> <!-- End Users View -->

                <!-- Teams View -->
                <div id="teams-view" class="hidden">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-bold text-on-surface">Teams</h2>
                        <button onclick="openTeamModal()" class="bg-primary text-on-primary px-4 py-2 rounded-lg font-semibold shadow-sm hover:bg-primary/90 transition-colors flex items-center gap-2">
                            <span class="material-symbols-outlined text-[18px]">group_add</span>
                            Create Team
                        </button>
                    </div>
                    
                    <div class="bg-surface-container-lowest border border-outline-variant rounded-2xl shadow-sm overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse">
                                <thead class="bg-surface-container-low border-b border-outline-variant">
                                    <tr>
                                        <th class="p-4 text-xs font-semibold text-secondary uppercase tracking-wider">Team Name</th>
                                        <th class="p-4 text-xs font-semibold text-secondary uppercase tracking-wider">Unit Head ID</th>
                                        <th class="p-4 text-xs font-semibold text-secondary uppercase tracking-wider">Members</th>
                                        <th class="p-4 text-xs font-semibold text-secondary uppercase tracking-wider text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="teams-tbody" class="divide-y divide-outline-variant bg-surface-bright">
                                    <!-- Teams injected here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
    """
    if '<!-- Teams View -->' not in html:
        html = html.replace('</main>', teams_view_html + '\n            </main>', 1)

    # 4. Add Team Modals (Create Team & Manage Team)
    modals_html = """
    <!-- Create Team Modal -->
    <div id="team-modal" class="hidden fixed inset-0 z-[100] flex items-center justify-center px-4 bg-black/80 backdrop-blur-sm transition-opacity duration-300">
        <div class="bg-surface-container-lowest border border-outline-variant rounded-2xl p-6 w-full max-w-md shadow-2xl relative">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-bold text-on-surface">Create Team</h3>
                <button onclick="closeTeamModal()" class="material-symbols-outlined text-secondary hover:text-on-surface transition-colors p-1 rounded-full hover:bg-surface-container">close</button>
            </div>
            
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-bold text-on-surface mb-2">Team Name</label>
                    <input type="text" id="team-name-input" class="w-full bg-surface-bright border border-outline-variant rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-on-surface" placeholder="e.g. Engineering">
                </div>
                <div>
                    <label class="block text-sm font-bold text-on-surface mb-2">Assign Unit Head (Optional)</label>
                    <select id="team-head-input" class="w-full bg-surface-bright border border-outline-variant rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-on-surface">
                        <option value="">-- None --</option>
                    </select>
                </div>
            </div>
            
            <div class="flex gap-3 mt-8">
                <button onclick="closeTeamModal()" class="flex-1 py-2.5 rounded-lg font-semibold text-secondary hover:bg-surface-container transition-colors">Cancel</button>
                <button onclick="saveTeam()" class="flex-1 py-2.5 rounded-lg font-bold bg-primary text-on-primary hover:bg-primary/90 transition-colors shadow-sm">Save Team</button>
            </div>
        </div>
    </div>

    <!-- Manage Team Members Modal -->
    <div id="manage-team-modal" class="hidden fixed inset-0 z-[100] flex items-center justify-center px-4 bg-black/80 backdrop-blur-sm transition-opacity duration-300">
        <div class="bg-surface-container-lowest border border-outline-variant rounded-2xl p-6 w-full max-w-md shadow-2xl relative">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-bold text-on-surface">Manage Team Members</h3>
                <button onclick="closeManageTeamModal()" class="material-symbols-outlined text-secondary hover:text-on-surface transition-colors p-1 rounded-full hover:bg-surface-container">close</button>
            </div>
            
            <div class="space-y-4">
                <input type="hidden" id="manage-team-id">
                <div>
                    <label class="block text-sm font-bold text-on-surface mb-2">Select Members</label>
                    <div id="manage-team-members-list" class="max-h-60 overflow-y-auto space-y-2 border border-outline-variant rounded-lg p-2 bg-surface-bright">
                        <!-- Checkboxes injected here -->
                    </div>
                </div>
            </div>
            
            <div class="flex gap-3 mt-8">
                <button onclick="closeManageTeamModal()" class="flex-1 py-2.5 rounded-lg font-semibold text-secondary hover:bg-surface-container transition-colors">Cancel</button>
                <button onclick="saveTeamMembers()" class="flex-1 py-2.5 rounded-lg font-bold bg-primary text-on-primary hover:bg-primary/90 transition-colors shadow-sm">Save Members</button>
            </div>
        </div>
    </div>
    """
    if '<!-- Create Team Modal -->' not in html:
        html = html.replace('<!-- Export Modal -->', modals_html + '\n    <!-- Export Modal -->', 1)

    # 5. Add JS logic for Teams
    teams_js = """
        let teams = [];

        function switchTab(tab) {
            document.getElementById('users-view').classList.add('hidden');
            document.getElementById('teams-view').classList.add('hidden');
            document.getElementById('tab-users').className = "py-2 px-4 border-b-2 border-transparent text-secondary hover:text-on-surface font-semibold transition-colors";
            document.getElementById('tab-teams').className = "py-2 px-4 border-b-2 border-transparent text-secondary hover:text-on-surface font-semibold transition-colors";

            if (tab === 'users') {
                document.getElementById('users-view').classList.remove('hidden');
                document.getElementById('tab-users').className = "py-2 px-4 border-b-2 border-primary text-primary font-semibold transition-colors";
            } else {
                document.getElementById('teams-view').classList.remove('hidden');
                document.getElementById('tab-teams').className = "py-2 px-4 border-b-2 border-primary text-primary font-semibold transition-colors";
                loadTeams();
            }
        }

        async function loadTeams() {
            try {
                const res = await fetch('/api/admin/teams');
                if (res.ok) {
                    teams = await res.json();
                    renderTeams();
                } else if (res.status === 401) {
                    window.location.href = '/login';
                }
            } catch (err) {
                console.error("Failed to load teams", err);
            }
        }

        function renderTeams() {
            const tbody = document.getElementById('teams-tbody');
            tbody.innerHTML = '';
            teams.forEach(t => {
                let headName = "None";
                if(t.unit_head_id) {
                    const h = users.find(u => u.id === t.unit_head_id);
                    if (h) headName = h.username;
                }
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-surface-container-low transition-colors group';
                tr.innerHTML = `
                    <td class="p-4 text-sm font-semibold text-on-surface">${t.name}</td>
                    <td class="p-4 text-sm text-secondary">${headName}</td>
                    <td class="p-4 text-sm text-secondary">${t.member_count}</td>
                    <td class="p-4 text-sm text-right space-x-2">
                        <button onclick="openManageTeamModal('${t.id}')" class="text-primary hover:text-primary/80 font-medium">Manage Members</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        function openTeamModal() {
            document.getElementById('team-modal').classList.remove('hidden');
            document.getElementById('team-name-input').value = '';
            const headSelect = document.getElementById('team-head-input');
            headSelect.innerHTML = '<option value="">-- None --</option>';
            users.filter(u => u.role === 'unit_head').forEach(u => {
                headSelect.innerHTML += `<option value="${u.id}">${u.username}</option>`;
            });
        }
        function closeTeamModal() {
            document.getElementById('team-modal').classList.add('hidden');
        }
        async function saveTeam() {
            const name = document.getElementById('team-name-input').value;
            const head = document.getElementById('team-head-input').value;
            if(!name) return alert('Name required');
            try {
                const res = await fetch('/api/admin/teams', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: name, unit_head_id: head || null})
                });
                if(res.ok) {
                    closeTeamModal();
                    loadTeams();
                } else {
                    const err = await res.json();
                    alert(err.detail || 'Error creating team');
                }
            } catch(e) { console.error(e); }
        }

        function openManageTeamModal(teamId) {
            document.getElementById('manage-team-modal').classList.remove('hidden');
            document.getElementById('manage-team-id').value = teamId;
            const list = document.getElementById('manage-team-members-list');
            list.innerHTML = '';
            users.filter(u => u.role !== 'admin').forEach(u => {
                const isMember = u.team_id === teamId;
                list.innerHTML += `
                    <label class="flex items-center space-x-2 text-sm text-on-surface p-1 hover:bg-surface-container rounded cursor-pointer">
                        <input type="checkbox" value="${u.id}" ${isMember ? 'checked' : ''} class="rounded border-outline-variant text-primary focus:ring-primary/20">
                        <span>${u.username} (${u.role})</span>
                    </label>
                `;
            });
        }
        function closeManageTeamModal() {
            document.getElementById('manage-team-modal').classList.add('hidden');
        }
        async function saveTeamMembers() {
            const teamId = document.getElementById('manage-team-id').value;
            const checkboxes = document.querySelectorAll('#manage-team-members-list input[type="checkbox"]:checked');
            const userIds = Array.from(checkboxes).map(c => c.value);
            
            try {
                const res = await fetch(`/api/admin/teams/${teamId}/members`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_ids: userIds})
                });
                if (res.ok) {
                    closeManageTeamModal();
                    loadUsers();
                    loadTeams();
                } else {
                    alert('Error saving members');
                }
            } catch(e) { console.error(e); }
        }
    """
    if 'let teams = [];' not in html:
        html = html.replace('// Initialize on load', teams_js + '\n        // Initialize on load')

    with open('static/admin.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    # Update unit_head.html to display team name
    with open('static/unit_head.html', 'r', encoding='utf-8') as f:
        uh_html = f.read()
    
    if "const h1 = document.querySelector('h1.text-3xl');" not in uh_html:
        fetch_team_js = """
        // Fetch My Team
        async function loadMyTeam() {
            try {
                const res = await fetch('/api/unit/my_team');
                if (res.ok) {
                    const team = await res.json();
                    const h1 = document.querySelector('h1.text-3xl');
                    if(h1) h1.textContent = team.name + " Team";
                }
            } catch (err) { console.error(err); }
        }
        """
        uh_html = uh_html.replace('async function initPage() {', fetch_team_js + '\n        async function initPage() {\n            loadMyTeam();')
        
    with open('static/unit_head.html', 'w', encoding='utf-8') as f:
        f.write(uh_html)

if __name__ == '__main__':
    patch_admin()
    print('Patched HTML files successfully')
