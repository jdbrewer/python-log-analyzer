// src/web/static/js/dashboard.js
let currentPage = 1;
const perPage = 50;

// Function to load and display statistics
async function loadStats() {
    console.log('Loading stats...');
    try {
        const response = await fetch('/api/stats');
        console.log('Stats response:', response);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Stats data:', data);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update stats cards
        document.getElementById('total-logs').textContent = data.total_logs.toLocaleString();
        document.getElementById('error-rate').textContent = `${data.error_rate.toFixed(2)}%`;
        document.getElementById('busiest-hour').textContent = 
            `${data.busiest_hour[0]}:00 (${data.busiest_hour[1].toLocaleString()} logs)`;
        
        // Load anomalies count
        const anomaliesResponse = await fetch('/api/anomalies');
        if (!anomaliesResponse.ok) {
            throw new Error(`HTTP error! status: ${anomaliesResponse.status}`);
        }
        const anomaliesData = await anomaliesResponse.json();
        document.getElementById('anomalies-count').textContent = 
            `${anomaliesData.length} anomalies detected`;
        
        // Update component dropdown
        const componentSelect = document.getElementById('component');
        componentSelect.innerHTML = '<option value="">All Components</option>';
        data.components.forEach(comp => {
            const option = document.createElement('option');
            option.value = comp.component;
            option.textContent = comp.component;
            componentSelect.appendChild(option);
        });

        // Load charts
        await loadCharts();
    } catch (error) {
        console.error('Error loading stats:', error);
        // Show error in the stats cards
        document.getElementById('total-logs').textContent = 'Error';
        document.getElementById('error-rate').textContent = 'Error';
        document.getElementById('busiest-hour').textContent = 'Error';
        document.getElementById('anomalies-count').textContent = 'Error';
    }
}

// Function to format date for API
function formatDateForAPI(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toISOString().split('.')[0]; // Format: YYYY-MM-DDTHH:mm:ss
}

// Function to load and display logs
async function loadLogs() {
    console.log('Loading logs...');
    const level = document.getElementById('level').value;
    const component = document.getElementById('component').value;
    const startDate = formatDateForAPI(document.getElementById('start-date').value);
    const endDate = formatDateForAPI(document.getElementById('end-date').value);
    
    try {
        const url = `/api/logs?page=${currentPage}&per_page=${perPage}` +
            `&level=${level}&component=${component}` +
            `&start_date=${startDate}&end_date=${endDate}`;
        console.log('Fetching logs from:', url);
        
        const response = await fetch(url);
        console.log('Logs response:', response);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Logs data:', data);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update table
        const tbody = document.getElementById('log-table');
        tbody.innerHTML = '';
        
        if (data.logs && data.logs.length > 0) {
            data.logs.forEach(log => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${log.timestamp}</td>
                    <td class="log-level-${log.level.toLowerCase()}">${log.level}</td>
                    <td>${log.component}</td>
                    <td>${log.message}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="4" class="text-center">No logs found</td>';
            tbody.appendChild(tr);
        }
        
        // Update pagination
        updatePagination(data.total_pages);
    } catch (error) {
        console.error('Error loading logs:', error);
        const tbody = document.getElementById('log-table');
        tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">Error loading logs: ${error.message}</td></tr>`;
    }
}

// Function to update pagination controls
function updatePagination(totalPages) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    // Previous button
    const prevLi = document.createElement("li");
    prevLi.className = `page-item${currentPage === 1 ? " disabled" : ""}`;
    prevLi.innerHTML = `<a class="page-link" href="#" tabindex="-1" aria-disabled="${currentPage === 1}" onclick="if(currentPage > 1) changePage(${currentPage - 1}); return false;">Previous</a>`;
    pagination.appendChild(prevLi);

    // Always show first page
    pagination.appendChild(createPageItem(1, "1", currentPage === 1));

    // Show ellipsis if needed
    if (currentPage > 4) {
        const li = document.createElement("li");
        li.className = "page-item disabled";
        li.innerHTML = `<span class="page-link">...</span>`;
        pagination.appendChild(li);
    }

    // Show pages around current page
    for (let i = Math.max(2, currentPage - 2); i <= Math.min(totalPages - 1, currentPage + 2); i++) {
        if (i === 1 || i === totalPages) continue; // already shown
        pagination.appendChild(createPageItem(i, i, currentPage === i));
    }

    // Show ellipsis if needed
    if (currentPage < totalPages - 3) {
        const li = document.createElement("li");
        li.className = "page-item disabled";
        li.innerHTML = `<span class="page-link">...</span>`;
        pagination.appendChild(li);
    }

    // Always show last page if more than one page
    if (totalPages > 1) {
        pagination.appendChild(createPageItem(totalPages, totalPages, currentPage === totalPages));
    }

    // Next button
    const nextLi = document.createElement("li");
    nextLi.className = `page-item${currentPage === totalPages ? " disabled" : ""}`;
    nextLi.innerHTML = `<a class="page-link" href="#" tabindex="-1" aria-disabled="${currentPage === totalPages}" onclick="if(currentPage < totalPages) changePage(${currentPage + 1}); return false;">Next</a>`;
    pagination.appendChild(nextLi);

    // Helper function
    function createPageItem(page, text = null, active = false, disabled = false) {
        const li = document.createElement("li");
        li.className = `page-item${active ? " active" : ""}${disabled ? " disabled" : ""}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="changePage(${page}); return false;">${text || page}</a>`;
        return li;
    }
}

// Function to change page
function changePage(page) {
    currentPage = page;
    loadLogs();
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadLogs();
    
    // Set up filter form
    document.getElementById('filter-form').addEventListener('submit', (e) => {
        e.preventDefault();
        currentPage = 1;
        loadLogs();
    });
});

async function loadCharts() {
    await Promise.all([
        loadErrorTimeSeries(),
        loadHourlyDistribution(),
        loadComponentErrorRates(),
        loadLogLevelDistribution()
    ]);
}

async function loadErrorTimeSeries() {
    try {
        const response = await fetch('/api/time-series');
        const data = await response.json();
        
        const ctx = document.getElementById('errorTimeSeriesChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.timestamp),
                datasets: [{
                    label: 'Error Count',
                    data: data.map(d => d.count),
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Error Count'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading time series:', error);
    }
}

async function loadHourlyDistribution() {
    try {
        const response = await fetch('/api/hourly-distribution');
        const data = await response.json();
        
        const ctx = document.getElementById('hourlyDistributionChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => `${d.hour}:00`),
                datasets: [{
                    label: 'Log Count',
                    data: data.map(d => d.count),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Hour of Day'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Log Count'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading hourly distribution:', error);
    }
}

async function loadComponentErrorRates() {
    try {
        const response = await fetch('/api/component-stats');
        const data = await response.json();
        
        const ctx = document.getElementById('componentErrorChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.component),
                datasets: [{
                    label: 'Error Rate (%)',
                    data: data.map(d => d.error_rate),
                    backgroundColor: 'rgba(255, 159, 64, 0.5)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Error Rate (%)'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading component error rates:', error);
    }
}

async function loadLogLevelDistribution() {
    try {
        const response = await fetch('/api/level-distribution');
        const data = await response.json();
        
        const ctx = document.getElementById('logLevelChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.map(d => d.level),
                datasets: [{
                    data: data.map(d => d.count),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(153, 102, 255, 0.5)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading log level distribution:', error);
    }
}