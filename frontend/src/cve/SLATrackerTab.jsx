import React, { useState, useEffect, useCallback } from "react";
import {
  Timer, AlertTriangle, Shield, TrendingUp, ChevronUp, ChevronDown,
  Loader2, Play, Settings, Clock, Zap, ArrowUpRight, Users,
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell,
} from "recharts";
import { SLA_API, SEVERITY_COLORS, fetcher, SeverityBadge, StatCard } from "./shared";

const CHART_COLORS = ["#ef4444", "#f97316", "#eab308", "#3b82f6"];

const SLAStatusBadge = ({ status }) => {
  const styles = {
    breached: "bg-red-500/20 text-red-300 border-red-500/30",
    warning: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    approaching: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  };
  return (
    <span data-testid={`sla-badge-${status}`} className={`px-2 py-0.5 rounded text-xs font-medium border ${styles[status] || styles.approaching}`}>
      {status.toUpperCase()}
    </span>
  );
};

const CountdownTimer = ({ remainingHours, percentElapsed }) => {
  const isOverdue = remainingHours <= 0;
  const absHours = Math.abs(remainingHours);
  const days = Math.floor(absHours / 24);
  const hours = Math.floor(absHours % 24);

  const barPct = Math.min(percentElapsed, 200);
  const barColor =
    percentElapsed >= 100 ? "bg-red-500" : percentElapsed >= 75 ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div data-testid="countdown-timer" className="flex items-center gap-3 min-w-[180px]">
      <div className="flex-1">
        <div className="w-full bg-slate-700/50 rounded-full h-1.5 mb-1">
          <div
            className={`h-1.5 rounded-full transition-all ${barColor}`}
            style={{ width: `${Math.min(barPct / 2, 100)}%` }}
          />
        </div>
        <div className={`text-xs font-mono ${isOverdue ? "text-red-400" : "text-slate-300"}`}>
          {isOverdue ? "+" : ""}
          {days > 0 ? `${days}d ` : ""}
          {hours}h {isOverdue ? "overdue" : "left"}
        </div>
      </div>
    </div>
  );
};

const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 shadow-xl">
      <p className="text-slate-300 text-xs mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-xs" style={{ color: p.color }}>
          {p.name}: <span className="font-semibold">{p.value}</span>
        </p>
      ))}
    </div>
  );
};

export const SLATrackerTab = ({ onRefresh }) => {
  const [view, setView] = useState("dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [atRisk, setAtRisk] = useState(null);
  const [rules, setRules] = useState(null);
  const [history, setHistory] = useState(null);
  const [escLog, setEscLog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [escalationResult, setEscalationResult] = useState(null);
  const [editRules, setEditRules] = useState(null);
  const [savingRules, setSavingRules] = useState(false);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [d, ar, r, h, el] = await Promise.all([
        fetcher(`${SLA_API}/dashboard`),
        fetcher(`${SLA_API}/at-risk?limit=50`),
        fetcher(`${SLA_API}/escalation-rules`),
        fetcher(`${SLA_API}/history?days=30`),
        fetcher(`${SLA_API}/escalation-log?limit=30`),
      ]);
      setDashboard(d);
      setAtRisk(ar);
      setRules(r);
      setHistory(h);
      setEscLog(el);
    } catch (e) {
      console.error("SLA fetch error:", e);
    }
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

  const saveRules = async () => {
    if (!editRules) return;
    setSavingRules(true);
    try {
      const result = await fetcher(`${SLA_API}/escalation-rules`, {
        method: "PUT",
        body: JSON.stringify({ rules: editRules }),
      });
      setRules(result);
      setEditRules(null);
    } catch (e) { console.error(e); }
    setSavingRules(false);
  };

  const addRule = () => {
    const current = editRules || rules?.rules || [];
    const nextLevel = current.length > 0 ? Math.max(...current.map((r) => r.level)) + 1 : 1;
    setEditRules([
      ...current,
      { level: nextLevel, name: `L${nextLevel} Escalation`, threshold_pct: nextLevel * 50 + 50, action: "escalate", notify_role: "admin", description: "" },
    ]);
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

  if (loading || !dashboard) {
    return (
      <div className="text-center py-16 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3" />
        Loading SLA tracking data...
      </div>
    );
  }

  const historyData = (history?.history || []).filter(
    (_, i, arr) => arr.length <= 15 || i % Math.ceil(arr.length / 15) === 0 || i === arr.length - 1
  );

  const sevBarData = Object.entries(dashboard.severity_stats || {}).map(([sev, d]) => ({
    severity: sev.charAt(0).toUpperCase() + sev.slice(1),
    "Within SLA": d.within_sla,
    Warning: d.warning,
    Breached: d.breached,
  }));

  const currentRules = editRules || rules?.rules || [];

  return (
    <div data-testid="sla-tracker-tab" className="space-y-6">
      {/* Sub-navigation */}
      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2">
        {[
          { id: "dashboard", label: "SLA Dashboard", icon: Shield },
          { id: "at-risk", label: "At-Risk CVEs", icon: AlertTriangle },
          { id: "escalations", label: "Escalation Rules", icon: Zap },
          { id: "trends", label: "SLA Trends", icon: TrendingUp },
        ].map((v) => (
          <button
            key={v.id}
            data-testid={`sla-view-${v.id}`}
            onClick={() => setView(v.id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
              view === v.id
                ? "bg-orange-500/10 text-orange-400 font-medium"
                : "text-slate-400 hover:text-white hover:bg-slate-800/50"
            }`}
          >
            <v.icon className="w-4 h-4" /> {v.label}
          </button>
        ))}
        <div className="flex-1" />
        <button
          data-testid="run-escalations-btn"
          onClick={runEscalations}
          disabled={actionLoading === "escalate"}
          className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          {actionLoading === "escalate" ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          Run Escalations
        </button>
      </div>

      {escalationResult && (
        <div data-testid="escalation-result" className="bg-slate-800/60 border border-orange-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <span className="text-white text-sm font-medium">Escalation Check Complete</span>
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

      {/* Dashboard View */}
      {view === "dashboard" && (
        <div className="space-y-6">
          {/* Overall health banner */}
          <div
            className={`border rounded-xl p-6 ${
              dashboard.overall_compliance >= 90
                ? "bg-emerald-900/20 border-emerald-500/30"
                : dashboard.overall_compliance >= 70
                ? "bg-amber-900/20 border-amber-500/30"
                : "bg-red-900/20 border-red-500/30"
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-white font-semibold text-lg">SLA Compliance Health</h3>
                <p className="text-sm text-slate-400 mt-1">
                  {dashboard.total_open} open CVEs — {dashboard.total_breached} breached, {dashboard.total_warning} warning
                </p>
              </div>
              <div data-testid="sla-overall-compliance" className="text-right">
                <div
                  className={`text-5xl font-bold ${
                    dashboard.overall_compliance >= 90
                      ? "text-emerald-400"
                      : dashboard.overall_compliance >= 70
                      ? "text-amber-400"
                      : "text-red-400"
                  }`}
                >
                  {dashboard.overall_compliance}%
                </div>
                <div className="text-xs text-slate-400 mt-1">Overall Compliance</div>
              </div>
            </div>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard icon={Shield} label="Total Open" value={dashboard.total_open} color="text-white" />
            <StatCard icon={Timer} label="Within SLA" value={dashboard.total_within_sla} color="text-emerald-400" />
            <StatCard icon={Clock} label="Warning" value={dashboard.total_warning} color="text-amber-400" />
            <StatCard icon={AlertTriangle} label="Breached" value={dashboard.total_breached} color="text-red-400" />
          </div>

          {/* Per-severity cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(dashboard.severity_stats || {}).map(([sev, d]) => {
              const c = SEVERITY_COLORS[sev] || SEVERITY_COLORS.info;
              const pct = d.compliance_pct;
              return (
                <div key={sev} data-testid={`sla-sev-${sev}`} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className={`${c.text} font-semibold text-sm uppercase`}>{sev}</h4>
                    <span
                      className={`text-xl font-bold ${
                        pct >= 90 ? "text-emerald-400" : pct >= 70 ? "text-amber-400" : "text-red-400"
                      }`}
                    >
                      {pct}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2 mb-3">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        pct >= 90 ? "bg-emerald-500" : pct >= 70 ? "bg-amber-500" : "bg-red-500"
                      }`}
                      style={{ width: `${Math.min(pct, 100)}%` }}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-slate-400">SLA:</span>{" "}
                      <span className="text-white">{d.sla_hours}h</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Total:</span>{" "}
                      <span className="text-white">{d.total}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Breached:</span>{" "}
                      <span className={d.breached > 0 ? "text-red-400" : "text-emerald-400"}>{d.breached}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Warning:</span>{" "}
                      <span className={d.warning > 0 ? "text-amber-400" : "text-emerald-400"}>{d.warning}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Severity breakdown chart */}
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">SLA Status by Severity</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={sevBarData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="severity" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Bar dataKey="Within SLA" fill="#10b981" stackId="a" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Warning" fill="#f59e0b" stackId="a" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Breached" fill="#ef4444" stackId="a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* At-Risk CVEs View */}
      {view === "at-risk" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-white font-semibold text-sm">
              At-Risk CVEs <span className="text-slate-400 font-normal ml-1">({atRisk?.total || 0} total)</span>
            </h3>
          </div>

          {(atRisk?.items || []).length === 0 ? (
            <div className="text-center py-16 text-slate-500">
              <Shield className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm">All CVEs are within SLA</p>
              <p className="text-xs text-slate-600 mt-1">No vulnerabilities are currently approaching or breaching SLA targets</p>
            </div>
          ) : (
            <div className="space-y-2">
              {(atRisk?.items || []).map((item) => (
                <div
                  key={item.cve_id}
                  data-testid={`at-risk-${item.cve_id}`}
                  className={`flex items-center gap-4 p-4 rounded-xl border transition-colors ${
                    item.sla_status === "breached"
                      ? "bg-red-900/10 border-red-500/30"
                      : item.sla_status === "warning"
                      ? "bg-amber-900/10 border-amber-500/30"
                      : "bg-slate-800/60 border-slate-700/50"
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-cyan-400 font-mono text-xs">{item.cve_id}</span>
                      <SeverityBadge severity={item.severity} />
                      <SLAStatusBadge status={item.sla_status} />
                      {item.escalation_level > 0 && (
                        <span className="px-2 py-0.5 rounded text-xs bg-orange-500/20 text-orange-300 border border-orange-500/30">
                          <ArrowUpRight className="w-3 h-3 inline mr-0.5" />
                          L{item.escalation_level}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-slate-300 truncate">{item.title}</p>
                    <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                      {item.assigned_to && (
                        <span className="flex items-center gap-1">
                          <Users className="w-3 h-3" /> {item.assigned_to}
                        </span>
                      )}
                      <span>SLA: {item.sla_hours}h</span>
                      <span>{item.percent_elapsed.toFixed(0)}% elapsed</span>
                    </div>
                  </div>
                  <CountdownTimer remainingHours={item.remaining_hours > 0 ? item.remaining_hours : -item.overdue_hours} percentElapsed={item.percent_elapsed} />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Escalation Rules View */}
      {view === "escalations" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-white font-semibold text-sm">Escalation Rules</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Define how CVEs are escalated when SLA thresholds are breached
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button data-testid="add-rule-btn" onClick={addRule} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors">
                + Add Rule
              </button>
              {editRules && (
                <>
                  <button onClick={() => setEditRules(null)} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-400 rounded-lg text-xs transition-colors">
                    Cancel
                  </button>
                  <button
                    data-testid="save-rules-btn"
                    onClick={saveRules}
                    disabled={savingRules}
                    className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-xs transition-colors disabled:opacity-50"
                  >
                    {savingRules ? "Saving..." : "Save Rules"}
                  </button>
                </>
              )}
            </div>
          </div>

          <div className="space-y-3">
            {currentRules.map((rule, idx) => (
              <div
                key={rule.id || idx}
                data-testid={`escalation-rule-${idx}`}
                className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5"
              >
                <div className="grid md:grid-cols-5 gap-4 items-end">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Level</label>
                    <input
                      type="number"
                      min="1"
                      className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
                      value={rule.level}
                      onChange={(e) => updateRule(idx, "level", e.target.value)}
                      disabled={!editRules}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="text-xs text-slate-400 block mb-1">Name</label>
                    <input
                      className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
                      value={rule.name}
                      onChange={(e) => updateRule(idx, "name", e.target.value)}
                      disabled={!editRules}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">Threshold %</label>
                    <input
                      type="number"
                      min="1"
                      className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
                      value={rule.threshold_pct}
                      onChange={(e) => updateRule(idx, "threshold_pct", e.target.value)}
                      disabled={!editRules}
                    />
                  </div>
                  <div className="flex items-end gap-2">
                    <div className="flex-1">
                      <label className="text-xs text-slate-400 block mb-1">Action</label>
                      <select
                        className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm"
                        value={rule.action}
                        onChange={(e) => updateRule(idx, "action", e.target.value)}
                        disabled={!editRules}
                      >
                        <option value="notify">Notify</option>
                        <option value="escalate">Escalate</option>
                      </select>
                    </div>
                    {editRules && (
                      <button
                        onClick={() => removeRule(idx)}
                        className="px-2 py-2 text-red-400 hover:bg-red-500/10 rounded-lg text-xs transition-colors"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                </div>
                {rule.description && (
                  <p className="text-xs text-slate-500 mt-2">{rule.description}</p>
                )}
              </div>
            ))}
          </div>

          {/* Escalation Log */}
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">
              Recent Escalations <span className="text-slate-400 font-normal ml-1">({escLog?.total || 0} total)</span>
            </h3>
            {(escLog?.items || []).length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-6">No escalations triggered yet. Run escalations to check at-risk CVEs.</p>
            ) : (
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {(escLog?.items || []).map((e) => (
                  <div
                    key={e.id}
                    data-testid={`esc-log-${e.id}`}
                    className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-3 py-2"
                  >
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        e.level >= 3
                          ? "bg-red-500/20 text-red-300"
                          : e.level >= 2
                          ? "bg-orange-500/20 text-orange-300"
                          : "bg-amber-500/20 text-amber-300"
                      }`}
                    >
                      L{e.level}
                    </span>
                    <span className="text-cyan-400 font-mono text-xs">{e.cve_id}</span>
                    <SeverityBadge severity={e.severity} />
                    <span className="text-xs text-slate-400 truncate flex-1">{e.rule_name}</span>
                    <span className="text-xs text-slate-500">{e.actual_pct}%</span>
                    <span className="text-xs text-slate-600">
                      {new Date(e.created_at).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Trends View */}
      {view === "trends" && (
        <div className="space-y-6">
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">SLA Compliance Trend (30 Days)</h3>
            {historyData.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-sm">No historical data available yet</div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={historyData}>
                  <defs>
                    <linearGradient id="gradCompliance" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: "#94a3b8", fontSize: 11 }}
                    label={{ value: "%", angle: -90, position: "insideLeft", fill: "#64748b", fontSize: 11 }}
                  />
                  <Tooltip content={<ChartTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="compliance_pct"
                    name="Compliance %"
                    stroke="#10b981"
                    fill="url(#gradCompliance)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">Open vs Breached CVEs Over Time</h3>
            {historyData.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-sm">No historical data available yet</div>
            ) : (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={historyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
                  <Tooltip content={<ChartTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                  <Bar dataKey="total_open" name="Total Open" fill="#3b82f6" radius={[0, 0, 0, 0]} stackId="a" />
                  <Bar dataKey="breached" name="Breached" fill="#ef4444" radius={[4, 4, 0, 0]} stackId="a" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
