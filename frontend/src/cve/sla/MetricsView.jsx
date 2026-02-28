import React from "react";
import { Clock, CheckCircle2, AlertTriangle, TrendingUp, Zap } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell } from "recharts";
import { SEVERITY_COLORS } from "../shared";
import { ChartTooltip } from "../components";

const MetricCard = ({ icon: Icon, label, value, unit, color, subtext }) => (
  <div data-testid={`metric-${label.toLowerCase().replace(/\s+/g, "-")}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
    <div className="flex items-center gap-3 mb-3">
      <div className={`p-2.5 rounded-lg ${color === "cyan" ? "bg-cyan-500/10" : color === "emerald" ? "bg-emerald-500/10" : color === "amber" ? "bg-amber-500/10" : "bg-red-500/10"}`}>
        <Icon className={`w-5 h-5 ${color === "cyan" ? "text-cyan-400" : color === "emerald" ? "text-emerald-400" : color === "amber" ? "text-amber-400" : "text-red-400"}`} />
      </div>
      <span className="text-slate-400 text-sm">{label}</span>
    </div>
    <div className="flex items-baseline gap-1.5">
      <span className="text-3xl font-bold text-white">{value}</span>
      {unit && <span className="text-sm text-slate-500">{unit}</span>}
    </div>
    {subtext && <div className="text-xs text-slate-500 mt-2">{subtext}</div>}
  </div>
);

const SEV_COLORS_BAR = { critical: "#ef4444", high: "#f97316", medium: "#eab308", low: "#3b82f6" };

export const MetricsView = ({ metrics }) => {
  if (!metrics) return null;

  const mttrData = Object.entries(metrics.mttr_by_severity || {}).map(([sev, d]) => ({
    severity: sev.charAt(0).toUpperCase() + sev.slice(1),
    key: sev,
    "Avg MTTR (h)": d.avg_hours,
    "SLA Limit (h)": d.sla_hours,
  }));

  const resolutionData = Object.entries(metrics.resolution_within_sla || {}).map(([sev, d]) => ({
    severity: sev.charAt(0).toUpperCase() + sev.slice(1),
    key: sev,
    "Within SLA": d.within_sla,
    "Breached": d.breached,
  }));

  return (
    <div data-testid="sla-metrics-view" className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={Clock}
          label="Overall MTTR"
          value={metrics.overall_mttr_hours > 0 ? metrics.overall_mttr_days : "--"}
          unit={metrics.overall_mttr_hours > 0 ? "days" : ""}
          color="cyan"
          subtext={metrics.overall_mttr_hours > 0 ? `${metrics.overall_mttr_hours}h average` : "No data yet"}
        />
        <MetricCard
          icon={Zap}
          label="Avg Triage Time"
          value={metrics.avg_triage_hours > 0 ? metrics.avg_triage_hours : "--"}
          unit={metrics.avg_triage_hours > 0 ? "hours" : ""}
          color="amber"
          subtext="Detection to triage"
        />
        <MetricCard
          icon={CheckCircle2}
          label="Total Resolved"
          value={metrics.total_resolved}
          color="emerald"
          subtext={`${metrics.resolved_this_week} this week`}
        />
        <MetricCard
          icon={AlertTriangle}
          label="Open CVEs"
          value={metrics.total_open}
          color="red"
          subtext="Awaiting resolution"
        />
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(metrics.mttr_by_severity || {}).map(([sev, d]) => {
          const c = SEVERITY_COLORS[sev] || SEVERITY_COLORS.info;
          const res = metrics.resolution_within_sla?.[sev] || {};
          const pct = res.rate_pct ?? 100;
          return (
            <div key={sev} data-testid={`mttr-card-${sev}`} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
              <div className="flex items-center justify-between mb-3">
                <h4 className={`${c.text} font-semibold text-sm uppercase`}>{sev}</h4>
                <span className={`text-lg font-bold ${pct >= 90 ? "text-emerald-400" : pct >= 70 ? "text-amber-400" : "text-red-400"}`}>
                  {pct}%
                </span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between"><span className="text-slate-400">MTTR:</span><span className="text-white font-medium">{d.avg_hours > 0 ? `${d.avg_hours}h` : "--"}</span></div>
                <div className="flex justify-between"><span className="text-slate-400">SLA Limit:</span><span className="text-white">{d.sla_hours}h</span></div>
                <div className="flex justify-between"><span className="text-slate-400">Resolved:</span><span className="text-white">{res.resolved_total || 0}</span></div>
                <div className="flex justify-between"><span className="text-slate-400">SLA Breached:</span><span className={res.breached > 0 ? "text-red-400" : "text-emerald-400"}>{res.breached || 0}</span></div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-4 text-sm">MTTR vs SLA Limit by Severity</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={mttrData} barCategoryGap="25%">
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="severity" tick={{ fill: "#94a3b8", fontSize: 12 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} label={{ value: "Hours", angle: -90, position: "insideLeft", fill: "#64748b", fontSize: 11 }} />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            <Bar dataKey="Avg MTTR (h)" fill="#22d3ee" radius={[4, 4, 0, 0]}>
              {mttrData.map((entry) => (
                <Cell key={entry.key} fill={SEV_COLORS_BAR[entry.key] || "#22d3ee"} fillOpacity={0.7} />
              ))}
            </Bar>
            <Bar dataKey="SLA Limit (h)" fill="#475569" radius={[4, 4, 0, 0]} fillOpacity={0.4} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-4 text-sm">Resolution SLA Compliance by Severity</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={resolutionData} barCategoryGap="25%">
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="severity" tick={{ fill: "#94a3b8", fontSize: 12 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            <Bar dataKey="Within SLA" fill="#10b981" stackId="a" />
            <Bar dataKey="Breached" fill="#ef4444" stackId="a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
