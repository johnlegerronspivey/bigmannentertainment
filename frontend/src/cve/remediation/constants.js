export const REMEDIATION_STATUS_COLORS = {
  open: "bg-slate-500/20 text-slate-300",
  issue_created: "bg-yellow-500/20 text-yellow-300",
  pr_created: "bg-blue-500/20 text-blue-300",
  in_review: "bg-purple-500/20 text-purple-300",
  merged: "bg-emerald-500/20 text-emerald-300",
  deployed: "bg-cyan-500/20 text-cyan-300",
  verified: "bg-green-500/20 text-green-300",
  closed: "bg-slate-600/20 text-slate-400",
  wont_fix: "bg-slate-600/20 text-slate-400",
};

export const REMEDIATION_STATUSES = ["open", "issue_created", "pr_created", "in_review", "merged", "deployed", "verified", "closed", "wont_fix"];
