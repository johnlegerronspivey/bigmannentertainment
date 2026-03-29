import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_BADGE = {
  released: 'bg-emerald-100 text-emerald-800',
  'pre-release': 'bg-amber-100 text-amber-800',
  draft: 'bg-gray-100 text-gray-600',
  taken_down: 'bg-red-100 text-red-800',
};

const ASSET_TYPES = ['single', 'album', 'ep', 'compilation', 'mixtape'];
const ASSET_STATUSES = ['draft', 'pre-release', 'released', 'taken_down'];
const TERRITORY_OPTIONS = ['GLOBAL', 'US', 'UK', 'EU', 'CA', 'AU', 'JP', 'BR', 'KR', 'IN', 'MX'];

const emptyAsset = { title: '', type: 'single', artist: '', isrc: '', upc: '', gtin: '', release_date: '', genre: '', status: 'draft', platforms: [], streams_total: 0 };

export const LabelCatalog = ({ activeLabel }) => {
  const [catalog, setCatalog] = useState({ assets: [], total_assets: 0 });
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingAsset, setEditingAsset] = useState(null);
  const [form, setForm] = useState({ ...emptyAsset });
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  // Rights panel
  const [rightsAssetId, setRightsAssetId] = useState(null);
  const [rights, setRights] = useState(null);
  const [rightsLoading, setRightsLoading] = useState(false);
  const [rightsForm, setRightsForm] = useState({ splits: [], territories: ['GLOBAL'], ai_consent: false, ai_consent_details: '', sponsorship_rules: '', exclusive: true, expiry_date: '' });
  const [rightsSaving, setRightsSaving] = useState(false);

  const token = localStorage.getItem('token');
  const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    if (activeLabel) fetchCatalog();
  }, [activeLabel?.label_id]);

  const fetchCatalog = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/catalog`, { headers });
      if (res.ok) setCatalog(await res.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  // ── Asset CRUD ────────────────────────────────────────────────
  const openCreate = () => { setEditingAsset(null); setForm({ ...emptyAsset }); setFormError(''); setShowForm(true); };
  const openEdit = (a) => { setEditingAsset(a); setForm({ ...a }); setFormError(''); setShowForm(true); };

  const handleSave = async () => {
    if (!form.title.trim()) { setFormError('Title is required'); return; }
    if (!form.gtin || !form.gtin.trim()) { setFormError('GTIN is required for every catalog asset'); return; }
    setSaving(true); setFormError('');
    try {
      const url = editingAsset
        ? `${API}/api/uln/labels/${activeLabel.label_id}/catalog/assets/${editingAsset.asset_id}`
        : `${API}/api/uln/labels/${activeLabel.label_id}/catalog/assets`;
      const method = editingAsset ? 'PUT' : 'POST';
      const res = await fetch(url, { method, headers, body: JSON.stringify(form) });
      const data = await res.json();
      if (res.ok && data.success) { setShowForm(false); fetchCatalog(); }
      else {
        const detail = data.detail;
        if (detail?.validation_errors) {
          const errMsgs = Object.entries(detail.validation_errors).map(([k, v]) => `${k}: ${v}`).join('; ');
          setFormError(errMsgs);
        } else {
          setFormError(typeof detail === 'string' ? detail : detail?.message || data.error || 'Failed to save');
        }
      }
    } catch (e) { setFormError('Network error'); }
    setSaving(false);
  };

  const handleDelete = async (assetId) => {
    if (!window.confirm('Delete this asset and its rights data?')) return;
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/catalog/assets/${assetId}`, { method: 'DELETE', headers });
      if (res.ok) { fetchCatalog(); if (rightsAssetId === assetId) setRightsAssetId(null); }
    } catch (e) { console.error(e); }
  };

  // ── Rights Panel ──────────────────────────────────────────────
  const openRights = async (assetId) => {
    setRightsAssetId(assetId); setRightsLoading(true); setRights(null);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/catalog/assets/${assetId}/rights`, { headers });
      if (res.ok) {
        const data = await res.json();
        if (data.rights) { setRights(data.rights); setRightsForm({ splits: data.rights.splits || [], territories: data.rights.territories || ['GLOBAL'], ai_consent: data.rights.ai_consent || false, ai_consent_details: data.rights.ai_consent_details || '', sponsorship_rules: data.rights.sponsorship_rules || '', exclusive: data.rights.exclusive !== false, expiry_date: data.rights.expiry_date || '' }); }
        else { setRights(null); setRightsForm({ splits: [], territories: ['GLOBAL'], ai_consent: false, ai_consent_details: '', sponsorship_rules: '', exclusive: true, expiry_date: '' }); }
      }
    } catch (e) { console.error(e); }
    setRightsLoading(false);
  };

  const addSplit = () => setRightsForm(f => ({ ...f, splits: [...f.splits, { party: '', role: '', percentage: 0 }] }));
  const removeSplit = (i) => setRightsForm(f => ({ ...f, splits: f.splits.filter((_, idx) => idx !== i) }));
  const updateSplit = (i, field, val) => setRightsForm(f => ({ ...f, splits: f.splits.map((s, idx) => idx === i ? { ...s, [field]: field === 'percentage' ? parseFloat(val) || 0 : val } : s) }));

  const toggleTerritory = (t) => setRightsForm(f => ({ ...f, territories: f.territories.includes(t) ? f.territories.filter(x => x !== t) : [...f.territories, t] }));

  const saveRights = async () => {
    setRightsSaving(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/catalog/assets/${rightsAssetId}/rights`, { method: 'PUT', headers, body: JSON.stringify(rightsForm) });
      if (res.ok) { const d = await res.json(); setRights(d.rights); }
    } catch (e) { console.error(e); }
    setRightsSaving(false);
  };

  const totalSplitPct = rightsForm.splits.reduce((s, x) => s + (x.percentage || 0), 0);

  if (!activeLabel) {
    return (<div className="bg-white rounded-xl shadow p-8 text-center" data-testid="catalog-no-label"><p className="text-gray-500">Select a label from the switcher above to view its catalog.</p></div>);
  }

  return (
    <div className="space-y-6" data-testid="label-catalog-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Catalog</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium text-purple-700">{activeLabel.name}</span> &middot; {catalog.total_assets} asset{catalog.total_assets !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/catalog-import" className="flex items-center gap-2 border border-purple-300 text-purple-700 px-4 py-2 rounded-lg font-medium text-sm hover:bg-purple-50 transition" data-testid="import-csv-btn">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
            Import CSV
          </Link>
          <button onClick={openCreate} className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-purple-700 transition" data-testid="add-asset-btn">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
            Add Asset
          </button>
        </div>
      </div>

      {/* Asset Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" data-testid="asset-form-modal">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
            <h3 className="text-lg font-bold mb-4">{editingAsset ? 'Edit Asset' : 'Add New Asset'}</h3>
            {formError && <div className="text-sm text-red-600 bg-red-50 p-2 rounded mb-3">{formError}</div>}
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Track / Album title" data-testid="asset-title-input" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" data-testid="asset-type-select">
                    {ASSET_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" data-testid="asset-status-select">
                    {ASSET_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Artist</label>
                <input value={form.artist} onChange={e => setForm(f => ({ ...f, artist: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" data-testid="asset-artist-input" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">GTIN (Global Trade Item Number) <span className="text-red-500">*</span></label>
                <input value={form.gtin || ''} onChange={e => setForm(f => ({ ...f, gtin: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm font-mono" placeholder="e.g. 00860004340201 (8/12/13/14 digits)" data-testid="asset-gtin-input" />
                <p className="text-xs text-gray-400 mt-0.5">Mandatory GS1 identifier with Modulo-10 check digit</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ISRC</label>
                  <input value={form.isrc} onChange={e => setForm(f => ({ ...f, isrc: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm font-mono" data-testid="asset-isrc-input" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">UPC</label>
                  <input value={form.upc} onChange={e => setForm(f => ({ ...f, upc: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm font-mono" data-testid="asset-upc-input" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Genre</label>
                  <input value={form.genre} onChange={e => setForm(f => ({ ...f, genre: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" data-testid="asset-genre-input" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Release Date</label>
                  <input type="date" value={form.release_date} onChange={e => setForm(f => ({ ...f, release_date: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" data-testid="asset-release-input" />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 border rounded-lg text-sm text-gray-600 hover:bg-gray-50" data-testid="asset-cancel-btn">Cancel</button>
              <button onClick={handleSave} disabled={saving} className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50" data-testid="asset-save-btn">
                {saving ? 'Saving...' : editingAsset ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assets Table */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div></div>
        ) : catalog.assets.length === 0 ? (
          <div className="p-8 text-center text-gray-500" data-testid="catalog-empty">
            <p className="mb-2">No assets in this label's catalog yet.</p>
            <button onClick={openCreate} className="text-purple-600 font-medium text-sm hover:underline">Add your first asset</button>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200" data-testid="catalog-table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Artist</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">GTIN</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ISRC</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Streams</th>
                <th className="px-5 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {catalog.assets.map((a) => (
                <tr key={a.asset_id} data-testid={`catalog-row-${a.asset_id}`} className="hover:bg-gray-50">
                  <td className="px-5 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{a.title}</td>
                  <td className="px-5 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{a.type}</td>
                  <td className="px-5 py-4 whitespace-nowrap text-sm text-gray-600">{a.artist}</td>
                  <td className="px-5 py-4 whitespace-nowrap text-xs font-mono text-gray-500">{a.gtin || '—'}</td>
                  <td className="px-5 py-4 whitespace-nowrap text-xs font-mono text-gray-500">{a.isrc || '—'}</td>
                  <td className="px-5 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${STATUS_BADGE[a.status] || 'bg-gray-100 text-gray-700'}`}>{a.status}</span>
                  </td>
                  <td className="px-5 py-4 whitespace-nowrap text-sm text-gray-700 text-right font-medium">
                    {a.streams_total != null ? a.streams_total.toLocaleString() : '—'}
                  </td>
                  <td className="px-5 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button onClick={() => openRights(a.asset_id)} className="p-1.5 rounded-md hover:bg-purple-50 text-purple-600" title="Manage Rights" data-testid={`rights-btn-${a.asset_id}`}>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                      </button>
                      <button onClick={() => openEdit(a)} className="p-1.5 rounded-md hover:bg-blue-50 text-blue-600" title="Edit" data-testid={`edit-asset-btn-${a.asset_id}`}>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                      </button>
                      <button onClick={() => handleDelete(a.asset_id)} className="p-1.5 rounded-md hover:bg-red-50 text-red-500" title="Delete" data-testid={`delete-asset-btn-${a.asset_id}`}>
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

      {/* Rights Panel */}
      {rightsAssetId && (
        <div className="bg-white rounded-xl shadow p-6 border-l-4 border-purple-500" data-testid="rights-panel">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">Rights Management</h3>
            <button onClick={() => setRightsAssetId(null)} className="text-gray-400 hover:text-gray-600">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
          <p className="text-sm text-gray-500 mb-4">
            Asset: <span className="font-medium text-gray-700">{catalog.assets.find(a => a.asset_id === rightsAssetId)?.title || rightsAssetId}</span>
          </p>

          {rightsLoading ? (
            <div className="p-4 text-center"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mx-auto"></div></div>
          ) : (
            <div className="space-y-5">
              {/* Splits */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-semibold text-gray-700">Revenue Splits</label>
                  <span className={`text-xs font-medium ${totalSplitPct === 100 ? 'text-emerald-600' : 'text-amber-600'}`}>{totalSplitPct}% allocated</span>
                </div>
                {rightsForm.splits.map((sp, i) => (
                  <div key={i} className="flex items-center gap-2 mb-2" data-testid={`split-row-${i}`}>
                    <input value={sp.party} onChange={e => updateSplit(i, 'party', e.target.value)} placeholder="Party name" className="flex-1 border rounded-lg px-2 py-1.5 text-sm" />
                    <input value={sp.role} onChange={e => updateSplit(i, 'role', e.target.value)} placeholder="Role" className="w-24 border rounded-lg px-2 py-1.5 text-sm" />
                    <div className="flex items-center gap-1 w-24">
                      <input type="number" value={sp.percentage} onChange={e => updateSplit(i, 'percentage', e.target.value)} className="w-16 border rounded-lg px-2 py-1.5 text-sm text-right" min="0" max="100" />
                      <span className="text-sm text-gray-500">%</span>
                    </div>
                    <button onClick={() => removeSplit(i)} className="text-red-400 hover:text-red-600 p-1" data-testid={`remove-split-${i}`}>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                  </div>
                ))}
                <button onClick={addSplit} className="text-purple-600 text-sm font-medium hover:underline" data-testid="add-split-btn">+ Add Split</button>
              </div>

              {/* Territories */}
              <div>
                <label className="text-sm font-semibold text-gray-700 mb-2 block">Territories</label>
                <div className="flex flex-wrap gap-2" data-testid="territory-chips">
                  {TERRITORY_OPTIONS.map(t => (
                    <button key={t} onClick={() => toggleTerritory(t)} className={`px-3 py-1 rounded-full text-xs font-medium transition ${rightsForm.territories.includes(t) ? 'bg-purple-100 text-purple-700 ring-1 ring-purple-300' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}`} data-testid={`territory-${t}`}>
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* AI Consent + Exclusive */}
              <div className="grid grid-cols-2 gap-4">
                <label className="flex items-center gap-2 cursor-pointer" data-testid="ai-consent-toggle">
                  <input type="checkbox" checked={rightsForm.ai_consent} onChange={e => setRightsForm(f => ({ ...f, ai_consent: e.target.checked }))} className="rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                  <span className="text-sm text-gray-700">AI Training Consent</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer" data-testid="exclusive-toggle">
                  <input type="checkbox" checked={rightsForm.exclusive} onChange={e => setRightsForm(f => ({ ...f, exclusive: e.target.checked }))} className="rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
                  <span className="text-sm text-gray-700">Exclusive Rights</span>
                </label>
              </div>

              {rightsForm.ai_consent && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">AI Consent Details</label>
                  <textarea value={rightsForm.ai_consent_details} onChange={e => setRightsForm(f => ({ ...f, ai_consent_details: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" rows={2} placeholder="Describe permitted AI usage..." data-testid="ai-details-input" />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sponsorship Rules</label>
                <input value={rightsForm.sponsorship_rules} onChange={e => setRightsForm(f => ({ ...f, sponsorship_rules: e.target.value }))} className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="e.g. No alcohol brands, etc." data-testid="sponsorship-input" />
              </div>

              <div className="flex justify-end">
                <button onClick={saveRights} disabled={rightsSaving} className="px-5 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50" data-testid="save-rights-btn">
                  {rightsSaving ? 'Saving...' : 'Save Rights'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
