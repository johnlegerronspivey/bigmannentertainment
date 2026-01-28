import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const GuardDutyDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ severity: '', status: '' });

  useEffect(() => {
    fetchDashboard();
    fetchFindings();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${API}/api/guardduty/dashboard`);
      if (res.ok) {
        setStats(await res.json());
      }
    } catch (err) {
      console.error('Error loading GuardDuty dashboard', err);
      toast.error('Failed to load GuardDuty dashboard');
    }
  };

  const fetchFindings = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.status) params.append('status', filters.status);
      const res = await fetch(`${API}/api/guardduty/findings?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setFindings(data.findings || []);
      }
    } catch (err) {
      console.error('Error loading GuardDuty findings', err);
      toast.error('Failed to load GuardDuty findings');
    }
    setLoading(false);
  };

  const handleStatusChange = async (findingId, action) => {
    try {
      const endpointMap = {
        acknowledge: 'acknowledge',
        resolve: 'resolve',
        archive: 'archive',
      };
      const endpoint = endpointMap[action];
      if (!endpoint) return;

      const method = action === 'archive' ? 'POST' : 'POST';
      const res = await fetch(`${API}/api/guardduty/findings/${findingId}/${endpoint}`, {
        method,
      });
      if (res.ok) {
        toast.success(`Finding ${action}d`);
        fetchDashboard();
        fetchFindings();
      } else {
        toast.error('Failed to update finding');
      }
    } catch (err) {
      console.error('Error updating finding', err);
      toast.error('Failed to update finding');
    }
  };

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading GuardDuty Threat Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900">
      <div className="bg-black/30 border-b border-emerald-500/30">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span className="text-4xl">🛡️</span>
                AWS GuardDuty Threat Detection
              </h1>
              <p className="text-emerald-300 mt-1">Real-time threat detection and GuardDuty findings overview</p>
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
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'findings', label: 'Findings', icon: '🔍' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'bg-emerald-600 text-white'
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
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard title="Total Detectors" value={stats?.total_detectors || 0} icon="🛰️" color="from-emerald-500 to-teal-500" />
              <StatCard title="Active Detectors" value={stats?.active_detectors || 0} icon="✅" color="from-green-500 to-emerald-500" />
              <StatCard title="Total Findings" value={stats?.total_findings || 0} icon="🔍" color="from-sky-500 to-blue-500" />
              <StatCard title="New Findings" value={stats?.new_findings || 0} icon="✨" color="from-indigo-500 to-purple-500" />
            </div>
          </div>
        )}

        {activeTab === 'findings' && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-4 items-end">
              <div>
                <label className="text-gray-300 text-sm block mb-1">Severity</label>
                <select
                  value={filters.severity}
                  onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
                  className="bg-white/10 text-white border border-emerald-500/30 rounded-lg px-3 py-2"
                >
                  <option value="" className="bg-slate-900">All</option>
                  <option value="CRITICAL" className="bg-slate-900">Critical</option>
                  <option value="HIGH" className="bg-slate-900">High</option>
                  <option value="MEDIUM" className="bg-slate-900">Medium</option>
                  <option value="LOW" className="bg-slate-900">Low</option>
                </select>
              </div>
              <div>
                <label className="text-gray-300 text-sm block mb-1">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                  className="bg-white/10 text-white border border-emerald-500/30 rounded-lg px-3 py-2"
                >
                  <option value="" className="bg-slate-900">All</option>
                  <option value="NEW" className="bg-slate-900">New</option>
                  <option value="ACKNOWLEDGED" className="bg-slate-900">Acknowledged</option>
                  <option value="RESOLVED" className="bg-slate-900">Resolved</option>
                  <option value="ARCHIVED" className="bg-slate-900">Archived</option>
                </select>
              </div>
              <button
                onClick={fetchFindings}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
              >
                Apply Filters
              </button>
            </div>

            <div className="bg-white/5 rounded-xl p-4 border border-emerald-500/20 overflow-x-auto">
              <table className="min-w-full text-sm text-left text-gray-300">
                <thead>
                  <tr className="border-b border-emerald-500/20">
                    <th className="py-2 px-3">Type</th>
                    <th className="py-2 px-3">Title</th>
                    <th className="py-2 px-3">Severity</th>
                    <th className="py-2 px-3">Status</th>
                    <th className="py-2 px-3">Resource</th>
                    <th className="py-2 px-3">Created</th>
                    <th className="py-2 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.map(f => (
                    <tr key={f.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-2 px-3 text-xs text-emerald-300">{f.type}</td>
                      <td className="py-2 px-3 max-w-xs truncate">{f.title}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${severityClass(f.severity_level)}`}>
                          {f.severity_level}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-xs">{f.status}</td>
                      <td className="py-2 px-3 text-xs">
                        {f.resource?.resource_type} {f.resource?.instance_id || f.resource?.bucket_name || ''}
                      </td>
                      <td className="py-2 px-3 text-xs">
                        {f.created_at ? new Date(f.created_at).toLocaleString() : ''}
                      </td>
                      <td className="py-2 px-3 text-right space-x-1">
                        <button
                          onClick={() => handleStatusChange(f.finding_id || f.id, 'acknowledge')}
                          className="px-2 py-1 text-xs bg-amber-600 text-white rounded hover:bg-amber-700"
                        >
                          Ack
                        </button>
                        <button
                          onClick={() => handleStatusChange(f.finding_id || f.id, 'resolve')}
                          className="px-2 py-1 text-xs bg-emerald-600 text-white rounded hover:bg-emerald-700"
                        >
                          Resolve
                        </button>
                        <button
                          onClick={() => handleStatusChange(f.finding_id || f.id, 'archive')}
                          className="px-2 py-1 text-xs bg-slate-600 text-white rounded hover:bg-slate-700"
                        >
                          Archive
                        </button>
                      </td>
                    </tr>
                  ))}
                  {findings.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-4 text-center text-gray-400">
                        No findings match the current filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
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

const severityClass = (level) => {
  switch (level) {
    case 'CRITICAL':
      return 'bg-red-600/80';
    case 'HIGH':
      return 'bg-orange-500/80';
    case 'MEDIUM':
      return 'bg-yellow-500/80';
    case 'LOW':
    default:
      return 'bg-blue-500/80';
  }
};

export default GuardDutyDashboard;
