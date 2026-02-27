import React, { useState, useEffect, useCallback } from "react";
import { Shield, AlertTriangle, TrendingUp, Loader2, Play, Zap, CheckCircle2, Bell } from "lucide-react";
import { SLA_API, fetcher } from "../shared";
import { DashboardView } from "./DashboardView";
import { AtRiskView } from "./AtRiskView";
import { EscalationRulesView } from "./EscalationRulesView";
import { EscalationWorkflowView } from "./EscalationWorkflowView";
import { NotificationSettingsView } from "./NotificationSettingsView";
import { TrendsView } from "./TrendsView";

export const SLATrackerTab = ({ onRefresh }) => {
  const [view, setView] = useState("dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [atRisk, setAtRisk] = useState(null);
  const [rules, setRules] = useState(null);
  const [history, setHistory] = useState(null);
  const [escLog, setEscLog] = useState(null);
  const [escStats, setEscStats] = useState(null);
  const [autoConfig, setAutoConfig] = useState(null);
  const [notifPrefs, setNotifPrefs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [escalationResult, setEscalationResult] = useState(null);
  const [editRules, setEditRules] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [d, ar, r, h, el, es, ac, np] = await Promise.all([
        fetcher(`${SLA_API}/dashboard`),
        fetcher(`${SLA_API}/at-risk?limit=50`),
        fetcher(`${SLA_API}/escalation-rules`),
        fetcher(`${SLA_API}/history?days=30`),
        fetcher(`${SLA_API}/escalation-log?limit=50`),
        fetcher(`${SLA_API}/escalation-stats`),
        fetcher(`${SLA_API}/auto-escalation-config`),
        fetcher(`${SLA_API}/notification-preferences`),
      ]);
      setDashboard(d); setAtRisk(ar); setRules(r); setHistory(h);
      setEscLog(el); setEscStats(es); setAutoConfig(ac); setNotifPrefs(np);
    } catch (e) { console.error("SLA fetch error:", e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const runEscalations = async () => {
    setActionLoading("escalate");
    try {
      const result = await fetcher(`${SLA_API}/run-escalations`, { method: "POST" });
      setEscalationResult(result);
      fetchAll();
      onRefresh();
    } catch (e) { console.error(e); }
    setActionLoading("");
  };

  if (loading || !dashboard) {
    return (
      <div className="text-center py-16 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3" />Loading SLA tracking data...
      </div>
    );
  }

  const views = [
    { id: "dashboard", label: "SLA Dashboard", icon: Shield },
    { id: "at-risk", label: "At-Risk CVEs", icon: AlertTriangle },
    { id: "escalations", label: "Escalation Rules", icon: Zap },
    { id: "workflow", label: "Escalation Workflow", icon: CheckCircle2 },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "trends", label: "SLA Trends", icon: TrendingUp },
  ];

  return (
    <div data-testid="sla-tracker-tab" className="space-y-6">
      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2 overflow-x-auto">
        {views.map((v) => (
          <button key={v.id} data-testid={`sla-view-${v.id}`} onClick={() => setView(v.id)} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all whitespace-nowrap ${view === v.id ? "bg-orange-500/10 text-orange-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <v.icon className="w-4 h-4" /> {v.label}
          </button>
        ))}
        <div className="flex-1" />
        <button data-testid="run-escalations-btn" onClick={runEscalations} disabled={actionLoading === "escalate"} className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50 whitespace-nowrap">
          {actionLoading === "escalate" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          Run Escalations
        </button>
      </div>

      {escalationResult && (
        <div data-testid="escalation-result" className="bg-slate-800/60 border border-orange-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <span className="text-white text-sm font-medium">Escalation Check Complete{escalationResult.email_sent ? " (Email sent)" : ""}</span>
            <button onClick={() => setEscalationResult(null)} className="text-slate-400 hover:text-white text-xs">Dismiss</button>
          </div>
          <div className="grid grid-cols-3 gap-3 mt-3 text-center">
            <div className="bg-slate-700/40 rounded-lg p-2">
              <div className="text-lg font-bold text-white">{escalationResult.checked}</div>
              <div className="text-xs text-slate-400">Checked</div>
            </div>
            <div className="bg-orange-500/10 rounded-lg p-2">
              <div className="text-lg font-bold text-orange-400">{escalationResult.escalations_created}</div>
              <div className="text-xs text-slate-400">Escalated</div>
            </div>
            <div className="bg-slate-700/40 rounded-lg p-2">
              <div className="text-lg font-bold text-cyan-400">{escalationResult.rules_applied}</div>
              <div className="text-xs text-slate-400">Rules Applied</div>
            </div>
          </div>
        </div>
      )}

      {view === "dashboard" && <DashboardView dashboard={dashboard} />}
      {view === "at-risk" && <AtRiskView atRisk={atRisk} />}
      {view === "escalations" && <EscalationRulesView rules={rules} editRules={editRules} setEditRules={setEditRules} setRules={setRules} onRefresh={fetchAll} />}
      {view === "workflow" && <EscalationWorkflowView escLog={escLog} escStats={escStats} fetchAll={fetchAll} />}
      {view === "notifications" && <NotificationSettingsView autoConfig={autoConfig} notifPrefs={notifPrefs} fetchAll={fetchAll} />}
      {view === "trends" && <TrendsView history={history} />}
    </div>
  );
};
