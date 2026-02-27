import React, { useState, useEffect, useCallback } from "react";
import { AlertTriangle, CheckCircle, RefreshCw, Plus, Layers, Wrench, Github, GitBranch, CloudLightning, CheckCircle2 } from "lucide-react";
import { API, REMEDIATION_API, fetcher, StatCard } from "../shared";
import { AwsFindingsView } from "./AwsFindingsView";
import { ItemsView } from "./ItemsView";
import { CreateView } from "./CreateView";
import { BulkView } from "./BulkView";

export const RemediationTab = ({ onRefresh }) => {
  const [config, setConfig] = useState(null);
  const [items, setItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [cves, setCves] = useState([]);
  const [awsFindings, setAwsFindings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState({});
  const [syncing, setSyncing] = useState(false);
  const [bulkCreating, setBulkCreating] = useState(false);
  const [filterStatus, setFilterStatus] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("");
  const [view, setView] = useState("items");

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [configRes, itemsRes, cvesRes] = await Promise.all([
        fetcher(`${REMEDIATION_API}/config`),
        fetcher(`${REMEDIATION_API}/items?${new URLSearchParams({ ...(filterStatus && { status: filterStatus }), ...(filterSeverity && { severity: filterSeverity }), limit: "50" })}`),
        fetcher(`${API}/entries?status=detected&limit=50`),
      ]);
      setConfig(configRes);
      setItems(itemsRes.items || []);
      setTotalItems(itemsRes.total || 0);
      setCves(cvesRes.items || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [filterStatus, filterSeverity]);

  const fetchAws = useCallback(async () => {
    try {
      const res = await fetcher(`${REMEDIATION_API}/aws/findings`);
      setAwsFindings(res);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => { if (view === "aws") fetchAws(); }, [view, fetchAws]);

  const handleCreateIssue = async (cveId) => {
    setCreating((p) => ({ ...p, [`issue_${cveId}`]: true }));
    try {
      await fetcher(`${REMEDIATION_API}/create-issue/${cveId}`, { method: "POST" });
      fetchData();
      onRefresh();
    } catch (e) { console.error(e); }
    setCreating((p) => ({ ...p, [`issue_${cveId}`]: false }));
  };

  const handleCreatePR = async (cveId) => {
    setCreating((p) => ({ ...p, [`pr_${cveId}`]: true }));
    try {
      await fetcher(`${REMEDIATION_API}/create-pr/${cveId}`, { method: "POST" });
      fetchData();
      onRefresh();
    } catch (e) { console.error(e); }
    setCreating((p) => ({ ...p, [`pr_${cveId}`]: false }));
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await fetcher(`${REMEDIATION_API}/sync-github`, { method: "POST" });
      fetchData();
    } catch (e) { console.error(e); }
    setSyncing(false);
  };

  const handleBulkCreate = async (severity) => {
    setBulkCreating(true);
    try {
      await fetcher(`${REMEDIATION_API}/bulk-create-issues`, { method: "POST", body: JSON.stringify({ severity, limit: 10 }) });
      fetchData();
      onRefresh();
    } catch (e) { console.error(e); }
    setBulkCreating(false);
  };

  const handleStatusChange = async (itemId, newStatus) => {
    try {
      await fetcher(`${REMEDIATION_API}/items/${itemId}/status`, { method: "PUT", body: JSON.stringify({ status: newStatus }) });
      fetchData();
    } catch (e) { console.error(e); }
  };

  const stats = config?.stats || {};

  const viewTabs = [
    { id: "items", label: "Remediation Items", icon: Wrench },
    { id: "create", label: "Create from CVEs", icon: Plus },
    { id: "bulk", label: "Bulk Operations", icon: Layers },
    { id: "aws", label: "AWS Findings", icon: CloudLightning },
  ];

  return (
    <div className="space-y-6">
      <div data-testid="github-connection-card" className={`border rounded-xl p-5 ${config?.repo_connected ? "bg-emerald-900/20 border-emerald-500/30" : "bg-red-900/20 border-red-500/30"}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Github className={`w-6 h-6 ${config?.repo_connected ? "text-emerald-400" : "text-red-400"}`} />
            <div>
              <h3 className="text-white font-semibold">GitHub Integration</h3>
              {config?.repo_connected ? (
                <div>
                  <p className="text-sm text-emerald-400">Connected to <a href={config.repo_url} target="_blank" rel="noreferrer" className="underline hover:text-emerald-300">{config.repo_full_name}</a> ({config.default_branch})</p>
                  {!config.write_access && <p className="text-xs text-yellow-400 mt-1">Token has read-only access. To create issues/PRs, update your token permissions at github.com/settings/tokens</p>}
                </div>
              ) : (
                <p className="text-sm text-red-400">Not connected. Configure GITHUB_TOKEN and GITHUB_REPO in backend/.env</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button data-testid="sync-github-btn" onClick={handleSync} disabled={syncing || !config?.repo_connected} className="flex items-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs transition-colors disabled:opacity-50">
              <RefreshCw className={`w-3 h-3 ${syncing ? "animate-spin" : ""}`} /> {syncing ? "Syncing..." : "Sync GitHub"}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard icon={Wrench} label="Total Items" value={stats.total || 0} color="text-cyan-400" />
        <StatCard icon={AlertTriangle} label="Open" value={stats.open || 0} color="text-yellow-400" />
        <StatCard icon={Github} label="Issues Created" value={stats.issues_created || 0} color="text-blue-400" />
        <StatCard icon={GitBranch} label="PRs Created" value={stats.prs_created || 0} color="text-purple-400" />
        <StatCard icon={CheckCircle2} label="Merged" value={stats.merged || 0} color="text-emerald-400" />
        <StatCard icon={CheckCircle} label="Closed" value={stats.closed || 0} color="text-green-400" />
      </div>

      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2">
        {viewTabs.map((v) => (
          <button key={v.id} data-testid={`remediation-view-${v.id}`} onClick={() => setView(v.id)} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${view === v.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <v.icon className="w-4 h-4" /> {v.label}
          </button>
        ))}
      </div>

      {view === "items" && (
        <ItemsView
          items={items}
          totalItems={totalItems}
          loading={loading}
          filterStatus={filterStatus}
          setFilterStatus={setFilterStatus}
          filterSeverity={filterSeverity}
          setFilterSeverity={setFilterSeverity}
          onStatusChange={handleStatusChange}
        />
      )}
      {view === "create" && (
        <CreateView
          cves={cves}
          creating={creating}
          repoConnected={config?.repo_connected}
          onCreateIssue={handleCreateIssue}
          onCreatePR={handleCreatePR}
        />
      )}
      {view === "bulk" && (
        <BulkView
          stats={stats}
          bulkCreating={bulkCreating}
          repoConnected={config?.repo_connected}
          onBulkCreate={handleBulkCreate}
        />
      )}
      {view === "aws" && (
        <AwsFindingsView awsFindings={awsFindings} fetchAws={fetchAws} fetchData={fetchData} />
      )}
    </div>
  );
};
