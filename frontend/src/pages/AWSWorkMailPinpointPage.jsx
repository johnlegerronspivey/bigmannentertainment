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
    Active: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    ENABLED: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    ACTIVE: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    Connected: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    COMPLETED: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    DISABLED: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
    PENDING: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    Unavailable: "bg-rose-500/15 text-rose-400 border-rose-500/30",
  };
  return map[s] || "bg-zinc-500/15 text-zinc-400 border-zinc-500/30";
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
          {data?.total_users !== undefined && <p>Your users: <span className="text-zinc-300">{data.total_users}</span></p>}
          {data?.total_apps !== undefined && <p>Your apps: <span className="text-zinc-300">{data.total_apps}</span></p>}
          {data?.organizations_found !== undefined && <p>Organizations: <span className="text-zinc-300">{data.organizations_found}</span></p>}
          {data?.applications_found !== undefined && <p>Applications: <span className="text-zinc-300">{data.applications_found}</span></p>}
        </div>
      </CardContent>
    </Card>
  );
};

/* ---- WorkMail Org Card ---- */
const OrgCard = ({ org, onSelect, selected }) => (
  <div
    className={`p-4 rounded-lg border transition-colors cursor-pointer ${selected ? "bg-indigo-500/10 border-indigo-500/40" : "bg-zinc-800/40 border-zinc-800 hover:border-zinc-700"}`}
    onClick={() => onSelect(org.organization_id)}
    data-testid={`workmail-org-${org.organization_id}`}
  >
    <div className="flex items-center justify-between mb-2">
      <h4 className="text-sm font-semibold text-zinc-100">{org.alias || org.organization_id}</h4>
      <Badge variant="outline" className={`text-[10px] ${statusColor(org.state)}`}>{org.state}</Badge>
    </div>
    {org.default_mail_domain && <p className="text-[10px] text-zinc-500">Domain: <span className="text-zinc-400">{org.default_mail_domain}</span></p>}
    <p className="text-[10px] text-zinc-500 mt-1">ID: <span className="text-zinc-400 font-mono">{org.organization_id}</span></p>
  </div>
);

/* ---- WorkMail User Card ---- */
const UserCard = ({ user, onDelete, deleting }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`workmail-user-${user.entity_id}`}>
    <div className="flex items-center justify-between mb-1">
      <h4 className="text-sm font-semibold text-zinc-100">{user.name}</h4>
      <Badge variant="outline" className={`text-[10px] ${statusColor(user.state)}`}>{user.state}</Badge>
    </div>
    {user.email && <p className="text-[10px] text-zinc-500">Email: <span className="text-zinc-400">{user.email}</span></p>}
    <p className="text-[10px] text-zinc-500">Role: <span className="text-zinc-400">{user.user_role}</span></p>
    <div className="flex justify-end mt-2">
      <Button size="sm" variant="ghost" className="text-rose-400 hover:text-rose-300 h-6 px-2 text-xs" onClick={() => onDelete(user.entity_id)} disabled={deleting} data-testid={`workmail-delete-user-${user.entity_id}`}>
        Delete
      </Button>
    </div>
  </div>
);

/* ---- Pinpoint App Card ---- */
const AppCard = ({ app, onSelect, selected, onDelete, deleting }) => (
  <div
    className={`p-4 rounded-lg border transition-colors cursor-pointer ${selected ? "bg-orange-500/10 border-orange-500/40" : "bg-zinc-800/40 border-zinc-800 hover:border-zinc-700"}`}
    onClick={() => onSelect(app.application_id)}
    data-testid={`pinpoint-app-${app.application_id}`}
  >
    <div className="flex items-center justify-between mb-2">
      <h4 className="text-sm font-semibold text-zinc-100">{app.name}</h4>
      <Button size="sm" variant="ghost" className="text-rose-400 hover:text-rose-300 h-6 px-2 text-xs" onClick={(e) => { e.stopPropagation(); onDelete(app.application_id); }} disabled={deleting} data-testid={`pinpoint-delete-app-${app.application_id}`}>
        Delete
      </Button>
    </div>
    <p className="text-[10px] text-zinc-500 font-mono truncate">ID: {app.application_id}</p>
  </div>
);

/* ---- Campaign Card ---- */
const CampaignCard = ({ campaign, onDelete, deleting }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`pinpoint-campaign-${campaign.campaign_id}`}>
    <div className="flex items-center justify-between mb-1">
      <h4 className="text-sm font-semibold text-zinc-100">{campaign.name}</h4>
      <Badge variant="outline" className={`text-[10px] ${statusColor(campaign.state)}`}>{campaign.state || "DRAFT"}</Badge>
    </div>
    {campaign.description && <p className="text-[10px] text-zinc-500 mb-1">{campaign.description}</p>}
    <p className="text-[10px] text-zinc-500">Segment: <span className="text-zinc-400 font-mono">{campaign.segment_id}</span></p>
    <div className="flex justify-end mt-2">
      <Button size="sm" variant="ghost" className="text-rose-400 hover:text-rose-300 h-6 px-2 text-xs" onClick={() => onDelete(campaign.campaign_id)} disabled={deleting} data-testid={`pinpoint-delete-campaign-${campaign.campaign_id}`}>
        Delete
      </Button>
    </div>
  </div>
);

/* ---- Segment Card ---- */
const SegmentCard = ({ segment, onDelete, deleting }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`pinpoint-segment-${segment.segment_id}`}>
    <div className="flex items-center justify-between mb-1">
      <h4 className="text-sm font-semibold text-zinc-100">{segment.name}</h4>
      <Badge variant="outline" className="text-[10px] bg-blue-500/15 text-blue-400 border-blue-500/30">{segment.segment_type || "DIMENSIONAL"}</Badge>
    </div>
    <p className="text-[10px] text-zinc-500">ID: <span className="text-zinc-400 font-mono">{segment.segment_id}</span></p>
    <div className="flex justify-end mt-2">
      <Button size="sm" variant="ghost" className="text-rose-400 hover:text-rose-300 h-6 px-2 text-xs" onClick={() => onDelete(segment.segment_id)} disabled={deleting} data-testid={`pinpoint-delete-segment-${segment.segment_id}`}>
        Delete
      </Button>
    </div>
  </div>
);

/* ================================================================
   MAIN PAGE
   ================================================================ */
export default function AWSWorkMailPinpointPage() {
  useAuth(); // Ensure user is authenticated
  const token = localStorage.getItem('token');
  
  // Create headers with current token
  const getHeaders = () => ({ Authorization: `Bearer ${token}`, "Content-Type": "application/json" });

  // Status
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  // WorkMail
  const [orgs, setOrgs] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [wmUsers, setWmUsers] = useState([]);
  const [wmGroups, setWmGroups] = useState([]);
  const [wmLoading, setWmLoading] = useState(false);
  const [createUserForm, setCreateUserForm] = useState({ name: "", display_name: "", password: "" });
  const [creatingUser, setCreatingUser] = useState(false);

  // Pinpoint
  const [ppApps, setPpApps] = useState([]);
  const [selectedApp, setSelectedApp] = useState(null);
  const [segments, setSegments] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [ppLoading, setPpLoading] = useState(false);
  const [createAppName, setCreateAppName] = useState("");
  const [creatingApp, setCreatingApp] = useState(false);
  const [createSegName, setCreateSegName] = useState("");
  const [creatingSeg, setCreatingSeg] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // ── Fetchers ────────────────────────────────────────────
  const fetchStatus = useCallback(async () => {
    const currentToken = localStorage.getItem('token');
    if (!currentToken) return;
    try {
      const r = await fetch(`${API}/api/aws-comms/status`, { headers: getHeaders() });
      if (r.ok) setStatus(await r.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  const fetchOrgs = useCallback(async () => {
    setWmLoading(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/workmail/organizations`, { headers: getHeaders() });
      if (r.ok) { const d = await r.json(); setOrgs(d.organizations || []); }
    } catch (e) { console.error(e); }
    setWmLoading(false);
  }, []);

  const fetchOrgDetails = useCallback(async (orgId) => {
    setWmLoading(true);
    try {
      const [usersR, groupsR] = await Promise.all([
        fetch(`${API}/api/aws-comms/workmail/users?organization_id=${orgId}`, { headers: getHeaders() }),
        fetch(`${API}/api/aws-comms/workmail/groups?organization_id=${orgId}`, { headers: getHeaders() }),
      ]);
      if (usersR.ok) { const d = await usersR.json(); setWmUsers(d.users || []); }
      if (groupsR.ok) { const d = await groupsR.json(); setWmGroups(d.groups || []); }
    } catch (e) { console.error(e); }
    setWmLoading(false);
  }, []);

  const [segmentsDeprecated, setSegmentsDeprecated] = useState(false);
  const [campaignsDeprecated, setCampaignsDeprecated] = useState(false);

  const fetchPpApps = useCallback(async () => {
    setPpLoading(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/pinpoint/applications`, { headers: getHeaders() });
      if (r.ok) { const d = await r.json(); setPpApps(d.applications || []); }
    } catch (e) { console.error(e); }
    setPpLoading(false);
  }, []);

  const fetchAppDetails = useCallback(async (appId) => {
    setPpLoading(true);
    try {
      const [segR, campR] = await Promise.all([
        fetch(`${API}/api/aws-comms/pinpoint/segments/${appId}`, { headers: getHeaders() }),
        fetch(`${API}/api/aws-comms/pinpoint/campaigns/${appId}`, { headers: getHeaders() }),
      ]);
      if (segR.ok) {
        const d = await segR.json();
        setSegments(d.segments || []);
        setSegmentsDeprecated(!!d.deprecated);
      }
      if (campR.ok) {
        const d = await campR.json();
        setCampaigns(d.campaigns || []);
        setCampaignsDeprecated(!!d.deprecated);
      }
    } catch (e) { console.error(e); }
    setPpLoading(false);
  }, []);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  // When selecting an org
  useEffect(() => {
    if (selectedOrg) fetchOrgDetails(selectedOrg);
  }, [selectedOrg, fetchOrgDetails]);

  // When selecting an app
  useEffect(() => {
    if (selectedApp) fetchAppDetails(selectedApp);
  }, [selectedApp, fetchAppDetails]);

  // ── Actions ────────────────────────────────────────────
  const handleCreateUser = async () => {
    if (!selectedOrg || !createUserForm.name) return;
    setCreatingUser(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/workmail/users`, {
        method: "POST", headers: getHeaders(),
        body: JSON.stringify({ organization_id: selectedOrg, ...createUserForm }),
      });
      if (r.ok) {
        toast.success("User created");
        setCreateUserForm({ name: "", display_name: "", password: "" });
        fetchOrgDetails(selectedOrg);
      } else {
        const e = await r.json();
        toast.error(e.detail || "Failed to create user");
      }
    } catch { toast.error("Network error"); }
    setCreatingUser(false);
  };

  const handleDeleteUser = async (orgId, userId) => {
    setDeleting(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/workmail/users/${orgId}/${userId}`, { method: "DELETE", headers: getHeaders() });
      if (r.ok) { toast.success("User deleted"); fetchOrgDetails(orgId); }
      else toast.error("Failed to delete user");
    } catch { toast.error("Network error"); }
    setDeleting(false);
  };

  const handleCreateApp = async () => {
    if (!createAppName.trim()) return;
    setCreatingApp(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/pinpoint/applications`, {
        method: "POST", headers: getHeaders(),
        body: JSON.stringify({ name: createAppName }),
      });
      if (r.ok) {
        toast.success("Application created");
        setCreateAppName("");
        fetchPpApps();
      } else {
        const e = await r.json();
        toast.error(e.detail || "Failed to create app");
      }
    } catch { toast.error("Network error"); }
    setCreatingApp(false);
  };

  const handleDeleteApp = async (appId) => {
    setDeleting(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/pinpoint/applications/${appId}`, { method: "DELETE", headers: getHeaders() });
      if (r.ok) {
        toast.success("Application deleted");
        if (selectedApp === appId) { setSelectedApp(null); setSegments([]); setCampaigns([]); }
        fetchPpApps();
      } else toast.error("Failed to delete application");
    } catch { toast.error("Network error"); }
    setDeleting(false);
  };

  const handleCreateSegment = async () => {
    if (!selectedApp || !createSegName.trim()) return;
    setCreatingSeg(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/pinpoint/segments`, {
        method: "POST", headers: getHeaders(),
        body: JSON.stringify({ application_id: selectedApp, name: createSegName }),
      });
      if (r.ok) {
        toast.success("Segment created");
        setCreateSegName("");
        fetchAppDetails(selectedApp);
      } else {
        const e = await r.json();
        toast.error(e.detail || "Failed to create segment");
      }
    } catch { toast.error("Network error"); }
    setCreatingSeg(false);
  };

  const handleDeleteSegment = async (segId) => {
    if (!selectedApp) return;
    setDeleting(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/pinpoint/segments/${selectedApp}/${segId}`, { method: "DELETE", headers: getHeaders() });
      if (r.ok) { toast.success("Segment deleted"); fetchAppDetails(selectedApp); }
      else toast.error("Failed to delete segment");
    } catch { toast.error("Network error"); }
    setDeleting(false);
  };

  const handleDeleteCampaign = async (campId) => {
    if (!selectedApp) return;
    setDeleting(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/pinpoint/campaigns/${selectedApp}/${campId}`, { method: "DELETE", headers: getHeaders() });
      if (r.ok) { toast.success("Campaign deleted"); fetchAppDetails(selectedApp); }
      else toast.error("Failed to delete campaign");
    } catch { toast.error("Network error"); }
    setDeleting(false);
  };

  // ── Render ────────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center" data-testid="comms-loading">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-comms-page">
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-zinc-50 tracking-tight" data-testid="comms-page-title">
            AWS Communications
          </h1>
          <p className="text-sm text-zinc-500 mt-1">WorkMail business email & Pinpoint marketing campaigns</p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8" data-testid="comms-status-cards">
          <ServiceStatus
            title="WorkMail"
            data={status?.workmail}
            icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>}
          />
          <ServiceStatus
            title="Pinpoint"
            data={status?.pinpoint}
            icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>}
          />
        </div>

        {/* Tabs */}
        <Tabs defaultValue="workmail" className="space-y-6" data-testid="comms-tabs">
          <TabsList className="bg-zinc-900 border border-zinc-800 p-1">
            <TabsTrigger value="workmail" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white text-xs px-4" data-testid="tab-workmail" onClick={fetchOrgs}>
              WorkMail
            </TabsTrigger>
            <TabsTrigger value="pinpoint" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white text-xs px-4" data-testid="tab-pinpoint" onClick={fetchPpApps}>
              Pinpoint
            </TabsTrigger>
          </TabsList>

          {/* ══════════════ WORKMAIL TAB ══════════════ */}
          <TabsContent value="workmail" className="space-y-6" data-testid="workmail-tab-content">
            {/* Organizations */}
            <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-zinc-100">Organizations</CardTitle>
                <CardDescription className="text-zinc-500 text-xs">Select an organization to manage users and groups</CardDescription>
              </CardHeader>
              <CardContent>
                {wmLoading && !orgs.length ? (
                  <div className="flex justify-center py-6"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500" /></div>
                ) : orgs.length === 0 ? (
                  <p className="text-sm text-zinc-500 text-center py-6" data-testid="no-orgs">No WorkMail organizations found. Create one in the AWS Console.</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="workmail-orgs-list">
                    {orgs.map((o) => <OrgCard key={o.organization_id} org={o} onSelect={setSelectedOrg} selected={selectedOrg === o.organization_id} />)}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Users & Groups (shown when org selected) */}
            {selectedOrg && (
              <>
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">Users</CardTitle>
                        <CardDescription className="text-zinc-500 text-xs">Manage WorkMail users in this organization</CardDescription>
                      </div>
                      <Badge variant="outline" className="text-xs bg-indigo-500/10 text-indigo-400 border-indigo-500/30">{wmUsers.length} users</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Create User Form */}
                    <div className="p-4 bg-zinc-800/30 rounded-lg border border-zinc-800 space-y-3" data-testid="create-user-form">
                      <p className="text-xs font-medium text-zinc-300">Create New User</p>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <input
                          className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none"
                          placeholder="Username"
                          value={createUserForm.name}
                          onChange={(e) => setCreateUserForm((p) => ({ ...p, name: e.target.value }))}
                          data-testid="create-user-name"
                        />
                        <input
                          className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none"
                          placeholder="Display Name"
                          value={createUserForm.display_name}
                          onChange={(e) => setCreateUserForm((p) => ({ ...p, display_name: e.target.value }))}
                          data-testid="create-user-display-name"
                        />
                        <input
                          className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none"
                          placeholder="Password"
                          type="password"
                          value={createUserForm.password}
                          onChange={(e) => setCreateUserForm((p) => ({ ...p, password: e.target.value }))}
                          data-testid="create-user-password"
                        />
                      </div>
                      <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-xs h-8" onClick={handleCreateUser} disabled={creatingUser || !createUserForm.name} data-testid="create-user-submit">
                        {creatingUser ? "Creating..." : "Create User"}
                      </Button>
                    </div>

                    {/* User List */}
                    {wmUsers.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-users">No users in this organization</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="workmail-users-list">
                        {wmUsers.map((u) => <UserCard key={u.entity_id} user={u} onDelete={(uid) => handleDeleteUser(selectedOrg, uid)} deleting={deleting} />)}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Groups */}
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base text-zinc-100">Groups</CardTitle>
                    <CardDescription className="text-zinc-500 text-xs">Distribution groups and mailing lists</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {wmGroups.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-groups">No groups in this organization</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="workmail-groups-list">
                        {wmGroups.map((g) => (
                          <div key={g.entity_id} className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800" data-testid={`workmail-group-${g.entity_id}`}>
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-semibold text-zinc-100">{g.name}</h4>
                              <Badge variant="outline" className={`text-[10px] ${statusColor(g.state)}`}>{g.state}</Badge>
                            </div>
                            {g.email && <p className="text-[10px] text-zinc-500 mt-1">Email: <span className="text-zinc-400">{g.email}</span></p>}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* ══════════════ PINPOINT TAB ══════════════ */}
          <TabsContent value="pinpoint" className="space-y-6" data-testid="pinpoint-tab-content">
            {/* Applications */}
            <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-base text-zinc-100">Applications</CardTitle>
                    <CardDescription className="text-zinc-500 text-xs">Pinpoint projects for campaign management</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Create App */}
                <div className="flex gap-2" data-testid="create-app-form">
                  <input
                    className="flex-1 bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-orange-500 focus:outline-none"
                    placeholder="Application name"
                    value={createAppName}
                    onChange={(e) => setCreateAppName(e.target.value)}
                    data-testid="create-app-name"
                  />
                  <Button size="sm" className="bg-orange-600 hover:bg-orange-700 text-xs h-8" onClick={handleCreateApp} disabled={creatingApp || !createAppName.trim()} data-testid="create-app-submit">
                    {creatingApp ? "Creating..." : "Create App"}
                  </Button>
                </div>

                {ppLoading && !ppApps.length ? (
                  <div className="flex justify-center py-6"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500" /></div>
                ) : ppApps.length === 0 ? (
                  <p className="text-sm text-zinc-500 text-center py-6" data-testid="no-apps">No Pinpoint applications found</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="pinpoint-apps-list">
                    {ppApps.map((a) => <AppCard key={a.application_id} app={a} onSelect={setSelectedApp} selected={selectedApp === a.application_id} onDelete={handleDeleteApp} deleting={deleting} />)}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Segments & Campaigns (shown when app selected) */}
            {selectedApp && (
              <>
                {/* Segments */}
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">Audience Segments</CardTitle>
                        <CardDescription className="text-zinc-500 text-xs">Target audience groups for campaigns</CardDescription>
                      </div>
                      {segmentsDeprecated ? (
                        <Badge variant="outline" className="text-xs bg-amber-500/10 text-amber-400 border-amber-500/30">Deprecated</Badge>
                      ) : (
                        <Badge variant="outline" className="text-xs bg-blue-500/10 text-blue-400 border-blue-500/30">{segments.length} segments</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {segmentsDeprecated && (
                      <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg" data-testid="segments-deprecated-notice">
                        <p className="text-xs text-amber-400">AWS is deprecating Pinpoint engagement features (segments, campaigns). Consider migrating to Amazon Connect.</p>
                      </div>
                    )}
                    {!segmentsDeprecated && (
                      <div className="flex gap-2" data-testid="create-segment-form">
                        <input
                          className="flex-1 bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-blue-500 focus:outline-none"
                          placeholder="Segment name"
                          value={createSegName}
                          onChange={(e) => setCreateSegName(e.target.value)}
                          data-testid="create-segment-name"
                        />
                        <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-xs h-8" onClick={handleCreateSegment} disabled={creatingSeg || !createSegName.trim()} data-testid="create-segment-submit">
                          {creatingSeg ? "Creating..." : "Create Segment"}
                        </Button>
                      </div>
                    )}
                    {segments.length === 0 && !segmentsDeprecated ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-segments">No segments yet</p>
                    ) : segments.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="pinpoint-segments-list">
                        {segments.map((s) => <SegmentCard key={s.segment_id} segment={s} onDelete={handleDeleteSegment} deleting={deleting} />)}
                      </div>
                    ) : null}
                  </CardContent>
                </Card>

                {/* Campaigns */}
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">Campaigns</CardTitle>
                        <CardDescription className="text-zinc-500 text-xs">Marketing campaigns targeting your segments</CardDescription>
                      </div>
                      {campaignsDeprecated ? (
                        <Badge variant="outline" className="text-xs bg-amber-500/10 text-amber-400 border-amber-500/30">Deprecated</Badge>
                      ) : (
                        <Badge variant="outline" className="text-xs bg-orange-500/10 text-orange-400 border-orange-500/30">{campaigns.length} campaigns</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    {campaignsDeprecated && (
                      <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg" data-testid="campaigns-deprecated-notice">
                        <p className="text-xs text-amber-400">AWS is deprecating Pinpoint engagement features (segments, campaigns). Consider migrating to Amazon Connect.</p>
                      </div>
                    )}
                    {campaigns.length === 0 && !campaignsDeprecated ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-campaigns">No campaigns yet. Create a segment first, then build a campaign.</p>
                    ) : campaigns.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="pinpoint-campaigns-list">
                        {campaigns.map((c) => <CampaignCard key={c.campaign_id} campaign={c} onDelete={handleDeleteCampaign} deleting={deleting} />)}
                      </div>
                    ) : null}
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
