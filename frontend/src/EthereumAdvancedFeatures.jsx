import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

// ==================== CONTRACT DEPLOYMENT UI ====================

export const ContractDeploymentUI = () => {
  const [contractType, setContractType] = useState('erc20');
  const [formData, setFormData] = useState({
    contract_name: '',
    contract_symbol: '',
    initial_supply: '1000000',
    base_uri: '',
    recipients: [],
    percentages: []
  });
  const [deploying, setDeploying] = useState(false);
  const [deploymentResult, setDeploymentResult] = useState(null);
  const [deployedContracts, setDeployedContracts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDeployedContracts();
  }, []);

  const fetchDeployedContracts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API}/api/ethereum/advanced/deployed-contracts`);
      if (response.ok) {
        const data = await response.json();
        setDeployedContracts(data.contracts || []);
      }
    } catch (error) {
      console.error('Error fetching contracts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeployContract = async (e) => {
    e.preventDefault();
    setDeploying(true);
    setDeploymentResult(null);

    try {
      const deploymentData = {
        contract_type: contractType,
        contract_name: formData.contract_name,
        contract_symbol: formData.contract_symbol || undefined,
        initial_supply: contractType === 'erc20' ? formData.initial_supply : undefined,
        base_uri: (contractType === 'erc721' || contractType === 'erc1155') ? formData.base_uri : undefined,
        recipients: contractType === 'royalty_splitter' ? formData.recipients : undefined,
        percentages: contractType === 'royalty_splitter' ? formData.percentages : undefined
      };

      const response = await fetch(`${API}/api/ethereum/advanced/deploy-contract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deploymentData)
      });

      const result = await response.json();
      setDeploymentResult(result);

      if (result.success) {
        // Reset form
        setFormData({
          contract_name: '',
          contract_symbol: '',
          initial_supply: '1000000',
          base_uri: '',
          recipients: [],
          percentages: []
        });
        // Refresh deployed contracts list
        fetchDeployedContracts();
      }
    } catch (error) {
      console.error('Deployment error:', error);
      setDeploymentResult({
        success: false,
        error: error.message
      });
    } finally {
      setDeploying(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🚀 Contract Deployment</h1>
          <p className="text-gray-400">Deploy smart contracts to Ethereum Mainnet</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Deployment Form */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 rounded-xl shadow-xl p-6">
              <h2 className="text-2xl font-bold text-white mb-6">Deploy New Contract</h2>

              <form onSubmit={handleDeployContract} className="space-y-6">
                {/* Contract Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Contract Type
                  </label>
                  <select
                    value={contractType}
                    onChange={(e) => setContractType(e.target.value)}
                    className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  >
                    <option value="erc20">ERC-20 Token (Fungible Token)</option>
                    <option value="erc721">ERC-721 NFT (Non-Fungible Token)</option>
                    <option value="erc1155">ERC-1155 (Multi-Token)</option>
                    <option value="royalty_splitter">Royalty Splitter Contract</option>
                  </select>
                </div>

                {/* Contract Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Contract Name
                  </label>
                  <input
                    type="text"
                    value={formData.contract_name}
                    onChange={(e) => setFormData({...formData, contract_name: e.target.value})}
                    placeholder="e.g., My Token"
                    required
                    className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                  />
                </div>

                {/* Contract Symbol (for tokens) */}
                {(contractType === 'erc20' || contractType === 'erc721') && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Contract Symbol
                    </label>
                    <input
                      type="text"
                      value={formData.contract_symbol}
                      onChange={(e) => setFormData({...formData, contract_symbol: e.target.value})}
                      placeholder="e.g., MTK"
                      required
                      className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                    />
                  </div>
                )}

                {/* Initial Supply (for ERC-20) */}
                {contractType === 'erc20' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Initial Supply
                    </label>
                    <input
                      type="number"
                      value={formData.initial_supply}
                      onChange={(e) => setFormData({...formData, initial_supply: e.target.value})}
                      placeholder="1000000"
                      required
                      className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                    />
                  </div>
                )}

                {/* Base URI (for NFTs) */}
                {(contractType === 'erc721' || contractType === 'erc1155') && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Base URI (Metadata Location)
                    </label>
                    <input
                      type="text"
                      value={formData.base_uri}
                      onChange={(e) => setFormData({...formData, base_uri: e.target.value})}
                      placeholder="https://api.example.com/metadata/"
                      className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                    />
                  </div>
                )}

                {/* Deploy Button */}
                <button
                  type="submit"
                  disabled={deploying}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
                >
                  {deploying ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Deploying Contract...</span>
                    </>
                  ) : (
                    <>
                      <span>🚀</span>
                      <span>Deploy Contract</span>
                    </>
                  )}
                </button>
              </form>

              {/* Deployment Result */}
              {deploymentResult && (
                <div className={`mt-6 p-4 rounded-lg ${deploymentResult.success ? 'bg-green-900/50 border-2 border-green-500' : 'bg-red-900/50 border-2 border-red-500'}`}>
                  <h3 className="text-lg font-bold text-white mb-2">
                    {deploymentResult.success ? '✅ Deployment Successful!' : '❌ Deployment Failed'}
                  </h3>
                  {deploymentResult.success ? (
                    <div className="space-y-2 text-sm text-gray-300">
                      <p><strong>Contract ID:</strong> {deploymentResult.contract_id}</p>
                      <p><strong>Contract Address:</strong> <code className="bg-gray-700 px-2 py-1 rounded">{deploymentResult.contract_address}</code></p>
                      <p><strong>Transaction Hash:</strong> <code className="bg-gray-700 px-2 py-1 rounded">{deploymentResult.transaction_hash}</code></p>
                      <p><strong>Gas Used:</strong> {deploymentResult.gas_used?.toLocaleString()}</p>
                      <p><strong>Cost:</strong> {deploymentResult.deployment_cost_eth} ETH</p>
                      <p><strong>Block Number:</strong> {deploymentResult.block_number}</p>
                      <a 
                        href={`https://etherscan.io/tx/${deploymentResult.transaction_hash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block mt-2 text-blue-400 hover:text-blue-300"
                      >
                        View on Etherscan →
                      </a>
                    </div>
                  ) : (
                    <p className="text-red-300">{deploymentResult.error}</p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Info Panel */}
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">📝 Contract Types</h3>
              <div className="space-y-4 text-sm text-gray-300">
                <div>
                  <div className="font-semibold text-purple-400">ERC-20 Token</div>
                  <div>Fungible tokens like cryptocurrencies</div>
                </div>
                <div>
                  <div className="font-semibold text-purple-400">ERC-721 NFT</div>
                  <div>Non-fungible tokens, unique digital assets</div>
                </div>
                <div>
                  <div className="font-semibold text-purple-400">ERC-1155</div>
                  <div>Multi-token standard (fungible + non-fungible)</div>
                </div>
                <div>
                  <div className="font-semibold text-purple-400">Royalty Splitter</div>
                  <div>Automatically distribute royalties to multiple recipients</div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">⚠️ Important Notes</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">⚡</span>
                  <span>Deploying on Ethereum Mainnet requires ETH for gas fees</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">🔒</span>
                  <span>Contract deployment is permanent and cannot be undone</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">📝</span>
                  <span>Ensure all contract details are correct before deploying</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400">💰</span>
                  <span>Gas costs vary based on network congestion</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Deployed Contracts List */}
        <div className="mt-8 bg-gray-800 rounded-xl shadow-xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Deployed Contracts</h2>
            <button
              onClick={fetchDeployedContracts}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              🔄 Refresh
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
            </div>
          ) : deployedContracts.length === 0 ? (
            <p className="text-gray-400 text-center py-8">No contracts deployed yet</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {deployedContracts.map((contract, index) => (
                <div key={index} className="bg-gray-700 rounded-lg p-4 border-2 border-purple-500/30 hover:border-purple-500 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-bold text-white">{contract.contract_name}</h3>
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                      {contract.status}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm text-gray-300">
                    <p><strong>Type:</strong> {contract.contract_type.toUpperCase()}</p>
                    <p><strong>Symbol:</strong> {contract.contract_symbol || 'N/A'}</p>
                    <p><strong>Network:</strong> {contract.network}</p>
                    <p className="truncate"><strong>Address:</strong> 
                      <code className="text-xs">{contract.contract_address?.substring(0, 20)}...</code>
                    </p>
                    <p><strong>Gas Used:</strong> {contract.gas_used?.toLocaleString()}</p>
                    <p><strong>Cost:</strong> {contract.deployment_cost_eth} ETH</p>
                    <p><strong>Deployed:</strong> {new Date(contract.deployed_at).toLocaleDateString()}</p>
                  </div>
                  <a 
                    href={`https://etherscan.io/address/${contract.contract_address}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-3 text-blue-400 hover:text-blue-300 text-sm"
                  >
                    View on Etherscan →
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ==================== TRANSACTION HISTORY VIEWER ====================

export const TransactionHistoryViewer = () => {
  const [address, setAddress] = useState('');
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [currentAddress, setCurrentAddress] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    // Load configured wallet address
    const configuredAddress = localStorage.getItem('ethereum_wallet_address');
    if (configuredAddress) {
      setAddress(configuredAddress);
    }
  }, []);

  const fetchTransactions = async (walletAddress = address) => {
    if (!walletAddress) {
      alert('Please enter an Ethereum address');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API}/api/ethereum/advanced/transactions/${walletAddress}`);
      if (response.ok) {
        const data = await response.json();
        setTransactions(data.transactions || []);
        setTotalCount(data.total_count || 0);
        setCurrentAddress(walletAddress);
      } else {
        alert('Error fetching transactions');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error fetching transactions');
    } finally {
      setLoading(false);
    }
  };

  const filteredTransactions = transactions.filter(tx => {
    if (filterStatus !== 'all' && tx.status !== filterStatus) return false;
    if (filterType === 'sent' && tx.from_address.toLowerCase() !== currentAddress.toLowerCase()) return false;
    if (filterType === 'received' && tx.to_address.toLowerCase() !== currentAddress.toLowerCase()) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">📜 Transaction History</h1>
          <p className="text-gray-400">View Ethereum transaction history for any wallet</p>
        </div>

        {/* Search Bar */}
        <div className="bg-gray-800 rounded-xl shadow-xl p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="Enter Ethereum address (0x...)"
              className="flex-1 px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
            <button
              onClick={() => fetchTransactions()}
              disabled={loading}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 text-white font-semibold rounded-lg transition-all"
            >
              {loading ? 'Loading...' : 'Search'}
            </button>
          </div>
        </div>

        {/* Filters and Stats */}
        {currentAddress && (
          <div className="bg-gray-800 rounded-xl shadow-xl p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-gray-700 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Total Transactions</div>
                <div className="text-3xl font-bold text-white">{totalCount}</div>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Filtered Results</div>
                <div className="text-3xl font-bold text-white">{filteredTransactions.length}</div>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <div className="text-gray-400 text-sm mb-1">Current Address</div>
                <div className="text-sm text-white truncate">{currentAddress}</div>
              </div>
            </div>

            <div className="flex flex-wrap gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Filter by Type</label>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Transactions</option>
                  <option value="sent">Sent</option>
                  <option value="received">Received</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Filter by Status</label>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="success">Success</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Transactions List */}
        <div className="bg-gray-800 rounded-xl shadow-xl p-6">
          <h2 className="text-2xl font-bold text-white mb-6">Transactions</h2>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-400 mt-4">Loading transactions...</p>
            </div>
          ) : filteredTransactions.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400">
                {currentAddress ? 'No transactions found for this address' : 'Enter an address to view transactions'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredTransactions.map((tx, index) => (
                <div key={index} className="bg-gray-700 rounded-lg p-4 border-2 border-blue-500/30 hover:border-blue-500 transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-2">
                      <span className={`text-2xl ${tx.from_address.toLowerCase() === currentAddress.toLowerCase() ? '📤' : '📥'}`}>
                        {tx.from_address.toLowerCase() === currentAddress.toLowerCase() ? '📤' : '📥'}
                      </span>
                      <span className="font-bold text-white">
                        {tx.from_address.toLowerCase() === currentAddress.toLowerCase() ? 'Sent' : 'Received'}
                      </span>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      tx.status === 'success' 
                        ? 'bg-green-500/20 text-green-400' 
                        : 'bg-red-500/20 text-red-400'
                    }`}>
                      {tx.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300">
                    <div>
                      <div className="text-gray-400 mb-1">Transaction Hash</div>
                      <code className="text-xs break-all">{tx.transaction_hash}</code>
                    </div>
                    <div>
                      <div className="text-gray-400 mb-1">Value</div>
                      <div className="font-semibold text-white">{tx.value_eth} ETH</div>
                    </div>
                    <div>
                      <div className="text-gray-400 mb-1">From</div>
                      <code className="text-xs break-all">{tx.from_address}</code>
                    </div>
                    <div>
                      <div className="text-gray-400 mb-1">To</div>
                      <code className="text-xs break-all">{tx.to_address}</code>
                    </div>
                    <div>
                      <div className="text-gray-400 mb-1">Block Number</div>
                      <div>{tx.block_number?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-gray-400 mb-1">Gas Used</div>
                      <div>{tx.gas_used?.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-gray-400 mb-1">Timestamp</div>
                      <div>{new Date(tx.timestamp).toLocaleString()}</div>
                    </div>
                    {tx.confirmations && (
                      <div>
                        <div className="text-gray-400 mb-1">Confirmations</div>
                        <div>{tx.confirmations.toLocaleString()}</div>
                      </div>
                    )}
                  </div>

                  <a 
                    href={`https://etherscan.io/tx/${tx.transaction_hash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-3 text-blue-400 hover:text-blue-300 text-sm"
                  >
                    View on Etherscan →
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ==================== DAO VOTING DASHBOARD ====================

export const DAOVotingDashboard = () => {
  const [activeTab, setActiveTab] = useState('proposals');
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newProposal, setNewProposal] = useState({
    title: '',
    description: '',
    proposal_type: 'feature_request',
    voting_period_days: 7,
    quorum_percentage: 10.0,
    approval_threshold: 51.0
  });
  const [votingAddress, setVotingAddress] = useState('');

  useEffect(() => {
    fetchProposals();
    // Load voter address from configured wallet
    const address = localStorage.getItem('ethereum_wallet_address') || '';
    setVotingAddress(address);
  }, []);

  const fetchProposals = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/ethereum/advanced/dao/proposals`);
      if (response.ok) {
        const data = await response.json();
        setProposals(data.proposals || []);
      }
    } catch (error) {
      console.error('Error fetching proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  const createProposal = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API}/api/ethereum/advanced/dao/create-proposal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newProposal)
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Proposal created successfully! ID: ${data.proposal_id}`);
        setNewProposal({
          title: '',
          description: '',
          proposal_type: 'feature_request',
          voting_period_days: 7,
          quorum_percentage: 10.0,
          approval_threshold: 51.0
        });
        setActiveTab('proposals');
        fetchProposals();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating proposal:', error);
      alert('Error creating proposal');
    } finally {
      setLoading(false);
    }
  };

  const voteOnProposal = async (proposalId, voteChoice) => {
    if (!votingAddress) {
      alert('Please enter your Ethereum address to vote');
      return;
    }

    try {
      const response = await fetch(`${API}/api/ethereum/advanced/dao/vote/${proposalId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vote_choice: voteChoice,
          voting_power: 1.0,
          voter_address: votingAddress
        })
      });

      if (response.ok) {
        alert(`Vote "${voteChoice}" submitted successfully!`);
        fetchProposals();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error voting:', error);
      alert('Error submitting vote');
    }
  };

  const executeProposal = async (proposalId) => {
    try {
      const response = await fetch(`${API}/api/ethereum/advanced/dao/execute/${proposalId}`, {
        method: 'POST'
      });

      if (response.ok) {
        alert('Proposal executed successfully!');
        fetchProposals();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error executing proposal:', error);
      alert('Error executing proposal');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🏛️ DAO Governance</h1>
          <p className="text-gray-400">Participate in platform decisions through decentralized voting</p>
        </div>

        {/* Voter Address */}
        <div className="bg-gray-800 rounded-xl shadow-xl p-4 mb-6">
          <label className="block text-sm text-gray-400 mb-2">Your Voting Address (Required for voting)</label>
          <input
            type="text"
            value={votingAddress}
            onChange={(e) => setVotingAddress(e.target.value)}
            placeholder="Enter your Ethereum address (0x...)"
            className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
          />
        </div>

        {/* Tabs */}
        <div className="bg-gray-800 rounded-xl shadow-xl mb-6">
          <div className="flex border-b border-gray-700">
            {[
              { id: 'proposals', label: 'Active Proposals', icon: '📋' },
              { id: 'create', label: 'Create Proposal', icon: '✨' },
              { id: 'history', label: 'Completed', icon: '📜' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-semibold text-sm transition-colors flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'text-purple-400 border-b-2 border-purple-500 bg-gray-900/50'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div>
          {/* Active Proposals */}
          {activeTab === 'proposals' && (
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
                </div>
              ) : proposals.filter(p => p.status === 'active').length === 0 ? (
                <div className="bg-gray-800 rounded-xl p-12 text-center">
                  <p className="text-gray-400">No active proposals at this time</p>
                </div>
              ) : (
                proposals.filter(p => p.status === 'active').map((proposal) => (
                  <div key={proposal.proposal_id} className="bg-gray-800 rounded-xl p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-white mb-2">{proposal.title}</h3>
                        <p className="text-gray-400 mb-4">{proposal.description}</p>
                        <div className="flex flex-wrap gap-2 mb-4">
                          <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm">
                            {proposal.proposal_type}
                          </span>
                          <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
                            Ends: {new Date(proposal.voting_ends_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Voting Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="bg-gray-700 rounded-lg p-4">
                        <div className="text-green-400 text-2xl font-bold">{proposal.votes_for}</div>
                        <div className="text-gray-400 text-sm">For ({proposal.for_percentage?.toFixed(1)}%)</div>
                      </div>
                      <div className="bg-gray-700 rounded-lg p-4">
                        <div className="text-red-400 text-2xl font-bold">{proposal.votes_against}</div>
                        <div className="text-gray-400 text-sm">Against ({proposal.against_percentage?.toFixed(1)}%)</div>
                      </div>
                      <div className="bg-gray-700 rounded-lg p-4">
                        <div className="text-gray-400 text-2xl font-bold">{proposal.votes_abstain}</div>
                        <div className="text-gray-400 text-sm">Abstain ({proposal.abstain_percentage?.toFixed(1)}%)</div>
                      </div>
                    </div>

                    {/* Progress Bars */}
                    <div className="space-y-2 mb-4">
                      <div>
                        <div className="flex justify-between text-sm text-gray-400 mb-1">
                          <span>Quorum Progress</span>
                          <span>{proposal.quorum_met ? '✅ Met' : '❌ Not Met'}</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-purple-500 h-2 rounded-full transition-all"
                            style={{ width: `${Math.min((proposal.total_voting_power / proposal.quorum_percentage) * 100, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm text-gray-400 mb-1">
                          <span>Approval Progress</span>
                          <span>{proposal.will_pass ? '✅ Passing' : '❌ Not Passing'}</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full transition-all"
                            style={{ width: `${proposal.for_percentage || 0}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    {/* Voting Buttons */}
                    <div className="flex gap-3">
                      <button
                        onClick={() => voteOnProposal(proposal.proposal_id, 'for')}
                        className="flex-1 px-4 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
                      >
                        👍 Vote For
                      </button>
                      <button
                        onClick={() => voteOnProposal(proposal.proposal_id, 'against')}
                        className="flex-1 px-4 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
                      >
                        👎 Vote Against
                      </button>
                      <button
                        onClick={() => voteOnProposal(proposal.proposal_id, 'abstain')}
                        className="flex-1 px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors"
                      >
                        🤷 Abstain
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Create Proposal */}
          {activeTab === 'create' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <div className="bg-gray-800 rounded-xl p-6">
                  <h2 className="text-2xl font-bold text-white mb-6">Create New Proposal</h2>
                  
                  <form onSubmit={createProposal} className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Proposal Title
                      </label>
                      <input
                        type="text"
                        value={newProposal.title}
                        onChange={(e) => setNewProposal({...newProposal, title: e.target.value})}
                        placeholder="Enter a clear, concise title"
                        required
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Description
                      </label>
                      <textarea
                        value={newProposal.description}
                        onChange={(e) => setNewProposal({...newProposal, description: e.target.value})}
                        placeholder="Provide detailed information about your proposal"
                        required
                        rows="6"
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Proposal Type
                      </label>
                      <select
                        value={newProposal.proposal_type}
                        onChange={(e) => setNewProposal({...newProposal, proposal_type: e.target.value})}
                        className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                      >
                        <option value="feature_request">Feature Request</option>
                        <option value="royalty_change">Royalty Adjustment</option>
                        <option value="platform_addition">Platform Addition</option>
                        <option value="policy_change">Policy Change</option>
                        <option value="treasury_allocation">Treasury Allocation</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Voting Period (days)
                        </label>
                        <input
                          type="number"
                          value={newProposal.voting_period_days}
                          onChange={(e) => setNewProposal({...newProposal, voting_period_days: parseInt(e.target.value)})}
                          min="1"
                          max="30"
                          className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Quorum (%)
                        </label>
                        <input
                          type="number"
                          value={newProposal.quorum_percentage}
                          onChange={(e) => setNewProposal({...newProposal, quorum_percentage: parseFloat(e.target.value)})}
                          min="1"
                          max="100"
                          step="0.1"
                          className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Approval Threshold (%)
                        </label>
                        <input
                          type="number"
                          value={newProposal.approval_threshold}
                          onChange={(e) => setNewProposal({...newProposal, approval_threshold: parseFloat(e.target.value)})}
                          min="1"
                          max="100"
                          step="0.1"
                          className="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-all"
                    >
                      {loading ? 'Creating...' : '✨ Create Proposal'}
                    </button>
                  </form>
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">📝 Guidelines</h3>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>Be clear and specific about what you're proposing</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>Provide detailed reasoning and expected benefits</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>Consider the impact on all platform stakeholders</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>Include relevant data or examples when possible</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Completed Proposals */}
          {activeTab === 'history' && (
            <div className="space-y-4">
              {proposals.filter(p => p.status !== 'active').map((proposal) => (
                <div key={proposal.proposal_id} className="bg-gray-800 rounded-xl p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-white mb-2">{proposal.title}</h3>
                      <p className="text-gray-400 mb-4">{proposal.description}</p>
                    </div>
                    <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
                      proposal.status === 'executed' 
                        ? 'bg-green-500/20 text-green-400' 
                        : proposal.status === 'rejected'
                        ? 'bg-red-500/20 text-red-400'
                        : 'bg-gray-500/20 text-gray-400'
                    }`}>
                      {proposal.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                    <div className="bg-gray-700 rounded p-3">
                      <div className="text-gray-400">For</div>
                      <div className="text-green-400 font-bold">{proposal.votes_for}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-3">
                      <div className="text-gray-400">Against</div>
                      <div className="text-red-400 font-bold">{proposal.votes_against}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-3">
                      <div className="text-gray-400">Abstain</div>
                      <div className="text-gray-400 font-bold">{proposal.votes_abstain}</div>
                    </div>
                    <div className="bg-gray-700 rounded p-3">
                      <div className="text-gray-400">Created</div>
                      <div className="text-white">{new Date(proposal.created_at).toLocaleDateString()}</div>
                    </div>
                  </div>

                  {proposal.status === 'ended' && proposal.will_pass && !proposal.executed && (
                    <button
                      onClick={() => executeProposal(proposal.proposal_id)}
                      className="mt-4 px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
                    >
                      ⚡ Execute Proposal
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default {
  ContractDeploymentUI,
  TransactionHistoryViewer,
  DAOVotingDashboard
};
