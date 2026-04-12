import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import { Shield, Key, AlertTriangle, CheckCircle, XCircle, Eye, RefreshCw, Search, Lock, Unlock, Clock, Activity } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const SENSITIVITY_CONFIG = {
  critical: { color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30", label: "CRITICAL" },
  high: { color: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/30", label: "HIGH" },
  medium: { color: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/30", label: "MEDIUM" },
  low: { color: "text-green-400", bg: "bg-green-500/10", border: "border-green-500/30", label: "LOW" },
};

const STATUS_CONFIG = {
  configured: { icon: CheckCircle, color: "text-emerald-400", label: "Configured" },
  missing: { icon: XCircle, color: "text-red-400", label: "Missing" },
  placeholder: { icon: AlertTriangle, color: "text-amber-400", label: "Placeholder" },
};

const CATEGORY_ICONS = {
  cloud: "fa-cloud",
  authentication: "fa-lock",
  payments: "fa-credit-card",
  blockchain: "fa-link",
  ai: "fa-brain",
  devops: "fa-code-branch",
  email: "fa-envelope",
  social: "fa-share-nodes",
  business: "fa-briefcase",
  database: "fa-database",
};

function HealthScoreRing({ score }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const ringColor = score >= 80 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <div className="relative w-36 h-36">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={radius} fill="none" stroke="#1e293b" strokeWidth="8" />
        <circle
          cx="60" cy="60" r={radius} fill="none"
          stroke={ringColor} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-white">{score}</span>
        <span className="text-xs text-slate-400 uppercase tracking-wider">Score</span>
      </div>
    </div>
  );
}

function KeyCard({ keyData }) {
  const sens = SENSITIVITY_CONFIG[keyData.sensitivity] || SENSITIVITY_CONFIG.low;
  const stat = STATUS_CONFIG[keyData.status] || STATUS_CONFIG.missing;
  const StatusIcon = stat.icon;

  return (
    <div
      data-testid={`key-card-${keyData.key_name}`}
      className={`rounded-lg border ${sens.border} ${sens.bg} p-4 transition-all hover:scale-[1.01]`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <StatusIcon size={16} className={stat.color} />
          <span className="text-sm font-semibold text-white truncate">{keyData.label}</span>
        </div>
        <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded ${sens.bg} ${sens.color}`}>
          {sens.label}
        </span>
      </div>
      <div className="font-mono text-xs text-slate-400 bg-black/30 rounded px-2 py-1.5 mb-2 overflow-hidden text-ellipsis whitespace-nowrap" data-testid={`masked-value-${keyData.key_name}`}>
        {keyData.masked_value}
      </div>
      <div className="flex items-center justify-between text-[11px] text-slate-500">
        <span>{keyData.category}</span>
        <span className={stat.color}>{stat.label}</span>
      </div>
      {keyData.fingerprint && (
        <div className="mt-1 text-[10px] text-slate-600 font-mono">
          Fingerprint: {keyData.fingerprint}
        </div>
      )}
    </div>
  );
}

function SecurityIssueCard({ issue }) {
  const severityColors = {
    critical: "border-red-500/40 bg-red-500/5",
    high: "border-orange-500/40 bg-orange-500/5",
    medium: "border-yellow-500/40 bg-yellow-500/5",
    info: "border-blue-500/40 bg-blue-500/5",
  };
  const severityText = {
    critical: "text-red-400",
    high: "text-orange-400",
    medium: "text-yellow-400",
    info: "text-blue-400",
  };

  return (
    <div className={`border rounded-lg p-4 ${severityColors[issue.severity] || severityColors.info}`} data-testid={`issue-card-${issue.title.replace(/\s+/g, '-').toLowerCase()}`}>
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle size={14} className={severityText[issue.severity]} />
        <span className={`text-xs font-bold uppercase ${severityText[issue.severity]}`}>{issue.severity}</span>
        <span className="text-sm font-medium text-white">{issue.title}</span>
      </div>
      <p className="text-xs text-slate-400 mb-2">{issue.description}</p>
      <div className="bg-black/20 rounded px-3 py-2">
        <span className="text-[10px] uppercase text-slate-500 tracking-wider">Remediation</span>
        <p className="text-xs text-slate-300 mt-1">{issue.remediation}</p>
      </div>
    </div>
  );
}

function AuditLogEntry({ entry }) {
  const actionColors = {
    vault_view: "text-blue-400",
    security_scan: "text-purple-400",
    rotation_initiated: "text-amber-400",
  };

  return (
    <div className="flex items-center gap-3 py-2 border-b border-slate-800 last:border-0">
      <Activity size={12} className={actionColors[entry.action] || "text-slate-400"} />
      <span className="text-xs text-slate-300 font-medium">{entry.action.replace(/_/g, " ")}</span>
      <span className="text-[10px] text-slate-500 font-mono">{entry.key_name}</span>
      <span className="ml-auto text-[10px] text-slate-600">{new Date(entry.timestamp).toLocaleString()}</span>
    </div>
  );
}

export default function KeyVaultPage() {
  const { user } = useAuth();
  const [vault, setVault] = useState(null);
  const [scan, setScan] = useState(null);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("vault");
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const token = localStorage.getItem("token");

  const fetchVault = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/keys/vault`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.status === "success") setVault(data.data);
    } catch (err) {
      console.error("Failed to fetch vault:", err);
    }
  }, [token]);

  const fetchScan = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/keys/security-scan`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.status === "success") setScan(data.data);
    } catch (err) {
      console.error("Failed to fetch scan:", err);
    }
  }, [token]);

  const fetchAuditLog = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/keys/audit-log?limit=50`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.status === "success") setAuditLog(data.data.entries || []);
    } catch (err) {
      console.error("Failed to fetch audit log:", err);
    }
  }, [token]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([fetchVault(), fetchScan(), fetchAuditLog()]);
      setLoading(false);
    };
    loadAll();
  }, [fetchVault, fetchScan, fetchAuditLog]);

  const handleRotate = async (keyName) => {
    try {
      const res = await fetch(`${API}/api/keys/rotate/${keyName}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.status === "success") {
        await fetchAuditLog();
      }
    } catch (err) {
      console.error("Rotation failed:", err);
    }
  };

  const filteredKeys = vault?.keys?.filter((k) => {
    const matchesSearch = searchQuery === "" || k.label.toLowerCase().includes(searchQuery.toLowerCase()) || k.key_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === "all" || k.category === categoryFilter;
    return matchesSearch && matchesCategory;
  }) || [];

  const categories = vault ? [...new Set(vault.keys.map((k) => k.category))] : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center" data-testid="key-vault-loading">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-slate-400 text-sm">Loading Key Vault...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white" data-testid="key-vault-page">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
                <Shield size={20} className="text-emerald-400" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Key Vault</h1>
                <p className="text-xs text-slate-500">Secrets management & protection dashboard</p>
              </div>
            </div>
            <button
              data-testid="refresh-vault-btn"
              onClick={() => { fetchVault(); fetchScan(); fetchAuditLog(); }}
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700 text-slate-400 hover:text-white hover:border-slate-500 transition-all text-sm"
            >
              <RefreshCw size={14} /> Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <div className="col-span-2 lg:col-span-1 flex items-center justify-center" data-testid="health-score-ring">
            <HealthScoreRing score={vault?.summary?.health_score || 0} />
          </div>
          <SummaryCard
            testId="total-keys-card"
            icon={Key} label="Total Keys" value={vault?.summary?.total_keys || 0}
            color="text-slate-300" bg="bg-slate-800"
          />
          <SummaryCard
            testId="configured-keys-card"
            icon={CheckCircle} label="Configured" value={vault?.summary?.configured || 0}
            color="text-emerald-400" bg="bg-emerald-500/10"
          />
          <SummaryCard
            testId="placeholder-keys-card"
            icon={AlertTriangle} label="Placeholder" value={vault?.summary?.placeholder || 0}
            color="text-amber-400" bg="bg-amber-500/10"
          />
          <SummaryCard
            testId="missing-keys-card"
            icon={XCircle} label="Missing" value={vault?.summary?.missing || 0}
            color="text-red-400" bg="bg-red-500/10"
          />
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-1 mb-6 bg-slate-900/50 rounded-lg p-1 w-fit" data-testid="vault-tabs">
          {[
            { id: "vault", label: "Key Vault", icon: Lock },
            { id: "scan", label: "Security Scan", icon: Shield },
            { id: "audit", label: "Audit Log", icon: Clock },
          ].map((tab) => (
            <button
              key={tab.id}
              data-testid={`tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm transition-all ${
                activeTab === tab.id
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <tab.icon size={14} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "vault" && (
          <div data-testid="vault-tab-content">
            {/* Search & Filter */}
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
              <div className="relative flex-1">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  data-testid="key-search-input"
                  type="text"
                  placeholder="Search keys..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white placeholder:text-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <select
                data-testid="category-filter"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white focus:border-emerald-500 focus:outline-none"
              >
                <option value="all">All Categories</option>
                {categories.map((c) => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
            </div>

            {/* Key Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredKeys.map((k) => (
                <KeyCard key={k.key_name} keyData={k} />
              ))}
            </div>
            {filteredKeys.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                <Key size={32} className="mx-auto mb-3 opacity-30" />
                <p>No keys match your filters</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "scan" && (
          <div data-testid="scan-tab-content">
            {scan && (
              <>
                <div className="flex items-center gap-3 mb-6">
                  <div className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                    scan.overall_status === "healthy" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" :
                    scan.overall_status === "warning" ? "bg-amber-500/10 text-amber-400 border border-amber-500/30" :
                    "bg-red-500/10 text-red-400 border border-red-500/30"
                  }`} data-testid="scan-overall-status">
                    {scan.overall_status}
                  </div>
                  <span className="text-sm text-slate-400">{scan.total_issues} issue{scan.total_issues !== 1 ? 's' : ''} found</span>
                </div>
                <div className="space-y-3">
                  {scan.issues.map((issue, idx) => (
                    <SecurityIssueCard key={idx} issue={issue} />
                  ))}
                </div>
                {scan.issues.length === 0 && (
                  <div className="text-center py-12 text-emerald-400">
                    <CheckCircle size={32} className="mx-auto mb-3" />
                    <p>No security issues detected</p>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === "audit" && (
          <div data-testid="audit-tab-content">
            <div className="bg-slate-900/50 rounded-lg border border-slate-800 p-4">
              {auditLog.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <Clock size={24} className="mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No audit entries yet</p>
                </div>
              ) : (
                auditLog.map((entry, idx) => (
                  <AuditLogEntry key={idx} entry={entry} />
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryCard({ icon: Icon, label, value, color, bg, testId }) {
  return (
    <div className={`${bg} rounded-lg border border-slate-800 p-4 flex flex-col items-center justify-center`} data-testid={testId}>
      <Icon size={20} className={`${color} mb-2`} />
      <span className="text-2xl font-bold text-white">{value}</span>
      <span className="text-xs text-slate-500 mt-1">{label}</span>
    </div>
  );
}
