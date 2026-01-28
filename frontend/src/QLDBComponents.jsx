import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const QLDBDashboard = () => {
  const [activeTab, setActiveTab] = useState('disputes');
  const [stats, setStats] = useState(null);
  const [disputes, setDisputes] = useState([]);
  const [auditEntries, setAuditEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newDispute, setNewDispute] = useState({
    type: 'ROYALTY_DISPUTE',
    title: '',
    description: '',
    amount_disputed: '',
    currency: 'USD',
    claimant_name: '',
    claimant_email: '',
  });

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${API}/api/qldb/dashboard`);
      if (res.ok) {
        setStats(await res.json());
      }
    } catch (err) {
      console.error('Error loading QLDB dashboard', err);
      toast.error('Failed to load QLDB dashboard');
    }
  };

  const fetchDisputes = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/qldb/disputes`);
      if (res.ok) {
        const data = await res.json();
        setDisputes(data.disputes || []);
      }
    } catch (err) {
      console.error('Error loading disputes', err);
      toast.error('Failed to load disputes');
    }
    setLoading(false);
  };

  const fetchAudit = async () => {
    try {
      const res = await fetch(`${API}/api/qldb/audit`);
      if (res.ok) {
        const data = await res.json();
        setAuditEntries(data.entries || []);
      }
    } catch (err) {
      console.error('Error loading audit trail', err);
      toast.error('Failed to load audit trail');
    }
  };

  useEffect(() => {
    fetchDashboard();
    fetchDisputes();
    fetchAudit();
  }, []);

  const handleCreateDispute = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newDispute,
        amount_disputed: newDispute.amount_disputed ? parseFloat(newDispute.amount_disputed) : undefined,
      };
      const res = await fetch(`${API}/api/qldb/disputes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        toast.success('Dispute created and recorded in ledger');
        setNewDispute({
          type: 'ROYALTY_DISPUTE',
          title: '',
          description: '',
          amount_disputed: '',
          currency: 'USD',
          claimant_name: '',
          claimant_email: '',
        });
        fetchDashboard();
        fetchDisputes();
      } else {
        toast.error('Failed to create dispute');
      }
    } catch (err) {
      console.error('Error creating dispute', err);
      toast.error('Failed to create dispute');
    }
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-sky-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-sky-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading QLDB Dispute Ledger...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-sky-900 to-slate-900">
      <div className="bg-black/30 border-b border-sky-500/30">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span className="text-4xl">📘</span>
                AWS QLDB Dispute Ledger
              </h1>
              <p className="text-sky-300 mt-1">Immutable dispute records and cryptographic audit trail</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={fetchDashboard}
                className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all"
              >
                ↻ Refresh
              </button>
            </div>
          </div>

          <div className="flex gap-2 mt-6 overflow-x-auto pb-2">
            {[
              { id: 'disputes', label: 'Disputes', icon: '⚖️' },
              { id: 'audit', label: 'Audit Trail', icon: '🔐' },
              { id: 'create', label: 'New Dispute', icon: '➕' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'bg-sky-600 text-white'
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'disputes' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <StatCard
                title="Open Disputes"
                value={stats?.dispute_stats?.open_disputes || 0}
                icon="🟠"
                color="from-amber-500 to-orange-500"
              />
              <StatCard
                title="Resolved Disputes"
                value={stats?.dispute_stats?.resolved_disputes || 0}
                icon="✅"
                color="from-emerald-500 to-teal-500"
              />
              <StatCard
                title="Total Amount Disputed"
                value={`$${(stats?.dispute_stats?.total_amount_disputed || 0).toLocaleString()}`}
                icon="💰"
                color="from-sky-500 to-blue-500"
              />
            </div>

            <div className="bg-white/5 rounded-xl p-4 border border-sky-500/20 overflow-x-auto">
              <table className="min-w-full text-sm text-left text-gray-300">
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
                    <tr key={d.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-2 px-3 text-xs text-sky-300">{d.dispute_number || d.id}</td>
                      <td className="py-2 px-3 max-w-xs truncate">{d.title}</td>
                      <td className="py-2 px-3 text-xs">{d.type}</td>
                      <td className="py-2 px-3 text-xs">{d.status}</td>
                      <td className="py-2 px-3 text-xs">{d.priority}</td>
                      <td className="py-2 px-3 text-xs">{d.amount_disputed ? `$${d.amount_disputed.toLocaleString()}` : '-'}</td>
                      <td className="py-2 px-3 text-xs">{d.claimant?.name}</td>
                      <td className="py-2 px-3 text-xs">{d.created_at ? new Date(d.created_at).toLocaleString() : ''}</td>
                    </tr>
                  ))}
                  {disputes.length === 0 && (
                    <tr>
                      <td colSpan={8} className="py-4 text-center text-gray-400">
                        No disputes found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <StatCard
                title="Audit Entries"
                value={stats?.audit_stats?.total_entries || 0}
                icon="🧾"
                color="from-indigo-500 to-purple-500"
              />
              <StatCard
                title="Last 24h"
                value={stats?.audit_stats?.entries_last_24h || 0}
                icon="🌙"
                color="from-sky-500 to-cyan-500"
              />
              <StatCard
                title="Chain Verified"
                value={stats?.chain_verified ? 'Yes' : 'Check'}
                icon="🔗"
                color="from-emerald-500 to-teal-500"
              />
            </div>

            <div className="bg-white/5 rounded-xl p-4 border border-sky-500/20 overflow-x-auto">
              <table className="min-w-full text-sm text-left text-gray-300">
                <thead>
                  <tr className="border-b border-sky-500/20">
                    <th className="py-2 px-3">Event</th>
                    <th className="py-2 px-3">Entity</th>
                    <th className="py-2 px-3">Actor</th>
                    <th className="py-2 px-3">Description</th>
                    <th className="py-2 px-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {auditEntries.map(e => (
                    <tr key={e.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-2 px-3 text-xs">{e.event_type}</td>
                      <td className="py-2 px-3 text-xs">{e.entity_type} {e.entity_id}</td>
                      <td className="py-2 px-3 text-xs">{e.actor_name}</td>
                      <td className="py-2 px-3 text-xs max-w-xs truncate">{e.action_description}</td>
                      <td className="py-2 px-3 text-xs">{e.timestamp ? new Date(e.timestamp).toLocaleString() : ''}</td>
                    </tr>
                  ))}
                  {auditEntries.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-4 text-center text-gray-400">
                        No audit entries found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'create' && (
          <div className="max-w-2xl bg-white/5 rounded-xl p-6 border border-sky-500/20">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <span>➕</span> Create New Dispute
            </h2>
            <form onSubmit={handleCreateDispute} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-1">Title</label>
                <input
                  type="text"
                  value={newDispute.title}
                  onChange={e => setNewDispute(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full bg-white/10 text-white border border-sky-500/30 rounded-lg px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Description</label>
                <textarea
                  value={newDispute.description}
                  onChange={e => setNewDispute(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full bg-white/10 text-white border border-sky-500/30 rounded-lg px-3 py-2 min-h-[100px]"
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Type</label>
                  <select
                    value={newDispute.type}
                    onChange={e => setNewDispute(prev => ({ ...prev, type: e.target.value }))}
                    className="w-full bg-white/10 text-white border border-sky-500/30 rounded-lg px-3 py-2"
                  >
                    <option value="ROYALTY_DISPUTE" className="bg-slate-900">Royalty Dispute</option>
                    <option value="CONTRACT_DISPUTE" className="bg-slate-900">Contract Dispute</option>
                    <option value="PAYMENT_DISPUTE" className="bg-slate-900">Payment Dispute</option>
                    <option value="COPYRIGHT_CLAIM" className="bg-slate-900">Copyright Claim</option>
                    <option value="LICENSING_ISSUE" className="bg-slate-900">Licensing Issue</option>
                    <option value="OTHER" className="bg-slate-900">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Amount Disputed</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newDispute.amount_disputed}
                    onChange={e => setNewDispute(prev => ({ ...prev, amount_disputed: e.target.value }))}
                    className="w-full bg-white/10 text-white border border-sky-500/30 rounded-lg px-3 py-2"
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Claimant Name</label>
                  <input
                    type="text"
                    value={newDispute.claimant_name}
                    onChange={e => setNewDispute(prev => ({ ...prev, claimant_name: e.target.value }))}
                    className="w-full bg-white/10 text-white border border-sky-500/30 rounded-lg px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-300 mb-1">Claimant Email</label>
                  <input
                    type="email"
                    value={newDispute.claimant_email}
                    onChange={e => setNewDispute(prev => ({ ...prev, claimant_email: e.target.value }))}
                    className="w-full bg-white/10 text-white border border-sky-500/30 rounded-lg px-3 py-2"
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full px-4 py-2 bg-gradient-to-r from-sky-500 to-blue-600 text-white rounded-lg hover:from-sky-600 hover:to-blue-700"
              >
                Create Dispute
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }) => (
  <div className={`bg-gradient-to-br ${color} rounded-xl p-4 text-white shadow-md`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-white/80">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
      </div>
      <div className="text-3xl">{icon}</div>
    </div>
  </div>
);

export default QLDBDashboard;
