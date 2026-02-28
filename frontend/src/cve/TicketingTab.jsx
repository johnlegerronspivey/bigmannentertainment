import React, { useState, useEffect, useCallback } from "react";
import { Settings, ExternalLink, RefreshCw, Plus, Loader2, Ticket, AlertTriangle, CheckCircle2, Eye, EyeOff, Shield, Zap, X, Link2, Info } from "lucide-react";
import { fetcher, RBAC_API } from "./shared";

const TICKETING_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/ticketing`;

const PROVIDER_META = {
  jira: {
    name: "Jira",
    description: "Atlassian Jira — industry-standard issue tracking for agile teams",
    color: "from-blue-600 to-blue-500",
    fields: [
      { key: "base_url", label: "Jira Base URL", type: "text", placeholder: "https://your-domain.atlassian.net", help: "Your Jira Cloud instance URL (e.g., https://acme.atlassian.net)" },
      { key: "email", label: "Email", type: "text", placeholder: "you@company.com", help: "The email associated with your Jira account" },
      { key: "api_token", label: "API Token", type: "secret", placeholder: "Your Jira API token", help: "Generate at id.atlassian.net/manage-profile/security/api-tokens" },
      { key: "project_key", label: "Project Key", type: "text", placeholder: "CVE", help: "The key of the Jira project to create issues in (e.g., CVE, SEC)" },
    ],
  },
  servicenow: {
    name: "ServiceNow",
    description: "ServiceNow ITSM — enterprise incident management and workflow",
    color: "from-emerald-600 to-teal-500",
    fields: [
      { key: "instance_url", label: "Instance URL", type: "text", placeholder: "https://your-instance.service-now.com", help: "Your ServiceNow instance URL" },
      { key: "username", label: "Username", type: "text", placeholder: "admin", help: "ServiceNow user with incident creation permissions" },
      { key: "password", label: "Password", type: "secret", placeholder: "Service account password", help: "Password for the ServiceNow user" },
      { key: "assignment_group", label: "Assignment Group", type: "text", placeholder: "Security Team", help: "Optional: group to auto-assign new incidents to" },
    ],
  },
};

const SEVERITY_COLORS = {
  critical: "bg-red-500/20 text-red-300",
  high: "bg-orange-500/20 text-orange-300",
  medium: "bg-yellow-500/20 text-yellow-300",
  low: "bg-blue-500/20 text-blue-300",
};

const STATUS_COLORS = {
  open: "bg-red-500/20 text-red-300",
  in_progress: "bg-blue-500/20 text-blue-300",
  in_review: "bg-purple-500/20 text-purple-300",
  on_hold: "bg-yellow-500/20 text-yellow-300",
  resolved: "bg-emerald-500/20 text-emerald-300",
  closed: "bg-slate-500/20 text-slate-400",
};

/* ═══════════ Connection Status Banner ═══════════ */
function ConnectionBanner({ config, testResult }) {
  if (!config?.provider) {
    return (
      <div data-testid="connection-banner-none" className="flex items-center gap-3 bg-slate-800/60 border border-slate-700/50 rounded-xl px-5 py-3">
        <div className="w-2.5 h-2.5 rounded-full bg-slate-500 animate-pulse" />
        <span className="text-sm text-slate-400">No ticketing provider configured</span>
      </div>
    );
  }
  const providerName = PROVIDER_META[config.provider]?.name || config.provider;
  if (config.simulation_mode) {
    return (
      <div data-testid="connection-banner-sim" className="flex items-center gap-3 bg-yellow-500/5 border border-yellow-500/20 rounded-xl px-5 py-3">
        <div className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
        <span className="text-sm text-yellow-300">Simulation Mode</span>
        <span className="text-xs text-slate-400">— {providerName} configured but using simulated tickets. Add full credentials for live integration.</span>
      </div>
    );
  }
  return (
    <div data-testid="connection-banner-live" className="flex items-center gap-3 bg-emerald-500/5 border border-emerald-500/20 rounded-xl px-5 py-3">
      <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
      <span className="text-sm text-emerald-300">Live</span>
      <span className="text-xs text-slate-400">— Connected to {providerName}. Tickets will be created in your real instance.</span>
      {testResult?.success && !testResult?.simulation && (
        <span className="ml-auto text-xs text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> {testResult.message}</span>
      )}
    </div>
  );
}

/* ═══════════ Full Config Panel (admin only) ═══════════ */
function FullConfigPanel({ config, onSave, canManage }) {
  const [provider, setProvider] = useState(config?.provider || "");
  const [settings, setSettings] = useState(config?.settings || {});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [showSecrets, setShowSecrets] = useState({});
  const [dirty, setDirty] = useState(false);

  const token = localStorage.getItem("token");
  const authHeaders = { "Content-Type": "application/json", Authorization: `Bearer ${token}` };

  const meta = PROVIDER_META[provider];

  useEffect(() => {
    setProvider(config?.provider || "");
    setSettings(config?.settings || {});
    setDirty(false);
  }, [config]);

  const handleFieldChange = (key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
  };

  const handleProviderSwitch = (newProvider) => {
    if (newProvider === provider) return;
    setProvider(newProvider);
    setSettings({});
    setDirty(true);
    setTestResult(null);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetcher(`${TICKETING_API}/config`, {
        method: "PUT",
        headers: authHeaders,
        body: JSON.stringify({ provider, settings }),
      });
      setDirty(false);
      setTestResult(null);
      onSave();
    } catch (e) { alert("Save failed: " + e.message); }
    setSaving(false);
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const r = await fetcher(`${TICKETING_API}/test-connection`, { method: "POST", headers: authHeaders });
      setTestResult(r);
    } catch (e) { setTestResult({ success: false, message: "Connection test failed" }); }
    setTesting(false);
  };

  const handleDisconnect = async () => {
    if (!window.confirm("Remove ticketing configuration? Existing tickets will be preserved.")) return;
    setSaving(true);
    try {
      await fetcher(`${TICKETING_API}/config`, {
        method: "PUT",
        headers: authHeaders,
        body: JSON.stringify({ provider: "", settings: {} }),
      });
      setProvider("");
      setSettings({});
      setDirty(false);
      setTestResult(null);
      onSave();
    } catch (e) { alert("Failed: " + e.message); }
    setSaving(false);
  };

  const toggleSecret = (key) => setShowSecrets((prev) => ({ ...prev, [key]: !prev[key] }));

  // Count filled required fields
  const requiredFields = meta?.fields?.filter((f) => f.key !== "assignment_group") || [];
  const filledCount = requiredFields.filter((f) => settings[f.key] && !settings[f.key].startsWith("••••")).length;
  const allFilled = filledCount === requiredFields.length;

  if (!canManage) return null;

  return (
    <div data-testid="ticketing-config-panel" className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-700/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-cyan-400" />
          <h3 className="text-white font-semibold">Ticketing Configuration</h3>
          <span className="text-xs text-slate-500 ml-1">Admin only</span>
        </div>
        {provider && (
          <button data-testid="disconnect-provider-btn" onClick={handleDisconnect}
            className="text-xs text-red-400 hover:text-red-300 transition-colors">
            Disconnect
          </button>
        )}
      </div>

      <div className="p-5 space-y-5">
        {/* Provider Selection */}
        <div>
          <label className="text-xs text-slate-400 block mb-2 uppercase tracking-wider">Select Provider</label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(PROVIDER_META).map(([key, pm]) => (
              <button
                key={key}
                data-testid={`provider-card-${key}`}
                onClick={() => handleProviderSwitch(key)}
                className={`text-left p-4 rounded-xl border transition-all ${
                  provider === key
                    ? "border-cyan-500/50 bg-cyan-500/5 ring-1 ring-cyan-500/30"
                    : "border-slate-700/50 bg-slate-900/40 hover:border-slate-600"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${pm.color} flex items-center justify-center`}>
                    <Link2 className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="text-white font-medium text-sm">{pm.name}</div>
                    <div className="text-xs text-slate-400">{pm.description}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Credential Fields */}
        {meta && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs text-slate-400 uppercase tracking-wider">Credentials</label>
              <span className="text-xs text-slate-500">{filledCount}/{requiredFields.length} required fields</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {meta.fields.map((field) => {
                const isSecret = field.type === "secret";
                const isRevealed = showSecrets[field.key];
                const value = settings[field.key] || "";
                const isMasked = value.startsWith("••••");
                return (
                  <div key={field.key}>
                    <label className="text-sm text-slate-300 block mb-1">{field.label}</label>
                    <div className="relative">
                      <input
                        data-testid={`ticketing-field-${field.key}`}
                        type={isSecret && !isRevealed ? "password" : "text"}
                        placeholder={field.placeholder}
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-white text-sm pr-10 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-colors"
                        value={value}
                        onChange={(e) => handleFieldChange(field.key, e.target.value)}
                      />
                      {isSecret && (
                        <button
                          type="button"
                          data-testid={`toggle-${field.key}-visibility`}
                          onClick={() => toggleSecret(field.key)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                        >
                          {isRevealed ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      )}
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                      <Info className="w-3 h-3 text-slate-600" />
                      <span className="text-xs text-slate-600">{field.help}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Actions */}
        {meta && (
          <div className="flex items-center gap-3 pt-2 border-t border-slate-700/30">
            <button
              data-testid="ticketing-save-btn"
              onClick={handleSave}
              disabled={saving || !provider}
              className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                dirty ? "bg-cyan-600 hover:bg-cyan-700 text-white" : "bg-slate-700 text-slate-400"
              } disabled:opacity-50`}
            >
              {saving ? "Saving..." : dirty ? "Save Configuration" : "Saved"}
            </button>
            <button
              data-testid="ticketing-test-btn"
              onClick={handleTest}
              disabled={testing || !provider || dirty}
              className="px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {testing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              {testing ? "Testing..." : "Test Connection"}
            </button>
            {testResult && (
              <span data-testid="test-connection-result" className={`text-xs flex items-center gap-1 ${testResult.success ? "text-emerald-400" : "text-red-400"}`}>
                {testResult.success ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
                {testResult.simulation && <span className="text-yellow-400">[Simulation] </span>}
                {testResult.message}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ═══════════ Ticket Row ═══════════ */
function TicketRow({ ticket, onSync }) {
  const [syncing, setSyncing] = useState(false);
  const handleSync = async () => {
    setSyncing(true);
    await onSync(ticket.id);
    setSyncing(false);
  };

  return (
    <div data-testid={`ticket-row-${ticket.id}`} className="flex items-center gap-4 bg-slate-800/40 border border-slate-700/30 rounded-xl px-4 py-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-white font-medium text-sm truncate">{ticket.external_key}</span>
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLORS[ticket.severity] || ""}`}>{ticket.severity?.toUpperCase()}</span>
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[ticket.status] || "bg-slate-600/30 text-slate-300"}`}>{ticket.status?.replace("_", " ").toUpperCase()}</span>
          {ticket.simulation && <span className="px-1.5 py-0.5 bg-yellow-500/10 text-yellow-400 rounded text-xs">SIM</span>}
        </div>
        <div className="text-xs text-slate-400 truncate">{ticket.title}</div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <a href={ticket.external_url} target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-cyan-400 transition-colors" title="Open in ticketing system">
          <ExternalLink className="w-4 h-4" />
        </a>
        <button onClick={handleSync} disabled={syncing} className="text-slate-400 hover:text-white transition-colors" title="Sync status">
          <RefreshCw className={`w-4 h-4 ${syncing ? "animate-spin" : ""}`} />
        </button>
      </div>
    </div>
  );
}

/* ═══════════ Main Tab ═══════════ */
export const TicketingTab = ({ onRefresh }) => {
  const [config, setConfig] = useState(null);
  const [tickets, setTickets] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [bulkSeverity, setBulkSeverity] = useState("critical");
  const [canManageConfig, setCanManageConfig] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const token = localStorage.getItem("token");

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const [c, t, s] = await Promise.all([
        fetcher(`${TICKETING_API}/config`, { headers }),
        fetcher(`${TICKETING_API}/tickets?limit=50`, { headers }),
        fetcher(`${TICKETING_API}/stats`, { headers }),
      ]);
      setConfig(c);
      setTickets(t);
      setStats(s);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [token]);

  const fetchRole = useCallback(async () => {
    if (!token) return;
    try {
      const data = await fetcher(`${RBAC_API}/me`, { headers: { Authorization: `Bearer ${token}` } });
      const role = data.cve_role || "analyst";
      setCanManageConfig(["super_admin", "tenant_admin"].includes(role));
    } catch (e) { console.error(e); }
  }, [token]);

  useEffect(() => { fetchAll(); fetchRole(); }, [fetchAll, fetchRole]);

  const handleBulkCreate = async () => {
    setCreating(true);
    try {
      await fetcher(`${TICKETING_API}/tickets/bulk`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ severity: bulkSeverity, limit: 10 }),
      });
      fetchAll();
      onRefresh();
    } catch (e) { console.error(e); }
    setCreating(false);
  };

  const handleSync = async (ticketId) => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      await fetcher(`${TICKETING_API}/tickets/${ticketId}/sync`, { method: "POST", headers });
      fetchAll();
    } catch (e) { console.error(e); }
  };

  const handleSyncAll = async () => {
    try {
      await fetcher(`${TICKETING_API}/sync-all`, { method: "POST" });
      fetchAll();
    } catch (e) { console.error(e); }
  };

  if (loading) {
    return (
      <div className="text-center py-16 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3" />Loading ticketing data...
      </div>
    );
  }

  return (
    <div data-testid="ticketing-tab" className="space-y-6">
      {/* Connection Status Banner */}
      <ConnectionBanner config={config} testResult={testResult} />

      {/* Config Panel (admin only) */}
      <FullConfigPanel config={config} onSave={fetchAll} canManage={canManageConfig} />

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-white">{stats.total}</div>
            <div className="text-xs text-slate-400">Total Tickets</div>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-red-400">{stats.open}</div>
            <div className="text-xs text-slate-400">Open</div>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.in_progress}</div>
            <div className="text-xs text-slate-400">In Progress</div>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-emerald-400">{stats.closed}</div>
            <div className="text-xs text-slate-400">Closed</div>
          </div>
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${config?.simulation_mode ? "text-yellow-400" : "text-emerald-400"}`}>
              {config?.simulation_mode ? "SIM" : "LIVE"}
            </div>
            <div className="text-xs text-slate-400">Mode</div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <select
            data-testid="bulk-severity-select"
            className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
            value={bulkSeverity}
            onChange={(e) => setBulkSeverity(e.target.value)}
          >
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <button
            data-testid="bulk-create-tickets-btn"
            onClick={handleBulkCreate}
            disabled={creating || !config?.configured}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Bulk Create Tickets
          </button>
        </div>
        <button
          data-testid="sync-all-tickets-btn"
          onClick={handleSyncAll}
          className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition-colors"
        >
          <RefreshCw className="w-4 h-4" /> Sync All
        </button>
      </div>

      {/* Ticket List */}
      <div className="space-y-2">
        <h3 className="text-white font-semibold flex items-center gap-2">
          <Ticket className="w-4 h-4 text-cyan-400" /> Tickets ({tickets?.total || 0})
        </h3>
        {tickets?.items?.length === 0 && (
          <div className="text-center text-slate-500 py-8">No tickets yet. Configure a provider and create tickets from your CVEs.</div>
        )}
        {tickets?.items?.map((t) => (
          <TicketRow key={t.id} ticket={t} onSync={handleSync} />
        ))}
      </div>
    </div>
  );
};
