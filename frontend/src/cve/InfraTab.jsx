import React, { useState, useEffect } from "react";
import { Cloud, Server, GitBranch, Terminal, CheckCircle, XCircle, Copy, ChevronDown, ChevronRight, Rocket, Clock, Box } from "lucide-react";
import { fetcher } from "./shared";

const IAC_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/iac`;

const StatusDot = ({ ok }) => (
  <span className={`inline-block w-2.5 h-2.5 rounded-full ${ok ? "bg-emerald-400" : "bg-slate-600"}`} />
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

const Collapsible = ({ title, icon: Icon, children, defaultOpen = false, testId }) => {
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
        {open ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
      </button>
      {open && <div className="px-5 pb-5 border-t border-slate-700/30">{children}</div>}
    </div>
  );
};

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
          <div className="text-xs text-slate-600 whitespace-nowrap">
            {new Date(d.deployed_at).toLocaleString()}
          </div>
        </div>
      ))}
    </div>
  );
};

export const InfraTab = ({ onRefresh }) => {
  const [overview, setOverview] = useState(null);
  const [terraform, setTerraform] = useState(null);
  const [lambda, setLambda] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEnv, setSelectedEnv] = useState("dev");
  const [recording, setRecording] = useState(false);

  useEffect(() => {
    Promise.all([
      fetcher(`${IAC_API}/overview`).catch(() => null),
      fetcher(`${IAC_API}/terraform`).catch(() => null),
      fetcher(`${IAC_API}/lambda`).catch(() => null),
      fetcher(`${IAC_API}/workflow`).catch(() => null),
      fetcher(`${IAC_API}/deployments`).catch(() => []),
    ]).then(([ov, tf, lm, wf, dep]) => {
      setOverview(ov);
      setTerraform(tf);
      setLambda(lm);
      setWorkflow(wf);
      setDeployments(dep);
      setLoading(false);
    });
  }, []);

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

  return (
    <div data-testid="infra-tab" className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
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
        <div data-testid="stat-lambda" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-amber-500/10"><Box className="w-5 h-5 text-amber-400" /></div>
            <span className="text-slate-400 text-sm">Lambda</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusDot ok={overview?.lambda?.configured} />
            <span className="text-white font-semibold">{overview?.lambda?.configured ? "Ready" : "Not Found"}</span>
          </div>
        </div>
        <div data-testid="stat-github-actions" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-cyan-500/10"><GitBranch className="w-5 h-5 text-cyan-400" /></div>
            <span className="text-slate-400 text-sm">GitHub Actions</span>
          </div>
          <div className="flex items-center gap-2">
            <StatusDot ok={overview?.github_actions?.configured} />
            <span className="text-white font-semibold">{overview?.github_actions?.configured ? "Active" : "Missing"}</span>
          </div>
        </div>
        <div data-testid="stat-deployments" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-emerald-500/10"><Rocket className="w-5 h-5 text-emerald-400" /></div>
            <span className="text-slate-400 text-sm">Deployments</span>
          </div>
          <div className="text-2xl font-bold text-white">{overview?.total_deployments || 0}</div>
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

      {/* Terraform Section */}
      <Collapsible title="Terraform Configuration" icon={Cloud} defaultOpen testId="section-terraform">
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

      {/* Lambda Section */}
      <Collapsible title="Lambda Function" icon={Box} testId="section-lambda">
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
          {lambda?.handler && (
            <div className="text-xs text-slate-500">{lambda.handler.file} — {lambda.handler.lines} lines</div>
          )}
        </div>
      </Collapsible>

      {/* GitHub Actions Section */}
      <Collapsible title="GitHub Actions Workflow" icon={GitBranch} testId="section-workflow">
        <div className="pt-3">
          {workflow?.exists ? (
            <CodeBlock code={workflow.content} title={workflow.file} />
          ) : (
            <div className="text-sm text-slate-500">No workflow file found</div>
          )}
        </div>
      </Collapsible>

      {/* Deployment Commands */}
      <Collapsible title={`Deploy Commands — ${selectedEnv.toUpperCase()}`} icon={Terminal} testId="section-deploy-commands">
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
