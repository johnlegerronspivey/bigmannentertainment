import React, { useState, useEffect, useCallback } from "react";
import { RefreshCw, ChevronDown, ChevronRight, Play, Package, XCircle } from "lucide-react";
import { SCANNER_API, fetcher, SeverityBadge } from "./shared";

export const ScannersTab = ({ onRefresh }) => {
  const [tools, setTools] = useState({});
  const [results, setResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [resultDetail, setResultDetail] = useState(null);
  const [running, setRunning] = useState({});
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [t, r] = await Promise.all([fetcher(`${SCANNER_API}/tools`), fetcher(`${SCANNER_API}/results?limit=30`)]);
      setTools(t);
      setResults(r);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const runScanner = async (key, url) => {
    setRunning((r) => ({ ...r, [key]: true }));
    try {
      await fetcher(url, { method: "POST" });
      fetchData();
      onRefresh();
    } catch (e) { console.error(e); }
    setRunning((r) => ({ ...r, [key]: false }));
  };

  const viewResult = async (id) => {
    if (selectedResult === id) { setSelectedResult(null); setResultDetail(null); return; }
    try { setResultDetail(await fetcher(`${SCANNER_API}/results/${id}`)); setSelectedResult(id); } catch (e) { console.error(e); }
  };

  const scanners = [
    { key: "trivy_fs", label: "Trivy Filesystem", desc: "Scan app dependencies for known vulnerabilities", url: `${SCANNER_API}/trivy/fs?target=/app&severity=CRITICAL,HIGH,MEDIUM,LOW`, icon: "FS", color: "bg-blue-500/10 text-blue-400 border-blue-500/30" },
    { key: "trivy_iac", label: "Trivy IaC", desc: "Scan Terraform/IaC for misconfigurations", url: `${SCANNER_API}/trivy/iac?target=/tmp/test_iac`, icon: "IaC", color: "bg-purple-500/10 text-purple-400 border-purple-500/30" },
    { key: "grype", label: "Grype", desc: "Anchore vulnerability scanner for dependencies", url: `${SCANNER_API}/grype?target=dir%3A/app/backend`, icon: "GR", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" },
    { key: "syft", label: "Syft SBOM", desc: "Generate Software Bill of Materials", url: `${SCANNER_API}/syft?target=/app/backend`, icon: "SB", color: "bg-amber-500/10 text-amber-400 border-amber-500/30" },
    { key: "checkov", label: "Checkov", desc: "IaC security scanner for Terraform, K8s, CloudFormation", url: `${SCANNER_API}/checkov?target=/tmp/test_iac`, icon: "CK", color: "bg-pink-500/10 text-pink-400 border-pink-500/30" },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-3">Installed Security Tools</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(tools).map(([name, info]) => (
            <div key={name} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-3 py-2">
              <div className={`w-2.5 h-2.5 rounded-full ${info.installed ? "bg-emerald-500" : "bg-red-500"}`} />
              <div>
                <div className="text-sm text-white font-medium capitalize">{name}</div>
                <div className="text-xs text-slate-500 truncate max-w-[150px]">{info.version || "Not installed"}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {scanners.map((s) => (
          <div key={s.key} data-testid={`scanner-${s.key}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className={`w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold border ${s.color}`}>{s.icon}</span>
                <div>
                  <div className="text-white font-medium text-sm">{s.label}</div>
                  <div className="text-xs text-slate-400">{s.desc}</div>
                </div>
              </div>
            </div>
            <button data-testid={`run-${s.key}`} onClick={() => runScanner(s.key, s.url)} disabled={running[s.key]} className="w-full mt-2 flex items-center justify-center gap-2 bg-cyan-600/80 hover:bg-cyan-600 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
              {running[s.key] ? <><RefreshCw className="w-4 h-4 animate-spin" /> Running...</> : <><Play className="w-4 h-4" /> Run Scan</>}
            </button>
          </div>
        ))}
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-3">Scan History</h3>
        <div className="space-y-2 max-h-[500px] overflow-y-auto">
          {results.map((r) => (
            <div key={r.id} className="bg-slate-900/50 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2.5 cursor-pointer hover:bg-slate-800/50 transition-colors" onClick={() => viewResult(r.id)}>
                <div className="flex items-center gap-3">
                  {selectedResult === r.id ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                  <span className="text-xs font-mono text-cyan-400">{r.scanner}</span>
                  <span className="text-xs text-slate-500">{r.scan_type}</span>
                  <span className={`px-1.5 py-0.5 rounded text-xs ${r.status === "completed" ? "bg-emerald-500/10 text-emerald-400" : r.status === "error" ? "bg-red-500/10 text-red-400" : "bg-yellow-500/10 text-yellow-400"}`}>{r.status}</span>
                </div>
                <div className="flex items-center gap-3">
                  {r.summary && <div className="flex items-center gap-2 text-xs">
                    {r.summary.critical > 0 && <span className="text-red-400">{r.summary.critical}C</span>}
                    {r.summary.high > 0 && <span className="text-orange-400">{r.summary.high}H</span>}
                    {r.summary.medium > 0 && <span className="text-yellow-400">{r.summary.medium}M</span>}
                    {(r.summary.total || r.summary.total_packages) > 0 && <span className="text-slate-400">Total: {r.summary.total || r.summary.total_packages}</span>}
                    {r.summary.passed !== undefined && <span className="text-emerald-400">P:{r.summary.passed}</span>}
                    {r.summary.failed !== undefined && <span className="text-red-400">F:{r.summary.failed}</span>}
                  </div>}
                  <span className="text-xs text-slate-500">{new Date(r.started_at).toLocaleString()}</span>
                </div>
              </div>
              {selectedResult === r.id && resultDetail && (
                <div className="px-4 pb-3 border-t border-slate-800/50 pt-2">
                  {resultDetail.vulnerabilities && (
                    <div className="space-y-1 max-h-60 overflow-y-auto">
                      {resultDetail.vulnerabilities.map((v, i) => (
                        <div key={i} className="flex items-center justify-between bg-slate-800/50 rounded px-3 py-1.5 text-xs">
                          <div className="flex items-center gap-2 min-w-0">
                            <SeverityBadge severity={v.severity} />
                            <span className="text-cyan-400 font-mono">{v.id}</span>
                            <span className="text-white truncate">{v.package}@{v.installed_version}</span>
                          </div>
                          <span className="text-emerald-400 shrink-0 ml-2">{v.fixed_version || "—"}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {resultDetail.misconfigurations && (
                    <div className="space-y-1 max-h-60 overflow-y-auto">
                      {resultDetail.misconfigurations.map((m, i) => (
                        <div key={i} className="bg-slate-800/50 rounded px-3 py-1.5 text-xs">
                          <div className="flex items-center gap-2">
                            <SeverityBadge severity={m.severity} />
                            <span className="text-cyan-400 font-mono">{m.id}</span>
                            <span className="text-white">{m.title}</span>
                          </div>
                          {m.resolution && <div className="text-slate-400 mt-1 ml-4">{m.resolution}</div>}
                        </div>
                      ))}
                    </div>
                  )}
                  {resultDetail.packages && (
                    <div className="space-y-1 max-h-60 overflow-y-auto">
                      <div className="text-xs text-slate-400 mb-1">By type: {JSON.stringify(resultDetail.summary?.by_type)}</div>
                      {resultDetail.packages.slice(0, 50).map((p, i) => (
                        <div key={i} className="flex items-center justify-between bg-slate-800/50 rounded px-3 py-1 text-xs">
                          <div className="flex items-center gap-2"><Package className="w-3 h-3 text-slate-500" /><span className="text-white">{p.name}</span><span className="text-slate-500">@{p.version}</span></div>
                          <div className="flex items-center gap-2"><span className="text-slate-400">{p.type}</span>{p.language && <span className="text-purple-400">{p.language}</span>}</div>
                        </div>
                      ))}
                      {resultDetail.packages.length > 50 && <div className="text-xs text-slate-500 text-center">...and {resultDetail.packages.length - 50} more</div>}
                    </div>
                  )}
                  {resultDetail.checks && (
                    <div className="space-y-1 max-h-60 overflow-y-auto">
                      {resultDetail.checks.filter((c) => c.status === "failed").map((c, i) => (
                        <div key={i} className="flex items-center gap-2 bg-red-900/10 rounded px-3 py-1.5 text-xs">
                          <XCircle className="w-3 h-3 text-red-400 shrink-0" />
                          <span className="text-red-300 font-mono">{c.check_id}</span>
                          <span className="text-white truncate">{c.resource}</span>
                          <span className="text-slate-500">{c.file}</span>
                        </div>
                      ))}
                      {resultDetail.checks.filter((c) => c.status === "passed").length > 0 && (
                        <div className="text-xs text-emerald-400 mt-1">{resultDetail.checks.filter((c) => c.status === "passed").length} checks passed</div>
                      )}
                    </div>
                  )}
                  {resultDetail.error && <div className="text-xs text-red-400 bg-red-900/10 rounded p-2">{resultDetail.error}</div>}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="text-center text-slate-400 py-6">Loading scan history...</div>}
          {!loading && results.length === 0 && <div className="text-center text-slate-500 py-6">No scan results yet. Run a scanner above.</div>}
        </div>
      </div>
    </div>
  );
};
