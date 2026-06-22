let chartInstances = {};

function destroyChart(key) {
    if (chartInstances[key]) {
        chartInstances[key].destroy();
        delete chartInstances[key];
    }
}

function createBarChart(canvasId, labels, values, label, color = '#3b82f6') {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{ label, data: values, backgroundColor: color, borderColor: color, borderWidth: 1, borderRadius: 3 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f0f0f0' } },
                x: { grid: { display: false }, ticks: { maxRotation: 45, font: { size: 11 } } }
            }
        }
    });
}

function createHorizBarChart(canvasId, labels, values, label, color = '#3b82f6') {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{ label, data: values, backgroundColor: color, borderColor: color, borderWidth: 1, borderRadius: 3 }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { beginAtZero: true, grid: { color: '#f0f0f0' } },
                y: { grid: { display: false }, ticks: { font: { size: 11 } } }
            }
        }
    });
}

function createLineChart(canvasId, labels, values, label, color = '#3b82f6', fill = false) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label, data: values, borderColor: color, backgroundColor: color + '22',
                borderWidth: 2, pointRadius: 3, pointHoverRadius: 5, fill
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f0f0f0' } },
                x: { grid: { display: false }, ticks: { maxRotation: 45, font: { size: 11 } } }
            }
        }
    });
}

function createPieChart(canvasId, labels, values, colors) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{ data: values, backgroundColor: colors, borderWidth: 2, borderColor: '#fff' }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { boxWidth: 12, padding: 12, font: { size: 11 } }
                }
            }
        }
    });
}
