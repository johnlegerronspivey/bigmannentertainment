import React, { useState, useEffect, useCallback } from "react";
import { AlertTriangle, CheckCircle, CheckCircle2, Target, TrendingUp, Users, Gauge, Loader2 } from "lucide-react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area } from "recharts";
import { API, GOVERNANCE_API, SEVERITY_COLORS, fetcher, StatCard, SeverityBadge } from "./shared";
import { AssignOwnerModal } from "./AssignOwnerModal";

const CHART_COLORS = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"];
const PIE_COLORS = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"];
const STATUS_CHART_COLORS = { detected: "#ef4444", triaged: "#eab308", in_progress: "#3b82f6", fixed: "#10b981", verified: "#22c55e", dismissed: "#64748b", wont_fix: "#475569" };

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 shadow-xl">
      <p className="text-slate-300 text-xs mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-xs" style={{ color: p.color }}>{p.name}: <span className="font-semibold">{p.value}</span></p>
      ))}
    </div>
  );
};

const RiskGauge = ({ score }) => {
  const color = score >= 75 ? "#ef4444" : score >= 50 ? "#f97316" : score >= 25 ? "#eab308" : "#10b981";
  const label = score >= 75 ? "Critical" : score >= 50 ? "High" : score >= 25 ? "Medium" : "Low";
  return (
    <div data-testid="risk-gauge" className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="10" />
          <circle cx="50" cy="50" r="42" fill="none" stroke={color} strokeWidth="10" strokeDasharray={`${score * 2.64} 264`} strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">{score}</span>
          <span className="text-xs" style={{ color }}>{label}</span>
        </div>
      </div>
      <p className="text-xs text-slate-400 mt-2">Risk Score</p>
    </div>
  );
};

export const GovernanceTab = ({ onRefresh }) => {
  const [metrics, setMetrics] = useState(null);
  const [trends, setTrends] = useState(null);
  const [sla, setSla] = useState(null);
  const [ownership, setOwnership] = useState(null);
  const [mttr, setMttr] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("overview");
  const [ownerInfo, setOwnerInfo] = useState(null);
  const [unassigned, setUnassigned] = useState(null);
  const [govAssignTarget, setGovAssignTarget] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [m, t, s, o, mt, ow, ua] = await Promise.all([
        fetcher(`${GOVERNANCE_API}/metrics`),
        fetcher(`${GOVERNANCE_API}/trends?days=30`),
        fetcher(`${GOVERNANCE_API}/sla`),
        fetcher(`${GOVERNANCE_API}/ownership`),
        fetcher(`${GOVERNANCE_API}/mttr`),
        fetcher(`${API}/owners`),
        fetcher(`${API}/unassigned?limit=20`),
      ]);
      setMetrics(m); setTrends(t); setSla(s); setOwnership(o); setMttr(mt); setOwnerInfo(ow); setUnassigned(ua);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  if (loading || !metrics) return (
    <div data-testid="governance-loading" className="space-y-6 animate-pulse">
      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2">
        {[1,2,3,4].map((i) => <div key={i} className="h-9 w-28 bg-slate-800/60 rounded-lg" />)}
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => <div key={i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5"><div className="h-4 bg-slate-700 rounded w-2/3 mb-3" /><div className="h-7 bg-slate-700 rounded w-1/3" /></div>)}
      </div>
      <div className="grid md:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => <div key={i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl h-52" />)}
      </div>
    </div>
  );

  const sevPieData = Object.entries(metrics.severity_distribution || {}).filter(([, v]) => v > 0).map(([k, v], i) => ({ name: k.charAt(0).toUpperCase() + k.slice(1), value: v, fill: CHART_COLORS[i] }));
  const statusPieData = (ownership?.by_status || []).map((s) => ({ name: s.status.replace("_", " "), value: s.count, fill: STATUS_CHART_COLORS[s.status] || "#64748b" }));
  const sourcePieData = (ownership?.by_source || []).map((s, i) => ({ name: s.source, value: s.count, fill: CHART_COLORS[i % CHART_COLORS.length] }));
  const servicesBarData = (metrics.services_affected || []).map((s) => ({ name: s.service.length > 18 ? s.service.slice(0, 18) + "..." : s.service, count: s.count }));
  const mttrBarData = Object.entries(mttr?.mttr || {}).map(([sev, d]) => ({ severity: sev.charAt(0).toUpperCase() + sev.slice(1), hours: d.avg_hours, days: d.avg_days, samples: d.sample_size }));
  const trendData = (trends?.trends || []).filter((_, i, arr) => arr.length <= 15 || i % Math.ceil(arr.length / 15) === 0 || i === arr.length - 1);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2">
        {[
          { id: "overview", label: "Overview", icon: Gauge },
          { id: "trends", label: "Trends", icon: TrendingUp },
          { id: "sla", label: "SLA Compliance", icon: Target },
          { id: "ownership", label: "Ownership", icon: Users },
        ].map((v) => (
          <button key={v.id} data-testid={`gov-view-${v.id}`} onClick={() => setView(v.id)} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${view === v.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <v.icon className="w-4 h-4" /> {v.label}
          </button>
        ))}
      </div>

      {view === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <StatCard icon={AlertTriangle} label="Total CVEs" value={metrics.total_cves} color="text-white" />
            <StatCard icon={AlertTriangle} label="Open" value={metrics.open_cves} color="text-red-400" />
            <StatCard icon={CheckCircle} label="Fixed" value={metrics.fixed_cves} color="text-emerald-400" />
            <StatCard icon={CheckCircle2} label="Verified" value={metrics.verified_cves} color="text-green-400" />
            <StatCard icon={TrendingUp} label="New (30d)" value={metrics.new_last_30_days} color="text-cyan-400" />
            <StatCard icon={Target} label="Fix Rate (30d)" value={`${metrics.fix_rate_30d}%`} color="text-blue-400" />
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 flex flex-col items-center justify-center">
              <h3 className="text-white font-semibold mb-4 text-sm">Risk Assessment</h3>
              <RiskGauge score={metrics.risk_score} />
              <p className="text-xs text-slate-500 mt-3 text-center">Weighted by open critical/high/medium CVEs</p>
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Severity</h3>
              {sevPieData.length === 0 ? (
                <div className="flex items-center justify-center h-40 text-slate-500 text-sm">No open CVEs</div>
              ) : (
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={sevPieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                      {sevPieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">CVEs by Status</h3>
              {statusPieData.length === 0 ? (
                <div className="flex items-center justify-center h-40 text-slate-500 text-sm">No data</div>
              ) : (
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={statusPieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                      {statusPieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Service</h3>
              {servicesBarData.length === 0 ? (
                <div className="flex items-center justify-center h-48 text-slate-500 text-sm">No services affected</div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={servicesBarData} layout="vertical" margin={{ left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <YAxis type="category" dataKey="name" width={120} tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]} barSize={18} name="Open CVEs" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">CVEs by Source</h3>
              {sourcePieData.length === 0 ? (
                <div className="flex items-center justify-center h-48 text-slate-500 text-sm">No data</div>
              ) : (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={sourcePieData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={30} name="CVEs" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">Mean Time to Remediate (MTTR) by Severity</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={mttrBarData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="severity" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} label={{ value: "Hours", angle: -90, position: "insideLeft", fill: "#64748b", fontSize: 11 }} />
                <Tooltip content={({ active, payload, label }) => {
                  if (!active || !payload?.length) return null;
                  const d = payload[0]?.payload;
                  return (
                    <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 shadow-xl">
                      <p className="text-slate-300 text-xs font-medium mb-1">{label}</p>
                      <p className="text-xs text-cyan-400">Avg: {d?.hours || 0}h ({d?.days || 0}d)</p>
                      <p className="text-xs text-slate-400">Samples: {d?.samples || 0}</p>
                    </div>
                  );
                }} />
                <Bar dataKey="hours" name="Avg Hours" radius={[4, 4, 0, 0]} barSize={40}>
                  {mttrBarData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {view === "trends" && (
        <div className="space-y-6">
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">CVE Detection & Resolution Trends (30 Days)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="gradDetected" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradFixed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Area type="monotone" dataKey="detected" name="Detected" stroke="#ef4444" fill="url(#gradDetected)" strokeWidth={2} />
                <Area type="monotone" dataKey="fixed" name="Fixed" stroke="#10b981" fill="url(#gradFixed)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard icon={AlertTriangle} label="New (7d)" value={metrics.new_last_7_days} color="text-red-400" />
            <StatCard icon={AlertTriangle} label="New (30d)" value={metrics.new_last_30_days} color="text-orange-400" />
            <StatCard icon={CheckCircle} label="Fixed (30d)" value={metrics.fixed_last_30_days} color="text-emerald-400" />
            <StatCard icon={Target} label="Fix Rate" value={`${metrics.fix_rate_30d}%`} color="text-cyan-400" />
          </div>
        </div>
      )}

      {view === "sla" && (
        <div className="space-y-6">
          <div className={`border rounded-xl p-5 ${sla?.overall_compliance >= 90 ? "bg-emerald-900/20 border-emerald-500/30" : sla?.overall_compliance >= 70 ? "bg-yellow-900/20 border-yellow-500/30" : "bg-red-900/20 border-red-500/30"}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-white font-semibold">Overall SLA Compliance</h3>
                <p className="text-sm text-slate-400">Percentage of open CVEs within SLA targets</p>
              </div>
              <div data-testid="sla-overall" className={`text-4xl font-bold ${sla?.overall_compliance >= 90 ? "text-emerald-400" : sla?.overall_compliance >= 70 ? "text-yellow-400" : "text-red-400"}`}>
                {sla?.overall_compliance || 0}%
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {(sla?.sla_data || []).map((d) => {
              const c = SEVERITY_COLORS[d.severity] || SEVERITY_COLORS.info;
              const pct = d.compliance_pct;
              return (
                <div key={d.severity} data-testid={`sla-${d.severity}`} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className={`${c.text} font-semibold text-sm uppercase`}>{d.severity}</h4>
                    <span className={`text-xl font-bold ${pct >= 90 ? "text-emerald-400" : pct >= 70 ? "text-yellow-400" : "text-red-400"}`}>{pct}%</span>
                  </div>
                  <div className="w-full bg-slate-700/50 rounded-full h-2 mb-3">
                    <div className={`h-2 rounded-full transition-all ${pct >= 90 ? "bg-emerald-500" : pct >= 70 ? "bg-yellow-500" : "bg-red-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div><span className="text-slate-400">SLA:</span> <span className="text-white">{d.sla_hours}h</span></div>
                    <div><span className="text-slate-400">Open:</span> <span className="text-white">{d.open}</span></div>
                    <div><span className="text-slate-400">Overdue:</span> <span className={d.overdue > 0 ? "text-red-400" : "text-emerald-400"}>{d.overdue}</span></div>
                    <div><span className="text-slate-400">Fixed:</span> <span className="text-emerald-400">{d.fixed_total}</span></div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">SLA Compliance by Severity</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={sla?.sla_data || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="severity" tick={{ fill: "#94a3b8", fontSize: 12 }} tickFormatter={(v) => v.charAt(0).toUpperCase() + v.slice(1)} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} domain={[0, "auto"]} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Bar dataKey="within_sla" name="Within SLA" fill="#10b981" radius={[4, 4, 0, 0]} stackId="a" />
                <Bar dataKey="overdue" name="Overdue" fill="#ef4444" radius={[4, 4, 0, 0]} stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {view === "ownership" && (
        <div className="space-y-6">
          {(ownerInfo?.unassigned_open_cves || 0) > 0 && (
            <div data-testid="unassigned-alert" className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400" />
                <div>
                  <span className="text-amber-300 font-semibold text-sm">{ownerInfo.unassigned_open_cves} unassigned open CVE{ownerInfo.unassigned_open_cves !== 1 ? "s" : ""}</span>
                  <p className="text-amber-400/70 text-xs mt-0.5">These vulnerabilities need an owner for accountability and SLA tracking</p>
                </div>
              </div>
            </div>
          )}

          {(unassigned?.items || []).length > 0 && (
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-3 text-sm flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" /> Unassigned CVEs
                <span className="text-xs text-slate-500 font-normal ml-1">({unassigned.total} total)</span>
              </h3>
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {(unassigned.items || []).map((c) => (
                  <div key={c.id} data-testid={`unassigned-cve-${c.id}`} className="flex items-center justify-between bg-slate-900/50 rounded-lg px-3 py-2">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <span className="text-cyan-400 font-mono text-xs">{c.cve_id}</span>
                      <SeverityBadge severity={c.severity} />
                      <span className="text-xs text-slate-300 truncate">{c.title}</span>
                    </div>
                    <button data-testid={`gov-assign-btn-${c.id}`} onClick={() => setGovAssignTarget(c)} className="ml-2 px-2.5 py-1 rounded text-xs bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/40 transition-colors border border-cyan-500/30 shrink-0">
                      <Users className="w-3 h-3 inline mr-1" />Assign
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Team</h3>
              {(ownership?.by_team || []).length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-sm">No team assignments yet</div>
              ) : (
                <div className="space-y-2">
                  {(ownership?.by_team || []).map((t) => {
                    const maxCount = Math.max(...(ownership?.by_team || []).map((x) => x.count), 1);
                    return (
                      <div key={t.team} className="flex items-center gap-3">
                        <span className="text-sm text-slate-300 w-32 truncate">{t.team}</span>
                        <div className="flex-1 bg-slate-700/50 rounded-full h-3">
                          <div className="h-3 rounded-full bg-cyan-500/70" style={{ width: `${(t.count / maxCount) * 100}%` }} />
                        </div>
                        <span className="text-sm text-white font-medium w-8 text-right">{t.count}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Assignee</h3>
              {(ownership?.by_person || []).length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-sm">No individual assignments yet</div>
              ) : (
                <div className="space-y-2">
                  {(ownership?.by_person || []).map((p) => {
                    const maxCount = Math.max(...(ownership?.by_person || []).map((x) => x.count), 1);
                    return (
                      <div key={p.person} className="flex items-center gap-3">
                        <span className="text-sm text-slate-300 w-32 truncate">{p.person}</span>
                        <div className="flex-1 bg-slate-700/50 rounded-full h-3">
                          <div className="h-3 rounded-full bg-purple-500/70" style={{ width: `${(p.count / maxCount) * 100}%` }} />
                        </div>
                        <span className="text-sm text-white font-medium w-8 text-right">{p.count}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-3 text-sm">Registered Owners</h3>
              {(ownerInfo?.people || []).length === 0 ? (
                <p className="text-slate-500 text-sm">No owners registered yet. Assign an owner to a CVE to populate this list.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {(ownerInfo?.people || []).map((p) => (
                    <span key={p} className="px-3 py-1 bg-purple-500/15 text-purple-300 rounded-lg text-xs border border-purple-500/20">{p}</span>
                  ))}
                </div>
              )}
            </div>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-3 text-sm">Registered Teams</h3>
              {(ownerInfo?.teams || []).length === 0 ? (
                <p className="text-slate-500 text-sm">No teams registered yet. Assign a team to a CVE to populate this list.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {(ownerInfo?.teams || []).map((t) => (
                    <span key={t} className="px-3 py-1 bg-cyan-500/15 text-cyan-300 rounded-lg text-xs border border-cyan-500/20">{t}</span>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">CVE Sources</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={sourcePieData} cx="50%" cy="50%" innerRadius={35} outerRadius={65} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                    {sourcePieData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-white font-semibold mb-4 text-sm">Status Distribution</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={statusPieData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" name="Count" radius={[4, 4, 0, 0]} barSize={30}>
                    {statusPieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {govAssignTarget && <AssignOwnerModal cve={govAssignTarget} onClose={() => setGovAssignTarget(null)} onAssigned={() => { setGovAssignTarget(null); fetchAll(); onRefresh(); }} />}
        </div>
      )}
    </div>
  );
};
