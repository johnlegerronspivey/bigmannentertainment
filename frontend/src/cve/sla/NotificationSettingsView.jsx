import React, { useState, useEffect } from "react";
import { Mail, Bell, Save, Send, ToggleLeft, ToggleRight, User } from "lucide-react";
import { SLA_API, SEVERITY_COLORS, fetcher } from "../shared";
import { NotificationPreferencesPanel } from "../NotificationPreferencesPanel";

const ToggleBtn = ({ enabled, onToggle, testId }) => (
  <button data-testid={testId} onClick={onToggle} className="text-slate-300">
    {enabled ? <ToggleRight className="w-8 h-8 text-emerald-400" /> : <ToggleLeft className="w-8 h-8 text-slate-500" />}
  </button>
);

function getCurrentUserId() {
  try {
    const token = localStorage.getItem("token");
    if (!token) return null;
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.sub || null;
  } catch { return null; }
}

export const NotificationSettingsView = ({ autoConfig, notifPrefs, fetchAll }) => {
  const [config, setConfig] = useState(null);
  const [prefs, setPrefs] = useState(null);
  const [saving, setSaving] = useState("");
  const [digestResult, setDigestResult] = useState(null);
  const [newRecipient, setNewRecipient] = useState("");

  useEffect(() => {
    if (autoConfig) setConfig({ ...autoConfig });
    if (notifPrefs) setPrefs({ ...notifPrefs });
  }, [autoConfig, notifPrefs]);

  if (!config || !prefs) return null;

  const saveAutoConfig = async () => {
    setSaving("config");
    try {
      await fetcher(`${SLA_API}/auto-escalation-config`, { method: "PUT", body: JSON.stringify(config) });
      fetchAll();
    } catch (e) { console.error(e); }
    setSaving("");
  };

  const savePrefs = async () => {
    setSaving("prefs");
    try {
      await fetcher(`${SLA_API}/notification-preferences`, { method: "PUT", body: JSON.stringify(prefs) });
      fetchAll();
    } catch (e) { console.error(e); }
    setSaving("");
  };

  const sendDigest = async () => {
    setSaving("digest");
    try {
      const result = await fetcher(`${SLA_API}/send-digest`, { method: "POST" });
      setDigestResult(result);
    } catch (e) { console.error(e); }
    setSaving("");
  };

  const addRecipient = () => {
    if (!newRecipient.trim() || config.recipients.includes(newRecipient.trim())) return;
    setConfig({ ...config, recipients: [...config.recipients, newRecipient.trim()] });
    setNewRecipient("");
  };

  const removeRecipient = (email) => {
    setConfig({ ...config, recipients: config.recipients.filter((r) => r !== email) });
  };

  return (
    <div className="space-y-6">
      {/* Auto-Escalation Settings */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-white font-semibold text-sm">Auto-Escalation</h3>
            <p className="text-xs text-slate-400 mt-0.5">Automatically check and escalate at-risk CVEs on a schedule</p>
          </div>
          <ToggleBtn testId="auto-escalation-toggle" enabled={config.enabled} onToggle={() => setConfig({ ...config, enabled: !config.enabled })} />
        </div>
        <div className="grid md:grid-cols-2 gap-4 mb-5">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Check Interval (minutes)</label>
            <input data-testid="interval-input" type="number" min="5" max="1440" className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={config.interval_minutes} onChange={(e) => setConfig({ ...config, interval_minutes: parseInt(e.target.value) || 60 })} />
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Digest Time (UTC hour)</label>
            <input data-testid="digest-hour-input" type="number" min="0" max="23" className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={config.digest_cron_hour} onChange={(e) => setConfig({ ...config, digest_cron_hour: parseInt(e.target.value) || 8 })} />
          </div>
        </div>
        <div className="space-y-3 mb-5">
          {[
            { key: "email_on_warning", label: "Email on SLA Warning (75%+)" },
            { key: "email_on_breach", label: "Email on SLA Breach (100%+)" },
            { key: "email_on_escalation", label: "Email on Escalation Trigger" },
            { key: "digest_enabled", label: "Daily SLA Digest Email" },
          ].map(({ key, label }) => (
            <div key={key} className="flex items-center justify-between py-1">
              <span className="text-sm text-slate-300">{label}</span>
              <ToggleBtn testId={`toggle-${key}`} enabled={config[key]} onToggle={() => setConfig({ ...config, [key]: !config[key] })} />
            </div>
          ))}
        </div>
        <div className="mb-5">
          <label className="text-xs text-slate-400 block mb-2">Email Recipients</label>
          <div className="flex gap-2 mb-2">
            <input data-testid="recipient-input" className="flex-1 bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" placeholder="email@example.com" value={newRecipient} onChange={(e) => setNewRecipient(e.target.value)} onKeyDown={(e) => e.key === "Enter" && addRecipient()} />
            <button data-testid="add-recipient-btn" onClick={addRecipient} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs">Add</button>
          </div>
          <div className="flex flex-wrap gap-2">
            {(config.recipients || []).map((r) => (
              <span key={r} data-testid={`recipient-${r}`} className="flex items-center gap-1.5 px-2.5 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-xs text-cyan-300">
                <Mail className="w-3 h-3" /> {r}
                <button onClick={() => removeRecipient(r)} className="text-red-400 hover:text-red-300 ml-1">&times;</button>
              </span>
            ))}
            {(config.recipients || []).length === 0 && <span className="text-xs text-slate-500">No recipients added</span>}
          </div>
        </div>
        <button data-testid="save-auto-config-btn" onClick={saveAutoConfig} disabled={saving === "config"} className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">
          <Save className="w-4 h-4" /> {saving === "config" ? "Saving..." : "Save Auto-Escalation Settings"}
        </button>
      </div>

      {/* Per-Severity Notification Preferences */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-6">
        <h3 className="text-white font-semibold text-sm mb-1">Per-Severity Notification Preferences</h3>
        <p className="text-xs text-slate-400 mb-5">Configure which severities send email vs in-app notifications</p>
        <div className="space-y-3">
          {["critical", "high", "medium", "low"].map((sev) => {
            const c = SEVERITY_COLORS[sev] || SEVERITY_COLORS.info;
            const sp = prefs.per_severity?.[sev] || { email: false, in_app: true };
            const updateSev = (field) => setPrefs({
              ...prefs,
              per_severity: { ...prefs.per_severity, [sev]: { ...sp, [field]: !sp[field] } },
            });
            return (
              <div key={sev} data-testid={`notif-pref-${sev}`} className={`flex items-center justify-between p-3 rounded-lg ${c.bg} border ${c.border}`}>
                <span className={`${c.text} font-semibold text-sm uppercase`}>{sev}</span>
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                    <Mail className="w-3.5 h-3.5" /> Email
                    <ToggleBtn testId={`toggle-${sev}-email`} enabled={sp.email} onToggle={() => updateSev("email")} />
                  </label>
                  <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                    <Bell className="w-3.5 h-3.5" /> In-App
                    <ToggleBtn testId={`toggle-${sev}-inapp`} enabled={sp.in_app} onToggle={() => updateSev("in_app")} />
                  </label>
                </div>
              </div>
            );
          })}
        </div>
        <button data-testid="save-notif-prefs-btn" onClick={savePrefs} disabled={saving === "prefs"} className="flex items-center gap-2 px-4 py-2 mt-5 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">
          <Save className="w-4 h-4" /> {saving === "prefs" ? "Saving..." : "Save Global Preferences"}
        </button>
      </div>

      {/* Per-User WebSocket Notification Preferences */}
      <NotificationPreferencesPanel userId={getCurrentUserId()} />

      {/* SLA Digest */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold text-sm">SLA Digest</h3>
            <p className="text-xs text-slate-400 mt-0.5">Send a summary of SLA compliance status to recipients</p>
          </div>
          <button data-testid="send-digest-btn" onClick={sendDigest} disabled={saving === "digest"} className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">
            <Send className="w-4 h-4" /> {saving === "digest" ? "Sending..." : "Send Digest Now"}
          </button>
        </div>
        {digestResult && (
          <div data-testid="digest-result" className={`mt-4 p-4 rounded-lg border ${digestResult.sent ? "bg-emerald-900/20 border-emerald-500/30" : "bg-amber-900/20 border-amber-500/30"}`}>
            <p className="text-sm text-white font-medium">{digestResult.sent ? "Digest sent successfully" : "Digest not sent"}</p>
            <p className="text-xs text-slate-400 mt-1">
              {digestResult.sent
                ? `Sent to ${digestResult.recipients} recipient(s) — ${digestResult.compliance}% compliance, ${digestResult.total_open} open, ${digestResult.total_breached} breached`
                : digestResult.reason || "Check recipients configuration"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
