import React, { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

export const Collapsible = ({ title, icon: Icon, children, defaultOpen = false, testId, badge }) => {
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
