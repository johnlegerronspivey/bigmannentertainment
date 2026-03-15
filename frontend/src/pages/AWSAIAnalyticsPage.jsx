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
      </div>
    </CardContent>
  </Card>
);

const sentimentColor = (s) => {
  const map = { POSITIVE: "text-emerald-400", NEGATIVE: "text-rose-400", NEUTRAL: "text-zinc-400", MIXED: "text-amber-400" };
  return map[s] || "text-zinc-400";
};

/* ──── Main Page ──── */
export default function AWSAIAnalyticsPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("comprehend");

  // Comprehend state
  const [text, setText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [sentimentResult, setSentimentResult] = useState(null);
  const [entitiesResult, setEntitiesResult] = useState(null);
  const [phrasesResult, setPhrasesResult] = useState(null);
  const [piiResult, setPiiResult] = useState(null);
  const [history, setHistory] = useState([]);

  // Personalize state
  const [datasetGroups, setDatasetGroups] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [solutions, setSolutions] = useState([]);
  const [recipes, setRecipes] = useState([]);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/aws-ai/status`, { headers });
      if (res.ok) setStatus(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  /* Comprehend actions */
  const analyzeAll = async () => {
    if (!text.trim()) return toast.error("Enter text to analyze");
    setAnalyzing(true);
    setSentimentResult(null); setEntitiesResult(null); setPhrasesResult(null); setPiiResult(null);
    try {
      const body = JSON.stringify({ text, language: "en" });
      const [sRes, eRes, pRes, piiRes] = await Promise.all([
        fetch(`${API}/api/aws-ai/comprehend/sentiment`, { method: "POST", headers, body }),
        fetch(`${API}/api/aws-ai/comprehend/entities`, { method: "POST", headers, body }),
        fetch(`${API}/api/aws-ai/comprehend/key-phrases`, { method: "POST", headers, body }),
        fetch(`${API}/api/aws-ai/comprehend/pii`, { method: "POST", headers, body }),
      ]);
      if (sRes.ok) setSentimentResult(await sRes.json());
      if (eRes.ok) setEntitiesResult(await eRes.json());
      if (pRes.ok) setPhrasesResult(await pRes.json());
      if (piiRes.ok) setPiiResult(await piiRes.json());
      toast.success("Analysis complete");
      fetchHistory();
    } catch (e) { toast.error("Analysis failed"); }
    finally { setAnalyzing(false); }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API}/api/aws-ai/comprehend/history?limit=10`, { headers });
      if (res.ok) { const d = await res.json(); setHistory(d.history || []); }
    } catch (e) { /* ignore */ }
  };

  /* Personalize actions */
  const fetchPersonalize = async () => {
    try {
      const [dgRes, cRes, sRes, rRes] = await Promise.all([
        fetch(`${API}/api/aws-ai/personalize/dataset-groups`, { headers }),
        fetch(`${API}/api/aws-ai/personalize/campaigns`, { headers }),
        fetch(`${API}/api/aws-ai/personalize/solutions`, { headers }),
        fetch(`${API}/api/aws-ai/personalize/recipes`, { headers }),
      ]);
      if (dgRes.ok) { const d = await dgRes.json(); setDatasetGroups(d.dataset_groups || []); }
      if (cRes.ok) { const d = await cRes.json(); setCampaigns(d.campaigns || []); }
      if (sRes.ok) { const d = await sRes.json(); setSolutions(d.solutions || []); }
      if (rRes.ok) { const d = await rRes.json(); setRecipes(d.recipes || []); }
    } catch (e) { console.error(e); }
  };

  useEffect(() => { if (tab === "comprehend" && token) fetchHistory(); }, [tab, token]);
  useEffect(() => { if (tab === "personalize" && token) fetchPersonalize(); }, [tab, token]);

  if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><div className="text-zinc-400">Loading...</div></div>;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-ai-analytics-page">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-zinc-100 mb-1">AI Analytics</h1>
          <p className="text-sm text-zinc-500">AWS Comprehend NLP & Personalize Recommendations</p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <ServiceCard title="AWS Comprehend" data={status?.comprehend} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>} />
          <ServiceCard title="AWS Personalize" data={status?.personalize} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>} />
        </div>

        {/* Tabs */}
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="bg-zinc-900 border border-zinc-800 mb-6">
            <TabsTrigger value="comprehend" className="data-[state=active]:bg-violet-600 data-[state=active]:text-white" data-testid="tab-comprehend">Comprehend</TabsTrigger>
            <TabsTrigger value="personalize" className="data-[state=active]:bg-violet-600 data-[state=active]:text-white" data-testid="tab-personalize">Personalize</TabsTrigger>
          </TabsList>

          {/* ── COMPREHEND TAB ── */}
          <TabsContent value="comprehend">
            <Card className="border-zinc-800 bg-zinc-900/60 mb-6">
              <CardHeader className="pb-3"><CardTitle className="text-base text-zinc-100">Text Analysis</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Enter text to analyze for sentiment, entities, key phrases, and PII..."
                  className="w-full h-32 bg-zinc-800 border border-zinc-700 rounded-lg p-3 text-sm text-zinc-100 placeholder-zinc-500 resize-none focus:outline-none focus:ring-1 focus:ring-violet-500"
                  data-testid="comprehend-text-input"
                />
                <div className="flex items-center justify-between">
                  <span className="text-xs text-zinc-500">{text.length} characters</span>
                  <Button onClick={analyzeAll} disabled={analyzing || !text.trim()} className="bg-violet-600 hover:bg-violet-700" data-testid="comprehend-analyze-btn">
                    {analyzing ? "Analyzing..." : "Analyze Text"}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Results */}
            {sentimentResult && (
              <Card className="border-zinc-800 bg-zinc-900/60 mb-4" data-testid="sentiment-result">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Sentiment Analysis</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex items-center gap-3 mb-3">
                    <Badge variant="outline" className={`${sentimentColor(sentimentResult.sentiment)} border-current/30 bg-current/10`}>{sentimentResult.sentiment}</Badge>
                  </div>
                  <div className="grid grid-cols-4 gap-2">
                    {Object.entries(sentimentResult.scores || {}).map(([k, v]) => (
                      <div key={k} className="bg-zinc-800/50 rounded p-2 text-center">
                        <div className="text-[10px] text-zinc-500 capitalize">{k}</div>
                        <div className="text-sm font-mono text-zinc-200">{(v * 100).toFixed(1)}%</div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {entitiesResult && entitiesResult.entities?.length > 0 && (
              <Card className="border-zinc-800 bg-zinc-900/60 mb-4" data-testid="entities-result">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Named Entities ({entitiesResult.total})</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {entitiesResult.entities.map((e, i) => (
                      <Badge key={i} variant="outline" className="bg-sky-500/10 text-sky-400 border-sky-500/30 text-xs">
                        {e.text} <span className="ml-1 text-sky-500/60">({e.type})</span>
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {phrasesResult && phrasesResult.key_phrases?.length > 0 && (
              <Card className="border-zinc-800 bg-zinc-900/60 mb-4" data-testid="phrases-result">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Key Phrases ({phrasesResult.total})</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {phrasesResult.key_phrases.map((p, i) => (
                      <Badge key={i} variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/30 text-xs">{p.text}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {piiResult && piiResult.pii_entities?.length > 0 && (
              <Card className="border-zinc-800 bg-zinc-900/60 mb-4" data-testid="pii-result">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">PII Detected ({piiResult.total})</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {piiResult.pii_entities.map((p, i) => (
                      <Badge key={i} variant="outline" className="bg-rose-500/10 text-rose-400 border-rose-500/30 text-xs">{p.type} ({(p.score * 100).toFixed(0)}%)</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* History */}
            {history.length > 0 && (
              <Card className="border-zinc-800 bg-zinc-900/60 mt-6" data-testid="analysis-history">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Recent Analyses</CardTitle></CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {history.map((h, i) => (
                      <div key={i} className="flex items-center justify-between bg-zinc-800/40 rounded p-3 border border-zinc-800">
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-zinc-300 truncate">{h.input_text}</p>
                          <p className="text-[10px] text-zinc-500">{h.created_at}</p>
                        </div>
                        <Badge variant="outline" className={`${sentimentColor(h.result?.sentiment)} border-current/30 bg-current/10 text-[10px] ml-2`}>{h.result?.sentiment}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* ── PERSONALIZE TAB ── */}
          <TabsContent value="personalize">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Dataset Groups */}
              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="personalize-dataset-groups">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Dataset Groups ({datasetGroups.length})</CardTitle></CardHeader>
                <CardContent>
                  {datasetGroups.length === 0 ? (
                    <p className="text-xs text-zinc-500">No dataset groups found. Create one in the AWS Console to start building recommendation models.</p>
                  ) : datasetGroups.map((dg, i) => (
                    <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                      <p className="text-sm font-medium text-zinc-200">{dg.name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-[10px] bg-indigo-500/10 text-indigo-400 border-indigo-500/30">{dg.status}</Badge>
                        {dg.domain && <span className="text-[10px] text-zinc-500">{dg.domain}</span>}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Campaigns */}
              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="personalize-campaigns">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Campaigns ({campaigns.length})</CardTitle></CardHeader>
                <CardContent>
                  {campaigns.length === 0 ? (
                    <p className="text-xs text-zinc-500">No campaigns found. Train a solution and deploy a campaign to serve real-time recommendations.</p>
                  ) : campaigns.map((c, i) => (
                    <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                      <p className="text-sm font-medium text-zinc-200">{c.name}</p>
                      <Badge variant="outline" className="text-[10px] bg-emerald-500/10 text-emerald-400 border-emerald-500/30 mt-1">{c.status}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Solutions */}
              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="personalize-solutions">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Solutions ({solutions.length})</CardTitle></CardHeader>
                <CardContent>
                  {solutions.length === 0 ? (
                    <p className="text-xs text-zinc-500">No solutions found. Create a solution using one of the available recipes to train a recommendation model.</p>
                  ) : solutions.map((s, i) => (
                    <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                      <p className="text-sm font-medium text-zinc-200">{s.name}</p>
                      <Badge variant="outline" className="text-[10px] mt-1">{s.status}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Recipes */}
              <Card className="border-zinc-800 bg-zinc-900/60" data-testid="personalize-recipes">
                <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Available Recipes ({recipes.length})</CardTitle></CardHeader>
                <CardContent>
                  {recipes.length === 0 ? (
                    <p className="text-xs text-zinc-500">No recipes available.</p>
                  ) : (
                    <div className="max-h-64 overflow-y-auto space-y-1">
                      {recipes.map((r, i) => (
                        <div key={i} className="p-2 bg-zinc-800/40 rounded border border-zinc-800">
                          <p className="text-xs font-medium text-zinc-200">{r.name}</p>
                          {r.description && <p className="text-[10px] text-zinc-500 mt-0.5">{r.description}</p>}
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
