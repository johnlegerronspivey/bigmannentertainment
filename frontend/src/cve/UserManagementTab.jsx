import React, { useState, useEffect, useCallback } from "react";
import { Plus, X } from "lucide-react";
import { RBAC_API, ROLE_BADGES, fetcher } from "./shared";

export const UserManagementTab = ({ currentRole }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [roles, setRoles] = useState({});
  const [showInvite, setShowInvite] = useState(false);
  const [inviteForm, setInviteForm] = useState({ email: "", full_name: "", role: "analyst" });
  const [saving, setSaving] = useState(false);

  const token = localStorage.getItem("token");
  const authHeaders = { "Content-Type": "application/json", Authorization: `Bearer ${token}` };

  const fetchUsers = useCallback(async () => {
    try {
      const data = await fetcher(`${RBAC_API}/users`, { headers: authHeaders });
      setUsers(data.users || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  const fetchRoles = useCallback(async () => {
    try {
      const data = await fetcher(`${RBAC_API}/roles`);
      setRoles(data.roles || {});
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchUsers(); fetchRoles(); }, [fetchUsers, fetchRoles]);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await fetcher(`${RBAC_API}/users/${userId}/role`, {
        method: "PUT", headers: authHeaders, body: JSON.stringify({ role: newRole }),
      });
      fetchUsers();
    } catch (e) { alert(e.message); }
  };

  const handleStatusToggle = async (userId, currentActive) => {
    try {
      await fetcher(`${RBAC_API}/users/${userId}/status`, {
        method: "PUT", headers: authHeaders, body: JSON.stringify({ is_active: !currentActive }),
      });
      fetchUsers();
    } catch (e) { alert(e.message); }
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetcher(`${RBAC_API}/users/invite`, {
        method: "POST", headers: authHeaders, body: JSON.stringify(inviteForm),
      });
      setShowInvite(false);
      setInviteForm({ email: "", full_name: "", role: "analyst" });
      fetchUsers();
    } catch (e) { alert(e.message); }
    setSaving(false);
  };

  if (loading) return <div className="text-slate-400 text-center py-12">Loading users...</div>;

  return (
    <div data-testid="user-management-tab" className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">User Management</h2>
          <p className="text-sm text-slate-400">Manage CVE platform users, roles, and access</p>
        </div>
        <button data-testid="invite-user-btn" onClick={() => setShowInvite(true)} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          <Plus className="w-4 h-4" /> Invite User
        </button>
      </div>

      <div className="flex gap-4 flex-wrap">
        {Object.entries(ROLE_BADGES).map(([key, r]) => (
          <div key={key} className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.bg} ${r.text}`}>{r.label}</span>
            <span className="text-xs text-slate-500">{roles[key]?.description || ""}</span>
          </div>
        ))}
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700/50">
              <th className="text-left px-4 py-3 text-slate-400 font-medium">User</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Role</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Status</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Joined</th>
              <th className="text-right px-4 py-3 text-slate-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => {
              const badge = ROLE_BADGES[u.cve_role] || ROLE_BADGES.analyst;
              return (
                <tr key={u.user_id} data-testid={`user-row-${u.user_id}`} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                  <td className="px-4 py-3">
                    <div className="text-white font-medium">{u.full_name}</div>
                    <div className="text-xs text-slate-400">{u.email}</div>
                  </td>
                  <td className="px-4 py-3">
                    {currentRole === "admin" ? (
                      <select data-testid={`role-select-${u.user_id}`} value={u.cve_role} onChange={(e) => handleRoleChange(u.user_id, e.target.value)}
                        className="bg-slate-700 border border-slate-600 text-white text-xs rounded-lg px-2 py-1.5 focus:ring-cyan-500 focus:border-cyan-500">
                        <option value="admin">Admin</option>
                        <option value="manager">Manager</option>
                        <option value="analyst">Analyst</option>
                      </select>
                    ) : (
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>{badge.label}</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${u.is_active ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"}`}>
                      {u.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                  <td className="px-4 py-3 text-right">
                    {currentRole === "admin" && (
                      <button data-testid={`toggle-status-${u.user_id}`} onClick={() => handleStatusToggle(u.user_id, u.is_active)}
                        className={`px-3 py-1 rounded text-xs transition-colors ${u.is_active ? "bg-red-500/10 text-red-400 hover:bg-red-500/20" : "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"}`}>
                        {u.is_active ? "Deactivate" : "Activate"}
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {users.length === 0 && <div className="text-center text-slate-500 py-8">No users found</div>}
      </div>

      {showInvite && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowInvite(false)}>
          <div data-testid="invite-modal" className="bg-slate-800 border border-slate-700 rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Invite User</h3>
              <button onClick={() => setShowInvite(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleInvite} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-300 mb-1">Email</label>
                <input data-testid="invite-email" type="email" required value={inviteForm.email} onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm focus:ring-cyan-500 focus:border-cyan-500" placeholder="user@example.com" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Full Name</label>
                <input data-testid="invite-name" type="text" required value={inviteForm.full_name} onChange={(e) => setInviteForm({ ...inviteForm, full_name: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm focus:ring-cyan-500 focus:border-cyan-500" placeholder="John Doe" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Role</label>
                <select data-testid="invite-role" value={inviteForm.role} onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm focus:ring-cyan-500 focus:border-cyan-500">
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="analyst">Analyst</option>
                </select>
              </div>
              <div className="flex gap-3 justify-end">
                <button type="button" onClick={() => setShowInvite(false)} className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-600">Cancel</button>
                <button data-testid="invite-submit-btn" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm hover:bg-cyan-700 disabled:opacity-50">
                  {saving ? "Inviting..." : "Invite User"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
