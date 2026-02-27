import React, { useState, useEffect, useCallback } from "react";
import {
  Cloud, Server, GitBranch, Terminal, Box, Activity, RefreshCw, Zap,
  Database, Package, Clock, Code, Rocket
} from "lucide-react";
import { fetcher } from "../shared";
import { Collapsible, CodeBlock } from "../components";
import { StatusDot, LiveBadge } from "./helpers";
import { DeploySteps } from "./DeploySteps";
import { DeploymentLog } from "./DeploymentLog";
import { LiveLambdaPanel } from "./LiveLambdaPanel";
import { GitHubRunsPanel } from "./GitHubRunsPanel";
import { TerraformStatePanel } from "./TerraformStatePanel";
import { TerraformModulesPanel, TerraformEnvsPanel } from "./TerraformModulesPanel";
import { CdkConstructsPanel } from "./CdkConstructsPanel";

const IAC_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/iac`;

export const InfraTab = ({ onRefresh }) => {
  const [overview, setOverview] = useState(null);
  const [terraform, setTerraform] = useState(null);
  const [lambda, setLambda] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEnv, setSelectedEnv] = useState("dev");
  const [recording, setRecording] = useState(false);

  const [liveStatus, setLiveStatus] = useState(null);
  const [lambdaLive, setLambdaLive] = useState(null);
  const [ghRuns, setGhRuns] = useState(null);
  const [tfState, setTfState] = useState(null);
  const [tfModules, setTfModules] = useState(null);
  const [cdkData, setCdkData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      fetcher(`${IAC_API}/overview`).catch(() => null),
      fetcher(`${IAC_API}/terraform`).catch(() => null),
      fetcher(`${IAC_API}/lambda`).catch(() => null),
      fetcher(`${IAC_API}/workflow`).catch(() => null),
      fetcher(`${IAC_API}/deployments`).catch(() => []),
      fetcher(`${IAC_API}/live-status`).catch(() => null),
      fetcher(`${IAC_API}/lambda/live`).catch(() => null),
      fetcher(`${IAC_API}/github/runs`).catch(() => null),
      fetcher(`${IAC_API}/terraform/state?environment=${selectedEnv}`).catch(() => null),
      fetcher(`${IAC_API}/terraform/modules`).catch(() => null),
      fetcher(`${IAC_API}/cdk/constructs`).catch(() => null),
    ]).then(([ov, tf, lm, wf, dep, ls, ll, gr, ts, tm, cdk]) => {
      setOverview(ov); setTerraform(tf); setLambda(lm); setWorkflow(wf);
      setDeployments(dep); setLiveStatus(ls); setLambdaLive(ll); setGhRuns(gr);
      setTfState(ts); setTfModules(tm); setCdkData(cdk); setLoading(false);
    });
  }, [selectedEnv]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
    setTimeout(() => setRefreshing(false), 1200);
  };

  useEffect(() => {
    if (!loading) {
      fetcher(`${IAC_API}/terraform/state?environment=${selectedEnv}`).then(setTfState).catch(() => setTfState(null));
    }
  }, [selectedEnv, loading]);

  const handleRecordDeploy = async () => {
    setRecording(true);
    try {
      await fetcher(`${IAC_API}/deployments`, {
        method: "POST",
        body: JSON.stringify({ environment: selectedEnv, component: "lambda", status: "success", deployed_by: "dashboard" }),
      });
      const deps = await fetcher(`${IAC_API}/deployments`);
      setDeployments(deps);
      const ov = await fetcher(`${IAC_API}/overview`);
      setOverview(ov);
    } catch (e) { console.error(e); }
    setRecording(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-slate-500">Loading infrastructure data...</div>
      </div>
    );
  }

  const conn = liveStatus || overview?.live_connections;

  return (
    <div data-testid="infra-tab" className="space-y-6">
      {/* Connection Status Bar */}
      <div data-testid="connection-status-bar" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 text-sm text-slate-300 font-semibold">
          <Activity className="w-4 h-4 text-cyan-400" />
          Live Connections
        </div>
        <div className="flex items-center gap-3 flex-wrap flex-1">
          <div className="flex items-center gap-1.5" data-testid="conn-lambda">
            <LiveBadge connected={conn?.aws_lambda?.connected} detail={conn?.aws_lambda?.detail} />
            <span className="text-xs text-slate-500">Lambda</span>
          </div>
          <div className="flex items-center gap-1.5" data-testid="conn-s3">
            <LiveBadge connected={conn?.aws_s3?.connected} detail={conn?.aws_s3?.detail} />
            <span className="text-xs text-slate-500">S3</span>
          </div>
          <div className="flex items-center gap-1.5" data-testid="conn-github">
            <LiveBadge connected={conn?.github?.connected} detail={conn?.github?.detail} />
            <span className="text-xs text-slate-500">GitHub</span>
          </div>
        </div>
        <button data-testid="refresh-live-btn" onClick={handleRefresh} className="flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} /> Refresh
        </button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        <div data-testid="stat-terraform" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-violet-500/10"><Cloud className="w-5 h-5 text-violet-400" /></div>
            <span className="text-slate-400 text-sm">Terraform</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusDot ok={overview?.terraform?.configured} />
            <span className="text-white font-semibold">{overview?.terraform?.configured ? "Configured" : "Not Found"}</span>
          </div>
        </div>
        <div data-testid="stat-cdk" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-orange-500/10"><Code className="w-5 h-5 text-orange-400" /></div>
            <span className="text-slate-400 text-sm">CDK</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusDot ok={cdkData?.exists} />
            <span className="text-white font-semibold">{cdkData?.exists ? `${cdkData.total_constructs} Constructs` : "Not Found"}</span>
          </div>
        </div>
        <div data-testid="stat-lambda" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-amber-500/10"><Box className="w-5 h-5 text-amber-400" /></div>
            <span className="text-slate-400 text-sm">Lambda</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusDot ok={overview?.lambda?.configured || (lambdaLive?.connected && lambdaLive?.total > 0)} />
            <span className="text-white font-semibold">
              {lambdaLive?.connected && lambdaLive?.total > 0 ? `${lambdaLive.total} Live` : overview?.lambda?.configured ? "Local Config" : "Not Found"}
            </span>
          </div>
        </div>
        <div data-testid="stat-github-actions" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-cyan-500/10"><GitBranch className="w-5 h-5 text-cyan-400" /></div>
            <span className="text-slate-400 text-sm">GitHub Actions</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusDot ok={overview?.github_actions?.configured || ghRuns?.connected} />
            <span className="text-white font-semibold">
              {ghRuns?.connected ? (ghRuns.runs?.length > 0 ? `${ghRuns.runs.length} Runs` : "Connected") : overview?.github_actions?.configured ? "Active" : "Missing"}
            </span>
          </div>
        </div>
        <div data-testid="stat-deployments" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-emerald-500/10"><Rocket className="w-5 h-5 text-emerald-400" /></div>
            <span className="text-slate-400 text-sm">Deployments</span>
          </div>
          <div className="text-2xl font-bold text-white">{overview?.total_deployments || 0}</div>
        </div>
        <div data-testid="stat-tf-modules" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-indigo-500/10"><Package className="w-5 h-5 text-indigo-400" /></div>
            <span className="text-slate-400 text-sm">TF Modules</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusDot ok={tfModules?.exists} />
            <span className="text-white font-semibold">{tfModules?.exists ? `${tfModules.total_modules} Modules` : "Not Found"}</span>
          </div>
        </div>
      </div>

      {/* Environment Pills */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-3">Environments</h3>
        <div className="flex gap-3">
          {overview?.environments?.map((env) => (
            <button key={env.name} data-testid={`env-${env.name}`} onClick={() => setSelectedEnv(env.name)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedEnv === env.name ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30" : "bg-slate-900/50 text-slate-400 border border-slate-700/50 hover:border-slate-600"}`}>
              <StatusDot ok={env.configured} /> {env.name.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <Collapsible title="AWS Lambda Functions (Live)" icon={Zap} defaultOpen testId="section-lambda-live" badge={<LiveBadge connected={lambdaLive?.connected} detail={lambdaLive?.error || "OK"} />}>
        <LiveLambdaPanel data={lambdaLive} />
      </Collapsible>

      <Collapsible title="GitHub Actions Runs (Live)" icon={GitBranch} testId="section-github-runs" badge={<LiveBadge connected={ghRuns?.connected} detail={ghRuns?.error || "OK"} />}>
        <GitHubRunsPanel data={ghRuns} />
      </Collapsible>

      <Collapsible title={`Terraform State — ${selectedEnv.toUpperCase()} (Live)`} icon={Database} testId="section-terraform-state" badge={<LiveBadge connected={tfState?.connected} detail={tfState?.error || "OK"} />}>
        <TerraformStatePanel data={tfState} />
      </Collapsible>

      <Collapsible title={`Terraform Modules (${tfModules?.total_modules || 0})`} icon={Package} defaultOpen testId="section-terraform-modules" badge={tfModules?.exists ? <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">{tfModules.total_resources} resources</span> : null}>
        <TerraformModulesPanel data={tfModules} />
      </Collapsible>

      <Collapsible title="Terraform Environments" icon={Cloud} testId="section-terraform-envs" badge={tfModules?.environments?.length ? <span className="text-xs text-slate-500">{tfModules.environments.length} configured</span> : null}>
        <TerraformEnvsPanel data={tfModules} />
      </Collapsible>

      <Collapsible title={`CDK Constructs (${cdkData?.total_constructs || 0})`} icon={Code} defaultOpen testId="section-cdk-constructs" badge={cdkData?.exists ? <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-orange-500/15 text-orange-300 border border-orange-500/30">{cdkData.total_services} services</span> : null}>
        <CdkConstructsPanel data={cdkData} />
      </Collapsible>

      <Collapsible title="Terraform Configuration (Local)" icon={Cloud} testId="section-terraform">
        <div className="space-y-4 pt-3">
          {terraform?.environments?.[selectedEnv]?.exists && (
            <div>
              <div className="text-sm text-slate-300 font-medium mb-2">Environment Variables ({selectedEnv})</div>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(terraform.environments[selectedEnv].parsed || {}).map(([k, v]) => (
                  <div key={k} className="bg-slate-900/50 rounded-lg px-3 py-2">
                    <div className="text-[10px] text-slate-500 uppercase">{k}</div>
                    <div className="text-sm text-slate-300 font-mono truncate">{v}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {terraform?.main_tf && <CodeBlock code={terraform.main_tf} title="main.tf" />}
          {terraform?.outputs_tf && <CodeBlock code={terraform.outputs_tf} title="outputs.tf" />}
        </div>
      </Collapsible>

      <Collapsible title="Lambda Function (Local Config)" icon={Box} testId="section-lambda">
        <div className="space-y-4 pt-3">
          {lambda && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                { label: "Runtime", value: lambda.runtime },
                { label: "Handler", value: lambda.handler_entry },
                { label: "Timeout", value: `${lambda.timeout}s` },
                { label: "Memory", value: `${lambda.memory_mb} MB` },
              ].map(({ label, value }) => (
                <div key={label} className="bg-slate-900/50 rounded-lg px-3 py-2">
                  <div className="text-[10px] text-slate-500">{label}</div>
                  <div className="text-sm text-slate-300 font-mono">{value}</div>
                </div>
              ))}
            </div>
          )}
          {lambda?.requirements?.packages?.length > 0 && (
            <div>
              <div className="text-sm text-slate-300 font-medium mb-2">Dependencies</div>
              <div className="flex flex-wrap gap-2">
                {lambda.requirements.packages.map((p, i) => (
                  <span key={i} className="px-3 py-1 bg-slate-900/60 border border-slate-700/50 rounded-lg text-xs text-slate-300 font-mono">{p}</span>
                ))}
              </div>
            </div>
          )}
          {lambda?.handler && <div className="text-xs text-slate-500">{lambda.handler.file} - {lambda.handler.lines} lines</div>}
        </div>
      </Collapsible>

      <Collapsible title="GitHub Actions Workflow (Local)" icon={GitBranch} testId="section-workflow">
        <div className="pt-3">
          {workflow?.exists ? <CodeBlock code={workflow.content} title={workflow.file} /> : <div className="text-sm text-slate-500">No workflow file found</div>}
        </div>
      </Collapsible>

      <Collapsible title={`Deploy Commands - ${selectedEnv.toUpperCase()}`} icon={Terminal} testId="section-deploy-commands">
        <DeploySteps environment={selectedEnv} />
        <div className="mt-4 pt-4 border-t border-slate-700/30 flex items-center gap-3">
          <button data-testid="record-deployment-btn" onClick={handleRecordDeploy} disabled={recording} className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
            <Rocket className="w-4 h-4" /> {recording ? "Recording..." : "Record Deployment"}
          </button>
          <span className="text-xs text-slate-500">Log a manual deployment to {selectedEnv}</span>
        </div>
      </Collapsible>

      <Collapsible title="Deployment History" icon={Clock} defaultOpen testId="section-deploy-history">
        <DeploymentLog deployments={deployments} />
      </Collapsible>
    </div>
  );
};
