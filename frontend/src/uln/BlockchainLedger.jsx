import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { RefreshCw, Box, Link2, Shield, Cpu, ChevronDown, ChevronUp } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const getToken = () => localStorage.getItem('token');

const api = async (path, opts = {}) => {
  const res = await fetch(`${API}/api/uln-enhanced${path}`, {
    ...opts,
    headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json', ...opts.headers },
  });
  return res.json();
};

// ── Blockchain Explorer ──
export const BlockchainLedger = () => {
  const [stats, setStats] = useState(null);
  const [blocks, setBlocks] = useState([]);
  const [txs, setTxs] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedBlock, setExpandedBlock] = useState(null);
  const [mining, setMining] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState(null);
  const [txPayload, setTxPayload] = useState({ tx_type: 'label_action', payload: {} });
  const [deployForm, setDeployForm] = useState({ contract_type: 'rights_split', label_id: '', parameters: {} });

  const refresh = useCallback(async () => {
    setLoading(true);
    const [s, b, t, c] = await Promise.all([
      api('/blockchain/stats'),
      api('/blockchain/blocks?limit=20'),
      api('/blockchain/transactions?limit=30'),
      api('/blockchain/contracts'),
    ]);
    if (s.success !== false) setStats(s);
    setBlocks(b.blocks || []);
    setTxs(t.transactions || []);
    setContracts(c.contracts || []);
    setLoading(false);
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const mine = async () => {
    setMining(true);
    await api('/blockchain/mine', { method: 'POST' });
    await refresh();
    setMining(false);
  };

  const verify = async () => {
    setVerifying(true);
    const res = await api('/blockchain/verify');
    setVerifyResult(res);
    setVerifying(false);
  };

  const addTx = async () => {
    await api('/blockchain/transactions', { method: 'POST', body: JSON.stringify(txPayload) });
    await refresh();
  };

  const deploy = async () => {
    if (!deployForm.label_id) return;
    await api('/blockchain/contracts/deploy', { method: 'POST', body: JSON.stringify(deployForm) });
    await refresh();
  };

  if (loading) return <div className="flex justify-center py-16"><RefreshCw className="w-8 h-8 animate-spin text-violet-500" /></div>;

  return (
    <div className="space-y-6" data-testid="blockchain-ledger">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Blocks', value: stats?.total_blocks, icon: <Box className="w-5 h-5" /> },
          { label: 'Transactions', value: stats?.total_transactions, icon: <Link2 className="w-5 h-5" /> },
          { label: 'Pending Tx', value: stats?.pending_transactions, icon: <Cpu className="w-5 h-5" /> },
          { label: 'Contracts', value: stats?.active_contracts, icon: <Shield className="w-5 h-5" /> },
        ].map((m) => (
          <Card key={m.label} className="bg-slate-800 border-slate-700">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-2 rounded-lg bg-violet-500/20 text-violet-400">{m.icon}</div>
              <div>
                <p className="text-xs text-slate-400">{m.label}</p>
                <p className="text-xl font-bold text-white">{m.value ?? 0}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Actions bar */}
      <div className="flex flex-wrap gap-3">
        <Button onClick={mine} disabled={mining} className="bg-violet-600 hover:bg-violet-700" data-testid="mine-block-btn">
          {mining ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Cpu className="w-4 h-4 mr-2" />}
          Mine Block
        </Button>
        <Button onClick={verify} disabled={verifying} variant="outline" className="border-slate-600 text-slate-200 hover:bg-slate-700" data-testid="verify-chain-btn">
          {verifying ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Shield className="w-4 h-4 mr-2" />}
          Verify Chain
        </Button>
        <Button onClick={refresh} variant="outline" className="border-slate-600 text-slate-200 hover:bg-slate-700">
          <RefreshCw className="w-4 h-4 mr-2" /> Refresh
        </Button>
      </div>

      {verifyResult && (
        <div className={`p-4 rounded-lg border ${verifyResult.valid ? 'bg-emerald-900/30 border-emerald-700 text-emerald-300' : 'bg-red-900/30 border-red-700 text-red-300'}`} data-testid="verify-result">
          {verifyResult.valid ? 'Chain integrity verified' : 'Chain integrity FAILED'} &mdash; {verifyResult.blocks_checked} blocks checked
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Blocks */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Blocks</CardTitle></CardHeader>
          <CardContent className="space-y-2 max-h-[420px] overflow-y-auto">
            {blocks.map((b) => (
              <div key={b.index} className="p-3 rounded bg-slate-700/60 cursor-pointer hover:bg-slate-700" onClick={() => setExpandedBlock(expandedBlock === b.index ? null : b.index)}>
                <div className="flex justify-between items-center">
                  <span className="text-violet-400 font-mono text-sm">Block #{b.index}</span>
                  <span className="text-xs text-slate-400">{b.tx_count ?? b.transactions?.length ?? 0} txs</span>
                  {expandedBlock === b.index ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                </div>
                {expandedBlock === b.index && (
                  <div className="mt-2 text-xs space-y-1 text-slate-300">
                    <p><span className="text-slate-500">Hash:</span> {b.hash?.slice(0, 24)}...</p>
                    <p><span className="text-slate-500">Prev:</span> {b.previous_hash?.slice(0, 24)}...</p>
                    <p><span className="text-slate-500">Nonce:</span> {b.nonce}</p>
                    <p><span className="text-slate-500">Merkle:</span> {b.merkle_root?.slice(0, 24)}...</p>
                    {b.mining_time_seconds && <p><span className="text-slate-500">Mined in:</span> {b.mining_time_seconds}s</p>}
                  </div>
                )}
              </div>
            ))}
            {blocks.length === 0 && <p className="text-slate-500 text-sm">No blocks yet</p>}
          </CardContent>
        </Card>

        {/* Transactions */}
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Recent Transactions</CardTitle></CardHeader>
          <CardContent className="space-y-2 max-h-[420px] overflow-y-auto">
            {txs.map((t) => (
              <div key={t.tx_id} className="p-3 rounded bg-slate-700/60">
                <div className="flex justify-between items-center">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded ${t.status === 'confirmed' ? 'bg-emerald-900/40 text-emerald-400' : 'bg-amber-900/40 text-amber-400'}`}>
                    {t.status}
                  </span>
                  <span className="text-xs text-slate-400">{t.tx_type}</span>
                </div>
                <p className="text-xs text-slate-400 mt-1 font-mono truncate">{t.tx_hash}</p>
              </div>
            ))}
            {txs.length === 0 && <p className="text-slate-500 text-sm">No transactions yet</p>}
          </CardContent>
        </Card>
      </div>

      {/* Add Transaction & Deploy Contract */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Add Transaction</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <select value={txPayload.tx_type} onChange={(e) => setTxPayload({ ...txPayload, tx_type: e.target.value })} className="w-full bg-slate-700 text-white border-slate-600 rounded px-3 py-2 text-sm">
              <option value="label_action">Label Action</option>
              <option value="royalty_payment">Royalty Payment</option>
              <option value="content_share">Content Share</option>
              <option value="dao_vote">DAO Vote</option>
              <option value="contract_execute">Contract Execute</option>
            </select>
            <Button onClick={addTx} className="w-full bg-violet-600 hover:bg-violet-700" data-testid="add-tx-btn">Submit Transaction</Button>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Deploy Smart Contract</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <select value={deployForm.contract_type} onChange={(e) => setDeployForm({ ...deployForm, contract_type: e.target.value })} className="w-full bg-slate-700 text-white border-slate-600 rounded px-3 py-2 text-sm">
              <option value="rights_split">Rights Split</option>
              <option value="royalty_distribution">Royalty Distribution</option>
              <option value="dao_governance">DAO Governance</option>
              <option value="licensing">Licensing</option>
            </select>
            <Input placeholder="Label ID (e.g. BM-LBL-...)" value={deployForm.label_id} onChange={(e) => setDeployForm({ ...deployForm, label_id: e.target.value })} className="bg-slate-700 border-slate-600 text-white" />
            <Button onClick={deploy} className="w-full bg-violet-600 hover:bg-violet-700" data-testid="deploy-contract-btn">Deploy Contract</Button>
          </CardContent>
        </Card>
      </div>

      {/* Contracts list */}
      {contracts.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Deployed Contracts ({contracts.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-slate-300">
                <thead className="text-xs text-slate-500 border-b border-slate-700">
                  <tr><th className="px-3 py-2">Contract ID</th><th className="px-3 py-2">Type</th><th className="px-3 py-2">Label</th><th className="px-3 py-2">Status</th><th className="px-3 py-2">Executions</th></tr>
                </thead>
                <tbody>
                  {contracts.map((c) => (
                    <tr key={c.contract_id} className="border-b border-slate-700/50">
                      <td className="px-3 py-2 font-mono text-xs">{c.contract_id}</td>
                      <td className="px-3 py-2">{c.contract_type}</td>
                      <td className="px-3 py-2 text-xs">{c.label_id}</td>
                      <td className="px-3 py-2"><span className="px-2 py-0.5 rounded text-xs bg-emerald-900/40 text-emerald-400">{c.status}</span></td>
                      <td className="px-3 py-2">{c.executions}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
