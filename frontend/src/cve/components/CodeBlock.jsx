import React, { useState } from "react";
import { Copy } from "lucide-react";

export const CodeBlock = ({ code, title }) => {
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
