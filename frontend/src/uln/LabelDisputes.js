import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const DISPUTE_TYPES = [
  { id: 'royalty_split', label: 'Royalty Split', color: 'bg-amber-100 text-amber-800' },
  { id: 'rights_ownership', label: 'Rights Ownership', color: 'bg-red-100 text-red-800' },
  { id: 'distribution', label: 'Distribution', color: 'bg-cyan-100 text-cyan-800' },
  { id: 'content_takedown', label: 'Content Takedown', color: 'bg-rose-100 text-rose-800' },
  { id: 'membership', label: 'Membership', color: 'bg-indigo-100 text-indigo-800' },
  { id: 'other', label: 'Other', color: 'bg-gray-100 text-gray-700' },
];

const STATUS_CONFIG = {
  open: { color: 'bg-blue-100 text-blue-800', label: 'Open' },
  under_review: { color: 'bg-yellow-100 text-yellow-800', label: 'Under Review' },
  resolved: { color: 'bg-green-100 text-green-800', label: 'Resolved' },
  escalated: { color: 'bg-red-100 text-red-800', label: 'Escalated' },
  closed: { color: 'bg-gray-100 text-gray-600', label: 'Closed' },
};

const PRIORITY_CONFIG = {
  low: { color: 'bg-slate-100 text-slate-600', dot: 'bg-slate-400' },
  medium: { color: 'bg-blue-100 text-blue-700', dot: 'bg-blue-500' },
  high: { color: 'bg-orange-100 text-orange-700', dot: 'bg-orange-500' },
  critical: { color: 'bg-red-100 text-red-700', dot: 'bg-red-600' },
};

export const LabelDisputes = ({ activeLabel }) => {
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [byStatus, setByStatus] = useState({});
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedDispute, setSelectedDispute] = useState(null);
  const [form, setForm] = useState({ dispute_type: 'royalty_split', title: '', description: '', priority: 'medium', assigned_to: '', related_asset_id: '', related_endpoint_id: '' });
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [responseText, setResponseText] = useState('');
  const [responseStatus, setResponseStatus] = useState('');
  const [respondLoading, setRespondLoading] = useState(false);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    if (activeLabel) fetchDisputes();
  }, [activeLabel?.label_id, statusFilter]);

  const fetchDisputes = async () => {
    setLoading(true);
    try {
      const qs = statusFilter ? `?status=${statusFilter}` : '';
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/disputes${qs}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setDisputes(data.disputes || []);
        setByStatus(data.disputes_by_status || {});
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const resetForm = () => {
    setForm({ dispute_type: 'royalty_split', title: '', description: '', priority: 'medium', assigned_to: '', related_asset_id: '', related_endpoint_id: '' });
    setShowCreateForm(false);
    setFormError('');
  };

  const handleCreate = async () => {
    if (!form.title.trim()) { setFormError('Title is required'); return; }
    setSaving(true);
    setFormError('');
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/disputes`, { method: 'POST', headers, body: JSON.stringify(form) });
      const data = await res.json();
      if (res.ok && data.success) { resetForm(); fetchDisputes(); }
      else setFormError(data.detail || data.error || 'Failed to create dispute');
    } catch (e) { setFormError('Network error'); }
    setSaving(false);
  };

  const openDetail = async (disputeId) => {
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/disputes/${disputeId}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setSelectedDispute(data.dispute);
        setResponseText('');
        setResponseStatus('');
      }
    } catch (e) { console.error(e); }
  };

  const handleRespond = async () => {
    if (!responseText.trim()) return;
    setRespondLoading(true);
    try {
      const body = { message: responseText, action: 'comment' };
      if (responseStatus) {
        body.new_status = responseStatus;
        if (responseStatus === 'resolved') body.resolution = responseText;
      }
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/disputes/${selectedDispute.dispute_id}/respond`, { method: 'POST', headers, body: JSON.stringify(body) });
      if (res.ok) {
        const data = await res.json();
        setSelectedDispute(data.dispute);
        setResponseText('');
        setResponseStatus('');
        fetchDisputes();
      }
    } catch (e) { console.error(e); }
    setRespondLoading(false);
  };

  if (!activeLabel) {
    return (
      <div className="bg-white rounded-xl shadow p-8 text-center" data-testid="disputes-no-label">
        <p className="text-gray-500">Select a label from the switcher above to manage its disputes.</p>
      </div>
    );
  }

  const typeInfo = (id) => DISPUTE_TYPES.find(t => t.id === id) || { label: id, color: 'bg-gray-100 text-gray-700' };

  return (
    <div className="space-y-6" data-testid="label-disputes-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Disputes</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium text-purple-700">{activeLabel.name}</span> &middot; {disputes.length} dispute{disputes.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button onClick={() => { resetForm(); setShowCreateForm(true); }} className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-purple-700 transition" data-testid="file-dispute-btn">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          File Dispute
        </button>
      </div>

      {/* Status filter pills */}
      <div className="flex flex-wrap gap-2">
        <button onClick={() => setStatusFilter('')} className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${!statusFilter ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`} data-testid="filter-all">All</button>
        {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
          <button key={key} onClick={() => setStatusFilter(key)} className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${statusFilter === key ? 'bg-purple-600 text-white' : cfg.color + ' hover:opacity-80'}`} data-testid={`filter-${key}`}>
            {cfg.label} {byStatus[key] ? `(${byStatus[key]})` : ''}
          </button>
        ))}
      </div>

      {/* Disputes list */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div></div>
        ) : disputes.length === 0 ? (
          <div className="p-8 text-center text-gray-500" data-testid="disputes-empty">No disputes found. Click "File Dispute" to create one.</div>
        ) : (
          <div className="divide-y divide-gray-200">
            {disputes.map(d => {
              const st = STATUS_CONFIG[d.status] || STATUS_CONFIG.open;
              const pr = PRIORITY_CONFIG[d.priority] || PRIORITY_CONFIG.medium;
              return (
                <div key={d.dispute_id} className="px-6 py-4 hover:bg-gray-50 transition cursor-pointer" onClick={() => openDetail(d.dispute_id)} data-testid={`dispute-row-${d.dispute_id}`}>
                  <div className="flex items-start justify-between">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="text-sm font-semibold text-gray-900">{d.title}</p>
                        <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium ${typeInfo(d.dispute_type).color}`}>{typeInfo(d.dispute_type).label}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1 line-clamp-1">{d.description || '—'}</p>
                      <p className="text-[10px] text-gray-400 mt-1">Filed {d.created_at ? new Date(d.created_at).toLocaleDateString() : '—'} &middot; {d.responses?.length || 0} response{(d.responses?.length || 0) !== 1 ? 's' : ''}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0 ml-4">
                      <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${pr.color}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${pr.dot}`}></span>{d.priority}
                      </span>
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium ${st.color}`}>{st.label}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Dispute Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={resetForm}>
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()} data-testid="create-dispute-modal">
            <h3 className="text-lg font-bold text-gray-900 mb-4">File a Dispute</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Dispute Type</label>
                <select value={form.dispute_type} onChange={e => setForm(f => ({ ...f, dispute_type: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" data-testid="dispute-type-select">
                  {DISPUTE_TYPES.map(dt => <option key={dt.id} value={dt.id}>{dt.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" placeholder="Brief description of the dispute" data-testid="dispute-title-input" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={4} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" placeholder="Provide details about the dispute..." data-testid="dispute-description-input" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select value={form.priority} onChange={e => setForm(f => ({ ...f, priority: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" data-testid="dispute-priority-select">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Assigned To (optional)</label>
                  <input value={form.assigned_to} onChange={e => setForm(f => ({ ...f, assigned_to: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" placeholder="User ID" data-testid="dispute-assigned-input" />
                </div>
              </div>
              {formError && <p className="text-sm text-red-600" data-testid="dispute-form-error">{formError}</p>}
              <div className="flex gap-3 pt-2">
                <button onClick={resetForm} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50">Cancel</button>
                <button onClick={handleCreate} disabled={saving} className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50" data-testid="submit-dispute-btn">
                  {saving ? 'Filing...' : 'File Dispute'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dispute Detail Modal */}
      {selectedDispute && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedDispute(null)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()} data-testid="dispute-detail-modal">
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold text-gray-900">{selectedDispute.title}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium ${typeInfo(selectedDispute.dispute_type).color}`}>{typeInfo(selectedDispute.dispute_type).label}</span>
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium ${(STATUS_CONFIG[selectedDispute.status] || STATUS_CONFIG.open).color}`}>{(STATUS_CONFIG[selectedDispute.status] || STATUS_CONFIG.open).label}</span>
                  <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${(PRIORITY_CONFIG[selectedDispute.priority] || PRIORITY_CONFIG.medium).color}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${(PRIORITY_CONFIG[selectedDispute.priority] || PRIORITY_CONFIG.medium).dot}`}></span>{selectedDispute.priority}
                  </span>
                </div>
              </div>
              <button onClick={() => setSelectedDispute(null)} className="text-gray-400 hover:text-gray-600 text-xl leading-none" data-testid="close-dispute-detail">&times;</button>
            </div>
            {/* Body */}
            <div className="px-6 py-4 space-y-4">
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Description</h4>
                <p className="text-sm text-gray-700">{selectedDispute.description || 'No description.'}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-gray-500">Filed:</span> <span className="text-gray-800">{selectedDispute.created_at ? new Date(selectedDispute.created_at).toLocaleString() : '—'}</span></div>
                <div><span className="text-gray-500">ID:</span> <span className="text-gray-800 font-mono text-xs">{selectedDispute.dispute_id}</span></div>
                {selectedDispute.assigned_to && <div><span className="text-gray-500">Assigned:</span> <span className="text-gray-800">{selectedDispute.assigned_to}</span></div>}
                {selectedDispute.resolved_at && <div><span className="text-gray-500">Resolved:</span> <span className="text-gray-800">{new Date(selectedDispute.resolved_at).toLocaleString()}</span></div>}
              </div>
              {selectedDispute.resolution && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-green-700 uppercase mb-1">Resolution</h4>
                  <p className="text-sm text-green-800">{selectedDispute.resolution}</p>
                </div>
              )}
              {/* Timeline */}
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase mb-3">Activity ({selectedDispute.responses?.length || 0})</h4>
                {(!selectedDispute.responses || selectedDispute.responses.length === 0) ? (
                  <p className="text-sm text-gray-400">No activity yet.</p>
                ) : (
                  <div className="space-y-3">
                    {selectedDispute.responses.map((r, i) => (
                      <div key={r.response_id || i} className="flex gap-3" data-testid={`response-${r.response_id}`}>
                        <div className="w-7 h-7 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                          {(r.author_name || r.author_id || '?')[0].toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-gray-900">{r.author_name || r.author_id}</span>
                            {r.action === 'status_change' && <span className="text-[10px] bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">Status changed</span>}
                            {r.action === 'resolution' && <span className="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded">Resolved</span>}
                          </div>
                          <p className="text-sm text-gray-700 mt-0.5">{r.message}</p>
                          <p className="text-[10px] text-gray-400 mt-0.5">{r.created_at ? new Date(r.created_at).toLocaleString() : ''}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {/* Respond form */}
              {selectedDispute.status !== 'closed' && selectedDispute.status !== 'resolved' && (
                <div className="border-t border-gray-200 pt-4 space-y-3">
                  <textarea value={responseText} onChange={e => setResponseText(e.target.value)} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" placeholder="Write a response..." data-testid="dispute-response-input" />
                  <div className="flex items-center gap-3">
                    <select value={responseStatus} onChange={e => setResponseStatus(e.target.value)} className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="response-status-select">
                      <option value="">Comment only</option>
                      <option value="under_review">Move to Under Review</option>
                      <option value="escalated">Escalate</option>
                      <option value="resolved">Mark Resolved</option>
                      <option value="closed">Close</option>
                    </select>
                    <button onClick={handleRespond} disabled={respondLoading || !responseText.trim()} className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50" data-testid="submit-response-btn">
                      {respondLoading ? 'Sending...' : 'Submit'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
