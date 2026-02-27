import React from "react";
import { Shield, Users, ArrowUpRight } from "lucide-react";
import { SeverityBadge } from "../shared";
import { SLAStatusBadge, CountdownTimer } from "./badges";

export const AtRiskView = ({ atRisk }) => (
  <div className="space-y-4">
    <div className="flex items-center justify-between">
      <h3 className="text-white font-semibold text-sm">At-Risk CVEs <span className="text-slate-400 font-normal ml-1">({atRisk?.total || 0} total)</span></h3>
    </div>
    {(atRisk?.items || []).length === 0 ? (
      <div className="text-center py-16 text-slate-500">
        <Shield className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p className="text-sm">All CVEs are within SLA</p>
      </div>
    ) : (
      <div className="space-y-2">
        {(atRisk?.items || []).map((item) => (
          <div key={item.cve_id} data-testid={`at-risk-${item.cve_id}`} className={`flex items-center gap-4 p-4 rounded-xl border transition-colors ${item.sla_status === "breached" ? "bg-red-900/10 border-red-500/30" : item.sla_status === "warning" ? "bg-amber-900/10 border-amber-500/30" : "bg-slate-800/60 border-slate-700/50"}`}>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className="text-cyan-400 font-mono text-xs">{item.cve_id}</span>
                <SeverityBadge severity={item.severity} />
                <SLAStatusBadge status={item.sla_status} />
                {item.escalation_level > 0 && (
                  <span className="px-2 py-0.5 rounded text-xs bg-orange-500/20 text-orange-300 border border-orange-500/30">
                    <ArrowUpRight className="w-3 h-3 inline mr-0.5" />L{item.escalation_level}
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-300 truncate">{item.title}</p>
              <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                {item.assigned_to && <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {item.assigned_to}</span>}
                <span>SLA: {item.sla_hours}h</span>
                <span>{item.percent_elapsed.toFixed(0)}% elapsed</span>
              </div>
            </div>
            <CountdownTimer remainingHours={item.remaining_hours > 0 ? item.remaining_hours : -item.overdue_hours} percentElapsed={item.percent_elapsed} />
          </div>
        ))}
      </div>
    )}
  </div>
);
