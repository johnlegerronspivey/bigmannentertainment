import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

// --- Constants ---
const DISPUTE_TYPES = [
  { value: 'ROYALTY_DISPUTE', label: 'Royalty Dispute' },
  { value: 'CONTRACT_DISPUTE', label: 'Contract Dispute' },
  { value: 'PAYMENT_DISPUTE', label: 'Payment Dispute' },
  { value: 'COPYRIGHT_CLAIM', label: 'Copyright Claim' },
  { value: 'OWNERSHIP_DISPUTE', label: 'Ownership Dispute' },
  { value: 'LICENSING_ISSUE', label: 'Licensing Issue' },
  { value: 'DISTRIBUTION_DISPUTE', label: 'Distribution Dispute' },
  { value: 'OTHER', label: 'Other' },
];

const PRIORITIES = [
  { value: 'LOW', label: 'Low', color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  { value: 'MEDIUM', label: 'Medium', color: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' },
  { value: 'HIGH', label: 'High', color: 'bg-orange-500/20 text-orange-300 border-orange-500/30' },
  { value: 'CRITICAL', label: 'Critical', color: 'bg-red-500/20 text-red-300 border-red-500/30' },
];

const STATUS_COLORS = {
  OPEN: 'bg-red-500/20 text-red-300 border-red-500/30',
  UNDER_REVIEW: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  RESOLVED: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  ESCALATED: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  CLOSED: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
  REJECTED: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
};

const EVENT_TYPE_STYLES = {
  DISPUTE_CREATED: { bg: 'bg-emerald-500/20', text: 'text-emerald-300', label: 'Created' },
  DISPUTE_UPDATED: { bg: 'bg-sky-500/20', text: 'text-sky-300', label: 'Updated' },
  DISPUTE_STATUS_CHANGED: { bg: 'bg-yellow-500/20', text: 'text-yellow-300', label: 'Status Changed' },
  DISPUTE_RESOLVED: { bg: 'bg-green-500/20', text: 'text-green-300', label: 'Resolved' },
  EVIDENCE_ADDED: { bg: 'bg-purple-500/20', text: 'text-purple-300', label: 'Evidence' },
  COMMENT_ADDED: { bg: 'bg-cyan-500/20', text: 'text-cyan-300', label: 'Comment' },
  ASSIGNMENT_CHANGED: { bg: 'bg-indigo-500/20', text: 'text-indigo-300', label: 'Assigned' },
  ESCALATION: { bg: 'bg-orange-500/20', text: 'text-orange-300', label: 'Escalated' },
  SETTLEMENT_PROPOSED: { bg: 'bg-teal-500/20', text: 'text-teal-300', label: 'Settlement' },
  SETTLEMENT_ACCEPTED: { bg: 'bg-green-500/20', text: 'text-green-300', label: 'Accepted' },
  SETTLEMENT_REJECTED: { bg: 'bg-red-500/20', text: 'text-red-300', label: 'Rejected' },
  DOCUMENT_UPLOADED: { bg: 'bg-blue-500/20', text: 'text-blue-300', label: 'Document' },
  VERIFICATION_COMPLETED: { bg: 'bg-emerald-500/20', text: 'text-emerald-300', label: 'Verified' },
};

const INITIAL_FORM_STATE = {
  type: 'ROYALTY_DISPUTE',
  priority: 'MEDIUM',
  title: '',
  description: '',
  amount_disputed: '',
  currency: 'USD',
  claimant_name: '',
  claimant_email: '',
  respondent_name: '',
  respondent_email: '',
};

// --- Badge Component ---
const Badge = ({ text, colorClass }) => (
  <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium border ${colorClass}`}>
    {text}
  </span>
);

// --- Stat Card ---
const StatCard = ({ title, value, icon, color, testId }) => (
  <div data-testid={testId} className={`bg-gradient-to-br ${color} rounded-xl p-4 text-white shadow-md`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-white/80">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
      </div>
      <div className="text-3xl">{icon}</div>
    </div>
  </div>
);

// --- Disputes Tab ---
const DisputesTab = ({ stats, disputes }) => (
  <div data-testid="disputes-tab-content" className="space-y-4">
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
      <StatCard title="Open Disputes" value={stats?.dispute_stats?.open_disputes || 0} icon="🟠" color="from-amber-500 to-orange-500" testId="stat-open-disputes" />
      <StatCard title="Under Review" value={stats?.dispute_stats?.under_review || 0} icon="🔍" color="from-yellow-500 to-amber-500" testId="stat-under-review" />
      <StatCard title="Resolved" value={stats?.dispute_stats?.resolved_disputes || 0} icon="✅" color="from-emerald-500 to-teal-500" testId="stat-resolved" />
      <StatCard title="Total Disputed" value={`$${(stats?.dispute_stats?.total_amount_disputed || 0).toLocaleString()}`} icon="💰" color="from-sky-500 to-blue-500" testId="stat-total-amount" />
    </div>

    <div className="bg-white/5 rounded-xl p-4 border border-sky-500/20 overflow-x-auto">
      <table data-testid="disputes-table" className="min-w-full text-sm text-left text-gray-300">
        <thead>
          <tr className="border-b border-sky-500/20">
            <th className="py-2 px-3">Dispute #</th>
            <th className="py-2 px-3">Title</th>
            <th className="py-2 px-3">Type</th>
            <th className="py-2 px-3">Status</th>
            <th className="py-2 px-3">Priority</th>
            <th className="py-2 px-3">Amount</th>
            <th className="py-2 px-3">Claimant</th>
            <th className="py-2 px-3">Created</th>
          </tr>
        </thead>
        <tbody>
          {disputes.map(d => (
            <tr key={d.id} data-testid={`dispute-row-${d.id}`} className="border-b border-white/5 hover:bg-white/5 transition-colors">
              <td className="py-2 px-3 text-xs text-sky-300 font-mono">{d.dispute_number || d.id?.slice(0, 8)}</td>
              <td className="py-2 px-3 max-w-xs truncate">{d.title}</td>
              <td className="py-2 px-3 text-xs">{DISPUTE_TYPES.find(t => t.value === d.type)?.label || d.type}</td>
              <td className="py-2 px-3"><Badge text={d.status} colorClass={STATUS_COLORS[d.status] || 'bg-gray-500/20 text-gray-300'} /></td>
              <td className="py-2 px-3"><Badge text={d.priority} colorClass={PRIORITIES.find(p => p.value === d.priority)?.color || ''} /></td>
              <td className="py-2 px-3 text-xs font-mono">{d.amount_disputed ? `$${d.amount_disputed.toLocaleString()}` : '-'}</td>
              <td className="py-2 px-3 text-xs">{d.claimant?.name}</td>
              <td className="py-2 px-3 text-xs text-gray-400">{d.created_at ? new Date(d.created_at).toLocaleDateString() : ''}</td>
            </tr>
          ))}
          {disputes.length === 0 && (
            <tr><td colSpan={8} className="py-8 text-center text-gray-400">No disputes found. Create one to get started.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  </div>
);

// --- Audit Trail Tab ---
const AuditTrailTab = ({ stats, auditEntries }) => {
  const [filterEventType, setFilterEventType] = useState('');
  const [expandedRow, setExpandedRow] = useState(null);

  const uniqueEventTypes = [...new Set(auditEntries.map(e => e.event_type))];

  const filteredEntries = filterEventType
    ? auditEntries.filter(e => e.event_type === filterEventType)
    : auditEntries;

  return (
    <div data-testid="audit-tab-content" className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <StatCard title="Audit Entries" value={stats?.audit_stats?.total_entries || 0} icon="🧾" color="from-indigo-500 to-purple-500" testId="stat-audit-entries" />
        <StatCard title="Last 24h" value={stats?.audit_stats?.entries_last_24h || 0} icon="🌙" color="from-sky-500 to-cyan-500" testId="stat-last-24h" />
        <StatCard title="Chain Verified" value={stats?.chain_verified ? 'Yes' : 'Check'} icon="🔗" color="from-emerald-500 to-teal-500" testId="stat-chain-verified" />
      </div>

      {/* Filters */}
      <div data-testid="audit-filters" className="flex flex-wrap gap-3 items-center">
        <span className="text-sm text-gray-400">Filter by event:</span>
        <select
          data-testid="audit-event-type-filter"
          value={filterEventType}
          onChange={e => { setFilterEventType(e.target.value); setExpandedRow(null); }}
          className="bg-white/10 text-white border border-sky-500/30 rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="" className="bg-slate-900">All Events</option>
          {uniqueEventTypes.map(et => (
            <option key={et} value={et} className="bg-slate-900">{EVENT_TYPE_STYLES[et]?.label || et}</option>
          ))}
        </select>
        <span className="text-xs text-gray-500">Showing {filteredEntries.length} of {auditEntries.length}</span>
      </div>

      <div className="bg-white/5 rounded-xl p-4 border border-sky-500/20 overflow-x-auto">
        <table data-testid="audit-table" className="min-w-full text-sm text-left text-gray-300">
          <thead>
            <tr className="border-b border-sky-500/20">
              <th className="py-2 px-3 w-8"></th>
              <th className="py-2 px-3">Event</th>
              <th className="py-2 px-3">Entity</th>
              <th className="py-2 px-3">Actor</th>
              <th className="py-2 px-3">Description</th>
              <th className="py-2 px-3">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {filteredEntries.map(e => {
              const style = EVENT_TYPE_STYLES[e.event_type] || { bg: 'bg-gray-500/20', text: 'text-gray-300', label: e.event_type };
              const isExpanded = expandedRow === e.id;
              return (
                <React.Fragment key={e.id}>
                  <tr
                    data-testid={`audit-row-${e.id}`}
                    onClick={() => setExpandedRow(isExpanded ? null : e.id)}
                    className="border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors"
                  >
                    <td className="py-2 px-3 text-xs text-gray-500">{isExpanded ? '▼' : '▶'}</td>
                    <td className="py-2 px-3">
                      <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${style.bg} ${style.text}`}>
                        {style.label}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-xs font-mono text-sky-300">{e.entity_id}</td>
                    <td className="py-2 px-3 text-xs">{e.actor_name}</td>
                    <td className="py-2 px-3 text-xs max-w-xs truncate">{e.action_description}</td>
                    <td className="py-2 px-3 text-xs text-gray-400">{e.timestamp ? new Date(e.timestamp).toLocaleString() : ''}</td>
                  </tr>
                  {isExpanded && (
                    <tr data-testid={`audit-detail-${e.id}`} className="bg-white/[0.02]">
                      <td colSpan={6} className="px-6 py-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                          <div>
                            <p className="text-gray-500 mb-1">Entity Type</p>
                            <p className="text-gray-300">{e.entity_type}</p>
                          </div>
                          <div>
                            <p className="text-gray-500 mb-1">Actor ID</p>
                            <p className="text-gray-300 font-mono">{e.actor_id}</p>
                          </div>
                          {e.change_summary && (
                            <div className="md:col-span-2">
                              <p className="text-gray-500 mb-1">Change Summary</p>
                              <p className="text-gray-300">{e.change_summary}</p>
                            </div>
                          )}
                          {e.metadata && Object.keys(e.metadata).length > 0 && (
                            <div className="md:col-span-2">
                              <p className="text-gray-500 mb-1">Metadata</p>
                              <pre className="text-gray-300 bg-black/20 rounded p-2 overflow-x-auto">{JSON.stringify(e.metadata, null, 2)}</pre>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
            {filteredEntries.length === 0 && (
              <tr><td colSpan={6} className="py-8 text-center text-gray-400">No audit entries found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// --- Create Dispute Form ---
const CreateDisputeForm = ({ onCreated }) => {
  const [form, setForm] = useState(INITIAL_FORM_STATE);
  const [submitting, setSubmitting] = useState(false);

  const set = (field, value) => setForm(prev => ({ ...prev, [field]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        amount_disputed: form.amount_disputed ? parseFloat(form.amount_disputed) : undefined,
        respondent_name: form.respondent_name || undefined,
        respondent_email: form.respondent_email || undefined,
      };
      const res = await fetch(`${API}/api/qldb/disputes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        toast.success('Dispute created and recorded in ledger');
        setForm(INITIAL_FORM_STATE);
        onCreated();
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || 'Failed to create dispute');
      }
    } catch (err) {
      console.error('Error creating dispute', err);
      toast.error('Failed to create dispute');
    }
    setSubmitting(false);
  };

  const inputClass = "w-full bg-white/10 text-white border border-sky-500/30 rounded-lg px-3 py-2 placeholder-gray-500 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400/50 transition-colors";
  const labelClass = "block text-sm text-gray-300 mb-1";

  return (
    <div data-testid="create-dispute-form-container" className="max-w-2xl bg-white/5 rounded-xl p-6 border border-sky-500/20">
      <h2 className="text-xl font-semibold text-white mb-6">Create New Dispute</h2>
      <form data-testid="create-dispute-form" onSubmit={handleSubmit} className="space-y-5">
        {/* Title */}
        <div>
          <label className={labelClass}>Title *</label>
          <input data-testid="input-title" type="text" value={form.title} onChange={e => set('title', e.target.value)} className={inputClass} placeholder="Brief description of the dispute" required />
        </div>

        {/* Description */}
        <div>
          <label className={labelClass}>Description *</label>
          <textarea data-testid="input-description" value={form.description} onChange={e => set('description', e.target.value)} className={`${inputClass} min-h-[100px]`} placeholder="Detailed explanation of the dispute..." required />
        </div>

        {/* Type + Priority */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Dispute Type *</label>
            <select data-testid="select-type" value={form.type} onChange={e => set('type', e.target.value)} className={inputClass}>
              {DISPUTE_TYPES.map(t => (
                <option key={t.value} value={t.value} className="bg-slate-900">{t.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Priority *</label>
            <select data-testid="select-priority" value={form.priority} onChange={e => set('priority', e.target.value)} className={inputClass}>
              {PRIORITIES.map(p => (
                <option key={p.value} value={p.value} className="bg-slate-900">{p.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Amount + Currency */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Amount Disputed</label>
            <input data-testid="input-amount" type="number" step="0.01" min="0" value={form.amount_disputed} onChange={e => set('amount_disputed', e.target.value)} className={inputClass} placeholder="0.00" />
          </div>
          <div>
            <label className={labelClass}>Currency</label>
            <select data-testid="select-currency" value={form.currency} onChange={e => set('currency', e.target.value)} className={inputClass}>
              {['USD', 'EUR', 'GBP', 'ETH', 'BTC'].map(c => (
                <option key={c} value={c} className="bg-slate-900">{c}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Separator */}
        <div className="border-t border-sky-500/10 pt-4">
          <p className="text-sm text-gray-400 mb-3">Claimant Information</p>
        </div>

        {/* Claimant */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Claimant Name *</label>
            <input data-testid="input-claimant-name" type="text" value={form.claimant_name} onChange={e => set('claimant_name', e.target.value)} className={inputClass} placeholder="Full name" required />
          </div>
          <div>
            <label className={labelClass}>Claimant Email</label>
            <input data-testid="input-claimant-email" type="email" value={form.claimant_email} onChange={e => set('claimant_email', e.target.value)} className={inputClass} placeholder="email@example.com" />
          </div>
        </div>

        {/* Respondent */}
        <div className="border-t border-sky-500/10 pt-4">
          <p className="text-sm text-gray-400 mb-3">Respondent Information (optional)</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Respondent Name</label>
            <input data-testid="input-respondent-name" type="text" value={form.respondent_name} onChange={e => set('respondent_name', e.target.value)} className={inputClass} placeholder="Full name" />
          </div>
          <div>
            <label className={labelClass}>Respondent Email</label>
            <input data-testid="input-respondent-email" type="email" value={form.respondent_email} onChange={e => set('respondent_email', e.target.value)} className={inputClass} placeholder="email@example.com" />
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          data-testid="submit-dispute-btn"
          disabled={submitting}
          className="w-full px-4 py-2.5 bg-gradient-to-r from-sky-500 to-blue-600 text-white rounded-lg hover:from-sky-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all"
        >
          {submitting ? 'Creating...' : 'Create Dispute'}
        </button>
      </form>
    </div>
  );
};

// --- Main Dashboard ---
const QLDBDashboard = () => {
  const [activeTab, setActiveTab] = useState('disputes');
  const [stats, setStats] = useState(null);
  const [disputes, setDisputes] = useState([]);
  const [auditEntries, setAuditEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/qldb/dashboard`);
      if (res.ok) setStats(await res.json());
    } catch (err) {
      console.error('Error loading QLDB dashboard', err);
    }
  }, []);

  const fetchDisputes = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/qldb/disputes`);
      if (res.ok) {
        const data = await res.json();
        setDisputes(data.disputes || []);
      }
    } catch (err) {
      console.error('Error loading disputes', err);
    }
  }, []);

  const fetchAudit = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/qldb/audit`);
      if (res.ok) {
        const data = await res.json();
        setAuditEntries(data.entries || []);
      }
    } catch (err) {
      console.error('Error loading audit trail', err);
    }
  }, []);

  const refreshAll = useCallback(() => {
    fetchDashboard();
    fetchDisputes();
    fetchAudit();
  }, [fetchDashboard, fetchDisputes, fetchAudit]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await Promise.all([fetchDashboard(), fetchDisputes(), fetchAudit()]);
      setLoading(false);
    };
    load();
  }, [fetchDashboard, fetchDisputes, fetchAudit]);

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-sky-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-sky-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Dispute Ledger...</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'disputes', label: 'Disputes', count: disputes.length },
    { id: 'audit', label: 'Audit Trail', count: auditEntries.length },
    { id: 'create', label: 'New Dispute' },
  ];

  return (
    <div data-testid="qldb-dashboard" className="min-h-screen bg-gradient-to-br from-slate-900 via-sky-900 to-slate-900">
      <div className="bg-black/30 border-b border-sky-500/30">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Dispute Ledger</h1>
              <p className="text-sky-300 mt-1 text-sm">Dispute records and audit trail powered by PostgreSQL</p>
            </div>
            <button
              data-testid="refresh-dashboard-btn"
              onClick={refreshAll}
              className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all text-sm"
            >
              Refresh
            </button>
          </div>

          <div className="flex gap-2 mt-6 overflow-x-auto pb-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                data-testid={`tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 text-sm ${
                  activeTab === tab.id
                    ? 'bg-sky-600 text-white'
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                {tab.label}
                {tab.count !== undefined && (
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${activeTab === tab.id ? 'bg-white/20' : 'bg-white/10'}`}>
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'disputes' && <DisputesTab stats={stats} disputes={disputes} />}
        {activeTab === 'audit' && <AuditTrailTab stats={stats} auditEntries={auditEntries} />}
        {activeTab === 'create' && <CreateDisputeForm onCreated={refreshAll} />}
      </div>
    </div>
  );
};

export default QLDBDashboard;
