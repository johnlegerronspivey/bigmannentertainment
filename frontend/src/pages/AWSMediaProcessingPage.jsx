import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Progress } from "../components/ui/progress";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

/* ─── Helpers ─── */
const statusColor = (s) => {
  const map = {
    COMPLETE: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    COMPLETED: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    PROGRESSING: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    IN_PROGRESS: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    SUBMITTED: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    ERROR: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    FAILED: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    CANCELED: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
  };
  return map[s] || "bg-zinc-500/15 text-zinc-400 border-zinc-500/30";
};

const fmt = (iso) => {
  if (!iso) return "—";
  try { return new Date(iso).toLocaleString(); } catch { return iso; }
};

/* ─── Service Status Card ─── */
const ServiceStatus = ({ title, data, icon }) => {
  const available = data?.available;
  return (
    <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm" data-testid={`service-status-${title.toLowerCase().replace(/\s/g, "-")}`}>
      <CardContent className="p-5">
        <div className="flex items-center gap-3 mb-3">
          <div className={`p-2.5 rounded-lg ${available ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`}>
            {icon}
          </div>
          <div>
            <h3 className="font-semibold text-zinc-100 text-sm">{title}</h3>
            <Badge variant="outline" className={`text-[10px] mt-1 ${available ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : "bg-rose-500/15 text-rose-400 border-rose-500/30"}`}>
              {available ? "Connected" : "Unavailable"}
            </Badge>
          </div>
        </div>
        <div className="text-xs text-zinc-500 space-y-1">
          {data?.region && <p>Region: <span className="text-zinc-300">{data.region}</span></p>}
          {data?.endpoint && <p>Endpoint: <span className="text-zinc-300 break-all">{data.endpoint}</span></p>}
          {data?.languages !== undefined && <p>Languages: <span className="text-zinc-300">{data.languages}</span></p>}
          {data?.total_jobs !== undefined && <p>Your jobs: <span className="text-zinc-300">{data.total_jobs}</span></p>}
        </div>
      </CardContent>
    </Card>
  );
};

/* ─── Transcode Form ─── */
const TranscodeForm = ({ presets, onSubmit, loading }) => {
  const [s3Key, setS3Key] = useState("");
  const [preset, setPreset] = useState("");

  return (
    <Card className="border-zinc-800 bg-zinc-900/60" data-testid="transcode-form">
      <CardHeader className="pb-3">
        <CardTitle className="text-base text-zinc-100">New Transcoding Job</CardTitle>
        <CardDescription className="text-zinc-500 text-xs">Convert media files for any platform using AWS MediaConvert</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="block text-xs text-zinc-400 mb-1.5">S3 Input Key</label>
          <input
            data-testid="mc-s3-key-input"
            type="text"
            value={s3Key}
            onChange={(e) => setS3Key(e.target.value)}
            placeholder="audio/user123/2026/track.mp4"
            className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:border-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-1.5">Output Preset</label>
          <select
            data-testid="mc-preset-select"
            value={preset}
            onChange={(e) => setPreset(e.target.value)}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select a preset...</option>
            {Object.entries(presets).map(([k, v]) => (
              <option key={k} value={k}>{v.label} ({v.container})</option>
            ))}
          </select>
        </div>
        <Button
          data-testid="mc-submit-btn"
          onClick={() => { onSubmit(s3Key, preset); setS3Key(""); setPreset(""); }}
          disabled={!s3Key || !preset || loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white"
        >
          {loading ? "Submitting..." : "Start Transcoding"}
        </Button>
      </CardContent>
    </Card>
  );
};

/* ─── Transcribe Form ─── */
const TranscribeForm = ({ languages, onSubmit, loading }) => {
  const [s3Key, setS3Key] = useState("");
  const [lang, setLang] = useState("en-US");
  const [autoDetect, setAutoDetect] = useState(false);
  const [subtitles, setSubtitles] = useState(true);

  return (
    <Card className="border-zinc-800 bg-zinc-900/60" data-testid="transcribe-form">
      <CardHeader className="pb-3">
        <CardTitle className="text-base text-zinc-100">New Transcription Job</CardTitle>
        <CardDescription className="text-zinc-500 text-xs">Generate captions & subtitles for audio/video using AWS Transcribe</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="block text-xs text-zinc-400 mb-1.5">S3 Input Key</label>
          <input
            data-testid="tr-s3-key-input"
            type="text"
            value={s3Key}
            onChange={(e) => setS3Key(e.target.value)}
            placeholder="video/user123/interview.mp4"
            className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:border-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-xs text-zinc-400 mb-1.5">Language</label>
          <select
            data-testid="tr-language-select"
            value={lang}
            onChange={(e) => setLang(e.target.value)}
            disabled={autoDetect}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 focus:border-blue-500 focus:outline-none disabled:opacity-50"
          >
            {Object.entries(languages).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-xs text-zinc-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoDetect}
              onChange={(e) => setAutoDetect(e.target.checked)}
              className="accent-blue-500"
            />
            Auto-detect language
          </label>
          <label className="flex items-center gap-2 text-xs text-zinc-400 cursor-pointer">
            <input
              type="checkbox"
              checked={subtitles}
              onChange={(e) => setSubtitles(e.target.checked)}
              className="accent-blue-500"
            />
            Generate subtitles (VTT + SRT)
          </label>
        </div>
        <Button
          data-testid="tr-submit-btn"
          onClick={() => { onSubmit(s3Key, lang, autoDetect, subtitles); setS3Key(""); }}
          disabled={!s3Key || loading}
          className="w-full bg-violet-600 hover:bg-violet-700 text-white"
        >
          {loading ? "Starting..." : "Start Transcription"}
        </Button>
      </CardContent>
    </Card>
  );
};

/* ─── Job Row ─── */
const MCJobRow = ({ job, onRefresh }) => (
  <div className="flex items-center justify-between p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`mc-job-${job.job_id}`}>
    <div className="min-w-0 flex-1">
      <p className="text-sm text-zinc-200 font-mono truncate">{job.job_id}</p>
      <div className="flex items-center gap-2 mt-1">
        <Badge variant="outline" className={`text-[10px] ${statusColor(job.status)}`}>{job.status}</Badge>
        {job.user_metadata?.preset && <span className="text-[10px] text-zinc-500">{job.user_metadata.preset}</span>}
        {job.progress > 0 && job.progress < 100 && (
          <Progress value={job.progress} className="w-24 h-1.5" />
        )}
      </div>
    </div>
    <div className="flex items-center gap-2 ml-3">
      <span className="text-[10px] text-zinc-600">{fmt(job.created_at)}</span>
      <Button size="sm" variant="ghost" className="text-zinc-400 hover:text-zinc-200 h-7 px-2" onClick={() => onRefresh(job.job_id)} data-testid={`mc-refresh-${job.job_id}`}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
      </Button>
    </div>
  </div>
);

const TRJobRow = ({ job, onView, onRefresh }) => (
  <div className="flex items-center justify-between p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`tr-job-${job.job_name}`}>
    <div className="min-w-0 flex-1">
      <p className="text-sm text-zinc-200 font-mono truncate">{job.job_name}</p>
      <div className="flex items-center gap-2 mt-1">
        <Badge variant="outline" className={`text-[10px] ${statusColor(job.status)}`}>{job.status}</Badge>
        <span className="text-[10px] text-zinc-500">{job.language}</span>
        {job.failure_reason && <span className="text-[10px] text-rose-400 truncate max-w-[200px]">{job.failure_reason}</span>}
      </div>
    </div>
    <div className="flex items-center gap-2 ml-3">
      <span className="text-[10px] text-zinc-600">{fmt(job.created_at)}</span>
      {job.status === "COMPLETED" && (
        <Button size="sm" variant="ghost" className="text-violet-400 hover:text-violet-300 h-7 px-2" onClick={() => onView(job.job_name)} data-testid={`tr-view-${job.job_name}`}>
          View
        </Button>
      )}
      <Button size="sm" variant="ghost" className="text-zinc-400 hover:text-zinc-200 h-7 px-2" onClick={() => onRefresh(job.job_name)} data-testid={`tr-refresh-${job.job_name}`}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
      </Button>
    </div>
  </div>
);

/* ─── Transcript Viewer Modal ─── */
const TranscriptViewer = ({ data, onClose }) => {
  if (!data) return null;
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose} data-testid="transcript-viewer-modal">
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-zinc-800">
          <div>
            <h3 className="text-sm font-semibold text-zinc-100">Transcript Result</h3>
            <p className="text-[10px] text-zinc-500 font-mono mt-0.5">{data.job_name}</p>
          </div>
          <Button size="sm" variant="ghost" onClick={onClose} className="text-zinc-400 h-7 px-2" data-testid="transcript-viewer-close">Close</Button>
        </div>
        <div className="p-4 overflow-y-auto max-h-[60vh] space-y-4">
          {data.transcript_text && (
            <div>
              <h4 className="text-xs font-medium text-zinc-400 mb-2">Full Transcript</h4>
              <p className="text-sm text-zinc-300 leading-relaxed bg-zinc-800/50 p-3 rounded-lg">{data.transcript_text}</p>
            </div>
          )}
          {data.subtitle_files?.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-zinc-400 mb-2">Subtitle Files</h4>
              <div className="space-y-2">
                {data.subtitle_files.map((f, i) => (
                  <div key={i} className="flex items-center justify-between bg-zinc-800/50 p-2 rounded-lg">
                    <div>
                      <Badge variant="outline" className="text-[10px] bg-violet-500/15 text-violet-400 border-violet-500/30">{f.format}</Badge>
                    </div>
                    <a href={f.cdn_url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:text-blue-300 underline">
                      Download via CDN
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-zinc-800/50 p-2 rounded-lg"><span className="text-zinc-500">Status:</span> <Badge variant="outline" className={`ml-1 text-[10px] ${statusColor(data.status)}`}>{data.status}</Badge></div>
            <div className="bg-zinc-800/50 p-2 rounded-lg"><span className="text-zinc-500">Language:</span> <span className="text-zinc-300 ml-1">{data.language}</span></div>
            {data.created_at && <div className="bg-zinc-800/50 p-2 rounded-lg"><span className="text-zinc-500">Started:</span> <span className="text-zinc-300 ml-1">{fmt(data.created_at)}</span></div>}
            {data.completed_at && <div className="bg-zinc-800/50 p-2 rounded-lg"><span className="text-zinc-500">Completed:</span> <span className="text-zinc-300 ml-1">{fmt(data.completed_at)}</span></div>}
          </div>
        </div>
      </div>
    </div>
  );
};

/* ══════════════════════════════════════════════════════════════ */
/*  MAIN PAGE                                                    */
/* ══════════════════════════════════════════════════════════════ */
export default function AWSMediaProcessingPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState("transcode");
  const [status, setStatus] = useState(null);
  const [presets, setPresets] = useState({});
  const [languages, setLanguages] = useState({});
  const [mcJobs, setMcJobs] = useState([]);
  const [trJobs, setTrJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState(null);

  const hdrs = () => ({ Authorization: `Bearer ${localStorage.getItem("token")}`, "Content-Type": "application/json" });

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-media/status`, { headers: hdrs() });
      if (res.ok) setStatus(await res.json());
    } catch {}
  }, [user]);

  const fetchPresets = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-media/mediaconvert/presets`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setPresets(d.presets || {}); }
    } catch {}
  }, [user]);

  const fetchLanguages = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-media/transcribe/languages`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setLanguages(d.languages || {}); }
    } catch {}
  }, [user]);

  const fetchMCJobs = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-media/mediaconvert/jobs`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setMcJobs(d.jobs || []); }
    } catch {}
  }, [user]);

  const fetchTRJobs = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-media/transcribe/jobs`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setTrJobs(d.jobs || []); }
    } catch {}
  }, [user]);

  useEffect(() => {
    if (!user) return;
    fetchStatus();
    fetchPresets();
    fetchLanguages();
    fetchMCJobs();
    fetchTRJobs();
  }, [user]);

  /* ─── Actions ─── */
  const submitMCJob = async (s3Key, preset) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-media/mediaconvert/jobs`, {
        method: "POST", headers: hdrs(), body: JSON.stringify({ s3_input_key: s3Key, preset }),
      });
      const d = await res.json();
      if (res.ok) { toast.success(`Transcoding job started: ${d.job_id}`); fetchMCJobs(); fetchStatus(); }
      else toast.error(d.detail || "Failed to start job");
    } catch (e) { toast.error("Network error"); }
    setLoading(false);
  };

  const submitTRJob = async (s3Key, lang, autoDetect, subtitles) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-media/transcribe/jobs`, {
        method: "POST", headers: hdrs(),
        body: JSON.stringify({ s3_input_key: s3Key, language_code: lang, identify_language: autoDetect, enable_subtitles: subtitles }),
      });
      const d = await res.json();
      if (res.ok) { toast.success(`Transcription started: ${d.job_name}`); fetchTRJobs(); fetchStatus(); }
      else toast.error(d.detail || "Failed to start transcription");
    } catch (e) { toast.error("Network error"); }
    setLoading(false);
  };

  const refreshMCJob = async (jobId) => {
    try {
      const res = await fetch(`${API}/api/aws-media/mediaconvert/jobs/${jobId}`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setMcJobs((prev) => prev.map((j) => j.job_id === jobId ? { ...j, ...d } : j)); toast.success("Job refreshed"); }
    } catch {}
  };

  const refreshTRJob = async (jobName) => {
    try {
      const res = await fetch(`${API}/api/aws-media/transcribe/jobs/${jobName}`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setTrJobs((prev) => prev.map((j) => j.job_name === jobName ? { ...j, ...d } : j)); toast.success("Job refreshed"); }
    } catch {}
  };

  const viewTranscript = async (jobName) => {
    try {
      const res = await fetch(`${API}/api/aws-media/transcribe/jobs/${jobName}`, { headers: hdrs() });
      if (res.ok) setTranscript(await res.json());
    } catch { toast.error("Failed to load transcript"); }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-media-processing-page">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight">AWS Media Processing</h1>
          <p className="text-sm text-zinc-500 mt-1">Transcode media for any platform and auto-generate captions & subtitles</p>
        </div>

        {/* Service Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <ServiceStatus
            title="MediaConvert"
            data={status?.mediaconvert}
            icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/><path d="m10 9 5 3-5 3V9z"/></svg>}
          />
          <ServiceStatus
            title="Transcribe"
            data={status?.transcribe}
            icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>}
          />
        </div>

        {/* Tabs */}
        <Tabs value={tab} onValueChange={setTab} className="space-y-6">
          <TabsList className="bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="transcode" className="data-[state=active]:bg-blue-600/20 data-[state=active]:text-blue-400" data-testid="tab-transcode">
              Transcode
            </TabsTrigger>
            <TabsTrigger value="transcribe" className="data-[state=active]:bg-violet-600/20 data-[state=active]:text-violet-400" data-testid="tab-transcribe">
              Transcribe
            </TabsTrigger>
          </TabsList>

          {/* ── Transcode Tab ── */}
          <TabsContent value="transcode" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <TranscodeForm presets={presets} onSubmit={submitMCJob} loading={loading} />
              </div>
              <div className="lg:col-span-2">
                <Card className="border-zinc-800 bg-zinc-900/60">
                  <CardHeader className="pb-3 flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-base text-zinc-100">Transcoding Jobs</CardTitle>
                      <CardDescription className="text-zinc-500 text-xs">{mcJobs.length} job{mcJobs.length !== 1 ? "s" : ""}</CardDescription>
                    </div>
                    <Button size="sm" variant="ghost" className="text-zinc-400 h-7" onClick={fetchMCJobs} data-testid="mc-refresh-all">Refresh</Button>
                  </CardHeader>
                  <CardContent className="space-y-2 max-h-[500px] overflow-y-auto">
                    {mcJobs.length === 0 ? (
                      <p className="text-sm text-zinc-600 text-center py-8">No transcoding jobs yet. Submit one to get started.</p>
                    ) : (
                      mcJobs.map((j) => <MCJobRow key={j.job_id} job={j} onRefresh={refreshMCJob} />)
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Preset Reference */}
            <Card className="border-zinc-800 bg-zinc-900/60">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-zinc-100">Available Presets</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {Object.entries(presets).map(([k, v]) => (
                    <div key={k} className="bg-zinc-800/50 rounded-lg p-3 border border-zinc-800">
                      <p className="text-sm text-zinc-200 font-medium">{v.label}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-[10px] bg-zinc-700/30 text-zinc-400 border-zinc-700">{v.container}</Badge>
                        <span className="text-[10px] text-zinc-600 font-mono">{k}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* ── Transcribe Tab ── */}
          <TabsContent value="transcribe" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <TranscribeForm languages={languages} onSubmit={submitTRJob} loading={loading} />
              </div>
              <div className="lg:col-span-2">
                <Card className="border-zinc-800 bg-zinc-900/60">
                  <CardHeader className="pb-3 flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-base text-zinc-100">Transcription Jobs</CardTitle>
                      <CardDescription className="text-zinc-500 text-xs">{trJobs.length} job{trJobs.length !== 1 ? "s" : ""}</CardDescription>
                    </div>
                    <Button size="sm" variant="ghost" className="text-zinc-400 h-7" onClick={fetchTRJobs} data-testid="tr-refresh-all">Refresh</Button>
                  </CardHeader>
                  <CardContent className="space-y-2 max-h-[500px] overflow-y-auto">
                    {trJobs.length === 0 ? (
                      <p className="text-sm text-zinc-600 text-center py-8">No transcription jobs yet. Submit one to get started.</p>
                    ) : (
                      trJobs.map((j) => <TRJobRow key={j.job_name} job={j} onView={viewTranscript} onRefresh={refreshTRJob} />)
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Language Reference */}
            <Card className="border-zinc-800 bg-zinc-900/60">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-zinc-100">Supported Languages</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                  {Object.entries(languages).map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between bg-zinc-800/50 rounded-lg px-3 py-2 border border-zinc-800">
                      <span className="text-sm text-zinc-300">{v}</span>
                      <span className="text-[10px] text-zinc-600 font-mono">{k}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Transcript viewer modal */}
      {transcript && <TranscriptViewer data={transcript} onClose={() => setTranscript(null)} />}
    </div>
  );
}
