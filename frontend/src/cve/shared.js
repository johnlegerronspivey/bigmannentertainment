import React from "react";

export const API = `${process.env.REACT_APP_BACKEND_URL}/api/cve`;
export const SCANNER_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/scanners`;
export const REMEDIATION_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/remediation`;
export const GOVERNANCE_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/governance`;
export const NOTIFICATION_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/notifications`;
export const REPORTS_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/reports`;
export const RBAC_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/rbac`;
export const SLA_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/sla`;
export const REPORTING_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/reporting`;
export const TENANT_API = `${process.env.REACT_APP_BACKEND_URL}/api/tenants`;

export const SEVERITY_COLORS = {
  critical: { bg: "bg-red-900/30", text: "text-red-400", border: "border-red-500/40", badge: "bg-red-500/20 text-red-300", dot: "bg-red-500" },
  high: { bg: "bg-orange-900/30", text: "text-orange-400", border: "border-orange-500/40", badge: "bg-orange-500/20 text-orange-300", dot: "bg-orange-500" },
  medium: { bg: "bg-yellow-900/30", text: "text-yellow-400", border: "border-yellow-500/40", badge: "bg-yellow-500/20 text-yellow-300", dot: "bg-yellow-500" },
  low: { bg: "bg-blue-900/30", text: "text-blue-400", border: "border-blue-500/40", badge: "bg-blue-500/20 text-blue-300", dot: "bg-blue-500" },
  info: { bg: "bg-slate-800/30", text: "text-slate-400", border: "border-slate-500/40", badge: "bg-slate-500/20 text-slate-300", dot: "bg-slate-500" },
};

export const STATUS_COLORS = {
  detected: "bg-red-500/20 text-red-300",
  triaged: "bg-yellow-500/20 text-yellow-300",
  in_progress: "bg-blue-500/20 text-blue-300",
  fixed: "bg-emerald-500/20 text-emerald-300",
  verified: "bg-green-500/20 text-green-300",
  dismissed: "bg-slate-500/20 text-slate-400",
  wont_fix: "bg-slate-500/20 text-slate-400",
};

export const ROLE_BADGES = {
  super_admin: { bg: "bg-fuchsia-500/20", text: "text-fuchsia-300", label: "Super Admin" },
  tenant_admin: { bg: "bg-violet-500/20", text: "text-violet-300", label: "Tenant Admin" },
  admin: { bg: "bg-red-500/20", text: "text-red-300", label: "Admin" },
  manager: { bg: "bg-amber-500/20", text: "text-amber-300", label: "Manager" },
  analyst: { bg: "bg-blue-500/20", text: "text-blue-300", label: "Analyst" },
};

export const ROLE_HIERARCHY = ["analyst", "manager", "admin", "tenant_admin", "super_admin"];

export const fetcher = async (url, opts = {}) => {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
};

export const StatCard = ({ icon: Icon, label, value, color = "text-white", subtext }) => (
  <div data-testid={`stat-${label.toLowerCase().replace(/\s+/g, "-")}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
    <div className="flex items-center gap-3 mb-2">
      <div className={`p-2 rounded-lg bg-slate-700/50`}><Icon className={`w-5 h-5 ${color}`} /></div>
      <span className="text-slate-400 text-sm">{label}</span>
    </div>
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
    {subtext && <div className="text-xs text-slate-500 mt-1">{subtext}</div>}
  </div>
);

export const SeverityBadge = ({ severity }) => {
  const c = SEVERITY_COLORS[severity] || SEVERITY_COLORS.info;
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${c.badge}`}>{severity.toUpperCase()}</span>;
};

export const StatusBadge = ({ status }) => (
  <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[status] || STATUS_COLORS.detected}`}>
    {status.replace("_", " ").toUpperCase()}
  </span>
);
