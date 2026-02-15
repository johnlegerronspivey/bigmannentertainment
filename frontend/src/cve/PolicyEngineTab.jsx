import React, { useState, useEffect, useCallback } from "react";
import { Plus, Shield, Trash2, ToggleLeft, ToggleRight, CheckCircle, XCircle } from "lucide-react";
import { SCANNER_API, fetcher } from "./shared";

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

export const PolicyEngineTab = ({ onRefresh }) => {
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
