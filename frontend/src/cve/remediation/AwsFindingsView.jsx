import React, { useState, useEffect } from "react";
import { RefreshCw, CloudLightning, Loader2, Shield } from "lucide-react";
import { REMEDIATION_API, fetcher, SeverityBadge } from "../shared";

export const AwsFindingsView = ({ awsFindings, fetchAws, fetchData }) => {
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
