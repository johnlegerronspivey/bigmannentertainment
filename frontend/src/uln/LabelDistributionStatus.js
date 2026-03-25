import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const DSP_STATUS_BADGE = {
  live: 'bg-emerald-100 text-emerald-800',
  pending: 'bg-amber-100 text-amber-800',
  error: 'bg-red-100 text-red-800',
  disabled: 'bg-gray-100 text-gray-600',
};

const PLATFORMS = ['Spotify', 'Apple Music', 'YouTube Music', 'Tidal', 'Deezer', 'Amazon Music', 'SoundCloud', 'Pandora', 'iHeartRadio', 'Napster', 'Audiomack'];
const EP_STATUSES = ['live', 'pending', 'error', 'disabled'];
const EP_TYPES = ['streaming', 'download', 'social', 'broadcast', 'sync'];

export const LabelDistributionStatus = ({ activeLabel }) => {
  const [distData, setDistData] = useState({ endpoints: [], summary: {} });
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingEp, setEditingEp] = useState(null);
  const [form, setForm] = useState({ platform: '', status: 'pending', endpoint_type: 'streaming', credentials_ref: '' });
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');

  const token = localStorage.getItem('token');
  const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    if (activeLabel) fetchDistribution();
  }, [activeLabel?.label_id]);

  const fetchDistribution = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/distribution/status`, { headers });
      if (res.ok) setDistData(await res.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const openCreate = () => { setEditingEp(null); setForm({ platform: '', status: 'pending', endpoint_type: 'streaming', credentials_ref: '' }); setFormError(''); setShowForm(true); };
  const openEdit = (ep) => { setEditingEp(ep); setForm({ platform: ep.platform, status: ep.status, endpoint_type: ep.endpoint_type || 'streaming', credentials_ref: ep.credentials_ref || '' }); setFormError(''); setShowForm(true); };

  const handleSave = async () => {
    if (!form.platform.trim()) { setFormError('Platform is required'); return; }
    setSaving(true); setFormError('');
    try {
      const url = editingEp
        ? `${API}/api/uln/labels/${activeLabel.label_id}/endpoints/${editingEp.endpoint_id}`
        : `${API}/api/uln/labels/${activeLabel.label_id}/endpoints`;
      const method = editingEp ? 'PUT' : 'POST';
      const res = await fetch(url, { method, headers, body: JSON.stringify(form) });
      const data = await res.json();
      if (res.ok && data.success) { setShowForm(false); fetchDistribution(); }
      else setFormError(data.detail || data.error || 'Failed to save');
    } catch (e) { setFormError('Network error'); }
    setSaving(false);
  };

  const handleDelete = async (epId) => {
    if (!window.confirm('Remove this distribution endpoint?')) return;
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/endpoints/${epId}`, { method: 'DELETE', headers });
      if (res.ok) fetchDistribution();
    } catch (e) { console.error(e); }
  };

  if (!activeLabel) {
    return (<div className="bg-white rounded-xl shadow p-8 text-center" data-testid="dist-no-label"><p className="text-gray-500">Select a label from the switcher above to view distribution status.</p></div>);
  }

  const { summary } = distData;

  return (
    <div className="space-y-6" data-testid="label-distribution-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Distribution Status</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium text-purple-700">{activeLabel.name}</span> &middot; {summary.total_endpoints || 0} endpoint{(summary.total_endpoints || 0) !== 1 ? 's' : ''}
          </p>
        </div>
        <button onClick={openCreate} className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-purple-700 transition" data-testid="add-endpoint-btn">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          Add Endpoint
        </button>
      </div>

      {/* Summary Cards */}
      {summary.total_endpoints > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4" data-testid="dist-summary-cards">
          <div className="bg-white rounded-xl shadow p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{summary.total_endpoints}</p>
            <p className="text-xs text-gray-500 mt-1">Total</p>
          </div>
          <div className="bg-white rounded-xl shadow p-4 text-center">
            <p className="text-2xl font-bold text-emerald-600">{summary.live}</p>
            <p className="text-xs text-gray-500 mt-1">Live</p>
          </div>
          <div className="bg-white rounded-xl shadow p-4 text-center">
            <p className="text-2xl font-bold text-amber-600">{summary.pending}</p>
            <p className="text-xs text-gray-500 mt-1">Pending</p>
          </div>
          <div className="bg-white rounded-xl shadow p-4 text-center">
            <p className="text-2xl font-bold text-red-600">{summary.error}</p>
            <p className="text-xs text-gray-500 mt-1">Errors</p>
          </div>
        </div>
      )}

      {/* Health bar */}
      {summary.total_endpoints > 0 && (
        <div className="bg-white rounded-xl shadow p-4" data-testid="dist-health-bar">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Distribution Health</span>
            <span className="text-sm font-bold text-gray-900">{summary.health_pct}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div className={`h-2.5 rounded-full transition-all ${summary.health_pct >= 80 ? 'bg-emerald-500' : summary.health_pct >= 50 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${summary.health_pct}%` }}></div>
          </div>
        </div>
      )}

      {/* Endpoint Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" data-testid="endpoint-form-modal">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-bold mb-4">{editingEp ? 'Edit Endpoint' : 'Add Distribution Endpoint'}</h3>
            {formError && <div className="text-sm text-red-600 bg-red-50 p-2 rounded mb-3">{formError}</div>}
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Platform *</label>
                <select value={form.platform} onChange={e => setForm(f => ({ ...f, platform: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" data-testid="ep-platform-select">
                  <option value="">Select platform...</option>
                  {PLATFORMS.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" data-testid="ep-status-select">
                    {EP_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select value={form.endpoint_type} onChange={e => setForm(f => ({ ...f, endpoint_type: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" data-testid="ep-type-select">
                    {EP_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Credentials Ref</label>
                <input value={form.credentials_ref} onChange={e => setForm(f => ({ ...f, credentials_ref: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Optional credential reference" data-testid="ep-cred-input" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 border rounded-lg text-sm text-gray-600 hover:bg-gray-50" data-testid="ep-cancel-btn">Cancel</button>
              <button onClick={handleSave} disabled={saving} className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50" data-testid="ep-save-btn">
                {saving ? 'Saving...' : editingEp ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Endpoints Table */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div></div>
        ) : distData.endpoints.length === 0 ? (
          <div className="p-8 text-center text-gray-500" data-testid="dist-empty">
            <p className="mb-2">No distribution endpoints configured.</p>
            <button onClick={openCreate} className="text-purple-600 font-medium text-sm hover:underline">Add your first endpoint</button>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200" data-testid="dist-table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Delivery</th>
                <th className="px-5 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Assets</th>
                <th className="px-5 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Errors</th>
                <th className="px-5 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {distData.endpoints.map((ep) => (
                <tr key={ep.endpoint_id} data-testid={`dist-row-${ep.endpoint_id}`} className="hover:bg-gray-50">
                  <td className="px-5 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{ep.platform}</td>
                  <td className="px-5 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{ep.endpoint_type || '—'}</td>
                  <td className="px-5 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${DSP_STATUS_BADGE[ep.status] || 'bg-gray-100 text-gray-700'}`}>{ep.status}</span>
                  </td>
                  <td className="px-5 py-4 whitespace-nowrap text-sm text-gray-600">
                    {ep.last_delivery ? new Date(ep.last_delivery).toLocaleString() : '—'}
                  </td>
                  <td className="px-5 py-4 whitespace-nowrap text-sm text-gray-700 text-right">{ep.assets_delivered || 0}</td>
                  <td className="px-5 py-4 whitespace-nowrap text-sm text-right">
                    {(ep.errors || 0) > 0 ? (
                      <span className="text-red-600 font-medium" title={ep.error_message || ''}>{ep.errors}</span>
                    ) : (
                      <span className="text-gray-400">0</span>
                    )}
                  </td>
                  <td className="px-5 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button onClick={() => openEdit(ep)} className="p-1.5 rounded-md hover:bg-blue-50 text-blue-600" title="Edit" data-testid={`edit-ep-btn-${ep.endpoint_id}`}>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                      </button>
                      <button onClick={() => handleDelete(ep.endpoint_id)} className="p-1.5 rounded-md hover:bg-red-50 text-red-500" title="Delete" data-testid={`delete-ep-btn-${ep.endpoint_id}`}>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
