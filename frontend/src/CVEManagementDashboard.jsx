import React, { useState, useEffect, useCallback } from "react";
import { Shield, AlertTriangle, CheckCircle, Clock, Search, Plus, RefreshCw, ChevronDown, ChevronRight, Package, Server, FileText, Settings, Activity, XCircle, Eye, Box, Layers, Scan, GitBranch, Lock, Play, Download, Trash2, ToggleLeft, ToggleRight, Terminal, Copy, Wrench, Github, ExternalLink, CloudLightning, ArrowUpRight, Loader2, CheckCircle2, BarChart3, TrendingUp, Users, Target, Gauge } from "lucide-react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend, AreaChart, Area } from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api/cve`;
const SCANNER_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/scanners`;
const REMEDIATION_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/remediation`;
const GOVERNANCE_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/governance`;

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
  const [assignTarget, setAssignTarget] = useState(null);

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
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500">Owner:</span>
                    <span className={`ml-2 ${c.assigned_to || c.assigned_team ? "text-white" : "text-slate-500 italic"}`}>{c.assigned_to || c.assigned_team || "Unassigned"}</span>
                    <button data-testid={`assign-owner-btn-${c.id}`} onClick={(e) => { e.stopPropagation(); setAssignTarget(c); }} className="ml-1 px-2 py-0.5 rounded text-xs bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/40 transition-colors border border-cyan-500/30">
                      <Users className="w-3 h-3 inline mr-1" />{c.assigned_to ? "Reassign" : "Assign"}
                    </button>
                  </div>
                </div>
                {c.assigned_team && <div className="text-xs text-slate-400"><span className="text-slate-500">Team:</span> <span className="ml-1">{c.assigned_team}</span></div>}
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
      {/* Assign Owner Modal */}
      {assignTarget && <AssignOwnerModal cve={assignTarget} onClose={() => setAssignTarget(null)} onAssigned={() => { setAssignTarget(null); fetchCves(); onRefresh(); }} />}
    </div>
  );
};

// ─── Assign Owner Modal ──────────────────────────────────────
const AssignOwnerModal = ({ cve, onClose, onAssigned }) => {
  const [form, setForm] = useState({ assigned_to: cve?.assigned_to || "", assigned_team: cve?.assigned_team || "", notes: "" });
  const [owners, setOwners] = useState({ people: [], teams: [] });
  const [saving, setSaving] = useState(false);
  const [customPerson, setCustomPerson] = useState(false);
  const [customTeam, setCustomTeam] = useState(false);

  useEffect(() => {
    fetcher(`${API}/owners`).then(setOwners).catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetcher(`${API}/entries/${cve.id}/owner`, { method: "PUT", body: JSON.stringify(form) });
      onAssigned();
    } catch (err) { console.error(err); }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-white text-lg font-semibold mb-1">Assign Owner</h3>
        <p className="text-slate-400 text-sm mb-4">{cve.cve_id} &mdash; {cve.title}</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-slate-400 block mb-1">Assignee</label>
            {!customPerson && owners.people.length > 0 ? (
              <div className="flex gap-2">
                <select data-testid="assign-owner-select" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })}>
                  <option value="">Unassigned</option>
                  {owners.people.map((p) => <option key={p} value={p}>{p}</option>)}
                </select>
                <button type="button" onClick={() => setCustomPerson(true)} className="px-3 py-2 text-xs text-cyan-400 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-700">New</button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input data-testid="assign-owner-input" placeholder="Enter person name" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })} />
                {owners.people.length > 0 && <button type="button" onClick={() => setCustomPerson(false)} className="px-3 py-2 text-xs text-slate-400 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-700">List</button>}
              </div>
            )}
          </div>
          <div>
            <label className="text-sm text-slate-400 block mb-1">Team</label>
            {!customTeam && owners.teams.length > 0 ? (
              <div className="flex gap-2">
                <select data-testid="assign-team-select" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.assigned_team} onChange={(e) => setForm({ ...form, assigned_team: e.target.value })}>
                  <option value="">No Team</option>
                  {owners.teams.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
                <button type="button" onClick={() => setCustomTeam(true)} className="px-3 py-2 text-xs text-cyan-400 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-700">New</button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input data-testid="assign-team-input" placeholder="Enter team name" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.assigned_team} onChange={(e) => setForm({ ...form, assigned_team: e.target.value })} />
                {owners.teams.length > 0 && <button type="button" onClick={() => setCustomTeam(false)} className="px-3 py-2 text-xs text-slate-400 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-700">List</button>}
              </div>
            )}
          </div>
          <div>
            <label className="text-sm text-slate-400 block mb-1">Notes</label>
            <input placeholder="Assignment notes (optional)" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white text-sm">Cancel</button>
            <button data-testid="assign-owner-submit" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">{saving ? "Saving..." : "Assign Owner"}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ─── Create CVE Modal ────────────────────────────────────────
const CreateCVEModal = ({ onClose, onCreated }) => {
  const [form, setForm] = useState({ cve_id: "", title: "", description: "", severity: "medium", cvss_score: 0, affected_package: "", affected_version: "", fixed_version: "", affected_services: "", source: "manual", assigned_to: "", assigned_team: "" });
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
// SCANNERS TAB (Phase 2)
// ═══════════════════════════════════════════════════════════════
const ScannersTab = ({ onRefresh }) => {
  const [tools, setTools] = useState({});
  const [results, setResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [resultDetail, setResultDetail] = useState(null);
  const [running, setRunning] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [t, r] = await Promise.all([fetcher(`${SCANNER_API}/tools`), fetcher(`${SCANNER_API}/results?limit=30`)]);
      setTools(t);
      setResults(r);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const runScanner = async (key, url) => {
    setRunning((r) => ({ ...r, [key]: true }));
    try {
      await fetcher(url, { method: "POST" });
      fetchData();
      onRefresh();
    } catch (e) { console.error(e); }
    setRunning((r) => ({ ...r, [key]: false }));
  };

  const viewResult = async (id) => {
    if (selectedResult === id) { setSelectedResult(null); setResultDetail(null); return; }
    try { setResultDetail(await fetcher(`${SCANNER_API}/results/${id}`)); setSelectedResult(id); } catch (e) { console.error(e); }
  };

  const scanners = [
    { key: "trivy_fs", label: "Trivy Filesystem", desc: "Scan app dependencies for known vulnerabilities", url: `${SCANNER_API}/trivy/fs?target=/app&severity=CRITICAL,HIGH,MEDIUM,LOW`, icon: "FS", color: "bg-blue-500/10 text-blue-400 border-blue-500/30" },
    { key: "trivy_iac", label: "Trivy IaC", desc: "Scan Terraform/IaC for misconfigurations", url: `${SCANNER_API}/trivy/iac?target=/tmp/test_iac`, icon: "IaC", color: "bg-purple-500/10 text-purple-400 border-purple-500/30" },
    { key: "grype", label: "Grype", desc: "Anchore vulnerability scanner for dependencies", url: `${SCANNER_API}/grype?target=dir%3A/app/backend`, icon: "GR", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" },
    { key: "syft", label: "Syft SBOM", desc: "Generate Software Bill of Materials", url: `${SCANNER_API}/syft?target=/app/backend`, icon: "SB", color: "bg-amber-500/10 text-amber-400 border-amber-500/30" },
    { key: "checkov", label: "Checkov", desc: "IaC security scanner for Terraform, K8s, CloudFormation", url: `${SCANNER_API}/checkov?target=/tmp/test_iac`, icon: "CK", color: "bg-pink-500/10 text-pink-400 border-pink-500/30" },
  ];

  const toolStatusDot = (name) => {
    const t = tools[name];
    if (!t) return "bg-slate-500";
    return t.installed ? "bg-emerald-500" : "bg-red-500";
  };

  return (
    <div className="space-y-6">
      {/* Tool Status */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-3">Installed Security Tools</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(tools).map(([name, info]) => (
            <div key={name} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-3 py-2">
              <div className={`w-2.5 h-2.5 rounded-full ${info.installed ? "bg-emerald-500" : "bg-red-500"}`} />
              <div>
                <div className="text-sm text-white font-medium capitalize">{name}</div>
                <div className="text-xs text-slate-500 truncate max-w-[150px]">{info.version || "Not installed"}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Scanner Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {scanners.map((s) => (
          <div key={s.key} data-testid={`scanner-${s.key}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className={`w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold border ${s.color}`}>{s.icon}</span>
                <div>
                  <div className="text-white font-medium text-sm">{s.label}</div>
                  <div className="text-xs text-slate-400">{s.desc}</div>
                </div>
              </div>
            </div>
            <button data-testid={`run-${s.key}`} onClick={() => runScanner(s.key, s.url)} disabled={running[s.key]} className="w-full mt-2 flex items-center justify-center gap-2 bg-cyan-600/80 hover:bg-cyan-600 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
              {running[s.key] ? <><RefreshCw className="w-4 h-4 animate-spin" /> Running...</> : <><Play className="w-4 h-4" /> Run Scan</>}
            </button>
          </div>
        ))}
      </div>

      {/* Scan History */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-3">Scan History</h3>
        <div className="space-y-2 max-h-[500px] overflow-y-auto">
          {results.map((r) => (
            <div key={r.id} className="bg-slate-900/50 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2.5 cursor-pointer hover:bg-slate-800/50 transition-colors" onClick={() => viewResult(r.id)}>
                <div className="flex items-center gap-3">
                  {selectedResult === r.id ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                  <span className="text-xs font-mono text-cyan-400">{r.scanner}</span>
                  <span className="text-xs text-slate-500">{r.scan_type}</span>
                  <span className={`px-1.5 py-0.5 rounded text-xs ${r.status === "completed" ? "bg-emerald-500/10 text-emerald-400" : r.status === "error" ? "bg-red-500/10 text-red-400" : "bg-yellow-500/10 text-yellow-400"}`}>{r.status}</span>
                </div>
                <div className="flex items-center gap-3">
                  {r.summary && <div className="flex items-center gap-2 text-xs">
                    {r.summary.critical > 0 && <span className="text-red-400">{r.summary.critical}C</span>}
                    {r.summary.high > 0 && <span className="text-orange-400">{r.summary.high}H</span>}
                    {r.summary.medium > 0 && <span className="text-yellow-400">{r.summary.medium}M</span>}
                    {(r.summary.total || r.summary.total_packages) > 0 && <span className="text-slate-400">Total: {r.summary.total || r.summary.total_packages}</span>}
                    {r.summary.passed !== undefined && <span className="text-emerald-400">P:{r.summary.passed}</span>}
                    {r.summary.failed !== undefined && <span className="text-red-400">F:{r.summary.failed}</span>}
                  </div>}
                  <span className="text-xs text-slate-500">{new Date(r.started_at).toLocaleString()}</span>
                </div>
              </div>
              {selectedResult === r.id && resultDetail && (
                <div className="px-4 pb-3 border-t border-slate-800/50 pt-2">
                  {/* Vulnerabilities */}
                  {resultDetail.vulnerabilities && (
                    <div className="space-y-1 max-h-60 overflow-y-auto">
                      {resultDetail.vulnerabilities.map((v, i) => (
                        <div key={i} className="flex items-center justify-between bg-slate-800/50 rounded px-3 py-1.5 text-xs">
                          <div className="flex items-center gap-2 min-w-0">
                            <SeverityBadge severity={v.severity} />
                            <span className="text-cyan-400 font-mono">{v.id}</span>
                            <span className="text-white truncate">{v.package}@{v.installed_version}</span>
                          </div>
                          <span className="text-emerald-400 shrink-0 ml-2">{v.fixed_version || "—"}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {/* Misconfigurations (Trivy IaC) */}
                  {resultDetail.misconfigurations && (
                    <div className="space-y-1 max-h-60 overflow-y-auto">
                      {resultDetail.misconfigurations.map((m, i) => (
                        <div key={i} className="bg-slate-800/50 rounded px-3 py-1.5 text-xs">
                          <div className="flex items-center gap-2">
                            <SeverityBadge severity={m.severity} />
                            <span className="text-cyan-400 font-mono">{m.id}</span>
                            <span className="text-white">{m.title}</span>
                          </div>
                          {m.resolution && <div className="text-slate-400 mt-1 ml-4">{m.resolution}</div>}
                        </div>
                      ))}
                    </div>
                  )}
                  {/* Packages (Syft) */}
                  {resultDetail.packages && (
                    <div className="space-y-1 max-h-60 overflow-y-auto">
                      <div className="text-xs text-slate-400 mb-1">By type: {JSON.stringify(resultDetail.summary?.by_type)}</div>
                      {resultDetail.packages.slice(0, 50).map((p, i) => (
                        <div key={i} className="flex items-center justify-between bg-slate-800/50 rounded px-3 py-1 text-xs">
                          <div className="flex items-center gap-2"><Package className="w-3 h-3 text-slate-500" /><span className="text-white">{p.name}</span><span className="text-slate-500">@{p.version}</span></div>
                          <div className="flex items-center gap-2"><span className="text-slate-400">{p.type}</span>{p.language && <span className="text-purple-400">{p.language}</span>}</div>
                        </div>
                      ))}
                      {resultDetail.packages.length > 50 && <div className="text-xs text-slate-500 text-center">...and {resultDetail.packages.length - 50} more</div>}
                    </div>
                  )}
                  {/* Checks (Checkov) */}
                  {resultDetail.checks && (
                    <div className="space-y-1 max-h-60 overflow-y-auto">
                      {resultDetail.checks.filter((c) => c.status === "failed").map((c, i) => (
                        <div key={i} className="flex items-center gap-2 bg-red-900/10 rounded px-3 py-1.5 text-xs">
                          <XCircle className="w-3 h-3 text-red-400 shrink-0" />
                          <span className="text-red-300 font-mono">{c.check_id}</span>
                          <span className="text-white truncate">{c.resource}</span>
                          <span className="text-slate-500">{c.file}</span>
                        </div>
                      ))}
                      {resultDetail.checks.filter((c) => c.status === "passed").length > 0 && (
                        <div className="text-xs text-emerald-400 mt-1">{resultDetail.checks.filter((c) => c.status === "passed").length} checks passed</div>
                      )}
                    </div>
                  )}
                  {resultDetail.error && <div className="text-xs text-red-400 bg-red-900/10 rounded p-2">{resultDetail.error}</div>}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="text-center text-slate-400 py-6">Loading scan history...</div>}
          {!loading && results.length === 0 && <div className="text-center text-slate-500 py-6">No scan results yet. Run a scanner above.</div>}
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// CI/CD PIPELINE GENERATOR TAB (Phase 2)
// ═══════════════════════════════════════════════════════════════
const CICDTab = ({ onRefresh }) => {
  const [config, setConfig] = useState({
    repo_name: "bigmannentertainment", branch: "main",
    enable_trivy: true, enable_grype: true, enable_checkov: true, enable_syft: true,
    fail_on_critical: true, fail_on_high: false, container_image: "", terraform_dir: "terraform/", notify_email: "",
  });
  const [generatedYaml, setGeneratedYaml] = useState(null);
  const [pipelines, setPipelines] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    (async () => { try { setPipelines(await fetcher(`${SCANNER_API}/pipeline/list`)); } catch (e) {} })();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const result = await fetcher(`${SCANNER_API}/pipeline/generate`, { method: "POST", body: JSON.stringify(config) });
      setGeneratedYaml(result.yaml_content);
      setPipelines(await fetcher(`${SCANNER_API}/pipeline/list`));
      onRefresh();
    } catch (e) { console.error(e); }
    setGenerating(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedYaml);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([generatedYaml], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "security-gates.yml";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Config Panel */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Pipeline Configuration</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Repository</label>
                <input data-testid="pipeline-repo" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={config.repo_name} onChange={(e) => setConfig({ ...config, repo_name: e.target.value })} />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Branch</label>
                <input data-testid="pipeline-branch" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={config.branch} onChange={(e) => setConfig({ ...config, branch: e.target.value })} />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-2">Security Scanners</label>
              <div className="grid grid-cols-2 gap-2">
                {[{ k: "enable_trivy", l: "Trivy (Vuln + IaC)" }, { k: "enable_grype", l: "Grype (Dependencies)" }, { k: "enable_checkov", l: "Checkov (IaC)" }, { k: "enable_syft", l: "Syft (SBOM)" }].map(({ k, l }) => (
                  <label key={k} className="flex items-center gap-2 bg-slate-900/50 rounded-lg px-3 py-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded bg-slate-800 border-slate-600 text-cyan-500" checked={config[k]} onChange={(e) => setConfig({ ...config, [k]: e.target.checked })} />
                    <span className="text-sm text-slate-300">{l}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-2">Fail Conditions</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 rounded bg-slate-800 border-slate-600 text-red-500" checked={config.fail_on_critical} onChange={(e) => setConfig({ ...config, fail_on_critical: e.target.checked })} />
                  <span className="text-sm text-red-300">Fail on Critical</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 rounded bg-slate-800 border-slate-600 text-orange-500" checked={config.fail_on_high} onChange={(e) => setConfig({ ...config, fail_on_high: e.target.checked })} />
                  <span className="text-sm text-orange-300">Fail on High</span>
                </label>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Container Image (optional)</label>
                <input className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" placeholder="e.g. myapp:latest" value={config.container_image} onChange={(e) => setConfig({ ...config, container_image: e.target.value })} />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Terraform Dir</label>
                <input className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={config.terraform_dir} onChange={(e) => setConfig({ ...config, terraform_dir: e.target.value })} />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-1">Notification Email</label>
              <input className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" placeholder="team@company.com" value={config.notify_email} onChange={(e) => setConfig({ ...config, notify_email: e.target.value })} />
            </div>

            <button data-testid="generate-pipeline-btn" onClick={handleGenerate} disabled={generating} className="w-full flex items-center justify-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50">
              <GitBranch className="w-4 h-4" /> {generating ? "Generating..." : "Generate GitHub Actions YAML"}
            </button>
          </div>
        </div>

        {/* YAML Preview */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white font-semibold">Generated Pipeline</h3>
            {generatedYaml && (
              <div className="flex items-center gap-2">
                <button data-testid="copy-yaml-btn" onClick={handleCopy} className="flex items-center gap-1 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded text-xs transition-colors">
                  <Copy className="w-3 h-3" /> {copied ? "Copied!" : "Copy"}
                </button>
                <button data-testid="download-yaml-btn" onClick={handleDownload} className="flex items-center gap-1 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded text-xs transition-colors">
                  <Download className="w-3 h-3" /> Download
                </button>
              </div>
            )}
          </div>
          {generatedYaml ? (
            <pre className="flex-1 bg-slate-950 rounded-lg p-4 text-xs text-green-400 font-mono overflow-auto max-h-[500px] whitespace-pre">{generatedYaml}</pre>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
              <div className="text-center">
                <Terminal className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                <div>Configure and generate your security pipeline</div>
                <div className="text-xs text-slate-600 mt-1">.github/workflows/security-gates.yml</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Pipeline History */}
      {pipelines.length > 0 && (
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3">Generated Pipelines</h3>
          <div className="space-y-2">
            {pipelines.map((p) => (
              <div key={p.id} className="flex items-center justify-between bg-slate-900/50 rounded-lg px-4 py-2.5">
                <div className="flex items-center gap-3">
                  <GitBranch className="w-4 h-4 text-cyan-400" />
                  <span className="text-sm text-white">{p.repo_name}</span>
                  <span className="text-xs text-slate-500">/{p.branch}</span>
                </div>
                <span className="text-xs text-slate-500">{new Date(p.created_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// POLICY ENGINE TAB (Phase 2)
// ═══════════════════════════════════════════════════════════════
const PolicyEngineTab = ({ onRefresh }) => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState(null);
  const [scans, setScans] = useState([]);
  const [evalScanId, setEvalScanId] = useState("");

  const fetchRules = useCallback(async () => {
    setLoading(true);
    try {
      const [r, s] = await Promise.all([fetcher(`${SCANNER_API}/policy-rules`), fetcher(`${SCANNER_API}/results?limit=20`)]);
      setRules(r);
      setScans(s);
      if (s.length > 0 && !evalScanId) setEvalScanId(s[0].id);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [evalScanId]);

  useEffect(() => { fetchRules(); }, [fetchRules]);

  const handleSeed = async () => {
    setSeeding(true);
    try { await fetcher(`${SCANNER_API}/policy-rules/seed`, { method: "POST" }); fetchRules(); } catch (e) { console.error(e); }
    setSeeding(false);
  };

  const handleToggle = async (rule) => {
    try {
      await fetcher(`${SCANNER_API}/policy-rules/${rule.id}`, { method: "PUT", body: JSON.stringify({ enabled: !rule.enabled }) });
      fetchRules();
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this policy rule?")) return;
    try { await fetcher(`${SCANNER_API}/policy-rules/${id}`, { method: "DELETE" }); fetchRules(); onRefresh(); } catch (e) { console.error(e); }
  };

  const handleEvaluate = async () => {
    if (!evalScanId) return;
    setEvaluating(true);
    try { setEvalResult(await fetcher(`${SCANNER_API}/policy-rules/evaluate/${evalScanId}`, { method: "POST" })); } catch (e) { console.error(e); }
    setEvaluating(false);
  };

  const conditionLabels = { severity_threshold: "Severity Threshold", cvss_threshold: "CVSS Score Threshold", package_blocklist: "Package Blocklist", iac_failures: "IaC Failure Count" };
  const actionColors = { block_deploy: "bg-red-500/20 text-red-300", warn: "bg-yellow-500/20 text-yellow-300", notify: "bg-blue-500/20 text-blue-300" };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-white font-semibold">Policy-as-Code Rules Engine</div>
          <div className="text-slate-400 text-xs mt-0.5">Define rules that block deployments based on scan results</div>
        </div>
        <div className="flex items-center gap-2">
          <button data-testid="seed-rules-btn" onClick={handleSeed} disabled={seeding} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors disabled:opacity-50">{seeding ? "Seeding..." : "Seed Default Rules"}</button>
          <button data-testid="create-rule-btn" onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
            <Plus className="w-4 h-4" /> Add Rule
          </button>
        </div>
      </div>

      {/* Rules List */}
      <div className="space-y-3">
        {rules.map((rule) => (
          <div key={rule.id} data-testid={`policy-rule-${rule.id}`} className={`bg-slate-800/60 border rounded-xl p-4 ${rule.enabled ? "border-slate-700/50" : "border-slate-700/30 opacity-60"}`}>
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <button onClick={() => handleToggle(rule)} className="mt-0.5" title={rule.enabled ? "Disable" : "Enable"}>
                  {rule.enabled ? <ToggleRight className="w-6 h-6 text-cyan-400" /> : <ToggleLeft className="w-6 h-6 text-slate-500" />}
                </button>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-white font-medium">{rule.name}</span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${actionColors[rule.action] || actionColors.warn}`}>{rule.action?.replace("_", " ").toUpperCase()}</span>
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">{rule.description}</div>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="px-2 py-0.5 bg-slate-700/50 rounded text-xs text-slate-300">{conditionLabels[rule.condition_type] || rule.condition_type}</span>
                    <span className="text-xs text-slate-500 font-mono">{JSON.stringify(rule.condition)}</span>
                  </div>
                </div>
              </div>
              <button onClick={() => handleDelete(rule.id)} className="text-slate-500 hover:text-red-400 transition-colors"><Trash2 className="w-4 h-4" /></button>
            </div>
          </div>
        ))}
        {loading && <div className="text-center text-slate-400 py-6">Loading rules...</div>}
        {!loading && rules.length === 0 && <div className="text-center text-slate-500 py-6">No policy rules. Click "Seed Default Rules" to get started.</div>}
      </div>

      {/* Policy Evaluation */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-3">Evaluate Against Scan</h3>
        <div className="flex items-center gap-3 mb-4">
          <select data-testid="eval-scan-select" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={evalScanId} onChange={(e) => setEvalScanId(e.target.value)}>
            <option value="">Select a scan result...</option>
            {scans.map((s) => (
              <option key={s.id} value={s.id}>{s.scanner} ({s.scan_type}) — {new Date(s.started_at).toLocaleString()} {s.summary?.total ? `[${s.summary.total} findings]` : ""}</option>
            ))}
          </select>
          <button data-testid="evaluate-policies-btn" onClick={handleEvaluate} disabled={evaluating || !evalScanId} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
            <Shield className="w-4 h-4" /> {evaluating ? "Evaluating..." : "Evaluate"}
          </button>
        </div>

        {evalResult && (
          <div className={`rounded-xl p-4 border ${evalResult.deploy_allowed ? "bg-emerald-900/20 border-emerald-500/40" : "bg-red-900/20 border-red-500/40"}`}>
            <div className="flex items-center gap-3 mb-3">
              {evalResult.deploy_allowed ? <CheckCircle className="w-6 h-6 text-emerald-400" /> : <XCircle className="w-6 h-6 text-red-400" />}
              <div>
                <div className={`text-lg font-bold ${evalResult.deploy_allowed ? "text-emerald-400" : "text-red-400"}`}>
                  {evalResult.deploy_allowed ? "DEPLOY ALLOWED" : "DEPLOY BLOCKED"}
                </div>
                <div className="text-xs text-slate-400">{evalResult.rules_evaluated} rules evaluated</div>
              </div>
            </div>
            {evalResult.rules_triggered.length > 0 && (
              <div className="space-y-1 mb-2">
                <div className="text-xs text-red-400 font-medium">Triggered Rules:</div>
                {evalResult.rules_triggered.map((r, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs bg-red-900/20 rounded px-3 py-1.5">
                    <XCircle className="w-3 h-3 text-red-400" />
                    <span className="text-white">{r.rule_name}</span>
                    <span className={`px-1.5 py-0.5 rounded ${actionColors[r.action]}`}>{r.action?.replace("_", " ")}</span>
                  </div>
                ))}
              </div>
            )}
            {evalResult.rules_passed.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs text-emerald-400 font-medium">Passed Rules:</div>
                {evalResult.rules_passed.map((r, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs bg-emerald-900/10 rounded px-3 py-1.5">
                    <CheckCircle className="w-3 h-3 text-emerald-400" />
                    <span className="text-white">{r.rule_name}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {showCreate && <CreateRuleModal onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); fetchRules(); onRefresh(); }} />}
    </div>
  );
};

const CreateRuleModal = ({ onClose, onCreated }) => {
  const [form, setForm] = useState({ name: "", description: "", condition_type: "severity_threshold", action: "block_deploy", conditionJson: '{"min_severity": "critical", "max_count": 0}' });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      let condition = {};
      try { condition = JSON.parse(form.conditionJson); } catch (e) {}
      await fetcher(`${SCANNER_API}/policy-rules`, {
        method: "POST",
        body: JSON.stringify({ name: form.name, description: form.description, condition_type: form.condition_type, condition, action: form.action }),
      });
      onCreated();
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  const templates = {
    severity_threshold: '{"min_severity": "critical", "max_count": 0}',
    cvss_threshold: '{"min_score": 9.0}',
    package_blocklist: '{"packages": ["jsonpath", "cryptography"]}',
    iac_failures: '{"max_failures": 3}',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-white text-lg font-semibold mb-4">Create Policy Rule</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input data-testid="rule-create-name" required placeholder="Rule Name *" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input placeholder="Description" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Condition Type</label>
              <select className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.condition_type} onChange={(e) => setForm({ ...form, condition_type: e.target.value, conditionJson: templates[e.target.value] || "{}" })}>
                <option value="severity_threshold">Severity Threshold</option>
                <option value="cvss_threshold">CVSS Score Threshold</option>
                <option value="package_blocklist">Package Blocklist</option>
                <option value="iac_failures">IaC Failure Count</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Action</label>
              <select className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.action} onChange={(e) => setForm({ ...form, action: e.target.value })}>
                <option value="block_deploy">Block Deploy</option>
                <option value="warn">Warn</option>
                <option value="notify">Notify</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Condition (JSON)</label>
            <textarea className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm font-mono h-20" value={form.conditionJson} onChange={(e) => setForm({ ...form, conditionJson: e.target.value })} />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white text-sm">Cancel</button>
            <button data-testid="rule-create-submit" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">{saving ? "Saving..." : "Create Rule"}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// REMEDIATION TAB (Phase 3)
// ═══════════════════════════════════════════════════════════════

const REMEDIATION_STATUS_COLORS = {
  open: "bg-slate-500/20 text-slate-300",
  issue_created: "bg-yellow-500/20 text-yellow-300",
  pr_created: "bg-blue-500/20 text-blue-300",
  in_review: "bg-purple-500/20 text-purple-300",
  merged: "bg-emerald-500/20 text-emerald-300",
  deployed: "bg-cyan-500/20 text-cyan-300",
  verified: "bg-green-500/20 text-green-300",
  closed: "bg-slate-600/20 text-slate-400",
  wont_fix: "bg-slate-600/20 text-slate-400",
};

const RemediationTab = ({ onRefresh }) => {
  const [config, setConfig] = useState(null);
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [cves, setCves] = useState([]);
  const [awsFindings, setAwsFindings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState({});
  const [syncing, setSyncing] = useState(false);
  const [bulkCreating, setBulkCreating] = useState(false);
  const [filterStatus, setFilterStatus] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("");
  const [view, setView] = useState("items");

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [configRes, itemsRes, cvesRes] = await Promise.all([
        fetcher(`${REMEDIATION_API}/config`),
        fetcher(`${REMEDIATION_API}/items?${new URLSearchParams({ ...(filterStatus && { status: filterStatus }), ...(filterSeverity && { severity: filterSeverity }), limit: "50" })}`),
        fetcher(`${API}/entries?status=detected&limit=50`),
      ]);
      setConfig(configRes);
      setItems(itemsRes.items || []);
      setTotalItems(itemsRes.total || 0);
      setCves(cvesRes.items || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [filterStatus, filterSeverity]);

  const fetchAws = useCallback(async () => {
    try {
      const res = await fetcher(`${REMEDIATION_API}/aws/findings`);
      setAwsFindings(res);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => { if (view === "aws") fetchAws(); }, [view, fetchAws]);

  const handleCreateIssue = async (cveId) => {
    setCreating((p) => ({ ...p, [`issue_${cveId}`]: true }));
    try {
      await fetcher(`${REMEDIATION_API}/create-issue/${cveId}`, { method: "POST" });
      fetchData();
      onRefresh();
    } catch (e) { console.error(e); }
    setCreating((p) => ({ ...p, [`issue_${cveId}`]: false }));
  };

  const handleCreatePR = async (cveId) => {
    setCreating((p) => ({ ...p, [`pr_${cveId}`]: true }));
    try {
      await fetcher(`${REMEDIATION_API}/create-pr/${cveId}`, { method: "POST" });
      fetchData();
      onRefresh();
    } catch (e) { console.error(e); }
    setCreating((p) => ({ ...p, [`pr_${cveId}`]: false }));
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await fetcher(`${REMEDIATION_API}/sync-github`, { method: "POST" });
      fetchData();
    } catch (e) { console.error(e); }
    setSyncing(false);
  };

  const handleBulkCreate = async (severity) => {
    setBulkCreating(true);
    try {
      await fetcher(`${REMEDIATION_API}/bulk-create-issues`, { method: "POST", body: JSON.stringify({ severity, limit: 10 }) });
      fetchData();
      onRefresh();
    } catch (e) { console.error(e); }
    setBulkCreating(false);
  };

  const handleStatusChange = async (itemId, newStatus) => {
    try {
      await fetcher(`${REMEDIATION_API}/items/${itemId}/status`, { method: "PUT", body: JSON.stringify({ status: newStatus }) });
      fetchData();
    } catch (e) { console.error(e); }
  };

  const stats = config?.stats || {};

  return (
    <div className="space-y-6">
      {/* GitHub Connection Status */}
      <div data-testid="github-connection-card" className={`border rounded-xl p-5 ${config?.repo_connected ? "bg-emerald-900/20 border-emerald-500/30" : "bg-red-900/20 border-red-500/30"}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Github className={`w-6 h-6 ${config?.repo_connected ? "text-emerald-400" : "text-red-400"}`} />
            <div>
              <h3 className="text-white font-semibold">GitHub Integration</h3>
              {config?.repo_connected ? (
                <div>
                  <p className="text-sm text-emerald-400">Connected to <a href={config.repo_url} target="_blank" rel="noreferrer" className="underline hover:text-emerald-300">{config.repo_full_name}</a> ({config.default_branch})</p>
                  {!config.write_access && <p className="text-xs text-yellow-400 mt-1">Token has read-only access. To create issues/PRs, update your token permissions at github.com/settings/tokens</p>}
                </div>
              ) : (
                <p className="text-sm text-red-400">Not connected. Configure GITHUB_TOKEN and GITHUB_REPO in backend/.env</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button data-testid="sync-github-btn" onClick={handleSync} disabled={syncing || !config?.repo_connected} className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs transition-colors disabled:opacity-50">
              <RefreshCw className={`w-3 h-3 ${syncing ? "animate-spin" : ""}`} /> {syncing ? "Syncing..." : "Sync GitHub"}
            </button>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard icon={Wrench} label="Total Items" value={stats.total || 0} color="text-cyan-400" />
        <StatCard icon={AlertTriangle} label="Open" value={stats.open || 0} color="text-yellow-400" />
        <StatCard icon={Github} label="Issues Created" value={stats.issues_created || 0} color="text-blue-400" />
        <StatCard icon={GitBranch} label="PRs Created" value={stats.prs_created || 0} color="text-purple-400" />
        <StatCard icon={CheckCircle2} label="Merged" value={stats.merged || 0} color="text-emerald-400" />
        <StatCard icon={CheckCircle} label="Closed" value={stats.closed || 0} color="text-green-400" />
      </div>

      {/* Sub-nav */}
      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2">
        {[
          { id: "items", label: "Remediation Items", icon: Wrench },
          { id: "create", label: "Create from CVEs", icon: Plus },
          { id: "bulk", label: "Bulk Operations", icon: Layers },
          { id: "aws", label: "AWS Findings", icon: CloudLightning },
        ].map((v) => (
          <button key={v.id} data-testid={`remediation-view-${v.id}`} onClick={() => setView(v.id)} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${view === v.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <v.icon className="w-4 h-4" /> {v.label}
          </button>
        ))}
      </div>

      {/* Remediation Items View */}
      {view === "items" && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <select data-testid="remediation-status-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="">All Statuses</option>
              {["open", "issue_created", "pr_created", "in_review", "merged", "deployed", "verified", "closed", "wont_fix"].map((s) => <option key={s} value={s}>{s.replace(/_/g, " ").toUpperCase()}</option>)}
            </select>
            <select data-testid="remediation-severity-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
              <option value="">All Severities</option>
              {["critical", "high", "medium", "low"].map((s) => <option key={s} value={s}>{s.toUpperCase()}</option>)}
            </select>
            <span className="text-sm text-slate-400 ml-auto">{totalItems} item{totalItems !== 1 ? "s" : ""}</span>
          </div>

          {loading ? (
            <div className="text-center py-12 text-slate-400"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" /> Loading...</div>
          ) : items.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <Wrench className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400 text-sm">No remediation items yet. Create issues from the CVE database.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {items.map((item) => (
                <div key={item.id} data-testid={`remediation-item-${item.id}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <SeverityBadge severity={item.severity} />
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${REMEDIATION_STATUS_COLORS[item.status] || REMEDIATION_STATUS_COLORS.open}`}>{item.status.replace(/_/g, " ").toUpperCase()}</span>
                        <span className="text-xs text-slate-500 font-mono">{item.cve_id}</span>
                      </div>
                      <h4 className="text-white text-sm font-medium truncate">{item.title || item.cve_id}</h4>
                      {item.affected_package && <p className="text-xs text-slate-400 mt-1">Package: <span className="text-slate-300 font-mono">{item.affected_package}</span> {item.affected_version && `@ ${item.affected_version}`} {item.fixed_version && <span className="text-emerald-400">→ {item.fixed_version}</span>}</p>}
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {item.github_issue_url && (
                        <a href={item.github_issue_url} target="_blank" rel="noreferrer" data-testid={`issue-link-${item.id}`} className="flex items-center gap-1 px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded text-xs text-white transition-colors">
                          <Github className="w-3 h-3" /> #{item.github_issue_number} <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {item.github_pr_url && (
                        <a href={item.github_pr_url} target="_blank" rel="noreferrer" data-testid={`pr-link-${item.id}`} className="flex items-center gap-1 px-2 py-1 bg-purple-600/30 hover:bg-purple-600/50 rounded text-xs text-purple-300 transition-colors">
                          <GitBranch className="w-3 h-3" /> PR #{item.github_pr_number} <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      <select className="bg-slate-700 border border-slate-600 rounded px-2 py-1 text-xs text-white" value={item.status} onChange={(e) => handleStatusChange(item.id, e.target.value)}>
                        {["open", "issue_created", "pr_created", "in_review", "merged", "deployed", "verified", "closed", "wont_fix"].map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create from CVEs View */}
      {view === "create" && (
        <div className="space-y-4">
          <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
            <h3 className="text-white font-semibold mb-1">Create GitHub Issues & PRs from Detected CVEs</h3>
            <p className="text-sm text-slate-400">Select a CVE below to create a GitHub issue or pull request for automated remediation.</p>
          </div>

          {cves.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <CheckCircle className="w-10 h-10 text-emerald-600 mx-auto mb-3" />
              <p className="text-slate-400 text-sm">No open CVEs detected. All vulnerabilities have been triaged.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {cves.map((cve) => (
                <div key={cve.id} data-testid={`cve-remediate-${cve.id}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 flex items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <SeverityBadge severity={cve.severity} />
                      <span className="text-xs text-slate-500 font-mono">{cve.cve_id}</span>
                    </div>
                    <h4 className="text-white text-sm font-medium truncate">{cve.title}</h4>
                    {cve.affected_package && <p className="text-xs text-slate-400 mt-1"><span className="font-mono text-slate-300">{cve.affected_package}</span> {cve.affected_version && `@ ${cve.affected_version}`} {cve.fixed_version && <span className="text-emerald-400">→ fix: {cve.fixed_version}</span>}</p>}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button data-testid={`create-issue-${cve.id}`} onClick={() => handleCreateIssue(cve.id)} disabled={creating[`issue_${cve.id}`] || !config?.repo_connected} className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-600/20 hover:bg-yellow-600/40 text-yellow-300 border border-yellow-500/30 rounded-lg text-xs transition-colors disabled:opacity-50">
                      {creating[`issue_${cve.id}`] ? <Loader2 className="w-3 h-3 animate-spin" /> : <Github className="w-3 h-3" />} Create Issue
                    </button>
                    <button data-testid={`create-pr-${cve.id}`} onClick={() => handleCreatePR(cve.id)} disabled={creating[`pr_${cve.id}`] || !config?.repo_connected || !cve.fixed_version} className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 border border-purple-500/30 rounded-lg text-xs transition-colors disabled:opacity-50" title={!cve.fixed_version ? "No fixed version available" : ""}>
                      {creating[`pr_${cve.id}`] ? <Loader2 className="w-3 h-3 animate-spin" /> : <GitBranch className="w-3 h-3" />} Create PR
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Bulk Operations View */}
      {view === "bulk" && (
        <div className="space-y-4">
          <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
            <h3 className="text-white font-semibold mb-1">Bulk Issue Creation</h3>
            <p className="text-sm text-slate-400">Automatically create GitHub issues for all detected CVEs matching a severity level.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {["critical", "high", "medium", "low"].map((sev) => {
              const c = SEVERITY_COLORS[sev];
              const count = stats.by_severity?.[sev] || 0;
              return (
                <div key={sev} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className={`${c.text} font-semibold text-sm uppercase`}>{sev}</h4>
                    <span className={`${c.text} text-2xl font-bold`}>{count}</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-4">{count} active remediation item{count !== 1 ? "s" : ""}</p>
                  <button data-testid={`bulk-create-${sev}`} onClick={() => handleBulkCreate(sev)} disabled={bulkCreating || !config?.repo_connected} className={`w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-50 ${c.bg} border ${c.border} ${c.text} hover:opacity-80`}>
                    {bulkCreating ? <Loader2 className="w-3 h-3 animate-spin" /> : <ArrowUpRight className="w-3 h-3" />}
                    Create Issues for {sev}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* AWS Findings View */}
      {view === "aws" && (
        <AwsFindingsView awsFindings={awsFindings} fetchAws={fetchAws} fetchData={fetchData} />
      )}
    </div>
  );
};

const AwsFindingsView = ({ awsFindings, fetchAws, fetchData }) => {
  const [securityHub, setSecurityHub] = useState(null);
  const [awsTab, setAwsTab] = useState("inspector");
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetcher(`${REMEDIATION_API}/aws/security-hub`).then(setSecurityHub).catch(console.error);
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try { await fetcher(`${REMEDIATION_API}/aws/sync`, { method: "POST" }); fetchAws(); fetchData(); } catch (e) { console.error(e); }
    setSyncing(false);
  };

  return (
    <div className="space-y-4">
      {/* AWS Connection Status */}
      <div className={`border rounded-xl p-4 ${awsFindings?.source === "aws_inspector" ? "bg-orange-900/15 border-orange-500/30" : "bg-slate-800/40 border-slate-700/50"}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CloudLightning className={`w-5 h-5 ${awsFindings?.source === "aws_inspector" ? "text-orange-400" : "text-slate-500"}`} />
            <div>
              <h3 className="text-white font-semibold text-sm">AWS Security Integration</h3>
              <p className="text-xs text-slate-400">
                Inspector: <span className={awsFindings?.source === "aws_inspector" ? "text-emerald-400" : "text-red-400"}>{awsFindings?.source === "aws_inspector" ? "Connected" : "Unavailable"}</span>
                {" | "}Security Hub: <span className={securityHub?.source === "security_hub" ? "text-emerald-400" : "text-red-400"}>{securityHub?.source === "security_hub" ? "Connected" : "Unavailable"}</span>
              </p>
            </div>
          </div>
          <button data-testid="sync-aws-btn" onClick={handleSync} disabled={syncing} className="flex items-center gap-2 px-3 py-2 bg-orange-600/20 hover:bg-orange-600/40 text-orange-300 border border-orange-500/30 rounded-lg text-xs transition-colors disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${syncing ? "animate-spin" : ""}`} /> {syncing ? "Syncing..." : "Sync AWS"}
          </button>
        </div>
      </div>

      {/* Sub tabs */}
      <div className="flex items-center gap-2">
        {[
          { id: "inspector", label: `Inspector (${awsFindings?.count || 0})` },
          { id: "security-hub", label: `Security Hub (${securityHub?.count || 0})` },
        ].map((t) => (
          <button key={t.id} data-testid={`aws-tab-${t.id}`} onClick={() => setAwsTab(t.id)} className={`px-3 py-1.5 rounded-lg text-xs transition-all ${awsTab === t.id ? "bg-orange-500/15 text-orange-400 font-medium border border-orange-500/30" : "text-slate-400 hover:text-white bg-slate-800/40 border border-slate-700/50"}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Inspector Findings */}
      {awsTab === "inspector" && (
        <>
          {!awsFindings ? (
            <div className="text-center py-12 text-slate-400"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" /> Loading...</div>
          ) : awsFindings.findings?.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <CloudLightning className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-white text-sm font-medium mb-1">No Active Inspector Findings</p>
              <p className="text-slate-400 text-xs">{awsFindings.source === "aws_inspector" ? "Your AWS Inspector has no active vulnerability findings." : "AWS Inspector may not be enabled in your account."}</p>
            </div>
          ) : (
            <div className="space-y-2">
              {awsFindings.findings.map((f, i) => (
                <div key={f.id || i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <SeverityBadge severity={f.severity || "medium"} />
                        <span className="text-xs text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded">Inspector</span>
                        {f.type && <span className="text-xs text-slate-500">{f.type}</span>}
                      </div>
                      <h4 className="text-white text-sm font-medium">{f.title}</h4>
                      {f.description && <p className="text-xs text-slate-400 mt-1 line-clamp-2">{f.description}</p>}
                      {f.resources?.length > 0 && <p className="text-xs text-slate-500 mt-1">Resources: {f.resources.join(", ")}</p>}
                    </div>
                    {f.first_observed && <span className="text-xs text-slate-500 whitespace-nowrap">{new Date(f.first_observed).toLocaleDateString()}</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Security Hub Findings */}
      {awsTab === "security-hub" && (
        <>
          {!securityHub ? (
            <div className="text-center py-12 text-slate-400"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" /> Loading...</div>
          ) : securityHub.findings?.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <Shield className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-white text-sm font-medium mb-1">No Security Hub Findings</p>
              <p className="text-slate-400 text-xs">{securityHub.source === "security_hub" ? "No new findings in Security Hub." : securityHub.note || "Security Hub may not be enabled."}</p>
            </div>
          ) : (
            <div className="space-y-2">
              {securityHub.findings.map((f, i) => (
                <div key={f.id || i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <SeverityBadge severity={f.severity || "medium"} />
                        <span className="text-xs text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">{f.product || "Security Hub"}</span>
                        {f.compliance_status && <span className={`text-xs px-2 py-0.5 rounded ${f.compliance_status === "PASSED" ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>{f.compliance_status}</span>}
                      </div>
                      <h4 className="text-white text-sm font-medium">{f.title}</h4>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// GOVERNANCE TAB (Phase 4)
// ═══════════════════════════════════════════════════════════════
const CHART_COLORS = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"];
const PIE_COLORS = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"];
const STATUS_CHART_COLORS = { detected: "#ef4444", triaged: "#eab308", in_progress: "#3b82f6", fixed: "#10b981", verified: "#22c55e", dismissed: "#64748b", wont_fix: "#475569" };

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 shadow-xl">
      <p className="text-slate-300 text-xs mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-xs" style={{ color: p.color }}>{p.name}: <span className="font-semibold">{p.value}</span></p>
      ))}
    </div>
  );
};

const RiskGauge = ({ score }) => {
  const color = score >= 75 ? "#ef4444" : score >= 50 ? "#f97316" : score >= 25 ? "#eab308" : "#10b981";
  const label = score >= 75 ? "Critical" : score >= 50 ? "High" : score >= 25 ? "Medium" : "Low";
  return (
    <div data-testid="risk-gauge" className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="10" />
          <circle cx="50" cy="50" r="42" fill="none" stroke={color} strokeWidth="10" strokeDasharray={`${score * 2.64} 264`} strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">{score}</span>
          <span className="text-xs" style={{ color }}>{label}</span>
        </div>
      </div>
      <p className="text-xs text-slate-400 mt-2">Risk Score</p>
    </div>
  );
};

const GovernanceTab = ({ onRefresh }) => {
  const [metrics, setMetrics] = useState(null);
  const [trends, setTrends] = useState(null);
  const [sla, setSla] = useState(null);
  const [ownership, setOwnership] = useState(null);
  const [mttr, setMttr] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("overview");
  const [ownerInfo, setOwnerInfo] = useState(null);
  const [unassigned, setUnassigned] = useState(null);
  const [govAssignTarget, setGovAssignTarget] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [m, t, s, o, mt, ow, ua] = await Promise.all([
        fetcher(`${GOVERNANCE_API}/metrics`),
        fetcher(`${GOVERNANCE_API}/trends?days=30`),
        fetcher(`${GOVERNANCE_API}/sla`),
        fetcher(`${GOVERNANCE_API}/ownership`),
        fetcher(`${GOVERNANCE_API}/mttr`),
        fetcher(`${API}/owners`),
        fetcher(`${API}/unassigned?limit=20`),
      ]);
      setMetrics(m);
      setTrends(t);
      setSla(s);
      setOwnership(o);
      setMttr(mt);
      setOwnerInfo(ow);
      setUnassigned(ua);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  if (loading || !metrics) return <div className="text-center py-16 text-slate-400"><Loader2 className="w-8 h-8 animate-spin mx-auto mb-3" />Loading governance data...</div>;

  const sevPieData = Object.entries(metrics.severity_distribution || {}).filter(([, v]) => v > 0).map(([k, v], i) => ({ name: k.charAt(0).toUpperCase() + k.slice(1), value: v, fill: CHART_COLORS[i] }));
  const statusPieData = (ownership?.by_status || []).map((s) => ({ name: s.status.replace("_", " "), value: s.count, fill: STATUS_CHART_COLORS[s.status] || "#64748b" }));
  const sourcePieData = (ownership?.by_source || []).map((s, i) => ({ name: s.source, value: s.count, fill: CHART_COLORS[i % CHART_COLORS.length] }));
  const servicesBarData = (metrics.services_affected || []).map((s) => ({ name: s.service.length > 18 ? s.service.slice(0, 18) + "..." : s.service, count: s.count }));
  const mttrBarData = Object.entries(mttr?.mttr || {}).map(([sev, d]) => ({ severity: sev.charAt(0).toUpperCase() + sev.slice(1), hours: d.avg_hours, days: d.avg_days, samples: d.sample_size }));
  const trendData = (trends?.trends || []).filter((_, i, arr) => arr.length <= 15 || i % Math.ceil(arr.length / 15) === 0 || i === arr.length - 1);

  return (
    <div className="space-y-6">
      {/* Sub-nav */}
      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2">
        {[
          { id: "overview", label: "Overview", icon: Gauge },
          { id: "trends", label: "Trends", icon: TrendingUp },
          { id: "sla", label: "SLA Compliance", icon: Target },
          { id: "ownership", label: "Ownership", icon: Users },
        ].map((v) => (
          <button key={v.id} data-testid={`gov-view-${v.id}`} onClick={() => setView(v.id)} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${view === v.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <v.icon className="w-4 h-4" /> {v.label}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW ────────────────────────────── */}
      {view === "overview" && (
        <div className="space-y-6">
          {/* Top metrics row */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <StatCard icon={AlertTriangle} label="Total CVEs" value={metrics.total_cves} color="text-white" />
            <StatCard icon={Shield} label="Open" value={metrics.open_cves} color="text-red-400" />
            <StatCard icon={CheckCircle} label="Fixed" value={metrics.fixed_cves} color="text-emerald-400" />
            <StatCard icon={CheckCircle2} label="Verified" value={metrics.verified_cves} color="text-green-400" />
            <StatCard icon={TrendingUp} label="New (30d)" value={metrics.new_last_30_days} color="text-cyan-400" />
            <StatCard icon={Target} label="Fix Rate (30d)" value={`${metrics.fix_rate_30d}%`} color="text-blue-400" />
          </div>

          {/* Risk Gauge + Severity Pie */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 flex flex-col items-center justify-center">
              <h3 className="text-white font-semibold mb-4 text-sm">Risk Assessment</h3>
              <RiskGauge score={metrics.risk_score} />
              <p className="text-xs text-slate-500 mt-3 text-center">Weighted by open critical/high/medium CVEs</p>
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Severity</h3>
              {sevPieData.length === 0 ? (
                <div className="flex items-center justify-center h-40 text-slate-500 text-sm">No open CVEs</div>
              ) : (
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={sevPieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                      {sevPieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">CVEs by Status</h3>
              {statusPieData.length === 0 ? (
                <div className="flex items-center justify-center h-40 text-slate-500 text-sm">No data</div>
              ) : (
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={statusPieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                      {statusPieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Affected Services Bar */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Service</h3>
              {servicesBarData.length === 0 ? (
                <div className="flex items-center justify-center h-48 text-slate-500 text-sm">No services affected</div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={servicesBarData} layout="vertical" margin={{ left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <YAxis type="category" dataKey="name" width={120} tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]} barSize={18} name="Open CVEs" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">CVEs by Source</h3>
              {sourcePieData.length === 0 ? (
                <div className="flex items-center justify-center h-48 text-slate-500 text-sm">No data</div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={sourcePieData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={30} name="CVEs" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* MTTR */}
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">Mean Time to Remediate (MTTR) by Severity</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={mttrBarData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="severity" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} label={{ value: "Hours", angle: -90, position: "insideLeft", fill: "#64748b", fontSize: 11 }} />
                <Tooltip content={({ active, payload, label }) => {
                  if (!active || !payload?.length) return null;
                  const d = payload[0]?.payload;
                  return (
                    <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 shadow-xl">
                      <p className="text-slate-300 text-xs font-medium mb-1">{label}</p>
                      <p className="text-xs text-cyan-400">Avg: {d?.hours || 0}h ({d?.days || 0}d)</p>
                      <p className="text-xs text-slate-400">Samples: {d?.samples || 0}</p>
                    </div>
                  );
                }} />
                <Bar dataKey="hours" name="Avg Hours" radius={[4, 4, 0, 0]} barSize={40}>
                  {mttrBarData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* ── TRENDS ─────────────────────────────── */}
      {view === "trends" && (
        <div className="space-y-6">
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">CVE Detection & Resolution Trends (30 Days)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="gradDetected" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradFixed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Area type="monotone" dataKey="detected" name="Detected" stroke="#ef4444" fill="url(#gradDetected)" strokeWidth={2} />
                <Area type="monotone" dataKey="fixed" name="Fixed" stroke="#10b981" fill="url(#gradFixed)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Summary cards for trends */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard icon={AlertTriangle} label="New (7d)" value={metrics.new_last_7_days} color="text-red-400" />
            <StatCard icon={AlertTriangle} label="New (30d)" value={metrics.new_last_30_days} color="text-orange-400" />
            <StatCard icon={CheckCircle} label="Fixed (30d)" value={metrics.fixed_last_30_days} color="text-emerald-400" />
            <StatCard icon={Target} label="Fix Rate" value={`${metrics.fix_rate_30d}%`} color="text-cyan-400" />
          </div>
        </div>
      )}

      {/* ── SLA COMPLIANCE ─────────────────────── */}
      {view === "sla" && (
        <div className="space-y-6">
          {/* Overall compliance */}
          <div className={`border rounded-xl p-5 ${sla?.overall_compliance >= 90 ? "bg-emerald-900/20 border-emerald-500/30" : sla?.overall_compliance >= 70 ? "bg-yellow-900/20 border-yellow-500/30" : "bg-red-900/20 border-red-500/30"}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-white font-semibold">Overall SLA Compliance</h3>
                <p className="text-sm text-slate-400">Percentage of open CVEs within SLA targets</p>
              </div>
              <div data-testid="sla-overall" className={`text-4xl font-bold ${sla?.overall_compliance >= 90 ? "text-emerald-400" : sla?.overall_compliance >= 70 ? "text-yellow-400" : "text-red-400"}`}>
                {sla?.overall_compliance || 0}%
              </div>
            </div>
          </div>

          {/* SLA per severity */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {(sla?.sla_data || []).map((d) => {
              const c = SEVERITY_COLORS[d.severity] || SEVERITY_COLORS.info;
              const pct = d.compliance_pct;
              return (
                <div key={d.severity} data-testid={`sla-${d.severity}`} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className={`${c.text} font-semibold text-sm uppercase`}>{d.severity}</h4>
                    <span className={`text-xl font-bold ${pct >= 90 ? "text-emerald-400" : pct >= 70 ? "text-yellow-400" : "text-red-400"}`}>{pct}%</span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2 mb-3">
                    <div className={`h-2 rounded-full transition-all ${pct >= 90 ? "bg-emerald-500" : pct >= 70 ? "bg-yellow-500" : "bg-red-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div><span className="text-slate-400">SLA:</span> <span className="text-white">{d.sla_hours}h</span></div>
                    <div><span className="text-slate-400">Open:</span> <span className="text-white">{d.open}</span></div>
                    <div><span className="text-slate-400">Overdue:</span> <span className={d.overdue > 0 ? "text-red-400" : "text-emerald-400"}>{d.overdue}</span></div>
                    <div><span className="text-slate-400">Fixed:</span> <span className="text-emerald-400">{d.fixed_total}</span></div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* SLA Bar Chart */}
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">SLA Compliance by Severity</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={sla?.sla_data || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="severity" tick={{ fill: "#94a3b8", fontSize: 12 }} tickFormatter={(v) => v.charAt(0).toUpperCase() + v.slice(1)} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} domain={[0, "auto"]} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Bar dataKey="within_sla" name="Within SLA" fill="#10b981" radius={[4, 4, 0, 0]} stackId="a" />
                <Bar dataKey="overdue" name="Overdue" fill="#ef4444" radius={[4, 4, 0, 0]} stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* ── OWNERSHIP ──────────────────────────── */}
      {view === "ownership" && (
        <div className="space-y-6">
          {/* Unassigned Alert */}
          {(ownerInfo?.unassigned_open_cves || 0) > 0 && (
            <div data-testid="unassigned-alert" className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400" />
                <div>
                  <span className="text-amber-300 font-semibold text-sm">{ownerInfo.unassigned_open_cves} unassigned open CVE{ownerInfo.unassigned_open_cves !== 1 ? "s" : ""}</span>
                  <p className="text-amber-400/70 text-xs mt-0.5">These vulnerabilities need an owner for accountability and SLA tracking</p>
                </div>
              </div>
            </div>
          )}

          {/* Unassigned CVEs List */}
          {(unassigned?.items || []).length > 0 && (
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-3 text-sm flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" /> Unassigned CVEs
                <span className="text-xs text-slate-500 font-normal ml-1">({unassigned.total} total)</span>
              </h3>
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {(unassigned.items || []).map((c) => (
                  <div key={c.id} data-testid={`unassigned-cve-${c.id}`} className="flex items-center justify-between bg-slate-900/50 rounded-lg px-3 py-2">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <span className="text-cyan-400 font-mono text-xs">{c.cve_id}</span>
                      <SeverityBadge severity={c.severity} />
                      <span className="text-xs text-slate-300 truncate">{c.title}</span>
                    </div>
                    <button data-testid={`gov-assign-btn-${c.id}`} onClick={() => setGovAssignTarget(c)} className="ml-2 px-2.5 py-1 rounded text-xs bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/40 transition-colors border border-cyan-500/30 shrink-0">
                      <Users className="w-3 h-3 inline mr-1" />Assign
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            {/* By Team */}
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Team</h3>
              {(ownership?.by_team || []).length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-sm">No team assignments yet</div>
              ) : (
                <div className="space-y-2">
                  {(ownership?.by_team || []).map((t) => {
                    const maxCount = Math.max(...(ownership?.by_team || []).map((x) => x.count), 1);
                    return (
                      <div key={t.team} className="flex items-center gap-3">
                        <span className="text-sm text-slate-300 w-32 truncate">{t.team}</span>
                        <div className="flex-1 bg-slate-700/50 rounded-full h-3">
                          <div className="h-3 rounded-full bg-cyan-500/70" style={{ width: `${(t.count / maxCount) * 100}%` }} />
                        </div>
                        <span className="text-sm text-white font-medium w-8 text-right">{t.count}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* By Person */}
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Assignee</h3>
              {(ownership?.by_person || []).length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-sm">No individual assignments yet</div>
              ) : (
                <div className="space-y-2">
                  {(ownership?.by_person || []).map((p) => {
                    const maxCount = Math.max(...(ownership?.by_person || []).map((x) => x.count), 1);
                    return (
                      <div key={p.person} className="flex items-center gap-3">
                        <span className="text-sm text-slate-300 w-32 truncate">{p.person}</span>
                        <div className="flex-1 bg-slate-700/50 rounded-full h-3">
                          <div className="h-3 rounded-full bg-purple-500/70" style={{ width: `${(p.count / maxCount) * 100}%` }} />
                        </div>
                        <span className="text-sm text-white font-medium w-8 text-right">{p.count}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Available Owners & Teams */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-3 text-sm">Registered Owners</h3>
              {(ownerInfo?.people || []).length === 0 ? (
                <p className="text-slate-500 text-sm">No owners registered yet. Assign an owner to a CVE to populate this list.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {(ownerInfo?.people || []).map((p) => (
                    <span key={p} className="px-3 py-1 bg-purple-500/15 text-purple-300 rounded-lg text-xs border border-purple-500/20">{p}</span>
                  ))}
                </div>
              )}
            </div>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-3 text-sm">Registered Teams</h3>
              {(ownerInfo?.teams || []).length === 0 ? (
                <p className="text-slate-500 text-sm">No teams registered yet. Assign a team to a CVE to populate this list.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {(ownerInfo?.teams || []).map((t) => (
                    <span key={t} className="px-3 py-1 bg-cyan-500/15 text-cyan-300 rounded-lg text-xs border border-cyan-500/20">{t}</span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* By Source + By Status */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">CVE Sources</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={sourcePieData} cx="50%" cy="50%" innerRadius={35} outerRadius={65} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                    {sourcePieData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Status Distribution</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={statusPieData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" name="Count" radius={[4, 4, 0, 0]} barSize={30}>
                    {statusPieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Assign Owner Modal from Governance */}
          {govAssignTarget && <AssignOwnerModal cve={govAssignTarget} onClose={() => setGovAssignTarget(null)} onAssigned={() => { setGovAssignTarget(null); fetchAll(); onRefresh(); }} />}
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════
// MAIN DASHBOARD
// ═══════════════════════════════════════════════════════════════
const TABS = [
  { id: "overview", label: "Overview", icon: Shield },
  { id: "cves", label: "CVE Database", icon: AlertTriangle },
  { id: "scanners", label: "Scanners", icon: Scan },
  { id: "remediation", label: "Remediation", icon: Wrench },
  { id: "governance", label: "Governance", icon: BarChart3 },
  { id: "services", label: "Services", icon: Server },
  { id: "sbom", label: "SBOM", icon: Layers },
  { id: "cicd", label: "CI/CD", icon: GitBranch },
  { id: "policy-engine", label: "Policy Engine", icon: Lock },
  { id: "policies", label: "SLA Policies", icon: Settings },
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
        {tab === "scanners" && <ScannersTab onRefresh={fetchDashboard} />}
        {tab === "remediation" && <RemediationTab onRefresh={fetchDashboard} />}
        {tab === "governance" && <GovernanceTab onRefresh={fetchDashboard} />}
        {tab === "services" && <ServicesTab onRefresh={fetchDashboard} />}
        {tab === "sbom" && <SBOMTab onRefresh={fetchDashboard} />}
        {tab === "cicd" && <CICDTab onRefresh={fetchDashboard} />}
        {tab === "policy-engine" && <PolicyEngineTab onRefresh={fetchDashboard} />}
        {tab === "policies" && <PoliciesTab onRefresh={fetchDashboard} />}
        {tab === "audit" && <AuditTrailTab />}
      </div>
    </div>
  );
}
