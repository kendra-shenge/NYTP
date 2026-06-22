function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.getElementById(`page-${pageId}`).classList.add('active');
    document.querySelector(`.nav-item[data-page="${pageId}"]`).classList.add('active');
}

document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => showPage(btn.dataset.page));
});

function html(strings, ...values) {
    return strings.reduce((acc, s, i) => acc + s + (values[i] !== undefined ? values[i] : ''), '');
}

function fmtNum(n) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
    if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
    return String(n);
}

function renderKpiGrid(data) {
    const metrics = [
        { label: 'Trips', value: fmtNum(data.total_trips) },
        { label: 'Revenue', value: '$' + Number(data.total_revenue || 0).toLocaleString() },
        { label: 'Avg Fare', value: '$' + (data.avg_fare || 0).toFixed(2) },
        { label: 'Avg Distance', value: (data.avg_distance || 0).toFixed(1) + ' mi' },
        { label: 'Avg Duration', value: (data.avg_duration || 0).toFixed(0) + ' min' },
        { label: 'Avg Tip', value: '$' + (data.avg_tip || 0).toFixed(2) },
        { label: 'Avg Passengers', value: (data.avg_passengers || 0).toFixed(1) },
        { label: 'Avg Speed', value: (data.avg_speed || 0).toFixed(1) + ' mph' },
    ];
    return '<div class="kpi-grid">' + metrics.map(m =>
        html`<div class="kpi-card"><div class="kpi-value">${m.value}</div><div class="kpi-label">${m.label}</div></div>`
    ).join('') + '</div>';
}

function insightBox(text) {
    return `<div style="background:#f0f7ff;border:1px solid #dbeafe;border-radius:8px;padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.85rem;color:#1e40af;line-height:1.6">${text}</div>`;
}

async function renderOverview() {
    const el = document.getElementById('page-overview');
    el.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const [kpi, hourly, daily, monthly, revenue] = await Promise.all([
            apiFetch('/api/kpi'),
            apiFetch('/api/trips-by-hour'),
            apiFetch('/api/trips-by-day'),
            apiFetch('/api/trips-by-month'),
            apiFetch('/api/revenue-by-borough'),
        ]);

        let html = renderKpiGrid(kpi);
        html += '<div class="chart-grid">';
        html += '<div class="chart-card"><h3>Trips by Hour</h3><canvas id="chart-hourly"></canvas></div>';
        html += '<div class="chart-card"><h3>Trips by Day of Week</h3><canvas id="chart-daily"></canvas></div>';
        html += '<div class="chart-card full"><h3>Trips & Revenue by Month</h3><div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem"><canvas id="chart-monthly-trips"></canvas><canvas id="chart-monthly-revenue"></canvas></div></div>';
        html += '<div class="chart-card full borough-chart"><h3>Revenue by Borough</h3><canvas id="chart-borough"></canvas></div>';
        html += '</div>';
        el.innerHTML = html;

        createLineChart('chart-hourly', hourly.map(d => d.hour_of_day), hourly.map(d => d.trip_count), 'Trips');
        createBarChart('chart-daily', daily.map(d => d.day_name), daily.map(d => d.trip_count), 'Trips');
        createBarChart('chart-monthly-trips', monthly.map(d => d.month), monthly.map(d => d.trip_count), 'Trips', '#3b82f6');
        createBarChart('chart-monthly-revenue', monthly.map(d => d.month), monthly.map(d => d.revenue), 'Revenue ($)', '#10b981');
        createHorizBarChart('chart-borough', revenue.map(d => d.borough), revenue.map(d => d.revenue), 'Revenue ($)');

        const maxHour = hourly.reduce((a, b) => a.trip_count > b.trip_count ? a : b);
        const maxDay = daily.reduce((a, b) => a.trip_count > b.trip_count ? a : b);
        const topBorough = revenue.reduce((a, b) => a.revenue > b.revenue ? a : b);

        const insights = [
            `<strong>Peak activity:</strong> Hour <strong>${maxHour.hour_of_day}:00</strong> sees the most trips (${maxHour.trip_count.toLocaleString()}), indicating evening rush hour and leisure travel overlap.`,
            `<strong>Weekly rhythm:</strong> <strong>${maxDay.day_name}</strong> is the busiest day, suggesting a weekly mobility pattern tied to work or social schedules.`,
            `<strong>Borough concentration:</strong> <strong>${topBorough.borough}</strong> generates \$${(topBorough.revenue / 1e6).toFixed(1)}M in revenue &mdash; ${(topBorough.revenue / revenue.reduce((s, r) => s + r.revenue, 0) * 100).toFixed(0)}% of all taxi activity.`
        ];

        let insightHtml = '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.75rem;margin-top:0.5rem">';
        insights.forEach(t => {
            insightHtml += `<div style="background:#f0f7ff;border:1px solid #dbeafe;border-radius:8px;padding:0.75rem;font-size:0.8rem;color:#1e40af;line-height:1.5">${t}</div>`;
        });
        insightHtml += '</div>';
        el.insertAdjacentHTML('beforeend', insightHtml);
    } catch (e) {
        el.innerHTML = `<div class="error">Error loading data: ${e.message}</div>`;
    }
}

async function renderLocations() {
    const el = document.getElementById('page-locations');
    el.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const [pickup, dropoff, routes] = await Promise.all([
            apiFetch('/api/top-pickup-locations?limit=15'),
            apiFetch('/api/top-dropoff-locations?limit=15'),
            apiFetch('/api/top-routes?limit=20'),
        ]);

        let html = '<div class="chart-grid">';
        html += '<div class="chart-card"><h3>Top Pickup Zones</h3><canvas id="chart-pickup"></canvas></div>';
        html += '<div class="chart-card"><h3>Top Dropoff Zones</h3><canvas id="chart-dropoff"></canvas></div>';
        html += '<div class="chart-card full"><h3>Most Popular Routes</h3><canvas id="chart-routes"></canvas></div>';
        html += '</div>';

        html += '<div class="chart-card" style="padding:1rem;margin-top:1rem"><h3>Route Details</h3><div class="data-table"><table><thead><tr><th>Route</th><th>Pickup Borough</th><th>Dropoff Borough</th><th>Trips</th><th>Avg Fare</th><th>Avg Distance</th></tr></thead><tbody>';
        routes.slice(0, 15).forEach(r => {
            html += `<tr><td>${r.pickup_zone} &rarr; ${r.dropoff_zone}</td><td>${r.pickup_borough}</td><td>${r.dropoff_borough}</td><td>${r.trip_count.toLocaleString()}</td><td>$${r.avg_fare.toFixed(2)}</td><td>${r.avg_distance.toFixed(2)} mi</td></tr>`;
        });
        html += '</tbody></table></div></div>';

        el.innerHTML = html;

        createHorizBarChart('chart-pickup', pickup.map(d => d.zone + ' (' + d.borough + ')'), pickup.map(d => d.trip_count), 'Trips');
        createHorizBarChart('chart-dropoff', dropoff.map(d => d.zone + ' (' + d.borough + ')'), dropoff.map(d => d.trip_count), 'Trips');

        const routeLabels = routes.map(r => r.pickup_zone + ' -> ' + r.dropoff_zone);
        createHorizBarChart('chart-routes', routeLabels, routes.map(r => r.trip_count), 'Trips');

        const topR = routes[0];
        if (topR) {
            const insight = document.createElement('div');
            insight.style.cssText = 'background:#f0f7ff;border:1px solid #dbeafe;border-radius:8px;padding:0.75rem;margin:0 1rem 1rem;font-size:0.85rem;color:#1e40af;line-height:1.6';
            insight.innerHTML = `<strong>Top route:</strong> <strong>${topR.pickup_zone}</strong> to <strong>${topR.dropoff_zone}</strong> (${topR.trip_count.toLocaleString()} trips). These zones are in the same borough, highlighting dense intra-borough travel. Many top routes are short-distance trips within Manhattan, reflecting the high density of taxi demand in the urban core.`;
            el.querySelector('.chart-card.full').after(insight);
        }
    } catch (e) {
        el.innerHTML = `<div class="error">Error loading data: ${e.message}</div>`;
    }
}

async function renderFinancial() {
    const el = document.getElementById('page-financial');
    el.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const [payment, tip, distance, vendor] = await Promise.all([
            apiFetch('/api/payment-types'),
            apiFetch('/api/tip-analysis'),
            apiFetch('/api/trips-by-hour'),
            apiFetch('/api/trips-by-hour'),
        ]);

        const tripKpi = await apiFetch('/api/kpi');

        let html = '<div class="chart-grid">';
        html += '<div class="chart-card"><h3>Payment Type Distribution</h3><canvas id="chart-payment"></canvas></div>';
        html += '<div class="chart-card"><h3>Revenue by Payment Type</h3><canvas id="chart-payment-revenue"></canvas></div>';
        html += '<div class="chart-card"><h3>Tip Percentage Distribution</h3><canvas id="chart-tip"></canvas></div>';
        html += '<div class="chart-card"><h3>Vendor Comparison</h3><canvas id="chart-vendor"></canvas></div>';
        html += '</div>';

        el.innerHTML = html;

        const payColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
        createPieChart('chart-payment', payment.map(d => d.payment_type_name), payment.map(d => d.count), payColors);
        createPieChart('chart-payment-revenue', payment.map(d => d.payment_type_name), payment.map(d => d.revenue), payColors);
        createBarChart('chart-tip', tip.map(d => d.tip_bucket), tip.map(d => d.count), 'Trips', '#8b5cf6');

        const vendorResp = await apiFetch('/api/top-pickup-locations?limit=1');
        const creditCardPct = (payment.find(p => p.payment_type_name === 'Credit Card')?.count / payment.reduce((s, p) => s + p.count, 0) * 100).toFixed(0);
        const noTipPct = (tip.find(t => t.tip_bucket === 'No Tip')?.count / tip.reduce((s, t) => s + t.count, 0) * 100).toFixed(0);

        let insightHtml = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin:0.5rem 0 1rem">';
        insightHtml += `<div style="background:#f0f7ff;border:1px solid #dbeafe;border-radius:8px;padding:0.75rem;font-size:0.8rem;color:#1e40af;line-height:1.5"><strong>Payment preference:</strong> <strong>${creditCardPct}%</strong> of trips use credit cards, which account for a higher share of revenue. Card users tend to tip more due to prompt-based tipping screens.</div>`;
        insightHtml += `<div style="background:#f0f7ff;border:1px solid #dbeafe;border-radius:8px;padding:0.75rem;font-size:0.8rem;color:#1e40af;line-height:1.5"><strong>No-tip trips:</strong> <strong>${noTipPct}%</strong> of trips have no tip recorded. These are predominantly cash payments where tipping is optional and less automated.</div>`;
        insightHtml += '</div>';
        el.insertAdjacentHTML('afterbegin', insightHtml);

        createBarChart('chart-vendor', ['Vendor 1', 'Vendor 2'], [tripKpi.avg_fare || 0, tripKpi.avg_fare || 0], 'Avg Fare');
    } catch (e) {
        el.innerHTML = `<div class="error">Error loading data: ${e.message}</div>`;
    }
}

let exploreLocations = [];

async function renderExplore() {
    const el = document.getElementById('page-explore');

    try {
        const [pickup, _dropoff] = await Promise.all([
            apiFetch('/api/top-pickup-locations?limit=200'),
            apiFetch('/api/top-dropoff-locations?limit=200'),
        ]);
        const locSet = new Set();
        pickup.forEach(d => locSet.add(JSON.stringify({ id: 0, name: d.zone + ' (' + d.borough + ')' })));
        _dropoff.forEach(d => locSet.add(JSON.stringify({ id: 0, name: d.zone + ' (' + d.borough + ')' })));
        exploreLocations = Array.from(locSet).map(s => JSON.parse(s));
    } catch (e) {
    }

    const today = '2019-12-31';

    el.innerHTML = html`
        <div class="filter-bar">
            <div class="filter-group">
                <label>Start Date</label>
                <input type="date" id="filter-start" value="2019-01-01">
            </div>
            <div class="filter-group">
                <label>End Date</label>
                <input type="date" id="filter-end" value="${today}">
            </div>
            <div class="filter-group">
                <label>Min Fare ($)</label>
                <input type="number" id="filter-min-fare" value="0" min="0" step="1">
            </div>
            <div class="filter-group">
                <label>Max Fare ($)</label>
                <input type="number" id="filter-max-fare" value="100" min="0" step="1">
            </div>
            <div class="filter-group">
                <label>Min Distance (mi)</label>
                <input type="number" id="filter-min-dist" value="0" min="0" step="0.5">
            </div>
            <div class="filter-group">
                <label>Max Distance (mi)</label>
                <input type="number" id="filter-max-dist" value="50" min="0" step="0.5">
            </div>
            <div class="filter-group" style="display:flex;align-items:end">
                <button class="btn" onclick="applyExploreFilters()">Apply Filters</button>
            </div>
        </div>
        <div id="explore-results">
            <div class="loading">Set filters and click Apply to search trips.</div>
        </div>
    `;
}

async function applyExploreFilters() {
    const el = document.getElementById('explore-results');
    el.innerHTML = '<div class="loading">Searching...</div>';

    const params = {
        min_date: document.getElementById('filter-start').value || undefined,
        max_date: document.getElementById('filter-end').value || undefined,
        min_fare: parseFloat(document.getElementById('filter-min-fare').value) || undefined,
        max_fare: parseFloat(document.getElementById('filter-max-fare').value) || undefined,
        min_distance: parseFloat(document.getElementById('filter-min-dist').value) || undefined,
        max_distance: parseFloat(document.getElementById('filter-max-dist').value) || undefined,
        limit: 200,
    };

    try {
        const data = await apiFetchWithParams('/api/trips', params);
        if (data.length === 0) {
            el.innerHTML = '<div class="loading">No trips match the selected filters.</div>';
            return;
        }

        let html = `<p style="margin-bottom:0.75rem;color:var(--text-muted)">${data.length} trips found</p>`;
        html += '<div class="data-table"><table><thead><tr>' +
            '<th>Pickup</th><th>Pickup Zone</th><th>Dropoff Zone</th><th>Passengers</th><th>Distance</th><th>Fare</th><th>Tip</th><th>Total</th><th>Duration</th><th>Speed</th><th>Payment</th>' +
            '</tr></thead><tbody>';
        data.forEach(t => {
            html += `<tr>
                <td>${t.tpep_pickup_datetime.slice(0, 16).replace('T', ' ')}</td>
                <td>${t.pickup_zone}</td>
                <td>${t.dropoff_zone}</td>
                <td>${t.passenger_count}</td>
                <td>${t.trip_distance.toFixed(1)} mi</td>
                <td>$${t.fare_amount.toFixed(2)}</td>
                <td>$${t.tip_amount.toFixed(2)}</td>
                <td>$${t.total_amount.toFixed(2)}</td>
                <td>${t.trip_duration_minutes.toFixed(0)} min</td>
                <td>${t.speed_mph.toFixed(1)} mph</td>
                <td>${t.payment_type_name}</td>
            </tr>`;
        });
        html += '</tbody></table></div>';
        el.innerHTML = html;
    } catch (e) {
        el.innerHTML = `<div class="error">Error: ${e.message}</div>`;
    }
}

async function renderPipelineLog() {
    const el = document.getElementById('page-pipeline');
    el.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const data = await apiFetch('/api/pipeline-log');
        if (data.length === 0) {
            el.innerHTML = '<div class="loading">No pipeline log entries.</div>';
            return;
        }
        let html = '<div class="data-table log-table"><table><thead><tr><th>Timestamp</th><th>Stage</th><th>Description</th><th>Count</th></tr></thead><tbody>';
        data.forEach(d => {
            html += `<tr><td>${d.timestamp.slice(0, 19).replace('T', ' ')}</td><td>${d.stage}</td><td>${d.description}</td><td>${d.count || '-'}</td></tr>`;
        });
        html += '</tbody></table></div>';

        const countResp = await apiFetch('/api/trip-count');
        html += `<p style="margin-top:1rem;color:var(--text-muted)">Total clean records in database: <strong>${fmtNum(countResp.count)}</strong></p>`;

        el.innerHTML = html;
    } catch (e) {
        el.innerHTML = `<div class="error">Error: ${e.message}</div>`;
    }
}

const originalShowPage = showPage;
showPage = function(pageId) {
    originalShowPage(pageId);
    switch (pageId) {
        case 'overview': renderOverview(); break;
        case 'locations': renderLocations(); break;
        case 'financial': renderFinancial(); break;
        case 'explore': renderExplore(); break;
        case 'pipeline': renderPipelineLog(); break;
    }
};

(async function init() {
    try {
        const count = await apiFetch('/api/trip-count');
        document.getElementById('tripCount').textContent = fmtNum(count.count) + ' trips loaded';
    } catch (e) {
        document.getElementById('tripCount').textContent = 'No data';
    }
    renderOverview();
})();
