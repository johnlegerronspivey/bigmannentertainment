import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

const statusBadge = (ok) => (
  <Badge variant="outline" className={`text-[10px] ${ok ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : "bg-rose-500/15 text-rose-400 border-rose-500/30"}`}>
    {ok ? "Connected" : "Unavailable"}
  </Badge>
);

const statusColor = (s) => {
  const map = { AVAILABLE: "bg-emerald-500/15 text-emerald-400", ACTIVE: "bg-emerald-500/15 text-emerald-400", CREATING: "bg-sky-500/15 text-sky-400", DELETING: "bg-amber-500/15 text-amber-400", DELETED: "bg-zinc-500/15 text-zinc-400", FAILED: "bg-rose-500/15 text-rose-400" };
  return map[s] || "bg-zinc-500/15 text-zinc-400";
};

export default function AWSBlockchainPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [networks, setNetworks] = useState([]);
  const [selectedNetwork, setSelectedNetwork] = useState(null);
  const [networkDetail, setNetworkDetail] = useState(null);
  const [members, setMembers] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [accessors, setAccessors] = useState([]);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/aws-blockchain/status`, { headers });
      if (res.ok) setStatus(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  const fetchNetworks = async () => {
    try {
      const res = await fetch(`${API}/api/aws-blockchain/networks`, { headers });
      if (res.ok) { const d = await res.json(); setNetworks(d.networks || []); }
    } catch (e) { console.error(e); }
  };

  const fetchAccessors = async () => {
    try {
      const res = await fetch(`${API}/api/aws-blockchain/accessors`, { headers });
      if (res.ok) { const d = await res.json(); setAccessors(d.accessors || []); }
    } catch (e) { console.error(e); }
  };

  const selectNetwork = async (networkId) => {
    setSelectedNetwork(networkId);
    setLoadingDetail(true);
    setNetworkDetail(null);
    setMembers([]);
    setProposals([]);
    try {
      const [nRes, mRes, pRes] = await Promise.all([
        fetch(`${API}/api/aws-blockchain/networks/${networkId}`, { headers }),
        fetch(`${API}/api/aws-blockchain/networks/${networkId}/members`, { headers }),
        fetch(`${API}/api/aws-blockchain/networks/${networkId}/proposals`, { headers }),
      ]);
      if (nRes.ok) setNetworkDetail(await nRes.json());
      if (mRes.ok) { const d = await mRes.json(); setMembers(d.members || []); }
      if (pRes.ok) { const d = await pRes.json(); setProposals(d.proposals || []); }
    } catch (e) { toast.error("Failed to load network details"); }
    finally { setLoadingDetail(false); }
  };

  useEffect(() => { fetchStatus(); }, [fetchStatus]);
  useEffect(() => { if (token) { fetchNetworks(); fetchAccessors(); } }, [token]);

  if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><div className="text-zinc-400">Loading...</div></div>;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-blockchain-page">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-zinc-100 mb-1">Managed Blockchain</h1>
          <p className="text-sm text-zinc-500">Amazon Managed Blockchain - Hyperledger Fabric & Ethereum networks</p>
        </div>

        {/* Status */}
        <div className="mb-8">
          <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm" data-testid="service-status-managed-blockchain">
            <CardContent className="p-5">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-lg ${status?.managed_blockchain?.available ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`}>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                </div>
                <div>
                  <h3 className="font-semibold text-zinc-100 text-sm">Amazon Managed Blockchain</h3>
                  {statusBadge(status?.managed_blockchain?.available)}
                </div>
                <div className="ml-auto text-xs text-zinc-500">
                  {status?.managed_blockchain?.region && <span>Region: <span className="text-zinc-300">{status.managed_blockchain.region}</span></span>}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Networks List */}
          <div className="lg:col-span-1 space-y-4">
            <Card className="border-zinc-800 bg-zinc-900/60" data-testid="blockchain-networks">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm text-zinc-100">Networks ({networks.length})</CardTitle>
                  <Button size="sm" variant="outline" onClick={fetchNetworks} className="text-xs h-7" data-testid="refresh-networks-btn">Refresh</Button>
                </div>
              </CardHeader>
              <CardContent>
                {networks.length === 0 ? (
                  <p className="text-xs text-zinc-500">No blockchain networks found. Create one in the AWS Console to manage Hyperledger Fabric or Ethereum networks.</p>
                ) : networks.map((n, i) => (
                  <div
                    key={i}
                    onClick={() => selectNetwork(n.id)}
                    className={`p-3 rounded border mb-2 cursor-pointer transition-colors ${selectedNetwork === n.id ? "bg-violet-600/10 border-violet-500/30" : "bg-zinc-800/40 border-zinc-800 hover:border-zinc-700"}`}
                    data-testid={`network-${n.id}`}
                  >
                    <p className="text-sm font-medium text-zinc-200">{n.name}</p>
                    <div className="flex gap-2 mt-1">
                      <Badge variant="outline" className={`text-[10px] ${statusColor(n.status)}`}>{n.status}</Badge>
                      <Badge variant="outline" className="text-[10px] bg-indigo-500/10 text-indigo-400 border-indigo-500/30">{n.framework}</Badge>
                    </div>
                    {n.description && <p className="text-[10px] text-zinc-500 mt-1">{n.description}</p>}
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Accessors */}
            <Card className="border-zinc-800 bg-zinc-900/60" data-testid="blockchain-accessors">
              <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Accessors ({accessors.length})</CardTitle></CardHeader>
              <CardContent>
                {accessors.length === 0 ? (
                  <p className="text-xs text-zinc-500">No accessors found. Create a token-based accessor for blockchain network access.</p>
                ) : accessors.map((a, i) => (
                  <div key={i} className="p-2 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={`text-[10px] ${statusColor(a.status)}`}>{a.status}</Badge>
                      <span className="text-[10px] text-zinc-400">{a.type}</span>
                      {a.network_type && <span className="text-[10px] text-zinc-500">{a.network_type}</span>}
                    </div>
                    <p className="text-[10px] text-zinc-500 font-mono mt-1 truncate">{a.id}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Network Detail */}
          <div className="lg:col-span-2 space-y-4">
            {!selectedNetwork ? (
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardContent className="p-12 text-center">
                  <svg className="w-12 h-12 text-zinc-700 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                  <p className="text-sm text-zinc-500">Select a network to view details</p>
                </CardContent>
              </Card>
            ) : loadingDetail ? (
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardContent className="p-12 text-center"><p className="text-sm text-zinc-500">Loading network details...</p></CardContent>
              </Card>
            ) : (
              <>
                {/* Network Info */}
                {networkDetail && (
                  <Card className="border-zinc-800 bg-zinc-900/60" data-testid="network-detail">
                    <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">{networkDetail.name}</CardTitle></CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div>
                          <span className="text-zinc-500">Framework:</span>
                          <span className="text-zinc-200 ml-1">{networkDetail.framework} {networkDetail.framework_version}</span>
                        </div>
                        <div>
                          <span className="text-zinc-500">Status:</span>
                          <Badge variant="outline" className={`ml-1 text-[10px] ${statusColor(networkDetail.status)}`}>{networkDetail.status}</Badge>
                        </div>
                        {networkDetail.framework_attributes?.edition && (
                          <div>
                            <span className="text-zinc-500">Edition:</span>
                            <span className="text-zinc-200 ml-1">{networkDetail.framework_attributes.edition}</span>
                          </div>
                        )}
                        {networkDetail.voting_policy?.threshold_percentage > 0 && (
                          <div>
                            <span className="text-zinc-500">Voting Threshold:</span>
                            <span className="text-zinc-200 ml-1">{networkDetail.voting_policy.threshold_percentage}%</span>
                          </div>
                        )}
                      </div>
                      {networkDetail.description && <p className="text-xs text-zinc-400 mt-3">{networkDetail.description}</p>}
                    </CardContent>
                  </Card>
                )}

                {/* Members */}
                <Card className="border-zinc-800 bg-zinc-900/60" data-testid="network-members">
                  <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Members ({members.length})</CardTitle></CardHeader>
                  <CardContent>
                    {members.length === 0 ? (
                      <p className="text-xs text-zinc-500">No members in this network.</p>
                    ) : members.map((m, i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                        <div>
                          <p className="text-sm font-medium text-zinc-200">{m.name}</p>
                          <p className="text-[10px] text-zinc-500 font-mono">{m.id}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          {m.is_owned && <Badge variant="outline" className="text-[10px] bg-violet-500/10 text-violet-400 border-violet-500/30">Owned</Badge>}
                          <Badge variant="outline" className={`text-[10px] ${statusColor(m.status)}`}>{m.status}</Badge>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Proposals */}
                <Card className="border-zinc-800 bg-zinc-900/60" data-testid="network-proposals">
                  <CardHeader className="pb-2"><CardTitle className="text-sm text-zinc-100">Proposals ({proposals.length})</CardTitle></CardHeader>
                  <CardContent>
                    {proposals.length === 0 ? (
                      <p className="text-xs text-zinc-500">No proposals for this network.</p>
                    ) : proposals.map((p, i) => (
                      <div key={i} className="p-3 bg-zinc-800/40 rounded border border-zinc-800 mb-2">
                        <div className="flex items-center justify-between mb-1">
                          <p className="text-sm font-medium text-zinc-200">{p.description || `Proposal ${p.id}`}</p>
                          <Badge variant="outline" className={`text-[10px] ${statusColor(p.status)}`}>{p.status}</Badge>
                        </div>
                        <p className="text-[10px] text-zinc-500">Proposed by: {p.proposed_by_member_name || p.proposed_by_member_id}</p>
                        {p.expiration_date && <p className="text-[10px] text-zinc-500">Expires: {p.expiration_date}</p>}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
