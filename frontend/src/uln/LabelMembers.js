import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const ROLE_COLORS = {
  owner: 'bg-amber-100 text-amber-800',
  admin: 'bg-blue-100 text-blue-800',
  a_and_r: 'bg-green-100 text-green-800',
  viewer: 'bg-gray-100 text-gray-700',
};

const ROLE_LABELS = { owner: 'Owner', admin: 'Admin', a_and_r: 'A&R', viewer: 'Viewer' };

export const LabelMembers = ({ activeLabel, onMemberChange }) => {
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
