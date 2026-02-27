import React, { useState, useEffect, useCallback } from "react";
import { Building2, Plus, Users, Trash2, Settings, ChevronRight, Loader2, Shield, Crown } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api/tenants`;

const fetcher = async (url, opts = {}) => {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
};

const PLAN_COLORS = {
  free: "bg-slate-500/20 text-slate-300",
  pro: "bg-blue-500/20 text-blue-300",
  enterprise: "bg-purple-500/20 text-purple-300",
};

function CreateTenantModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ name: "", plan: "free" });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetcher(API + "/", { method: "POST", body: JSON.stringify(form) });
      onCreated();
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-white text-lg font-semibold mb-4">Create Organization</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input data-testid="tenant-name-input" required placeholder="Organization Name *" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <div>
            <label className="text-xs text-slate-400 block mb-1">Plan</label>
            <select data-testid="tenant-plan-select" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.plan} onChange={(e) => setForm({ ...form, plan: e.target.value })}>
              <option value="free">Free (5 users, 100 CVEs)</option>
              <option value="pro">Pro (25 users, 5K CVEs)</option>
              <option value="enterprise">Enterprise (Unlimited)</option>
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white text-sm">Cancel</button>
            <button data-testid="tenant-create-submit" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">{saving ? "Creating..." : "Create"}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

function TenantCard({ tenant, onSelect, onDelete }) {
  return (
    <div data-testid={`tenant-card-${tenant.id}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 hover:border-cyan-500/30 transition-all cursor-pointer group" onClick={() => onSelect(tenant)}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-slate-700/50 rounded-lg">
            <Building2 className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="text-white font-medium">{tenant.name}</div>
            <div className="text-xs text-slate-400">{tenant.slug}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${PLAN_COLORS[tenant.plan] || PLAN_COLORS.free}`}>{tenant.plan?.toUpperCase()}</span>
          <button onClick={(e) => { e.stopPropagation(); onDelete(tenant.id); }} className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-all"><Trash2 className="w-4 h-4" /></button>
        </div>
      </div>
      <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
        <span>{tenant.active ? "Active" : "Inactive"}</span>
        <span>Created: {tenant.created_at?.slice(0, 10)}</span>
        <ChevronRight className="w-3 h-3 ml-auto text-slate-500" />
      </div>
    </div>
  );
}

export default function TenantManagement() {
  const [tenants, setTenants] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [tenantUsers, setTenantUsers] = useState([]);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [t, s] = await Promise.all([fetcher(API + "/"), fetcher(API + "/stats")]);
      setTenants(t);
      setStats(s);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleSelectTenant = async (tenant) => {
    setSelectedTenant(tenant);
    try {
      const users = await fetcher(`${API}/${tenant.id}/users`);
      setTenantUsers(users);
    } catch (e) { setTenantUsers([]); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this organization? Users will be unassigned.")) return;
    try { await fetcher(`${API}/${id}`, { method: "DELETE" }); fetchAll(); if (selectedTenant?.id === id) setSelectedTenant(null); } catch (e) { console.error(e); }
  };

  const handleSeed = async () => {
    try { await fetcher(API + "/seed", { method: "POST" }); fetchAll(); } catch (e) { console.error(e); }
  };

  if (loading) return <div className="flex items-center justify-center py-20"><Loader2 className="w-8 h-8 text-cyan-400 animate-spin" /></div>;

  return (
    <div data-testid="tenant-management" className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-500/10 rounded-xl"><Building2 className="w-7 h-7 text-cyan-400" /></div>
            <div>
              <h1 className="text-xl font-bold text-white">Multi-Tenant Management</h1>
              <p className="text-xs text-slate-400">Manage organizations, plans, and user assignments</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button data-testid="seed-tenant-btn" onClick={handleSeed} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors">Seed Default</button>
            <button data-testid="create-tenant-btn" onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
              <Plus className="w-4 h-4" /> New Organization
            </button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-white">{stats.total_tenants}</div>
              <div className="text-xs text-slate-400">Organizations</div>
            </div>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-emerald-400">{stats.active_tenants}</div>
              <div className="text-xs text-slate-400">Active</div>
            </div>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-blue-400">{stats.users_with_tenant}</div>
              <div className="text-xs text-slate-400">Assigned Users</div>
            </div>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-yellow-400">{stats.users_without_tenant}</div>
              <div className="text-xs text-slate-400">Unassigned Users</div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Tenant List */}
          <div className="lg:col-span-2 space-y-3">
            <h2 className="text-white font-semibold text-sm">Organizations ({tenants?.total || 0})</h2>
            {tenants?.items?.length === 0 && (
              <div className="text-center text-slate-500 py-8">No organizations yet. Click "Seed Default" or create one.</div>
            )}
            {tenants?.items?.map((t) => (
              <TenantCard key={t.id} tenant={t} onSelect={handleSelectTenant} onDelete={handleDelete} />
            ))}
          </div>

          {/* Selected Tenant Detail */}
          <div className="space-y-3">
            {selectedTenant ? (
              <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 space-y-4">
                <div className="flex items-center gap-2">
                  <Crown className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-white font-semibold">{selectedTenant.name}</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-slate-400">Plan</span><span className={`px-2 py-0.5 rounded text-xs font-medium ${PLAN_COLORS[selectedTenant.plan]}`}>{selectedTenant.plan?.toUpperCase()}</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">Status</span><span className="text-white">{selectedTenant.active ? "Active" : "Inactive"}</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">Max Users</span><span className="text-white">{selectedTenant.limits?.max_users === -1 ? "Unlimited" : selectedTenant.limits?.max_users}</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">Max CVEs</span><span className="text-white">{selectedTenant.limits?.max_cves === -1 ? "Unlimited" : selectedTenant.limits?.max_cves}</span></div>
                </div>

                <div>
                  <h4 className="text-white font-medium text-sm flex items-center gap-2 mb-2"><Users className="w-4 h-4 text-cyan-400" /> Users ({tenantUsers.length})</h4>
                  <div className="space-y-1 max-h-60 overflow-y-auto">
                    {tenantUsers.map((u) => (
                      <div key={u.id} className="flex items-center justify-between bg-slate-900/50 rounded-lg px-3 py-1.5 text-xs">
                        <span className="text-white">{u.email || u.username || u.id}</span>
                        <span className="text-slate-400">{u.role || "user"}</span>
                      </div>
                    ))}
                    {tenantUsers.length === 0 && <div className="text-xs text-slate-500">No users assigned</div>}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-800/30 border border-slate-700/30 rounded-xl p-8 text-center text-slate-500 text-sm">
                Click an organization to view details
              </div>
            )}
          </div>
        </div>
      </div>

      {showCreate && <CreateTenantModal onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); fetchAll(); }} />}
    </div>
  );
}
