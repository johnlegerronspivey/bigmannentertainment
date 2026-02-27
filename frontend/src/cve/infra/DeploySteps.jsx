import React, { useState, useEffect } from "react";
import { fetcher } from "../shared";
import { CodeBlock } from "../components";

const IAC_API = `${process.env.REACT_APP_BACKEND_URL}/api/cve/iac`;

export const DeploySteps = ({ environment }) => {
  const [commands, setCommands] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    setLoading(true);
    fetcher(`${IAC_API}/commands/${environment}`)
      .then(setCommands)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [environment]);
  if (loading) return <div className="text-slate-500 text-sm py-4">Loading commands...</div>;
  if (!commands) return null;
  return (
    <div className="space-y-3 pt-3">
      {commands.steps.map((step, i) => (
        <div key={i}>
          <div className="text-sm text-slate-300 font-medium mb-1">{step.title}</div>
          <div className="text-xs text-slate-500 mb-1">{step.description}</div>
          <CodeBlock code={step.command} />
        </div>
      ))}
    </div>
  );
};
