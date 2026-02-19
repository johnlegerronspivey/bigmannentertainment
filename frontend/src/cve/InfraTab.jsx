import React, { useState, useEffect, useCallback } from "react";
import {
  Cloud, Server, GitBranch, Terminal, CheckCircle, XCircle, Copy,
  ChevronDown, ChevronRight, Rocket, Clock, Box, Wifi, WifiOff,
  Activity, RefreshCw, ExternalLink, Zap, Database, AlertTriangle,
  Shield, Globe, Bell, Lock, BookOpen, Film, Layers, Package, Code
} from "lucide-react";
import { fetcher } from "./shared";

const IAC_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/iac`;

/* ── tiny helpers ───────────────────────────────────────────────── */
const StatusDot = ({ ok }) => (
  <span className={`inline-block w-2.5 h-2.5 rounded-full ${ok ? "bg-emerald-400" : "bg-slate-600"}`} />
);

const LiveBadge = ({ connected, detail }) => (
  <span
    data-testid="live-badge"
    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${
      connected ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30" : "bg-slate-700/60 text-slate-400 border border-slate-600/40"
    }`}
    title={detail}
  >
    {connected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
    {connected ? "LIVE" : "OFFLINE"}
  </span>
);

const CodeBlock = ({ code, title }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <div className="relative group">
      {title && <div className="text-xs text-slate-500 mb-1">{title}</div>}
      <pre className="bg-slate-950 rounded-lg p-3 text-xs text-green-400 font-mono overflow-x-auto max-h-[320px] whitespace-pre">{code}</pre>
      <button
        onClick={handleCopy}
        data-testid={`copy-${(title || "code").toLowerCase().replace(/\s+/g, "-")}`}
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1.5 bg-slate-800 hover:bg-slate-700 rounded text-slate-400 transition-all"
      >
        <Copy className="w-3.5 h-3.5" />
        {copied && <span className="absolute -top-6 right-0 text-[10px] bg-emerald-600 text-white px-1.5 py-0.5 rounded">Copied</span>}
      </button>
    </div>
  );
};

const Collapsible = ({ title, icon: Icon, children, defaultOpen = false, testId, badge }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
      <button
        data-testid={testId}
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-slate-800/80 transition-colors"
      >
        {Icon && <Icon className="w-5 h-5 text-cyan-400 flex-shrink-0" />}
        <span className="text-white font-semibold flex-1">{title}</span>
        {badge}
        {open ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
      </button>
      {open && <div className="px-5 pb-5 border-t border-slate-700/30">{children}</div>}
    </div>
  );
};

/* ── deploy steps (local commands) ──────────────────────────────── */
const DeploySteps = ({ environment }) => {
  const [commands, setCommands] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    setLoading(true);
    fetcher(`${IAC_API}/commands/${environment}`)
      .then(setCommands)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [environment]);
  if (loading) return <div className="text-slate-500 text-sm py-4">Loading commands...</div>;
  if (!commands) return null;
  return (
    <div className="space-y-3 pt-3">
      {commands.steps.map((step, i) => (
        <div key={i}>
          <div className="text-sm text-slate-300 font-medium mb-1">{step.title}</div>
          <div className="text-xs text-slate-500 mb-1">{step.description}</div>
          <CodeBlock code={step.command} />
        </div>
      ))}
    </div>
  );
};

/* ── deployment log (MongoDB) ───────────────────────────────────── */
const DeploymentLog = ({ deployments }) => {
  if (!deployments || deployments.length === 0) {
    return <div className="text-slate-500 text-sm text-center py-6">No deployments recorded yet</div>;
  }
  return (
    <div className="space-y-2 pt-3">
      {deployments.map((d, i) => (
        <div key={i} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-4 py-3">
          <div className={`p-1.5 rounded-lg ${d.status === "success" ? "bg-emerald-500/10" : "bg-red-500/10"}`}>
            {d.status === "success" ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm text-white font-medium">{d.component}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-cyan-500/15 text-cyan-300">{d.environment}</span>
            </div>
            {d.notes && <div className="text-xs text-slate-500 truncate">{d.notes}</div>}
          </div>
          <div className="text-xs text-slate-500 whitespace-nowrap">{d.deployed_by}</div>
          <div className="text-xs text-slate-600 whitespace-nowrap">{new Date(d.deployed_at).toLocaleString()}</div>
        </div>
      ))}
    </div>
  );
};

/* ── Live Lambda functions panel ────────────────────────────────── */
const LiveLambdaPanel = ({ data }) => {
  if (!data) return <div className="text-slate-500 text-sm py-4">Loading...</div>;
  if (!data.connected) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (data.error) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (!data.functions || data.functions.length === 0) return <div className="text-slate-500 text-sm py-4">No Lambda functions found in {data.region || "region"}</div>;

  return (
    <div className="space-y-3 pt-3">
      <div className="text-xs text-slate-500 mb-2">{data.total} function(s) found</div>
      {data.functions.map((fn, i) => (
        <div key={i} data-testid={`live-lambda-${fn.name}`} className="bg-slate-900/60 border border-slate-700/40 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-white font-semibold text-sm">{fn.name}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${fn.state === "Active" ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"}`}>
                {fn.state}
              </span>
            </div>
            <span className="text-xs text-slate-600">{fn.runtime}</span>
          </div>
          {fn.description && <div className="text-xs text-slate-400 mb-3">{fn.description}</div>}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 mb-3">
            <div className="bg-slate-800/60 rounded px-3 py-2">
              <div className="text-[10px] text-slate-500">Memory</div>
              <div className="text-sm text-slate-300">{fn.memory_mb} MB</div>
            </div>
            <div className="bg-slate-800/60 rounded px-3 py-2">
              <div className="text-[10px] text-slate-500">Timeout</div>
              <div className="text-sm text-slate-300">{fn.timeout}s</div>
            </div>
            <div className="bg-slate-800/60 rounded px-3 py-2">
              <div className="text-[10px] text-slate-500">Code Size</div>
              <div className="text-sm text-slate-300">{(fn.code_size_bytes / 1024).toFixed(1)} KB</div>
            </div>
            <div className="bg-slate-800/60 rounded px-3 py-2">
              <div className="text-[10px] text-slate-500">Handler</div>
              <div className="text-sm text-slate-300 font-mono truncate">{fn.handler}</div>
            </div>
          </div>
          {fn.metrics && (
            <div className="grid grid-cols-4 gap-2">
              <div className="bg-cyan-500/5 border border-cyan-500/10 rounded px-3 py-2 text-center">
                <div className="text-[10px] text-cyan-400">Invocations (24h)</div>
                <div className="text-lg font-bold text-white">{fn.metrics.invocations ?? "-"}</div>
              </div>
              <div className="bg-red-500/5 border border-red-500/10 rounded px-3 py-2 text-center">
                <div className="text-[10px] text-red-400">Errors (24h)</div>
                <div className="text-lg font-bold text-white">{fn.metrics.errors ?? "-"}</div>
              </div>
              <div className="bg-violet-500/5 border border-violet-500/10 rounded px-3 py-2 text-center">
                <div className="text-[10px] text-violet-400">Avg Duration</div>
                <div className="text-lg font-bold text-white">{fn.metrics.duration != null ? `${fn.metrics.duration}ms` : "-"}</div>
              </div>
              <div className="bg-amber-500/5 border border-amber-500/10 rounded px-3 py-2 text-center">
                <div className="text-[10px] text-amber-400">Throttles (24h)</div>
                <div className="text-lg font-bold text-white">{fn.metrics.throttles ?? "-"}</div>
              </div>
            </div>
          )}
          {fn.last_modified && (
            <div className="text-[10px] text-slate-600 mt-2">Last modified: {new Date(fn.last_modified).toLocaleString()}</div>
          )}
        </div>
      ))}
    </div>
  );
};

/* ── Live GitHub Actions panel ──────────────────────────────────── */
const conclusionColor = {
  success: "bg-emerald-500/15 text-emerald-300",
  failure: "bg-red-500/15 text-red-300",
  cancelled: "bg-slate-500/15 text-slate-300",
  skipped: "bg-slate-500/15 text-slate-400",
  timed_out: "bg-amber-500/15 text-amber-300",
};

const GitHubRunsPanel = ({ data }) => {
  if (!data) return <div className="text-slate-500 text-sm py-4">Loading...</div>;
  if (!data.connected) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (data.error) {
    return (
      <div className="pt-3">
        <div className="text-amber-400 text-sm mb-3"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>
        {data.available_repos && data.available_repos.length > 0 && (
          <div>
            <div className="text-xs text-slate-500 mb-2">Available repositories:</div>
            <div className="space-y-1">
              {data.available_repos.map((r, i) => (
                <div key={i} className="bg-slate-900/50 rounded px-3 py-2 text-sm text-slate-300 font-mono flex items-center gap-2">
                  <GitBranch className="w-3.5 h-3.5 text-slate-500" />
                  {r.full_name}
                  {r.private && <span className="text-[10px] bg-amber-500/15 text-amber-300 px-1.5 py-0.5 rounded">private</span>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
  if (!data.runs || data.runs.length === 0) return <div className="text-slate-500 text-sm py-4">No workflow runs found for {data.repo}</div>;

  return (
    <div className="space-y-2 pt-3">
      <div className="text-xs text-slate-500 mb-2">Repo: <span className="text-slate-300 font-mono">{data.repo}</span></div>
      {data.runs.map((run) => (
        <div key={run.id} data-testid={`gh-run-${run.id}`} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-4 py-3">
          <div className={`p-1.5 rounded-lg ${run.conclusion === "success" ? "bg-emerald-500/10" : run.conclusion === "failure" ? "bg-red-500/10" : "bg-slate-600/10"}`}>
            {run.conclusion === "success" ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : run.conclusion === "failure" ? <XCircle className="w-4 h-4 text-red-400" /> : <Clock className="w-4 h-4 text-slate-400" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm text-white font-medium truncate">{run.name}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${conclusionColor[run.conclusion] || "bg-slate-600/30 text-slate-400"}`}>
                {run.conclusion || run.status}
              </span>
            </div>
            <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
              <span>#{run.run_number}</span>
              <span>{run.branch}</span>
              <span>{run.event}</span>
            </div>
          </div>
          {run.html_url && (
            <a href={run.html_url} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300" data-testid={`gh-run-link-${run.id}`}>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
          <div className="text-xs text-slate-600 whitespace-nowrap">{run.created_at ? new Date(run.created_at).toLocaleString() : ""}</div>
        </div>
      ))}
    </div>
  );
};

/* ── Terraform State panel ──────────────────────────────────────── */
const TerraformStatePanel = ({ data }) => {
  if (!data) return <div className="text-slate-500 text-sm py-4">Loading...</div>;
  if (!data.connected) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (data.error) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (!data.resources || data.resources.length === 0) return <div className="text-slate-500 text-sm py-4">No resources in state for {data.environment}</div>;

  return (
    <div className="pt-3">
      <div className="flex items-center gap-4 mb-3 text-xs text-slate-500">
        <span>Terraform v{data.terraform_version}</span>
        <span>Serial: {data.serial}</span>
        <span>{data.total_resources} resource(s)</span>
      </div>
      <div className="space-y-1">
        {data.resources.map((r, i) => (
          <div key={i} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-4 py-2.5">
            <Database className="w-4 h-4 text-violet-400 flex-shrink-0" />
            <span className="text-sm text-cyan-300 font-mono">{r.type}</span>
            <span className="text-sm text-white">{r.name}</span>
            <span className="text-[10px] text-slate-600 ml-auto">{r.instances} instance(s)</span>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ── Terraform Modules panel ─────────────────────────────────────── */
const MODULE_ICONS = {
  shield: Shield, globe: Globe, database: Database, activity: Activity,
  zap: Zap, "git-branch": GitBranch, bell: Bell, lock: Lock,
  "book-open": BookOpen, film: Film, layers: Layers, box: Box,
};

const CATEGORY_COLORS = {
  auth: "border-violet-500/30 bg-violet-500/5",
  hosting: "border-cyan-500/30 bg-cyan-500/5",
  database: "border-amber-500/30 bg-amber-500/5",
  streaming: "border-pink-500/30 bg-pink-500/5",
  compute: "border-yellow-500/30 bg-yellow-500/5",
  events: "border-teal-500/30 bg-teal-500/5",
  notifications: "border-orange-500/30 bg-orange-500/5",
  security: "border-red-500/30 bg-red-500/5",
  ledger: "border-indigo-500/30 bg-indigo-500/5",
  media: "border-fuchsia-500/30 bg-fuchsia-500/5",
  orchestration: "border-emerald-500/30 bg-emerald-500/5",
  networking: "border-sky-500/30 bg-sky-500/5",
  other: "border-slate-500/30 bg-slate-500/5",
};

const CATEGORY_ICON_COLORS = {
  auth: "text-violet-400", hosting: "text-cyan-400", database: "text-amber-400",
  streaming: "text-pink-400", compute: "text-yellow-400", events: "text-teal-400",
  notifications: "text-orange-400", security: "text-red-400", ledger: "text-indigo-400",
  media: "text-fuchsia-400", orchestration: "text-emerald-400", networking: "text-sky-400", other: "text-slate-400",
};

const TerraformModuleCard = ({ mod }) => {
  const [expanded, setExpanded] = useState(false);
  const [activeFile, setActiveFile] = useState("main.tf");
  const Icon = MODULE_ICONS[mod.icon] || Box;
  const borderColor = CATEGORY_COLORS[mod.category] || CATEGORY_COLORS.other;
  const iconColor = CATEGORY_ICON_COLORS[mod.category] || CATEGORY_ICON_COLORS.other;

  return (
    <div data-testid={`tf-module-${mod.name}`} className={`border rounded-xl overflow-hidden transition-all ${borderColor}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-800/40 transition-colors"
        data-testid={`tf-module-toggle-${mod.name}`}
      >
        <Icon className={`w-5 h-5 flex-shrink-0 ${iconColor}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-white font-semibold text-sm">{mod.name}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-700/60 text-slate-400">{mod.category}</span>
          </div>
          <div className="text-xs text-slate-500 truncate">{mod.description}</div>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span>{mod.resource_count} resource{mod.resource_count !== 1 ? "s" : ""}</span>
          <span>{mod.file_count} file{mod.file_count !== 1 ? "s" : ""}</span>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
      </button>
      {expanded && (
        <div className="px-4 pb-4 border-t border-slate-700/30 space-y-3 pt-3">
          {mod.resources.length > 0 && (
            <div>
              <div className="text-[10px] text-slate-500 uppercase mb-1.5 tracking-wider">Resources</div>
              <div className="flex flex-wrap gap-1.5">
                {mod.resources.map((r, i) => (
                  <span key={i} className="px-2 py-1 bg-slate-900/60 border border-slate-700/40 rounded text-xs font-mono text-cyan-300">
                    {r.type}<span className="text-slate-500">.</span><span className="text-white">{r.name}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
          {mod.variables.length > 0 && (
            <div>
              <div className="text-[10px] text-slate-500 uppercase mb-1.5 tracking-wider">Variables</div>
              <div className="flex flex-wrap gap-1.5">
                {mod.variables.map((v, i) => (
                  <span key={i} className="px-2 py-1 bg-slate-800/60 rounded text-xs font-mono text-slate-300">{v}</span>
                ))}
              </div>
            </div>
          )}
          {mod.outputs.length > 0 && (
            <div>
              <div className="text-[10px] text-slate-500 uppercase mb-1.5 tracking-wider">Outputs</div>
              <div className="flex flex-wrap gap-1.5">
                {mod.outputs.map((o, i) => (
                  <span key={i} className="px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded text-xs font-mono text-emerald-300">{o}</span>
                ))}
              </div>
            </div>
          )}
          {mod.files && Object.keys(mod.files).length > 0 && (
            <div>
              <div className="flex gap-1 mb-2">
                {Object.keys(mod.files).map((fname) => (
                  <button
                    key={fname}
                    onClick={() => setActiveFile(fname)}
                    data-testid={`tf-file-tab-${mod.name}-${fname.replace(".", "-")}`}
                    className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                      activeFile === fname ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30" : "bg-slate-800/60 text-slate-500 hover:text-slate-300"
                    }`}
                  >
                    {fname}
                  </button>
                ))}
              </div>
              {mod.files[activeFile] && <CodeBlock code={mod.files[activeFile]} title={`${mod.name}/${activeFile}`} />}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const TerraformModulesPanel = ({ data }) => {
  if (!data) return <div className="text-slate-500 text-sm py-4">Loading modules...</div>;
  if (!data.exists) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error || "Modules not found"}</div>;

  return (
    <div className="space-y-4 pt-3">
      <div className="flex items-center gap-4 text-xs text-slate-500">
        <span>{data.total_modules} modules</span>
        <span>{data.total_resources} total resources</span>
        <span>{data.environments?.length || 0} environment{(data.environments?.length || 0) !== 1 ? "s" : ""}</span>
      </div>
      <div className="space-y-2">
        {data.modules?.map((mod) => (
          <TerraformModuleCard key={mod.name} mod={mod} />
        ))}
      </div>
    </div>
  );
};

const TerraformEnvsPanel = ({ data }) => {
  const [activeEnv, setActiveEnv] = useState(null);
  const [activeFile, setActiveFile] = useState(null);

  if (!data || !data.environments || data.environments.length === 0) {
    return <div className="text-slate-500 text-sm py-4">No environment configurations found</div>;
  }

  const currentEnv = activeEnv ? data.environments.find(e => e.name === activeEnv) : null;

  return (
    <div className="space-y-3 pt-3">
      <div className="flex gap-2">
        {data.environments.map((env) => (
          <button
            key={env.name}
            onClick={() => { setActiveEnv(env.name); setActiveFile(Object.keys(env.files)[0] || null); }}
            data-testid={`tf-env-btn-${env.name}`}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeEnv === env.name
                ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30"
                : "bg-slate-900/50 text-slate-400 border border-slate-700/50 hover:border-slate-600"
            }`}
          >
            {env.name.toUpperCase()}
            <span className="ml-1.5 text-[10px] text-slate-600">{env.file_count} files</span>
          </button>
        ))}
      </div>
      {currentEnv && (
        <div>
          <div className="flex gap-1 mb-2">
            {Object.keys(currentEnv.files).map((fname) => (
              <button
                key={fname}
                onClick={() => setActiveFile(fname)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                  activeFile === fname ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30" : "bg-slate-800/60 text-slate-500 hover:text-slate-300"
                }`}
              >
                {fname}
              </button>
            ))}
          </div>
          {activeFile && currentEnv.files[activeFile] && (
            <CodeBlock code={currentEnv.files[activeFile]} title={`envs/${currentEnv.name}/${activeFile}`} />
          )}
        </div>
      )}
    </div>
  );
};

/* ── CDK Constructs panel ─────────────────────────────────────────── */
const CDK_ICON_MAP = {
  shield: Shield, globe: Globe, database: Database, activity: Activity,
  zap: Zap, "git-branch": GitBranch, "book-open": BookOpen, server: Server, box: Box,
};

const CDK_CAT_COLORS = {
  auth: "border-violet-500/30 bg-violet-500/5",
  hosting: "border-cyan-500/30 bg-cyan-500/5",
  api: "border-blue-500/30 bg-blue-500/5",
  compute: "border-yellow-500/30 bg-yellow-500/5",
  database: "border-amber-500/30 bg-amber-500/5",
  streaming: "border-pink-500/30 bg-pink-500/5",
  events: "border-teal-500/30 bg-teal-500/5",
  ledger: "border-indigo-500/30 bg-indigo-500/5",
  other: "border-slate-500/30 bg-slate-500/5",
};

const CDK_CAT_ICON_COLORS = {
  auth: "text-violet-400", hosting: "text-cyan-400", api: "text-blue-400",
  compute: "text-yellow-400", database: "text-amber-400", streaming: "text-pink-400",
  events: "text-teal-400", ledger: "text-indigo-400", other: "text-slate-400",
};

const CdkConstructCard = ({ construct: c }) => {
  const [expanded, setExpanded] = useState(false);
  const Icon = CDK_ICON_MAP[c.icon] || Box;
  const borderColor = CDK_CAT_COLORS[c.category] || CDK_CAT_COLORS.other;
  const iconColor = CDK_CAT_ICON_COLORS[c.category] || CDK_CAT_ICON_COLORS.other;

  return (
    <div data-testid={`cdk-construct-${c.name}`} className={`border rounded-xl overflow-hidden transition-all ${borderColor}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-800/40 transition-colors"
        data-testid={`cdk-construct-toggle-${c.name}`}
      >
        <Icon className={`w-5 h-5 flex-shrink-0 ${iconColor}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-white font-semibold text-sm">{c.name}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-700/60 text-slate-400">{c.category}</span>
            {c.exports?.length > 0 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 font-mono">{c.exports[0]}</span>
            )}
          </div>
          <div className="text-xs text-slate-500 truncate">{c.description}</div>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span>{c.services?.length || 0} service{(c.services?.length || 0) !== 1 ? "s" : ""}</span>
          <span>{c.lines} lines</span>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
      </button>
      {expanded && (
        <div className="px-4 pb-4 border-t border-slate-700/30 space-y-3 pt-3">
          {c.services?.length > 0 && (
            <div>
              <div className="text-[10px] text-slate-500 uppercase mb-1.5 tracking-wider">AWS Services / Resources</div>
              <div className="flex flex-wrap gap-1.5">
                {c.services.map((s, i) => (
                  <span key={i} className="px-2 py-1 bg-slate-900/60 border border-slate-700/40 rounded text-xs font-mono text-cyan-300">{s}</span>
                ))}
              </div>
            </div>
          )}
          {c.code && <CodeBlock code={c.code} title={c.file} />}
        </div>
      )}
    </div>
  );
};

const CdkConstructsPanel = ({ data }) => {
  const [showStack, setShowStack] = useState(false);
  const [showEntry, setShowEntry] = useState(false);
  const [activeConfig, setActiveConfig] = useState(null);

  if (!data) return <div className="text-slate-500 text-sm py-4">Loading CDK constructs...</div>;
  if (!data.exists) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error || "CDK project not found"}</div>;

  return (
    <div className="space-y-4 pt-3">
      <div className="flex items-center gap-4 text-xs text-slate-500">
        <span>{data.total_constructs} constructs</span>
        <span>{data.total_services} total services</span>
      </div>

      {/* Stack & Entry quick toggles */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => { setShowStack(!showStack); setShowEntry(false); setActiveConfig(null); }}
          data-testid="cdk-show-stack"
          className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${showStack ? "bg-orange-500/15 text-orange-300 border border-orange-500/30" : "bg-slate-900/50 text-slate-400 border border-slate-700/50 hover:border-slate-600"}`}
        >
          infra-stack.ts
        </button>
        <button
          onClick={() => { setShowEntry(!showEntry); setShowStack(false); setActiveConfig(null); }}
          data-testid="cdk-show-entry"
          className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${showEntry ? "bg-orange-500/15 text-orange-300 border border-orange-500/30" : "bg-slate-900/50 text-slate-400 border border-slate-700/50 hover:border-slate-600"}`}
        >
          bin/infra.ts
        </button>
        {data.config_files && Object.keys(data.config_files).map((fname) => (
          <button
            key={fname}
            onClick={() => { setActiveConfig(activeConfig === fname ? null : fname); setShowStack(false); setShowEntry(false); }}
            data-testid={`cdk-config-${fname.replace(".", "-")}`}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${activeConfig === fname ? "bg-orange-500/15 text-orange-300 border border-orange-500/30" : "bg-slate-900/50 text-slate-400 border border-slate-700/50 hover:border-slate-600"}`}
          >
            {fname}
          </button>
        ))}
      </div>

      {showStack && data.stack_file?.code && <CodeBlock code={data.stack_file.code} title={data.stack_file.name} />}
      {showEntry && data.entry_file?.code && <CodeBlock code={data.entry_file.code} title={data.entry_file.name} />}
      {activeConfig && data.config_files?.[activeConfig] && <CodeBlock code={data.config_files[activeConfig]} title={activeConfig} />}

      {/* Construct cards */}
      <div className="space-y-2">
        {data.constructs?.map((c) => (
          <CdkConstructCard key={c.name} construct={c} />
        ))}
      </div>
    </div>
  );
};

/* ═══════════════════ MAIN COMPONENT ═══════════════════════════════ */
export const InfraTab = ({ onRefresh }) => {
  const [overview, setOverview] = useState(null);
  const [terraform, setTerraform] = useState(null);
  const [lambda, setLambda] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEnv, setSelectedEnv] = useState("dev");
  const [recording, setRecording] = useState(false);

  // live data
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
      setOverview(ov);
      setTerraform(tf);
      setLambda(lm);
      setWorkflow(wf);
      setDeployments(dep);
      setLiveStatus(ls);
      setLambdaLive(ll);
      setGhRuns(gr);
      setTfState(ts);
      setTfModules(tm);
      setCdkData(cdk);
      setLoading(false);
    });
  }, [selectedEnv]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
    setTimeout(() => setRefreshing(false), 1200);
  };

  // reload TF state when env changes
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
        <button
          data-testid="refresh-live-btn"
          onClick={handleRefresh}
          className="flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
          Refresh
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
            <span className="text-white font-semibold">
              {cdkData?.exists ? `${cdkData.total_constructs} Constructs` : "Not Found"}
            </span>
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
            <span className="text-white font-semibold">
              {tfModules?.exists ? `${tfModules.total_modules} Modules` : "Not Found"}
            </span>
          </div>
        </div>
      </div>

      {/* Environment Pills */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-3">Environments</h3>
        <div className="flex gap-3">
          {overview?.environments?.map((env) => (
            <button
              key={env.name}
              data-testid={`env-${env.name}`}
              onClick={() => setSelectedEnv(env.name)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedEnv === env.name
                  ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30"
                  : "bg-slate-900/50 text-slate-400 border border-slate-700/50 hover:border-slate-600"
              }`}
            >
              <StatusDot ok={env.configured} />
              {env.name.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* ── LIVE: Lambda Functions ──────────────────────────────── */}
      <Collapsible
        title="AWS Lambda Functions (Live)"
        icon={Zap}
        defaultOpen
        testId="section-lambda-live"
        badge={<LiveBadge connected={lambdaLive?.connected} detail={lambdaLive?.error || "OK"} />}
      >
        <LiveLambdaPanel data={lambdaLive} />
      </Collapsible>

      {/* ── LIVE: GitHub Actions Runs ──────────────────────────── */}
      <Collapsible
        title="GitHub Actions Runs (Live)"
        icon={GitBranch}
        testId="section-github-runs"
        badge={<LiveBadge connected={ghRuns?.connected} detail={ghRuns?.error || "OK"} />}
      >
        <GitHubRunsPanel data={ghRuns} />
      </Collapsible>

      {/* ── LIVE: Terraform State ──────────────────────────────── */}
      <Collapsible
        title={`Terraform State — ${selectedEnv.toUpperCase()} (Live)`}
        icon={Database}
        testId="section-terraform-state"
        badge={<LiveBadge connected={tfState?.connected} detail={tfState?.error || "OK"} />}
      >
        <TerraformStatePanel data={tfState} />
      </Collapsible>

      {/* ── Terraform Modules ──────────────────────────────────── */}
      <Collapsible
        title={`Terraform Modules (${tfModules?.total_modules || 0})`}
        icon={Package}
        defaultOpen
        testId="section-terraform-modules"
        badge={
          tfModules?.exists ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              {tfModules.total_resources} resources
            </span>
          ) : null
        }
      >
        <TerraformModulesPanel data={tfModules} />
      </Collapsible>

      {/* ── Terraform Environments (Prod / Staging) ────────────── */}
      <Collapsible
        title="Terraform Environments"
        icon={Cloud}
        testId="section-terraform-envs"
        badge={
          tfModules?.environments?.length ? (
            <span className="text-xs text-slate-500">{tfModules.environments.length} configured</span>
          ) : null
        }
      >
        <TerraformEnvsPanel data={tfModules} />
      </Collapsible>

      {/* ── CDK Constructs ──────────────────────────────────────── */}
      <Collapsible
        title={`CDK Constructs (${cdkData?.total_constructs || 0})`}
        icon={Code}
        defaultOpen
        testId="section-cdk-constructs"
        badge={
          cdkData?.exists ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-orange-500/15 text-orange-300 border border-orange-500/30">
              {cdkData.total_services} services
            </span>
          ) : null
        }
      >
        <CdkConstructsPanel data={cdkData} />
      </Collapsible>

      {/* ── Local: Terraform Configuration ─────────────────────── */}
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

      {/* ── Local: Lambda Function ─────────────────────────────── */}
      <Collapsible title="Lambda Function (Local Config)" icon={Box} testId="section-lambda">
        <div className="space-y-4 pt-3">
          {lambda && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="bg-slate-900/50 rounded-lg px-3 py-2">
                <div className="text-[10px] text-slate-500">Runtime</div>
                <div className="text-sm text-slate-300 font-mono">{lambda.runtime}</div>
              </div>
              <div className="bg-slate-900/50 rounded-lg px-3 py-2">
                <div className="text-[10px] text-slate-500">Handler</div>
                <div className="text-sm text-slate-300 font-mono">{lambda.handler_entry}</div>
              </div>
              <div className="bg-slate-900/50 rounded-lg px-3 py-2">
                <div className="text-[10px] text-slate-500">Timeout</div>
                <div className="text-sm text-slate-300">{lambda.timeout}s</div>
              </div>
              <div className="bg-slate-900/50 rounded-lg px-3 py-2">
                <div className="text-[10px] text-slate-500">Memory</div>
                <div className="text-sm text-slate-300">{lambda.memory_mb} MB</div>
              </div>
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

      {/* ── Local: GitHub Actions Workflow ─────────────────────── */}
      <Collapsible title="GitHub Actions Workflow (Local)" icon={GitBranch} testId="section-workflow">
        <div className="pt-3">
          {workflow?.exists ? (
            <CodeBlock code={workflow.content} title={workflow.file} />
          ) : (
            <div className="text-sm text-slate-500">No workflow file found</div>
          )}
        </div>
      </Collapsible>

      {/* Deployment Commands */}
      <Collapsible title={`Deploy Commands - ${selectedEnv.toUpperCase()}`} icon={Terminal} testId="section-deploy-commands">
        <DeploySteps environment={selectedEnv} />
        <div className="mt-4 pt-4 border-t border-slate-700/30 flex items-center gap-3">
          <button
            data-testid="record-deployment-btn"
            onClick={handleRecordDeploy}
            disabled={recording}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            <Rocket className="w-4 h-4" />
            {recording ? "Recording..." : "Record Deployment"}
          </button>
          <span className="text-xs text-slate-500">Log a manual deployment to {selectedEnv}</span>
        </div>
      </Collapsible>

      {/* Deployment History */}
      <Collapsible title="Deployment History" icon={Clock} defaultOpen testId="section-deploy-history">
        <DeploymentLog deployments={deployments} />
      </Collapsible>
    </div>
  );
};
