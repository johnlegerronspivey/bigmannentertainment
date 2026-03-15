import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { toast } from "sonner";

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
        {data?.account_id && <p>Account: <span className="text-zinc-300">{data.account_id}</span></p>}
        {data?.output_location && <p>Output: <span className="text-zinc-300 font-mono text-[10px]">{data.output_location}</span></p>}
      </div>
    </CardContent>
  </Card>
);

const stateColor = (s) => {
  const map = { SUCCEEDED: "bg-emerald-500/15 text-emerald-400", RUNNING: "bg-sky-500/15 text-sky-400", QUEUED: "bg-amber-500/15 text-amber-400", FAILED: "bg-rose-500/15 text-rose-400", CANCELLED: "bg-zinc-500/15 text-zinc-400" };
  return map[s] || "bg-zinc-500/15 text-zinc-400";
};

export default function AWSDataAnalyticsPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("quicksight");

  // QuickSight state
  const [dashboards, setDashboards] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [dataSources, setDataSources] = useState([]);
  const [analyses, setAnalyses] = useState([]);

  // Athena state
  const [workGroups, setWorkGroups] = useState([]);
  const [databases, setDatabases] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [savedQueries, setSavedQueries] = useState([]);
  const [queryText, setQueryText] = useState("");
  const [queryDb, setQueryDb] = useState("default");
  const [submitting, setSubmitting] = useState(false);
  const [queryResult, setQueryResult] = useState(null);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/aws-data/status`, { headers });
      if (res.ok) setStatus(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  /* QuickSight fetchers */
  const fetchQuickSight = async () => {
    try {
      const [dRes, dsRes, srcRes, aRes] = await Promise.all([
        fetch(`${API}/api/aws-data/quicksight/dashboards`, { headers }),
        fetch(`${API}/api/aws-data/quicksight/datasets`, { headers }),
        fetch(`${API}/api/aws-data/quicksight/data-sources`, { headers }),
        fetch(`${API}/api/aws-data/quicksight/analyses`, { headers }),
      ]);
      if (dRes.ok) { const d = await dRes.json(); setDashboards(d.dashboards || []); }
      if (dsRes.ok) { const d = await dsRes.json(); setDatasets(d.datasets || []); }
      if (srcRes.ok) { const d = await srcRes.json(); setDataSources(d.data_sources || []); }
      if (aRes.ok) { const d = await aRes.json(); setAnalyses(d.analyses || []); }
    } catch (e) { console.error(e); }
  };

  /* Athena fetchers */
  const fetchAthena = async () => {
    try {
      const [wgRes, dbRes, exRes, sqRes] = await Promise.all([
        fetch(`${API}/api/aws-data/athena/work-groups`, { headers }),
        fetch(`${API}/api/aws-data/athena/databases`, { headers }),
        fetch(`${API}/api/aws-data/athena/executions`, { headers }),
        fetch(`${API}/api/aws-data/athena/saved-queries`, { headers }),
      ]);
      if (wgRes.ok) { const d = await wgRes.json(); setWorkGroups(d.work_groups || []); }
      if (dbRes.ok) { const d = await dbRes.json(); setDatabases(d.databases || []); }
      if (exRes.ok) { const d = await exRes.json(); setExecutions(d.executions || []); }
      if (sqRes.ok) { const d = await sqRes.json(); setSavedQueries(d.queries || []); }
    } catch (e) { console.error(e); }
  };

  const submitQuery = async () => {
    if (!queryText.trim()) return toast.error("Enter a query");
    setSubmitting(true);
    setQueryResult(null);
    try {
      const res = await fetch(`${API}/api/aws-data/athena/query`, {
        method: "POST", headers,
        body: JSON.stringify({ query: queryText, database: queryDb }),
      });
      if (!res.ok) throw new Error("Query submission failed");
      const data = await res.json();
      toast.success(`Query started: ${data.query_execution_id}`);
      // Poll for results
      const eid = data.query_execution_id;
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        try {
          const sRes = await fetch(`${API}/api/aws-data/athena/query/${eid}/status`, { headers });
          if (sRes.ok) {
            const st = await sRes.json();
            if (st.state === "SUCCEEDED") {
              clearInterval(poll);
              const rRes = await fetch(`${API}/api/aws-data/athena/query/${eid}/results`, { headers });
              if (rRes.ok) setQueryResult(await rRes.json());
              setSubmitting(false);
              fetchAthena();
            } else if (st.state === "FAILED" || st.state === "CANCELLED") {
              clearInterval(poll);
              toast.error(`Query ${st.state}: ${st.reason}`);
              setSubmitting(false);
            }
          }
        } catch (e) { /* ignore polling errors */ }
        if (attempts > 30) { clearInterval(poll); setSubmitting(false); toast.error("Query timed out"); }
      }, 2000);
    } catch (e) { toast.error(e.message); setSubmitting(false); }
  };

  useEffect(() => { if (tab === "quicksight" && token) fetchQuickSight(); }, [tab, token]);
  useEffect(() => { if (tab === "athena" && token) fetchAthena(); }, [tab, token]);

  if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><div className="text-zinc-400">Loading...</div></div>;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-data-analytics-page">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-zinc-100 mb-1">Data Analytics</h1>
          <p className="text-sm text-zinc-500">Amazon QuickSight Dashboards & AWS Athena S3 Queries</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <ServiceCard title="Amazon QuickSight" data={status?.quicksight} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>} />
          <ServiceCard title="AWS Athena" data={status?.athena} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>} />
        </div>

        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="bg-zinc-900 border border-zinc-800 mb-6">
            <TabsTrigger value="quicksight" className="data-[state=active]:bg-cyan-600 data-[state=active]:text-white" data-testid="tab-quicksight">QuickSight</TabsTrigger>
            <TabsTrigger value="athena" className="data-[state=active]:bg-cyan-600 data-[state=active]:text-white" data-testid="tab-athena">Athena</TabsTrigger>
          </TabsList>

          {/* ── QUICKSIGHT ── */}
          <TabsContent value="quicksight">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="qs-dashboards">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Dashboards ({dashboards.length})</CardTitle></CardHeader>
                <CardContent>
                  {dashboards.length === 0 ? (
                    <p className="text-xs text-zinc-500">No dashboards found. Create one in the QuickSight console to visualize your data.</p>
                  ) : dashboards.map((d, i) => (
                    <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                      <p className="text-sm font-medium text-zinc-200">{d.name}</p>
                      <p className="text-[10px] text-zinc-500 font-mono">{d.id}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="qs-datasets">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Datasets ({datasets.length})</CardTitle></CardHeader>
                <CardContent>
                  {datasets.length === 0 ? (
                    <p className="text-xs text-zinc-500">No datasets found. Import data to create datasets for analysis.</p>
                  ) : datasets.map((ds, i) => (
                    <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                      <p className="text-sm font-medium text-zinc-200">{ds.name}</p>
                      <Badge variant="outline" className="text-[10px] mt-1">{ds.import_mode || "N/A"}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="qs-data-sources">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Data Sources ({dataSources.length})</CardTitle></CardHeader>
                <CardContent>
                  {dataSources.length === 0 ? (
                    <p className="text-xs text-zinc-500">No data sources configured. Connect to S3, RDS, or other data stores.</p>
                  ) : dataSources.map((s, i) => (
                    <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                      <p className="text-sm font-medium text-zinc-200">{s.name}</p>
                      <div className="flex gap-2 mt-1">
                        <Badge variant="outline" className="text-[10px]">{s.type}</Badge>
                        <Badge variant="outline" className={`text-[10px] ${s.status === "CREATION_SUCCESSFUL" ? "bg-emerald-500/10 text-emerald-400" : ""}`}>{s.status}</Badge>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="qs-analyses">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Analyses ({analyses.length})</CardTitle></CardHeader>
                <CardContent>
                  {analyses.length === 0 ? (
                    <p className="text-xs text-zinc-500">No analyses found. Create an analysis from your datasets to build visualizations.</p>
                  ) : analyses.map((a, i) => (
                    <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                      <p className="text-sm font-medium text-zinc-200">{a.name}</p>
                      <Badge variant="outline" className="text-[10px] mt-1">{a.status}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* ── ATHENA ── */}
          <TabsContent value="athena">
            {/* Query Editor */}
            <Card className="border-zinc-800 bg-zinc-900/60 mb-6" data-testid="athena-query-editor">
              <CardHeader className="pb-3"><CardTitle className="text-base text-zinc-100">SQL Query Editor</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="flex gap-3 items-end">
                  <div className="flex-1">
                    <label className="text-xs text-zinc-500 mb-1 block">Database</label>
                    <select
                      value={queryDb}
                      onChange={(e) => setQueryDb(e.target.value)}
                      className="w-full bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-200"
                      data-testid="athena-db-select"
                    >
                      <option value="default">default</option>
                      {databases.map((db, i) => (
                        <option key={i} value={db.name}>{db.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <textarea
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  placeholder="SELECT * FROM your_table LIMIT 10"
                  className="w-full h-28 bg-zinc-800 border border-zinc-700 rounded-lg p-3 text-sm text-zinc-100 placeholder-zinc-500 font-mono resize-none focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  data-testid="athena-query-input"
                />
                <div className="flex justify-end">
                  <Button onClick={submitQuery} disabled={submitting || !queryText.trim()} className="bg-cyan-600 hover:bg-cyan-700" data-testid="athena-run-btn">
                    {submitting ? "Running..." : "Run Query"}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Query Results */}
            {queryResult && (
              <Card className="border-zinc-800 bg-zinc-900/60 mb-6" data-testid="athena-results">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Results ({queryResult.total} rows)</CardTitle></CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-zinc-700">
                          {queryResult.columns?.map((col, i) => (
                            <th key={i} className="px-3 py-2 text-left text-zinc-400 font-medium">{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResult.rows?.map((row, i) => (
                          <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                            {queryResult.columns?.map((col, j) => (
                              <td key={j} className="px-3 py-2 text-zinc-300 font-mono">{row[col]}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Work Groups */}
              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="athena-workgroups">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Work Groups ({workGroups.length})</CardTitle></CardHeader>
                <CardContent>
                  {workGroups.length === 0 ? (
                    <p className="text-xs text-zinc-500">No work groups found.</p>
                  ) : workGroups.map((wg, i) => (
                    <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                      <p className="text-sm font-medium text-zinc-200">{wg.name}</p>
                      <div className="flex gap-2 mt-1">
                        <Badge variant="outline" className={`text-[10px] ${wg.state === "ENABLED" ? "bg-emerald-500/10 text-emerald-400" : ""}`}>{wg.state}</Badge>
                        {wg.engine_version && <span className="text-[10px] text-zinc-500">{wg.engine_version}</span>}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Databases */}
              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="athena-databases">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Databases ({databases.length})</CardTitle></CardHeader>
                <CardContent>
                  {databases.length === 0 ? (
                    <p className="text-xs text-zinc-500">No databases found. Create tables from your S3 data.</p>
                  ) : databases.map((db, i) => (
                    <div key={i} className="p-2 bg-zinc-800/40 rounded border border-zinc-800 mb-1">
                      <p className="text-xs font-medium text-zinc-200 font-mono">{db.name}</p>
                      {db.description && <p className="text-[10px] text-zinc-500">{db.description}</p>}
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Recent Executions */}
              <Card className="border-zinc-800 bg-zinc-900/60 md:col-span-2" data-testid="athena-executions">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Recent Executions ({executions.length})</CardTitle></CardHeader>
                <CardContent>
                  {executions.length === 0 ? (
                    <p className="text-xs text-zinc-500">No recent query executions.</p>
                  ) : (
                    <div className="space-y-2">
                      {executions.map((ex, i) => (
                        <div key={i} className="flex items-center justify-between bg-zinc-800/40 rounded p-3 border border-zinc-800">
                          <div className="flex-1 min-w-0 mr-3">
                            <p className="text-xs text-zinc-300 font-mono truncate">{ex.query}</p>
                            <p className="text-[10px] text-zinc-500">{ex.submitted_at} | {(ex.data_scanned_bytes / 1024).toFixed(1)} KB scanned</p>
                          </div>
                          <Badge variant="outline" className={`text-[10px] ${stateColor(ex.state)}`}>{ex.state}</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
