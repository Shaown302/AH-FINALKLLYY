// Dashboard Logic
async function fetchDashboardData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        const { stats, users, groups } = data;
        
        // Update Stats
        document.getElementById('stat-users').innerText = stats.users_count || 0;
        document.getElementById('stat-groups').innerText = stats.groups_count || 0;
        document.getElementById('stat-broadcasts').innerText = stats.broadcasts || 0;
        document.getElementById('stat-uptime').innerText = stats.uptime || '00:00:00';
        
        const statusDot = document.getElementById('bot-status-dot');
        const statusText = document.getElementById('bot-status-text');
        
        if (stats.status === 'online') {
            statusDot.classList.add('online');
            statusText.innerText = 'Online';
        } else {
            statusDot.classList.remove('online');
            statusText.innerText = 'Offline';
        }

        // Render Tables
        renderUserTable(users);
        renderGroupTable(groups);
        renderBannedTable(data.banned_users || []);

        // Update Access Toggle Button
        const accessBtn = document.getElementById('access-toggle-btn');
        if (accessBtn) {
            const isPublic = stats.global_access;
            accessBtn.innerHTML = isPublic ? '<i class="fas fa-lock-open"></i> Public: ON' : '<i class="fas fa-lock"></i> Public: OFF';
            accessBtn.className = isPublic ? 'btn btn-primary' : 'btn btn-secondary';
        }

        // Update Power Button
        const powerBtn = document.getElementById('power-btn');
        if (powerBtn) {
            const isOnline = stats.status === 'online';
            powerBtn.innerHTML = isOnline ? '<i class="fas fa-power-off"></i> Bot: ON' : '<i class="fas fa-power-off"></i> Bot: OFF';
            powerBtn.className = isOnline ? 'btn btn-success' : 'btn btn-danger';
        }
    } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
    }
}

function renderUserTable(users) {
    const container = document.getElementById('users-table-body');
    if (!container) return;
    
    container.innerHTML = users.length ? users.map(user => `
        <tr>
            <td><code>${user.id}</code></td>
            <td>${user.name || 'Unknown'}</td>
            <td>${user.username ? '@'+user.username : '-'}</td>
            <td><span class="badge">${user.joined_at || '-'}</span></td>
        </tr>
    `).join('') : '<tr><td colspan="4" class="empty">No users yet</td></tr>';
}

function renderGroupTable(groups) {
    const container = document.getElementById('groups-table-body');
    if (!container) return;

    container.innerHTML = groups.length ? groups.map(group => `
        <tr>
            <td><code>${group.id}</code></td>
            <td>${group.title || 'Unknown'}</td>
            <td><span class="badge type">${group.type || 'group'}</span></td>
            <td><span class="badge">${group.added_at || '-'}</span></td>
        </tr>
    `).join('') : '<tr><td colspan="4" class="empty">No groups yet</td></tr>';
}

function renderBannedTable(banned) {
    const container = document.getElementById('banned-table-body');
    if (!container) return;

    container.innerHTML = banned.length ? banned.map(uid => `
        <tr>
            <td><code>${uid}</code></td>
            <td><span class="badge danger">BANNED</span></td>
        </tr>
    `).join('') : '<tr><td colspan="2" class="empty">No banned users</td></tr>';
}


async function fetchLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        const container = document.getElementById('logs-container');
        
        container.innerHTML = logs.map(log => {
            let type = 'info';
            if (log.toLowerCase().includes('error')) type = 'error';
            if (log.toLowerCase().includes('warn')) type = 'warn';
            if (log.toLowerCase().includes('system')) type = 'system';
            
            return `<div class="log-entry ${type}">${log}</div>`;
        }).join('');
        
        container.scrollTop = container.scrollHeight;
    } catch (error) {
        console.error('Failed to fetch logs:', error);
    }
}

async function sendBroadcast(target) {
    const msg = document.getElementById('broadcast-msg').value;
    if (!msg) return alert('Please enter a message!');
    
    try {
        const response = await fetch('/api/broadcast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, message: msg })
        });
        const result = await response.json();
        if (result.success) {
            alert('Broadcast started successfully!');
            document.getElementById('broadcast-msg').value = '';
        } else {
            alert('Failed to send broadcast: ' + result.error);
        }
    } catch (error) {
        alert('Error sending broadcast');
    }
}

async function controlBot(action) {
    if (action !== 'toggle_access' && !confirm(`Are you sure you want to ${action.replace('_', ' ')}?`)) return;
    
    try {
        const response = await fetch('/api/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        const result = await response.json();
        if (result.success) {
            if (action === 'toggle_access') {
                fetchDashboardData();
            } else if (action === 'delete_broadcast') {
                alert(`✅ Cleanup Complete!\n🗑️ Deleted: ${result.deleted}\n⚠️ Failed: ${result.failed}`);
            } else {
                alert('Action completed: ' + action);
            }
        }
    } catch (error) {
        alert('Error executing control action');
    }
}

// Auto-update every 10 seconds (optimized)
setInterval(fetchDashboardData, 10000);
setInterval(fetchLogs, 10000);

// Initial call
fetchDashboardData();
fetchLogs();

