// Global state
let complianceChart = null;
let violationsChart = null;
let entityChart = null;
let currentData = null;
let allTickets = [];
let currentFilteredTickets = [];

// API Base URL
const API_BASE = 'http://localhost:5000/api';

// GLPI Base URL (will be loaded from API)
let GLPI_BASE_URL = '';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    setupEventListeners();
    loadGLPIConfig();
    loadEntities();
});

function initializeDashboard() {
    // Set default dates (last 30 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);

    document.getElementById('startDate').valueAsDate = startDate;
    document.getElementById('endDate').valueAsDate = endDate;

    // Load theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function setupEventListeners() {
    // Dark mode toggle
    document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);

    // Load data button
    document.getElementById('loadDataButton').addEventListener('click', loadComplianceData);

    // Refresh button
    document.getElementById('refreshButton').addEventListener('click', () => {
        loadComplianceData();
    });

    // Export button
    document.getElementById('exportButton').addEventListener('click', exportToCSV);

    // Export Table Button
    const exportTableBtn = document.getElementById('exportTableButton');
    if (exportTableBtn) {
        exportTableBtn.addEventListener('click', exportTableToCSV);
    }

    // Enter key on date inputs
    document.getElementById('startDate').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loadComplianceData();
    });

    document.getElementById('endDate').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loadComplianceData();
    });

    // Filter Buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active class from all
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            // Add active to clicked
            e.target.classList.add('active');
            // Filter
            filterTickets(e.target.dataset.filter);
        });
    });
}

function toggleDarkMode() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);

    // Update charts with new theme
    if (currentData) {
        updateCharts(currentData);
    }
}

function updateThemeIcon(theme) {
    const button = document.getElementById('darkModeToggle');
    const icon = theme === 'dark'
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    button.innerHTML = icon;
}

function showLoading(show = true) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

async function loadGLPIConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();

        if (data.success) {
            GLPI_BASE_URL = data.glpi_base_url;
            console.log('GLPI Base URL loaded:', GLPI_BASE_URL);
        }
    } catch (error) {
        console.error('Error loading GLPI config:', error);
    }
}

async function loadEntities() {
    try {
        const response = await fetch(`${API_BASE}/entities`);
        const data = await response.json();

        if (data.success) {
            const select = document.getElementById('entityFilter');
            select.innerHTML = '<option value="">All Entities</option>';

            data.entities.forEach(entity => {
                const option = document.createElement('option');
                option.value = entity.id;
                option.textContent = entity.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading entities:', error);
        showNotification('Failed to load entities', 'error');
    }
}

async function loadComplianceData() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const entityId = document.getElementById('entityFilter').value;

    if (!startDate || !endDate) {
        showNotification('Please select start and end dates', 'warning');
        return;
    }

    showLoading(true);

    try {
        let url = `${API_BASE}/compliance-data?start_date=${startDate}&end_date=${endDate}`;
        if (entityId) {
            url += `&entity_id=${entityId}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            currentData = data;
            updateDashboard(data);
            updateLastUpdate();
            showNotification('Data loaded successfully', 'success');
        } else {
            showNotification(data.error || 'Failed to load data', 'error');
        }
    } catch (error) {
        console.error('Error loading compliance data:', error);
        showNotification('Failed to load compliance data', 'error');
    } finally {
        showLoading(false);
    }
}

function updateDashboard(data) {
    // Update summary cards
    document.getElementById('totalTickets').textContent = data.summary.total_tickets.toLocaleString();
    document.getElementById('slaTotalTickets').textContent = data.summary.total_sla_tickets.toLocaleString();
    document.getElementById('slaActive').textContent = data.summary.sla_active.toLocaleString();
    document.getElementById('slaOk').textContent = data.summary.sla_ok.toLocaleString();
    document.getElementById('slaViolated').textContent = data.summary.sla_violated.toLocaleString();
    document.getElementById('complianceRate').textContent = data.summary.compliance_rate.toFixed(1) + '%';

    // Update charts
    updateCharts(data);

    // Update tickets table
    allTickets = data.tickets || [];
    currentFilteredTickets = allTickets;
    // Reset filters
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');

    updateTicketTable(allTickets);
}

function updateCharts(data) {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#cbd5e1' : '#6b7280';
    const gridColor = isDark ? '#334155' : '#e5e7eb';

    // Compliance Overview Chart (Pie)
    const complianceCtx = document.getElementById('complianceChart').getContext('2d');

    if (complianceChart) {
        complianceChart.destroy();
    }

    complianceChart = new Chart(complianceCtx, {
        type: 'doughnut',
        data: {
            labels: ['SLA Compliant', 'SLA Violated'],
            datasets: [{
                data: [data.summary.sla_ok, data.summary.sla_violated],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: textColor,
                        padding: 15,
                        font: {
                            size: 13,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });

    // Top Violations Chart (Bar)
    const violationsCtx = document.getElementById('violationsChart').getContext('2d');

    if (violationsChart) {
        violationsChart.destroy();
    }

    // Get top 10 entities by violations
    const topViolations = data.entities
        .sort((a, b) => b.sla_violated - a.sla_violated)
        .slice(0, 10);

    violationsChart = new Chart(violationsCtx, {
        type: 'bar',
        data: {
            labels: topViolations.map(e => e.entity.length > 30 ? e.entity.substring(0, 30) + '...' : e.entity),
            datasets: [{
                label: 'Violations',
                data: topViolations.map(e => e.sla_violated),
                backgroundColor: 'rgba(239, 68, 68, 0.8)',
                borderColor: 'rgba(239, 68, 68, 1)',
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Violations: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: textColor,
                        precision: 0
                    },
                    grid: {
                        color: gridColor
                    }
                },
                x: {
                    ticks: {
                        color: textColor,
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Entity Breakdown Chart (Horizontal Bar)
    const entityCtx = document.getElementById('entityChart').getContext('2d');

    if (entityChart) {
        entityChart.destroy();
    }

    // Get top 15 entities by total tickets
    const topEntities = data.entities
        .sort((a, b) => b.total - a.total)
        .slice(0, 15);

    entityChart = new Chart(entityCtx, {
        type: 'bar',
        data: {
            labels: topEntities.map(e => e.entity.length > 40 ? e.entity.substring(0, 40) + '...' : e.entity),
            datasets: [
                {
                    label: 'SLA Compliant',
                    data: topEntities.map(e => e.sla_ok),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2,
                    borderRadius: 6
                },
                {
                    label: 'SLA Violated',
                    data: topEntities.map(e => e.sla_violated),
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 2,
                    borderRadius: 6
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: textColor,
                        padding: 15,
                        font: {
                            size: 13,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.x}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        color: textColor,
                        precision: 0
                    },
                    grid: {
                        color: gridColor
                    }
                },
                y: {
                    stacked: true,
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateTicketTable(tickets) {
    const tbody = document.getElementById('ticketsTableBody');
    const count = document.getElementById('ticketCount');

    count.textContent = tickets.length;

    if (tickets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No tickets found for the selected filter.</td></tr>';
        return;
    }

    tbody.innerHTML = tickets.map(t => {
        // Status Badge
        let statusBadge = '';
        if (t.status === 'violated') {
            statusBadge = '<span class="badge" style="background: var(--gradient-danger);">Violated</span>';
        } else if (t.status === 'compliant') {
            statusBadge = '<span class="badge" style="background: var(--gradient-success);">Compliant</span>';
        } else {
            statusBadge = '<span class="badge" style="background: var(--gradient-info);">Active</span>';
        }

        // GLPI ticket URL oluştur
        const ticketUrl = GLPI_BASE_URL ? `${GLPI_BASE_URL}/front/ticket.form.php?id=${t.ticket_id}` : '#';

        return `
            <tr>
                <td>${escapeHtml(t.entity)}</td>
                <td><a href="${ticketUrl}" target="_blank" class="ticket-link" title="Open ticket in GLPI"><strong>#${t.ticket_id}</strong></a></td>
                <td>${escapeHtml(t.ticket_name)}</td>
                <td>${formatDate(t.date)}</td>
                <td>${statusBadge}</td>
                <td>${escapeHtml(t.sla_names || '-')}</td>
            </tr>
        `;
    }).join('');
}

function filterTickets(filter) {
    let filtered = [];
    if (filter === 'all') {
        filtered = allTickets;
    } else {
        filtered = allTickets.filter(t => t.status === filter);
    }
    currentFilteredTickets = filtered;
    updateTicketTable(filtered);
}

function exportTableToCSV() {
    if (!currentFilteredTickets || currentFilteredTickets.length === 0) {
        showNotification('No data to export', 'warning');
        return;
    }

    // Headers
    const headers = ['Entity', 'Ticket ID', 'Ticket Name', 'Date', 'Status', 'SLAs'];

    // Rows
    const rows = currentFilteredTickets.map(t => [
        t.entity,
        t.ticket_id,
        t.ticket_name,
        t.date,
        t.status.charAt(0).toUpperCase() + t.status.slice(1),
        t.sla_names || '-'
    ]);

    // Combine
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    // Create Blob and Download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    // Filename with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    link.setAttribute('href', url);
    link.setAttribute('download', `table_export_${timestamp}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showNotification('Table data exported successfully', 'success');
}

function exportToCSV() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!startDate || !endDate) {
        showNotification('Please select start and end dates', 'warning');
        return;
    }

    const url = `${API_BASE}/export/csv?start_date=${startDate}&end_date=${endDate}`;
    window.open(url, '_blank');
    showNotification('Exporting to CSV...', 'info');
}

function updateLastUpdate() {
    const now = new Date();
    const formatted = now.toLocaleString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('lastUpdate').textContent = formatted;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // Simple console notification for now
    // You can implement a toast notification system here
    const emoji = {
        'success': '✓',
        'error': '✗',
        'warning': '⚠',
        'info': 'ℹ'
    };

    console.log(`${emoji[type]} ${message}`);

    // Optional: Create a toast notification
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? 'var(--gradient-danger)' : type === 'success' ? 'var(--gradient-success)' : type === 'warning' ? 'var(--gradient-warning)' : 'var(--gradient-info)'};
        color: white;
        padding: 16px 24px;
        border-radius: 10px;
        box-shadow: var(--shadow-lg);
        z-index: 2000;
        animation: slideIn 0.3s ease;
        font-weight: 600;
    `;
    toast.textContent = `${emoji[type]} ${message}`;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
