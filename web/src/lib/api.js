const BASE = '/api';

function getToken() {
  return localStorage.getItem('pramaanai_token');
}

async function request(path, { method = 'GET', body, form } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let payload = body;
  if (body && !form) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }

  const res = await fetch(`${BASE}${path}`, { method, headers, body: form || payload });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const errJson = await res.json();
      detail = errJson.detail || detail;
    } catch { /* ignore */ }
    const err = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    err.status = res.status;
    throw err;
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  async login(email, password) {
    const form = new URLSearchParams();
    form.set('username', email);
    form.set('password', password);
    return request('/auth/login', {
      method: 'POST',
      form,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  me: () => request('/auth/me'),

  listTenders: () => request('/tenders'),
  getTender: (id) => request(`/tenders/${id}`),
  createTender: (body) => request('/tenders', { method: 'POST', body }),
  extractRequirements: (tenderId, text) =>
    request(`/tenders/${tenderId}/requirements/extract`, { method: 'POST', body: { text } }),
  confirmRequirements: (tenderId, requirement_ids) =>
    request(`/tenders/${tenderId}/requirements/confirm`, { method: 'POST', body: { requirement_ids } }),
  listSubmissions: (tenderId) => request(`/tenders/${tenderId}/submissions`),
  getSubmission: (id) => request(`/tenders/submissions/${id}`),

  listDocuments: (submissionId) => request(`/documents/submission/${submissionId}`),
  uploadDocument: (submissionId, docType, file) => {
    const form = new FormData();
    form.set('submission_id', submissionId);
    form.set('doc_type', docType);
    form.set('file', file);
    return request('/documents/upload', { method: 'POST', form });
  },

  getMatrix: (submissionId) => request(`/compliance/submission/${submissionId}/matrix`),
  reEvaluate: (submissionId) => request(`/compliance/submission/${submissionId}/evaluate`, { method: 'POST' }),
  getEvidence: (resultId) => request(`/compliance/results/${resultId}/evidence`),
  takeAction: (resultId, action, payload) =>
    request(`/compliance/results/${resultId}/action/${action}`, { method: 'POST', body: payload }),

  listAudit: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/audit${qs ? `?${qs}` : ''}`);
  },

  analyticsOverview: () => request('/analytics/overview'),
  listAlerts: () => request('/alerts'),
  search: (q) => request(`/search?q=${encodeURIComponent(q)}`),
};

export { getToken };
