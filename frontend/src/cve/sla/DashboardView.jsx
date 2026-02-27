import React from "react";
import { Shield, Timer, Clock, AlertTriangle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { SEVERITY_COLORS, StatCard } from "../shared";
import { ChartTooltip } from "../components";

export const DashboardView = ({ dashboard }) => {
  const sevBarData = Object.entries(dashboard.severity_stats || {}).map(([sev, d]) => ({
    severity: sev.charAt(0).toUpperCase() + sev.slice(1),
    "Within SLA": d.within_sla, Warning: d.warning, Breached: d.breached,
  }));
  return (
    <div className="space-y-6">
      <div className={`border rounded-xl p-6 ${dashboard.overall_compliance >= 90 ? "bg-emerald-900/20 border-emerald-500/30" : dashboard.overall_compliance >= 70 ? "bg-amber-900/20 border-amber-500/30" : "bg-red-900/20 border-red-500/30"}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold text-lg">SLA Compliance Health</h3>
            <p className="text-sm text-slate-400 mt-1">{dashboard.total_open} open CVEs — {dashboard.total_breached} breached, {dashboard.total_warning} warning</p>
          </div>
          <div data-testid="sla-overall-compliance" className="text-right">
            <div className={`text-5xl font-bold ${dashboard.overall_compliance >= 90 ? "text-emerald-400" : dashboard.overall_compliance >= 70 ? "text-amber-400" : "text-red-400"}`}>{dashboard.overall_compliance}%</div>
            <div className="text-xs text-slate-400 mt-1">Overall Compliance</div>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Shield} label="Total Open" value={dashboard.total_open} color="text-white" />
        <StatCard icon={Timer} label="Within SLA" value={dashboard.total_within_sla} color="text-emerald-400" />
        <StatCard icon={Clock} label="Warning" value={dashboard.total_warning} color="text-amber-400" />
        <StatCard icon={AlertTriangle} label="Breached" value={dashboard.total_breached} color="text-red-400" />
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(dashboard.severity_stats || {}).map(([sev, d]) => {
          const c = SEVERITY_COLORS[sev] || SEVERITY_COLORS.info;
          const pct = d.compliance_pct;
          return (
            <div key={sev} data-testid={`sla-sev-${sev}`} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
              <div className="flex items-center justify-between mb-3">
                <h4 className={`${c.text} font-semibold text-sm uppercase`}>{sev}</h4>
                <span className={`text-xl font-bold ${pct >= 90 ? "text-emerald-400" : pct >= 70 ? "text-amber-400" : "text-red-400"}`}>{pct}%</span>
              </div>
              <div className="w-full bg-slate-700/50 rounded-full h-2 mb-3">
                <div className={`h-2 rounded-full transition-all ${pct >= 90 ? "bg-emerald-500" : pct >= 70 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div><span className="text-slate-400">SLA:</span> <span className="text-white">{d.sla_hours}h</span></div>
                <div><span className="text-slate-400">Total:</span> <span className="text-white">{d.total}</span></div>
                <div><span className="text-slate-400">Breached:</span> <span className={d.breached > 0 ? "text-red-400" : "text-emerald-400"}>{d.breached}</span></div>
                <div><span className="text-slate-400">Warning:</span> <span className={d.warning > 0 ? "text-amber-400" : "text-emerald-400"}>{d.warning}</span></div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-4 text-sm">SLA Status by Severity</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={sevBarData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="severity" tick={{ fill: "#94a3b8", fontSize: 12 }} />
            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            <Bar dataKey="Within SLA" fill="#10b981" stackId="a" />
            <Bar dataKey="Warning" fill="#f59e0b" stackId="a" />
            <Bar dataKey="Breached" fill="#ef4444" stackId="a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
