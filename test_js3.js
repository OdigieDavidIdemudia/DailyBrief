
        let todayLogs = [];
        let archivedReports = [];
        let debounceTimers = {};
        let expandedTaskIds = new Set();

        function toggleExpand(logId) {
            const detailsEl = document.getElementById(`details-${logId}`);
            const arrowEl = document.getElementById(`arrow-${logId}`);
            if (detailsEl.classList.contains('hidden')) {
                detailsEl.classList.remove('hidden');
                arrowEl.textContent = 'keyboard_arrow_up';
                expandedTaskIds.add(logId);
            } else {
                detailsEl.classList.add('hidden');
                arrowEl.textContent = 'keyboard_arrow_down';
                expandedTaskIds.delete(logId);
            }
        }


        // Fetch User and page data
        async function initPage() {
            try {
                // Verify auth
                const userRes = await fetch('/api/auth/me');
                if (!userRes.ok) {
                    window.location.href = '/login';
                    return;
                }
                const userData = await userRes.json();
                document.getElementById('user-display-email').textContent = userData.user.email;

                if (userData.user.email === 'estylily.johnson') {
                    const aiHandoverSec = document.getElementById('ai-handover-section');
                    if (aiHandoverSec) {
                        aiHandoverSec.style.display = 'none';
                    }
                }

                // Load dates
                const today = new Date();
                const options = { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' };
                document.getElementById('today-date-string').textContent = today.toLocaleDateString('en-US', options);

                // Load operational data
                await loadTasks();
                await loadReports();
                await loadVisualizer();
            } catch (err) {
                console.error("Initialization failed", err);
            }
        }

        // Load tasks list
        async function loadTasks() {
            try {
                const res = await fetch('/api/logs');
                if (res.ok) {
                    todayLogs = await res.json();
                    renderTasks();
                    updateBadge();
                }
            } catch (err) {
                console.error("Load tasks failed", err);
            }
        }

        // Render Tasks
        function renderTasks() {
            const container = document.getElementById('tasks-container');
            if (todayLogs.length === 0) {
                container.innerHTML = `
                    <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-8 text-center flex flex-col items-center justify-center min-h-[300px] shadow-sm">
                        <span class="material-symbols-outlined text-[48px] text-primary/30 mb-2">assignment_late</span>
                        <h3 class="text-lg font-bold text-on-surface mb-1">Roster Empty for Today</h3>
                        <p class="text-sm text-secondary max-w-[400px] mb-6 leading-relaxed">
                            No active tasks have been deployed for today. You need to provision the roster in the Setup Configuration view first.
                        </p>
                        <a href="/configure" class="bg-primary text-on-primary font-semibold px-6 py-3 rounded-lg flex items-center gap-1 hover:bg-primary/95 transition-all shadow-lg shadow-primary/10 active:scale-[0.98] duration-150">
                            <span class="material-symbols-outlined">lock_open</span>
                            Configure & Deploy Month
                        </a>
                    </div>
                `;
                return;
            }

            const searchInput = document.getElementById('search-input');
            const categoryFilter = document.getElementById('category-filter');
            
            const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
            const selectedCategory = categoryFilter ? categoryFilter.value : 'All';

            const filteredLogs = todayLogs.filter(log => {
                const matchesSearch = log.title.toLowerCase().includes(searchTerm) || 
                                      (log.summary && log.summary.toLowerCase().includes(searchTerm));
                const matchesCategory = selectedCategory === 'All' || log.category === selectedCategory;
                return matchesSearch && matchesCategory;
            });

            if (filteredLogs.length === 0) {
                container.innerHTML = `
                    <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-8 text-center flex flex-col items-center justify-center min-h-[150px] shadow-sm">
                        <p class="text-sm text-secondary">No tasks match your search or filter.</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = filteredLogs.map(log => {
                const isCriticalChecked = log.is_critical ? 'checked' : '';
                const isExpanded = expandedTaskIds.has(log.id);
                return `
                    <section data-log-id="${log.id}" class="bg-surface-container-lowest border ${log.is_critical ? 'border-error/40' : 'border-outline-variant'} rounded-xl p-6 transition-all hover:border-primary/30 relative flex flex-col gap-4">
                        <div class="flex justify-between items-start cursor-pointer select-none" onclick="toggleExpand('${log.id}')">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-lg flex items-center justify-center bg-surface-container text-primary">
                                    <span class="material-symbols-outlined">${log.category === 'Monthly' ? 'layers' : (log.category === 'Personal' ? 'person' : (log.category === 'Subsidiary' ? 'business' : (log.category === 'Colleague Handover' ? 'handshake' : 'security')))}</span>
                                </div>
                                <div>
                                    <h3 class="text-base font-bold text-on-surface leading-tight">${log.title}</h3>
                                    <p class="text-xs text-secondary">${log.category} &bull; ${log.priority} Priority</p>
                                </div>
                            </div>

                            <div class="flex items-center gap-2" onclick="event.stopPropagation()">
                                <!-- Save status indicator -->
                                <span id="save-status-${log.id}" class="text-[10px] text-secondary flex items-center gap-1"></span>
                                
                                <select onchange="updateLogField('${log.id}', 'status', this.value)" class="bg-surface-bright border border-outline-variant rounded-lg text-xs px-3 py-1 font-medium text-on-surface focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all cursor-pointer">
                                    <option value="Pending" ${log.status === 'Pending' ? 'selected' : ''}>Pending</option>
                                    <option value="In Progress" ${log.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                                    <option value="Completed" ${log.status === 'Completed' ? 'selected' : ''}>Completed</option>
                                    <option value="Flagged" ${log.status === 'Flagged' ? 'selected' : ''}>Flagged</option>
                                    <option value="Blocked" ${log.status === 'Blocked' ? 'selected' : ''}>Blocked</option>
                                </select>
                                
                                <button class="material-symbols-outlined text-secondary hover:text-primary transition-colors p-1 rounded-full hover:bg-slate-100 flex items-center justify-center cursor-pointer ml-1" onclick="event.stopPropagation(); toggleExpand('${log.id}')">
                                    <span id="arrow-${log.id}">${isExpanded ? 'keyboard_arrow_up' : 'keyboard_arrow_down'}</span>
                                </button>
                            </div>
                        </div>

                        <div id="details-${log.id}" class="${isExpanded ? '' : 'hidden'} space-y-4 border-t border-outline-variant/30 pt-4 mt-2">
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div class="space-y-1">
                                    <label class="text-xs font-semibold text-secondary uppercase tracking-wider">Summary</label>
                                    <textarea oninput="debounceSave('${log.id}', 'summary', this.value)" class="w-full min-h-[100px] p-3 bg-surface-bright border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none text-on-surface" placeholder="Describe current scan progress...">${log.summary || ''}</textarea>
                                </div>
                                <div class="space-y-1">
                                    <label class="text-xs font-semibold text-secondary uppercase tracking-wider">Challenges</label>
                                    <textarea oninput="debounceSave('${log.id}', 'challenges', this.value)" class="w-full min-h-[100px] p-3 bg-surface-bright border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none text-on-surface" placeholder="Note any blocked files or system lag...">${log.challenges || ''}</textarea>
                                </div>
                                <div class="space-y-1">
                                    <label class="text-xs font-semibold text-secondary uppercase tracking-wider">Mail Trail</label>
                                    <textarea oninput="debounceSave('${log.id}', 'mail_trail', this.value)" class="w-full min-h-[100px] p-3 bg-surface-bright border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none text-on-surface" placeholder="Note any relevant email discussions...">${log.mail_trail || ''}</textarea>
                                </div>
                            </div>

                            <!-- Critical Blocker Toggle -->
                            <div class="flex items-center justify-between pt-2">
                                <div class="flex items-center gap-1">
                                    <span class="material-symbols-outlined report-icon text-[20px] ${log.is_critical ? 'text-error fill-1' : 'text-secondary/50'}">report</span>
                                    <span class="text-xs text-secondary">This task has critical blockers affecting delivery</span>
                                </div>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" ${isCriticalChecked} onchange="updateLogField('${log.id}', 'is_critical', this.checked)" class="sr-only peer"/>
                                    <div class="w-9 h-5 bg-secondary-container rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-outline after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-error"></div>
                                </label>
                            </div>
                        </div>
                    </section>
                `;
            }).join('');
        }

        // Update task count badge
        function updateBadge() {
            const pendingCount = todayLogs.filter(l => l.status !== 'Completed').length;
            const badge = document.getElementById('pending-tasks-badge');
            
            if (todayLogs.length > 0) {
                badge.classList.remove('hidden');
                badge.textContent = pendingCount === 0 ? 'All Tasks Completed' : `${pendingCount} Tasks Pending`;
            } else {
                badge.classList.add('hidden');
            }
        }

        // Debounce text inputs
        function debounceSave(logId, field, value) {
            const statusEl = document.getElementById(`save-status-${logId}`);
            statusEl.innerHTML = `<span class="material-symbols-outlined text-[14px] animate-spin">sync</span> Saving...`;

            if (debounceTimers[logId + field]) {
                clearTimeout(debounceTimers[logId + field]);
            }

            debounceTimers[logId + field] = setTimeout(() => {
                const log = todayLogs.find(l => l.id === logId);
                if (log) {
                    log[field] = value;
                    saveLog(log);
                }
            }, 800);
        }

        // Direct updates (select/checkbox)
        function updateLogField(logId, field, value) {
            const log = todayLogs.find(l => l.id === logId);
            if (log) {
                log[field] = value;
                // Update card border color in-place for critical toggle without full re-render
                if (field === 'is_critical') {
                    const card = document.querySelector(`section[data-log-id="${logId}"]`);
                    if (card) {
                        card.className = card.className
                            .replace(/border-error\/40|border-outline-variant/g, '')
                            .trim();
                        card.classList.add(value ? 'border-error/40' : 'border-outline-variant');
                        // Update icon color
                        const icon = card.querySelector('.report-icon');
                        if (icon) {
                            icon.className = icon.className
                                .replace(/text-error|text-secondary\/50/g, '')
                                .trim() + (value ? ' text-error' : ' text-secondary/50');
                        }
                    }
                }
                saveLog(log);
            }
        }

        // Save call to API
        async function saveLog(log) {
            const statusEl = document.getElementById(`save-status-${log.id}`);
            try {
                const response = await fetch(`/api/logs/${log.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        status: log.status,
                        summary: log.summary || "",
                        challenges: log.challenges || "",
                        mail_trail: log.mail_trail || "",
                        is_critical: log.is_critical
                    })
                });

                if (response.ok) {
                    statusEl.innerHTML = `<span class="material-symbols-outlined text-[14px] text-green-600">done</span> Saved`;
                    updateBadge();
                    setTimeout(() => {
                        statusEl.innerHTML = "";
                    }, 1500);
                } else {
                    statusEl.innerHTML = `<span class="material-symbols-outlined text-[14px] text-error">error</span> Error`;
                }
            } catch (err) {
                statusEl.innerHTML = `<span class="material-symbols-outlined text-[14px] text-error">error</span> Error`;
            }
        }

        // Load reports archives
        async function loadReports() {
            try {
                const res = await fetch('/api/reports');
                if (res.ok) {
                    archivedReports = await res.json();
                    renderReports();
                }
            } catch (err) {
                console.error("Load reports failed", err);
            }
        }

        // Render Reports section
        function renderReports() {
            const todayStr = new Date().toISOString().split('T')[0];
            
            // Check if reports for today already exist
            const todayPdf = archivedReports.find(r => r.format === 'pdf' && r.date_generated.startsWith(todayStr));
            const todayCsv = archivedReports.find(r => r.format === 'csv' && r.date_generated.startsWith(todayStr));
            const todayXlsx = archivedReports.find(r => r.format === 'xlsx' && r.date_generated.startsWith(todayStr));
            
            const statusEl = document.getElementById('report-hub-status');
            const actionsEl = document.getElementById('export-actions');
            
            if (todayPdf || todayCsv || todayXlsx) {
                statusEl.textContent = "Available for download";
                actionsEl.innerHTML = `
                    <div class="grid grid-cols-3 gap-2">
                        ${todayPdf ? `
                        <a href="${todayPdf.file_url}" download class="flex items-center justify-center gap-1 bg-surface-container text-primary font-bold py-3 rounded-lg hover:bg-surface-container-high border border-outline-variant transition-all text-center text-[10px] shadow-sm active:scale-95 cursor-pointer">
                            <span class="material-symbols-outlined text-[16px]">picture_as_pdf</span>
                            PDF
                        </a>` : ''}
                        ${todayXlsx ? `
                        <a href="${todayXlsx.file_url}" download class="flex items-center justify-center gap-1 bg-surface-container text-primary font-bold py-3 rounded-lg hover:bg-surface-container-high border border-outline-variant transition-all text-center text-[10px] shadow-sm active:scale-95 cursor-pointer">
                            <span class="material-symbols-outlined text-[16px]">grid_on</span>
                            Excel
                        </a>` : ''}
                        ${todayCsv ? `
                        <a href="${todayCsv.file_url}" download class="flex items-center justify-center gap-1 bg-surface-container text-primary font-bold py-3 rounded-lg hover:bg-surface-container-high border border-outline-variant transition-all text-center text-[10px] shadow-sm active:scale-95 cursor-pointer">
                            <span class="material-symbols-outlined text-[16px]">table_chart</span>
                            CSV
                        </a>` : ''}
                    </div>
                    <button onclick="openExportModal()" class="w-full mt-4 bg-surface-container-high text-primary font-bold py-2 rounded-lg flex items-center justify-center gap-2 border border-outline-variant hover:bg-surface-container-highest transition-all shadow-sm active:scale-[0.98]">
                        <span class="material-symbols-outlined text-[18px]">tune</span>
                        Custom Export
                    </button>
                `;
            } else {
                statusEl.textContent = "Generated automatically at 17:00 WAT";
                actionsEl.innerHTML = `
                    <button class="w-full bg-surface-container-low text-secondary font-bold py-3 rounded-lg border border-outline-variant border-dashed text-sm flex items-center justify-center gap-2 cursor-not-allowed mb-2">
                        <span class="material-symbols-outlined text-[18px]">lock</span>
                        Unlocks at 17:00 WAT
                    </button>
                    <button id="manual-gen-btn" onclick="openExportModal()" class="w-full mt-4 bg-primary text-on-primary font-bold py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-primary/90 transition-all shadow-lg shadow-primary/10 active:scale-[0.98]">
                        <span class="material-symbols-outlined text-[18px]">rocket_launch</span>
                        Generate Custom Report
                    </button>
                `;
            }

            // Render Previous Archive (excluding today)
            const archiveContainer = document.getElementById('archive-container');
            const previousReports = archivedReports.filter(r => !r.date_generated.startsWith(todayStr));
            
            if (previousReports.length === 0) {
                archiveContainer.innerHTML = `
                    <p class="text-xs text-secondary/60 italic text-center py-4 border border-dashed border-outline-variant/60 rounded-lg">
                        No archived reports yet.
                    </p>
                `;
                return;
            }

            // Group by date
            const grouped = {};
            previousReports.forEach(r => {
                const datePart = r.date_generated.split('T')[0];
                if (!grouped[datePart]) {
                    grouped[datePart] = { date: datePart };
                }
                grouped[datePart][r.format] = r.file_url;
            });

            const sortedDates = Object.values(grouped).sort((a,b) => new Date(b.date) - new Date(a.date));
            
            archiveContainer.innerHTML = sortedDates.map(item => {
                const dt = new Date(item.date);
                const dayLabel = dt.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
                
                return `
                    <div class="group flex items-center justify-between p-3 border border-outline-variant/50 rounded-lg hover:bg-surface-container-low transition-colors">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-secondary">description</span>
                            <div class="flex flex-col">
                                <span class="text-sm font-semibold text-on-surface">${dayLabel}</span>
                                <span class="text-[10px] text-secondary">Log Complete</span>
                            </div>
                        </div>
                        <div class="flex items-center gap-1">
                            ${item.pdf ? `<a href="${item.pdf}" download class="p-1 text-secondary hover:text-primary hover:bg-surface-container rounded transition-colors flex items-center justify-center" title="Download PDF"><span class="material-symbols-outlined text-[18px]">picture_as_pdf</span></a>` : ''}
                            ${item.xlsx ? `<a href="${item.xlsx}" download class="p-1 text-secondary hover:text-primary hover:bg-surface-container rounded transition-colors flex items-center justify-center" title="Download Excel"><span class="material-symbols-outlined text-[18px]">grid_on</span></a>` : ''}
                            ${item.csv ? `<a href="${item.csv}" download class="p-1 text-secondary hover:text-primary hover:bg-surface-container rounded transition-colors flex items-center justify-center" title="Download CSV"><span class="material-symbols-outlined text-[18px]">table_chart</span></a>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        // Export Modal Logic
        let exportSelectedIds = new Set();
        
        function openExportModal() {
            if (todayLogs.length === 0) {
                alert("Cannot generate report: No active tasks logged for today.");
                return;
            }
            const modal = document.getElementById('export-modal');
            document.getElementById('export-search').value = "";
            document.getElementById('export-category-filter').value = "All";
            
            // Check all by default on open
            exportSelectedIds = new Set(todayLogs.map(l => l.id));
            renderExportTasks();
            
            modal.classList.remove('hidden');
        }
        
        function renderExportTasks() {
            const taskList = document.getElementById('export-task-list');
            const searchQ = document.getElementById('export-search').value.toLowerCase();
            const catFilter = document.getElementById('export-category-filter').value;
            
            let filtered = todayLogs.filter(log => {
                const matchesSearch = log.title.toLowerCase().includes(searchQ) || (log.summary && log.summary.toLowerCase().includes(searchQ));
                const matchesCategory = catFilter === 'All' || log.category === catFilter;
                return matchesSearch && matchesCategory;
            });
            
            if (filtered.length === 0) {
                taskList.innerHTML = `<p class="text-xs text-secondary italic py-4 text-center border border-dashed border-outline-variant/60 rounded-lg">No tasks match your filters.</p>`;
                return;
            }
            
            taskList.innerHTML = filtered.map(log => `
                <label class="flex items-center gap-3 p-3 bg-surface-bright border border-outline-variant rounded-lg cursor-pointer hover:bg-surface-container transition-colors">
                    <input type="checkbox" value="${log.id}" onchange="toggleExportSelection('${log.id}', this.checked)" class="w-4 h-4 text-primary rounded border-outline-variant focus:ring-primary/20 export-task-checkbox" ${exportSelectedIds.has(log.id) ? 'checked' : ''} />
                    <div class="flex-grow">
                        <p class="text-sm font-semibold text-on-surface leading-tight">${log.title}</p>
                        <p class="text-[10px] text-secondary">${log.category} • ${log.status}</p>
                    </div>
                </label>
            `).join('');
        }
        
        function toggleExportSelection(id, isChecked) {
            if (isChecked) exportSelectedIds.add(id);
            else exportSelectedIds.delete(id);
        }
        
        function toggleAllExportTasks() {
            // Only affect the currently visible filtered list
            const checkboxes = document.querySelectorAll('.export-task-checkbox');
            if(checkboxes.length === 0) return;
            
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            checkboxes.forEach(cb => {
                cb.checked = !allChecked;
                toggleExportSelection(cb.value, !allChecked);
            });
        }

        function closeExportModal() {
            document.getElementById('export-modal').classList.add('hidden');
        }

        async function submitCustomExport() {
            const selectedIds = Array.from(exportSelectedIds);
            
            if (selectedIds.length === 0) {
                alert("Please select at least one task to export.");
                return;
            }

            const format = document.getElementById('export-format').value;
            const btn = document.getElementById('submit-export-btn');
            const originalText = btn.innerHTML;
            
            btn.disabled = true;
            btn.innerHTML = `<span class="material-symbols-outlined animate-spin text-[18px]">sync</span> Generating...`;
            
            try {
                const res = await fetch('/api/reports/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        included_log_ids: selectedIds
                    })
                });

                if (res.ok) {
                    const data = await res.json();
                    
                    if (format === 'all') {
                        await loadReports();
                    } else if (data[format] && data[format].file_url) {
                        // Create temporary link to download immediately
                        const link = document.createElement('a');
                        link.href = data[format].file_url;
                        link.download = '';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        
                        await loadReports(); // Refresh side panel
                    }
                    closeExportModal();
                } else {
                    const data = await res.json();
                    alert(data.detail || "Failed to generate report.");
                }
            } catch (err) {
                alert("Network error occurred.");
            } finally {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        }

        // Load visualizer consistency pills
        async function loadVisualizer() {
            try {
                const res = await fetch('/api/visualizer/weekly');
                if (res.ok) {
                    const data = await res.json();
                    const streak = data.streak;
                    const daysData = data.days;
                    
                    // Render streak badge
                    const streakBadge = document.getElementById('streak-badge');
                    if (streak > 0) {
                        streakBadge.innerHTML = `🔥 ${streak}-Day Streak`;
                        streakBadge.classList.remove('hidden');
                    } else {
                        streakBadge.classList.add('hidden');
                    }

                    // Render grid (pills + labels together)
                    const gridContainer = document.getElementById('visualizer-grid');
                    gridContainer.innerHTML = daysData.map(d => {
                        const isToday = d.label === 'Today';
                        
                        // Select color based on status
                        let colorClass = 'bg-slate-200'; // Default empty
                        let statusText = 'No tasks scheduled';
                        
                        if (d.status === 'consistent') {
                            colorClass = 'bg-[#1b5e20]'; // Same consistent green as the lock button
                            statusText = 'Consistency followed (100%)';
                        } else if (d.status === 'missed') {
                            colorClass = 'bg-error';
                            statusText = `Missed tasks (${d.completed}/${d.total} completed)`;
                        } else if (d.status === 'pending') {
                            colorClass = 'bg-primary';
                            statusText = `Tasks active today (${d.completed}/${d.total} completed)`;
                        }
                        
                        const tooltip = `${d.day}: ${statusText}`;
                        
                        return `
                            <div class="flex flex-col items-center gap-3">
                                <div class="w-full h-2 rounded-full ${colorClass} transition-all duration-300 cursor-help" 
                                     title="${tooltip}"></div>
                                <span class="text-xs ${isToday ? 'text-primary font-bold' : 'text-secondary'}">
                                    ${d.day.substring(0, 1)}
                                </span>
                            </div>
                        `;
                    }).join('');
                }
            } catch (err) {
                console.error("Load weekly visualizer failed", err);
            }
        }

        // Logout action
        async function performLogout() {
            try {
                const response = await fetch('/api/auth/logout', { method: 'POST' });
                if (response.ok) {
                    window.location.href = '/login';
                }
            } catch (err) {
                console.error("Logout failed", err);
            }
        }

        document.getElementById('logout-btn').addEventListener('click', performLogout);
        document.getElementById('logout-btn-mobile').addEventListener('click', performLogout);

        // Run on startup
        initPage();
        
        // --- AI Handover Logic ---
        let handoverDraftData = null;
        
        function filterHandoverTasks() {
            const isUpdate = document.querySelector('input[name="handoverType"]:checked').value === "true";
            const listContainer = document.getElementById('handover-task-list');
            
            let filteredLogs = todayLogs;
            if (isUpdate) {
                filteredLogs = todayLogs.filter(l => l.category === 'Colleague Handover');
            }
            
            if (filteredLogs.length === 0) {
                listContainer.innerHTML = `<p class="text-sm text-secondary italic p-2">No tasks found for this mode.</p>`;
                return;
            }
            
            if (isUpdate) {
                document.getElementById('duration-container').classList.add('hidden');
            } else {
                document.getElementById('duration-container').classList.remove('hidden');
            }
            
            listContainer.innerHTML = filteredLogs.map(l => `
                <label class="flex items-start gap-3 p-2 hover:bg-surface-container rounded cursor-pointer border border-outline-variant/30 mb-1 flex-col">
                    <div class="flex items-start gap-3 w-full">
                        <input type="checkbox" name="handover_task_select" value="${l.id}" checked class="mt-1 text-primary h-4 w-4 rounded border-outline-variant focus:ring-primary">
                        <div class="flex-1">
                            <p class="text-sm font-semibold text-on-surface">${l.title || 'Untitled Task'}</p>
                            <p class="text-xs text-secondary truncate">${l.summary || 'No summary yet...'}</p>
                        </div>
                    </div>
                    ${!isUpdate ? `
                    <div class="w-full pl-7 mt-2">
                        <input type="text" id="assignee-${l.id}" placeholder="Assign to (e.g. Godwin)" class="w-full bg-surface border border-outline-variant rounded px-2 py-1 text-xs focus:ring-1 focus:ring-primary/50 focus:border-primary outline-none transition-all">
                    </div>` : ''}
                </label>
            `).join('');
        }
        
        
        function toggleReportTypeUI() {
            const reportType = document.querySelector('input[name="reportType"]:checked').value;
            if (reportType === 'subsidiary') {
                document.getElementById('duration-container').classList.add('hidden');
                document.getElementById('handover-location-container').classList.add('hidden');
                document.getElementById('handover-type-container').classList.add('hidden');
                document.getElementById('subsidiary-name-container').classList.remove('hidden');
            } else {
                document.getElementById('duration-container').classList.remove('hidden');
                document.getElementById('handover-location-container').classList.remove('hidden');
                document.getElementById('handover-type-container').classList.remove('hidden');
                document.getElementById('subsidiary-name-container').classList.add('hidden');
            }
        }

        function openHandoverModal() {
            document.getElementById('handover-modal').classList.remove('hidden');
            document.getElementById('handover-config-view').classList.remove('hidden');
            document.getElementById('handover-review-view').classList.add('hidden');
            document.getElementById('handover-loading-view').classList.add('hidden');
            document.getElementById('btn-generate-draft').classList.remove('hidden');
            document.getElementById('btn-export-docx').classList.add('hidden');
            filterHandoverTasks();
        }

        function closeHandoverModal() {
            document.getElementById('handover-modal').classList.add('hidden');
        }
        
        function selectAllHandoverTasks() {
            const checkboxes = document.querySelectorAll('input[name="handover_task_select"]');
            const anyUnchecked = Array.from(checkboxes).some(cb => !cb.checked);
            checkboxes.forEach(cb => cb.checked = anyUnchecked);
        }

        async function generateHandoverDraft() {
            const checkedBoxes = document.querySelectorAll('input[name="handover_task_select"]:checked');
            const selectedTasks = Array.from(checkedBoxes).map(cb => {
                const assigneeInput = document.getElementById(`assignee-${cb.value}`);
                return {
                    id: cb.value,
                    assignee: assigneeInput ? assigneeInput.value.trim() : ""
                };
            });
            
            if (selectedTasks.length === 0) {
                alert("Please select at least one task to hand over.");
                return;
            }
            
            const isUpdate = document.querySelector('input[name="handoverType"]:checked').value === "true";
            const durationText = document.getElementById('handover-duration') ? document.getElementById('handover-duration').value.trim() : "";
            
            document.getElementById('handover-config-view').classList.add('hidden');
            document.getElementById('btn-generate-draft').classList.add('hidden');
            document.getElementById('handover-loading-view').classList.remove('hidden');
            document.getElementById('handover-modal-title').textContent = "AI is generating draft...";
            
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
                
                const data = await res.json();
                document.getElementById('handover-loading-view').classList.add('hidden');
                
                if (res.ok) {
                    handoverDraftData = data.ai_data;
                    document.getElementById('handover-review-view').classList.remove('hidden');
                    document.getElementById('btn-export-docx').classList.remove('hidden');
                    document.getElementById('handover-modal-title').textContent = "Review & Edit AI Draft";
                    document.getElementById('handover-json-editor').value = JSON.stringify(handoverDraftData, null, 2);
                } else {
                    alert("Error: " + (data.detail || "Failed to generate draft"));
                    openHandoverModal();
                }
            } catch (err) {
                alert("Network error occurred.");
                openHandoverModal();
            }
        }

        async function exportHandoverDocx() {
            try {
                const editedJsonStr = document.getElementById('handover-json-editor').value;
                const editedData = JSON.parse(editedJsonStr);
                
                const isUpdate = document.querySelector('input[name="handoverType"]:checked').value === "true";
                const location = document.getElementById('handover-location').value.trim() || "Processing Centre";
                const todayStr = new Date().toISOString().split('T')[0];
                
                const btn = document.getElementById('btn-export-docx');
                btn.innerHTML = `<span class="material-symbols-outlined text-[14px] animate-spin">sync</span> Exporting...`;
                btn.disabled = true;
                
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
                
                if (res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    let filename = "handover.docx";
                    const disposition = res.headers.get('Content-Disposition');
                    if (disposition && disposition.indexOf('filename=') !== -1) {
                        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                        const matches = filenameRegex.exec(disposition);
                        if (matches != null && matches[1]) { 
                            filename = matches[1].replace(/['"]/g, '');
                        }
                    }
                    
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);
                    
                    btn.innerHTML = `<span class="material-symbols-outlined text-sm">download</span> Download DOCX`;
                    btn.disabled = false;
                    closeHandoverModal();
                } else {
                    const errorText = await res.text();
                    alert("Export failed. Server returned an error.");
                    btn.innerHTML = `<span class="material-symbols-outlined text-sm">download</span> Download DOCX`;
                    btn.disabled = false;
                }
            } catch (err) {
                alert("Invalid JSON syntax. Please fix the formatting before exporting.");
            }
        }

    