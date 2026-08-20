with open('static/unit_head.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Task section after the User table (find the closing tag of the main container and insert before it)
# The main container ends with a </div></main>. 

task_html = """
        <!-- Tasks Section -->
        <div class="mt-8">
            <div class="flex justify-between items-center mb-6">
                <div>
                    <h2 class="text-xl font-bold text-on-surface">Team Tasks</h2>
                    <p class="text-sm text-secondary">Tasks assigned to your team members.</p>
                </div>
                <button onclick="document.getElementById('task-modal').classList.remove('hidden')" class="px-4 py-2 bg-primary text-on-primary rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2">
                    <span class="material-symbols-outlined text-[20px]">add_task</span>
                    Assign Task
                </button>
            </div>
            
            <div class="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden shadow-sm">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-surface-container-low border-b border-outline-variant">
                                <th class="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Title</th>
                                <th class="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Category</th>
                                <th class="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Priority</th>
                                <th class="py-3 px-4 text-xs font-semibold text-secondary uppercase tracking-wider">Assigned To</th>
                            </tr>
                        </thead>
                        <tbody id="tasks-table-body" class="divide-y divide-outline-variant">
                            <!-- Tasks injected here -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Assign Task Modal -->
        <div id="task-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
            <div class="bg-surface-container-lowest border border-outline-variant rounded-2xl p-6 w-full max-w-md shadow-2xl relative">
                <button onclick="document.getElementById('task-modal').classList.add('hidden')" class="absolute top-4 right-4 material-symbols-outlined text-secondary hover:text-on-surface transition-colors p-1 rounded-full hover:bg-surface-container">close</button>
                <h3 class="text-xl font-bold text-on-surface mb-4">Assign New Task</h3>
                <form id="task-form" onsubmit="handleCreateTask(event)" class="space-y-4">
                    <div class="space-y-1.5">
                        <label class="block text-sm font-medium text-on-surface">Task Title</label>
                        <input type="text" id="task_title" required class="w-full h-10 px-3 bg-surface-bright border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary/20 outline-none text-on-surface">
                    </div>
                    <div class="space-y-1.5">
                        <label class="block text-sm font-medium text-on-surface">Category</label>
                        <select id="task_category" class="w-full h-10 px-3 bg-surface-bright border border-outline-variant rounded-lg text-sm outline-none text-on-surface">
                            <option value="Daily">Daily</option>
                            <option value="Monthly">Monthly</option>
                        </select>
                    </div>
                    <div class="space-y-1.5">
                        <label class="block text-sm font-medium text-on-surface">Priority</label>
                        <select id="task_priority" class="w-full h-10 px-3 bg-surface-bright border border-outline-variant rounded-lg text-sm outline-none text-on-surface">
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                            <option value="Critical">Critical</option>
                        </select>
                    </div>
                    <div class="space-y-1.5">
                        <label class="block text-sm font-medium text-on-surface">Assign To</label>
                        <select id="task_assignee" required class="w-full h-10 px-3 bg-surface-bright border border-outline-variant rounded-lg text-sm outline-none text-on-surface">
                            <!-- Team members injected here -->
                        </select>
                    </div>
                    <div id="task-error-message" class="hidden p-3 rounded-lg bg-red-50 text-red-600 text-sm border border-red-100"></div>
                    <button type="submit" id="task-submit-btn" class="w-full h-11 rounded-lg font-bold bg-primary text-on-primary hover:bg-primary/90 transition-colors">Assign Task</button>
                </form>
            </div>
        </div>
"""

# Insert task_html right before </main>
main_end = content.find('</main>')
if main_end != -1:
    content = content[:main_end] + task_html + content[main_end:]
else:
    print('Error: </main> not found')

js_html = """
// Fetch Tasks
async function fetchTasks() {
    try {
        const res = await fetch('/api/unit/tasks');
        if (res.ok) {
            const tasks = await res.json();
            renderTasks(tasks);
        }
    } catch(err) {
        console.error('Failed to fetch tasks', err);
    }
}

function renderTasks(tasks) {
    const tbody = document.getElementById('tasks-table-body');
    tbody.innerHTML = '';
    if (tasks.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="py-8 text-center text-secondary text-sm">No tasks assigned yet.</td></tr>`;
        return;
    }
    
    tasks.forEach(t => {
        // Find assignee username
        const member = usersList.find(u => u.id === t.user_id);
        const assigneeName = member ? member.username : 'Unknown';
        
        let priorityColor = 'text-secondary bg-surface-container';
        if (t.priority === 'High') priorityColor = 'text-[#ea580c] bg-[#fff7ed]';
        if (t.priority === 'Critical') priorityColor = 'text-[#dc2626] bg-[#fef2f2]';
        
        tbody.innerHTML += `
            <tr class="hover:bg-surface-bright/50 transition-colors">
                <td class="py-3 px-4 text-sm font-medium text-on-surface">${t.title}</td>
                <td class="py-3 px-4 text-sm text-secondary">${t.category}</td>
                <td class="py-3 px-4"><span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${priorityColor}">${t.priority}</span></td>
                <td class="py-3 px-4 text-sm text-secondary">${assigneeName}</td>
            </tr>
        `;
    });
}

async function handleCreateTask(e) {
    e.preventDefault();
    const btn = document.getElementById('task-submit-btn');
    const errEl = document.getElementById('task-error-message');
    btn.disabled = true;
    errEl.classList.add('hidden');
    
    const payload = {
        title: document.getElementById('task_title').value,
        category: document.getElementById('task_category').value,
        priority: document.getElementById('task_priority').value,
        assigned_to: document.getElementById('task_assignee').value
    };
    
    try {
        const res = await fetch('/api/unit/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('task-modal').classList.add('hidden');
            document.getElementById('task-form').reset();
            fetchTasks();
        } else {
            throw new Error(data.detail || 'Failed to assign task');
        }
    } catch(err) {
        errEl.textContent = err.message;
        errEl.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    }
}
"""

# Append js_html to the script block (right before the closing </script>)
script_end = content.rfind('</script>')
if script_end != -1:
    content = content[:script_end] + js_html + content[script_end:]
else:
    print('Error: </script> not found')

# Also modify fetchUsers() to populate the assignee dropdown
# Instead of replacing fetchUsers entirely, we can just add a call to populateAssigneeDropdown() inside renderUsers()
# Or better, inside fetchUsers after setting usersList
populate_js = """
    // Populate task assignee dropdown
    const select = document.getElementById('task_assignee');
    if (select) {
        select.innerHTML = '';
        usersList.forEach(u => {
            select.innerHTML += `<option value="${u.id}">${u.username}</option>`;
        });
    }
"""
content = content.replace('renderUsers();', 'renderUsers();\n' + populate_js)

# And call fetchTasks() in initPage()
content = content.replace('fetchUsers();', 'fetchUsers();\n        fetchTasks();')

with open('static/unit_head.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Added Task section to unit_head.html')
