import React, { useState, useEffect } from "react";
import { Settings, Save, RotateCcw } from "lucide-react";
import { SLA_API, SEVERITY_COLORS, fetcher } from "../shared";

export const PoliciesView = ({ policies: initialPolicies, fetchAll }) => {
  const [policies, setPolicies] = useState([]);
  const [defaults, setDefaults] = useState({});
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (initialPolicies) {
      setPolicies(initialPolicies.policies || []);
      setDefaults(initialPolicies.defaults || {});
    }
  }, [initialPolicies]);

  const updateHours = (sev, hours) => {
    setPolicies((prev) =>
      prev.map((p) => (p.severity === sev ? { ...p, sla_hours: Math.max(1, parseInt(hours) || 1) } : p))
    );
    setDirty(true);
  };

  const resetToDefaults = () => {
    setPolicies((prev) =>
      prev.map((p) => ({ ...p, sla_hours: defaults[p.severity] || p.sla_hours }))
    );
    setDirty(true);
  };

  const savePolicies = async () => {
    setSaving(true);
    try {
      await fetcher(`${SLA_API}/policies`, {
        method: "PUT",
        body: JSON.stringify({ policies: policies.map((p) => ({ severity: p.severity, sla_hours: p.sla_hours })) }),
      });
      setDirty(false);
      fetchAll();
    } catch (e) {
      console.error(e);
    }
    setSaving(false);
  };

  return (
    <div data-testid="sla-policies-view" className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-white font-semibold text-sm">SLA Policy Configuration</h3>
          <p className="text-xs text-slate-400 mt-0.5">Set the maximum hours allowed to resolve CVEs per severity level</p>
        </div>
        <div className="flex items-center gap-2">
          <button data-testid="reset-policies-btn" onClick={resetToDefaults} className="flex items-center gap-1.5 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors">
            <RotateCcw className="w-3.5 h-3.5" /> Reset to Defaults
          </button>
          <button data-testid="save-policies-btn" onClick={savePolicies} disabled={saving || !dirty} className="flex items-center gap-1.5 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-xs transition-colors disabled:opacity-50">
            <Save className="w-3.5 h-3.5" /> {saving ? "Saving..." : "Save Policies"}
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {policies.map((policy) => {
          const c = SEVERITY_COLORS[policy.severity] || SEVERITY_COLORS.info;
          const isDefault = policy.sla_hours === (defaults[policy.severity] || 0);
          const days = Math.floor(policy.sla_hours / 24);
          const hours = policy.sla_hours % 24;
          return (
            <div key={policy.severity} data-testid={`policy-card-${policy.severity}`} className={`${c.bg} border ${c.border} rounded-xl p-6`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Settings className={`w-4 h-4 ${c.text}`} />
                  <h4 className={`${c.text} font-semibold text-sm uppercase`}>{policy.severity}</h4>
                </div>
                {isDefault && <span className="text-xs text-slate-500 px-2 py-0.5 bg-slate-700/50 rounded">Default</span>}
                {!isDefault && <span className="text-xs text-cyan-400 px-2 py-0.5 bg-cyan-500/10 rounded">Custom</span>}
              </div>
              <div className="mb-4">
                <label className="text-xs text-slate-400 block mb-1.5">SLA Hours</label>
                <input
                  data-testid={`policy-input-${policy.severity}`}
                  type="number"
                  min="1"
                  max="8760"
                  className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2.5 text-white text-sm focus:border-cyan-500/50 focus:outline-none transition-colors"
                  value={policy.sla_hours}
                  onChange={(e) => updateHours(policy.severity, e.target.value)}
                />
              </div>
              <div className="text-xs text-slate-400">
                = {days > 0 ? `${days} day${days > 1 ? "s" : ""} ` : ""}{hours > 0 ? `${hours} hour${hours > 1 ? "s" : ""}` : days > 0 ? "" : "0 hours"}
                {defaults[policy.severity] && <span className="ml-2 text-slate-500">(default: {defaults[policy.severity]}h)</span>}
              </div>
              {policy.updated_at && <div className="text-xs text-slate-600 mt-2">Last updated: {new Date(policy.updated_at).toLocaleDateString()}</div>}
            </div>
          );
        })}
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h4 className="text-white font-semibold text-sm mb-3">SLA Policy Reference</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          {policies.map((p) => {
            const c = SEVERITY_COLORS[p.severity] || SEVERITY_COLORS.info;
            return (
              <div key={p.severity} className="bg-slate-900/50 rounded-lg p-3 text-center">
                <div className={`${c.text} font-semibold uppercase mb-1`}>{p.severity}</div>
                <div className="text-white text-lg font-bold">{p.sla_hours}h</div>
                <div className="text-slate-500">{Math.floor(p.sla_hours / 24)}d {p.sla_hours % 24}h</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
