import React from "react";
import { CheckCircle, XCircle } from "lucide-react";

export const DeploymentLog = ({ deployments }) => {
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
