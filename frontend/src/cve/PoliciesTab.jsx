import React, { useState, useEffect, useCallback } from "react";
import { Settings, Activity } from "lucide-react";
import { API, SEVERITY_COLORS, fetcher } from "./shared";

export const PoliciesTab = ({ onRefresh }) => {
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

export const AuditTrailTab = () => {
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
