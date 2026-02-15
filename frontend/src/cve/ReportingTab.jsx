import React, { useState, useEffect, useCallback } from "react";
import {
  BarChart3, TrendingUp, Users, Download, FileText, Shield, Clock, Target,
  AlertTriangle, CheckCircle, Loader2, Calendar, ChevronDown, Trash2, Save, Scan
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";
import { REPORTING_API, fetcher, SEVERITY_COLORS, StatCard } from "./shared";

const CHART_COLORS = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#64748b"];
const STATUS_COLORS_MAP = {
  detected: "#ef4444", triaged: "#eab308", in_progress: "#3b82f6",
  fixed: "#10b981", verified: "#22c55e", dismissed: "#64748b", wont_fix: "#475569",
};

const SUB_TABS = [
  { id: "executive", label: "Executive Summary", icon: Shield },
  { id: "trends", label: "Trends", icon: TrendingUp },
  { id: "team", label: "Team Performance", icon: Users },
  { id: "scanners", label: "Scanner Stats", icon: Scan },
  { id: "export", label: "Export", icon: Download },
];

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

/* ─── Executive Summary ──────────────────────────────── */
const ExecutiveView = ({ data, loading }) => {
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

/* ─── Trends View ────────────────────────────────────── */
const TrendsView = ({ trends, severityTrends, statusDist, loading, days, setDays }) => {
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

      {/* Discovery vs Resolution */}
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
        {/* Backlog trend */}
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

        {/* Severity stacked bar */}
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

      {/* Status distribution pie */}
      {statusData.length > 0 && (
        <div data-testid="status-distribution-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <p className="text-slate-400 text-sm mb-4">Current Status Distribution</p>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={statusData} cx="50%" cy="50%" innerRadius={55} outerRadius={90} dataKey="value" paddingAngle={2} label={({ name, value }) => `${name}: ${value}`}>
                {statusData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_COLORS_MAP[entry.name.replace(" ", "_")] || "#64748b"} />
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

/* ─── Team Performance ───────────────────────────────── */
const TeamView = ({ data, loading }) => {
  if (loading) return <LoadingState />;
  if (!data?.teams?.length) return <EmptyState text="No team data — assign CVEs to owners first" />;

  return (
    <div className="space-y-6">
      <h3 className="text-white font-semibold">Team Performance</h3>

      {/* Team bar chart */}
      <div data-testid="team-bar-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <p className="text-slate-400 text-sm mb-4">Assigned vs Resolved by Owner</p>
        <ResponsiveContainer width="100%" height={Math.max(200, data.teams.length * 40)}>
          <BarChart data={data.teams} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis type="category" dataKey="owner" tick={{ fill: "#94a3b8", fontSize: 11 }} width={100} />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            <Bar dataKey="assigned" name="Assigned" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            <Bar dataKey="resolved" name="Resolved" fill="#10b981" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Team table */}
      <div data-testid="team-table" className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50">
                {["Owner", "Assigned", "Open", "Resolved", "Rate", "Avg MTTR", "Crit", "High", "Med", "Low"].map((h) => (
                  <th key={h} className="text-left text-slate-400 font-medium px-4 py-3 text-xs">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.teams.map((t) => (
                <tr key={t.owner} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                  <td className="px-4 py-3 text-white font-medium">{t.owner}</td>
                  <td className="px-4 py-3 text-slate-300">{t.assigned}</td>
                  <td className="px-4 py-3 text-orange-400">{t.open}</td>
                  <td className="px-4 py-3 text-emerald-400">{t.resolved}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${t.resolution_rate >= 80 ? "bg-emerald-500/20 text-emerald-300" : t.resolution_rate >= 50 ? "bg-yellow-500/20 text-yellow-300" : "bg-red-500/20 text-red-300"}`}>
                      {t.resolution_rate}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-cyan-400">{t.avg_resolution_hours}h</td>
                  <td className="px-4 py-3 text-red-400">{t.critical}</td>
                  <td className="px-4 py-3 text-orange-400">{t.high}</td>
                  <td className="px-4 py-3 text-yellow-400">{t.medium}</td>
                  <td className="px-4 py-3 text-blue-400">{t.low}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

/* ─── Scanner Stats ──────────────────────────────────── */
const ScannerView = ({ data, loading }) => {
  if (loading) return <LoadingState />;
  if (!data?.scanners?.length) return <EmptyState text="No scanner data — run a scan first" />;

  return (
    <div className="space-y-6">
      <h3 className="text-white font-semibold">Scanner Effectiveness</h3>

      <div data-testid="scanner-bar-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <p className="text-slate-400 text-sm mb-4">CVEs Found per Scanner</p>
        <ResponsiveContainer width="100%" height={Math.max(200, data.scanners.length * 50)}>
          <BarChart data={data.scanners} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis type="category" dataKey="scanner" tick={{ fill: "#94a3b8", fontSize: 11 }} width={100} />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            <Bar dataKey="total_scans" name="Total Scans" fill="#6366f1" radius={[0, 4, 4, 0]} />
            <Bar dataKey="cves_found" name="CVEs Found" fill="#f97316" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.scanners.map((s) => (
          <div key={s.scanner} data-testid={`scanner-card-${s.scanner}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-white font-medium text-sm">{s.scanner}</span>
              <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded">{s.total_scans} scans</span>
            </div>
            <div className="text-2xl font-bold text-orange-400 mb-1">{s.cves_found}</div>
            <div className="text-xs text-slate-500">CVEs found ({s.avg_findings_per_scan} avg/scan)</div>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ─── Export View ─────────────────────────────────────── */
const ExportView = ({ days, savedReports, onDelete }) => {
  const [saving, setSaving] = useState(false);
  const [reportName, setReportName] = useState("");

  const downloadFile = (url, filename) => {
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleExport = (type) => {
    const base = REPORTING_API;
    if (type === "cves") downloadFile(`${base}/export/cves`, "cve_export.csv");
    else if (type === "executive") downloadFile(`${base}/export/executive?days=${days}`, "executive_report.csv");
    else if (type === "team") downloadFile(`${base}/export/team`, "team_performance.csv");
  };

  const handleSave = async () => {
    if (!reportName.trim()) return;
    setSaving(true);
    try {
      await fetcher(`${REPORTING_API}/saved`, {
        method: "POST",
        body: JSON.stringify({ name: reportName, report_type: "executive", config: { days } }),
      });
      setReportName("");
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  return (
    <div className="space-y-6">
      <h3 className="text-white font-semibold">Export Reports</h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { type: "cves", title: "CVE Database", desc: "Full CVE list with all fields", icon: AlertTriangle },
          { type: "executive", title: "Executive Summary", desc: `Summary for last ${days} days`, icon: BarChart3 },
          { type: "team", title: "Team Performance", desc: "Per-owner resolution stats", icon: Users },
        ].map(({ type, title, desc, icon: Icon }) => (
          <button key={type} data-testid={`export-${type}-btn`} onClick={() => handleExport(type)} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 text-left hover:bg-slate-700/40 transition-colors group">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-cyan-500/10 rounded-lg group-hover:bg-cyan-500/20 transition-colors"><Icon className="w-5 h-5 text-cyan-400" /></div>
              <span className="text-white font-medium text-sm">{title}</span>
            </div>
            <p className="text-slate-500 text-xs mb-3">{desc}</p>
            <div className="flex items-center gap-1 text-cyan-400 text-xs font-medium">
              <Download className="w-3.5 h-3.5" /> Download CSV
            </div>
          </button>
        ))}
      </div>

      {/* Save report config */}
      <div data-testid="save-report-section" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <p className="text-white font-medium text-sm mb-3">Save Report Configuration</p>
        <div className="flex gap-3">
          <input data-testid="report-name-input" value={reportName} onChange={(e) => setReportName(e.target.value)} placeholder="Report name..." className="flex-1 bg-slate-900/60 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50" />
          <button data-testid="save-report-btn" onClick={handleSave} disabled={saving || !reportName.trim()} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
            <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      {/* Saved reports list */}
      {savedReports?.reports?.length > 0 && (
        <div data-testid="saved-reports-list" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <p className="text-white font-medium text-sm mb-3">Saved Reports</p>
          <div className="space-y-2">
            {savedReports.reports.map((r) => (
              <div key={r.id} className="flex items-center justify-between bg-slate-900/40 rounded-lg px-4 py-3">
                <div>
                  <span className="text-white text-sm font-medium">{r.name}</span>
                  <span className="text-slate-500 text-xs ml-2">{r.report_type} — {new Date(r.created_at).toLocaleDateString()}</span>
                </div>
                <button data-testid={`delete-report-${r.id}`} onClick={() => onDelete(r.id)} className="p-1.5 hover:bg-red-500/20 rounded-lg transition-colors">
                  <Trash2 className="w-4 h-4 text-red-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/* ─── Utilities ───────────────────────────────────────── */
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

const LoadingState = () => (
  <div className="flex items-center justify-center py-16">
    <Loader2 className="w-7 h-7 text-cyan-400 animate-spin" />
    <span className="ml-3 text-slate-400 text-sm">Loading report data...</span>
  </div>
);

const EmptyState = ({ text }) => (
  <div className="text-center py-16">
    <FileText className="w-10 h-10 text-slate-600 mx-auto mb-3" />
    <p className="text-slate-500 text-sm">{text}</p>
  </div>
);

/* ─── Main Component ─────────────────────────────────── */
export const ReportingTab = () => {
  const [subTab, setSubTab] = useState("executive");
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState(null);
  const [severityTrends, setSeverityTrends] = useState(null);
  const [statusDist, setStatusDist] = useState(null);
  const [teamData, setTeamData] = useState(null);
  const [scannerData, setScannerData] = useState(null);
  const [savedReports, setSavedReports] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [sum, tr, sev, st, team, scan, saved] = await Promise.all([
        fetcher(`${REPORTING_API}/summary?days=${days}`),
        fetcher(`${REPORTING_API}/trends?days=${days}`),
        fetcher(`${REPORTING_API}/severity-trends?days=${days}`),
        fetcher(`${REPORTING_API}/status-distribution`),
        fetcher(`${REPORTING_API}/team-performance`),
        fetcher(`${REPORTING_API}/scanner-stats`),
        fetcher(`${REPORTING_API}/saved`),
      ]);
      setSummary(sum);
      setTrends(tr);
      setSeverityTrends(sev);
      setStatusDist(st);
      setTeamData(team);
      setScannerData(scan);
      setSavedReports(saved);
    } catch (e) {
      console.error("Failed to load reporting data:", e);
    }
    setLoading(false);
  }, [days]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleDeleteReport = async (id) => {
    try {
      await fetcher(`${REPORTING_API}/saved/${id}`, { method: "DELETE" });
      setSavedReports((prev) => ({
        ...prev,
        reports: (prev?.reports || []).filter((r) => r.id !== id),
      }));
    } catch (e) { console.error(e); }
  };

  return (
    <div data-testid="reporting-tab" className="space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex items-center gap-1 bg-slate-800/40 rounded-xl p-1 overflow-x-auto">
        {SUB_TABS.map((t) => (
          <button key={t.id} data-testid={`reporting-subtab-${t.id}`} onClick={() => setSubTab(t.id)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all whitespace-nowrap ${subTab === t.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <t.icon className="w-4 h-4" /> {t.label}
          </button>
        ))}
      </div>

      {subTab === "executive" && <ExecutiveView data={summary} loading={loading} />}
      {subTab === "trends" && <TrendsView trends={trends} severityTrends={severityTrends} statusDist={statusDist} loading={loading} days={days} setDays={setDays} />}
      {subTab === "team" && <TeamView data={teamData} loading={loading} />}
      {subTab === "scanners" && <ScannerView data={scannerData} loading={loading} />}
      {subTab === "export" && <ExportView days={days} savedReports={savedReports} onDelete={handleDeleteReport} />}
    </div>
  );
};
