import React from "react";
import { AlertTriangle, Shield, CheckCircle, Clock, Target } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { StatCard } from "../shared";
import { ChartTooltip, LoadingState, EmptyState } from "../components";
import { CHART_COLORS } from "../constants";

export const ExecutiveView = ({ data, loading }) => {
  if (loading) return <LoadingState />;
  if (!data) return <EmptyState text="No summary data available" />;

  const severityData = Object.entries(data.severity_distribution || {})
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ name: k.charAt(0).toUpperCase() + k.slice(1), value: v }));

  const riskColor = data.risk_score >= 70 ? "text-red-400" : data.risk_score >= 40 ? "text-orange-400" : "text-emerald-400";
  const slaColor = data.sla_compliance >= 90 ? "text-emerald-400" : data.sla_compliance >= 70 ? "text-yellow-400" : "text-red-400";

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <StatCard icon={AlertTriangle} label="Total CVEs" value={data.total_cves} color="text-white" />
        <StatCard icon={Shield} label="Open" value={data.total_open} color="text-red-400" subtext={`${data.new_in_period} new this period`} />
        <StatCard icon={CheckCircle} label="Closed" value={data.total_closed} color="text-emerald-400" subtext={`${data.fixed_in_period} fixed this period`} />
        <StatCard icon={Clock} label="MTTR" value={`${data.mttr_hours}h`} color="text-cyan-400" subtext="Mean time to resolve" />
        <StatCard icon={Target} label="Resolution Rate" value={`${data.resolution_rate}%`} color="text-blue-400" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Score */}
        <div data-testid="risk-score-card" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-6 flex flex-col items-center justify-center">
          <p className="text-slate-400 text-sm mb-3">Risk Score</p>
          <div className="relative w-28 h-28">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="10" />
              <circle cx="50" cy="50" r="42" fill="none" stroke={data.risk_score >= 70 ? "#ef4444" : data.risk_score >= 40 ? "#f97316" : "#10b981"} strokeWidth="10" strokeDasharray={`${data.risk_score * 2.64} 264`} strokeLinecap="round" />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-3xl font-bold ${riskColor}`}>{data.risk_score}</span>
            </div>
          </div>
          <p className={`text-sm mt-2 font-medium ${riskColor}`}>
            {data.risk_score >= 70 ? "Critical" : data.risk_score >= 40 ? "Moderate" : "Low"}
          </p>
        </div>

        {/* SLA Compliance */}
        <div data-testid="sla-compliance-card" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-6 flex flex-col items-center justify-center">
          <p className="text-slate-400 text-sm mb-3">SLA Compliance</p>
          <div className="relative w-28 h-28">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="10" />
              <circle cx="50" cy="50" r="42" fill="none" stroke={data.sla_compliance >= 90 ? "#10b981" : data.sla_compliance >= 70 ? "#eab308" : "#ef4444"} strokeWidth="10" strokeDasharray={`${data.sla_compliance * 2.64} 264`} strokeLinecap="round" />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-3xl font-bold ${slaColor}`}>{data.sla_compliance}%</span>
            </div>
          </div>
          <p className={`text-sm mt-2 font-medium ${slaColor}`}>
            {data.sla_compliance >= 90 ? "Healthy" : data.sla_compliance >= 70 ? "At Risk" : "Critical"}
          </p>
        </div>

        {/* Severity Pie */}
        <div data-testid="severity-pie-card" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-6">
          <p className="text-slate-400 text-sm mb-3 text-center">Severity Distribution</p>
          {severityData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={severityData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" paddingAngle={2}>
                  {severityData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-slate-500 text-sm text-center py-12">No CVE data</p>
          )}
        </div>
      </div>
    </div>
  );
};
