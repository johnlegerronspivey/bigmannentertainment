import React from "react";

export const RiskGauge = ({ score }) => {
  const color = score >= 75 ? "#ef4444" : score >= 50 ? "#f97316" : score >= 25 ? "#eab308" : "#10b981";
  const label = score >= 75 ? "Critical" : score >= 50 ? "High" : score >= 25 ? "Medium" : "Low";
  return (
    <div data-testid="risk-gauge" className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="10" />
          <circle cx="50" cy="50" r="42" fill="none" stroke={color} strokeWidth="10" strokeDasharray={`${score * 2.64} 264`} strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">{score}</span>
          <span className="text-xs" style={{ color }}>{label}</span>
        </div>
      </div>
      <p className="text-xs text-slate-400 mt-2">Risk Score</p>
    </div>
  );
};
