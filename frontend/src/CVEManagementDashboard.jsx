import React, { useState, useEffect, useCallback } from "react";
import { Shield, AlertTriangle, RefreshCw, Scan, Server, Layers, GitBranch, Lock, Settings, Activity, Wrench, BarChart3, Bell, Users, Timer, FileBarChart, Cloud } from "lucide-react";
import { API, NOTIFICATION_API, RBAC_API, fetcher, ROLE_BADGES } from "./cve/shared";
import { OverviewTab } from "./cve/OverviewTab";
import { CVEDatabaseTab } from "./cve/CVEDatabaseTab";
import { ScannersTab } from "./cve/ScannersTab";
import { RemediationTab } from "./cve/RemediationTab";
import { GovernanceTab } from "./cve/GovernanceTab";
import { NotificationsTab } from "./cve/NotificationsTab";
import { ServicesTab, SBOMTab } from "./cve/ServicesTab";
import { CICDTab } from "./cve/CICDTab";
import { PolicyEngineTab } from "./cve/PolicyEngineTab";
import { PoliciesTab, AuditTrailTab } from "./cve/PoliciesTab";
import { UserManagementTab } from "./cve/UserManagementTab";
import { SLATrackerTab } from "./cve/SLATrackerTab";
import { ReportingTab } from "./cve/ReportingTab";
import { InfraTab } from "./cve/InfraTab";

const TABS = [
  { id: "overview", label: "Overview", icon: Shield },
  { id: "cves", label: "CVE Database", icon: AlertTriangle },
  { id: "scanners", label: "Scanners", icon: Scan },
  { id: "remediation", label: "Remediation", icon: Wrench },
  { id: "governance", label: "Governance", icon: BarChart3 },
  { id: "sla-tracker", label: "SLA Tracker", icon: Timer },
  { id: "reporting", label: "Reporting", icon: FileBarChart },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "services", label: "Services", icon: Server },
  { id: "sbom", label: "SBOM", icon: Layers },
  { id: "cicd", label: "CI/CD", icon: GitBranch },
  { id: "infra", label: "Infrastructure", icon: Cloud },
  { id: "policy-engine", label: "Policy Engine", icon: Lock },
  { id: "policies", label: "SLA Policies", icon: Settings },
  { id: "audit", label: "Audit Trail", icon: Activity },
  { id: "users", label: "Users & RBAC", icon: Users, adminOnly: true },
];

export default function CVEManagementDashboard() {
  const [tab, setTab] = useState("overview");
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [cveRole, setCveRole] = useState("analyst");
  const [cvePermissions, setCvePermissions] = useState([]);

  const fetchDashboard = useCallback(async () => {
    try { setDashboard(await fetcher(`${API}/dashboard`)); } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  const fetchUnread = useCallback(async () => {
    try {
      const data = await fetcher(`${NOTIFICATION_API}/unread-count`);
      setUnreadCount(data.unread || 0);
    } catch (e) { console.error(e); }
  }, []);

  const fetchMyRole = useCallback(async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      const data = await fetcher(`${RBAC_API}/me`, { headers: { Authorization: `Bearer ${token}` } });
      setCveRole(data.cve_role || "analyst");
      setCvePermissions(data.permissions || []);
    } catch (e) { console.error("RBAC fetch failed:", e); }
  }, []);

  useEffect(() => { fetchDashboard(); fetchUnread(); fetchMyRole(); }, [fetchDashboard, fetchUnread, fetchMyRole]);

  const hasPerm = (perm) => cvePermissions.includes(perm);
  const roleBadge = ROLE_BADGES[cveRole] || ROLE_BADGES.analyst;
  const visibleTabs = TABS.filter((t) => !t.adminOnly || hasPerm("users.view"));

  const handleScan = async () => {
    setScanning(true);
    try { await fetcher(`${API}/scan`, { method: "POST" }); fetchDashboard(); } catch (e) { console.error(e); }
    setScanning(false);
  };

  const handleSeed = async () => {
    setSeeding(true);
    try { await fetcher(`${API}/seed`, { method: "POST" }); fetchDashboard(); } catch (e) { console.error(e); }
    setSeeding(false);
  };

  return (
    <div data-testid="cve-management-dashboard" className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="border-b border-slate-800/60 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-cyan-500/10 rounded-xl"><Shield className="w-7 h-7 text-cyan-400" /></div>
              <div>
                <h1 className="text-xl font-bold text-white">CVE Management Platform</h1>
                <p className="text-xs text-slate-400">Central vulnerability brain — detect, triage, fix, verify</p>
              </div>
              <span data-testid="user-role-badge" className={`ml-2 px-2.5 py-1 rounded-lg text-xs font-semibold ${roleBadge.bg} ${roleBadge.text}`}>{roleBadge.label}</span>
            </div>
            <div className="flex items-center gap-3">
              <button data-testid="notification-bell" onClick={() => setTab("notifications")} className="relative p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors">
                <Bell className={`w-5 h-5 ${unreadCount > 0 ? "text-cyan-400" : "text-slate-400"}`} />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">{unreadCount > 99 ? "99+" : unreadCount}</span>
                )}
              </button>
              {hasPerm("cves.create") && (
                <button data-testid="seed-data-btn" onClick={handleSeed} disabled={seeding} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs transition-colors disabled:opacity-50">{seeding ? "Seeding..." : "Seed Data"}</button>
              )}
              {hasPerm("scans.run") && (
                <button data-testid="run-scan-btn" onClick={handleScan} disabled={scanning} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
                  <RefreshCw className={`w-4 h-4 ${scanning ? "animate-spin" : ""}`} /> {scanning ? "Scanning..." : "Run Scan"}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800/60 bg-slate-900/40">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1 overflow-x-auto py-1">
            {visibleTabs.map((t) => (
              <button key={t.id} data-testid={`tab-${t.id}`} onClick={() => setTab(t.id)} className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm transition-all whitespace-nowrap ${tab === t.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
                <t.icon className="w-4 h-4" /> {t.label}
                {t.id === "cves" && dashboard?.open_cves > 0 && <span className="ml-1 px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-xs">{dashboard.open_cves}</span>}
                {t.id === "notifications" && unreadCount > 0 && <span className="ml-1 px-1.5 py-0.5 bg-cyan-500/20 text-cyan-400 rounded text-xs">{unreadCount}</span>}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {tab === "overview" && <OverviewTab dashboard={dashboard} onRefresh={fetchDashboard} loading={loading} />}
        {tab === "cves" && <CVEDatabaseTab onRefresh={fetchDashboard} />}
        {tab === "scanners" && <ScannersTab onRefresh={fetchDashboard} />}
        {tab === "remediation" && <RemediationTab onRefresh={fetchDashboard} />}
        {tab === "governance" && <GovernanceTab onRefresh={fetchDashboard} />}
        {tab === "sla-tracker" && <SLATrackerTab onRefresh={fetchDashboard} />}
        {tab === "reporting" && <ReportingTab />}
        {tab === "notifications" && <NotificationsTab onRefresh={fetchDashboard} unreadCount={unreadCount} onUnreadUpdate={fetchUnread} />}
        {tab === "services" && <ServicesTab onRefresh={fetchDashboard} />}
        {tab === "sbom" && <SBOMTab onRefresh={fetchDashboard} />}
        {tab === "cicd" && <CICDTab onRefresh={fetchDashboard} />}
        {tab === "infra" && <InfraTab onRefresh={fetchDashboard} />}
        {tab === "policy-engine" && <PolicyEngineTab onRefresh={fetchDashboard} />}
        {tab === "policies" && <PoliciesTab onRefresh={fetchDashboard} />}
        {tab === "audit" && <AuditTrailTab />}
        {tab === "users" && hasPerm("users.view") && <UserManagementTab currentRole={cveRole} />}
      </div>
    </div>
  );
}
