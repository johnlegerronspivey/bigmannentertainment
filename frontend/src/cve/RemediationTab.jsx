import React, { useState, useEffect, useCallback } from "react";
import { AlertTriangle, CheckCircle, RefreshCw, Plus, Layers, Wrench, Github, ExternalLink, GitBranch, ArrowUpRight, CloudLightning, Loader2, CheckCircle2, Shield } from "lucide-react";
import { API, REMEDIATION_API, SEVERITY_COLORS, fetcher, StatCard, SeverityBadge } from "./shared";

const REMEDIATION_STATUS_COLORS = {
  open: "bg-slate-500/20 text-slate-300",
  issue_created: "bg-yellow-500/20 text-yellow-300",
  pr_created: "bg-blue-500/20 text-blue-300",
  in_review: "bg-purple-500/20 text-purple-300",
  merged: "bg-emerald-500/20 text-emerald-300",
  deployed: "bg-cyan-500/20 text-cyan-300",
  verified: "bg-green-500/20 text-green-300",
  closed: "bg-slate-600/20 text-slate-400",
  wont_fix: "bg-slate-600/20 text-slate-400",
};

const AwsFindingsView = ({ awsFindings, fetchAws, fetchData }) => {
  const [securityHub, setSecurityHub] = useState(null);
  const [awsTab, setAwsTab] = useState("inspector");
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetcher(`${REMEDIATION_API}/aws/security-hub`).then(setSecurityHub).catch(console.error);
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try { await fetcher(`${REMEDIATION_API}/aws/sync`, { method: "POST" }); fetchAws(); fetchData(); } catch (e) { console.error(e); }
    setSyncing(false);
  };

  return (
    <div className="space-y-4">
      <div className={`border rounded-xl p-4 ${awsFindings?.source === "aws_inspector" ? "bg-orange-900/15 border-orange-500/30" : "bg-slate-800/40 border-slate-700/50"}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CloudLightning className={`w-5 h-5 ${awsFindings?.source === "aws_inspector" ? "text-orange-400" : "text-slate-500"}`} />
            <div>
              <h3 className="text-white font-semibold text-sm">AWS Security Integration</h3>
              <p className="text-xs text-slate-400">
                Inspector: <span className={awsFindings?.source === "aws_inspector" ? "text-emerald-400" : "text-red-400"}>{awsFindings?.source === "aws_inspector" ? "Connected" : "Unavailable"}</span>
                {" | "}Security Hub: <span className={securityHub?.source === "security_hub" ? "text-emerald-400" : "text-red-400"}>{securityHub?.source === "security_hub" ? "Connected" : "Unavailable"}</span>
              </p>
            </div>
          </div>
          <button data-testid="sync-aws-btn" onClick={handleSync} disabled={syncing} className="flex items-center gap-2 px-3 py-2 bg-orange-600/20 hover:bg-orange-600/40 text-orange-300 border border-orange-500/30 rounded-lg text-xs transition-colors disabled:opacity-50">
            <RefreshCw className={`w-3 h-3 ${syncing ? "animate-spin" : ""}`} /> {syncing ? "Syncing..." : "Sync AWS"}
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {[
          { id: "inspector", label: `Inspector (${awsFindings?.count || 0})` },
          { id: "security-hub", label: `Security Hub (${securityHub?.count || 0})` },
        ].map((t) => (
          <button key={t.id} data-testid={`aws-tab-${t.id}`} onClick={() => setAwsTab(t.id)} className={`px-3 py-1.5 rounded-lg text-xs transition-all ${awsTab === t.id ? "bg-orange-500/15 text-orange-400 font-medium border border-orange-500/30" : "text-slate-400 hover:text-white bg-slate-800/40 border border-slate-700/50"}`}>
            {t.label}
          </button>
        ))}
      </div>

      {awsTab === "inspector" && (
        <>
          {!awsFindings ? (
            <div className="text-center py-12 text-slate-400"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" /> Loading...</div>
          ) : awsFindings.findings?.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <CloudLightning className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-white text-sm font-medium mb-1">No Active Inspector Findings</p>
              <p className="text-slate-400 text-xs">{awsFindings.source === "aws_inspector" ? "Your AWS Inspector has no active vulnerability findings." : "AWS Inspector may not be enabled in your account."}</p>
            </div>
          ) : (
            <div className="space-y-2">
              {awsFindings.findings.map((f, i) => (
                <div key={f.id || i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <SeverityBadge severity={f.severity || "medium"} />
                        <span className="text-xs text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded">Inspector</span>
                        {f.type && <span className="text-xs text-slate-500">{f.type}</span>}
                      </div>
                      <h4 className="text-white text-sm font-medium">{f.title}</h4>
                      {f.description && <p className="text-xs text-slate-400 mt-1 line-clamp-2">{f.description}</p>}
                      {f.resources?.length > 0 && <p className="text-xs text-slate-500 mt-1">Resources: {f.resources.join(", ")}</p>}
                    </div>
                    {f.first_observed && <span className="text-xs text-slate-500 whitespace-nowrap">{new Date(f.first_observed).toLocaleDateString()}</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {awsTab === "security-hub" && (
        <>
          {!securityHub ? (
            <div className="text-center py-12 text-slate-400"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" /> Loading...</div>
          ) : securityHub.findings?.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <Shield className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-white text-sm font-medium mb-1">No Security Hub Findings</p>
              <p className="text-slate-400 text-xs">{securityHub.source === "security_hub" ? "No new findings in Security Hub." : securityHub.note || "Security Hub may not be enabled."}</p>
            </div>
          ) : (
            <div className="space-y-2">
              {securityHub.findings.map((f, i) => (
                <div key={f.id || i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <SeverityBadge severity={f.severity || "medium"} />
                        <span className="text-xs text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">{f.product || "Security Hub"}</span>
                        {f.compliance_status && <span className={`text-xs px-2 py-0.5 rounded ${f.compliance_status === "PASSED" ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>{f.compliance_status}</span>}
                      </div>
                      <h4 className="text-white text-sm font-medium">{f.title}</h4>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

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
        {[
          { id: "items", label: "Remediation Items", icon: Wrench },
          { id: "create", label: "Create from CVEs", icon: Plus },
          { id: "bulk", label: "Bulk Operations", icon: Layers },
          { id: "aws", label: "AWS Findings", icon: CloudLightning },
        ].map((v) => (
          <button key={v.id} data-testid={`remediation-view-${v.id}`} onClick={() => setView(v.id)} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${view === v.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <v.icon className="w-4 h-4" /> {v.label}
          </button>
        ))}
      </div>

      {view === "items" && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <select data-testid="remediation-status-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="">All Statuses</option>
              {["open", "issue_created", "pr_created", "in_review", "merged", "deployed", "verified", "closed", "wont_fix"].map((s) => <option key={s} value={s}>{s.replace(/_/g, " ").toUpperCase()}</option>)}
            </select>
            <select data-testid="remediation-severity-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
              <option value="">All Severities</option>
              {["critical", "high", "medium", "low"].map((s) => <option key={s} value={s}>{s.toUpperCase()}</option>)}
            </select>
            <span className="text-sm text-slate-400 ml-auto">{totalItems} item{totalItems !== 1 ? "s" : ""}</span>
          </div>

          {loading ? (
            <div className="text-center py-12 text-slate-400"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" /> Loading...</div>
          ) : items.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <Wrench className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400 text-sm">No remediation items yet. Create issues from the CVE database.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {items.map((item) => (
                <div key={item.id} data-testid={`remediation-item-${item.id}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <SeverityBadge severity={item.severity} />
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${REMEDIATION_STATUS_COLORS[item.status] || REMEDIATION_STATUS_COLORS.open}`}>{item.status.replace(/_/g, " ").toUpperCase()}</span>
                        <span className="text-xs text-slate-500 font-mono">{item.cve_id}</span>
                      </div>
                      <h4 className="text-white text-sm font-medium truncate">{item.title || item.cve_id}</h4>
                      {item.affected_package && <p className="text-xs text-slate-400 mt-1">Package: <span className="text-slate-300 font-mono">{item.affected_package}</span> {item.affected_version && `@ ${item.affected_version}`} {item.fixed_version && <span className="text-emerald-400">→ {item.fixed_version}</span>}</p>}
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {item.github_issue_url && (
                        <a href={item.github_issue_url} target="_blank" rel="noreferrer" data-testid={`issue-link-${item.id}`} className="flex items-center gap-1 px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded text-xs text-white transition-colors">
                          <Github className="w-3 h-3" /> #{item.github_issue_number} <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {item.github_pr_url && (
                        <a href={item.github_pr_url} target="_blank" rel="noreferrer" data-testid={`pr-link-${item.id}`} className="flex items-center gap-1 px-2 py-1 bg-purple-600/30 hover:bg-purple-600/50 rounded text-xs text-purple-300 transition-colors">
                          <GitBranch className="w-3 h-3" /> PR #{item.github_pr_number} <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      <select className="bg-slate-700 border border-slate-600 rounded px-2 py-1 text-xs text-white" value={item.status} onChange={(e) => handleStatusChange(item.id, e.target.value)}>
                        {["open", "issue_created", "pr_created", "in_review", "merged", "deployed", "verified", "closed", "wont_fix"].map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {view === "create" && (
        <div className="space-y-4">
          <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
            <h3 className="text-white font-semibold mb-1">Create GitHub Issues & PRs from Detected CVEs</h3>
            <p className="text-sm text-slate-400">Select a CVE below to create a GitHub issue or pull request for automated remediation.</p>
          </div>

          {cves.length === 0 ? (
            <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
              <CheckCircle className="w-10 h-10 text-emerald-600 mx-auto mb-3" />
              <p className="text-slate-400 text-sm">No open CVEs detected. All vulnerabilities have been triaged.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {cves.map((cve) => (
                <div key={cve.id} data-testid={`cve-remediate-${cve.id}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 flex items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <SeverityBadge severity={cve.severity} />
                      <span className="text-xs text-slate-500 font-mono">{cve.cve_id}</span>
                    </div>
                    <h4 className="text-white text-sm font-medium truncate">{cve.title}</h4>
                    {cve.affected_package && <p className="text-xs text-slate-400 mt-1"><span className="font-mono text-slate-300">{cve.affected_package}</span> {cve.affected_version && `@ ${cve.affected_version}`} {cve.fixed_version && <span className="text-emerald-400">→ fix: {cve.fixed_version}</span>}</p>}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button data-testid={`create-issue-${cve.id}`} onClick={() => handleCreateIssue(cve.id)} disabled={creating[`issue_${cve.id}`] || !config?.repo_connected} className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-600/20 hover:bg-yellow-600/40 text-yellow-300 border border-yellow-500/30 rounded-lg text-xs transition-colors disabled:opacity-50">
                      {creating[`issue_${cve.id}`] ? <Loader2 className="w-3 h-3 animate-spin" /> : <Github className="w-3 h-3" />} Create Issue
                    </button>
                    <button data-testid={`create-pr-${cve.id}`} onClick={() => handleCreatePR(cve.id)} disabled={creating[`pr_${cve.id}`] || !config?.repo_connected || !cve.fixed_version} className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 border border-purple-500/30 rounded-lg text-xs transition-colors disabled:opacity-50" title={!cve.fixed_version ? "No fixed version available" : ""}>
                      {creating[`pr_${cve.id}`] ? <Loader2 className="w-3 h-3 animate-spin" /> : <GitBranch className="w-3 h-3" />} Create PR
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {view === "bulk" && (
        <div className="space-y-4">
          <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
            <h3 className="text-white font-semibold mb-1">Bulk Issue Creation</h3>
            <p className="text-sm text-slate-400">Automatically create GitHub issues for all detected CVEs matching a severity level.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {["critical", "high", "medium", "low"].map((sev) => {
              const c = SEVERITY_COLORS[sev];
              const count = stats.by_severity?.[sev] || 0;
              return (
                <div key={sev} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className={`${c.text} font-semibold text-sm uppercase`}>{sev}</h4>
                    <span className={`${c.text} text-2xl font-bold`}>{count}</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-4">{count} active remediation item{count !== 1 ? "s" : ""}</p>
                  <button data-testid={`bulk-create-${sev}`} onClick={() => handleBulkCreate(sev)} disabled={bulkCreating || !config?.repo_connected} className={`w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-50 ${c.bg} border ${c.border} ${c.text} hover:opacity-80`}>
                    {bulkCreating ? <Loader2 className="w-3 h-3 animate-spin" /> : <ArrowUpRight className="w-3 h-3" />}
                    Create Issues for {sev}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {view === "aws" && (
        <AwsFindingsView awsFindings={awsFindings} fetchAws={fetchAws} fetchData={fetchData} />
      )}
    </div>
  );
};
