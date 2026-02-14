import React, { useState, useEffect, useCallback } from "react";
import { Shield, AlertTriangle, CheckCircle, Clock, Search, Plus, RefreshCw, ChevronDown, ChevronRight, Package, Server, FileText, Settings, Activity, XCircle, Eye, Box, Layers } from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api/cve`;

const SEVERITY_COLORS = {
  critical: { bg: "bg-red-900/30", text: "text-red-400", border: "border-red-500/40", badge: "bg-red-500/20 text-red-300", dot: "bg-red-500" },
  high: { bg: "bg-orange-900/30", text: "text-orange-400", border: "border-orange-500/40", badge: "bg-orange-500/20 text-orange-300", dot: "bg-orange-500" },
  medium: { bg: "bg-yellow-900/30", text: "text-yellow-400", border: "border-yellow-500/40", badge: "bg-yellow-500/20 text-yellow-300", dot: "bg-yellow-500" },
  low: { bg: "bg-blue-900/30", text: "text-blue-400", border: "border-blue-500/40", badge: "bg-blue-500/20 text-blue-300", dot: "bg-blue-500" },
  info: { bg: "bg-slate-800/30", text: "text-slate-400", border: "border-slate-500/40", badge: "bg-slate-500/20 text-slate-300", dot: "bg-slate-500" },
};

const STATUS_COLORS = {
  detected: "bg-red-500/20 text-red-300",
  triaged: "bg-yellow-500/20 text-yellow-300",
  in_progress: "bg-blue-500/20 text-blue-300",
  fixed: "bg-emerald-500/20 text-emerald-300",
  verified: "bg-green-500/20 text-green-300",
  dismissed: "bg-slate-500/20 text-slate-400",
  wont_fix: "bg-slate-500/20 text-slate-400",
};

const fetcher = async (url, opts = {}) => {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
};

// ─── Stat Card ───────────────────────────────────────────────
const StatCard = ({ icon: Icon, label, value, color = "text-white", subtext }) => (
  <div data-testid={`stat-${label.toLowerCase().replace(/\s+/g, "-")}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
    <div className="flex items-center gap-3 mb-2">
      <div className={`p-2 rounded-lg bg-slate-700/50`}><Icon className={`w-5 h-5 ${color}`} /></div>
      <span className="text-slate-400 text-sm">{label}</span>
    </div>
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
    {subtext && <div className="text-xs text-slate-500 mt-1">{subtext}</div>}
  </div>
);

// ─── Severity Badge ──────────────────────────────────────────
const SeverityBadge = ({ severity }) => {
  const c = SEVERITY_COLORS[severity] || SEVERITY_COLORS.info;
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${c.badge}`}>{severity.toUpperCase()}</span>;
};

const StatusBadge = ({ status }) => (
  <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[status] || STATUS_COLORS.detected}`}>
    {status.replace("_", " ").toUpperCase()}
  </span>
);

// ═══════════════════════════════════════════════════════════════
// OVERVIEW TAB
// ═══════════════════════════════════════════════════════════════
const OverviewTab = ({ dashboard, onRefresh, loading }) => {
  if (!dashboard) return <div className="text-slate-400 p-8 text-center">Loading...</div>;
  const { severity_breakdown: sb } = dashboard;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <StatCard icon={AlertTriangle} label="Open CVEs" value={dashboard.open_cves} color="text-red-400" />
        <StatCard icon={Clock} label="Overdue" value={dashboard.overdue_cves} color="text-orange-400" />
        <StatCard icon={CheckCircle} label="Fixed" value={dashboard.fixed_cves} color="text-emerald-400" />
        <StatCard icon={Shield} label="Verified" value={dashboard.verified_cves} color="text-green-400" />
        <StatCard icon={Server} label="Services" value={dashboard.total_services} color="text-cyan-400" />
        <StatCard icon={Box} label="SBOMs" value={dashboard.total_sboms} color="text-purple-400" />
      </div>

      {/* Severity breakdown */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-4">Open CVEs by Severity</h3>
        <div className="grid grid-cols-5 gap-3">
          {["critical", "high", "medium", "low", "info"].map((s) => {
            const c = SEVERITY_COLORS[s];
            return (
              <div key={s} className={`${c.bg} border ${c.border} rounded-lg p-4 text-center`}>
                <div className={`text-2xl font-bold ${c.text}`}>{sb[s] || 0}</div>
                <div className={`text-xs ${c.text} mt-1 uppercase`}>{s}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Recent CVEs */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3">Recent CVEs</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {(dashboard.recent_cves || []).map((c) => (
              <div key={c.id} className="flex items-center justify-between bg-slate-700/30 rounded-lg px-3 py-2">
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-white truncate">{c.cve_id}</div>
                  <div className="text-xs text-slate-400 truncate">{c.title}</div>
                </div>
                <div className="flex items-center gap-2 ml-2 shrink-0">
                  <SeverityBadge severity={c.severity} />
                  <StatusBadge status={c.status} />
                </div>
              </div>
            ))}
            {(!dashboard.recent_cves || dashboard.recent_cves.length === 0) && (
              <div className="text-slate-500 text-sm text-center py-4">No CVEs yet. Run a scan to detect vulnerabilities.</div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3">Recent Activity</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {(dashboard.recent_activity || []).map((a) => (
              <div key={a.id} className="flex items-start gap-3 bg-slate-700/30 rounded-lg px-3 py-2">
                <Activity className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div className="min-w-0">
                  <div className="text-sm text-white truncate">{a.message}</div>
                  <div className="text-xs text-slate-500">{new Date(a.timestamp).toLocaleString()}</div>
                </div>
              </div>
            ))}
            {(!dashboard.recent_activity || dashboard.recent_activity.length === 0) && (
              <div className="text-slate-500 text-sm text-center py-4">No activity recorded yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// CVE DATABASE TAB
// ═══════════════════════════════════════════════════════════════
const CVEDatabaseTab = ({ onRefresh }) => {
  const [cves, setCves] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: "", severity: "", search: "" });
  const [expanded, setExpanded] = useState(null);
  const [showCreate, setShowCreate] = useState(false);

  const fetchCves = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.status) params.set("status", filters.status);
      if (filters.severity) params.set("severity", filters.severity);
      if (filters.search) params.set("search", filters.search);
      params.set("limit", "50");
      const data = await fetcher(`${API}/entries?${params}`);
      setCves(data.items || []);
      setTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [filters]);

  useEffect(() => { fetchCves(); }, [fetchCves]);

  const handleStatusChange = async (id, newStatus) => {
    try {
      await fetcher(`${API}/entries/${id}/status`, { method: "PUT", body: JSON.stringify({ status: newStatus }) });
      fetchCves();
      onRefresh();
    } catch (e) { console.error(e); }
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input data-testid="cve-search-input" className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" placeholder="Search CVE ID, package, title..." value={filters.search} onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))} />
        </div>
        <select data-testid="cve-status-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={filters.status} onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}>
          <option value="">All Statuses</option>
          {["detected", "triaged", "in_progress", "fixed", "verified", "dismissed", "wont_fix"].map((s) => <option key={s} value={s}>{s.replace("_", " ").toUpperCase()}</option>)}
        </select>
        <select data-testid="cve-severity-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={filters.severity} onChange={(e) => setFilters((f) => ({ ...f, severity: e.target.value }))}>
          <option value="">All Severities</option>
          {["critical", "high", "medium", "low", "info"].map((s) => <option key={s} value={s}>{s.toUpperCase()}</option>)}
        </select>
        <button data-testid="cve-create-btn" onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          <Plus className="w-4 h-4" /> Add CVE
        </button>
      </div>

      <div className="text-sm text-slate-400">{total} CVE{total !== 1 ? "s" : ""} found</div>

      {/* CVE List */}
      <div className="space-y-2">
        {cves.map((c) => (
          <div key={c.id} className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-slate-700/30 transition-colors" onClick={() => setExpanded(expanded === c.id ? null : c.id)}>
              <div className="flex items-center gap-3 flex-1 min-w-0">
                {expanded === c.id ? <ChevronDown className="w-4 h-4 text-slate-400 shrink-0" /> : <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-cyan-400 font-mono text-sm">{c.cve_id}</span>
                    <SeverityBadge severity={c.severity} />
                    <StatusBadge status={c.status} />
                  </div>
                  <div className="text-sm text-white mt-0.5 truncate">{c.title}</div>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0 ml-4">
                <span className="text-xs text-slate-500">{c.affected_package}</span>
                {c.cvss_score > 0 && <span className="text-xs font-mono text-slate-400">CVSS {c.cvss_score}</span>}
              </div>
            </div>
            {expanded === c.id && (
              <div className="px-4 pb-4 border-t border-slate-700/50 pt-3 space-y-3">
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div><span className="text-slate-500">Package:</span> <span className="text-white ml-2">{c.affected_package} {c.affected_version}</span></div>
                  <div><span className="text-slate-500">Fixed in:</span> <span className="text-emerald-400 ml-2">{c.fixed_version || "N/A"}</span></div>
                  <div><span className="text-slate-500">Source:</span> <span className="text-white ml-2">{c.source}</span></div>
                  <div><span className="text-slate-500">Exploitability:</span> <span className="text-white ml-2">{c.exploitability}</span></div>
                  <div><span className="text-slate-500">Detected:</span> <span className="text-white ml-2">{new Date(c.detected_at).toLocaleString()}</span></div>
                  <div><span className="text-slate-500">Assigned:</span> <span className="text-white ml-2">{c.assigned_to || c.assigned_team || "Unassigned"}</span></div>
                </div>
                {c.description && <div className="text-sm text-slate-300 bg-slate-900/50 rounded-lg p-3">{c.description}</div>}
                {c.affected_services?.length > 0 && (
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-slate-500">Services:</span>
                    {c.affected_services.map((s) => <span key={s} className="px-2 py-0.5 bg-slate-700/50 rounded text-xs text-slate-300">{s}</span>)}
                  </div>
                )}
                {/* Status transition buttons */}
                <div className="flex items-center gap-2 pt-2">
                  <span className="text-xs text-slate-500 mr-2">Transition:</span>
                  {c.status === "detected" && <><button onClick={() => handleStatusChange(c.id, "triaged")} className="px-3 py-1 rounded text-xs bg-yellow-600/30 text-yellow-300 hover:bg-yellow-600/50 transition-colors">Triage</button><button onClick={() => handleStatusChange(c.id, "dismissed")} className="px-3 py-1 rounded text-xs bg-slate-600/30 text-slate-300 hover:bg-slate-600/50 transition-colors">Dismiss</button></>}
                  {c.status === "triaged" && <><button onClick={() => handleStatusChange(c.id, "in_progress")} className="px-3 py-1 rounded text-xs bg-blue-600/30 text-blue-300 hover:bg-blue-600/50 transition-colors">Start Fix</button><button onClick={() => handleStatusChange(c.id, "wont_fix")} className="px-3 py-1 rounded text-xs bg-slate-600/30 text-slate-300 hover:bg-slate-600/50 transition-colors">Won't Fix</button></>}
                  {c.status === "in_progress" && <button onClick={() => handleStatusChange(c.id, "fixed")} className="px-3 py-1 rounded text-xs bg-emerald-600/30 text-emerald-300 hover:bg-emerald-600/50 transition-colors">Mark Fixed</button>}
                  {c.status === "fixed" && <button onClick={() => handleStatusChange(c.id, "verified")} className="px-3 py-1 rounded text-xs bg-green-600/30 text-green-300 hover:bg-green-600/50 transition-colors">Verify</button>}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-center text-slate-400 py-8">Loading CVEs...</div>}
        {!loading && cves.length === 0 && <div className="text-center text-slate-500 py-8">No CVEs found. Run a scan or add one manually.</div>}
      </div>

      {/* Create CVE Modal */}
      {showCreate && <CreateCVEModal onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); fetchCves(); onRefresh(); }} />}
    </div>
  );
};

// ─── Create CVE Modal ────────────────────────────────────────
const CreateCVEModal = ({ onClose, onCreated }) => {
  const [form, setForm] = useState({ cve_id: "", title: "", description: "", severity: "medium", cvss_score: 0, affected_package: "", affected_version: "", fixed_version: "", affected_services: "", source: "manual" });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetcher(`${API}/entries`, {
        method: "POST",
        body: JSON.stringify({ ...form, cvss_score: parseFloat(form.cvss_score) || 0, affected_services: form.affected_services ? form.affected_services.split(",").map((s) => s.trim()) : [] }),
      });
      onCreated();
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-white text-lg font-semibold mb-4">Report New CVE</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input data-testid="cve-create-id" placeholder="CVE ID (e.g. CVE-2026-XXXX)" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm col-span-2" value={form.cve_id} onChange={(e) => setForm({ ...form, cve_id: e.target.value })} />
            <input data-testid="cve-create-title" placeholder="Title *" required className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm col-span-2" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <select data-testid="cve-create-severity" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
              {["critical", "high", "medium", "low", "info"].map((s) => <option key={s} value={s}>{s.toUpperCase()}</option>)}
            </select>
            <input data-testid="cve-create-cvss" type="number" step="0.1" min="0" max="10" placeholder="CVSS Score" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.cvss_score} onChange={(e) => setForm({ ...form, cvss_score: e.target.value })} />
            <input data-testid="cve-create-package" placeholder="Affected Package" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.affected_package} onChange={(e) => setForm({ ...form, affected_package: e.target.value })} />
            <input placeholder="Affected Version" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.affected_version} onChange={(e) => setForm({ ...form, affected_version: e.target.value })} />
            <input placeholder="Fixed Version" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.fixed_version} onChange={(e) => setForm({ ...form, fixed_version: e.target.value })} />
            <input placeholder="Services (comma-separated)" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.affected_services} onChange={(e) => setForm({ ...form, affected_services: e.target.value })} />
          </div>
          <textarea placeholder="Description" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm h-20" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white text-sm">Cancel</button>
            <button data-testid="cve-create-submit" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">{saving ? "Saving..." : "Create CVE"}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// SERVICES TAB
// ═══════════════════════════════════════════════════════════════
const ServicesTab = ({ onRefresh }) => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const fetchServices = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetcher(`${API}/services`);
      setServices(data);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchServices(); }, [fetchServices]);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this service?")) return;
    try {
      await fetcher(`${API}/services/${id}`, { method: "DELETE" });
      fetchServices();
      onRefresh();
    } catch (e) { console.error(e); }
  };

  const critColors = { critical: "text-red-400 bg-red-500/10 border-red-500/30", high: "text-orange-400 bg-orange-500/10 border-orange-500/30", medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30", low: "text-blue-400 bg-blue-500/10 border-blue-500/30" };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="text-slate-400 text-sm">{services.length} registered service{services.length !== 1 ? "s" : ""}</div>
        <button data-testid="service-create-btn" onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          <Plus className="w-4 h-4" /> Register Service
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {services.map((s) => (
          <div key={s.id} data-testid={`service-card-${s.name}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="text-white font-semibold">{s.name}</div>
                <div className="text-xs text-slate-400 mt-0.5">{s.description}</div>
              </div>
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${critColors[s.criticality] || critColors.medium}`}>{s.criticality?.toUpperCase()}</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs mb-3">
              <div><span className="text-slate-500">Owner:</span> <span className="text-white ml-1">{s.owner || "—"}</span></div>
              <div><span className="text-slate-500">Team:</span> <span className="text-white ml-1">{s.team || "—"}</span></div>
              <div><span className="text-slate-500">Env:</span> <span className="text-white ml-1">{s.environment}</span></div>
              <div><span className="text-slate-500">Open CVEs:</span> <span className={`ml-1 font-medium ${s.open_cves > 0 ? "text-red-400" : "text-emerald-400"}`}>{s.open_cves || 0}</span></div>
            </div>
            {s.tech_stack?.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {s.tech_stack.map((t) => <span key={t} className="px-2 py-0.5 bg-slate-700/50 rounded text-xs text-slate-300">{t}</span>)}
              </div>
            )}
            {s.repo_url && <a href={s.repo_url} target="_blank" rel="noopener noreferrer" className="text-xs text-cyan-400 hover:underline">{s.repo_url}</a>}
            <div className="mt-3 pt-3 border-t border-slate-700/40 flex justify-end">
              <button onClick={() => handleDelete(s.id)} className="text-xs text-red-400 hover:text-red-300 transition-colors">Delete</button>
            </div>
          </div>
        ))}
      </div>
      {loading && <div className="text-center text-slate-400 py-8">Loading services...</div>}
      {!loading && services.length === 0 && <div className="text-center text-slate-500 py-8">No services registered. Seed sample data or add services.</div>}

      {showCreate && <CreateServiceModal onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); fetchServices(); onRefresh(); }} />}
    </div>
  );
};

const CreateServiceModal = ({ onClose, onCreated }) => {
  const [form, setForm] = useState({ name: "", description: "", repo_url: "", owner: "", team: "", environment: "production", criticality: "medium", tech_stack: "" });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetcher(`${API}/services`, {
        method: "POST",
        body: JSON.stringify({ ...form, tech_stack: form.tech_stack ? form.tech_stack.split(",").map((s) => s.trim()) : [] }),
      });
      onCreated();
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-white text-lg font-semibold mb-4">Register Service</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input data-testid="service-create-name" required placeholder="Service Name *" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input placeholder="Description" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <input placeholder="Repository URL" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.repo_url} onChange={(e) => setForm({ ...form, repo_url: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input placeholder="Owner" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} />
            <input placeholder="Team" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.team} onChange={(e) => setForm({ ...form, team: e.target.value })} />
            <select className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}>
              <option value="production">Production</option><option value="staging">Staging</option><option value="development">Development</option>
            </select>
            <select className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.criticality} onChange={(e) => setForm({ ...form, criticality: e.target.value })}>
              <option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
            </select>
          </div>
          <input placeholder="Tech Stack (comma-separated)" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.tech_stack} onChange={(e) => setForm({ ...form, tech_stack: e.target.value })} />
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white text-sm">Cancel</button>
            <button data-testid="service-create-submit" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">{saving ? "Saving..." : "Register"}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// SBOM TAB
// ═══════════════════════════════════════════════════════════════
const SBOMTab = ({ onRefresh }) => {
  const [sboms, setSboms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedSbom, setSelectedSbom] = useState(null);
  const [sbomDetail, setSbomDetail] = useState(null);

  const fetchSboms = useCallback(async () => {
    setLoading(true);
    try { setSboms(await fetcher(`${API}/sbom/list`)); } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchSboms(); }, [fetchSboms]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await fetcher(`${API}/sbom/generate`, { method: "POST" });
      fetchSboms();
      onRefresh();
    } catch (e) { console.error(e); }
    setGenerating(false);
  };

  const handleView = async (id) => {
    if (selectedSbom === id) { setSelectedSbom(null); setSbomDetail(null); return; }
    try {
      const detail = await fetcher(`${API}/sbom/${id}`);
      setSbomDetail(detail);
      setSelectedSbom(id);
    } catch (e) { console.error(e); }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <div className="text-white font-semibold">Software Bill of Materials</div>
          <div className="text-slate-400 text-xs mt-0.5">Track every dependency in your stack</div>
        </div>
        <button data-testid="sbom-generate-btn" onClick={handleGenerate} disabled={generating} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
          <Layers className="w-4 h-4" /> {generating ? "Generating..." : "Generate SBOM"}
        </button>
      </div>

      <div className="space-y-3">
        {sboms.map((s) => (
          <div key={s.id} className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-slate-700/30 transition-colors" onClick={() => handleView(s.id)}>
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-purple-400" />
                <div>
                  <div className="text-white text-sm font-medium">{s.service_name} — {s.environment}</div>
                  <div className="text-xs text-slate-400">{new Date(s.generated_at).toLocaleString()} | {s.total_components} components | Hash: {s.hash?.slice(0, 12)}...</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded">FE: {s.frontend_components}</span>
                <span className="text-xs text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded">BE: {s.backend_components}</span>
                <Eye className="w-4 h-4 text-slate-400" />
              </div>
            </div>
            {selectedSbom === s.id && sbomDetail && (
              <div className="px-4 pb-4 border-t border-slate-700/50 pt-3">
                <div className="text-xs text-slate-400 mb-2">{sbomDetail.components?.length || 0} components</div>
                <div className="max-h-60 overflow-y-auto space-y-1">
                  {(sbomDetail.components || []).map((c, i) => (
                    <div key={i} className="flex items-center justify-between bg-slate-900/50 rounded px-3 py-1.5 text-xs">
                      <div className="flex items-center gap-2">
                        <Package className="w-3 h-3 text-slate-500" />
                        <span className="text-white">{c.name}</span>
                        <span className="text-slate-500">@{c.version}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-1.5 py-0.5 rounded ${c.layer === "frontend" ? "bg-purple-500/10 text-purple-300" : "bg-cyan-500/10 text-cyan-300"}`}>{c.layer}</span>
                        <span className="text-slate-500">{c.type}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-center text-slate-400 py-8">Loading SBOMs...</div>}
        {!loading && sboms.length === 0 && <div className="text-center text-slate-500 py-8">No SBOMs generated yet. Click &quot;Generate SBOM&quot; to create one.</div>}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// POLICIES TAB
// ═══════════════════════════════════════════════════════════════
const PoliciesTab = ({ onRefresh }) => {
  const [policies, setPolicies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      try { setPolicies(await fetcher(`${API}/policies`)); } catch (e) { console.error(e); }
      setLoading(false);
    })();
  }, []);

  const handleChange = (severity, field, value) => {
    setPolicies((p) => ({ ...p, [severity]: { ...p[severity], [field]: field.includes("auto") ? value : parseInt(value) || 0 } }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetcher(`${API}/policies`, { method: "PUT", body: JSON.stringify({ policies }) });
      onRefresh();
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  if (loading || !policies) return <div className="text-slate-400 p-8 text-center">Loading policies...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="text-white font-semibold">Severity Policies & SLAs</div>
          <div className="text-slate-400 text-xs mt-0.5">Configure response time requirements and automated actions per severity level</div>
        </div>
        <button data-testid="policies-save-btn" onClick={handleSave} disabled={saving} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
          {saving ? "Saving..." : "Save Policies"}
        </button>
      </div>

      <div className="space-y-4">
        {["critical", "high", "medium", "low", "info"].map((sev) => {
          const c = SEVERITY_COLORS[sev];
          const p = policies[sev] || {};
          return (
            <div key={sev} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-3 h-3 rounded-full ${c.dot}`} />
                <span className={`text-lg font-semibold ${c.text} uppercase`}>{sev}</span>
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">SLA (hours)</label>
                  <input data-testid={`policy-sla-${sev}`} type="number" min="0" className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={p.sla_hours || 0} onChange={(e) => handleChange(sev, "sla_hours", e.target.value)} />
                  <span className="text-xs text-slate-500 mt-1 block">{p.sla_hours ? `${(p.sla_hours / 24).toFixed(1)} days` : "No SLA"}</span>
                </div>
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded bg-slate-900 border-slate-600 text-cyan-500" checked={p.auto_block_deploy || false} onChange={(e) => handleChange(sev, "auto_block_deploy", e.target.checked)} />
                    <span className="text-sm text-slate-300">Block Deploy</span>
                  </label>
                </div>
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded bg-slate-900 border-slate-600 text-cyan-500" checked={p.auto_create_pr || false} onChange={(e) => handleChange(sev, "auto_create_pr", e.target.checked)} />
                    <span className="text-sm text-slate-300">Auto-Create PR</span>
                  </label>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// AUDIT TRAIL TAB
// ═══════════════════════════════════════════════════════════════
const AuditTrailTab = () => {
  const [trail, setTrail] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("");

  const fetchTrail = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (actionFilter) params.set("action", actionFilter);
      const data = await fetcher(`${API}/audit-trail?${params}`);
      setTrail(data.items || []);
      setTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [actionFilter]);

  useEffect(() => { fetchTrail(); }, [fetchTrail]);

  const actionColors = {
    cve_created: "bg-red-500/10 text-red-400",
    status_changed: "bg-yellow-500/10 text-yellow-400",
    cve_updated: "bg-blue-500/10 text-blue-400",
    scan_completed: "bg-emerald-500/10 text-emerald-400",
    sbom_generated: "bg-purple-500/10 text-purple-400",
    service_created: "bg-cyan-500/10 text-cyan-400",
    service_updated: "bg-cyan-500/10 text-cyan-400",
    service_deleted: "bg-slate-500/10 text-slate-400",
    policies_updated: "bg-orange-500/10 text-orange-400",
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <select data-testid="audit-action-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={actionFilter} onChange={(e) => setActionFilter(e.target.value)}>
          <option value="">All Actions</option>
          {["cve_created", "status_changed", "cve_updated", "scan_completed", "sbom_generated", "service_created", "policies_updated"].map((a) => <option key={a} value={a}>{a.replace("_", " ").toUpperCase()}</option>)}
        </select>
        <span className="text-sm text-slate-400">{total} entries</span>
      </div>

      <div className="space-y-2">
        {trail.map((a) => (
          <div key={a.id} className="flex items-start gap-3 bg-slate-800/60 border border-slate-700/50 rounded-lg px-4 py-3">
            <div className="mt-0.5 shrink-0">
              <div className={`w-2 h-2 rounded-full ${a.action.includes("created") ? "bg-emerald-400" : a.action.includes("changed") ? "bg-yellow-400" : a.action.includes("scan") ? "bg-blue-400" : "bg-slate-400"}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${actionColors[a.action] || "bg-slate-500/10 text-slate-400"}`}>{a.action.replace("_", " ")}</span>
                <span className="text-xs text-slate-500 font-mono">{a.target_id?.slice(0, 20)}</span>
              </div>
              <div className="text-sm text-white mt-1">{a.message}</div>
              <div className="text-xs text-slate-500 mt-0.5">{new Date(a.timestamp).toLocaleString()} — {a.user}</div>
            </div>
          </div>
        ))}
        {loading && <div className="text-center text-slate-400 py-8">Loading audit trail...</div>}
        {!loading && trail.length === 0 && <div className="text-center text-slate-500 py-8">No audit entries found.</div>}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// MAIN DASHBOARD
// ═══════════════════════════════════════════════════════════════
const TABS = [
  { id: "overview", label: "Overview", icon: Shield },
  { id: "cves", label: "CVE Database", icon: AlertTriangle },
  { id: "services", label: "Services", icon: Server },
  { id: "sbom", label: "SBOM", icon: Layers },
  { id: "policies", label: "Policies", icon: Settings },
  { id: "audit", label: "Audit Trail", icon: Activity },
];

export default function CVEManagementDashboard() {
  const [tab, setTab] = useState("overview");
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [seeding, setSeeding] = useState(false);

  const fetchDashboard = useCallback(async () => {
    try { setDashboard(await fetcher(`${API}/dashboard`)); } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchDashboard(); }, [fetchDashboard]);

  const handleScan = async () => {
    setScanning(true);
    try { await fetcher(`${API}/scan`, { method: "POST" }); fetchDashboard(); } catch (e) { console.error(e); }
    setScanning(false);
  };

  const handleSeed = async () => {
    setSeeding(true);
    try { await fetcher(`${API}/seed`, { method: "POST" }); fetchDashboard(); } catch (e) { console.error(e); }
    setSeeding(false);
  };

  return (
    <div data-testid="cve-management-dashboard" className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="border-b border-slate-800/60 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-cyan-500/10 rounded-xl"><Shield className="w-7 h-7 text-cyan-400" /></div>
              <div>
                <h1 className="text-xl font-bold text-white">CVE Management Platform</h1>
                <p className="text-xs text-slate-400">Central vulnerability brain — detect, triage, fix, verify</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button data-testid="seed-data-btn" onClick={handleSeed} disabled={seeding} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors disabled:opacity-50">{seeding ? "Seeding..." : "Seed Data"}</button>
              <button data-testid="run-scan-btn" onClick={handleScan} disabled={scanning} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
                <RefreshCw className={`w-4 h-4 ${scanning ? "animate-spin" : ""}`} /> {scanning ? "Scanning..." : "Run Scan"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800/60 bg-slate-900/40">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1 overflow-x-auto py-1">
            {TABS.map((t) => (
              <button key={t.id} data-testid={`tab-${t.id}`} onClick={() => setTab(t.id)} className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm transition-all whitespace-nowrap ${tab === t.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
                <t.icon className="w-4 h-4" /> {t.label}
                {t.id === "cves" && dashboard?.open_cves > 0 && <span className="ml-1 px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-xs">{dashboard.open_cves}</span>}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {tab === "overview" && <OverviewTab dashboard={dashboard} onRefresh={fetchDashboard} loading={loading} />}
        {tab === "cves" && <CVEDatabaseTab onRefresh={fetchDashboard} />}
        {tab === "services" && <ServicesTab onRefresh={fetchDashboard} />}
        {tab === "sbom" && <SBOMTab onRefresh={fetchDashboard} />}
        {tab === "policies" && <PoliciesTab onRefresh={fetchDashboard} />}
        {tab === "audit" && <AuditTrailTab />}
      </div>
    </div>
  );
}
