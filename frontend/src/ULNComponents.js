import React, { useState, useEffect } from 'react';
import { BlockchainIntegrationDashboard, BlockchainContractsViewer, BlockchainAuditTrail } from './BlockchainComponents';
import { EnhancedEditLabelModal } from './EnhancedULNComponents';
import { BulkLabelEditor, AdvancedSearch, LabelDataExporter } from './ULNAdminComponents';
import { BlockchainLedger } from './uln/BlockchainLedger';
import { AnalyticsDashboard } from './uln/AnalyticsDashboard';
import { OnboardingWizard } from './uln/OnboardingWizard';
import { InterLabelMessaging } from './uln/InterLabelMessaging';

// Get API URL from environment
const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// ===== UNIFIED LABEL NETWORK (ULN) MAIN DASHBOARD =====

export const ULNDashboard = () => {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [myLabels, setMyLabels] = useState([]);
  const [activeLabel, setActiveLabel] = useState(null);
  const [showLabelSwitcher, setShowLabelSwitcher] = useState(false);

  useEffect(() => {
    fetchDashboardStats();
    fetchMyLabels();
  }, []);

  const fetchMyLabels = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      const res = await fetch(`${API}/api/uln/me/labels`, {
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      if (res.ok) {
        const data = await res.json();
        setMyLabels(data.labels || []);
        if (data.labels?.length > 0 && !activeLabel) {
          setActiveLabel(data.labels[0]);
        }
      }
    } catch (e) {
      console.error('Failed to load labels:', e);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please log in.');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API}/api/uln/dashboard/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardStats(data.dashboard_stats);
        setError('');
      } else if (response.status === 401) {
        setError('Session expired. Please log in again.');
        localStorage.removeItem('token');
      } else {
        setError('Failed to load ULN dashboard data');
      }
    } catch (error) {
      console.error('ULN dashboard fetch error:', error);
      setError('Error connecting to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header with Label Switcher */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Unified Label Network</h1>
            <p className="text-lg text-gray-600">
              Complete ecosystem for cross-label collaboration, content sharing, and royalty distribution
            </p>
          </div>
          {/* Label Switcher */}
          {myLabels.length > 0 && (
            <div className="relative" data-testid="label-switcher-container">
              <button
                onClick={() => setShowLabelSwitcher(!showLabelSwitcher)}
                className="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-4 py-2.5 shadow-sm hover:shadow transition min-w-[220px]"
                data-testid="label-switcher-btn"
              >
                <span className="w-8 h-8 rounded-lg bg-purple-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                  {(activeLabel?.name || '?')[0].toUpperCase()}
                </span>
                <div className="text-left flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">{activeLabel?.name || 'Select Label'}</p>
                  <p className="text-[10px] text-gray-500 capitalize">{activeLabel?.role || ''} &middot; {activeLabel?.member_count || 0} members</p>
                </div>
                <svg className={`w-4 h-4 text-gray-400 transition ${showLabelSwitcher ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              </button>
              {showLabelSwitcher && (
                <div className="absolute right-0 top-full mt-1 w-72 bg-white border border-gray-200 rounded-xl shadow-lg z-50 max-h-80 overflow-y-auto" data-testid="label-switcher-dropdown">
                  <div className="p-2">
                    <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wide px-2 py-1">My Labels ({myLabels.length})</p>
                    {myLabels.map((lbl) => (
                      <button
                        key={lbl.label_id}
                        onClick={() => { setActiveLabel(lbl); setShowLabelSwitcher(false); }}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition ${
                          activeLabel?.label_id === lbl.label_id ? 'bg-purple-50 ring-1 ring-purple-200' : 'hover:bg-gray-50'
                        }`}
                        data-testid={`label-switch-${lbl.label_id}`}
                      >
                        <span className="w-7 h-7 rounded-md bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-[10px] shrink-0">
                          {(lbl.name || '?')[0].toUpperCase()}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-gray-800 truncate">{lbl.name}</p>
                          <p className="text-[10px] text-gray-400 capitalize">{lbl.role} &middot; {lbl.label_type}</p>
                        </div>
                        {activeLabel?.label_id === lbl.label_id && (
                          <span className="w-2 h-2 rounded-full bg-purple-600 shrink-0"></span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <nav className="flex flex-wrap gap-2 px-6 py-4">
            {['overview', 'labels', 'members', 'catalog', 'distribution', 'audit', 'content', 'royalties', 'dao', 'blockchain', 'analytics', 'onboarding', 'messaging'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                data-testid={`uln-tab-${tab}`}
                className={`capitalize font-medium py-2 px-4 rounded-md transition-colors ${
                  activeTab === tab 
                    ? 'bg-purple-100 text-purple-700' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab === 'dao' ? 'DAO Governance' : tab === 'onboarding' ? 'Register Label' : tab === 'messaging' ? 'Messages' : tab === 'members' ? 'Members' : tab === 'catalog' ? 'Catalog' : tab === 'distribution' ? 'Distribution' : tab === 'audit' ? 'Audit Snapshot' : tab.replace('_', ' ')}
              </button>
            ))}
          </nav>
        </div>

        {/* Dashboard Content */}
        {dashboardStats && (
          <>
            {activeTab === 'overview' && (
              <ULNOverview stats={dashboardStats} />
            )}
            {activeTab === 'labels' && (
              <LabelHub />
            )}
            {activeTab === 'members' && (
              <LabelMembers activeLabel={activeLabel} onMemberChange={() => fetchMyLabels()} />
            )}
            {activeTab === 'catalog' && (
              <LabelCatalog activeLabel={activeLabel} />
            )}
            {activeTab === 'distribution' && (
              <LabelDistributionStatus activeLabel={activeLabel} />
            )}
            {activeTab === 'audit' && (
              <LabelAuditSnapshot activeLabel={activeLabel} />
            )}
            {activeTab === 'content' && (
              <CrossLabelContentSharing />
            )}
            {activeTab === 'royalties' && (
              <RoyaltyPoolManagement />
            )}
            {activeTab === 'dao' && (
              <DAOGovernance />
            )}
            {activeTab === 'blockchain' && (
              <div className="bg-slate-900 rounded-lg p-6">
                <BlockchainLedger />
              </div>
            )}
            {activeTab === 'analytics' && (
              <div className="bg-slate-900 rounded-lg p-6">
                <AnalyticsDashboard />
              </div>
            )}
            {activeTab === 'onboarding' && (
              <div className="bg-slate-900 rounded-lg p-6">
                <OnboardingWizard />
              </div>
            )}
            {activeTab === 'messaging' && (
              <div className="bg-slate-900 rounded-lg p-6">
                <InterLabelMessaging />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};


// ===== LABEL MEMBERS COMPONENT =====

const ROLE_COLORS = {
  owner: 'bg-amber-100 text-amber-800',
  admin: 'bg-blue-100 text-blue-800',
  a_and_r: 'bg-green-100 text-green-800',
  viewer: 'bg-gray-100 text-gray-700',
};

const ROLE_LABELS = { owner: 'Owner', admin: 'Admin', a_and_r: 'A&R', viewer: 'Viewer' };

const LabelMembers = ({ activeLabel, onMemberChange }) => {
  const [members, setMembers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [addEmail, setAddEmail] = useState('');
  const [addRole, setAddRole] = useState('viewer');
  const [addError, setAddError] = useState('');
  const [addLoading, setAddLoading] = useState(false);
  const [editingMember, setEditingMember] = useState(null);
  const [myRole, setMyRole] = useState(null);

  const token = localStorage.getItem('token');
  const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    if (activeLabel) {
      fetchMembers();
      fetchMyRole();
    }
    fetchRoles();
  }, [activeLabel?.label_id]);

  const fetchMembers = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/members`, { headers });
      if (res.ok) {
        const data = await res.json();
        setMembers(data.members || []);
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const fetchMyRole = async () => {
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/my-role`, { headers });
      if (res.ok) {
        const data = await res.json();
        setMyRole(data.role);
      }
    } catch (e) { console.error(e); }
  };

  const fetchRoles = async () => {
    try {
      const res = await fetch(`${API}/api/uln/roles`, { headers });
      if (res.ok) {
        const data = await res.json();
        setRoles(data.roles || []);
      }
    } catch (e) { console.error(e); }
  };

  const handleAddMember = async () => {
    if (!addEmail.trim()) { setAddError('Enter an email address'); return; }
    setAddLoading(true);
    setAddError('');
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/members`, {
        method: 'POST', headers,
        body: JSON.stringify({ email: addEmail, role: addRole }),
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setShowAddModal(false);
        setAddEmail('');
        setAddRole('viewer');
        fetchMembers();
        if (onMemberChange) onMemberChange();
      } else {
        setAddError(data.detail || data.error || 'Failed to add member');
      }
    } catch (e) { setAddError('Network error'); }
    setAddLoading(false);
  };

  const handleChangeRole = async (userId, newRole) => {
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/members/${userId}/role`, {
        method: 'PUT', headers,
        body: JSON.stringify({ role: newRole }),
      });
      if (res.ok) {
        setEditingMember(null);
        fetchMembers();
        if (onMemberChange) onMemberChange();
      }
    } catch (e) { console.error(e); }
  };

  const handleRemove = async (userId) => {
    if (!window.confirm('Remove this member from the label?')) return;
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/members/${userId}`, {
        method: 'DELETE', headers,
      });
      if (res.ok) {
        fetchMembers();
        if (onMemberChange) onMemberChange();
      }
    } catch (e) { console.error(e); }
  };

  if (!activeLabel) {
    return (
      <div className="bg-white rounded-xl shadow p-8 text-center" data-testid="members-no-label">
        <p className="text-gray-500">Select a label from the switcher above to manage its members.</p>
      </div>
    );
  }

  const canManage = myRole === 'owner' || myRole === 'admin';
  const canChangeRoles = myRole === 'owner';

  return (
    <div className="space-y-6" data-testid="label-members-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Members</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium text-purple-700">{activeLabel.name}</span> &middot; {members.length} member{members.length !== 1 ? 's' : ''}
          </p>
        </div>
        {canManage && (
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-purple-700 transition"
            data-testid="add-member-btn"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
            Add Member
          </button>
        )}
      </div>

      {/* Members Table */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div></div>
        ) : members.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No members found.</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200" data-testid="members-table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Member</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Label Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                {canManage && <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {members.map((m) => (
                <tr key={m.user_id} className="hover:bg-gray-50 transition" data-testid={`member-row-${m.user_id}`}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <span className="w-9 h-9 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-sm">
                        {(m.full_name || m.email || '?')[0].toUpperCase()}
                      </span>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{m.full_name || 'Unknown'}</p>
                        <p className="text-xs text-gray-500">{m.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {editingMember === m.user_id ? (
                      <select
                        value={m.label_role}
                        onChange={(e) => handleChangeRole(m.user_id, e.target.value)}
                        className="text-sm border border-gray-300 rounded-lg px-2 py-1 focus:ring-2 focus:ring-purple-500"
                        data-testid={`role-select-${m.user_id}`}
                      >
                        {roles.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
                      </select>
                    ) : (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ROLE_COLORS[m.label_role] || ROLE_COLORS.viewer}`} data-testid={`role-badge-${m.user_id}`}>
                        {ROLE_LABELS[m.label_role] || m.label_role}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {m.joined_at ? new Date(m.joined_at).toLocaleDateString() : '—'}
                  </td>
                  {canManage && (
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                      {canChangeRoles && m.label_role !== 'owner' && (
                        <button
                          onClick={() => setEditingMember(editingMember === m.user_id ? null : m.user_id)}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                          data-testid={`edit-role-${m.user_id}`}
                        >
                          {editingMember === m.user_id ? 'Cancel' : 'Change Role'}
                        </button>
                      )}
                      {m.label_role !== 'owner' && (
                        <button
                          onClick={() => handleRemove(m.user_id)}
                          className="text-red-600 hover:text-red-800 font-medium"
                          data-testid={`remove-member-${m.user_id}`}
                        >
                          Remove
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Role Legend */}
      <div className="bg-white rounded-xl shadow p-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Role Permissions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {roles.map(r => (
            <div key={r.id} className="flex items-start gap-2">
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium mt-0.5 ${ROLE_COLORS[r.id] || ROLE_COLORS.viewer}`}>
                {r.label}
              </span>
              <p className="text-xs text-gray-500 leading-relaxed">{r.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Add Member Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowAddModal(false)}>
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()} data-testid="add-member-modal">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add Member to {activeLabel.name}</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input
                  type="email"
                  value={addEmail}
                  onChange={(e) => setAddEmail(e.target.value)}
                  placeholder="member@example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  data-testid="add-member-email"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  value={addRole}
                  onChange={(e) => setAddRole(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  data-testid="add-member-role"
                >
                  {roles.filter(r => r.id !== 'owner').map(r => <option key={r.id} value={r.id}>{r.label} — {r.description}</option>)}
                </select>
              </div>
              {addError && <p className="text-sm text-red-600" data-testid="add-member-error">{addError}</p>}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => { setShowAddModal(false); setAddError(''); }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddMember}
                  disabled={addLoading}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition disabled:opacity-50"
                  data-testid="confirm-add-member"
                >
                  {addLoading ? 'Adding...' : 'Add Member'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ===== ULN OVERVIEW COMPONENT =====

const ULNOverview = ({ stats }) => {
  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard 
          title="Connected Labels" 
          value={stats.total_labels} 
          subtitle={`${stats.active_labels} active`}
          icon="🏢" 
          color="bg-blue-500"
        />
        <MetricCard 
          title="Major Labels" 
          value={stats.major_labels || 0} 
          subtitle="Premium tier"
          icon="🌟" 
          color="bg-purple-500"
        />
        <MetricCard 
          title="Independent Labels" 
          value={stats.independent_labels || 0} 
          subtitle="Creative freedom"
          icon="🎵" 
          color="bg-green-500"
        />
        <MetricCard 
          title="Cross-Label Collaborations" 
          value={stats.cross_collaborations || 0} 
          subtitle="Active partnerships"
          icon="🤝" 
          color="bg-orange-500"
        />
        <MetricCard 
          title="Smart Contracts" 
          value={stats.smart_contracts || 0} 
          subtitle="Blockchain enabled"
          icon="📋" 
          color="bg-teal-500"
        />
        <MetricCard 
          title="DAO Proposals" 
          value={stats.total_dao_proposals} 
          subtitle="Governance actions"
          icon="🗳️" 
          color="bg-red-500"
        />
      </div>

      {/* Geographic Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">🌍 Global Distribution</h3>
          <div className="space-y-3">
            {Object.entries(stats.labels_by_territory || {}).map(([territory, count]) => (
              <div key={territory} className="flex justify-between items-center">
                <span className="font-medium">{territory}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full" 
                      style={{ width: `${(count / stats.total_labels * 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">📈 Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <div>
                <div className="font-medium">New Registrations</div>
                <div className="text-sm text-gray-600">Last 30 days</div>
              </div>
              <div className="text-blue-600 font-bold text-xl">
                {stats.recent_registrations || 0}
              </div>
            </div>
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <div>
                <div className="font-medium">Content Shares</div>
                <div className="text-sm text-gray-600">Last 30 days</div>
              </div>
              <div className="text-green-600 font-bold text-xl">
                {stats.recent_content_shares || 0}
              </div>
            </div>
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
              <div>
                <div className="font-medium">DAO Proposals</div>
                <div className="text-sm text-gray-600">Last 30 days</div>
              </div>
              <div className="text-purple-600 font-bold text-xl">
                {stats.recent_proposals || 0}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">⚙️ System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-green-600 text-xl">✓</span>
            </div>
            <div className="font-medium">Label Registry</div>
            <div className="text-sm text-green-600">Operational</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-green-600 text-xl">✓</span>
            </div>
            <div className="font-medium">Royalty Engine</div>
            <div className="text-sm text-green-600">Processing</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-yellow-600 text-xl">⚠</span>
            </div>
            <div className="font-medium">Blockchain</div>
            <div className="text-sm text-yellow-600">Development Mode</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, subtitle, icon, color }) => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <div className="flex items-center">
      <div className={`${color} p-3 rounded-full text-white text-2xl`}>
        {icon}
      </div>
      <div className="ml-4">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
      </div>
    </div>
  </div>
);

// ===== LABEL HUB COMPONENT =====

const LabelHub = () => {
  const [labelHubData, setLabelHubData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    territory: '',
    genre: '',
    dao_affiliated: null
  });
  const [initializationStatus, setInitializationStatus] = useState('');
  const [editingLabel, setEditingLabel] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showBulkEditor, setShowBulkEditor] = useState(false);
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [showExporter, setShowExporter] = useState(false);
  const [selectedLabelsForBulk, setSelectedLabelsForBulk] = useState([]);

  useEffect(() => {
    fetchLabelHubData();
  }, [filters]);

  const fetchLabelHubData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const params = new URLSearchParams();
      if (filters.territory) params.append('territory', filters.territory);
      if (filters.genre) params.append('genre', filters.genre);
      if (filters.dao_affiliated !== null) params.append('dao_affiliated', filters.dao_affiliated);

      const response = await fetch(`${API}/api/uln/dashboard/label-hub?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setLabelHubData(data.label_hub_entries || []);
        setError('');
      } else {
        setError('Failed to load label hub data');
      }
    } catch (error) {
      console.error('Error fetching label hub data:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const initializeMajorLabels = async () => {
    try {
      setLoading(true);
      setInitializationStatus('Initializing major labels...');
      
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/uln/initialize-major-labels`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setInitializationStatus(`✅ Success! ${data.message}`);
        // Show detailed results
        if (data.statistics) {
          setInitializationStatus(
            `✅ Successfully initialized ${data.statistics.total_initialized} labels ` +
            `(${data.statistics.major_labels} major, ${data.statistics.independent_labels} independent)`
          );
        }
        
        // Refresh the label hub data
        setTimeout(() => {
          fetchLabelHubData();
          setInitializationStatus('');
        }, 3000);
        
      } else {
        setInitializationStatus(`❌ Error: ${data.error || 'Failed to initialize labels'}`);
        setTimeout(() => setInitializationStatus(''), 5000);
      }
    } catch (error) {
      console.error('Error initializing major labels:', error);
      setInitializationStatus('❌ Network error. Please try again.');
      setTimeout(() => setInitializationStatus(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleEditLabel = (label) => {
    setEditingLabel(label);
    setShowEditModal(true);
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setEditingLabel(null);
  };

  const handleLabelUpdated = () => {
    fetchLabelHubData();
    handleCloseEditModal();
  };

  if (loading) {
    return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold">🏢 Label Hub</h2>
          <p className="text-gray-600">Connected labels in the Unified Label Network</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button 
            onClick={() => setShowAdvancedSearch(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-1"
          >
            <span>🔍</span>
            <span>Advanced Search</span>
          </button>
          <button 
            onClick={() => {
              setSelectedLabelsForBulk(labelHubData);
              setShowBulkEditor(true);
            }}
            disabled={labelHubData.length === 0}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-1"
          >
            <span>📦</span>
            <span>Bulk Edit</span>
          </button>
          <button 
            onClick={() => setShowExporter(true)}
            disabled={labelHubData.length === 0}
            className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-1"
          >
            <span>📤</span>
            <span>Export</span>
          </button>
          <button 
            onClick={initializeMajorLabels}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-1"
          >
            <span>🏢</span>
            <span className="hidden sm:inline">Initialize Labels</span>
          </button>
          <button 
            onClick={() => window.location.href = '/uln/register'}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-1"
          >
            <span>+</span>
            <span>Register</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.territory}
            onChange={(e) => setFilters({...filters, territory: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Territories</option>
            <option value="US">United States</option>
            <option value="UK">United Kingdom</option>
            <option value="EU">European Union</option>
            <option value="CA">Canada</option>
            <option value="AU">Australia</option>
            <option value="JP">Japan</option>
          </select>
          
          <input
            type="text"
            placeholder="Filter by genre..."
            value={filters.genre}
            onChange={(e) => setFilters({...filters, genre: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <select
            value={filters.dao_affiliated === null ? '' : filters.dao_affiliated.toString()}
            onChange={(e) => setFilters({...filters, dao_affiliated: e.target.value === '' ? null : e.target.value === 'true'})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Labels</option>
            <option value="true">DAO Affiliated</option>
            <option value="false">Non-DAO</option>
          </select>

          <button
            onClick={() => setFilters({territory: '', genre: '', dao_affiliated: null})}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {initializationStatus && (
        <div className={`px-4 py-3 rounded ${
          initializationStatus.includes('✅') 
            ? 'bg-green-100 border border-green-400 text-green-700' 
            : initializationStatus.includes('❌')
            ? 'bg-red-100 border border-red-400 text-red-700'
            : 'bg-blue-100 border border-blue-400 text-blue-700'
        }`}>
          {initializationStatus}
        </div>
      )}

      {/* Labels Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {labelHubData.map((label) => (
          <LabelHubCard key={label.global_id} label={label} onEdit={handleEditLabel} />
        ))}
      </div>

      {labelHubData.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">No labels found matching your criteria</div>
          <p className="text-gray-400 mt-2">Try adjusting your filters or register a new label</p>
        </div>
      )}

      {/* Edit Label Modal - Using Enhanced Version */}
      {showEditModal && editingLabel && (
        <EnhancedEditLabelModal
          label={editingLabel}
          onClose={handleCloseEditModal}
          onUpdate={handleLabelUpdated}
        />
      )}

      {/* Bulk Label Editor */}
      {showBulkEditor && (
        <BulkLabelEditor
          labels={selectedLabelsForBulk}
          onClose={() => setShowBulkEditor(false)}
          onUpdate={() => {
            fetchLabelHubData();
            setShowBulkEditor(false);
          }}
        />
      )}

      {/* Advanced Search */}
      {showAdvancedSearch && (
        <AdvancedSearch
          onSearch={(criteria) => {
            console.log('Search criteria:', criteria);
            // Apply search filters
            setFilters(prev => ({ ...prev, ...criteria }));
            setShowAdvancedSearch(false);
          }}
          onClose={() => setShowAdvancedSearch(false)}
        />
      )}

      {/* Data Exporter */}
      {showExporter && (
        <LabelDataExporter
          labels={labelHubData}
          onClose={() => setShowExporter(false)}
        />
      )}
    </div>
  );
};

const LabelHubCard = ({ label, onEdit }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getVerificationIcon = (status) => {
    switch (status) {
      case 'verified': return '✅';
      case 'pending': return '⏳';
      case 'rejected': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow p-6 border-l-4 border-purple-500">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{label.name}</h3>
          <div className="flex items-center space-x-2 mt-1">
            <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${
              label.label_type === 'major' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
            }`}>
              {label.label_type}
            </span>
            <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(label.status)}`}>
              {label.status}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-2xl">
            {label.label_type === 'major' ? '🏢' : 
             label.label_type === 'independent' ? '🎵' :
             label.label_type === 'distribution' ? '📦' : '🎼'}
          </div>
          <button
            onClick={() => onEdit(label)}
            className="text-purple-600 hover:text-purple-800 transition-colors"
            title="Edit Label"
          >
            ✏️
          </button>
        </div>
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        <div className="flex items-center justify-between">
          <span className="font-medium">Territory:</span>
          <span>{label.territory}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="font-medium">Integration:</span>
          <span className="capitalize">{label.integration_type.replace('_', ' ')}</span>
        </div>

        {label.genre_focus && label.genre_focus.length > 0 && (
          <div className="flex items-center justify-between">
            <span className="font-medium">Genres:</span>
            <span className="text-xs">{label.genre_focus.slice(0, 2).join(', ')}</span>
          </div>
        )}

        <div className="flex items-center justify-between">
          <span className="font-medium">Verification:</span>
          <span>{getVerificationIcon(label.verification_status)} {label.verification_status}</span>
        </div>
      </div>

      {/* Features */}
      <div className="mt-4 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          {label.blockchain_enabled && <span className="text-purple-600" title="Blockchain Enabled">⛓️</span>}
          {label.dao_affiliated && <span className="text-blue-600" title="DAO Affiliated">🗳️</span>}
          {label.compliance_status === 'verified' && <span className="text-green-600" title="Compliance Verified">✅</span>}
        </div>
        <div className="text-gray-500">
          ID: {label.global_id.slice(-8)}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center text-xs">
          <div>
            <div className="font-bold text-gray-900">{label.content_count || 0}</div>
            <div className="text-gray-500">Content</div>
          </div>
          <div>
            <div className="font-bold text-gray-900">{label.shared_content_count || 0}</div>
            <div className="text-gray-500">Shared</div>
          </div>
          <div>
            <div className="font-bold text-gray-900">${(label.monthly_revenue || 0).toLocaleString()}</div>
            <div className="text-gray-500">Monthly</div>
          </div>
        </div>
      </div>

      {/* Major Label Additional Info */}
      {label.label_type === 'major' && (
        <div className="mt-3 pt-3 border-t border-purple-200">
          <div className="flex items-center justify-between text-xs">
            <span className="text-purple-600 font-medium">🌟 Major Label Network</span>
            <span className="text-purple-500">Premium Tier</span>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Full ULN integration • Smart contracts • DAO governance
          </div>
        </div>
      )}

      {/* Independent Label Additional Info */}
      {label.label_type === 'independent' && (
        <div className="mt-3 pt-3 border-t border-blue-200">
          <div className="flex items-center justify-between text-xs">
            <span className="text-blue-600 font-medium">🎶 Independent Spirit</span>
            <span className="text-blue-500">API Partner</span>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Creative freedom • Direct artist relationships • Innovation focus
          </div>
        </div>
      )}
    </div>
  );
};

// ===== EDIT LABEL MODAL COMPONENT =====

const EditLabelModal = ({ label, onClose, onUpdate }) => {
  const [formData, setFormData] = useState({
    name: label.name || '',
    legal_name: label.metadata_profile?.legal_name || '',
    genres: (label.genre_focus || []).join(', '),
    integration: label.integration_type || '',
    owner: '',
    headquarters: label.metadata_profile?.headquarters || '',
    tax_status: label.metadata_profile?.tax_status || 'corporation'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Get owner name from associated_entities
  useEffect(() => {
    const fetchLabelDetails = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API}/api/uln/labels/${label.global_id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.label) {
            const ownerEntity = data.label.associated_entities?.find(
              e => e.entity_type === 'owner' || e.role === 'Owner'
            );
            if (ownerEntity) {
              setFormData(prev => ({...prev, owner: ownerEntity.name}));
            }
          }
        }
      } catch (error) {
        console.error('Error fetching label details:', error);
      }
    };
    fetchLabelDetails();
  }, [label.global_id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({...prev, [name]: value}));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      
      // Prepare update data
      const updateData = {};
      
      if (formData.name !== label.name) {
        updateData.name = formData.name;
      }
      if (formData.legal_name) {
        updateData.legal_name = formData.legal_name;
      }
      if (formData.genres) {
        // Convert comma-separated string to array
        updateData.genres = formData.genres.split(',').map(g => g.trim()).filter(g => g);
      }
      if (formData.integration !== label.integration_type) {
        updateData.integration = formData.integration;
      }
      if (formData.owner) {
        updateData.owner = formData.owner;
      }
      if (formData.headquarters) {
        updateData.headquarters = formData.headquarters;
      }
      if (formData.tax_status) {
        updateData.tax_status = formData.tax_status;
      }

      const response = await fetch(`${API}/api/uln/labels/${label.global_id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setSuccess('✅ Label updated successfully!');
        setTimeout(() => {
          onUpdate();
        }, 1500);
      } else {
        setError(data.error || data.detail || 'Failed to update label');
      }
    } catch (error) {
      console.error('Error updating label:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-purple-600 text-white px-6 py-4 rounded-t-lg flex justify-between items-center">
          <h2 className="text-xl font-bold">✏️ Edit Label</h2>
          <button 
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Label Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Label Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter label name"
            />
          </div>

          {/* Legal Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Legal Name
            </label>
            <input
              type="text"
              name="legal_name"
              value={formData.legal_name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter legal name"
            />
          </div>

          {/* Genres */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Music Genres
            </label>
            <input
              type="text"
              name="genres"
              value={formData.genres}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="e.g., Hip-Hop, R&B, Rap (comma-separated)"
            />
            <p className="text-xs text-gray-500 mt-1">Separate multiple genres with commas</p>
          </div>

          {/* Integration Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Integration Type
            </label>
            <select
              name="integration"
              value={formData.integration}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="full_integration">Full Integration</option>
              <option value="api_partner">API Partner</option>
              <option value="distribution_only">Distribution Only</option>
              <option value="metadata_sync">Metadata Sync</option>
              <option value="content_sharing">Content Sharing</option>
            </select>
          </div>

          {/* Owner */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Owner
            </label>
            <input
              type="text"
              name="owner"
              value={formData.owner}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter owner name"
            />
          </div>

          {/* Headquarters */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Headquarters
            </label>
            <input
              type="text"
              name="headquarters"
              value={formData.headquarters}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter headquarters location"
            />
          </div>

          {/* Tax Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tax Status
            </label>
            <select
              name="tax_status"
              value={formData.tax_status}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="corporation">Corporation</option>
              <option value="llc">LLC</option>
              <option value="partnership">Partnership</option>
              <option value="sole_proprietorship">Sole Proprietorship</option>
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '⏳ Saving...' : '💾 Save Changes'}
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="flex-1 bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ===== CROSS-LABEL CONTENT SHARING COMPONENT =====

const CrossLabelContentSharing = () => {
  const [activeSection, setActiveSection] = useState('federated');
  const [federatedContent, setFederatedContent] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchFederatedContent = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // This would typically get current user's label ID
      const currentLabelId = 'current-label-id'; // Would be dynamic
      
      const response = await fetch(`${API}/api/uln/content/federated/${currentLabelId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFederatedContent(data.federated_content || []);
      }
    } catch (error) {
      console.error('Error fetching federated content:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeSection === 'federated') {
      fetchFederatedContent();
    }
  }, [activeSection]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">🔗 Cross-Label Content Sharing</h2>
          <p className="text-gray-600">Federated access and metadata sync across labels</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          + Share Content
        </button>
      </div>

      {/* Section Navigation */}
      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['federated', 'metadata', 'permissions', 'usage'].map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`capitalize py-2 px-4 rounded-md font-medium transition-colors ${
                activeSection === section 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {section.replace('_', ' ')}
            </button>
          ))}
        </nav>
      </div>

      {/* Section Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {loading && (
          <div className="flex justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        )}

        {activeSection === 'federated' && !loading && (
          <FederatedContentList content={federatedContent} />
        )}

        {activeSection === 'metadata' && (
          <MetadataSync />
        )}

        {activeSection === 'permissions' && (
          <PermissionsManagement />
        )}

        {activeSection === 'usage' && (
          <UsageAttribution />
        )}
      </div>

      {/* Create Content Sharing Modal */}
      {showCreateModal && (
        <CreateContentSharingModal 
          onClose={() => setShowCreateModal(false)}
          onCreated={fetchFederatedContent}
        />
      )}
    </div>
  );
};

const FederatedContentList = ({ content }) => {
  if (content.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">No federated content found</div>
        <p className="text-gray-400 mt-2">Start sharing content across labels to see it here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold mb-4">📁 Federated Content</h3>
      {content.map((item, index) => (
        <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium">Content ID: {item.content_id}</h4>
              <p className="text-sm text-gray-600">Primary Label: {item.primary_label_id}</p>
              <p className="text-sm text-gray-500">
                Shared with: {item.licensing_labels?.length || 0} labels
              </p>
              <p className="text-sm text-gray-500">
                Access Level: {item.access_level}
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Active
              </span>
            </div>
          </div>

          {/* Rights Splits */}
          {item.rights_splits && Object.keys(item.rights_splits).length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <h5 className="text-sm font-medium text-gray-700 mb-2">Rights Distribution:</h5>
              <div className="flex flex-wrap gap-2">
                {Object.entries(item.rights_splits).map(([labelId, percentage]) => (
                  <span key={labelId} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    {labelId}: {percentage}%
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

const MetadataSync = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🔄 Metadata Synchronization</h3>
    <p className="text-gray-600">Sync metadata across all connected labels</p>
    
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <span className="text-blue-600 text-xl">ℹ️</span>
        </div>
        <div className="ml-3">
          <h4 className="text-sm font-medium text-blue-900">Automatic Metadata Sync</h4>
          <p className="text-sm text-blue-700">
            Metadata is automatically synchronized across all labels with federated access when changes are made.
          </p>
        </div>
      </div>
    </div>

    <div className="space-y-3">
      <div className="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
        <div>
          <div className="font-medium">Content Metadata</div>
          <div className="text-sm text-gray-600">Title, artist, genre, duration</div>
        </div>
        <div className="text-green-600 font-medium">✓ Sync Active</div>
      </div>

      <div className="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
        <div>
          <div className="font-medium">Rights Information</div>
          <div className="text-sm text-gray-600">Ownership, splits, restrictions</div>
        </div>
        <div className="text-green-600 font-medium">✓ Sync Active</div>
      </div>

      <div className="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
        <div>
          <div className="font-medium">Revenue Data</div>
          <div className="text-sm text-gray-600">Streams, plays, earnings</div>
        </div>
        <div className="text-green-600 font-medium">✓ Sync Active</div>
      </div>
    </div>
  </div>
);

const PermissionsManagement = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🔐 Role-Based Permissions</h3>
    <p className="text-gray-600">Manage access levels and permissions for federated content</p>
    
    <div className="space-y-3">
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Read Only Access</h4>
        <p className="text-sm text-gray-600 mb-3">View content and basic metadata only</p>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">View Metadata</span>
          <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">View Usage Stats</span>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Edit Metadata</h4>
        <p className="text-sm text-gray-600 mb-3">Modify non-rights metadata</p>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Edit Title/Artist</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Update Genre</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Add Description</span>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Full Access</h4>
        <p className="text-sm text-gray-600 mb-3">Complete control including rights management</p>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Edit Rights</span>
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Change Splits</span>
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Manage Distribution</span>
        </div>
      </div>
    </div>
  </div>
);

const UsageAttribution = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">📊 Usage Attribution</h3>
    <p className="text-gray-600">Track streams, views, and revenue attribution by label</p>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Streams by Label</h4>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm">Label A</span>
            <span className="font-medium">1,234,567</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm">Label B</span>
            <span className="font-medium">987,654</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm">Label C</span>
            <span className="font-medium">456,789</span>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Revenue Attribution</h4>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm">Label A</span>
            <span className="font-medium">$12,345</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm">Label B</span>
            <span className="font-medium">$9,876</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm">Label C</span>
            <span className="font-medium">$4,567</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// ===== ROYALTY POOL MANAGEMENT COMPONENT =====

const RoyaltyPoolManagement = () => {
  const [activeSection, setActiveSection] = useState('pools');
  const [royaltyPools, setRoyaltyPools] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">💰 Multi-Label Royalty Engine</h2>
          <p className="text-gray-600">Aggregate and distribute royalties across labels</p>
        </div>
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors">
          + Create Pool
        </button>
      </div>

      {/* Section Navigation */}
      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['pools', 'earnings', 'ledger', 'distribution'].map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`capitalize py-2 px-4 rounded-md font-medium transition-colors ${
                activeSection === section 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {section.replace('_', ' ')}
            </button>
          ))}
        </nav>
      </div>

      {/* Section Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {activeSection === 'pools' && <RoyaltyPoolsList />}
        {activeSection === 'earnings' && <EarningsProcessing />}
        {activeSection === 'ledger' && <PayoutLedger />}
        {activeSection === 'distribution' && <DistributionManagement />}
      </div>
    </div>
  );
};

const RoyaltyPoolsList = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🏊 Active Royalty Pools</h3>
    
    <div className="space-y-3">
      <div className="border border-gray-200 rounded-lg p-4">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Q1 2025 Pool</h4>
            <p className="text-sm text-gray-600">5 participating labels</p>
            <p className="text-sm text-gray-500">Period: Jan 1 - Mar 31, 2025</p>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-green-600">$125,430</div>
            <div className="text-sm text-gray-500">Total collected</div>
            <span className="inline-block px-2 py-1 mt-1 bg-green-100 text-green-800 text-xs rounded-full">
              Ready to distribute
            </span>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Distribution method: Proportional</span>
            <button className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 text-sm rounded">
              Distribute
            </button>
          </div>
        </div>
      </div>

      <div className="border border-gray-200 rounded-lg p-4">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Q4 2024 Pool</h4>
            <p className="text-sm text-gray-600">8 participating labels</p>
            <p className="text-sm text-gray-500">Period: Oct 1 - Dec 31, 2024</p>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-gray-600">$98,765</div>
            <div className="text-sm text-gray-500">Distributed</div>
            <span className="inline-block px-2 py-1 mt-1 bg-gray-100 text-gray-800 text-xs rounded-full">
              Completed
            </span>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Distributed on: Jan 15, 2025</span>
            <button className="bg-gray-500 text-white px-3 py-1 text-sm rounded">
              View Report
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const EarningsProcessing = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">💸 Earnings Processing</h3>
    <p className="text-gray-600">Process incoming royalty earnings for multi-label distribution</p>
    
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h4 className="font-medium text-blue-900 mb-2">Processing Status</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">1,234</div>
          <div className="text-sm text-blue-700">Earnings processed today</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">$45,678</div>
          <div className="text-sm text-green-700">Total amount processed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">23</div>
          <div className="text-sm text-purple-700">Labels involved</div>
        </div>
      </div>
    </div>

    <div className="space-y-3">
      <h4 className="font-medium">Recent Processing Activity</h4>
      <div className="space-y-2">
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
          <div>
            <div className="font-medium">Spotify Q1 Earnings</div>
            <div className="text-sm text-gray-600">Processed 15 minutes ago</div>
          </div>
          <div className="text-green-600 font-medium">$12,345</div>
        </div>
        
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
          <div>
            <div className="font-medium">Apple Music Batch #1247</div>
            <div className="text-sm text-gray-600">Processed 1 hour ago</div>
          </div>
          <div className="text-green-600 font-medium">$8,901</div>
        </div>
        
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
          <div>
            <div className="font-medium">YouTube Content ID</div>
            <div className="text-sm text-gray-600">Processed 2 hours ago</div>
          </div>
          <div className="text-green-600 font-medium">$3,456</div>
        </div>
      </div>
    </div>
  </div>
);

const PayoutLedger = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">📋 Transparent Payout Ledger</h3>
    <p className="text-gray-600">Complete breakdown of all payouts by label, creator, and investor</p>
    
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Recipient
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Gross Amount
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Deductions
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Net Amount
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              Atlantic Records
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              Label
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              $25,000.00
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              $2,625.00
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
              $22,375.00
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                Completed
              </span>
            </td>
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              Def Jam Recordings
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              Label
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              $18,500.00
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              $1,942.50
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
              $16,557.50
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                Processing
              </span>
            </td>
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              Artist Collective LLC
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              Creator
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              $12,000.00
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              $1,200.00
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
              $10,800.00
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                Pending
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
);

const DistributionManagement = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🎯 Distribution Management</h3>
    <p className="text-gray-600">Manage royalty distribution methods and DAO overrides</p>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Distribution Methods</h4>
        <div className="space-y-3">
          <div className="flex items-center">
            <input type="radio" name="distribution" id="proportional" className="mr-2" defaultChecked />
            <label htmlFor="proportional" className="text-sm">
              <div className="font-medium">Proportional</div>
              <div className="text-gray-600">Based on revenue contribution</div>
            </label>
          </div>
          
          <div className="flex items-center">
            <input type="radio" name="distribution" id="equal" className="mr-2" />
            <label htmlFor="equal" className="text-sm">
              <div className="font-medium">Equal Split</div>
              <div className="text-gray-600">Even distribution among labels</div>
            </label>
          </div>
          
          <div className="flex items-center">
            <input type="radio" name="distribution" id="custom" className="mr-2" />
            <label htmlFor="custom" className="text-sm">
              <div className="font-medium">Custom Splits</div>
              <div className="text-gray-600">Manually defined percentages</div>
            </label>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">DAO Overrides</h4>
        <div className="space-y-3">
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
            <div className="flex items-center">
              <span className="text-yellow-600 text-sm">⚠️</span>
              <span className="ml-2 text-sm font-medium">Pending Override</span>
            </div>
            <div className="text-xs text-yellow-700 mt-1">
              Proposal #123: Adjust split for Q1 2025
            </div>
          </div>
          
          <div className="p-3 bg-green-50 border border-green-200 rounded">
            <div className="flex items-center">
              <span className="text-green-600 text-sm">✅</span>
              <span className="ml-2 text-sm font-medium">Override Applied</span>
            </div>
            <div className="text-xs text-green-700 mt-1">
              Dispute resolution for content ABC123
            </div>
          </div>
        </div>

        <button className="w-full mt-4 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          View All DAO Actions
        </button>
      </div>
    </div>
  </div>
);

// ===== DAO GOVERNANCE COMPONENT =====

const DAOGovernance = () => {
  const [activeSection, setActiveSection] = useState('proposals');
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchProposals = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/uln/dao/proposals`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setProposals(data.proposals || []);
      }
    } catch (error) {
      console.error('Error fetching proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeSection === 'proposals') {
      fetchProposals();
    }
  }, [activeSection]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">🗳️ DAO Governance</h2>
          <p className="text-gray-600">Decentralized decision-making for the Unified Label Network</p>
        </div>
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors">
          + Create Proposal
        </button>
      </div>

      {/* Section Navigation */}
      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['proposals', 'voting', 'governance', 'history'].map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`capitalize py-2 px-4 rounded-md font-medium transition-colors ${
                activeSection === section 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {section.replace('_', ' ')}
            </button>
          ))}
        </nav>
      </div>

      {/* Section Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {loading && (
          <div className="flex justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        )}

        {activeSection === 'proposals' && !loading && (
          <ProposalsList proposals={proposals} />
        )}

        {activeSection === 'voting' && (
          <VotingInterface />
        )}

        {activeSection === 'governance' && (
          <GovernanceRules />
        )}

        {activeSection === 'history' && (
          <GovernanceHistory />
        )}
      </div>
    </div>
  );
};

const ProposalsList = ({ proposals }) => {
  const getProposalTypeColor = (type) => {
    switch (type) {
      case 'content_approval': return 'bg-blue-100 text-blue-800';
      case 'takedown_request': return 'bg-red-100 text-red-800';
      case 'royalty_split_change': return 'bg-green-100 text-green-800';
      case 'cross_label_agreement': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-yellow-100 text-yellow-800';
      case 'passed': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'executed': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (proposals.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">No active proposals</div>
        <p className="text-gray-400 mt-2">Create a new proposal to get started with DAO governance</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold mb-4">📋 Active Proposals</h3>
      {proposals.map((proposal, index) => (
        <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h4 className="font-medium text-lg">{proposal.title}</h4>
              <p className="text-sm text-gray-600 mt-1">{proposal.description}</p>
            </div>
            <div className="flex space-x-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getProposalTypeColor(proposal.proposal_type)}`}>
                {proposal.proposal_type.replace('_', ' ')}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(proposal.status)}`}>
                {proposal.status}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
            <div className="text-sm">
              <span className="font-medium">Proposer:</span> {proposal.proposer_id}
            </div>
            <div className="text-sm">
              <span className="font-medium">Voting Deadline:</span> {new Date(proposal.voting_deadline).toLocaleDateString()}
            </div>
            <div className="text-sm">
              <span className="font-medium">Affected Labels:</span> {proposal.affected_labels?.length || 0}
            </div>
          </div>

          {/* Voting Progress */}
          <div className="bg-gray-50 rounded-lg p-3 mb-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Voting Progress</span>
              <span className="text-sm text-gray-600">
                {((proposal.participation_rate || 0) * 100).toFixed(1)}% participation
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full" 
                style={{ width: `${(proposal.participation_rate || 0) * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <div className="flex space-x-4 text-sm">
              <span className="text-green-600">
                👍 For: {Object.keys(proposal.votes_for || {}).length}
              </span>
              <span className="text-red-600">
                👎 Against: {Object.keys(proposal.votes_against || {}).length}
              </span>
              <span className="text-gray-600">
                🤷 Abstain: {Object.keys(proposal.votes_abstain || {}).length}
              </span>
            </div>
            
            {proposal.status === 'active' && (
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 text-sm rounded transition-colors">
                Vote
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

const VotingInterface = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🗳️ Voting Interface</h3>
    <p className="text-gray-600">Cast your vote on active proposals</p>
    
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h4 className="font-medium text-blue-900 mb-2">Your Voting Power</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">5.0</div>
          <div className="text-sm text-blue-700">Total voting power</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">3</div>
          <div className="text-sm text-green-700">Labels represented</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">12</div>
          <div className="text-sm text-purple-700">Votes cast this quarter</div>
        </div>
      </div>
    </div>
    
    <div className="p-4 border border-gray-200 rounded-lg">
      <h4 className="font-medium mb-2">How Voting Power is Calculated</h4>
      <div className="text-sm text-gray-600 space-y-1">
        <p>• Each label in the ULN receives base voting power of 1.0</p>
        <p>• Additional power based on revenue contribution (max +2.0)</p>
        <p>• Bonus for active participation in governance (+0.5)</p>
        <p>• Penalty for missed votes in previous quarter (-0.5)</p>
      </div>
    </div>
  </div>
);

const GovernanceRules = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">⚖️ Governance Rules</h3>
    <p className="text-gray-600">Rules and thresholds for DAO decision-making</p>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Voting Thresholds</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span>Content Approval:</span>
            <span className="font-medium">Simple majority (51%)</span>
          </div>
          <div className="flex justify-between">
            <span>Royalty Changes:</span>
            <span className="font-medium">Supermajority (67%)</span>
          </div>
          <div className="flex justify-between">
            <span>Takedown Requests:</span>
            <span className="font-medium">Simple majority (51%)</span>
          </div>
          <div className="flex justify-between">
            <span>System Changes:</span>
            <span className="font-medium">Supermajority (75%)</span>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Participation Requirements</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span>Minimum participation:</span>
            <span className="font-medium">51% of voting power</span>
          </div>
          <div className="flex justify-between">
            <span>Voting period:</span>
            <span className="font-medium">7 days (standard)</span>
          </div>
          <div className="flex justify-between">
            <span>Emergency voting:</span>
            <span className="font-medium">24 hours</span>
          </div>
          <div className="flex justify-between">
            <span>Proposal bond:</span>
            <span className="font-medium">$1,000 (refundable)</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const GovernanceHistory = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">📜 Governance History</h3>
    <p className="text-gray-600">Historical record of all DAO decisions and votes</p>
    
    <div className="space-y-3">
      <div className="p-4 border border-gray-200 rounded-lg">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Cross-label content sharing for track XYZ123</h4>
            <p className="text-sm text-gray-600">Approved federated access across 5 labels</p>
            <p className="text-xs text-gray-500">Executed on: March 15, 2025</p>
          </div>
          <div className="text-right">
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              Passed (78% approval)
            </span>
            <div className="text-xs text-gray-500 mt-1">
              15 votes cast
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Q4 2024 Royalty Distribution Method</h4>
            <p className="text-sm text-gray-600">Change from equal split to proportional distribution</p>
            <p className="text-xs text-gray-500">Executed on: March 10, 2025</p>
          </div>
          <div className="text-right">
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              Passed (89% approval)
            </span>
            <div className="text-xs text-gray-500 mt-1">
              23 votes cast
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Content takedown request for track ABC456</h4>
            <p className="text-sm text-gray-600">Request to remove content due to rights dispute</p>
            <p className="text-xs text-gray-500">Rejected on: March 8, 2025</p>
          </div>
          <div className="text-right">
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
              Rejected (34% approval)
            </span>
            <div className="text-xs text-gray-500 mt-1">
              18 votes cast
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// ===== ULN ANALYTICS COMPONENT =====

const ULNAnalytics = ({ stats }) => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-2">📊 ULN Analytics</h2>
        <p className="text-gray-600">Deep insights into the Unified Label Network performance</p>
      </div>

      {/* Network Growth */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">📈 Network Growth</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Label Registrations Over Time</h4>
            <div className="h-48 bg-gray-100 rounded flex items-center justify-center">
              <span className="text-gray-500">Chart: Label registration trends</span>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Content Sharing Activity</h4>
            <div className="h-48 bg-gray-100 rounded flex items-center justify-center">
              <span className="text-gray-500">Chart: Cross-label content sharing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Financial Analytics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">💰 Financial Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">${(stats.total_revenue_processed || 0).toLocaleString()}</div>
            <div className="text-gray-600">Total Revenue Processed</div>
            <div className="text-sm text-green-600 mt-1">↗️ +15% from last quarter</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">${(stats.pending_distributions || 0).toLocaleString()}</div>
            <div className="text-gray-600">Pending Distributions</div>
            <div className="text-sm text-blue-600 mt-1">Ready for payout</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">2.5%</div>
            <div className="text-gray-600">Platform Fee</div>
            <div className="text-sm text-purple-600 mt-1">Transparent & competitive</div>
          </div>
        </div>
      </div>

      {/* Governance Analytics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">🗳️ Governance Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Proposal Success Rate</h4>
            <div className="flex items-center justify-center h-32">
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600">73%</div>
                <div className="text-gray-600">of proposals passed</div>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Average Participation</h4>
            <div className="flex items-center justify-center h-32">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600">68%</div>
                <div className="text-gray-600">voter participation</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ===== HELPER MODALS =====

const CreateContentSharingModal = ({ onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    content_id: '',
    target_labels: [],
    access_level: 'read_only',
    proposed_rights_splits: {},
    usage_restrictions: [],
    expiry_date: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/uln/content/federated-access`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content_id: formData.content_id,
          requesting_label_id: 'current-label-id', // Would be dynamic
          target_labels: formData.target_labels,
          access_level: formData.access_level,
          proposed_rights_splits: formData.proposed_rights_splits,
          usage_restrictions: formData.usage_restrictions,
          expiry_date: formData.expiry_date ? new Date(formData.expiry_date).toISOString() : null
        })
      });

      if (response.ok) {
        onCreated();
        onClose();
      }
    } catch (error) {
      console.error('Error creating content sharing:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-screen overflow-y-auto">
        <h3 className="text-xl font-bold mb-4">Share Content Across Labels</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content ID</label>
            <input
              type="text"
              required
              value={formData.content_id}
              onChange={(e) => setFormData({...formData, content_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter content identifier"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Labels</label>
            <input
              type="text"
              value={formData.target_labels.join(', ')}
              onChange={(e) => setFormData({
                ...formData, 
                target_labels: e.target.value.split(',').map(id => id.trim()).filter(id => id)
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter label IDs (comma-separated)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Access Level</label>
            <select
              value={formData.access_level}
              onChange={(e) => setFormData({...formData, access_level: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="read_only">Read Only</option>
              <option value="edit_metadata">Edit Metadata</option>
              <option value="full_access">Full Access</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date (Optional)</label>
            <input
              type="date"
              value={formData.expiry_date}
              onChange={(e) => setFormData({...formData, expiry_date: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Create Sharing Agreement
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ===== LABEL CATALOG COMPONENT =====

const STATUS_BADGE = {
  released: 'bg-emerald-100 text-emerald-800',
  'pre-release': 'bg-amber-100 text-amber-800',
  draft: 'bg-gray-100 text-gray-600',
  taken_down: 'bg-red-100 text-red-800',
};

const LabelCatalog = ({ activeLabel }) => {
  const [catalog, setCatalog] = useState({ assets: [], total_assets: 0, is_seed_data: false });
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('token');
  const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    if (activeLabel) fetchCatalog();
  }, [activeLabel?.label_id]);

  const fetchCatalog = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/catalog`, { headers });
      if (res.ok) {
        const data = await res.json();
        setCatalog(data);
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  if (!activeLabel) {
    return (
      <div className="bg-white rounded-xl shadow p-8 text-center" data-testid="catalog-no-label">
        <p className="text-gray-500">Select a label from the switcher above to view its catalog.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="label-catalog-panel">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Catalog</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium text-purple-700">{activeLabel.name}</span> &middot; {catalog.total_assets} asset{catalog.total_assets !== 1 ? 's' : ''}
          </p>
        </div>
        {catalog.is_seed_data && (
          <span className="text-xs bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full font-medium" data-testid="catalog-seed-badge">
            Sample Data &mdash; Real assets will appear after Phase B
          </span>
        )}
      </div>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div></div>
        ) : catalog.assets.length === 0 ? (
          <div className="p-8 text-center text-gray-500" data-testid="catalog-empty">No assets in this label's catalog yet.</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200" data-testid="catalog-table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Artist</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ISRC</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Release</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Streams</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {catalog.assets.map((a) => (
                <tr key={a.asset_id} data-testid={`catalog-row-${a.asset_id}`}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{a.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 capitalize">{a.type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{a.artist}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-xs font-mono text-gray-500">{a.isrc}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{a.release_date}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${STATUS_BADGE[a.status] || 'bg-gray-100 text-gray-700'}`}>{a.status}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-right font-medium">
                    {a.streams_total != null ? a.streams_total.toLocaleString() : '—'}
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


// ===== LABEL DISTRIBUTION STATUS COMPONENT =====

const DSP_STATUS_BADGE = {
  live: 'bg-emerald-100 text-emerald-800',
  pending: 'bg-amber-100 text-amber-800',
  error: 'bg-red-100 text-red-800',
  disabled: 'bg-gray-100 text-gray-600',
};

const LabelDistributionStatus = ({ activeLabel }) => {
  const [distData, setDistData] = useState({ endpoints: [], summary: {} });
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('token');
  const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    if (activeLabel) fetchDistribution();
  }, [activeLabel?.label_id]);

  const fetchDistribution = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/distribution/status`, { headers });
      if (res.ok) {
        const data = await res.json();
        setDistData(data);
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  if (!activeLabel) {
    return (
      <div className="bg-white rounded-xl shadow p-8 text-center" data-testid="dist-no-label">
        <p className="text-gray-500">Select a label from the switcher above to view distribution status.</p>
      </div>
    );
  }

  const { summary } = distData;

  return (
    <div className="space-y-6" data-testid="label-distribution-panel">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Distribution Status</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium text-purple-700">{activeLabel.name}</span> &middot; {summary.total_endpoints || 0} endpoint{(summary.total_endpoints || 0) !== 1 ? 's' : ''}
          </p>
        </div>
        {distData.is_seed_data && (
          <span className="text-xs bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full font-medium" data-testid="dist-seed-badge">
            Sample Data
          </span>
        )}
      </div>

      {/* Summary Cards */}
      {summary.total_endpoints > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4" data-testid="dist-summary-cards">
          <div className="bg-white rounded-xl shadow p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{summary.total_endpoints}</p>
            <p className="text-xs text-gray-500 mt-1">Total Endpoints</p>
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
            <div
              className={`h-2.5 rounded-full transition-all ${summary.health_pct >= 80 ? 'bg-emerald-500' : summary.health_pct >= 50 ? 'bg-amber-500' : 'bg-red-500'}`}
              style={{ width: `${summary.health_pct}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Endpoints Table */}
      <div className="bg-white rounded-xl shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div></div>
        ) : distData.endpoints.length === 0 ? (
          <div className="p-8 text-center text-gray-500" data-testid="dist-empty">No distribution endpoints configured.</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200" data-testid="dist-table">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Delivery</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Assets Delivered</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Errors</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {distData.endpoints.map((ep) => (
                <tr key={ep.endpoint_id} data-testid={`dist-row-${ep.endpoint_id}`}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{ep.platform}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${DSP_STATUS_BADGE[ep.status] || 'bg-gray-100 text-gray-700'}`}>{ep.status}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {ep.last_delivery ? new Date(ep.last_delivery).toLocaleString() : '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-right">{ep.assets_delivered}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                    {ep.errors > 0 ? (
                      <span className="text-red-600 font-medium" title={ep.error_message || ''}>{ep.errors}</span>
                    ) : (
                      <span className="text-gray-400">0</span>
                    )}
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


// ===== LABEL AUDIT SNAPSHOT COMPONENT =====

const LabelAuditSnapshot = ({ activeLabel }) => {
  const [downloading, setDownloading] = useState(false);
  const [lastDownload, setLastDownload] = useState(null);
  const token = localStorage.getItem('token');

  const handleDownload = async () => {
    if (!activeLabel) return;
    setDownloading(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/audit-snapshot`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `label_${activeLabel.label_id}_audit_snapshot.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        setLastDownload(new Date().toLocaleString());
      }
    } catch (e) { console.error(e); }
    setDownloading(false);
  };

  if (!activeLabel) {
    return (
      <div className="bg-white rounded-xl shadow p-8 text-center" data-testid="audit-no-label">
        <p className="text-gray-500">Select a label from the switcher above to export an audit snapshot.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="label-audit-snapshot-panel">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Audit Snapshot</h2>
        <p className="text-sm text-gray-500 mt-1">
          Export a comprehensive JSON snapshot of <span className="font-medium text-purple-700">{activeLabel.name}</span> for compliance and record-keeping.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">Full Label Snapshot</h3>
            <p className="text-sm text-gray-500 mt-1">
              Includes: label metadata, members, catalog assets, distribution endpoints, and recent audit trail entries.
            </p>
          </div>
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-2 bg-purple-600 text-white px-5 py-2.5 rounded-lg font-medium text-sm hover:bg-purple-700 transition disabled:opacity-50 shrink-0"
            data-testid="audit-download-btn"
          >
            {downloading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Generating...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                Download Snapshot
              </>
            )}
          </button>
        </div>
        {lastDownload && (
          <p className="text-xs text-gray-400 mt-3" data-testid="audit-last-download">Last downloaded: {lastDownload}</p>
        )}
      </div>

      <div className="bg-gray-50 rounded-xl p-5 border border-gray-200">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">What's included in the snapshot?</h4>
        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600">
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Label metadata & configuration</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> All team members & roles</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Catalog assets (titles, ISRCs, UPCs)</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Distribution endpoint statuses</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Distribution health summary</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Recent audit trail (up to 100 entries)</li>
        </ul>
      </div>
    </div>
  );
};

export default ULNDashboard;