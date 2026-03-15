import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";

const API = process.env.REACT_APP_BACKEND_URL;

const statusBadge = (ok) => (
  <Badge variant="outline" className={`text-[10px] ${ok ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : "bg-rose-500/15 text-rose-400 border-rose-500/30"}`}>
    {ok ? "Connected" : "Unavailable"}
  </Badge>
);

const ServiceCard = ({ title, data, icon }) => (
  <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm" data-testid={`service-status-${title.toLowerCase().replace(/\s+/g, "-")}`}>
    <CardContent className="p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className={`p-2.5 rounded-lg ${data?.available ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`}>{icon}</div>
        <div>
          <h3 className="font-semibold text-zinc-100 text-sm">{title}</h3>
          {statusBadge(data?.available)}
        </div>
      </div>
      <div className="text-xs text-zinc-500 space-y-1">
        {data?.region && <p>Region: <span className="text-zinc-300">{data.region}</span></p>}
        {data?.service && <p>Service: <span className="text-zinc-300">{data.service}</span></p>}
      </div>
    </CardContent>
  </Card>
);

const DataTable = ({ columns, rows, emptyMsg }) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm" data-testid="data-table">
      <thead>
        <tr className="border-b border-zinc-800">
          {columns.map((c, i) => <th key={i} className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">{c.label}</th>)}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr><td colSpan={columns.length} className="py-8 text-center text-zinc-500">{emptyMsg || "No data"}</td></tr>
        ) : rows.map((row, i) => (
          <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
            {columns.map((c, j) => <td key={j} className="py-2 px-3 text-zinc-300 text-xs">{c.render ? c.render(row) : row[c.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default function AWSInfrastructurePage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("stepfunctions");

  // Step Functions
  const [stateMachines, setStateMachines] = useState([]);
  const [activities, setActivities] = useState([]);
  // ElastiCache
  const [clusters, setClusters] = useState([]);
  const [replGroups, setReplGroups] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  // Neptune
  const [neptuneClusters, setNeptuneClusters] = useState([]);
  const [neptuneInstances, setNeptuneInstances] = useState([]);
  const [neptuneSnapshots, setNeptuneSnapshots] = useState([]);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/aws-infra/status`, { headers });
      if (res.ok) setStatus(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const fetchStepFunctions = async () => {
    try {
      const [sm, act] = await Promise.all([
        fetch(`${API}/api/aws-infra/stepfunctions/state-machines`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-infra/stepfunctions/activities`, { headers }).then(r => r.ok ? r.json() : null),
      ]);
      if (sm) setStateMachines(sm.state_machines || []);
      if (act) setActivities(act.activities || []);
    } catch (e) { console.error(e); }
  };

  const fetchElastiCache = async () => {
    try {
      const [c, rg, s] = await Promise.all([
        fetch(`${API}/api/aws-infra/elasticache/clusters`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-infra/elasticache/replication-groups`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-infra/elasticache/snapshots`, { headers }).then(r => r.ok ? r.json() : null),
      ]);
      if (c) setClusters(c.clusters || []);
      if (rg) setReplGroups(rg.replication_groups || []);
      if (s) setSnapshots(s.snapshots || []);
    } catch (e) { console.error(e); }
  };

  const fetchNeptune = async () => {
    try {
      const [c, i, s] = await Promise.all([
        fetch(`${API}/api/aws-infra/neptune/clusters`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-infra/neptune/instances`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-infra/neptune/snapshots`, { headers }).then(r => r.ok ? r.json() : null),
      ]);
      if (c) setNeptuneClusters(c.clusters || []);
      if (i) setNeptuneInstances(i.instances || []);
      if (s) setNeptuneSnapshots(s.snapshots || []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    if (tab === "stepfunctions") fetchStepFunctions();
    if (tab === "elasticache") fetchElastiCache();
    if (tab === "neptune") fetchNeptune();
  }, [tab]);

  if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><div className="animate-spin w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full" /></div>;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-infrastructure-page">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">Infrastructure Services</h1>
          <p className="text-zinc-400 text-sm">Step Functions Workflows, ElastiCache, Neptune Graph DB</p>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-8">
          <ServiceCard title="Step Functions" data={status?.step_functions} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>} />
          <ServiceCard title="ElastiCache" data={status?.elasticache} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>} />
          <ServiceCard title="Neptune" data={status?.neptune} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>} />
        </div>

        <Tabs value={tab} onValueChange={setTab} className="space-y-6">
          <TabsList className="bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="stepfunctions" data-testid="tab-stepfunctions">Step Functions</TabsTrigger>
            <TabsTrigger value="elasticache" data-testid="tab-elasticache">ElastiCache</TabsTrigger>
            <TabsTrigger value="neptune" data-testid="tab-neptune">Neptune</TabsTrigger>
          </TabsList>

          {/* STEP FUNCTIONS TAB */}
          <TabsContent value="stepfunctions">
            <div className="space-y-6">
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">State Machines ({stateMachines.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Name" },
                    { key: "type", label: "Type", render: (r) => <Badge variant="outline" className={`text-[10px] ${r.type === "EXPRESS" ? "bg-amber-500/15 text-amber-400" : "bg-sky-500/15 text-sky-400"}`}>{r.type}</Badge> },
                    { key: "arn", label: "ARN", render: (r) => <span className="truncate max-w-[300px] inline-block text-xs">{r.arn}</span> },
                    { key: "created_at", label: "Created" },
                  ]} rows={stateMachines} emptyMsg="No state machines" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Activities ({activities.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Activity" },
                    { key: "arn", label: "ARN", render: (r) => <span className="truncate max-w-[300px] inline-block text-xs">{r.arn}</span> },
                    { key: "created_at", label: "Created" },
                  ]} rows={activities} emptyMsg="No activities" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* ELASTICACHE TAB */}
          <TabsContent value="elasticache">
            <div className="space-y-6">
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Cache Clusters ({clusters.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "id", label: "Cluster ID" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className={`text-[10px] ${r.status === "available" ? "bg-emerald-500/15 text-emerald-400" : "bg-amber-500/15 text-amber-400"}`}>{r.status}</Badge> },
                    { key: "engine", label: "Engine" },
                    { key: "engine_version", label: "Version" },
                    { key: "node_type", label: "Node Type" },
                    { key: "num_nodes", label: "Nodes" },
                  ]} rows={clusters} emptyMsg="No cache clusters" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Replication Groups ({replGroups.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "id", label: "Group ID" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className="text-[10px]">{r.status}</Badge> },
                    { key: "automatic_failover", label: "Auto Failover" },
                    { key: "multi_az", label: "Multi-AZ" },
                    { key: "node_groups", label: "Node Groups" },
                  ]} rows={replGroups} emptyMsg="No replication groups" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Snapshots ({snapshots.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Snapshot" },
                    { key: "status", label: "Status" },
                    { key: "engine", label: "Engine" },
                    { key: "node_type", label: "Node Type" },
                    { key: "source", label: "Source" },
                  ]} rows={snapshots} emptyMsg="No snapshots" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* NEPTUNE TAB */}
          <TabsContent value="neptune">
            <div className="space-y-6">
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Graph DB Clusters ({neptuneClusters.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "id", label: "Cluster ID" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className={`text-[10px] ${r.status === "available" ? "bg-emerald-500/15 text-emerald-400" : "bg-amber-500/15 text-amber-400"}`}>{r.status}</Badge> },
                    { key: "engine", label: "Engine" },
                    { key: "engine_version", label: "Version" },
                    { key: "multi_az", label: "Multi-AZ", render: (r) => r.multi_az ? "Yes" : "No" },
                    { key: "members", label: "Members" },
                    { key: "storage_encrypted", label: "Encrypted", render: (r) => r.storage_encrypted ? "Yes" : "No" },
                  ]} rows={neptuneClusters} emptyMsg="No Neptune clusters" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Instances ({neptuneInstances.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "id", label: "Instance ID" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className="text-[10px]">{r.status}</Badge> },
                    { key: "class", label: "Class" },
                    { key: "engine", label: "Engine" },
                    { key: "availability_zone", label: "AZ" },
                    { key: "cluster_id", label: "Cluster" },
                  ]} rows={neptuneInstances} emptyMsg="No instances" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Snapshots ({neptuneSnapshots.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "id", label: "Snapshot ID" },
                    { key: "cluster_id", label: "Cluster" },
                    { key: "status", label: "Status" },
                    { key: "snapshot_type", label: "Type" },
                    { key: "storage_encrypted", label: "Encrypted", render: (r) => r.storage_encrypted ? "Yes" : "No" },
                  ]} rows={neptuneSnapshots} emptyMsg="No snapshots" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
