import React, { useState } from "react";
import {
  Shield, Globe, Database, Activity, Zap, GitBranch, BookOpen,
  Server, Box, ChevronDown, ChevronRight, AlertTriangle
} from "lucide-react";
import { CodeBlock } from "../components";

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

export const CdkConstructsPanel = ({ data }) => {
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

      <div className="space-y-2">
        {data.constructs?.map((c) => (
          <CdkConstructCard key={c.name} construct={c} />
        ))}
      </div>
    </div>
  );
};
