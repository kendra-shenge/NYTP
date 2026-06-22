const API_BASE = window.location.origin;

async function apiFetch(endpoint) {
    const resp = await fetch(`${API_BASE}${endpoint}`);
    if (!resp.ok) throw new Error(`API error: ${resp.status}`);
    return resp.json();
}

async function apiFetchWithParams(endpoint, params) {
    const qs = Object.entries(params)
        .filter(([, v]) => v !== null && v !== undefined && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&');
    return apiFetch(`${endpoint}?${qs}`);
}
