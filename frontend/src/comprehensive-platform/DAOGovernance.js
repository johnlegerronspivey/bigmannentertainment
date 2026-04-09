import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';

const DAOGovernance = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [proposals, setProposals] = useState([]);
  const [daoMetrics, setDaoMetrics] = useState({});
  const [memberProfile, setMemberProfile] = useState({});
  const [treasury, setTreasury] = useState({});
  const [blockchainStatus, setBlockchainStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('proposals');

  useEffect(() => {
    fetchDaoData();
    fetchBlockchainStatus();
  }, []);

  const fetchDaoData = async () => {
    setLoading(true);
    try {
      const [proposalsRes, metricsRes, memberRes, treasuryRes] = await Promise.all([
        axios.get(`${API}/api/platform/dao/proposals?user_id=user_123`),
        axios.get(`${API}/api/platform/dao/metrics?user_id=user_123`),
        axios.get(`${API}/api/platform/dao/member?user_id=user_123`),
        axios.get(`${API}/api/platform/dao/treasury?user_id=user_123`)
      ]);

      if (proposalsRes.data.success) setProposals(proposalsRes.data.proposals || []);
      if (metricsRes.data.success) setDaoMetrics(metricsRes.data.metrics || {});
      if (memberRes.data.success) setMemberProfile(memberRes.data.member || {});
      if (treasuryRes.data.success) setTreasury(treasuryRes.data.treasury || {});
    } catch (error) {
      handleApiError(error, 'fetchDaoData');
    } finally {
      setLoading(false);
    }
  };

  const fetchBlockchainStatus = async () => {
    try {
      const response = await axios.get(`${API}/api/platform/dao/blockchain/status`);
      if (response.data.success) {
        setBlockchainStatus(response.data);
      }
    } catch (error) {
      handleApiError(error, 'fetchBlockchainStatus');
    }
  };

  const createBlockchainProposal = async (proposalData) => {
    try {
      const response = await axios.post(`${API}/api/platform/dao/proposals?user_id=user_123`, proposalData);
      if (response.data.success) {
        fetchDaoData(); // Refresh data
        return response.data;
      }
    } catch (error) {
      handleApiError(error, 'createBlockchainProposal');
    }
  };

  const castBlockchainVote = async (proposalId, choice, reason = '') => {
    try {
      const response = await axios.post(`${API}/api/platform/dao/proposals/${proposalId}/vote`, {
        choice,
        reason,
        user_id: 'user_123',
        wallet_address: memberProfile.wallet_address || '0xmock'
      });
      if (response.data.success) {
        fetchDaoData(); // Refresh data
        return response.data;
      }
    } catch (error) {
      handleApiError(error, 'castBlockchainVote');
    }
  };

  const getProposalStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'passed': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'rejected': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'executed': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const tabs = [
    { id: 'proposals', name: 'Proposals', icon: '🗳️' },
    { id: 'voting', name: 'Voting Power', icon: '⚡' },
    { id: 'treasury', name: 'Treasury', icon: '🏛️' },
    { id: 'blockchain', name: 'Blockchain', icon: '⛓️' },
    { id: 'governance', name: 'Governance', icon: '🏛️' },
    { id: 'profile', name: 'My Profile', icon: '👤' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">DAO Governance</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Decentralized governance and voting with Ethereum integration</p>
        </div>
        <div className="flex space-x-2">
          {/* Blockchain Connection Status */}
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${
            blockchainStatus.blockchain_connected 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          }`}>
            {blockchainStatus.blockchain_connected ? '🟢 Blockchain Connected' : '🟡 Mock Mode'}
          </div>
          <button 
            onClick={() => setActiveTab('blockchain')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <span>➕</span>
            <span>Create Proposal</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Proposals</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{daoMetrics.total_proposals || '15'}</p>
            </div>
            <span className="text-2xl">🗳️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Proposals</p>
              <p className="text-2xl font-bold text-blue-600">{daoMetrics.active_proposals || '3'}</p>
            </div>
            <span className="text-2xl">🔄</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Token Holders</p>
              <p className="text-2xl font-bold text-green-600">{blockchainStatus.total_token_holders || '247'}</p>
            </div>
            <span className="text-2xl">👥</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">My Voting Power</p>
              <p className="text-2xl font-bold text-green-600">{memberProfile.voting_power?.toLocaleString() || '15,000'}</p>
            </div>
            <span className="text-2xl">⚡</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Treasury Value</p>
              <p className="text-2xl font-bold text-purple-600">${treasury.total_value_usd?.toLocaleString() || '2,450,000'}</p>
            </div>
            <span className="text-2xl">🏛️</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'proposals' && (
          <div className="space-y-4">
            {proposals.length > 0 ? proposals.map((proposal, index) => (
              <div key={proposal.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{proposal.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getProposalStatusColor(proposal.status)}`}>
                        {proposal.status}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{proposal.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Type: {proposal.proposal_type?.replace('_', ' ')}</span>
                      <span>Proposer: {proposal.proposer_id}</span>
                      <span>Voting ends: {proposal.voting_ends ? new Date(proposal.voting_ends).toLocaleDateString() : 'N/A'}</span>
                    </div>
                  </div>
                  {proposal.status === 'active' && (
                    <div className="flex space-x-2 ml-4">
                      <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Vote Yes
                      </button>
                      <button className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700">
                        Vote No
                      </button>
                    </div>
                  )}
                </div>
                
                {proposal.status === 'active' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Yes Votes</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{width: `${((proposal.vote_weight_yes || 0) / ((proposal.vote_weight_yes || 0) + (proposal.vote_weight_no || 0) + 0.01)) * 100}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{proposal.yes_votes || 0}</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">No Votes</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-red-600 h-2 rounded-full" 
                            style={{width: `${((proposal.vote_weight_no || 0) / ((proposal.vote_weight_yes || 0) + (proposal.vote_weight_no || 0) + 0.01)) * 100}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{proposal.no_votes || 0}</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Quorum</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{width: `${Math.min(((proposal.total_votes || 0) / (proposal.quorum_required || 1)) * 100, 100)}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{((proposal.total_votes || 0) / (proposal.quorum_required || 1) * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🗳️</div>
                <p className="text-gray-600 dark:text-gray-400">No proposals found. Create the first proposal!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'voting' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`${isDarkMode ? 'bg-blue-800 border-blue-700' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">My Voting Power</h3>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-2">
                  {memberProfile.voting_power?.toLocaleString() || '15,000'} BME
                </p>
              </div>
              <div className={`${isDarkMode ? 'bg-green-800 border-green-700' : 'bg-green-50 border-green-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-green-900 dark:text-green-100">Token Balance</h3>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-2">
                  {memberProfile.token_balance?.toLocaleString() || '15,000'} BME
                </p>
              </div>
              <div className={`${isDarkMode ? 'bg-purple-800 border-purple-700' : 'bg-purple-50 border-purple-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-purple-900 dark:text-purple-100">Delegated Power</h3>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100 mt-2">
                  {memberProfile.delegated_power?.toLocaleString() || '0'} BME
                </p>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Delegation Options</h3>
              <div className="space-y-4">
                <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Delegate Your Voting Power</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Allow another member to vote on your behalf while retaining token ownership.
                  </p>
                  <div className="flex space-x-4">
                    <input 
                      type="text" 
                      placeholder="Enter wallet address..."
                      className={`flex-1 px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                    />
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                      Delegate
                    </button>
                  </div>
                </div>
                
                <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Remove Delegation</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Reclaim your voting power and vote directly on proposals.
                  </p>
                  <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
                    Remove Delegation  
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'treasury' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Treasury Assets</h3>
                <div className="space-y-4">
                  {treasury.assets?.map((asset, index) => (
                    <div key={asset.symbol || index} className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{asset.symbol}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{asset.balance?.toLocaleString()} tokens</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900 dark:text-white">
                          ${asset.value_usd?.toLocaleString()}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{asset.percentage}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Monthly Flow</h3>
                <div className="space-y-3">
                  {treasury.monthly_flow?.slice(-6).map((month, index) => (
                    <div key={month.month || index} className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-400">{month.month}</span>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          Net: ${month.net?.toLocaleString()}
                        </p>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          In: ${month.inflow?.toLocaleString()} | Out: ${month.outflow?.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Transactions</h3>
              <div className="space-y-4">
                {treasury.recent_transactions?.map((tx, index) => (
                  <div key={tx.id || index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{tx.description}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {tx.timestamp ? new Date(tx.timestamp).toLocaleDateString() : 'Recent'} • {tx.token_symbol}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`font-semibold ${
                        tx.transaction_type === 'deposit' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {tx.transaction_type === 'deposit' ? '+' : '-'}${tx.amount?.toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-32">
                        {tx.transaction_hash}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'blockchain' && (
          <div className="space-y-6">
            {/* Blockchain Status Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Network Status</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Network</span>
                    <span className={`font-medium ${blockchainStatus.blockchain_connected ? 'text-green-600' : 'text-yellow-600'}`}>
                      {blockchainStatus.network || 'Mock'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Connection</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      blockchainStatus.blockchain_connected 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}>
                      {blockchainStatus.blockchain_connected ? 'Connected' : 'Mock Mode'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Participation Rate</span>
                    <span className="font-medium text-blue-600">
                      {(blockchainStatus.participation_rate * 100).toFixed(1) || '73.0'}%
                    </span>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Contract Addresses</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Governance Contract</p>
                    <p className="font-mono text-xs text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 p-2 rounded">
                      {blockchainStatus.governance_contract || '0xabcd...ef12'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Token Contract</p>
                    <p className="font-mono text-xs text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 p-2 rounded">
                      {blockchainStatus.token_contract || '0x1234...5678'}
                    </p>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Blockchain Proposals</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">On-Chain Proposals</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {blockchainStatus.blockchain_proposals || '0'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Quorum Threshold</span>
                    <span className="font-medium text-purple-600">
                      {blockchainStatus.quorum_threshold?.toLocaleString() || '1,000'} BME
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Blockchain Activity */}
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Blockchain Activity</h3>
              <div className="space-y-4">
                {blockchainStatus.recent_blockchain_proposals?.length > 0 ? (
                  blockchainStatus.recent_blockchain_proposals.map((proposal, index) => (
                    <div key={proposal.id || index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{proposal.description}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Proposer: {proposal.proposer?.slice(0, 6)}...{proposal.proposer?.slice(-4)}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          proposal.status === 'active' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                          proposal.status === 'passed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                          'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {proposal.status}
                        </span>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Category: {proposal.category}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">⛓️</div>
                    <p className="text-gray-600 dark:text-gray-400">No recent blockchain activity</p>
                    <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                      Blockchain proposals will appear here when created
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Blockchain Integration Tools */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create Blockchain Proposal</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Proposal Title
                    </label>
                    <input 
                      type="text" 
                      placeholder="Enter proposal title..."
                      className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Description
                    </label>
                    <textarea 
                      rows={4}
                      placeholder="Describe your proposal..."
                      className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Proposal Type
                    </label>
                    <select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                      <option value="revenue_distribution">Revenue Distribution</option>
                      <option value="platform_upgrade">Platform Upgrade</option>
                      <option value="policy_change">Policy Change</option>
                      <option value="partnership">Partnership</option>
                      <option value="budget_allocation">Budget Allocation</option>
                    </select>
                  </div>
                  <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                    ⛓️ Create On-Chain Proposal
                  </button>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Smart Contract Integration</h3>
                <div className="space-y-4">
                  <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Voting Power from Blockchain</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      Your voting power is automatically calculated from your BME token balance on-chain.
                    </p>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Current Voting Power</span>
                      <span className="font-semibold text-blue-600">100 BME</span>
                    </div>
                  </div>
                  
                  <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Transaction Verification</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      All votes and proposals are recorded on the blockchain for transparency.
                    </p>
                    <button className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                      🔍 View on Blockchain Explorer
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'governance' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Governance Statistics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Token Holders</span>
                    <span className="font-medium text-gray-900 dark:text-white">{daoMetrics.total_token_holders?.toLocaleString() || '1,250'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Unique Voters</span>
                    <span className="font-medium text-gray-900 dark:text-white">{daoMetrics.unique_voters || '234'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Avg Participation</span>
                    <span className="font-medium text-blue-600">{daoMetrics.average_participation || '67.8'}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Votes Cast</span>
                    <span className="font-medium text-gray-900 dark:text-white">{daoMetrics.total_votes_cast?.toLocaleString() || '1,456'}</span>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Smart Contracts</h3>
                <div className="space-y-3">
                  <div className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900 dark:text-white">Governance Contract</span>
                      <span className="text-green-500">✅</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">0xabcd...ef12</p>
                  </div>
                  <div className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900 dark:text-white">BME Token Contract</span>
                      <span className="text-green-500">✅</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">0x1234...7890</p>
                  </div>
                  <div className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900 dark:text-white">Treasury Contract</span>
                      <span className="text-green-500">✅</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">0xfedc...ba09</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">DAO Member Profile</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Participation Stats</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Proposals Created</span>
                      <span className="font-medium text-gray-900 dark:text-white">{memberProfile.proposals_created || '3'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Votes Cast</span>
                      <span className="font-medium text-gray-900 dark:text-white">{memberProfile.votes_cast || '12'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Participation Rate</span>
                      <span className="font-medium text-green-600">{memberProfile.participation_rate || '85.7'}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Reputation Score</span>
                      <span className="font-medium text-purple-600">{memberProfile.reputation_score || '92.5'}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Token Information</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Token Balance</span>
                      <span className="font-medium text-gray-900 dark:text-white">{memberProfile.token_balance?.toLocaleString() || '15,000'} BME</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Voting Power</span>
                      <span className="font-medium text-blue-600">{memberProfile.voting_power?.toLocaleString() || '15,000'} BME</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Member Since</span>
                      <span className="font-medium text-gray-900 dark:text-white">Jan 2024</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Role</span>
                      <span className="font-medium text-gray-900 dark:text-white">{memberProfile.role || 'Token Holder'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { DAOGovernance };
