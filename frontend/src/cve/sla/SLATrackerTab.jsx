import React, { useState, useEffect, useCallback } from "react";
import { Shield, AlertTriangle, TrendingUp, Loader2, Play, Zap, CheckCircle2, Bell, BarChart3, Users, Settings, Calendar } from "lucide-react";
import { SLA_API, fetcher } from "../shared";
import { DashboardView } from "./DashboardView";
import { AtRiskView } from "./AtRiskView";
import { EscalationRulesView } from "./EscalationRulesView";
import { EscalationWorkflowView } from "./EscalationWorkflowView";
import { NotificationSettingsView } from "./NotificationSettingsView";
import { TrendsView } from "./TrendsView";
import { MetricsView } from "./MetricsView";
import { TeamPerformanceView } from "./TeamPerformanceView";
import { PoliciesView } from "./PoliciesView";
import { BreachTimelineView } from "./BreachTimelineView";

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
  const [metrics, setMetrics] = useState(null);
  const [teamData, setTeamData] = useState(null);
  const [policies, setPolicies] = useState(null);
  const [breachTimeline, setBreachTimeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [escalationResult, setEscalationResult] = useState(null);
  const [editRules, setEditRules] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [d, ar, r, h, el, es, ac, np, m, tp, pol, bt] = await Promise.all([
        fetcher(`${SLA_API}/dashboard`),
        fetcher(`${SLA_API}/at-risk?limit=50`),
        fetcher(`${SLA_API}/escalation-rules`),
        fetcher(`${SLA_API}/history?days=30`),
        fetcher(`${SLA_API}/escalation-log?limit=50`),
        fetcher(`${SLA_API}/escalation-stats`),
        fetcher(`${SLA_API}/auto-escalation-config`),
        fetcher(`${SLA_API}/notification-preferences`),
        fetcher(`${SLA_API}/metrics`),
        fetcher(`${SLA_API}/team-performance`),
        fetcher(`${SLA_API}/policies`),
        fetcher(`${SLA_API}/breach-timeline?days=30`),
      ]);
      setDashboard(d); setAtRisk(ar); setRules(r); setHistory(h);
      setEscLog(el); setEscStats(es); setAutoConfig(ac); setNotifPrefs(np);
      setMetrics(m); setTeamData(tp); setPolicies(pol); setBreachTimeline(bt);
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
    { id: "dashboard", label: "Overview", icon: Shield },
    { id: "metrics", label: "Metrics & MTTR", icon: BarChart3 },
    { id: "at-risk", label: "At-Risk CVEs", icon: AlertTriangle },
    { id: "breach-timeline", label: "Breach Timeline", icon: Calendar },
    { id: "team", label: "Team Performance", icon: Users },
    { id: "escalations", label: "Escalation Rules", icon: Zap },
    { id: "workflow", label: "Workflow", icon: CheckCircle2 },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "trends", label: "Trends", icon: TrendingUp },
    { id: "policies", label: "SLA Policies", icon: Settings },
  ];

  return (
    <div data-testid="sla-tracker-tab" className="space-y-6">
      <div className="flex items-center gap-1.5 border-b border-slate-700/50 pb-2 overflow-x-auto">
        {views.map((v) => (
          <button key={v.id} data-testid={`sla-view-${v.id}`} onClick={() => setView(v.id)} className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs transition-all whitespace-nowrap ${view === v.id ? "bg-orange-500/10 text-orange-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <v.icon className="w-3.5 h-3.5" /> {v.label}
          </button>
        ))}
        <div className="flex-1" />
        <button data-testid="run-escalations-btn" onClick={runEscalations} disabled={actionLoading === "escalate"} className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-xs transition-colors disabled:opacity-50 whitespace-nowrap">
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

      {view === "dashboard" && <DashboardView dashboard={dashboard} metrics={metrics} />}
      {view === "metrics" && <MetricsView metrics={metrics} />}
      {view === "at-risk" && <AtRiskView atRisk={atRisk} />}
      {view === "breach-timeline" && <BreachTimelineView breachTimeline={breachTimeline} />}
      {view === "team" && <TeamPerformanceView teamData={teamData} />}
      {view === "escalations" && <EscalationRulesView rules={rules} editRules={editRules} setEditRules={setEditRules} setRules={setRules} onRefresh={fetchAll} />}
      {view === "workflow" && <EscalationWorkflowView escLog={escLog} escStats={escStats} fetchAll={fetchAll} />}
      {view === "notifications" && <NotificationSettingsView autoConfig={autoConfig} notifPrefs={notifPrefs} fetchAll={fetchAll} />}
      {view === "trends" && <TrendsView history={history} />}
      {view === "policies" && <PoliciesView policies={policies} fetchAll={fetchAll} />}
    </div>
  );
};
