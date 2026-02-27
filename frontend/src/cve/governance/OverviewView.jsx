import React from "react";
import { AlertTriangle, CheckCircle, CheckCircle2, TrendingUp, Target } from "lucide-react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { StatCard } from "../shared";
import { ChartTooltip, RiskGauge } from "../components";
import { CHART_COLORS, PIE_COLORS, STATUS_CHART_COLORS } from "../constants";

const CustomTooltip = ChartTooltip;

export const OverviewView = ({ metrics, ownership, mttr }) => {
  const sevPieData = Object.entries(metrics.severity_distribution || {}).filter(([, v]) => v > 0).map(([k, v], i) => ({ name: k.charAt(0).toUpperCase() + k.slice(1), value: v, fill: CHART_COLORS[i] }));
  const statusPieData = (ownership?.by_status || []).map((s) => ({ name: s.status.replace("_", " "), value: s.count, fill: STATUS_CHART_COLORS[s.status] || "#64748b" }));
  const sourcePieData = (ownership?.by_source || []).map((s, i) => ({ name: s.source, value: s.count, fill: CHART_COLORS[i % CHART_COLORS.length] }));
  const servicesBarData = (metrics.services_affected || []).map((s) => ({ name: s.service.length > 18 ? s.service.slice(0, 18) + "..." : s.service, count: s.count }));
  const mttrBarData = Object.entries(mttr?.mttr || {}).map(([sev, d]) => ({ severity: sev.charAt(0).toUpperCase() + sev.slice(1), hours: d.avg_hours, days: d.avg_days, samples: d.sample_size }));

  return (
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
  );
};
