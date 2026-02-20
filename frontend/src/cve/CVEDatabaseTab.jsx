import React, { useState, useEffect, useCallback, useRef } from "react";
import { Search, Plus, ChevronDown, ChevronRight, Users, Calendar, X, Filter } from "lucide-react";
import { API, fetcher, SeverityBadge, StatusBadge } from "./shared";
import { AssignOwnerModal } from "./AssignOwnerModal";

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
            <input data-testid="cve-create-id" placeholder="CVE ID (e.g. CVE-2026-XXXX)" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm col-span-2 focus:border-cyan-500 focus:outline-none" value={form.cve_id} onChange={(e) => setForm({ ...form, cve_id: e.target.value })} />
            <input data-testid="cve-create-title" placeholder="Title *" required className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm col-span-2 focus:border-cyan-500 focus:outline-none" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <select data-testid="cve-create-severity" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
              {["critical", "high", "medium", "low", "info"].map((s) => <option key={s} value={s}>{s.toUpperCase()}</option>)}
            </select>
            <input data-testid="cve-create-cvss" type="number" step="0.1" min="0" max="10" placeholder="CVSS Score" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={form.cvss_score} onChange={(e) => setForm({ ...form, cvss_score: e.target.value })} />
            <input data-testid="cve-create-package" placeholder="Affected Package" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={form.affected_package} onChange={(e) => setForm({ ...form, affected_package: e.target.value })} />
            <input placeholder="Affected Version" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={form.affected_version} onChange={(e) => setForm({ ...form, affected_version: e.target.value })} />
            <input placeholder="Fixed Version" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={form.fixed_version} onChange={(e) => setForm({ ...form, fixed_version: e.target.value })} />
            <input placeholder="Services (comma-separated)" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={form.affected_services} onChange={(e) => setForm({ ...form, affected_services: e.target.value })} />
            <input data-testid="cve-create-owner" placeholder="Assign to (person)" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })} />
            <input data-testid="cve-create-team" placeholder="Assign to (team)" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={form.assigned_team} onChange={(e) => setForm({ ...form, assigned_team: e.target.value })} />
          </div>
          <textarea placeholder="Description" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm h-20 focus:border-cyan-500 focus:outline-none" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white text-sm">Cancel</button>
            <button data-testid="cve-create-submit" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">{saving ? "Saving..." : "Create CVE"}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

const CVERowSkeleton = () => (
  <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl px-4 py-3 animate-pulse">
    <div className="flex items-center gap-3">
      <div className="w-4 h-4 bg-slate-700 rounded" />
      <div className="flex-1">
        <div className="h-4 bg-slate-700 rounded w-1/4 mb-2" />
        <div className="h-3 bg-slate-700 rounded w-1/2" />
      </div>
      <div className="h-5 bg-slate-700 rounded w-16" />
    </div>
  </div>
);

const ActiveFilters = ({ filters, onClear }) => {
  const active = [];
  if (filters.status) active.push({ key: "status", label: `Status: ${filters.status.replace("_", " ")}` });
  if (filters.severity) active.push({ key: "severity", label: `Severity: ${filters.severity}` });
  if (filters.search) active.push({ key: "search", label: `Search: "${filters.search}"` });
  if (active.length === 0) return null;

  return (
    <div data-testid="active-filters" className="flex items-center gap-2 flex-wrap">
      <Filter className="w-3.5 h-3.5 text-slate-500" />
      {active.map((f) => (
        <span key={f.key} className="flex items-center gap-1 px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded-lg text-xs border border-cyan-500/20">
          {f.label}
          <button onClick={() => onClear(f.key)} className="hover:text-white transition-colors"><X className="w-3 h-3" /></button>
        </span>
      ))}
      <button data-testid="clear-all-filters-btn" onClick={() => onClear("all")} className="text-xs text-slate-500 hover:text-white transition-colors ml-1">Clear all</button>
    </div>
  );
};

export const CVEDatabaseTab = ({ onRefresh }) => {
  const [cves, setCves] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: "", severity: "", search: "" });
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [expanded, setExpanded] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [assignTarget, setAssignTarget] = useState(null);
  const debounceTimer = useRef(null);

  // Debounce search input
  const handleSearchChange = (value) => {
    setFilters((f) => ({ ...f, search: value }));
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(() => setDebouncedSearch(value), 350);
  };

  const fetchCves = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.status) params.set("status", filters.status);
      if (filters.severity) params.set("severity", filters.severity);
      if (debouncedSearch) params.set("search", debouncedSearch);
      params.set("limit", "50");
      const data = await fetcher(`${API}/entries?${params}`);
      setCves(data.items || []);
      setTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [filters.status, filters.severity, debouncedSearch]);

  useEffect(() => { fetchCves(); }, [fetchCves]);

  const handleStatusChange = async (id, newStatus) => {
    try {
      await fetcher(`${API}/entries/${id}/status`, { method: "PUT", body: JSON.stringify({ status: newStatus }) });
      fetchCves();
      onRefresh();
    } catch (e) { console.error(e); }
  };

  const handleClearFilter = (key) => {
    if (key === "all") {
      setFilters({ status: "", severity: "", search: "" });
      setDebouncedSearch("");
    } else {
      setFilters((f) => ({ ...f, [key]: "" }));
      if (key === "search") setDebouncedSearch("");
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input data-testid="cve-search-input" className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none transition-colors" placeholder="Search CVE ID, package, title..." value={filters.search} onChange={(e) => handleSearchChange(e.target.value)} />
          {filters.search && (
            <button onClick={() => handleClearFilter("search")} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <select data-testid="cve-status-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={filters.status} onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}>
          <option value="">All Statuses</option>
          {["detected", "triaged", "in_progress", "fixed", "verified", "dismissed", "wont_fix"].map((s) => <option key={s} value={s}>{s.replace("_", " ").toUpperCase()}</option>)}
        </select>
        <select data-testid="cve-severity-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 focus:outline-none" value={filters.severity} onChange={(e) => setFilters((f) => ({ ...f, severity: e.target.value }))}>
          <option value="">All Severities</option>
          {["critical", "high", "medium", "low", "info"].map((s) => <option key={s} value={s}>{s.toUpperCase()}</option>)}
        </select>
        <button data-testid="cve-create-btn" onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          <Plus className="w-4 h-4" /> Add CVE
        </button>
      </div>

      <ActiveFilters filters={filters} onClear={handleClearFilter} />

      <div className="flex items-center justify-between">
        <div data-testid="cve-count-label" className="text-sm text-slate-400">{total} CVE{total !== 1 ? "s" : ""} found</div>
      </div>

      <div className="space-y-2">
        {loading && cves.length === 0 && [...Array(5)].map((_, i) => <CVERowSkeleton key={i} />)}
        {cves.map((c) => (
          <div key={c.id} data-testid={`cve-row-${c.id}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden hover:border-slate-600/60 transition-colors">
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
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    <span className="text-slate-500">Detected:</span> <span className="text-white ml-1">{new Date(c.detected_at).toLocaleString()}</span>
                  </div>
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
                <div className="flex items-center gap-2 pt-2">
                  <span className="text-xs text-slate-500 mr-2">Transition:</span>
                  {c.status === "detected" && <><button data-testid={`triage-btn-${c.id}`} onClick={() => handleStatusChange(c.id, "triaged")} className="px-3 py-1 rounded text-xs bg-yellow-600/30 text-yellow-300 hover:bg-yellow-600/50 transition-colors">Triage</button><button onClick={() => handleStatusChange(c.id, "dismissed")} className="px-3 py-1 rounded text-xs bg-slate-600/30 text-slate-300 hover:bg-slate-600/50 transition-colors">Dismiss</button></>}
                  {c.status === "triaged" && <><button data-testid={`start-fix-btn-${c.id}`} onClick={() => handleStatusChange(c.id, "in_progress")} className="px-3 py-1 rounded text-xs bg-blue-600/30 text-blue-300 hover:bg-blue-600/50 transition-colors">Start Fix</button><button onClick={() => handleStatusChange(c.id, "wont_fix")} className="px-3 py-1 rounded text-xs bg-slate-600/30 text-slate-300 hover:bg-slate-600/50 transition-colors">Won't Fix</button></>}
                  {c.status === "in_progress" && <button data-testid={`mark-fixed-btn-${c.id}`} onClick={() => handleStatusChange(c.id, "fixed")} className="px-3 py-1 rounded text-xs bg-emerald-600/30 text-emerald-300 hover:bg-emerald-600/50 transition-colors">Mark Fixed</button>}
                  {c.status === "fixed" && <button data-testid={`verify-btn-${c.id}`} onClick={() => handleStatusChange(c.id, "verified")} className="px-3 py-1 rounded text-xs bg-green-600/30 text-green-300 hover:bg-green-600/50 transition-colors">Verify</button>}
                </div>
              </div>
            )}
          </div>
        ))}
        {!loading && cves.length === 0 && (
          <div data-testid="cve-empty-state" className="text-center py-12">
            <Search className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400 text-sm">No CVEs found matching your filters.</p>
            <p className="text-slate-600 text-xs mt-1">Try adjusting your search or filters, or run a scan.</p>
          </div>
        )}
      </div>

      {showCreate && <CreateCVEModal onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); fetchCves(); onRefresh(); }} />}
      {assignTarget && <AssignOwnerModal cve={assignTarget} onClose={() => setAssignTarget(null)} onAssigned={() => { setAssignTarget(null); fetchCves(); onRefresh(); }} />}
    </div>
  );
};
