import React, { useState, useEffect } from "react";
import { AlertTriangle, Clock, CheckCircle, Shield, Server, Box, Activity, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { AreaChart, Area, ResponsiveContainer, Tooltip } from "recharts";
import { SEVERITY_COLORS, REPORTING_API, fetcher, SeverityBadge, StatusBadge } from "./shared";

const TrendIndicator = ({ delta, label }) => {
  if (delta === 0) return <div className="flex items-center gap-1 text-slate-500 text-xs"><Minus className="w-3 h-3" /> No change</div>;
  const isUp = delta > 0;
  return (
    <div data-testid={`trend-${label}`} className={`flex items-center gap-1 text-xs ${isUp ? "text-orange-400" : "text-emerald-400"}`}>
      {isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
      {isUp ? "+" : ""}{delta} vs last week
    </div>
  );
};

const EnhancedStatCard = ({ icon: Icon, label, value, color = "text-white", subtext, delta }) => (
  <div data-testid={`stat-${label.toLowerCase().replace(/\s+/g, "-")}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 hover:border-slate-600/60 transition-colors">
    <div className="flex items-center gap-3 mb-2">
      <div className="p-2 rounded-lg bg-slate-700/50"><Icon className={`w-5 h-5 ${color}`} /></div>
      <span className="text-slate-400 text-sm">{label}</span>
    </div>
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
    {delta !== undefined && <TrendIndicator delta={delta} label={label.toLowerCase().replace(/\s+/g, "-")} />}
    {subtext && <div className="text-xs text-slate-500 mt-1">{subtext}</div>}
  </div>
);

const MiniSparkline = ({ data }) => {
  if (!data || data.length === 0) return null;
  return (
    <div data-testid="mini-sparkline" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-white font-semibold text-sm">New CVEs This Week</h3>
        <span className="text-xs text-slate-500">7-day trend</span>
      </div>
      <ResponsiveContainer width="100%" height={80}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
            </linearGradient>
          </defs>
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8, fontSize: 11 }}
            labelStyle={{ color: "#94a3b8" }}
            itemStyle={{ color: "#06b6d4" }}
          />
          <Area type="monotone" dataKey="count" stroke="#06b6d4" fill="url(#sparkGrad)" strokeWidth={2} dot={{ r: 3, fill: "#06b6d4" }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

const LoadingSkeleton = () => (
  <div data-testid="overview-loading" className="space-y-6 animate-pulse">
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="h-4 bg-slate-700 rounded w-2/3 mb-3" />
          <div className="h-7 bg-slate-700 rounded w-1/3" />
        </div>
      ))}
    </div>
    <div className="h-40 bg-slate-800/60 border border-slate-700/50 rounded-xl" />
    <div className="grid md:grid-cols-2 gap-6">
      <div className="h-64 bg-slate-800/60 border border-slate-700/50 rounded-xl" />
      <div className="h-64 bg-slate-800/60 border border-slate-700/50 rounded-xl" />
    </div>
  </div>
);

export const OverviewTab = ({ dashboard, onRefresh, loading }) => {
  const [trends, setTrends] = useState(null);

  useEffect(() => {
    fetcher(`${REPORTING_API}/dashboard-trends`).then(setTrends).catch(console.error);
  }, []);

  if (loading || !dashboard) return <LoadingSkeleton />;

  const { severity_breakdown: sb } = dashboard;
  const deltas = trends?.deltas || {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <EnhancedStatCard icon={AlertTriangle} label="Open CVEs" value={dashboard.open_cves} color="text-red-400" delta={deltas.open_delta} />
        <EnhancedStatCard icon={Clock} label="Overdue" value={dashboard.overdue_cves} color="text-orange-400" />
        <EnhancedStatCard icon={CheckCircle} label="Fixed" value={dashboard.fixed_cves} color="text-emerald-400" delta={deltas.fixed_delta} />
        <EnhancedStatCard icon={Shield} label="Verified" value={dashboard.verified_cves} color="text-green-400" />
        <EnhancedStatCard icon={Server} label="Services" value={dashboard.total_services} color="text-cyan-400" />
        <EnhancedStatCard icon={Box} label="SBOMs" value={dashboard.total_sboms} color="text-purple-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Open CVEs by Severity</h3>
          <div className="grid grid-cols-5 gap-3">
            {["critical", "high", "medium", "low", "info"].map((s) => {
              const c = SEVERITY_COLORS[s];
              return (
                <div key={s} data-testid={`severity-card-${s}`} className={`${c.bg} border ${c.border} rounded-lg p-4 text-center hover:scale-[1.02] transition-transform`}>
                  <div className={`text-2xl font-bold ${c.text}`}>{sb[s] || 0}</div>
                  <div className={`text-xs ${c.text} mt-1 uppercase`}>{s}</div>
                </div>
              );
            })}
          </div>
        </div>
        <MiniSparkline data={trends?.mini_trend} />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3">Recent CVEs</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {(dashboard.recent_cves || []).map((c) => (
              <div key={c.id} data-testid={`recent-cve-${c.cve_id}`} className="flex items-center justify-between bg-slate-700/30 rounded-lg px-3 py-2 hover:bg-slate-700/40 transition-colors">
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-white truncate">{c.cve_id}</div>
                  <div className="text-xs text-slate-400 truncate">{c.title}</div>
                </div>
                <div className="flex items-center gap-2 ml-2 shrink-0">
                  <SeverityBadge severity={c.severity} />
                  <StatusBadge status={c.status} />
                </div>
              </div>
            ))}
            {(!dashboard.recent_cves || dashboard.recent_cves.length === 0) && (
              <div className="text-slate-500 text-sm text-center py-4">No CVEs yet. Run a scan to detect vulnerabilities.</div>
            )}
          </div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3">Recent Activity</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {(dashboard.recent_activity || []).map((a) => (
              <div key={a.id} data-testid={`activity-${a.id}`} className="flex items-start gap-3 bg-slate-700/30 rounded-lg px-3 py-2 hover:bg-slate-700/40 transition-colors">
                <Activity className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div className="min-w-0">
                  <div className="text-sm text-white truncate">{a.message}</div>
                  <div className="text-xs text-slate-500">{new Date(a.timestamp).toLocaleString()}</div>
                </div>
              </div>
            ))}
            {(!dashboard.recent_activity || dashboard.recent_activity.length === 0) && (
              <div className="text-slate-500 text-sm text-center py-4">No activity recorded yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
