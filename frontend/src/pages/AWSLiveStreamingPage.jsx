import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

const statusColor = (s) => {
  const map = {
    LIVE: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    HEALTHY: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    Connected: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    STARVING: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    OFFLINE: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
    Unavailable: "bg-rose-500/15 text-rose-400 border-rose-500/30",
  };
  return map[s] || "bg-zinc-500/15 text-zinc-400 border-zinc-500/30";
};

const fmt = (iso) => {
  if (!iso) return "\u2014";
  try { return new Date(iso).toLocaleString(); } catch { return iso; }
};

/* ---- Service Status Card ---- */
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
          {data?.service && <p>Service: <span className="text-zinc-300">{data.service}</span></p>}
          {data?.total_channels !== undefined && <p>Your channels: <span className="text-zinc-300">{data.total_channels}</span></p>}
        </div>
      </CardContent>
    </Card>
  );
};

/* ---- IVS Channel Card ---- */
const IVSChannelCard = ({ channel, onDelete, onViewStream, deleting }) => (
  <div className="p-4 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`ivs-channel-${channel.channel_name || channel.channel_arn}`}>
    <div className="flex items-center justify-between mb-2">
      <h4 className="text-sm font-semibold text-zinc-100">{channel.channel_name}</h4>
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="text-[10px] bg-blue-500/15 text-blue-400 border-blue-500/30">
          {channel.latency_mode}
        </Badge>
        {channel.authorized && (
          <Badge variant="outline" className="text-[10px] bg-amber-500/15 text-amber-400 border-amber-500/30">Auth Required</Badge>
        )}
      </div>
    </div>
    {channel.playback_url && (
      <p className="text-[10px] text-zinc-500 truncate mb-1">Playback: <span className="text-zinc-400">{channel.playback_url}</span></p>
    )}
    {channel.ingest_endpoint && (
      <p className="text-[10px] text-zinc-500 truncate mb-1">Ingest: <span className="text-zinc-400">{channel.ingest_endpoint}</span></p>
    )}
    {channel.stream_key_value && (
      <p className="text-[10px] text-zinc-500 truncate mb-2">Stream Key: <span className="text-amber-400 font-mono">{channel.stream_key_value.substring(0, 12)}...</span></p>
    )}
    <div className="flex items-center gap-2 mt-3">
      <Button size="sm" variant="ghost" className="text-blue-400 hover:text-blue-300 h-7 px-2 text-xs" onClick={() => onViewStream(channel.channel_arn)} data-testid={`ivs-view-stream-${channel.channel_name}`}>
        Stream Status
      </Button>
      <Button size="sm" variant="ghost" className="text-rose-400 hover:text-rose-300 h-7 px-2 text-xs" onClick={() => onDelete(channel.channel_arn)} disabled={deleting} data-testid={`ivs-delete-${channel.channel_name}`}>
        Delete
      </Button>
    </div>
  </div>
);

/* ---- MP Channel Card ---- */
const MPChannelCard = ({ channel, onDelete, onViewEndpoints, deleting }) => (
  <div className="p-4 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`mp-channel-${channel.id}`}>
    <div className="flex items-center justify-between mb-2">
      <h4 className="text-sm font-semibold text-zinc-100">{channel.id}</h4>
      <Badge variant="outline" className="text-[10px] bg-violet-500/15 text-violet-400 border-violet-500/30">
        {channel.ingest_endpoint_count || 0} ingest EP{(channel.ingest_endpoint_count || 0) !== 1 ? "s" : ""}
      </Badge>
    </div>
    {channel.description && <p className="text-xs text-zinc-500 mb-2">{channel.description}</p>}
    <div className="flex items-center gap-2 mt-2">
      <Button size="sm" variant="ghost" className="text-violet-400 hover:text-violet-300 h-7 px-2 text-xs" onClick={() => onViewEndpoints(channel.id)} data-testid={`mp-view-endpoints-${channel.id}`}>
        View Endpoints
      </Button>
      <Button size="sm" variant="ghost" className="text-rose-400 hover:text-rose-300 h-7 px-2 text-xs" onClick={() => onDelete(channel.id)} disabled={deleting} data-testid={`mp-delete-${channel.id}`}>
        Delete
      </Button>
    </div>
  </div>
);

/* ---- Origin Endpoint Card ---- */
const OriginEndpointCard = ({ ep, onDelete, deleting }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800" data-testid={`mp-endpoint-${ep.id}`}>
    <div className="flex items-center justify-between mb-1">
      <span className="text-sm text-zinc-200 font-mono">{ep.id}</span>
      <Badge variant="outline" className={`text-[10px] ${ep.packaging_format === "hls" ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : ep.packaging_format === "dash" ? "bg-blue-500/15 text-blue-400 border-blue-500/30" : "bg-zinc-500/15 text-zinc-400 border-zinc-500/30"}`}>
        {ep.packaging_format?.toUpperCase()}
      </Badge>
    </div>
    {ep.url && <p className="text-[10px] text-zinc-500 truncate">URL: <span className="text-zinc-400">{ep.url}</span></p>}
    {ep.description && <p className="text-[10px] text-zinc-500 mt-1">{ep.description}</p>}
    <div className="flex justify-end mt-2">
      <Button size="sm" variant="ghost" className="text-rose-400 hover:text-rose-300 h-6 px-2 text-[10px]" onClick={() => onDelete(ep.id)} disabled={deleting}>
        Delete
      </Button>
    </div>
  </div>
);

/* ---- Stream Status Modal ---- */
const StreamStatusModal = ({ data, onClose, onStop }) => {
  if (!data) return null;
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose} data-testid="stream-status-modal">
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-md w-full" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-zinc-800">
          <h3 className="text-sm font-semibold text-zinc-100">Stream Status</h3>
          <Button size="sm" variant="ghost" onClick={onClose} className="text-zinc-400 h-7 px-2" data-testid="stream-modal-close">Close</Button>
        </div>
        <div className="p-4 space-y-3">
          {data.streaming ? (
            <>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-sm text-emerald-400 font-medium">LIVE</span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-zinc-800/50 p-2 rounded-lg">
                  <span className="text-zinc-500">State:</span>
                  <Badge variant="outline" className={`ml-1 text-[10px] ${statusColor(data.state)}`}>{data.state}</Badge>
                </div>
                <div className="bg-zinc-800/50 p-2 rounded-lg">
                  <span className="text-zinc-500">Health:</span>
                  <Badge variant="outline" className={`ml-1 text-[10px] ${statusColor(data.health)}`}>{data.health}</Badge>
                </div>
                <div className="bg-zinc-800/50 p-2 rounded-lg">
                  <span className="text-zinc-500">Viewers:</span>
                  <span className="text-zinc-300 ml-1">{data.viewer_count}</span>
                </div>
                <div className="bg-zinc-800/50 p-2 rounded-lg">
                  <span className="text-zinc-500">Started:</span>
                  <span className="text-zinc-300 ml-1 text-[10px]">{fmt(data.start_time)}</span>
                </div>
              </div>
              <Button
                size="sm"
                className="w-full bg-rose-600 hover:bg-rose-700 text-white mt-2"
                onClick={() => onStop(data.channel_arn)}
                data-testid="stop-stream-btn"
              >
                Stop Stream
              </Button>
            </>
          ) : (
            <div className="text-center py-6">
              <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center mx-auto mb-3">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-zinc-500"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              </div>
              <p className="text-sm text-zinc-400">Channel is not broadcasting</p>
              <p className="text-xs text-zinc-600 mt-1">Use your stream key and ingest endpoint to start streaming</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/* ---- Endpoints Viewer Modal ---- */
const EndpointsModal = ({ channelId, endpoints, onClose, onDeleteEndpoint, deleting }) => {
  if (!channelId) return null;
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose} data-testid="endpoints-modal">
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-lg w-full max-h-[80vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-4 border-b border-zinc-800">
          <div>
            <h3 className="text-sm font-semibold text-zinc-100">Origin Endpoints</h3>
            <p className="text-[10px] text-zinc-500 font-mono mt-0.5">{channelId}</p>
          </div>
          <Button size="sm" variant="ghost" onClick={onClose} className="text-zinc-400 h-7 px-2" data-testid="endpoints-modal-close">Close</Button>
        </div>
        <div className="p-4 overflow-y-auto max-h-[60vh] space-y-3">
          {endpoints.length === 0 ? (
            <p className="text-sm text-zinc-600 text-center py-6">No origin endpoints for this channel</p>
          ) : (
            endpoints.map((ep) => (
              <OriginEndpointCard key={ep.id} ep={ep} onDelete={onDeleteEndpoint} deleting={deleting} />
            ))
          )}
        </div>
      </div>
    </div>
  );
};


/* ================================================================ */
/*  MAIN PAGE                                                        */
/* ================================================================ */
export default function AWSLiveStreamingPage() {
  const { user } = useAuth();
  const [tab, setTab] = useState("ivs");
  const [status, setStatus] = useState(null);
  const [ivsChannels, setIvsChannels] = useState([]);
  const [mpChannels, setMpChannels] = useState([]);
  const [mpEndpoints, setMpEndpoints] = useState([]);
  const [formats, setFormats] = useState({});
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [streamModal, setStreamModal] = useState(null);
  const [endpointsModal, setEndpointsModal] = useState(null);

  // IVS form state
  const [ivsName, setIvsName] = useState("");
  const [ivsType, setIvsType] = useState("STANDARD");
  const [ivsLatency, setIvsLatency] = useState("LOW");

  // MP form state
  const [mpId, setMpId] = useState("");
  const [mpDesc, setMpDesc] = useState("");
  const [epChannelId, setEpChannelId] = useState("");
  const [epId, setEpId] = useState("");
  const [epFormat, setEpFormat] = useState("hls");

  const hdrs = () => ({ Authorization: `Bearer ${localStorage.getItem("token")}`, "Content-Type": "application/json" });

  /* ---- Data fetching ---- */
  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-livestream/status`, { headers: hdrs() });
      if (res.ok) setStatus(await res.json());
    } catch {}
  }, []);

  const fetchIVSChannels = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-livestream/ivs/channels`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setIvsChannels(d.channels || []); }
    } catch {}
  }, []);

  const fetchMPChannels = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-livestream/mediapackage/channels`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setMpChannels(d.channels || []); }
    } catch {}
  }, []);

  const fetchFormats = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-livestream/mediapackage/formats`, { headers: hdrs() });
      if (res.ok) { const d = await res.json(); setFormats(d.formats || {}); }
    } catch {}
  }, []);

  useEffect(() => {
    if (!user) return;
    fetchStatus();
    fetchIVSChannels();
    fetchMPChannels();
    fetchFormats();
  }, [user]);

  /* ---- IVS Actions ---- */
  const createIVSChannel = async () => {
    if (!ivsName.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-livestream/ivs/channels`, {
        method: "POST", headers: hdrs(),
        body: JSON.stringify({ name: ivsName, channel_type: ivsType, latency_mode: ivsLatency }),
      });
      const d = await res.json();
      if (res.ok) {
        toast.success(`Channel "${ivsName}" created`);
        setIvsName("");
        fetchIVSChannels();
        fetchStatus();
      } else {
        toast.error(d.detail || "Failed to create channel");
      }
    } catch { toast.error("Network error"); }
    setLoading(false);
  };

  const deleteIVSChannel = async (arn) => {
    setDeleting(true);
    try {
      const res = await fetch(`${API}/api/aws-livestream/ivs/channels/${encodeURIComponent(arn)}`, {
        method: "DELETE", headers: hdrs(),
      });
      if (res.ok) {
        toast.success("Channel deleted");
        fetchIVSChannels();
        fetchStatus();
      } else {
        const d = await res.json();
        toast.error(d.detail || "Delete failed");
      }
    } catch { toast.error("Network error"); }
    setDeleting(false);
  };

  const viewStream = async (channelArn) => {
    try {
      const res = await fetch(`${API}/api/aws-livestream/ivs/streams/${encodeURIComponent(channelArn)}`, { headers: hdrs() });
      if (res.ok) setStreamModal(await res.json());
    } catch { toast.error("Failed to fetch stream status"); }
  };

  const stopStream = async (channelArn) => {
    try {
      const res = await fetch(`${API}/api/aws-livestream/ivs/streams/${encodeURIComponent(channelArn)}/stop`, {
        method: "POST", headers: hdrs(),
      });
      if (res.ok) {
        toast.success("Stream stopped");
        setStreamModal(null);
      } else {
        toast.error("Failed to stop stream");
      }
    } catch { toast.error("Network error"); }
  };

  /* ---- MediaPackage Actions ---- */
  const createMPChannel = async () => {
    if (!mpId.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-livestream/mediapackage/channels`, {
        method: "POST", headers: hdrs(),
        body: JSON.stringify({ channel_id: mpId, description: mpDesc }),
      });
      const d = await res.json();
      if (res.ok) {
        toast.success(`MediaPackage channel "${mpId}" created`);
        setMpId("");
        setMpDesc("");
        fetchMPChannels();
        fetchStatus();
      } else {
        toast.error(d.detail || "Failed to create channel");
      }
    } catch { toast.error("Network error"); }
    setLoading(false);
  };

  const deleteMPChannel = async (id) => {
    setDeleting(true);
    try {
      const res = await fetch(`${API}/api/aws-livestream/mediapackage/channels/${encodeURIComponent(id)}`, {
        method: "DELETE", headers: hdrs(),
      });
      if (res.ok) {
        toast.success("Channel deleted");
        fetchMPChannels();
        fetchStatus();
      } else {
        const d = await res.json();
        toast.error(d.detail || "Delete failed");
      }
    } catch { toast.error("Network error"); }
    setDeleting(false);
  };

  const viewEndpoints = async (channelId) => {
    try {
      const res = await fetch(`${API}/api/aws-livestream/mediapackage/endpoints?channel_id=${encodeURIComponent(channelId)}`, { headers: hdrs() });
      if (res.ok) {
        const d = await res.json();
        setMpEndpoints(d.endpoints || []);
        setEndpointsModal(channelId);
      }
    } catch { toast.error("Failed to fetch endpoints"); }
  };

  const createOriginEndpoint = async () => {
    if (!epChannelId.trim() || !epId.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-livestream/mediapackage/endpoints`, {
        method: "POST", headers: hdrs(),
        body: JSON.stringify({ channel_id: epChannelId, endpoint_id: epId, packaging_format: epFormat }),
      });
      const d = await res.json();
      if (res.ok) {
        toast.success(`Endpoint "${epId}" created`);
        setEpId("");
        if (endpointsModal) viewEndpoints(endpointsModal);
      } else {
        toast.error(d.detail || "Failed to create endpoint");
      }
    } catch { toast.error("Network error"); }
    setLoading(false);
  };

  const deleteEndpoint = async (id) => {
    setDeleting(true);
    try {
      const res = await fetch(`${API}/api/aws-livestream/mediapackage/endpoints/${encodeURIComponent(id)}`, {
        method: "DELETE", headers: hdrs(),
      });
      if (res.ok) {
        toast.success("Endpoint deleted");
        if (endpointsModal) viewEndpoints(endpointsModal);
      } else {
        toast.error("Delete failed");
      }
    } catch { toast.error("Network error"); }
    setDeleting(false);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-livestream-page">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight">AWS Live Streaming</h1>
          <p className="text-sm text-zinc-500 mt-1">Manage live streaming channels with IVS and package content for distribution with MediaPackage</p>
        </div>

        {/* Service Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <ServiceStatus
            title="Interactive Video Service"
            data={status?.ivs}
            icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>}
          />
          <ServiceStatus
            title="MediaPackage"
            data={status?.mediapackage}
            icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>}
          />
        </div>

        {/* Tabs */}
        <Tabs value={tab} onValueChange={setTab} className="space-y-6">
          <TabsList className="bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="ivs" className="data-[state=active]:bg-blue-600/20 data-[state=active]:text-blue-400" data-testid="tab-ivs">
              IVS Channels
            </TabsTrigger>
            <TabsTrigger value="mediapackage" className="data-[state=active]:bg-violet-600/20 data-[state=active]:text-violet-400" data-testid="tab-mediapackage">
              MediaPackage
            </TabsTrigger>
          </TabsList>

          {/* ---- IVS Tab ---- */}
          <TabsContent value="ivs" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Create Form */}
              <div className="lg:col-span-1">
                <Card className="border-zinc-800 bg-zinc-900/60" data-testid="ivs-create-form">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base text-zinc-100">New IVS Channel</CardTitle>
                    <CardDescription className="text-zinc-500 text-xs">Create a low-latency live streaming channel</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="block text-xs text-zinc-400 mb-1.5">Channel Name</label>
                      <input
                        data-testid="ivs-name-input"
                        type="text"
                        value={ivsName}
                        onChange={(e) => setIvsName(e.target.value)}
                        placeholder="my-live-channel"
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:border-blue-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-zinc-400 mb-1.5">Channel Type</label>
                      <select
                        data-testid="ivs-type-select"
                        value={ivsType}
                        onChange={(e) => setIvsType(e.target.value)}
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 focus:border-blue-500 focus:outline-none"
                      >
                        <option value="STANDARD">Standard</option>
                        <option value="BASIC">Basic</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-zinc-400 mb-1.5">Latency Mode</label>
                      <select
                        data-testid="ivs-latency-select"
                        value={ivsLatency}
                        onChange={(e) => setIvsLatency(e.target.value)}
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 focus:border-blue-500 focus:outline-none"
                      >
                        <option value="LOW">Low Latency</option>
                        <option value="NORMAL">Normal</option>
                      </select>
                    </div>
                    <Button
                      data-testid="ivs-create-btn"
                      onClick={createIVSChannel}
                      disabled={!ivsName.trim() || loading}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      {loading ? "Creating..." : "Create Channel"}
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* Channel List */}
              <div className="lg:col-span-2">
                <Card className="border-zinc-800 bg-zinc-900/60">
                  <CardHeader className="pb-3 flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-base text-zinc-100">IVS Channels</CardTitle>
                      <CardDescription className="text-zinc-500 text-xs">{ivsChannels.length} channel{ivsChannels.length !== 1 ? "s" : ""}</CardDescription>
                    </div>
                    <Button size="sm" variant="ghost" className="text-zinc-400 h-7" onClick={fetchIVSChannels} data-testid="ivs-refresh-btn">Refresh</Button>
                  </CardHeader>
                  <CardContent className="space-y-3 max-h-[500px] overflow-y-auto">
                    {ivsChannels.length === 0 ? (
                      <p className="text-sm text-zinc-600 text-center py-8">No IVS channels yet. Create one to start live streaming.</p>
                    ) : (
                      ivsChannels.map((ch) => (
                        <IVSChannelCard
                          key={ch.channel_arn}
                          channel={ch}
                          onDelete={deleteIVSChannel}
                          onViewStream={viewStream}
                          deleting={deleting}
                        />
                      ))
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* IVS Info Card */}
            <Card className="border-zinc-800 bg-zinc-900/60">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-zinc-100">Getting Started with IVS</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-800">
                    <div className="text-blue-400 font-bold text-lg mb-1">1</div>
                    <h4 className="text-sm text-zinc-200 font-medium mb-1">Create Channel</h4>
                    <p className="text-xs text-zinc-500">Set up a channel with low-latency or normal mode</p>
                  </div>
                  <div className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-800">
                    <div className="text-blue-400 font-bold text-lg mb-1">2</div>
                    <h4 className="text-sm text-zinc-200 font-medium mb-1">Start Broadcasting</h4>
                    <p className="text-xs text-zinc-500">Use the ingest endpoint and stream key with OBS, Streamlabs, or FFMPEG</p>
                  </div>
                  <div className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-800">
                    <div className="text-blue-400 font-bold text-lg mb-1">3</div>
                    <h4 className="text-sm text-zinc-200 font-medium mb-1">Watch Live</h4>
                    <p className="text-xs text-zinc-500">Share the playback URL with viewers for sub-second latency streaming</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* ---- MediaPackage Tab ---- */}
          <TabsContent value="mediapackage" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Create Channel Form */}
              <div className="lg:col-span-1 space-y-4">
                <Card className="border-zinc-800 bg-zinc-900/60" data-testid="mp-create-channel-form">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base text-zinc-100">New MediaPackage Channel</CardTitle>
                    <CardDescription className="text-zinc-500 text-xs">Create a packaging channel for content origination</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="block text-xs text-zinc-400 mb-1.5">Channel ID</label>
                      <input
                        data-testid="mp-channel-id-input"
                        type="text"
                        value={mpId}
                        onChange={(e) => setMpId(e.target.value)}
                        placeholder="bme-live-channel-01"
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:border-violet-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-zinc-400 mb-1.5">Description</label>
                      <input
                        data-testid="mp-channel-desc-input"
                        type="text"
                        value={mpDesc}
                        onChange={(e) => setMpDesc(e.target.value)}
                        placeholder="Optional description"
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:border-violet-500 focus:outline-none"
                      />
                    </div>
                    <Button
                      data-testid="mp-create-channel-btn"
                      onClick={createMPChannel}
                      disabled={!mpId.trim() || loading}
                      className="w-full bg-violet-600 hover:bg-violet-700 text-white"
                    >
                      {loading ? "Creating..." : "Create Channel"}
                    </Button>
                  </CardContent>
                </Card>

                {/* Create Endpoint Form */}
                <Card className="border-zinc-800 bg-zinc-900/60" data-testid="mp-create-endpoint-form">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base text-zinc-100">New Origin Endpoint</CardTitle>
                    <CardDescription className="text-zinc-500 text-xs">Add a playback endpoint to an existing channel</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="block text-xs text-zinc-400 mb-1.5">Channel ID</label>
                      <select
                        data-testid="ep-channel-select"
                        value={epChannelId}
                        onChange={(e) => setEpChannelId(e.target.value)}
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 focus:border-violet-500 focus:outline-none"
                      >
                        <option value="">Select channel...</option>
                        {mpChannels.map((ch) => (
                          <option key={ch.id} value={ch.id}>{ch.id}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-zinc-400 mb-1.5">Endpoint ID</label>
                      <input
                        data-testid="ep-id-input"
                        type="text"
                        value={epId}
                        onChange={(e) => setEpId(e.target.value)}
                        placeholder="bme-hls-endpoint"
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:border-violet-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-zinc-400 mb-1.5">Packaging Format</label>
                      <select
                        data-testid="ep-format-select"
                        value={epFormat}
                        onChange={(e) => setEpFormat(e.target.value)}
                        className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-200 focus:border-violet-500 focus:outline-none"
                      >
                        {Object.entries(formats).map(([k, v]) => (
                          <option key={k} value={k}>{v.label}</option>
                        ))}
                      </select>
                    </div>
                    <Button
                      data-testid="ep-create-btn"
                      onClick={createOriginEndpoint}
                      disabled={!epChannelId || !epId.trim() || loading}
                      className="w-full bg-violet-600 hover:bg-violet-700 text-white"
                    >
                      {loading ? "Creating..." : "Create Endpoint"}
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* Channel List */}
              <div className="lg:col-span-2">
                <Card className="border-zinc-800 bg-zinc-900/60">
                  <CardHeader className="pb-3 flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-base text-zinc-100">MediaPackage Channels</CardTitle>
                      <CardDescription className="text-zinc-500 text-xs">{mpChannels.length} channel{mpChannels.length !== 1 ? "s" : ""}</CardDescription>
                    </div>
                    <Button size="sm" variant="ghost" className="text-zinc-400 h-7" onClick={fetchMPChannels} data-testid="mp-refresh-btn">Refresh</Button>
                  </CardHeader>
                  <CardContent className="space-y-3 max-h-[500px] overflow-y-auto">
                    {mpChannels.length === 0 ? (
                      <p className="text-sm text-zinc-600 text-center py-8">No MediaPackage channels yet. Create one to start packaging content.</p>
                    ) : (
                      mpChannels.map((ch) => (
                        <MPChannelCard
                          key={ch.id}
                          channel={ch}
                          onDelete={deleteMPChannel}
                          onViewEndpoints={viewEndpoints}
                          deleting={deleting}
                        />
                      ))
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Packaging Formats Reference */}
            <Card className="border-zinc-800 bg-zinc-900/60">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-zinc-100">Packaging Formats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {Object.entries(formats).map(([k, v]) => (
                    <div key={k} className="bg-zinc-800/50 rounded-lg p-3 border border-zinc-800">
                      <p className="text-sm text-zinc-200 font-medium">{v.label}</p>
                      <p className="text-[10px] text-zinc-500 mt-1">{v.description}</p>
                      <Badge variant="outline" className="text-[10px] bg-zinc-700/30 text-zinc-400 border-zinc-700 mt-2">{k.toUpperCase()}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Modals */}
      {streamModal && <StreamStatusModal data={streamModal} onClose={() => setStreamModal(null)} onStop={stopStream} />}
      {endpointsModal && <EndpointsModal channelId={endpointsModal} endpoints={mpEndpoints} onClose={() => setEndpointsModal(null)} onDeleteEndpoint={deleteEndpoint} deleting={deleting} />}
    </div>
  );
}
