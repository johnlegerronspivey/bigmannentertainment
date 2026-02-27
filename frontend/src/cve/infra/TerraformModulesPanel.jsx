import React, { useState } from "react";
import {
  Shield, Globe, Database, Activity, Zap, GitBranch, Bell, Lock,
  BookOpen, Film, Layers, Box, ChevronDown, ChevronRight, AlertTriangle, Package
} from "lucide-react";
import { CodeBlock } from "../components";

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

export const TerraformModulesPanel = ({ data }) => {
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

export const TerraformEnvsPanel = ({ data }) => {
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
