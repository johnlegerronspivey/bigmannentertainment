import React from "react";
import { AlertTriangle, CheckCircle, Target } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { StatCard } from "../shared";
import { ChartTooltip } from "../components";

const CustomTooltip = ChartTooltip;

export const TrendsView = ({ metrics, trends }) => {
  const trendData = (trends?.trends || []).filter((_, i, arr) => arr.length <= 15 || i % Math.ceil(arr.length / 15) === 0 || i === arr.length - 1);

  return (
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
  );
};
