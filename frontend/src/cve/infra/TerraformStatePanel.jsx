import React from "react";
import { Database, AlertTriangle } from "lucide-react";

export const TerraformStatePanel = ({ data }) => {
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
