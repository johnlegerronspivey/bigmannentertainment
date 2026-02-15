import React, { useState, useEffect, useCallback } from "react";
import { AlertTriangle, Clock, Activity, XCircle, Eye, Scan, Wrench, Loader2, Target, Bell, Mail, Send, Settings, X, FileDown, Users } from "lucide-react";
import { NOTIFICATION_API, REPORTS_API, fetcher } from "./shared";

const NOTIF_TYPE_LABELS = {
  new_cve: "New CVE", cve_assigned: "Assignment", sla_warning: "SLA Warning",
  sla_breach: "SLA Breach", status_change: "Status Change", remediation_update: "Remediation",
  scan_complete: "Scan Complete", weekly_digest: "Weekly Digest",
};
const NOTIF_TYPE_ICONS = {
  new_cve: AlertTriangle, cve_assigned: Users, sla_warning: Clock,
  sla_breach: XCircle, status_change: Activity, remediation_update: Wrench,
  scan_complete: Scan, weekly_digest: Mail,
};
const NOTIF_SEVERITY_DOT = {
  critical: "bg-red-500", high: "bg-orange-500", medium: "bg-yellow-500", low: "bg-blue-500", info: "bg-slate-500",
};

export const NotificationsTab = ({ onRefresh, unreadCount, onUnreadUpdate }) => {
  const [notifications, setNotifications] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [prefs, setPrefs] = useState(null);
  const [showPrefs, setShowPrefs] = useState(false);
  const [slaResult, setSlaResult] = useState(null);
  const [digestResult, setDigestResult] = useState(null);
  const [testEmailResult, setTestEmailResult] = useState(null);
  const [actionLoading, setActionLoading] = useState("");

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, limit: 30 });
      if (unreadOnly) params.set("unread_only", "true");
      if (filter) params.set("type", filter);
      const data = await fetcher(`${NOTIFICATION_API}?${params}`);
      setNotifications(data.notifications || []);
      setTotal(data.total || 0);
      setPages(data.pages || 1);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [page, filter, unreadOnly]);

  const fetchPrefs = useCallback(async () => {
    try { setPrefs(await fetcher(`${NOTIFICATION_API}/preferences`)); } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchNotifications(); }, [fetchNotifications]);
  useEffect(() => { fetchPrefs(); }, [fetchPrefs]);

  const markRead = async (id) => {
    await fetcher(`${NOTIFICATION_API}/${id}/read`, { method: "PUT" });
    fetchNotifications();
    onUnreadUpdate();
  };
  const markAllRead = async () => {
    await fetcher(`${NOTIFICATION_API}/read-all`, { method: "PUT" });
    fetchNotifications();
    onUnreadUpdate();
  };
  const dismiss = async (id) => {
    await fetcher(`${NOTIFICATION_API}/${id}`, { method: "DELETE" });
    fetchNotifications();
    onUnreadUpdate();
  };

  const checkSla = async () => {
    setActionLoading("sla");
    try { setSlaResult(await fetcher(`${NOTIFICATION_API}/check-sla`, { method: "POST" })); fetchNotifications(); onUnreadUpdate(); } catch (e) { console.error(e); }
    setActionLoading("");
  };

  const sendDigest = async () => {
    setActionLoading("digest");
    try { setDigestResult(await fetcher(`${NOTIFICATION_API}/weekly-digest`, { method: "POST" })); } catch (e) { console.error(e); }
    setActionLoading("");
  };

  const sendTestEmail = async () => {
    setActionLoading("test");
    try { setTestEmailResult(await fetcher(`${NOTIFICATION_API}/test-email`, { method: "POST", body: JSON.stringify({}) })); } catch (e) { console.error(e); }
    setActionLoading("");
  };

  const updatePref = async (key, value) => {
    try {
      const updated = await fetcher(`${NOTIFICATION_API}/preferences`, { method: "PUT", body: JSON.stringify({ [key]: value }) });
      setPrefs(updated);
    } catch (e) { console.error(e); }
  };

  const toggleEmailType = async (type) => {
    if (!prefs) return;
    const newTypes = { ...prefs.email_types, [type]: !prefs.email_types[type] };
    await updatePref("email_types", newTypes);
  };

  const exportCvesCsv = () => { window.open(`${REPORTS_API}/cves/csv`, "_blank"); };
  const exportGovernanceCsv = () => { window.open(`${REPORTS_API}/governance/csv`, "_blank"); };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <button data-testid="check-sla-btn" onClick={checkSla} disabled={actionLoading === "sla"} className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">
          {actionLoading === "sla" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Target className="w-4 h-4" />} Check SLA
        </button>
        <button data-testid="send-digest-btn" onClick={sendDigest} disabled={actionLoading === "digest"} className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">
          {actionLoading === "digest" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />} Weekly Digest
        </button>
        <button data-testid="test-email-btn" onClick={sendTestEmail} disabled={actionLoading === "test"} className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors disabled:opacity-50">
          {actionLoading === "test" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />} Test Email
        </button>
        <button data-testid="notif-prefs-btn" onClick={() => setShowPrefs(!showPrefs)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-colors ${showPrefs ? "bg-cyan-500/20 text-cyan-400" : "bg-slate-700 hover:bg-slate-600 text-white"}`}>
          <Settings className="w-4 h-4" /> Preferences
        </button>
        <div className="flex-1" />
        <button data-testid="export-cves-csv-btn" onClick={exportCvesCsv} className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors">
          <FileDown className="w-4 h-4" /> Export CVEs CSV
        </button>
        <button data-testid="export-governance-csv-btn" onClick={exportGovernanceCsv} className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors">
          <FileDown className="w-4 h-4" /> Export Governance CSV
        </button>
      </div>

      {slaResult && (
        <div data-testid="sla-result" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white font-semibold text-sm">SLA Check Result</h3>
            <button onClick={() => setSlaResult(null)} className="text-slate-400 hover:text-white"><X className="w-4 h-4" /></button>
          </div>
          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="bg-slate-700/40 rounded-lg p-3">
              <div className="text-xl font-bold text-white">{slaResult.checked}</div><div className="text-xs text-slate-400">Checked</div>
            </div>
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
              <div className="text-xl font-bold text-yellow-400">{slaResult.warnings}</div><div className="text-xs text-yellow-400/80">Warnings</div>
            </div>
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              <div className="text-xl font-bold text-red-400">{slaResult.breaches}</div><div className="text-xs text-red-400/80">Breaches</div>
            </div>
          </div>
        </div>
      )}

      {digestResult && (
        <div data-testid="digest-result" className="bg-slate-800/60 border border-purple-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white font-semibold text-sm">Weekly Digest — {digestResult.period}</h3>
            <button onClick={() => setDigestResult(null)} className="text-slate-400 hover:text-white"><X className="w-4 h-4" /></button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center text-sm">
            <div className="bg-slate-700/40 rounded-lg p-3"><div className="text-lg font-bold text-cyan-400">{digestResult.open_cves}</div><div className="text-xs text-slate-400">Open</div></div>
            <div className="bg-slate-700/40 rounded-lg p-3"><div className="text-lg font-bold text-orange-400">{digestResult.new_cves}</div><div className="text-xs text-slate-400">New This Week</div></div>
            <div className="bg-slate-700/40 rounded-lg p-3"><div className="text-lg font-bold text-emerald-400">{digestResult.fixed_cves}</div><div className="text-xs text-slate-400">Fixed</div></div>
            <div className="bg-slate-700/40 rounded-lg p-3"><div className="text-lg font-bold text-red-400">{digestResult.critical_open}</div><div className="text-xs text-slate-400">Critical Open</div></div>
          </div>
        </div>
      )}

      {testEmailResult && (
        <div data-testid="test-email-result" className={`rounded-xl p-3 text-sm ${testEmailResult.sent ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-400" : "bg-red-500/10 border border-red-500/30 text-red-400"}`}>
          {testEmailResult.sent ? `Test email sent to ${testEmailResult.recipient}` : `Failed: ${testEmailResult.error}`}
          <button onClick={() => setTestEmailResult(null)} className="ml-3 text-slate-400 hover:text-white"><X className="w-3 h-3 inline" /></button>
        </div>
      )}

      {showPrefs && prefs && (
        <div data-testid="notif-preferences" className="bg-slate-800/60 border border-cyan-500/20 rounded-xl p-5">
          <h3 className="text-white font-semibold text-sm mb-4">Notification Preferences</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 text-sm">Email Notifications</span>
              <button onClick={() => updatePref("email_enabled", !prefs.email_enabled)} className={`w-10 h-5 rounded-full transition-colors ${prefs.email_enabled ? "bg-cyan-500" : "bg-slate-600"}`}>
                <div className={`w-4 h-4 bg-white rounded-full transition-transform ${prefs.email_enabled ? "translate-x-5" : "translate-x-0.5"}`} />
              </button>
            </div>
            <div className="text-slate-400 text-xs">Recipient: {prefs.email_recipient || "Not set"}</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {Object.entries(prefs.email_types || {}).map(([type, enabled]) => (
                <button key={type} onClick={() => toggleEmailType(type)} className={`px-3 py-2 rounded-lg text-xs transition-colors ${enabled ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30" : "bg-slate-700/50 text-slate-500 border border-slate-600/30"}`}>
                  {NOTIF_TYPE_LABELS[type] || type}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center gap-3 flex-wrap">
        <select data-testid="notif-type-filter" value={filter} onChange={(e) => { setFilter(e.target.value); setPage(1); }} className="bg-slate-800 border border-slate-700 text-slate-300 text-sm rounded-lg px-3 py-2">
          <option value="">All Types</option>
          {Object.entries(NOTIF_TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
        <button data-testid="notif-unread-toggle" onClick={() => { setUnreadOnly(!unreadOnly); setPage(1); }} className={`px-3 py-2 rounded-lg text-sm transition-colors ${unreadOnly ? "bg-cyan-500/20 text-cyan-400" : "bg-slate-700 text-slate-400 hover:text-white"}`}>
          {unreadOnly ? "Unread Only" : "All"}
        </button>
        {unreadCount > 0 && (
          <button data-testid="mark-all-read-btn" onClick={markAllRead} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition-colors">
            Mark All Read ({unreadCount})
          </button>
        )}
        <span className="text-xs text-slate-500 ml-auto">{total} notification{total !== 1 ? "s" : ""}</span>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />Loading...</div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <Bell className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="text-sm">No notifications yet</p>
          <p className="text-xs text-slate-600 mt-1">Run an SLA check or create CVEs to generate notifications</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => {
            const Icon = NOTIF_TYPE_ICONS[n.type] || Bell;
            return (
              <div key={n.id} data-testid={`notification-${n.id}`} className={`flex items-start gap-3 p-4 rounded-xl border transition-colors ${n.read ? "bg-slate-800/30 border-slate-700/30" : "bg-slate-800/60 border-slate-600/50"}`}>
                <div className={`p-2 rounded-lg ${n.read ? "bg-slate-700/30" : "bg-slate-700/60"}`}>
                  <Icon className={`w-4 h-4 ${n.read ? "text-slate-500" : "text-cyan-400"}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {!n.read && <div className="w-2 h-2 rounded-full bg-cyan-400 flex-shrink-0" />}
                    <span className={`text-sm font-medium ${n.read ? "text-slate-400" : "text-white"}`}>{n.title}</span>
                    <span className={`w-2 h-2 rounded-full flex-shrink-0 ${NOTIF_SEVERITY_DOT[n.severity] || "bg-slate-500"}`} />
                    <span className="text-xs text-slate-500 ml-auto flex-shrink-0">{new Date(n.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2">{n.message}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-700/50 text-slate-400">{NOTIF_TYPE_LABELS[n.type] || n.type}</span>
                    {n.cve_id && <span className="text-xs text-cyan-400/70">{n.cve_id}</span>}
                    {n.email_sent && <span className="text-xs text-emerald-400/60 flex items-center gap-1"><Mail className="w-3 h-3" />Emailed</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  {!n.read && (
                    <button onClick={() => markRead(n.id)} className="p-1.5 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors" title="Mark read">
                      <Eye className="w-3.5 h-3.5" />
                    </button>
                  )}
                  <button onClick={() => dismiss(n.id)} className="p-1.5 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-colors" title="Dismiss">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm disabled:opacity-40">Prev</button>
          <span className="text-xs text-slate-400">Page {page} of {pages}</span>
          <button disabled={page >= pages} onClick={() => setPage(page + 1)} className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm disabled:opacity-40">Next</button>
        </div>
      )}
    </div>
  );
};
