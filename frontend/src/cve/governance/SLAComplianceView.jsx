import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { SEVERITY_COLORS } from "../shared";
import { ChartTooltip } from "../components";

const CustomTooltip = ChartTooltip;

export const SLAComplianceView = ({ sla }) => {
  return (
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
  );
};
