import React, { useState } from "react";
import { fetcher, SLA_API } from "../shared";

export const EscalationRulesView = ({ rules, editRules, setEditRules, setRules, onRefresh }) => {
  const [savingRules, setSavingRules] = useState(false);
  const currentRules = editRules || rules?.rules || [];

  const saveRules = async () => {
    if (!editRules) return;
    setSavingRules(true);
    try {
      const result = await fetcher(`${SLA_API}/escalation-rules`, { method: "PUT", body: JSON.stringify({ rules: editRules }) });
      setRules(result);
      setEditRules(null);
    } catch (e) { console.error(e); }
    setSavingRules(false);
  };

  const addRule = () => {
    const current = editRules || rules?.rules || [];
    const nextLevel = current.length > 0 ? Math.max(...current.map((r) => r.level)) + 1 : 1;
    setEditRules([...current, { level: nextLevel, name: `L${nextLevel} Escalation`, threshold_pct: nextLevel * 50 + 50, action: "escalate", notify_role: "admin", description: "" }]);
  };

  const removeRule = (idx) => {
    const current = editRules || rules?.rules || [];
    setEditRules(current.filter((_, i) => i !== idx));
  };

  const updateRule = (idx, field, value) => {
    const current = [...(editRules || rules?.rules || [])];
    current[idx] = { ...current[idx], [field]: field === "level" || field === "threshold_pct" ? Number(value) : value };
    setEditRules(current);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-white font-semibold text-sm">Escalation Rules</h3>
          <p className="text-xs text-slate-400 mt-0.5">Define how CVEs are escalated when SLA thresholds are breached</p>
        </div>
        <div className="flex items-center gap-2">
          <button data-testid="add-rule-btn" onClick={addRule} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors">+ Add Rule</button>
          {editRules && (
            <>
              <button onClick={() => setEditRules(null)} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-400 rounded-lg text-xs">Cancel</button>
              <button data-testid="save-rules-btn" onClick={saveRules} disabled={savingRules} className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-xs disabled:opacity-50">
                {savingRules ? "Saving..." : "Save Rules"}
              </button>
            </>
          )}
        </div>
      </div>
      <div className="space-y-3">
        {currentRules.map((rule, idx) => (
          <div key={rule.id || idx} data-testid={`escalation-rule-${idx}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <div className="grid md:grid-cols-5 gap-4 items-end">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Level</label>
                <input type="number" min="1" className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={rule.level} onChange={(e) => updateRule(idx, "level", e.target.value)} disabled={!editRules} />
              </div>
              <div className="md:col-span-2">
                <label className="text-xs text-slate-400 block mb-1">Name</label>
                <input className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={rule.name} onChange={(e) => updateRule(idx, "name", e.target.value)} disabled={!editRules} />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Threshold %</label>
                <input type="number" min="1" className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={rule.threshold_pct} onChange={(e) => updateRule(idx, "threshold_pct", e.target.value)} disabled={!editRules} />
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1">
                  <label className="text-xs text-slate-400 block mb-1">Action</label>
                  <select className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={rule.action} onChange={(e) => updateRule(idx, "action", e.target.value)} disabled={!editRules}>
                    <option value="notify">Notify</option>
                    <option value="escalate">Escalate</option>
                  </select>
                </div>
                {editRules && <button onClick={() => removeRule(idx)} className="px-2 py-2 text-red-400 hover:bg-red-500/10 rounded-lg text-xs">Remove</button>}
              </div>
            </div>
            {rule.description && <p className="text-xs text-slate-500 mt-2">{rule.description}</p>}
          </div>
        ))}
      </div>
    </div>
  );
};
