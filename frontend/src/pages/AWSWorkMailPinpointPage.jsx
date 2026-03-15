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
    CREATION_IN_PROGRESS: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    DISABLED: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
    PENDING: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    Unavailable: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    PUBLISHED: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
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
          {data?.instances_found !== undefined && <p>Instances: <span className="text-zinc-300">{data.instances_found}</span></p>}
          {data?.organizations_found !== undefined && <p>Organizations: <span className="text-zinc-300">{data.organizations_found}</span></p>}
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

/* ---- Connect Instance Card ---- */
const InstanceCard = ({ instance, onSelect, selected }) => (
  <div
    className={`p-4 rounded-lg border transition-colors cursor-pointer ${selected ? "bg-teal-500/10 border-teal-500/40" : "bg-zinc-800/40 border-zinc-800 hover:border-zinc-700"}`}
    onClick={() => onSelect(instance.instance_id)}
    data-testid={`connect-instance-${instance.instance_id}`}
  >
    <div className="flex items-center justify-between mb-2">
      <h4 className="text-sm font-semibold text-zinc-100">{instance.instance_alias || instance.instance_id}</h4>
      <Badge variant="outline" className={`text-[10px] ${statusColor(instance.instance_status)}`}>{instance.instance_status}</Badge>
    </div>
    <div className="space-y-0.5">
      <p className="text-[10px] text-zinc-500">Identity: <span className="text-zinc-400">{instance.identity_management_type}</span></p>
      <p className="text-[10px] text-zinc-500">
        Inbound: <span className={instance.inbound_calls_enabled ? "text-emerald-400" : "text-rose-400"}>{instance.inbound_calls_enabled ? "Yes" : "No"}</span>
        {" / "}
        Outbound: <span className={instance.outbound_calls_enabled ? "text-emerald-400" : "text-rose-400"}>{instance.outbound_calls_enabled ? "Yes" : "No"}</span>
      </p>
      <p className="text-[10px] text-zinc-500 font-mono truncate">ID: {instance.instance_id}</p>
    </div>
  </div>
);

/* ---- Queue Card ---- */
const QueueCard = ({ queue }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`connect-queue-${queue.queue_id}`}>
    <div className="flex items-center justify-between mb-1">
      <h4 className="text-sm font-semibold text-zinc-100">{queue.name}</h4>
      <Badge variant="outline" className="text-[10px] bg-teal-500/15 text-teal-400 border-teal-500/30">{queue.queue_type || "STANDARD"}</Badge>
    </div>
    <p className="text-[10px] text-zinc-500 font-mono truncate">ID: {queue.queue_id}</p>
  </div>
);

/* ---- Contact Flow Card ---- */
const FlowCard = ({ flow }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`connect-flow-${flow.flow_id}`}>
    <div className="flex items-center justify-between mb-1">
      <h4 className="text-sm font-semibold text-zinc-100">{flow.name}</h4>
      <Badge variant="outline" className={`text-[10px] ${statusColor(flow.contact_flow_state || flow.contact_flow_status)}`}>
        {flow.contact_flow_state || flow.contact_flow_status || "ACTIVE"}
      </Badge>
    </div>
    <p className="text-[10px] text-zinc-500">Type: <span className="text-zinc-400">{flow.contact_flow_type}</span></p>
  </div>
);

/* ---- Hours Card ---- */
const HoursCard = ({ hours }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`connect-hours-${hours.hours_id}`}>
    <h4 className="text-sm font-semibold text-zinc-100 mb-1">{hours.name}</h4>
    <p className="text-[10px] text-zinc-500 font-mono truncate">ID: {hours.hours_id}</p>
  </div>
);

/* ---- Connect User Card ---- */
const ConnectUserCard = ({ user }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`connect-user-${user.user_id}`}>
    <h4 className="text-sm font-semibold text-zinc-100 mb-1">{user.username}</h4>
    <p className="text-[10px] text-zinc-500 font-mono truncate">ID: {user.user_id}</p>
  </div>
);

/* ---- Routing Profile Card ---- */
const RoutingProfileCard = ({ profile }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`connect-profile-${profile.routing_profile_id}`}>
    <h4 className="text-sm font-semibold text-zinc-100 mb-1">{profile.name}</h4>
    <p className="text-[10px] text-zinc-500 font-mono truncate">ID: {profile.routing_profile_id}</p>
  </div>
);

/* ================================================================
   MAIN PAGE
   ================================================================ */
export default function AWSWorkMailConnectPage() {
  useAuth();
  const token = localStorage.getItem("token");
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

  // Connect
  const [instances, setInstances] = useState([]);
  const [selectedInstance, setSelectedInstance] = useState(null);
  const [queues, setQueues] = useState([]);
  const [flows, setFlows] = useState([]);
  const [hours, setHours] = useState([]);
  const [connectUsers, setConnectUsers] = useState([]);
  const [routingProfiles, setRoutingProfiles] = useState([]);
  const [cnLoading, setCnLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // ── Fetchers ────────────────────────────────────────────
  const fetchStatus = useCallback(async () => {
    const currentToken = localStorage.getItem("token");
    if (!currentToken) return;
    try {
      const r = await fetch(`${API}/api/aws-comms/status`, { headers: { Authorization: `Bearer ${currentToken}`, "Content-Type": "application/json" } });
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

  const fetchInstances = useCallback(async () => {
    setCnLoading(true);
    try {
      const r = await fetch(`${API}/api/aws-comms/connect/instances`, { headers: getHeaders() });
      if (r.ok) { const d = await r.json(); setInstances(d.instances || []); }
    } catch (e) { console.error(e); }
    setCnLoading(false);
  }, []);

  const fetchInstanceDetails = useCallback(async (instId) => {
    setCnLoading(true);
    try {
      const [qR, fR, hR, uR, rpR] = await Promise.all([
        fetch(`${API}/api/aws-comms/connect/queues?instance_id=${instId}`, { headers: getHeaders() }),
        fetch(`${API}/api/aws-comms/connect/contact-flows?instance_id=${instId}`, { headers: getHeaders() }),
        fetch(`${API}/api/aws-comms/connect/hours-of-operation?instance_id=${instId}`, { headers: getHeaders() }),
        fetch(`${API}/api/aws-comms/connect/users?instance_id=${instId}`, { headers: getHeaders() }),
        fetch(`${API}/api/aws-comms/connect/routing-profiles?instance_id=${instId}`, { headers: getHeaders() }),
      ]);
      if (qR.ok) { const d = await qR.json(); setQueues(d.queues || []); }
      if (fR.ok) { const d = await fR.json(); setFlows(d.contact_flows || []); }
      if (hR.ok) { const d = await hR.json(); setHours(d.hours_of_operation || []); }
      if (uR.ok) { const d = await uR.json(); setConnectUsers(d.users || []); }
      if (rpR.ok) { const d = await rpR.json(); setRoutingProfiles(d.routing_profiles || []); }
    } catch (e) { console.error(e); }
    setCnLoading(false);
  }, []);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  useEffect(() => {
    if (selectedOrg) fetchOrgDetails(selectedOrg);
  }, [selectedOrg, fetchOrgDetails]);

  useEffect(() => {
    if (selectedInstance) fetchInstanceDetails(selectedInstance);
  }, [selectedInstance, fetchInstanceDetails]);

  // ── WorkMail Actions ──────────────────────────────────
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
          <p className="text-sm text-zinc-500 mt-1">WorkMail business email & Amazon Connect contact center</p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8" data-testid="comms-status-cards">
          <ServiceStatus
            title="WorkMail"
            data={status?.workmail}
            icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>}
          />
          <ServiceStatus
            title="Amazon Connect"
            data={status?.connect}
            icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>}
          />
        </div>

        {/* Tabs */}
        <Tabs defaultValue="workmail" className="space-y-6" data-testid="comms-tabs">
          <TabsList className="bg-zinc-900 border border-zinc-800 p-1">
            <TabsTrigger value="workmail" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white text-xs px-4" data-testid="tab-workmail" onClick={fetchOrgs}>
              WorkMail
            </TabsTrigger>
            <TabsTrigger value="connect" className="data-[state=active]:bg-teal-600 data-[state=active]:text-white text-xs px-4" data-testid="tab-connect" onClick={fetchInstances}>
              Amazon Connect
            </TabsTrigger>
          </TabsList>

          {/* ══════════════ WORKMAIL TAB ══════════════ */}
          <TabsContent value="workmail" className="space-y-6" data-testid="workmail-tab-content">
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
                    <div className="p-4 bg-zinc-800/30 rounded-lg border border-zinc-800 space-y-3" data-testid="create-user-form">
                      <p className="text-xs font-medium text-zinc-300">Create New User</p>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <input className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none" placeholder="Username" value={createUserForm.name} onChange={(e) => setCreateUserForm((p) => ({ ...p, name: e.target.value }))} data-testid="create-user-name" />
                        <input className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none" placeholder="Display Name" value={createUserForm.display_name} onChange={(e) => setCreateUserForm((p) => ({ ...p, display_name: e.target.value }))} data-testid="create-user-display-name" />
                        <input className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none" placeholder="Password" type="password" value={createUserForm.password} onChange={(e) => setCreateUserForm((p) => ({ ...p, password: e.target.value }))} data-testid="create-user-password" />
                      </div>
                      <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-xs h-8" onClick={handleCreateUser} disabled={creatingUser || !createUserForm.name} data-testid="create-user-submit">
                        {creatingUser ? "Creating..." : "Create User"}
                      </Button>
                    </div>
                    {wmUsers.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-users">No users in this organization</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="workmail-users-list">
                        {wmUsers.map((u) => <UserCard key={u.entity_id} user={u} onDelete={(uid) => handleDeleteUser(selectedOrg, uid)} deleting={deleting} />)}
                      </div>
                    )}
                  </CardContent>
                </Card>

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

          {/* ══════════════ AMAZON CONNECT TAB ══════════════ */}
          <TabsContent value="connect" className="space-y-6" data-testid="connect-tab-content">
            {/* Instances */}
            <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-zinc-100">Connect Instances</CardTitle>
                <CardDescription className="text-zinc-500 text-xs">Select an instance to view queues, flows, hours, users & routing profiles</CardDescription>
              </CardHeader>
              <CardContent>
                {cnLoading && !instances.length ? (
                  <div className="flex justify-center py-6"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-teal-500" /></div>
                ) : instances.length === 0 ? (
                  <p className="text-sm text-zinc-500 text-center py-6" data-testid="no-instances">No Amazon Connect instances found. Create one in the AWS Console.</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="connect-instances-list">
                    {instances.map((inst) => <InstanceCard key={inst.instance_id} instance={inst} onSelect={setSelectedInstance} selected={selectedInstance === inst.instance_id} />)}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Instance Detail Sections */}
            {selectedInstance && (
              <>
                {/* Queues */}
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">Queues</CardTitle>
                        <CardDescription className="text-zinc-500 text-xs">Contact queues for routing incoming contacts</CardDescription>
                      </div>
                      <Badge variant="outline" className="text-xs bg-teal-500/10 text-teal-400 border-teal-500/30">{queues.length} queues</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {queues.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-queues">No queues found</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="connect-queues-list">
                        {queues.map((q) => <QueueCard key={q.queue_id} queue={q} />)}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Contact Flows */}
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">Contact Flows</CardTitle>
                        <CardDescription className="text-zinc-500 text-xs">IVR and routing flows for contact handling</CardDescription>
                      </div>
                      <Badge variant="outline" className="text-xs bg-cyan-500/10 text-cyan-400 border-cyan-500/30">{flows.length} flows</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {flows.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-flows">No contact flows found</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="connect-flows-list">
                        {flows.map((f) => <FlowCard key={f.flow_id} flow={f} />)}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Hours of Operation */}
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">Hours of Operation</CardTitle>
                        <CardDescription className="text-zinc-500 text-xs">Business hours schedules for queues</CardDescription>
                      </div>
                      <Badge variant="outline" className="text-xs bg-amber-500/10 text-amber-400 border-amber-500/30">{hours.length} schedules</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {hours.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-hours">No hours of operation found</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="connect-hours-list">
                        {hours.map((h) => <HoursCard key={h.hours_id} hours={h} />)}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Connect Users */}
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">Connect Users</CardTitle>
                        <CardDescription className="text-zinc-500 text-xs">Agents and supervisors in this instance</CardDescription>
                      </div>
                      <Badge variant="outline" className="text-xs bg-violet-500/10 text-violet-400 border-violet-500/30">{connectUsers.length} users</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {connectUsers.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-connect-users">No users found</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="connect-users-list">
                        {connectUsers.map((u) => <ConnectUserCard key={u.user_id} user={u} />)}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Routing Profiles */}
                <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base text-zinc-100">Routing Profiles</CardTitle>
                        <CardDescription className="text-zinc-500 text-xs">Agent routing configurations</CardDescription>
                      </div>
                      <Badge variant="outline" className="text-xs bg-rose-500/10 text-rose-400 border-rose-500/30">{routingProfiles.length} profiles</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {routingProfiles.length === 0 ? (
                      <p className="text-sm text-zinc-500 text-center py-4" data-testid="no-routing-profiles">No routing profiles found</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="connect-routing-profiles-list">
                        {routingProfiles.map((p) => <RoutingProfileCard key={p.routing_profile_id} profile={p} />)}
                      </div>
                    )}
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
