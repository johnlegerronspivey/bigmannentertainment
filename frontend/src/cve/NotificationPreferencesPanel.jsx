import React, { useState, useEffect, useCallback } from "react";
import { Bell, BellOff, Volume2, VolumeX, Clock, Save, Loader2 } from "lucide-react";
import { fetcher } from "./shared";

const API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/sla`;

const SEVERITIES = ["critical", "high", "medium", "low"];
const SEV_COLORS = {
  critical: "text-red-400",
  high: "text-orange-400",
  medium: "text-yellow-400",
  low: "text-blue-400",
};

export function NotificationPreferencesPanel({ userId }) {
  const [prefs, setPrefs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const fetchPrefs = useCallback(async () => {
    setLoading(true);
    try {
      const params = userId ? `?user_id=${userId}` : "";
      const data = await fetcher(`${API}/notification-preferences${params}`);
      setPrefs(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [userId]);

  useEffect(() => { fetchPrefs(); }, [fetchPrefs]);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      const params = userId ? `?user_id=${userId}` : "";
      const { updated_at, user_id: _, ...body } = prefs;
      await fetcher(`${API}/notification-preferences${params}`, {
        method: "PUT",
        body: JSON.stringify(body),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  const toggleSeverity = (sev, channel) => {
    setPrefs((p) => ({
      ...p,
      per_severity: {
        ...p.per_severity,
        [sev]: {
          ...p.per_severity?.[sev],
          [channel]: !p.per_severity?.[sev]?.[channel],
        },
      },
    }));
  };

  const toggleMuteSeverity = (sev) => {
    setPrefs((p) => {
      const muted = p.muted_severities || [];
      return {
        ...p,
        muted_severities: muted.includes(sev) ? muted.filter((s) => s !== sev) : [...muted, sev],
      };
    });
  };

  if (loading || !prefs) {
    return (
      <div className="text-center py-8 text-slate-400">
        <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" /> Loading preferences...
      </div>
    );
  }

  return (
    <div data-testid="notification-preferences-panel" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold flex items-center gap-2">
          <Bell className="w-4 h-4 text-cyan-400" /> Notification Preferences
        </h3>
        <button
          data-testid="save-notification-prefs-btn"
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
          {saved ? "Saved!" : "Save"}
        </button>
      </div>

      {/* Event type toggles */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { key: "notify_on_warning", label: "Warnings", icon: Volume2 },
          { key: "notify_on_breach", label: "Breaches", icon: Bell },
          { key: "notify_on_escalation", label: "Escalations", icon: Bell },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            data-testid={`toggle-${key}`}
            onClick={() => setPrefs((p) => ({ ...p, [key]: !p[key] }))}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm border transition-all ${
              prefs[key]
                ? "bg-cyan-600/20 border-cyan-500/40 text-cyan-300"
                : "bg-slate-900/50 border-slate-700/30 text-slate-500"
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Quiet hours */}
      <div className="bg-slate-900/50 rounded-lg p-3 space-y-2">
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <Clock className="w-4 h-4 text-slate-400" /> Quiet Hours
          </label>
          <button
            data-testid="toggle-quiet-hours"
            onClick={() => setPrefs((p) => ({ ...p, quiet_hours_enabled: !p.quiet_hours_enabled }))}
            className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
              prefs.quiet_hours_enabled
                ? "bg-cyan-600/30 text-cyan-300"
                : "bg-slate-700/50 text-slate-500"
            }`}
          >
            {prefs.quiet_hours_enabled ? "ON" : "OFF"}
          </button>
        </div>
        {prefs.quiet_hours_enabled && (
          <div className="flex items-center gap-2 text-sm">
            <input
              type="time"
              data-testid="quiet-hours-start"
              value={prefs.quiet_hours_start || "22:00"}
              onChange={(e) => setPrefs((p) => ({ ...p, quiet_hours_start: e.target.value }))}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-white text-xs"
            />
            <span className="text-slate-500">to</span>
            <input
              type="time"
              data-testid="quiet-hours-end"
              value={prefs.quiet_hours_end || "07:00"}
              onChange={(e) => setPrefs((p) => ({ ...p, quiet_hours_end: e.target.value }))}
              className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-white text-xs"
            />
          </div>
        )}
      </div>

      {/* Per-severity channel matrix */}
      <div>
        <h4 className="text-xs text-slate-400 mb-2 uppercase tracking-wider">Per-Severity Channels</h4>
        <div className="space-y-1.5">
          <div className="grid grid-cols-5 gap-2 text-xs text-slate-500 px-1">
            <span>Severity</span>
            <span className="text-center">Email</span>
            <span className="text-center">In-App</span>
            <span className="text-center">WebSocket</span>
            <span className="text-center">Muted</span>
          </div>
          {SEVERITIES.map((sev) => {
            const sevPrefs = prefs.per_severity?.[sev] || {};
            const muted = (prefs.muted_severities || []).includes(sev);
            return (
              <div key={sev} className={`grid grid-cols-5 gap-2 items-center px-1 py-1.5 rounded ${muted ? "opacity-40" : ""}`}>
                <span className={`text-sm font-medium uppercase ${SEV_COLORS[sev]}`}>{sev}</span>
                {["email", "in_app", "ws"].map((ch) => (
                  <button
                    key={ch}
                    data-testid={`toggle-${sev}-${ch}`}
                    onClick={() => toggleSeverity(sev, ch)}
                    disabled={muted}
                    className="flex justify-center"
                  >
                    <div className={`w-8 h-5 rounded-full transition-colors flex items-center ${
                      sevPrefs[ch] && !muted ? "bg-cyan-500 justify-end" : "bg-slate-700 justify-start"
                    }`}>
                      <div className="w-3.5 h-3.5 bg-white rounded-full mx-0.5 shadow-sm" />
                    </div>
                  </button>
                ))}
                <button
                  data-testid={`mute-${sev}`}
                  onClick={() => toggleMuteSeverity(sev)}
                  className="flex justify-center"
                >
                  {muted ? (
                    <BellOff className="w-4 h-4 text-red-400" />
                  ) : (
                    <Bell className="w-4 h-4 text-slate-500 hover:text-slate-300" />
                  )}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
