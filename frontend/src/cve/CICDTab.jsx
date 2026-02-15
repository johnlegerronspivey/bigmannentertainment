import React, { useState, useEffect } from "react";
import { GitBranch, Copy, Download, Terminal } from "lucide-react";
import { SCANNER_API, fetcher } from "./shared";

export const CICDTab = ({ onRefresh }) => {
  const [config, setConfig] = useState({
    repo_name: "bigmannentertainment", branch: "main",
    enable_trivy: true, enable_grype: true, enable_checkov: true, enable_syft: true,
    fail_on_critical: true, fail_on_high: false, container_image: "", terraform_dir: "terraform/", notify_email: "",
  });
  const [generatedYaml, setGeneratedYaml] = useState(null);
  const [pipelines, setPipelines] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    (async () => { try { setPipelines(await fetcher(`${SCANNER_API}/pipeline/list`)); } catch (e) {} })();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const result = await fetcher(`${SCANNER_API}/pipeline/generate`, { method: "POST", body: JSON.stringify(config) });
      setGeneratedYaml(result.yaml_content);
      setPipelines(await fetcher(`${SCANNER_API}/pipeline/list`));
      onRefresh();
    } catch (e) { console.error(e); }
    setGenerating(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedYaml);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([generatedYaml], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "security-gates.yml";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Pipeline Configuration</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Repository</label>
                <input data-testid="pipeline-repo" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={config.repo_name} onChange={(e) => setConfig({ ...config, repo_name: e.target.value })} />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Branch</label>
                <input data-testid="pipeline-branch" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={config.branch} onChange={(e) => setConfig({ ...config, branch: e.target.value })} />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-2">Security Scanners</label>
              <div className="grid grid-cols-2 gap-2">
                {[{ k: "enable_trivy", l: "Trivy (Vuln + IaC)" }, { k: "enable_grype", l: "Grype (Dependencies)" }, { k: "enable_checkov", l: "Checkov (IaC)" }, { k: "enable_syft", l: "Syft (SBOM)" }].map(({ k, l }) => (
                  <label key={k} className="flex items-center gap-2 bg-slate-900/50 rounded-lg px-3 py-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4 rounded bg-slate-800 border-slate-600 text-cyan-500" checked={config[k]} onChange={(e) => setConfig({ ...config, [k]: e.target.checked })} />
                    <span className="text-sm text-slate-300">{l}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-2">Fail Conditions</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 rounded bg-slate-800 border-slate-600 text-red-500" checked={config.fail_on_critical} onChange={(e) => setConfig({ ...config, fail_on_critical: e.target.checked })} />
                  <span className="text-sm text-red-300">Fail on Critical</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 rounded bg-slate-800 border-slate-600 text-orange-500" checked={config.fail_on_high} onChange={(e) => setConfig({ ...config, fail_on_high: e.target.checked })} />
                  <span className="text-sm text-orange-300">Fail on High</span>
                </label>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Container Image (optional)</label>
                <input className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" placeholder="e.g. myapp:latest" value={config.container_image} onChange={(e) => setConfig({ ...config, container_image: e.target.value })} />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Terraform Dir</label>
                <input className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={config.terraform_dir} onChange={(e) => setConfig({ ...config, terraform_dir: e.target.value })} />
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-1">Notification Email</label>
              <input className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" placeholder="team@company.com" value={config.notify_email} onChange={(e) => setConfig({ ...config, notify_email: e.target.value })} />
            </div>

            <button data-testid="generate-pipeline-btn" onClick={handleGenerate} disabled={generating} className="w-full flex items-center justify-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50">
              <GitBranch className="w-4 h-4" /> {generating ? "Generating..." : "Generate GitHub Actions YAML"}
            </button>
          </div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-white font-semibold">Generated Pipeline</h3>
            {generatedYaml && (
              <div className="flex items-center gap-2">
                <button data-testid="copy-yaml-btn" onClick={handleCopy} className="flex items-center gap-1 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded text-xs transition-colors">
                  <Copy className="w-3 h-3" /> {copied ? "Copied!" : "Copy"}
                </button>
                <button data-testid="download-yaml-btn" onClick={handleDownload} className="flex items-center gap-1 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded text-xs transition-colors">
                  <Download className="w-3 h-3" /> Download
                </button>
              </div>
            )}
          </div>
          {generatedYaml ? (
            <pre className="flex-1 bg-slate-950 rounded-lg p-4 text-xs text-green-400 font-mono overflow-auto max-h-[500px] whitespace-pre">{generatedYaml}</pre>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
              <div className="text-center">
                <Terminal className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                <div>Configure and generate your security pipeline</div>
                <div className="text-xs text-slate-600 mt-1">.github/workflows/security-gates.yml</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {pipelines.length > 0 && (
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3">Generated Pipelines</h3>
          <div className="space-y-2">
            {pipelines.map((p) => (
              <div key={p.id} className="flex items-center justify-between bg-slate-900/50 rounded-lg px-4 py-2.5">
                <div className="flex items-center gap-3">
                  <GitBranch className="w-4 h-4 text-cyan-400" />
                  <span className="text-sm text-white">{p.repo_name}</span>
                  <span className="text-xs text-slate-500">/{p.branch}</span>
                </div>
                <span className="text-xs text-slate-500">{new Date(p.created_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
