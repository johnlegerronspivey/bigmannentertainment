import React from "react";
import { Loader2, FileText } from "lucide-react";

export const LoadingState = () => (
  <div className="flex items-center justify-center py-16">
    <Loader2 className="w-7 h-7 text-cyan-400 animate-spin" />
    <span className="ml-3 text-slate-400 text-sm">Loading report data...</span>
  </div>
);

export const EmptyState = ({ text }) => (
  <div className="text-center py-16">
    <FileText className="w-10 h-10 text-slate-600 mx-auto mb-3" />
    <p className="text-slate-500 text-sm">{text}</p>
  </div>
);
