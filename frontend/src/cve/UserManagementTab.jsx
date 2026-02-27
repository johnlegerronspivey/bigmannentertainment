import React, { useState, useEffect, useCallback } from "react";
import { Plus, X, Users, Database, Building2, Shield, ChevronDown, Settings, Trash2 } from "lucide-react";
import { RBAC_API, TENANT_API, ROLE_BADGES, ROLE_HIERARCHY, fetcher } from "./shared";
import { TenantMigrationPanel } from "./TenantMigrationPanel";

const SUB_TABS_SUPER = [
  { id: "users", label: "Users & Roles", icon: Users },
  { id: "tenants", label: "Tenants", icon: Building2 },
  { id: "migration", label: "Data Migration", icon: Database },
];

const SUB_TABS_DEFAULT = [
  { id: "users", label: "Users & Roles", icon: Users },
];

/* ── helper: roles this actor can assign ─────────────── */
function assignableRoles(actorRole) {
  const actorLevel = ROLE_HIERARCHY.indexOf(actorRole);
  if (actorLevel < 0) return [];
  return ROLE_HIERARCHY.filter((_, i) => i < actorLevel);
}

/* ═══════════════════ Tenant Management Panel ═══════════ */
const TenantManagementPanel = ({ token }) => {
  const [tenants, setTenants] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({ name: "", plan: "free" });
  const [saving, setSaving] = useState(false);
  const authHeaders = { "Content-Type": "application/json", Authorization: `Bearer ${token}` };

  const fetchTenants = useCallback(async () => {
    try {
      const [tData, sData] = await Promise.all([
        fetcher(`${TENANT_API}/`, { headers: authHeaders }),
        fetcher(`${TENANT_API}/stats`, { headers: authHeaders }),
      ]);
      setTenants(tData.items || []);
      setStats(sData);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchTenants(); }, [fetchTenants]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetcher(`${TENANT_API}/`, { method: "POST", headers: authHeaders, body: JSON.stringify(createForm) });
      setShowCreate(false);
      setCreateForm({ name: "", plan: "free" });
      fetchTenants();
    } catch (e) { alert(e.message); }
    setSaving(false);
  };

  const handleDelete = async (tenantId, name) => {
    if (!window.confirm(`Delete tenant "${name}"? This will unassign all users.`)) return;
    try {
      await fetcher(`${TENANT_API}/${tenantId}`, { method: "DELETE", headers: authHeaders });
      fetchTenants();
    } catch (e) { alert(e.message); }
  };

  const planColors = {
    free: "bg-slate-500/20 text-slate-300",
    pro: "bg-cyan-500/20 text-cyan-300",
    enterprise: "bg-amber-500/20 text-amber-300",
  };

  if (loading) return <div className="text-slate-400 text-center py-12">Loading tenants...</div>;

  return (
    <div data-testid="tenant-management-panel" className="space-y-6">
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
            <div className="text-xs text-slate-400 mb-1">Total Tenants</div>
            <div data-testid="stat-total-tenants" className="text-2xl font-bold text-white">{stats.total_tenants}</div>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
            <div className="text-xs text-slate-400 mb-1">Active</div>
            <div data-testid="stat-active-tenants" className="text-2xl font-bold text-emerald-400">{stats.active_tenants}</div>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
            <div className="text-xs text-slate-400 mb-1">Users Assigned</div>
            <div className="text-2xl font-bold text-cyan-400">{stats.users_with_tenant}</div>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
            <div className="text-xs text-slate-400 mb-1">Users Unassigned</div>
            <div className="text-2xl font-bold text-orange-400">{stats.users_without_tenant}</div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">Tenant Organizations</h2>
          <p className="text-sm text-slate-400">Manage organizations and their plans</p>
        </div>
        <button data-testid="create-tenant-btn" onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          <Plus className="w-4 h-4" /> Create Tenant
        </button>
      </div>

      {/* Tenants Table */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700/50">
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Organization</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Plan</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Status</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Created</th>
              <th className="text-right px-4 py-3 text-slate-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {tenants.map((t) => (
              <tr key={t.id} data-testid={`tenant-row-${t.id}`} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-violet-400" />
                    <div>
                      <div className="text-white font-medium">{t.name}</div>
                      <div className="text-xs text-slate-500">{t.slug}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${planColors[t.plan] || planColors.free}`}>
                    {t.plan?.toUpperCase()}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${t.active ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"}`}>
                    {t.active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs text-slate-400">{t.created_at ? new Date(t.created_at).toLocaleDateString() : "—"}</td>
                <td className="px-4 py-3 text-right">
                  <button data-testid={`delete-tenant-${t.id}`} onClick={() => handleDelete(t.id, t.name)}
                    className="p-1.5 rounded bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {tenants.length === 0 && <div className="text-center text-slate-500 py-8">No tenants found</div>}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowCreate(false)}>
          <div data-testid="create-tenant-modal" className="bg-slate-800 border border-slate-700 rounded-xl p-6 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">Create Tenant</h3>
              <button onClick={() => setShowCreate(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-300 mb-1">Organization Name</label>
                <input data-testid="tenant-name-input" type="text" required value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm" placeholder="Acme Corp" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Plan</label>
                <select data-testid="tenant-plan-select" value={createForm.plan}
                  onChange={(e) => setCreateForm({ ...createForm, plan: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm">
                  <option value="free">Free</option>
                  <option value="pro">Pro</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
              <div className="flex gap-3 justify-end">
                <button type="button" onClick={() => setShowCreate(false)}
                  className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-600">Cancel</button>
                <button data-testid="create-tenant-submit" type="submit" disabled={saving}
                  className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm hover:bg-cyan-700 disabled:opacity-50">
                  {saving ? "Creating..." : "Create Tenant"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

/* ═══════════════════ Main Tab Component ═══════════════ */
export const UserManagementTab = ({ currentRole }) => {
  const [subTab, setSubTab] = useState("users");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [roles, setRoles] = useState({});
  const [showInvite, setShowInvite] = useState(false);
  const [inviteForm, setInviteForm] = useState({ email: "", full_name: "", role: "analyst" });
  const [saving, setSaving] = useState(false);
  const [myProfile, setMyProfile] = useState(null);

  const token = localStorage.getItem("token");
  const authHeaders = { "Content-Type": "application/json", Authorization: `Bearer ${token}` };

  const isSuperAdmin = currentRole === "super_admin";
  const subTabs = isSuperAdmin ? SUB_TABS_SUPER : SUB_TABS_DEFAULT;
  const canManageUsers = ["super_admin", "tenant_admin"].includes(currentRole);
  const rolesICanAssign = assignableRoles(currentRole);

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

  const fetchMyProfile = useCallback(async () => {
    try {
      const data = await fetcher(`${RBAC_API}/me`, { headers: authHeaders });
      setMyProfile(data);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchUsers(); fetchRoles(); fetchMyProfile(); }, [fetchUsers, fetchRoles, fetchMyProfile]);

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

  const myLevel = ROLE_HIERARCHY.indexOf(currentRole);

  if (loading) return <div className="text-slate-400 text-center py-12">Loading users...</div>;

  return (
    <div data-testid="user-management-tab" className="space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex gap-2 border-b border-slate-700/50 pb-1">
        {subTabs.map((st) => (
          <button
            key={st.id}
            data-testid={`subtab-${st.id}`}
            onClick={() => setSubTab(st.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg text-sm transition-colors ${
              subTab === st.id
                ? "bg-slate-800/80 text-cyan-400 font-medium border-b-2 border-cyan-400"
                : "text-slate-400 hover:text-white hover:bg-slate-800/30"
            }`}
          >
            <st.icon className="w-4 h-4" /> {st.label}
          </button>
        ))}
      </div>

      {subTab === "migration" && isSuperAdmin && <TenantMigrationPanel />}
      {subTab === "tenants" && isSuperAdmin && <TenantManagementPanel token={token} />}

      {subTab === "users" && (
      <>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white">User Management</h2>
          <p className="text-sm text-slate-400">
            {isSuperAdmin ? "Manage all CVE platform users across tenants" : "Manage users in your organization"}
          </p>
        </div>
        {canManageUsers && (
          <button data-testid="invite-user-btn" onClick={() => setShowInvite(true)}
            className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
            <Plus className="w-4 h-4" /> Invite User
          </button>
        )}
      </div>

      {/* Role Legend */}
      <div className="flex gap-4 flex-wrap">
        {Object.entries(ROLE_BADGES).map(([key, r]) => (
          <div key={key} className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.bg} ${r.text}`}>{r.label}</span>
            <span className="text-xs text-slate-500">{roles[key]?.description || ""}</span>
          </div>
        ))}
      </div>

      {/* Users Table */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700/50">
              <th className="text-left px-4 py-3 text-slate-400 font-medium">User</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Role</th>
              {isSuperAdmin && <th className="text-left px-4 py-3 text-slate-400 font-medium">Tenant</th>}
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Status</th>
              <th className="text-left px-4 py-3 text-slate-400 font-medium">Joined</th>
              <th className="text-right px-4 py-3 text-slate-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => {
              const badge = ROLE_BADGES[u.cve_role] || ROLE_BADGES.analyst;
              const targetLevel = ROLE_HIERARCHY.indexOf(u.cve_role);
              const canEdit = canManageUsers && targetLevel < myLevel && u.user_id !== myProfile?.user_id;
              return (
                <tr key={u.user_id} data-testid={`user-row-${u.user_id}`} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                  <td className="px-4 py-3">
                    <div className="text-white font-medium">{u.full_name}</div>
                    <div className="text-xs text-slate-400">{u.email}</div>
                  </td>
                  <td className="px-4 py-3">
                    {canEdit ? (
                      <select data-testid={`role-select-${u.user_id}`} value={u.cve_role}
                        onChange={(e) => handleRoleChange(u.user_id, e.target.value)}
                        className="bg-slate-700 border border-slate-600 text-white text-xs rounded-lg px-2 py-1.5 focus:ring-cyan-500 focus:border-cyan-500">
                        {rolesICanAssign.map((r) => (
                          <option key={r} value={r}>{ROLE_BADGES[r]?.label || r}</option>
                        ))}
                        {/* Keep current role visible even if not assignable */}
                        {!rolesICanAssign.includes(u.cve_role) && (
                          <option value={u.cve_role} disabled>{ROLE_BADGES[u.cve_role]?.label || u.cve_role}</option>
                        )}
                      </select>
                    ) : (
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>{badge.label}</span>
                    )}
                  </td>
                  {isSuperAdmin && (
                    <td className="px-4 py-3">
                      <span className="text-xs text-slate-400">{u.tenant_id ? u.tenant_id.substring(0, 8) + "..." : "—"}</span>
                    </td>
                  )}
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${u.is_active ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"}`}>
                      {u.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">{u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}</td>
                  <td className="px-4 py-3 text-right">
                    {canEdit && (
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

      {/* Invite Modal */}
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
                <input data-testid="invite-email" type="email" required value={inviteForm.email}
                  onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm" placeholder="user@example.com" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Full Name</label>
                <input data-testid="invite-name" type="text" required value={inviteForm.full_name}
                  onChange={(e) => setInviteForm({ ...inviteForm, full_name: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm" placeholder="John Doe" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Role</label>
                <select data-testid="invite-role" value={inviteForm.role}
                  onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2 text-sm">
                  {rolesICanAssign.map((r) => (
                    <option key={r} value={r}>{ROLE_BADGES[r]?.label || r}</option>
                  ))}
                </select>
              </div>
              <div className="flex gap-3 justify-end">
                <button type="button" onClick={() => setShowInvite(false)}
                  className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-600">Cancel</button>
                <button data-testid="invite-submit-btn" type="submit" disabled={saving}
                  className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm hover:bg-cyan-700 disabled:opacity-50">
                  {saving ? "Inviting..." : "Invite User"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      </>
      )}
    </div>
  );
};
