import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const RULE_TYPES = [
  { id: 'voting', label: 'Voting', color: 'bg-indigo-100 text-indigo-800' },
  { id: 'content_approval', label: 'Content Approval', color: 'bg-emerald-100 text-emerald-800' },
  { id: 'financial', label: 'Financial', color: 'bg-amber-100 text-amber-800' },
  { id: 'distribution', label: 'Distribution', color: 'bg-cyan-100 text-cyan-800' },
  { id: 'membership', label: 'Membership', color: 'bg-rose-100 text-rose-800' },
];

const STATUS_COLORS = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-600',
  draft: 'bg-yellow-100 text-yellow-800',
};

const ENFORCEMENT_LABELS = { automatic: 'Auto-enforced', manual: 'Manual review' };

export const LabelGovernance = ({ activeLabel }) => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [form, setForm] = useState({ rule_type: 'voting', title: '', description: '', enforcement: 'manual', status: 'draft', conditions: {} });
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [conditionKey, setConditionKey] = useState('');
  const [conditionVal, setConditionVal] = useState('');

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    if (activeLabel) fetchRules();
  }, [activeLabel?.label_id]);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/governance`, { headers });
      if (res.ok) {
        const data = await res.json();
        setRules(data.rules || []);
        setStats({ total: data.total_rules, active: data.active_rules, byType: data.rules_by_type || {} });
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const resetForm = () => {
    setForm({ rule_type: 'voting', title: '', description: '', enforcement: 'manual', status: 'draft', conditions: {} });
    setEditingRule(null);
    setShowForm(false);
    setFormError('');
    setConditionKey('');
    setConditionVal('');
  };

  const openEdit = (rule) => {
    setEditingRule(rule);
    setForm({ rule_type: rule.rule_type, title: rule.title, description: rule.description, enforcement: rule.enforcement, status: rule.status, conditions: rule.conditions || {} });
    setShowForm(true);
  };

  const addCondition = () => {
    if (!conditionKey.trim()) return;
    const numVal = Number(conditionVal);
    setForm(f => ({ ...f, conditions: { ...f.conditions, [conditionKey.trim()]: isNaN(numVal) ? conditionVal : numVal } }));
    setConditionKey('');
    setConditionVal('');
  };

  const removeCondition = (key) => {
    setForm(f => {
      const c = { ...f.conditions };
      delete c[key];
      return { ...f, conditions: c };
    });
  };

  const handleSave = async () => {
    if (!form.title.trim()) { setFormError('Title is required'); return; }
    setSaving(true);
    setFormError('');
    try {
      const url = editingRule
        ? `${API}/api/uln/labels/${activeLabel.label_id}/governance/${editingRule.rule_id}`
        : `${API}/api/uln/labels/${activeLabel.label_id}/governance`;
      const method = editingRule ? 'PUT' : 'POST';
      const res = await fetch(url, { method, headers, body: JSON.stringify(form) });
      const data = await res.json();
      if (res.ok && data.success) { resetForm(); fetchRules(); }
      else setFormError(data.detail || data.error || 'Failed to save');
    } catch (e) { setFormError('Network error'); }
    setSaving(false);
  };

  const handleDelete = async (ruleId) => {
    if (!window.confirm('Delete this governance rule?')) return;
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/governance/${ruleId}`, { method: 'DELETE', headers });
      if (res.ok) fetchRules();
    } catch (e) { console.error(e); }
  };

  if (!activeLabel) {
    return (
      <div className="bg-white rounded-xl shadow p-8 text-center" data-testid="governance-no-label">
        <p className="text-gray-500">Select a label from the switcher above to manage its governance rules.</p>
      </div>
    );
  }

  const ruleTypeInfo = (id) => RULE_TYPES.find(t => t.id === id) || { label: id, color: 'bg-gray-100 text-gray-700' };

  return (
    <div className="space-y-6" data-testid="label-governance-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Governance Rules</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium text-purple-700">{activeLabel.name}</span> &middot; {stats.total || 0} rule{(stats.total || 0) !== 1 ? 's' : ''} ({stats.active || 0} active)
          </p>
        </div>
        <button onClick={() => { resetForm(); setShowForm(true); }} className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-purple-700 transition" data-testid="add-governance-rule-btn">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          Add Rule
        </button>
      </div>

      {/* Summary Cards */}
      {stats.total > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {RULE_TYPES.map(rt => (
            <div key={rt.id} className="bg-white rounded-lg shadow p-3 text-center">
              <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-medium ${rt.color}`}>{rt.label}</span>
              <p className="text-xl font-bold text-gray-900 mt-1">{stats.byType?.[rt.id] || 0}</p>
            </div>
          ))}
        </div>
      )}

      {/* Rules Table */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div></div>
        ) : rules.length === 0 ? (
          <div className="p-8 text-center text-gray-500" data-testid="governance-empty">No governance rules defined yet. Click "Add Rule" to create one.</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200" data-testid="governance-table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Enforcement</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {rules.map(rule => (
                <tr key={rule.rule_id} className="hover:bg-gray-50 transition" data-testid={`governance-row-${rule.rule_id}`}>
                  <td className="px-6 py-4">
                    <p className="text-sm font-medium text-gray-900">{rule.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{rule.description || '—'}</p>
                    {Object.keys(rule.conditions || {}).length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {Object.entries(rule.conditions).map(([k, v]) => (
                          <span key={k} className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">{k}: {String(v)}</span>
                        ))}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4"><span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${ruleTypeInfo(rule.rule_type).color}`}>{ruleTypeInfo(rule.rule_type).label}</span></td>
                  <td className="px-6 py-4 text-sm text-gray-600">{ENFORCEMENT_LABELS[rule.enforcement] || rule.enforcement}</td>
                  <td className="px-6 py-4"><span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[rule.status] || STATUS_COLORS.draft}`}>{rule.status}</span></td>
                  <td className="px-6 py-4 text-right text-sm space-x-2">
                    <button onClick={() => openEdit(rule)} className="text-blue-600 hover:text-blue-800 font-medium" data-testid={`edit-rule-${rule.rule_id}`}>Edit</button>
                    <button onClick={() => handleDelete(rule.rule_id)} className="text-red-600 hover:text-red-800 font-medium" data-testid={`delete-rule-${rule.rule_id}`}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Add / Edit Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => resetForm()}>
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()} data-testid="governance-form-modal">
            <h3 className="text-lg font-bold text-gray-900 mb-4">{editingRule ? 'Edit Governance Rule' : 'New Governance Rule'}</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rule Type</label>
                <select value={form.rule_type} onChange={e => setForm(f => ({ ...f, rule_type: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" data-testid="governance-rule-type">
                  {RULE_TYPES.map(rt => <option key={rt.id} value={rt.id}>{rt.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" placeholder="e.g. Quorum voting rule" data-testid="governance-title" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" placeholder="Describe what this rule enforces..." data-testid="governance-description" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Enforcement</label>
                  <select value={form.enforcement} onChange={e => setForm(f => ({ ...f, enforcement: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" data-testid="governance-enforcement">
                    <option value="manual">Manual</option>
                    <option value="automatic">Automatic</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select value={form.status} onChange={e => setForm(f => ({ ...f, status: e.target.value }))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500" data-testid="governance-status">
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
              </div>
              {/* Conditions builder */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Conditions</label>
                <div className="flex gap-2 mb-2">
                  <input value={conditionKey} onChange={e => setConditionKey(e.target.value)} className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm" placeholder="Key (e.g. quorum)" data-testid="condition-key" />
                  <input value={conditionVal} onChange={e => setConditionVal(e.target.value)} className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm" placeholder="Value" data-testid="condition-value" />
                  <button type="button" onClick={addCondition} className="px-3 py-1.5 bg-gray-200 rounded-lg text-sm font-medium hover:bg-gray-300" data-testid="add-condition-btn">+</button>
                </div>
                {Object.keys(form.conditions).length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {Object.entries(form.conditions).map(([k, v]) => (
                      <span key={k} className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded-full">
                        {k}: {String(v)}
                        <button onClick={() => removeCondition(k)} className="text-red-400 hover:text-red-600 ml-0.5">&times;</button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
              {formError && <p className="text-sm text-red-600" data-testid="governance-form-error">{formError}</p>}
              <div className="flex gap-3 pt-2">
                <button onClick={resetForm} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50">Cancel</button>
                <button onClick={handleSave} disabled={saving} className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50" data-testid="save-governance-rule-btn">
                  {saving ? 'Saving...' : editingRule ? 'Update Rule' : 'Create Rule'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
