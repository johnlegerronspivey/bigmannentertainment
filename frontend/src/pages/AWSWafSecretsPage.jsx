import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

const statusColor = (s) => {
  const map = {
    Active: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    ENABLED: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    Connected: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    allow: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    block: "bg-rose-500/15 text-rose-400 border-rose-500/30",
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
          {data?.total_acls !== undefined && <p>Your Web ACLs: <span className="text-zinc-300">{data.total_acls}</span></p>}
          {data?.total_secrets !== undefined && <p>Your secrets: <span className="text-zinc-300">{data.total_secrets}</span></p>}
          {data?.web_acls_found !== undefined && <p>Web ACLs found: <span className="text-zinc-300">{data.web_acls_found}</span></p>}
          {data?.secrets_found !== undefined && <p>Secrets found: <span className="text-zinc-300">{data.secrets_found}</span></p>}
        </div>
      </CardContent>
    </Card>
  );
};

/* ---- Web ACL Card ---- */
const WebACLCard = ({ acl, onView, onDelete, deleting }) => (
  <div className="p-4 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`waf-acl-${acl.id}`}>
    <div className="flex items-center justify-between mb-2">
      <h4 className="text-sm font-semibold text-zinc-100">{acl.name}</h4>
      <Badge variant="outline" className="text-[10px] bg-indigo-500/15 text-indigo-400 border-indigo-500/30">Web ACL</Badge>
    </div>
    {acl.description && <p className="text-[10px] text-zinc-500 mb-1">{acl.description}</p>}
    <p className="text-[10px] text-zinc-500">ID: <span className="text-zinc-400 font-mono">{acl.id}</span></p>
    <div className="flex justify-end mt-2 gap-2">
      <Button size="sm" variant="outline" className="h-7 text-xs border-zinc-700 text-zinc-300 hover:bg-zinc-700" onClick={() => onView(acl)} data-testid={`view-acl-${acl.id}`}>
        Details
      </Button>
      <Button size="sm" variant="outline" className="h-7 text-xs border-rose-800 text-rose-400 hover:bg-rose-900/30" disabled={deleting} onClick={() => onDelete(acl)} data-testid={`delete-acl-${acl.id}`}>
        {deleting ? "..." : "Delete"}
      </Button>
    </div>
  </div>
);

/* ---- IP Set Card ---- */
const IPSetCard = ({ ipSet, onView, onDelete, deleting }) => (
  <div className="p-4 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`waf-ipset-${ipSet.id}`}>
    <div className="flex items-center justify-between mb-2">
      <h4 className="text-sm font-semibold text-zinc-100">{ipSet.name}</h4>
      <Badge variant="outline" className="text-[10px] bg-amber-500/15 text-amber-400 border-amber-500/30">IP Set</Badge>
    </div>
    {ipSet.description && <p className="text-[10px] text-zinc-500 mb-1">{ipSet.description}</p>}
    <p className="text-[10px] text-zinc-500">ID: <span className="text-zinc-400 font-mono">{ipSet.id}</span></p>
    <div className="flex justify-end mt-2 gap-2">
      <Button size="sm" variant="outline" className="h-7 text-xs border-zinc-700 text-zinc-300 hover:bg-zinc-700" onClick={() => onView(ipSet)} data-testid={`view-ipset-${ipSet.id}`}>
        Details
      </Button>
      <Button size="sm" variant="outline" className="h-7 text-xs border-rose-800 text-rose-400 hover:bg-rose-900/30" disabled={deleting} onClick={() => onDelete(ipSet)} data-testid={`delete-ipset-${ipSet.id}`}>
        {deleting ? "..." : "Delete"}
      </Button>
    </div>
  </div>
);

/* ---- Secret Card ---- */
const SecretCard = ({ secret, onView, onDelete, deleting }) => (
  <div className="p-4 bg-zinc-800/40 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`secret-${secret.name}`}>
    <div className="flex items-center justify-between mb-2">
      <h4 className="text-sm font-semibold text-zinc-100 truncate max-w-[200px]">{secret.name}</h4>
      <div className="flex gap-1.5">
        {secret.rotation_enabled && <Badge variant="outline" className="text-[10px] bg-emerald-500/15 text-emerald-400 border-emerald-500/30">Rotation</Badge>}
        <Badge variant="outline" className="text-[10px] bg-violet-500/15 text-violet-400 border-violet-500/30">Secret</Badge>
      </div>
    </div>
    {secret.description && <p className="text-[10px] text-zinc-500 mb-1">{secret.description}</p>}
    <p className="text-[10px] text-zinc-500">Created: <span className="text-zinc-400">{secret.created_date ? new Date(secret.created_date).toLocaleDateString() : "N/A"}</span></p>
    {secret.last_changed_date && <p className="text-[10px] text-zinc-500">Last changed: <span className="text-zinc-400">{new Date(secret.last_changed_date).toLocaleDateString()}</span></p>}
    <div className="flex justify-end mt-2 gap-2">
      <Button size="sm" variant="outline" className="h-7 text-xs border-zinc-700 text-zinc-300 hover:bg-zinc-700" onClick={() => onView(secret)} data-testid={`view-secret-${secret.name}`}>
        Details
      </Button>
      <Button size="sm" variant="outline" className="h-7 text-xs border-rose-800 text-rose-400 hover:bg-rose-900/30" disabled={deleting} onClick={() => onDelete(secret)} data-testid={`delete-secret-${secret.name}`}>
        {deleting ? "..." : "Delete"}
      </Button>
    </div>
  </div>
);

/* ---- Managed Rule Group Card ---- */
const ManagedRuleCard = ({ rule }) => (
  <div className="p-3 bg-zinc-800/40 rounded-lg border border-zinc-800" data-testid={`managed-rule-${rule.name}`}>
    <div className="flex items-center justify-between mb-1">
      <h4 className="text-xs font-semibold text-zinc-100">{rule.name}</h4>
      <Badge variant="outline" className="text-[9px] bg-cyan-500/15 text-cyan-400 border-cyan-500/30">{rule.vendor}</Badge>
    </div>
    {rule.description && <p className="text-[10px] text-zinc-500">{rule.description}</p>}
  </div>
);

/* ========== MAIN PAGE ========== */
export default function AWSWafSecretsPage() {
  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("waf");

  // WAF state
  const [webACLs, setWebACLs] = useState([]);
  const [ipSets, setIPSets] = useState([]);
  const [managedRules, setManagedRules] = useState([]);
  const [aclLoading, setAclLoading] = useState(false);
  const [ipSetLoading, setIPSetLoading] = useState(false);
  const [managedRulesLoading, setManagedRulesLoading] = useState(false);
  const [selectedACL, setSelectedACL] = useState(null);
  const [selectedIPSet, setSelectedIPSet] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [showCreateACL, setShowCreateACL] = useState(false);
  const [showCreateIPSet, setShowCreateIPSet] = useState(false);
  const [aclForm, setAclForm] = useState({ name: "", default_action: "allow", description: "" });
  const [ipSetForm, setIPSetForm] = useState({ name: "", addresses: "", ip_version: "IPV4", description: "" });

  // Secrets state
  const [secrets, setSecrets] = useState([]);
  const [secretsLoading, setSecretsLoading] = useState(false);
  const [selectedSecret, setSelectedSecret] = useState(null);
  const [showCreateSecret, setShowCreateSecret] = useState(false);
  const [secretForm, setSecretForm] = useState({ name: "", secret_value: "", description: "", is_json: false });

  // ── Fetchers ──
  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/aws-security/status`, { headers });
      if (res.ok) setStatus(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  const fetchWebACLs = useCallback(async () => {
    setAclLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-security/waf/web-acls?scope=REGIONAL`, { headers });
      if (res.ok) { const d = await res.json(); setWebACLs(d.web_acls || []); }
    } catch (e) { console.error(e); }
    finally { setAclLoading(false); }
  }, [token]);

  const fetchIPSets = useCallback(async () => {
    setIPSetLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-security/waf/ip-sets?scope=REGIONAL`, { headers });
      if (res.ok) { const d = await res.json(); setIPSets(d.ip_sets || []); }
    } catch (e) { console.error(e); }
    finally { setIPSetLoading(false); }
  }, [token]);

  const fetchManagedRules = useCallback(async () => {
    setManagedRulesLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-security/waf/managed-rules?scope=REGIONAL`, { headers });
      if (res.ok) { const d = await res.json(); setManagedRules(d.managed_rule_groups || []); }
    } catch (e) { console.error(e); }
    finally { setManagedRulesLoading(false); }
  }, [token]);

  const fetchSecrets = useCallback(async () => {
    setSecretsLoading(true);
    try {
      const res = await fetch(`${API}/api/aws-security/secrets`, { headers });
      if (res.ok) { const d = await res.json(); setSecrets(d.secrets || []); }
    } catch (e) { console.error(e); }
    finally { setSecretsLoading(false); }
  }, [token]);

  useEffect(() => { if (token) fetchStatus(); }, [fetchStatus, token]);

  useEffect(() => {
    if (!token) return;
    if (tab === "waf") { fetchWebACLs(); fetchIPSets(); fetchManagedRules(); }
    if (tab === "secrets") { fetchSecrets(); }
  }, [tab, token, fetchWebACLs, fetchIPSets, fetchManagedRules, fetchSecrets]);

  // ── WAF Handlers ──
  const handleViewACL = async (acl) => {
    try {
      const res = await fetch(`${API}/api/aws-security/waf/web-acls/${acl.id}?name=${encodeURIComponent(acl.name)}&scope=REGIONAL`, { headers });
      if (res.ok) setSelectedACL(await res.json());
      else toast.error("Failed to load Web ACL details");
    } catch (e) { toast.error("Error loading details"); }
  };

  const handleCreateACL = async () => {
    if (!aclForm.name.trim()) { toast.error("Name is required"); return; }
    try {
      const res = await fetch(`${API}/api/aws-security/waf/web-acls`, {
        method: "POST", headers, body: JSON.stringify(aclForm),
      });
      if (res.ok) {
        toast.success("Web ACL created");
        setShowCreateACL(false);
        setAclForm({ name: "", default_action: "allow", description: "" });
        fetchWebACLs(); fetchStatus();
      } else {
        const d = await res.json();
        toast.error(d.detail || "Failed to create Web ACL");
      }
    } catch (e) { toast.error("Error creating Web ACL"); }
  };

  const handleDeleteACL = async (acl) => {
    if (!window.confirm(`Delete Web ACL "${acl.name}"?`)) return;
    setDeletingId(acl.id);
    try {
      const res = await fetch(`${API}/api/aws-security/waf/web-acls`, {
        method: "DELETE", headers,
        body: JSON.stringify({ name: acl.name, acl_id: acl.id, lock_token: acl.lock_token, scope: "REGIONAL" }),
      });
      if (res.ok) { toast.success("Web ACL deleted"); fetchWebACLs(); fetchStatus(); }
      else toast.error("Failed to delete Web ACL");
    } catch (e) { toast.error("Error deleting"); }
    finally { setDeletingId(null); }
  };

  const handleViewIPSet = async (ipSet) => {
    try {
      const res = await fetch(`${API}/api/aws-security/waf/ip-sets/${ipSet.id}?name=${encodeURIComponent(ipSet.name)}&scope=REGIONAL`, { headers });
      if (res.ok) setSelectedIPSet(await res.json());
      else toast.error("Failed to load IP set details");
    } catch (e) { toast.error("Error loading details"); }
  };

  const handleCreateIPSet = async () => {
    if (!ipSetForm.name.trim() || !ipSetForm.addresses.trim()) { toast.error("Name and addresses required"); return; }
    const addresses = ipSetForm.addresses.split("\n").map(a => a.trim()).filter(Boolean);
    try {
      const res = await fetch(`${API}/api/aws-security/waf/ip-sets`, {
        method: "POST", headers,
        body: JSON.stringify({ ...ipSetForm, addresses }),
      });
      if (res.ok) {
        toast.success("IP set created");
        setShowCreateIPSet(false);
        setIPSetForm({ name: "", addresses: "", ip_version: "IPV4", description: "" });
        fetchIPSets();
      } else {
        const d = await res.json();
        toast.error(d.detail || "Failed to create IP set");
      }
    } catch (e) { toast.error("Error creating IP set"); }
  };

  const handleDeleteIPSet = async (ipSet) => {
    if (!window.confirm(`Delete IP set "${ipSet.name}"?`)) return;
    setDeletingId(ipSet.id);
    try {
      const res = await fetch(`${API}/api/aws-security/waf/ip-sets`, {
        method: "DELETE", headers,
        body: JSON.stringify({ name: ipSet.name, ip_set_id: ipSet.id, lock_token: ipSet.lock_token, scope: "REGIONAL" }),
      });
      if (res.ok) { toast.success("IP set deleted"); fetchIPSets(); }
      else toast.error("Failed to delete IP set");
    } catch (e) { toast.error("Error deleting"); }
    finally { setDeletingId(null); }
  };

  // ── Secrets Handlers ──
  const handleViewSecret = async (secret) => {
    try {
      const res = await fetch(`${API}/api/aws-security/secrets/${encodeURIComponent(secret.name)}`, { headers });
      if (res.ok) setSelectedSecret(await res.json());
      else toast.error("Failed to load secret details");
    } catch (e) { toast.error("Error loading details"); }
  };

  const handleCreateSecret = async () => {
    if (!secretForm.name.trim() || !secretForm.secret_value.trim()) { toast.error("Name and value required"); return; }
    try {
      const res = await fetch(`${API}/api/aws-security/secrets`, {
        method: "POST", headers, body: JSON.stringify(secretForm),
      });
      if (res.ok) {
        toast.success("Secret created");
        setShowCreateSecret(false);
        setSecretForm({ name: "", secret_value: "", description: "", is_json: false });
        fetchSecrets(); fetchStatus();
      } else {
        const d = await res.json();
        toast.error(d.detail || "Failed to create secret");
      }
    } catch (e) { toast.error("Error creating secret"); }
  };

  const handleDeleteSecret = async (secret) => {
    if (!window.confirm(`Delete secret "${secret.name}"? It will have a 7-day recovery window.`)) return;
    setDeletingId(secret.name);
    try {
      const res = await fetch(`${API}/api/aws-security/secrets/${encodeURIComponent(secret.name)}`, {
        method: "DELETE", headers,
      });
      if (res.ok) { toast.success("Secret scheduled for deletion"); fetchSecrets(); fetchStatus(); }
      else toast.error("Failed to delete secret");
    } catch (e) { toast.error("Error deleting"); }
    finally { setDeletingId(null); }
  };

  // ── Shield Icon ──
  const ShieldIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
  );
  const KeyIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-security-page">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-zinc-50 mb-1" data-testid="page-title">AWS Security</h1>
          <p className="text-sm text-zinc-500">WAF firewall rules & Secrets Manager for secure credential storage</p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <ServiceStatus title="AWS WAF" data={status?.waf} icon={<ShieldIcon />} />
          <ServiceStatus title="Secrets Manager" data={status?.secrets_manager} icon={<KeyIcon />} />
        </div>

        {/* Tabs */}
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="bg-zinc-900 border border-zinc-800 mb-6">
            <TabsTrigger value="waf" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white" data-testid="tab-waf">
              WAF Firewall
            </TabsTrigger>
            <TabsTrigger value="secrets" className="data-[state=active]:bg-violet-600 data-[state=active]:text-white" data-testid="tab-secrets">
              Secrets Manager
            </TabsTrigger>
          </TabsList>

          {/* ═══════ WAF TAB ═══════ */}
          <TabsContent value="waf">
            <div className="space-y-6">
              {/* Web ACLs Section */}
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-base text-zinc-100">Web ACLs</CardTitle>
                      <CardDescription className="text-xs text-zinc-500">Firewall access control lists</CardDescription>
                    </div>
                    <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-xs h-8" onClick={() => setShowCreateACL(!showCreateACL)} data-testid="create-acl-btn">
                      {showCreateACL ? "Cancel" : "Create Web ACL"}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {showCreateACL && (
                    <div className="p-4 bg-zinc-800/60 rounded-lg border border-zinc-700 mb-4 space-y-3" data-testid="create-acl-form">
                      <input className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500" placeholder="Web ACL name" value={aclForm.name} onChange={e => setAclForm({...aclForm, name: e.target.value})} data-testid="acl-name-input" />
                      <input className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500" placeholder="Description (optional)" value={aclForm.description} onChange={e => setAclForm({...aclForm, description: e.target.value})} data-testid="acl-desc-input" />
                      <div className="flex items-center gap-3">
                        <label className="text-xs text-zinc-400">Default action:</label>
                        <select className="bg-zinc-900 border border-zinc-700 rounded-md px-2 py-1 text-sm text-zinc-100" value={aclForm.default_action} onChange={e => setAclForm({...aclForm, default_action: e.target.value})} data-testid="acl-action-select">
                          <option value="allow">Allow</option>
                          <option value="block">Block</option>
                        </select>
                      </div>
                      <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-xs" onClick={handleCreateACL} data-testid="submit-acl-btn">Create</Button>
                    </div>
                  )}
                  {aclLoading ? (
                    <div className="text-center py-6"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500 mx-auto" /></div>
                  ) : webACLs.length === 0 ? (
                    <p className="text-xs text-zinc-500 text-center py-6">No Web ACLs found. Create one to get started.</p>
                  ) : (
                    <div className="grid gap-3">{webACLs.map(acl => <WebACLCard key={acl.id} acl={acl} onView={handleViewACL} onDelete={handleDeleteACL} deleting={deletingId === acl.id} />)}</div>
                  )}
                </CardContent>
              </Card>

              {/* Web ACL Detail Modal */}
              {selectedACL && (
                <Card className="border-indigo-800 bg-zinc-900/80">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base text-zinc-100">{selectedACL.name} - Details</CardTitle>
                      <Button size="sm" variant="outline" className="h-7 text-xs border-zinc-700" onClick={() => setSelectedACL(null)} data-testid="close-acl-detail">Close</Button>
                    </div>
                  </CardHeader>
                  <CardContent className="text-xs text-zinc-400 space-y-2">
                    <p>ARN: <span className="text-zinc-300 font-mono text-[10px] break-all">{selectedACL.arn}</span></p>
                    <p>Default action: <Badge variant="outline" className={`text-[10px] ${statusColor(selectedACL.default_action)}`}>{selectedACL.default_action}</Badge></p>
                    <p>Capacity: <span className="text-zinc-300">{selectedACL.capacity}</span></p>
                    <p>Rules count: <span className="text-zinc-300">{selectedACL.rules_count}</span></p>
                    {selectedACL.rules?.length > 0 && (
                      <div>
                        <p className="font-semibold text-zinc-200 mt-2 mb-1">Rules:</p>
                        {selectedACL.rules.map((r, i) => (
                          <div key={i} className="p-2 bg-zinc-800/50 rounded mb-1 flex items-center justify-between">
                            <span className="text-zinc-300">{r.name}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-zinc-500">Priority: {r.priority}</span>
                              <Badge variant="outline" className={`text-[9px] ${statusColor(r.action)}`}>{r.action}</Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* IP Sets Section */}
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-base text-zinc-100">IP Sets</CardTitle>
                      <CardDescription className="text-xs text-zinc-500">Manage IP address blocklists/allowlists</CardDescription>
                    </div>
                    <Button size="sm" className="bg-amber-600 hover:bg-amber-700 text-xs h-8" onClick={() => setShowCreateIPSet(!showCreateIPSet)} data-testid="create-ipset-btn">
                      {showCreateIPSet ? "Cancel" : "Create IP Set"}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {showCreateIPSet && (
                    <div className="p-4 bg-zinc-800/60 rounded-lg border border-zinc-700 mb-4 space-y-3" data-testid="create-ipset-form">
                      <input className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500" placeholder="IP Set name" value={ipSetForm.name} onChange={e => setIPSetForm({...ipSetForm, name: e.target.value})} data-testid="ipset-name-input" />
                      <textarea className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 h-20" placeholder="IP addresses (one per line, CIDR format e.g. 192.168.1.0/24)" value={ipSetForm.addresses} onChange={e => setIPSetForm({...ipSetForm, addresses: e.target.value})} data-testid="ipset-addresses-input" />
                      <div className="flex items-center gap-3">
                        <label className="text-xs text-zinc-400">IP Version:</label>
                        <select className="bg-zinc-900 border border-zinc-700 rounded-md px-2 py-1 text-sm text-zinc-100" value={ipSetForm.ip_version} onChange={e => setIPSetForm({...ipSetForm, ip_version: e.target.value})} data-testid="ipset-version-select">
                          <option value="IPV4">IPv4</option>
                          <option value="IPV6">IPv6</option>
                        </select>
                      </div>
                      <input className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500" placeholder="Description (optional)" value={ipSetForm.description} onChange={e => setIPSetForm({...ipSetForm, description: e.target.value})} data-testid="ipset-desc-input" />
                      <Button size="sm" className="bg-amber-600 hover:bg-amber-700 text-xs" onClick={handleCreateIPSet} data-testid="submit-ipset-btn">Create</Button>
                    </div>
                  )}
                  {ipSetLoading ? (
                    <div className="text-center py-6"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-500 mx-auto" /></div>
                  ) : ipSets.length === 0 ? (
                    <p className="text-xs text-zinc-500 text-center py-6">No IP sets found.</p>
                  ) : (
                    <div className="grid gap-3">{ipSets.map(s => <IPSetCard key={s.id} ipSet={s} onView={handleViewIPSet} onDelete={handleDeleteIPSet} deleting={deletingId === s.id} />)}</div>
                  )}
                </CardContent>
              </Card>

              {/* IP Set Detail Modal */}
              {selectedIPSet && (
                <Card className="border-amber-800 bg-zinc-900/80">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base text-zinc-100">{selectedIPSet.name} - Details</CardTitle>
                      <Button size="sm" variant="outline" className="h-7 text-xs border-zinc-700" onClick={() => setSelectedIPSet(null)} data-testid="close-ipset-detail">Close</Button>
                    </div>
                  </CardHeader>
                  <CardContent className="text-xs text-zinc-400 space-y-2">
                    <p>ARN: <span className="text-zinc-300 font-mono text-[10px] break-all">{selectedIPSet.arn}</span></p>
                    <p>IP Version: <span className="text-zinc-300">{selectedIPSet.ip_version}</span></p>
                    <p>Total addresses: <span className="text-zinc-300">{selectedIPSet.addresses?.length || 0}</span></p>
                    {selectedIPSet.addresses?.length > 0 && (
                      <div>
                        <p className="font-semibold text-zinc-200 mt-2 mb-1">Addresses:</p>
                        <div className="bg-zinc-800/50 rounded p-2 max-h-32 overflow-y-auto font-mono text-[10px]">
                          {selectedIPSet.addresses.map((a, i) => <div key={i} className="text-zinc-300">{a}</div>)}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Managed Rules Section */}
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base text-zinc-100">AWS Managed Rule Groups</CardTitle>
                  <CardDescription className="text-xs text-zinc-500">Pre-built rule sets from AWS for common protections</CardDescription>
                </CardHeader>
                <CardContent>
                  {managedRulesLoading ? (
                    <div className="text-center py-6"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-500 mx-auto" /></div>
                  ) : managedRules.length === 0 ? (
                    <p className="text-xs text-zinc-500 text-center py-6">No managed rule groups found.</p>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-64 overflow-y-auto">{managedRules.map((r, i) => <ManagedRuleCard key={i} rule={r} />)}</div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* ═══════ SECRETS TAB ═══════ */}
          <TabsContent value="secrets">
            <div className="space-y-6">
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-base text-zinc-100">Secrets</CardTitle>
                      <CardDescription className="text-xs text-zinc-500">Securely store API keys, credentials, and configuration</CardDescription>
                    </div>
                    <Button size="sm" className="bg-violet-600 hover:bg-violet-700 text-xs h-8" onClick={() => setShowCreateSecret(!showCreateSecret)} data-testid="create-secret-btn">
                      {showCreateSecret ? "Cancel" : "Create Secret"}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {showCreateSecret && (
                    <div className="p-4 bg-zinc-800/60 rounded-lg border border-zinc-700 mb-4 space-y-3" data-testid="create-secret-form">
                      <input className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500" placeholder="Secret name (e.g. prod/api-key)" value={secretForm.name} onChange={e => setSecretForm({...secretForm, name: e.target.value})} data-testid="secret-name-input" />
                      <textarea className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 h-24 font-mono" placeholder='Secret value (plain text or JSON, e.g. {"api_key": "xxx"})' value={secretForm.secret_value} onChange={e => setSecretForm({...secretForm, secret_value: e.target.value})} data-testid="secret-value-input" />
                      <input className="w-full bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500" placeholder="Description (optional)" value={secretForm.description} onChange={e => setSecretForm({...secretForm, description: e.target.value})} data-testid="secret-desc-input" />
                      <div className="flex items-center gap-2">
                        <input type="checkbox" id="is-json" checked={secretForm.is_json} onChange={e => setSecretForm({...secretForm, is_json: e.target.checked})} className="rounded border-zinc-700" data-testid="secret-json-checkbox" />
                        <label htmlFor="is-json" className="text-xs text-zinc-400">Value is JSON</label>
                      </div>
                      <Button size="sm" className="bg-violet-600 hover:bg-violet-700 text-xs" onClick={handleCreateSecret} data-testid="submit-secret-btn">Create</Button>
                    </div>
                  )}
                  {secretsLoading ? (
                    <div className="text-center py-6"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-violet-500 mx-auto" /></div>
                  ) : secrets.length === 0 ? (
                    <p className="text-xs text-zinc-500 text-center py-6">No secrets found. Create one to securely store credentials.</p>
                  ) : (
                    <div className="grid gap-3">{secrets.map(s => <SecretCard key={s.name} secret={s} onView={handleViewSecret} onDelete={handleDeleteSecret} deleting={deletingId === s.name} />)}</div>
                  )}
                </CardContent>
              </Card>

              {/* Secret Detail Modal */}
              {selectedSecret && (
                <Card className="border-violet-800 bg-zinc-900/80">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base text-zinc-100">{selectedSecret.name} - Metadata</CardTitle>
                      <Button size="sm" variant="outline" className="h-7 text-xs border-zinc-700" onClick={() => setSelectedSecret(null)} data-testid="close-secret-detail">Close</Button>
                    </div>
                  </CardHeader>
                  <CardContent className="text-xs text-zinc-400 space-y-2">
                    <p>ARN: <span className="text-zinc-300 font-mono text-[10px] break-all">{selectedSecret.arn}</span></p>
                    <p>Created: <span className="text-zinc-300">{selectedSecret.created_date ? new Date(selectedSecret.created_date).toLocaleString() : "N/A"}</span></p>
                    <p>Last changed: <span className="text-zinc-300">{selectedSecret.last_changed_date ? new Date(selectedSecret.last_changed_date).toLocaleString() : "N/A"}</span></p>
                    <p>Last accessed: <span className="text-zinc-300">{selectedSecret.last_accessed_date ? new Date(selectedSecret.last_accessed_date).toLocaleString() : "N/A"}</span></p>
                    <p>Rotation enabled: <Badge variant="outline" className={`text-[10px] ${selectedSecret.rotation_enabled ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : "bg-zinc-500/15 text-zinc-400 border-zinc-500/30"}`}>{selectedSecret.rotation_enabled ? "Yes" : "No"}</Badge></p>
                    {selectedSecret.rotation_lambda_arn && <p>Rotation Lambda: <span className="text-zinc-300 font-mono text-[10px]">{selectedSecret.rotation_lambda_arn}</span></p>}
                    {Object.keys(selectedSecret.tags || {}).length > 0 && (
                      <div>
                        <p className="font-semibold text-zinc-200 mt-2 mb-1">Tags:</p>
                        <div className="flex flex-wrap gap-1">
                          {Object.entries(selectedSecret.tags).map(([k, v]) => (
                            <Badge key={k} variant="outline" className="text-[9px] bg-zinc-800 text-zinc-300 border-zinc-700">{k}: {v}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {Object.keys(selectedSecret.version_ids || {}).length > 0 && (
                      <div>
                        <p className="font-semibold text-zinc-200 mt-2 mb-1">Versions:</p>
                        {Object.entries(selectedSecret.version_ids).map(([vid, stages]) => (
                          <div key={vid} className="p-1.5 bg-zinc-800/50 rounded mb-1 text-[10px]">
                            <span className="text-zinc-500 font-mono">{vid.slice(0, 16)}...</span>
                            <span className="text-zinc-400 ml-2">{Array.isArray(stages) ? stages.join(", ") : String(stages)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
