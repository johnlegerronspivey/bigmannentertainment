import React, { useState, useEffect, useCallback } from 'react';
import { ChevronRight, Vote, Users, Wallet, Settings, TrendingUp, Clock, CheckCircle, XCircle, AlertCircle, ExternalLink, Copy, RefreshCw, Plus, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// ==================== UTILITY FUNCTIONS ====================

const formatAddress = (address) => {
  if (!address) return '';
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

const formatNumber = (num) => {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(2)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toFixed(0);
};

const formatCurrency = (num) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
};

const getStateColor = (state) => {
  const colors = {
    active: 'bg-green-500/20 text-green-400 border-green-500/30',
    succeeded: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    executed: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    defeated: 'bg-red-500/20 text-red-400 border-red-500/30',
    draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    queued: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    canceled: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    expired: 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  };
  return colors[state] || colors.draft;
};

const getCategoryIcon = (category) => {
  const icons = {
    treasury_allocation: '💰',
    revenue_distribution: '📊',
    platform_upgrade: '🚀',
    policy_change: '📜',
    partnership: '🤝',
    governance_change: '🏛️',
    emergency_action: '⚡',
    feature_request: '✨',
    contract_upgrade: '📝',
    token_distribution: '🪙'
  };
  return icons[category] || '📋';
};

// ==================== MAIN COMPONENT ====================

const DAOGovernanceV2Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Data states
  const [proposals, setProposals] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [treasury, setTreasury] = useState(null);
  const [delegates, setDelegates] = useState([]);
  const [council, setCouncil] = useState([]);
  const [memberProfile, setMemberProfile] = useState(null);
  const [config, setConfig] = useState(null);
  
  // Filters
  const [proposalFilter, setProposalFilter] = useState('all');
  const [networkFilter, setNetworkFilter] = useState('all');
  
  // Mock user for demo
  const currentUserId = 'user_001';
  const currentWallet = '0x742d35C6C7C3F4b1e6a0dCc1C3aF2f6D4E5B5e4A';

  // ==================== DATA FETCHING ====================

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [proposalsRes, metricsRes, treasuryRes, delegatesRes, councilRes, profileRes, configRes] = await Promise.all([
        fetch(`${API}/api/dao-v2/proposals?limit=20`),
        fetch(`${API}/api/dao-v2/metrics`),
        fetch(`${API}/api/dao-v2/treasury`),
        fetch(`${API}/api/dao-v2/delegates`),
        fetch(`${API}/api/dao-v2/council`),
        fetch(`${API}/api/dao-v2/members/me?user_id=${currentUserId}&wallet_address=${currentWallet}`),
        fetch(`${API}/api/dao-v2/config`)
      ]);
      
      const [proposalsData, metricsData, treasuryData, delegatesData, councilData, profileData, configData] = await Promise.all([
        proposalsRes.json(),
        metricsRes.json(),
        treasuryRes.json(),
        delegatesRes.json(),
        councilRes.json(),
        profileRes.json(),
        configRes.json()
      ]);
      
      if (proposalsData.success) setProposals(proposalsData.proposals || []);
      if (metricsData.success) setMetrics(metricsData);
      if (treasuryData.success) setTreasury(treasuryData);
      if (delegatesData.success) setDelegates(delegatesData.delegates || []);
      if (councilData.success) setCouncil(councilData.council || []);
      if (profileData.success) setMemberProfile(profileData);
      if (configData.success) setConfig(configData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load DAO data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ==================== VOTING ====================

  const handleVote = async (proposalId, choice) => {
    try {
      const response = await fetch(`${API}/api/dao-v2/vote?user_id=${currentUserId}&wallet_address=${currentWallet}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          proposal_id: proposalId,
          choice: choice,
          reason: ''
        })
      });
      
      const result = await response.json();
      if (result.success) {
        alert(`Vote "${choice}" cast successfully!`);
        fetchData();
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (err) {
      console.error('Error voting:', err);
      alert('Failed to cast vote');
    }
  };

  // ==================== TABS ====================

  const tabs = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'proposals', label: 'Proposals', icon: Vote },
    { id: 'treasury', label: 'Treasury', icon: Wallet },
    { id: 'delegates', label: 'Delegates', icon: Users },
    { id: 'council', label: 'Council', icon: Settings },
    { id: 'profile', label: 'My Profile', icon: Users }
  ];

  // ==================== RENDER COMPONENTS ====================

  // Overview Tab
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Proposals"
          value={metrics?.metrics?.total_proposals || 0}
          subtitle={`${metrics?.metrics?.active_proposals || 0} active`}
          icon={Vote}
          color="purple"
        />
        <MetricCard
          title="Treasury Value"
          value={formatCurrency(metrics?.metrics?.treasury_total_usd || 0)}
          subtitle="Multi-chain holdings"
          icon={Wallet}
          color="green"
        />
        <MetricCard
          title="Token Holders"
          value={formatNumber(metrics?.metrics?.total_token_holders || 0)}
          subtitle={`${metrics?.metrics?.active_voters_30d || 0} active (30d)`}
          icon={Users}
          color="blue"
        />
        <MetricCard
          title="Participation Rate"
          value={`${metrics?.metrics?.average_participation_rate?.toFixed(1) || 0}%`}
          subtitle="Avg. voter turnout"
          icon={TrendingUp}
          color="yellow"
        />
      </div>

      {/* Active Proposals */}
      <div className="bg-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-white">Active Proposals</h3>
          <button 
            onClick={() => setActiveTab('proposals')}
            className="text-purple-400 hover:text-purple-300 text-sm flex items-center gap-1"
          >
            View All <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        <div className="space-y-4">
          {proposals.filter(p => p.state === 'active').slice(0, 3).map(proposal => (
            <ProposalCard key={proposal.id} proposal={proposal} onVote={handleVote} compact />
          ))}
          {proposals.filter(p => p.state === 'active').length === 0 && (
            <p className="text-gray-400 text-center py-8">No active proposals at this time</p>
          )}
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Participation Trends */}
        <div className="bg-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">Participation Trends</h3>
          <div className="space-y-3">
            {metrics?.participation_trends?.map((trend, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-gray-400">{trend.month}</span>
                <div className="flex-1 mx-4">
                  <div className="h-2 bg-gray-700 rounded-full">
                    <div 
                      className="h-2 bg-purple-500 rounded-full transition-all"
                      style={{ width: `${trend.participation}%` }}
                    />
                  </div>
                </div>
                <span className="text-white font-medium">{trend.participation.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Voters */}
        <div className="bg-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">Top Voters</h3>
          <div className="space-y-3">
            {metrics?.top_voters?.map((voter, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 font-bold">
                    {idx + 1}
                  </div>
                  <span className="text-white font-mono text-sm">{voter.address}</span>
                </div>
                <div className="text-right">
                  <div className="text-white font-medium">{voter.votes} votes</div>
                  <div className="text-gray-400 text-sm">{formatNumber(voter.power)} BME</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Governance Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {metrics?.insights?.map((insight, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-sm">
                {idx + 1}
              </div>
              <span className="text-gray-300">{insight}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Proposals Tab
  const renderProposals = () => (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 bg-gray-800 rounded-xl p-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Status</label>
          <select 
            value={proposalFilter}
            onChange={(e) => setProposalFilter(e.target.value)}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Proposals</option>
            <option value="active">Active</option>
            <option value="succeeded">Succeeded</option>
            <option value="executed">Executed</option>
            <option value="defeated">Defeated</option>
            <option value="draft">Draft</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Network</label>
          <select 
            value={networkFilter}
            onChange={(e) => setNetworkFilter(e.target.value)}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Networks</option>
            <option value="ethereum">Ethereum</option>
            <option value="polygon">Polygon</option>
          </select>
        </div>
        <div className="flex-1" />
        <button 
          onClick={fetchData}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg flex items-center gap-2 self-end"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Proposals List */}
      <div className="space-y-4">
        {proposals
          .filter(p => proposalFilter === 'all' || p.state === proposalFilter)
          .filter(p => networkFilter === 'all' || p.network === networkFilter)
          .map(proposal => (
            <ProposalCard key={proposal.id} proposal={proposal} onVote={handleVote} />
          ))}
        {proposals.length === 0 && (
          <div className="text-center py-12 bg-gray-800 rounded-xl">
            <Vote className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No proposals found</p>
          </div>
        )}
      </div>
    </div>
  );

  // Treasury Tab
  const renderTreasury = () => (
    <div className="space-y-6">
      {/* Treasury Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-xl p-6">
          <div className="text-gray-400 text-sm mb-1">Total Value</div>
          <div className="text-3xl font-bold text-white">
            {formatCurrency(treasury?.treasury?.total_value_usd || 0)}
          </div>
          <div className="text-green-400 text-sm mt-2 flex items-center gap-1">
            <ArrowUpRight className="w-4 h-4" /> +18% this quarter
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl p-6">
          <div className="text-gray-400 text-sm mb-1">Monthly Inflow</div>
          <div className="text-3xl font-bold text-green-400">
            +{formatCurrency(treasury?.treasury?.monthly_inflow || 0)}
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl p-6">
          <div className="text-gray-400 text-sm mb-1">Monthly Outflow</div>
          <div className="text-3xl font-bold text-red-400">
            -{formatCurrency(treasury?.treasury?.monthly_outflow || 0)}
          </div>
        </div>
      </div>

      {/* Assets */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-4">Treasury Assets</h3>
        <div className="space-y-4">
          {treasury?.treasury?.assets?.map((asset, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center text-lg">
                  {asset.symbol === 'ETH' ? '⟠' : asset.symbol === 'MATIC' ? '🟣' : '💵'}
                </div>
                <div>
                  <div className="text-white font-medium">{asset.name}</div>
                  <div className="text-gray-400 text-sm">{asset.network}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">{formatNumber(asset.balance)} {asset.symbol}</div>
                <div className="text-gray-400 text-sm">{formatCurrency(asset.value_usd)}</div>
              </div>
              <div className="w-24">
                <div className="h-2 bg-gray-600 rounded-full">
                  <div 
                    className="h-2 bg-purple-500 rounded-full"
                    style={{ width: `${asset.percentage_of_treasury}%` }}
                  />
                </div>
                <div className="text-gray-400 text-xs text-right mt-1">
                  {asset.percentage_of_treasury?.toFixed(1)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Flow Chart */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Monthly Flow</h3>
        <div className="flex items-end justify-between h-40 gap-4">
          {treasury?.flow_chart?.map((month, idx) => (
            <div key={idx} className="flex-1 flex flex-col items-center gap-2">
              <div className="flex-1 w-full flex flex-col justify-end gap-1">
                <div 
                  className="w-full bg-green-500/60 rounded-t"
                  style={{ height: `${(month.inflow / 200000) * 100}%` }}
                  title={`Inflow: ${formatCurrency(month.inflow)}`}
                />
                <div 
                  className="w-full bg-red-500/60 rounded-b"
                  style={{ height: `${(month.outflow / 200000) * 100}%` }}
                  title={`Outflow: ${formatCurrency(month.outflow)}`}
                />
              </div>
              <span className="text-gray-400 text-sm">{month.month}</span>
            </div>
          ))}
        </div>
        <div className="flex justify-center gap-6 mt-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500/60 rounded" />
            <span className="text-gray-400">Inflow</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500/60 rounded" />
            <span className="text-gray-400">Outflow</span>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Recent Transactions</h3>
        <div className="space-y-3">
          {treasury?.recent_transactions?.map((tx, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  tx.type === 'deposit' ? 'bg-green-500/20 text-green-400' : 
                  tx.type === 'withdrawal' ? 'bg-red-500/20 text-red-400' : 
                  'bg-blue-500/20 text-blue-400'
                }`}>
                  {tx.type === 'deposit' ? <ArrowUpRight className="w-4 h-4" /> : 
                   tx.type === 'withdrawal' ? <ArrowDownRight className="w-4 h-4" /> : 
                   <RefreshCw className="w-4 h-4" />}
                </div>
                <div>
                  <div className="text-white font-medium">{tx.description}</div>
                  <div className="text-gray-400 text-sm">{tx.timestamp}</div>
                </div>
              </div>
              <div className={`font-medium ${
                tx.type === 'deposit' ? 'text-green-400' : 
                tx.type === 'withdrawal' ? 'text-red-400' : 
                'text-white'
              }`}>
                {tx.type === 'deposit' ? '+' : tx.type === 'withdrawal' ? '-' : ''}
                {formatNumber(tx.amount)} {tx.asset}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Insights */}
      <div className="bg-gradient-to-r from-green-600/20 to-blue-600/20 border border-green-500/30 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Treasury Insights</h3>
        <ul className="space-y-2">
          {treasury?.insights?.map((insight, idx) => (
            <li key={idx} className="flex items-center gap-2 text-gray-300">
              <CheckCircle className="w-4 h-4 text-green-400" />
              {insight}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );

  // Delegates Tab
  const renderDelegates = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-2">Delegation</h3>
        <p className="text-gray-300 mb-4">
          Delegates are trusted community members who vote on behalf of token holders. 
          Delegating your votes helps ensure active participation in governance.
        </p>
        <div className="flex gap-4 text-sm">
          <div className="bg-gray-800/50 rounded-lg px-4 py-2">
            <span className="text-gray-400">Total Delegates:</span>
            <span className="text-white font-bold ml-2">{delegates.length}</span>
          </div>
          <div className="bg-gray-800/50 rounded-lg px-4 py-2">
            <span className="text-gray-400">Total Delegated:</span>
            <span className="text-white font-bold ml-2">{formatNumber(metrics?.metrics?.total_delegated_power || 0)} BME</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {delegates.map((delegate, idx) => (
          <div key={idx} className="bg-gray-800 rounded-xl p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-xl">
                  {delegate.display_name?.[0] || '?'}
                </div>
                <div>
                  <div className="text-white font-bold">{delegate.display_name || 'Anonymous'}</div>
                  <div className="text-gray-400 text-sm font-mono">{formatAddress(delegate.wallet_address)}</div>
                </div>
              </div>
              <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm">
                Delegate
              </span>
            </div>
            
            {delegate.bio && (
              <p className="text-gray-400 text-sm mb-4">{delegate.bio}</p>
            )}
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="text-gray-400 text-xs">Voting Power</div>
                <div className="text-white font-bold">{formatNumber(delegate.total_voting_power)} BME</div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="text-gray-400 text-xs">Delegators</div>
                <div className="text-white font-bold">{delegate.delegators_count}</div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="text-gray-400 text-xs">Votes Cast</div>
                <div className="text-white font-bold">{delegate.votes_cast}</div>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-3">
                <div className="text-gray-400 text-xs">Participation</div>
                <div className="text-white font-bold">{delegate.participation_rate?.toFixed(1)}%</div>
              </div>
            </div>
            
            <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors">
              Delegate Votes
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  // Council Tab
  const renderCouncil = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 border border-yellow-500/30 rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-2">DAO Council</h3>
        <p className="text-gray-300 mb-4">
          The Council consists of elected members with elevated governance privileges. 
          Council members can propose emergency actions and have higher voting weight on critical decisions.
        </p>
        <div className="flex gap-4 text-sm">
          <div className="bg-gray-800/50 rounded-lg px-4 py-2">
            <span className="text-gray-400">Council Members:</span>
            <span className="text-white font-bold ml-2">{council.length}</span>
          </div>
          <div className="bg-gray-800/50 rounded-lg px-4 py-2">
            <span className="text-gray-400">Required Tokens:</span>
            <span className="text-white font-bold ml-2">{formatNumber(config?.config?.council_threshold || 10000)} BME</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {council.map((member, idx) => (
          <div key={idx} className="bg-gray-800 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-14 h-14 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-400 text-2xl">
                {member.display_name?.[0] || '?'}
              </div>
              <div>
                <div className="text-white font-bold">{member.display_name || 'Anonymous'}</div>
                <div className="text-gray-400 text-sm font-mono">{formatAddress(member.wallet_address)}</div>
                <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded text-xs">
                  Council Member
                </span>
              </div>
            </div>
            
            {member.bio && (
              <p className="text-gray-400 text-sm mb-4">{member.bio}</p>
            )}
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Voting Power</span>
                <span className="text-white">{formatNumber(member.voting_power)} BME</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Proposals Created</span>
                <span className="text-white">{member.proposals_created}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Votes Cast</span>
                <span className="text-white">{member.votes_cast}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Reputation</span>
                <span className="text-white">{member.reputation_score?.toFixed(1)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // Profile Tab
  const renderProfile = () => (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="bg-gray-800 rounded-xl p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-3xl">
              {memberProfile?.member?.display_name?.[0] || 'U'}
            </div>
            <div>
              <div className="text-2xl font-bold text-white">
                {memberProfile?.member?.display_name || 'Anonymous'}
              </div>
              <div className="text-gray-400 font-mono flex items-center gap-2">
                {formatAddress(memberProfile?.member?.primary_wallet)}
                <button className="text-purple-400 hover:text-purple-300">
                  <Copy className="w-4 h-4" />
                </button>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm mt-2 inline-block ${
                memberProfile?.member?.role === 'council' ? 'bg-yellow-500/20 text-yellow-400' :
                memberProfile?.member?.role === 'delegate' ? 'bg-purple-500/20 text-purple-400' :
                'bg-gray-500/20 text-gray-400'
              }`}>
                {memberProfile?.member?.role?.toUpperCase() || 'MEMBER'}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-gray-400 text-sm">Reputation Score</div>
            <div className="text-3xl font-bold text-white">
              {memberProfile?.member?.reputation_score?.toFixed(1) || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-xl p-4">
          <div className="text-gray-400 text-sm mb-1">Total Voting Power</div>
          <div className="text-2xl font-bold text-white">
            {formatNumber(memberProfile?.stats?.voting_power || 0)}
          </div>
          <div className="text-purple-400 text-sm">BME Tokens</div>
        </div>
        <div className="bg-gray-800 rounded-xl p-4">
          <div className="text-gray-400 text-sm mb-1">Votes Cast</div>
          <div className="text-2xl font-bold text-white">
            {memberProfile?.stats?.votes_cast || 0}
          </div>
          <div className="text-blue-400 text-sm">All time</div>
        </div>
        <div className="bg-gray-800 rounded-xl p-4">
          <div className="text-gray-400 text-sm mb-1">Proposals Created</div>
          <div className="text-2xl font-bold text-white">
            {memberProfile?.stats?.proposals_created || 0}
          </div>
          <div className="text-green-400 text-sm">
            {memberProfile?.stats?.proposals_passed || 0} passed
          </div>
        </div>
        <div className="bg-gray-800 rounded-xl p-4">
          <div className="text-gray-400 text-sm mb-1">Participation Rate</div>
          <div className="text-2xl font-bold text-white">
            {memberProfile?.stats?.participation_rate?.toFixed(1) || 0}%
          </div>
          <div className="text-yellow-400 text-sm">Active voter</div>
        </div>
      </div>

      {/* Token Balances */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">Token Balances by Network</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(memberProfile?.member?.token_balances || {}).map(([network, balance]) => (
            <div key={network} className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                  {network === 'ethereum' ? '⟠' : '🟣'}
                </div>
                <div>
                  <div className="text-white font-medium capitalize">{network}</div>
                  <div className="text-gray-400 text-sm">
                    {network === 'ethereum' ? 'Mainnet' : 'Polygon'}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-white font-bold">{formatNumber(balance)} BME</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">Recent Votes</h3>
          <div className="space-y-3">
            {memberProfile?.recent_votes?.length > 0 ? (
              memberProfile.recent_votes.map((vote, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                  <div>
                    <div className="text-white text-sm">Proposal #{vote.proposal_id?.slice(0, 8)}...</div>
                    <div className="text-gray-400 text-xs">
                      {new Date(vote.voted_at).toLocaleDateString()}
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    vote.choice === 'for' ? 'bg-green-500/20 text-green-400' :
                    vote.choice === 'against' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {vote.choice?.toUpperCase()}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-center py-4">No recent votes</p>
            )}
          </div>
        </div>

        <div className="bg-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white mb-4">My Proposals</h3>
          <div className="space-y-3">
            {memberProfile?.recent_proposals?.length > 0 ? (
              memberProfile.recent_proposals.map((proposal, idx) => (
                <div key={idx} className="p-3 bg-gray-700/50 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-white text-sm font-medium">{proposal.title}</div>
                    <span className={`px-2 py-0.5 rounded text-xs border ${getStateColor(proposal.state)}`}>
                      {proposal.state?.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-gray-400 text-xs">
                    Created {new Date(proposal.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-center py-4">No proposals created</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  // ==================== MAIN RENDER ====================

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 py-8" data-testid="dao-governance-v2">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-purple-400 text-sm mb-2">
            <span>Governance</span>
            <ChevronRight className="w-4 h-4" />
            <span>DAO 2.0</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">DAO 2.0 Governance</h1>
          <p className="text-gray-400">
            Advanced multi-chain governance with token-based voting, treasury management, and delegation
          </p>
          <div className="flex gap-2 mt-4">
            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm flex items-center gap-1">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Ethereum Connected
            </span>
            <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm flex items-center gap-1">
              <span className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
              Polygon Connected
            </span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/30 rounded-xl p-4 mb-6 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-300">{error}</span>
            <button onClick={fetchData} className="ml-auto text-red-400 hover:text-red-300">
              Retry
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-gray-800 rounded-xl shadow-xl mb-6">
          <div className="flex overflow-x-auto border-b border-gray-700">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                data-testid={`tab-${tab.id}`}
                className={`px-6 py-4 font-semibold text-sm transition-colors flex items-center gap-2 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'text-purple-400 border-b-2 border-purple-500 bg-gray-900/50'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto" />
            <p className="text-gray-400 mt-4">Loading DAO data...</p>
          </div>
        )}

        {/* Tab Content */}
        {!loading && (
          <div>
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'proposals' && renderProposals()}
            {activeTab === 'treasury' && renderTreasury()}
            {activeTab === 'delegates' && renderDelegates()}
            {activeTab === 'council' && renderCouncil()}
            {activeTab === 'profile' && renderProfile()}
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== SUB-COMPONENTS ====================

const MetricCard = ({ title, value, subtitle, icon: Icon, color }) => {
  const colorClasses = {
    purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
    green: 'from-green-500/20 to-green-600/10 border-green-500/30',
    blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
    yellow: 'from-yellow-500/20 to-yellow-600/10 border-yellow-500/30'
  };
  
  const iconColors = {
    purple: 'text-purple-400',
    green: 'text-green-400',
    blue: 'text-blue-400',
    yellow: 'text-yellow-400'
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-xl p-6`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <Icon className={`w-5 h-5 ${iconColors[color]}`} />
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="text-gray-400 text-sm mt-1">{subtitle}</div>
    </div>
  );
};

const ProposalCard = ({ proposal, onVote, compact = false }) => {
  const quorumProgress = proposal.total_voting_power_snapshot > 0
    ? ((proposal.weight_for + proposal.weight_against + proposal.weight_abstain) / proposal.total_voting_power_snapshot * 100)
    : 0;
  const approvalProgress = (proposal.weight_for + proposal.weight_against) > 0
    ? (proposal.weight_for / (proposal.weight_for + proposal.weight_against) * 100)
    : 0;

  if (compact) {
    return (
      <div className="p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700 transition-colors">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">{getCategoryIcon(proposal.category)}</span>
            <h4 className="text-white font-medium">{proposal.title}</h4>
          </div>
          <span className={`px-2 py-0.5 rounded text-xs border ${getStateColor(proposal.state)}`}>
            {proposal.state?.toUpperCase()}
          </span>
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <span className="flex items-center gap-1">
            <Vote className="w-3 h-3" /> {proposal.total_votes} votes
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" /> 
            {proposal.voting_ends && new Date(proposal.voting_ends).toLocaleDateString()}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{getCategoryIcon(proposal.category)}</span>
            <span className={`px-2 py-0.5 rounded text-xs ${
              proposal.network === 'ethereum' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'
            }`}>
              {proposal.network?.toUpperCase()}
            </span>
            <span className={`px-2 py-0.5 rounded text-xs ${
              proposal.governance_type === 'on_chain' ? 'bg-green-500/20 text-green-400' : 
              proposal.governance_type === 'off_chain' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-blue-500/20 text-blue-400'
            }`}>
              {proposal.governance_type?.replace('_', '-').toUpperCase()}
            </span>
          </div>
          <h3 className="text-xl font-bold text-white mb-2">{proposal.title}</h3>
          <p className="text-gray-400 text-sm mb-4 line-clamp-2">{proposal.description}</p>
          
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
            <span>Proposed by {formatAddress(proposal.proposer_address)}</span>
            <span>#{proposal.proposal_number}</span>
            {proposal.voting_ends && (
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                Ends {new Date(proposal.voting_ends).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm border ${getStateColor(proposal.state)}`}>
          {proposal.state?.toUpperCase()}
        </span>
      </div>

      {/* Voting Stats */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="bg-gray-700/50 rounded-lg p-3">
          <div className="text-green-400 text-xl font-bold">{proposal.votes_for}</div>
          <div className="text-gray-400 text-sm">For ({formatNumber(proposal.weight_for)} BME)</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-3">
          <div className="text-red-400 text-xl font-bold">{proposal.votes_against}</div>
          <div className="text-gray-400 text-sm">Against ({formatNumber(proposal.weight_against)} BME)</div>
        </div>
        <div className="bg-gray-700/50 rounded-lg p-3">
          <div className="text-gray-400 text-xl font-bold">{proposal.votes_abstain}</div>
          <div className="text-gray-400 text-sm">Abstain ({formatNumber(proposal.weight_abstain)} BME)</div>
        </div>
      </div>

      {/* Progress Bars */}
      <div className="space-y-3 mb-4">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">Quorum Progress</span>
            <span className={quorumProgress >= proposal.quorum_required ? 'text-green-400' : 'text-gray-400'}>
              {quorumProgress.toFixed(1)}% / {proposal.quorum_required}%
              {quorumProgress >= proposal.quorum_required && <CheckCircle className="w-4 h-4 inline ml-1" />}
            </span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full">
            <div 
              className="h-2 bg-purple-500 rounded-full transition-all"
              style={{ width: `${Math.min(quorumProgress, 100)}%` }}
            />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">Approval</span>
            <span className={approvalProgress >= proposal.approval_threshold ? 'text-green-400' : 'text-gray-400'}>
              {approvalProgress.toFixed(1)}% / {proposal.approval_threshold}%
              {approvalProgress >= proposal.approval_threshold && <CheckCircle className="w-4 h-4 inline ml-1" />}
            </span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full">
            <div 
              className="h-2 bg-green-500 rounded-full transition-all"
              style={{ width: `${Math.min(approvalProgress, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Voting Buttons */}
      {proposal.state === 'active' && (
        <div className="flex gap-3">
          <button
            onClick={() => onVote(proposal.id, 'for')}
            data-testid={`vote-for-${proposal.id}`}
            className="flex-1 px-4 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <CheckCircle className="w-4 h-4" /> Vote For
          </button>
          <button
            onClick={() => onVote(proposal.id, 'against')}
            data-testid={`vote-against-${proposal.id}`}
            className="flex-1 px-4 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <XCircle className="w-4 h-4" /> Vote Against
          </button>
          <button
            onClick={() => onVote(proposal.id, 'abstain')}
            data-testid={`vote-abstain-${proposal.id}`}
            className="flex-1 px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <AlertCircle className="w-4 h-4" /> Abstain
          </button>
        </div>
      )}
    </div>
  );
};

export default DAOGovernanceV2Dashboard;
