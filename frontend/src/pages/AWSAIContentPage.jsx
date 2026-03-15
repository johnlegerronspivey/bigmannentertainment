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
          <tr><td colSpan={columns.length} className="py-8 text-center text-zinc-500">{emptyMsg || "No data found"}</td></tr>
        ) : rows.map((row, i) => (
          <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
            {columns.map((c, j) => <td key={j} className="py-2 px-3 text-zinc-300 text-xs">{c.render ? c.render(row) : row[c.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

/* ──── Main Page ──── */
export default function AWSAIContentPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("translate");

  // Translate state
  const [srcText, setSrcText] = useState("");
  const [targetLang, setTargetLang] = useState("es");
  const [translatedResult, setTranslatedResult] = useState(null);
  const [languages, setLanguages] = useState([]);
  const [translating, setTranslating] = useState(false);

  // Polly state
  const [voices, setVoices] = useState([]);
  const [ttsText, setTtsText] = useState("");
  const [ttsVoice, setTtsVoice] = useState("Joanna");
  const [ttsResult, setTtsResult] = useState(null);
  const [synthesizing, setSynthesizing] = useState(false);

  // Textract state
  const [textractBucket, setTextractBucket] = useState("");
  const [textractKey, setTextractKey] = useState("");
  const [textractResult, setTextractResult] = useState(null);
  const [extracting, setExtracting] = useState(false);

  // SageMaker state
  const [notebooks, setNotebooks] = useState([]);
  const [trainingJobs, setTrainingJobs] = useState([]);
  const [models, setModels] = useState([]);
  const [endpoints, setEndpoints] = useState([]);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/aws-ai-content/status`, { headers });
      if (res.ok) setStatus(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  /* Translate */
  const translateText = async () => {
    if (!srcText.trim()) return toast.error("Enter text to translate");
    setTranslating(true);
    try {
      const res = await fetch(`${API}/api/aws-ai-content/translate/text`, { method: "POST", headers, body: JSON.stringify({ text: srcText, source_language: "auto", target_language: targetLang }) });
      if (res.ok) { setTranslatedResult(await res.json()); toast.success("Translated!"); }
      else toast.error("Translation failed");
    } catch (e) { toast.error("Translation error"); }
    finally { setTranslating(false); }
  };

  const fetchLanguages = async () => {
    try {
      const res = await fetch(`${API}/api/aws-ai-content/translate/languages`, { headers });
      if (res.ok) { const d = await res.json(); setLanguages(d.languages || []); }
    } catch (e) { console.error(e); }
  };

  /* Polly */
  const fetchVoices = async () => {
    try {
      const res = await fetch(`${API}/api/aws-ai-content/polly/voices`, { headers });
      if (res.ok) { const d = await res.json(); setVoices(d.voices || []); }
    } catch (e) { console.error(e); }
  };

  const synthesize = async () => {
    if (!ttsText.trim()) return toast.error("Enter text for speech");
    setSynthesizing(true);
    try {
      const res = await fetch(`${API}/api/aws-ai-content/polly/synthesize`, { method: "POST", headers, body: JSON.stringify({ text: ttsText, voice_id: ttsVoice }) });
      if (res.ok) { setTtsResult(await res.json()); toast.success("Speech synthesized!"); }
      else toast.error("Synthesis failed");
    } catch (e) { toast.error("Synthesis error"); }
    finally { setSynthesizing(false); }
  };

  /* Textract */
  const analyzeDoc = async () => {
    if (!textractBucket || !textractKey) return toast.error("Enter S3 bucket and key");
    setExtracting(true);
    try {
      const res = await fetch(`${API}/api/aws-ai-content/textract/detect-text`, { method: "POST", headers, body: JSON.stringify({ bucket: textractBucket, key: textractKey }) });
      if (res.ok) { setTextractResult(await res.json()); toast.success("Text extracted!"); }
      else toast.error("Extraction failed");
    } catch (e) { toast.error("Extraction error"); }
    finally { setExtracting(false); }
  };

  /* SageMaker */
  const fetchSageMaker = async () => {
    const endpoints_list = ["notebooks", "training-jobs", "models", "endpoints"];
    const setters = [setNotebooks, setTrainingJobs, setModels, setEndpoints];
    const keys = ["notebooks", "training_jobs", "models", "endpoints"];
    for (let i = 0; i < endpoints_list.length; i++) {
      try {
        const res = await fetch(`${API}/api/aws-ai-content/sagemaker/${endpoints_list[i]}`, { headers });
        if (res.ok) { const d = await res.json(); setters[i](d[keys[i]] || []); }
      } catch (e) { console.error(e); }
    }
  };

  useEffect(() => {
    if (tab === "translate") fetchLanguages();
    if (tab === "polly") fetchVoices();
    if (tab === "sagemaker") fetchSageMaker();
  }, [tab]);

  if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><div className="animate-spin w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full" /></div>;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-ai-content-page">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">AI & Content Services</h1>
          <p className="text-zinc-400 text-sm">Translate, Polly TTS, Textract OCR, SageMaker ML</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <ServiceCard title="Translate" data={status?.translate} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" /></svg>} />
          <ServiceCard title="Polly" data={status?.polly} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>} />
          <ServiceCard title="Textract" data={status?.textract} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>} />
          <ServiceCard title="SageMaker" data={status?.sagemaker} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>} />
        </div>

        <Tabs value={tab} onValueChange={setTab} className="space-y-6">
          <TabsList className="bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="translate" data-testid="tab-translate">Translate</TabsTrigger>
            <TabsTrigger value="polly" data-testid="tab-polly">Polly TTS</TabsTrigger>
            <TabsTrigger value="textract" data-testid="tab-textract">Textract</TabsTrigger>
            <TabsTrigger value="sagemaker" data-testid="tab-sagemaker">SageMaker</TabsTrigger>
          </TabsList>

          {/* TRANSLATE TAB */}
          <TabsContent value="translate">
            <Card className="border-zinc-800 bg-zinc-900/60">
              <CardHeader><CardTitle className="text-lg">Text Translation</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <textarea className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-3 text-sm text-zinc-100 resize-none" rows={4} placeholder="Enter text to translate..." value={srcText} onChange={(e) => setSrcText(e.target.value)} data-testid="translate-input" />
                <div className="flex items-center gap-3">
                  <select className="bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-sm text-zinc-100" value={targetLang} onChange={(e) => setTargetLang(e.target.value)} data-testid="translate-target-lang">
                    {languages.length > 0 ? languages.map(l => <option key={l.code} value={l.code}>{l.name} ({l.code})</option>) :
                      ["es","fr","de","it","pt","ja","ko","zh","ar","hi","ru"].map(c => <option key={c} value={c}>{c}</option>)
                    }
                  </select>
                  <Button onClick={translateText} disabled={translating} data-testid="translate-btn">{translating ? "Translating..." : "Translate"}</Button>
                </div>
                {translatedResult && (
                  <Card className="border-zinc-700 bg-zinc-800/50" data-testid="translate-result">
                    <CardContent className="p-4">
                      <p className="text-xs text-zinc-500 mb-1">{translatedResult.source_language} → {translatedResult.target_language}</p>
                      <p className="text-zinc-100">{translatedResult.translated_text}</p>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* POLLY TAB */}
          <TabsContent value="polly">
            <Card className="border-zinc-800 bg-zinc-900/60">
              <CardHeader><CardTitle className="text-lg">Text-to-Speech</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <textarea className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-3 text-sm text-zinc-100 resize-none" rows={3} placeholder="Enter text to convert to speech..." value={ttsText} onChange={(e) => setTtsText(e.target.value)} data-testid="polly-text-input" />
                <div className="flex items-center gap-3">
                  <select className="bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-sm text-zinc-100" value={ttsVoice} onChange={(e) => setTtsVoice(e.target.value)} data-testid="polly-voice-select">
                    {voices.length > 0 ? voices.slice(0, 30).map(v => <option key={v.id} value={v.id}>{v.name} ({v.language_name}, {v.gender})</option>) :
                      ["Joanna","Matthew","Ivy","Kendra","Amy"].map(v => <option key={v} value={v}>{v}</option>)
                    }
                  </select>
                  <Button onClick={synthesize} disabled={synthesizing} data-testid="polly-synthesize-btn">{synthesizing ? "Synthesizing..." : "Synthesize"}</Button>
                </div>
                {ttsResult && (
                  <Card className="border-zinc-700 bg-zinc-800/50" data-testid="polly-result">
                    <CardContent className="p-4 text-sm">
                      <p className="text-zinc-400">Content-Type: <span className="text-zinc-200">{ttsResult.content_type}</span></p>
                      <p className="text-zinc-400">Characters: <span className="text-zinc-200">{ttsResult.request_characters}</span></p>
                      <p className="text-zinc-400">Audio Ready: <span className="text-emerald-400">{ttsResult.audio_available ? "Yes" : "No"}</span></p>
                    </CardContent>
                  </Card>
                )}
                <h3 className="text-sm font-semibold text-zinc-300 mt-6">Available Voices ({voices.length})</h3>
                <DataTable
                  columns={[
                    { key: "name", label: "Name" },
                    { key: "id", label: "ID" },
                    { key: "gender", label: "Gender" },
                    { key: "language_name", label: "Language" },
                    { key: "supported_engines", label: "Engines", render: (r) => (r.supported_engines || []).join(", ") },
                  ]}
                  rows={voices.slice(0, 20)}
                  emptyMsg="No voices found"
                />
              </CardContent>
            </Card>
          </TabsContent>

          {/* TEXTRACT TAB */}
          <TabsContent value="textract">
            <Card className="border-zinc-800 bg-zinc-900/60">
              <CardHeader><CardTitle className="text-lg">Document Text Extraction</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <input className="bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-sm text-zinc-100" placeholder="S3 Bucket" value={textractBucket} onChange={(e) => setTextractBucket(e.target.value)} data-testid="textract-bucket" />
                  <input className="bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-sm text-zinc-100" placeholder="S3 Key (file path)" value={textractKey} onChange={(e) => setTextractKey(e.target.value)} data-testid="textract-key" />
                </div>
                <Button onClick={analyzeDoc} disabled={extracting} data-testid="textract-extract-btn">{extracting ? "Extracting..." : "Extract Text"}</Button>
                {textractResult && (
                  <Card className="border-zinc-700 bg-zinc-800/50" data-testid="textract-result">
                    <CardContent className="p-4 space-y-2 text-sm">
                      <div className="grid grid-cols-3 gap-2">
                        <p className="text-zinc-400">Lines: <span className="text-zinc-200">{textractResult.lines}</span></p>
                        <p className="text-zinc-400">Words: <span className="text-zinc-200">{textractResult.words}</span></p>
                        <p className="text-zinc-400">Confidence: <span className="text-emerald-400">{textractResult.confidence}%</span></p>
                      </div>
                      {textractResult.extracted_text && (
                        <pre className="bg-zinc-900 p-3 rounded text-xs text-zinc-300 whitespace-pre-wrap max-h-60 overflow-y-auto">{textractResult.extracted_text}</pre>
                      )}
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* SAGEMAKER TAB */}
          <TabsContent value="sagemaker">
            <div className="space-y-6">
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Notebook Instances ({notebooks.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Name" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className="text-[10px]">{r.status}</Badge> },
                    { key: "instance_type", label: "Type" },
                    { key: "created_at", label: "Created" },
                  ]} rows={notebooks} emptyMsg="No notebook instances" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Training Jobs ({trainingJobs.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Job Name" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className="text-[10px]">{r.status}</Badge> },
                    { key: "created_at", label: "Created" },
                  ]} rows={trainingJobs} emptyMsg="No training jobs" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Models ({models.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Model Name" },
                    { key: "created_at", label: "Created" },
                  ]} rows={models} emptyMsg="No models deployed" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Endpoints ({endpoints.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Endpoint Name" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className="text-[10px]">{r.status}</Badge> },
                    { key: "created_at", label: "Created" },
                  ]} rows={endpoints} emptyMsg="No endpoints" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
