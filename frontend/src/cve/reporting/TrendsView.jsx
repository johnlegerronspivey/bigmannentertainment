import React from "react";
import { Calendar } from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";
import { ChartTooltip, LoadingState, EmptyState } from "../components";
import { STATUS_CHART_COLORS } from "../constants";

const DaysPicker = ({ value, onChange }) => (
  <div className="flex items-center gap-2">
    <Calendar className="w-4 h-4 text-slate-400" />
    <select data-testid="days-picker" value={value} onChange={(e) => onChange(Number(e.target.value))} className="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-cyan-500/50">
      <option value={7}>7 days</option>
      <option value={14}>14 days</option>
      <option value={30}>30 days</option>
      <option value={60}>60 days</option>
      <option value={90}>90 days</option>
    </select>
  </div>
);

export { DaysPicker };

export const TrendsView = ({ trends, severityTrends, statusDist, loading, days, setDays }) => {
  if (loading) return <LoadingState />;

  const statusData = statusDist ? Object.entries(statusDist.distribution || {})
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ name: k.replace("_", " "), value: v })) : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold">CVE Trends</h3>
        <DaysPicker value={days} onChange={setDays} />
      </div>

      <div data-testid="discovery-resolution-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <p className="text-slate-400 text-sm mb-4">Discovered vs Resolved Over Time</p>
        {trends?.trends?.length > 0 ? (
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={trends.trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 11 }} interval={Math.floor((trends.trends.length) / 8)} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip content={<ChartTooltip />} />
              <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
              <Area type="monotone" dataKey="discovered" name="Discovered" stroke="#f97316" fill="#f97316" fillOpacity={0.15} strokeWidth={2} />
              <Area type="monotone" dataKey="resolved" name="Resolved" stroke="#10b981" fill="#10b981" fillOpacity={0.15} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        ) : <EmptyState text="No trend data" />}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div data-testid="backlog-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <p className="text-slate-400 text-sm mb-4">Open Backlog Over Time</p>
          {trends?.trends?.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trends.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 11 }} interval={Math.floor((trends.trends.length) / 6)} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip content={<ChartTooltip />} />
                <Line type="monotone" dataKey="backlog" name="Open Backlog" stroke="#06b6d4" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : <EmptyState text="No backlog data" />}
        </div>

        <div data-testid="severity-trends-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <p className="text-slate-400 text-sm mb-4">Severity Breakdown Over Time</p>
          {severityTrends?.trends?.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={severityTrends.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 11 }} interval={Math.floor((severityTrends.trends.length) / 6)} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
                <Bar dataKey="critical" name="Critical" stackId="a" fill="#ef4444" />
                <Bar dataKey="high" name="High" stackId="a" fill="#f97316" />
                <Bar dataKey="medium" name="Medium" stackId="a" fill="#eab308" />
                <Bar dataKey="low" name="Low" stackId="a" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyState text="No severity trend data" />}
        </div>
      </div>

      {statusData.length > 0 && (
        <div data-testid="status-distribution-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <p className="text-slate-400 text-sm mb-4">Current Status Distribution</p>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={statusData} cx="50%" cy="50%" innerRadius={55} outerRadius={90} dataKey="value" paddingAngle={2} label={({ name, value }) => `${name}: ${value}`}>
                {statusData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_CHART_COLORS[entry.name.replace(" ", "_")] || "#64748b"} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
