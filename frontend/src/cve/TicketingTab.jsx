import React, { useState, useEffect, useCallback } from "react";
import { Settings, ExternalLink, RefreshCw, Plus, Loader2, Ticket, AlertTriangle, CheckCircle2 } from "lucide-react";
import { fetcher } from "./shared";

const TICKETING_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/ticketing`;

const PROVIDER_OPTIONS = [
  { id: "jira", name: "Jira", fields: ["base_url", "email", "api_token", "project_key"] },
  { id: "servicenow", name: "ServiceNow", fields: ["instance_url", "username", "password", "assignment_group"] },
];

const FIELD_LABELS = {
  base_url: "Base URL",
  email: "Email",
  api_token: "API Token",
  project_key: "Project Key",
  instance_url: "Instance URL",
  username: "Username",
  password: "Password",
  assignment_group: "Assignment Group",
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

function ConfigPanel({ config, onSave }) {
  const [provider, setProvider] = useState(config?.provider || "");
  const [settings, setSettings] = useState(config?.settings || {});
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const providerDef = PROVIDER_OPTIONS.find((p) => p.id === provider);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetcher(`${TICKETING_API}/config`, {
        method: "PUT",
        body: JSON.stringify({ provider, settings }),
      });
      onSave();
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  const handleTest = async () => {
    setTestResult(null);
    try {
      const r = await fetcher(`${TICKETING_API}/test-connection`, { method: "POST" });
      setTestResult(r);
    } catch (e) { setTestResult({ success: false, message: "Connection test failed" }); }
  };

  return (
    <div data-testid="ticketing-config-panel" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 space-y-4">
      <h3 className="text-white font-semibold flex items-center gap-2"><Settings className="w-4 h-4 text-cyan-400" /> Ticketing Configuration</h3>
      <div>
        <label className="text-xs text-slate-400 block mb-1">Provider</label>
        <select
          data-testid="ticketing-provider-select"
          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
          value={provider}
          onChange={(e) => { setProvider(e.target.value); setSettings({}); }}
        >
          <option value="">Select provider...</option>
          {PROVIDER_OPTIONS.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>
      {providerDef && (
        <div className="grid grid-cols-2 gap-3">
          {providerDef.fields.map((f) => (
            <div key={f}>
              <label className="text-xs text-slate-400 block mb-1">{FIELD_LABELS[f] || f}</label>
              <input
                data-testid={`ticketing-field-${f}`}
                type={f.includes("password") || f.includes("token") ? "password" : "text"}
                placeholder={FIELD_LABELS[f]}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
                value={settings[f] || ""}
                onChange={(e) => setSettings({ ...settings, [f]: e.target.value })}
              />
            </div>
          ))}
        </div>
      )}
      <div className="flex items-center gap-3">
        <button data-testid="ticketing-save-btn" onClick={handleSave} disabled={saving || !provider} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">
          {saving ? "Saving..." : "Save Configuration"}
        </button>
        <button data-testid="ticketing-test-btn" onClick={handleTest} disabled={!provider} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition-colors disabled:opacity-50">
          Test Connection
        </button>
        {testResult && (
          <span className={`text-xs ${testResult.success ? "text-emerald-400" : "text-red-400"}`}>
            {testResult.simulation && <span className="text-yellow-400 mr-1">[Simulation]</span>}
            {testResult.message}
          </span>
        )}
      </div>
    </div>
  );
}

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

export const TicketingTab = ({ onRefresh }) => {
  const [config, setConfig] = useState(null);
  const [tickets, setTickets] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [bulkSeverity, setBulkSeverity] = useState("critical");

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [c, t, s] = await Promise.all([
        fetcher(`${TICKETING_API}/config`),
        fetcher(`${TICKETING_API}/tickets?limit=50`),
        fetcher(`${TICKETING_API}/stats`),
      ]);
      setConfig(c);
      setTickets(t);
      setStats(s);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleBulkCreate = async () => {
    setCreating(true);
    try {
      await fetcher(`${TICKETING_API}/tickets/bulk`, {
        method: "POST",
        body: JSON.stringify({ severity: bulkSeverity, limit: 10 }),
      });
      fetchAll();
      onRefresh();
    } catch (e) { console.error(e); }
    setCreating(false);
  };

  const handleSync = async (ticketId) => {
    try {
      await fetcher(`${TICKETING_API}/tickets/${ticketId}/sync`, { method: "POST" });
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
      <ConfigPanel config={config} onSave={fetchAll} />

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
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
        {config?.simulation_mode && config?.configured && (
          <span className="px-2 py-1 bg-yellow-500/10 text-yellow-400 rounded-lg text-xs flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" /> Simulation Mode — provide full credentials for live integration
          </span>
        )}
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
