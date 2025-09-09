import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// License Builder Component
export const LicenseBuilder = ({ assetId, onComplete }) => {
  const [formData, setFormData] = useState({
    blockchain_network: 'ethereum',
    contract_standard: 'erc721',
    license_type: 'non_exclusive',
    base_price: 100,
    royalty_splits: {
      agency: 0.7,
      talent: 0.25,
      platform: 0.05
    },
    usage_terms: {
      commercial_use: false,
      editorial_use: true,
      web_use: true,
      print_use: false
    },
    exclusivity: false,
    duration_months: null,
    territory: ['worldwide']
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/agency/license-contract`, {
        asset_id: assetId,
        ...formData
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (onComplete) {
        onComplete(response.data);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create license contract');
    } finally {
      setLoading(false);
    }
  };

  const updateRoyaltySplit = (recipient, value) => {
    const newSplits = { ...formData.royalty_splits };
    newSplits[recipient] = parseFloat(value);
    
    // Ensure splits sum to 1.0
    const total = Object.values(newSplits).reduce((sum, val) => sum + val, 0);
    if (Math.abs(total - 1.0) > 0.01) {
      setError('Royalty splits must sum to 100%');
      return;
    }
    
    setError('');
    setFormData(prev => ({ ...prev, royalty_splits: newSplits }));
  };

  const updateUsageTerm = (term, value) => {
    setFormData(prev => ({
      ...prev,
      usage_terms: {
        ...prev.usage_terms,
        [term]: value
      }
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold mb-6">Create License Contract</h2>
      
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Blockchain Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">Blockchain Network</label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="ethereum"
                checked={formData.blockchain_network === 'ethereum'}
                onChange={(e) => setFormData(prev => ({ ...prev, blockchain_network: e.target.value }))}
                className="mr-2"
              />
              <span className="text-sm">Ethereum</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="solana"
                checked={formData.blockchain_network === 'solana'}
                onChange={(e) => setFormData(prev => ({ ...prev, blockchain_network: e.target.value }))}
                className="mr-2"
              />
              <span className="text-sm">Solana</span>
            </label>
          </div>
        </div>

        {/* Contract Standard */}
        <div>
          <label className="block text-sm font-medium mb-2">Contract Standard</label>
          <select
            value={formData.contract_standard}
            onChange={(e) => setFormData(prev => ({ ...prev, contract_standard: e.target.value }))}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="erc721">ERC-721 (Unique NFT)</option>
            <option value="erc1155">ERC-1155 (Multi-Edition)</option>
            {formData.blockchain_network === 'solana' && (
              <option value="spl_token">SPL Token</option>
            )}
          </select>
        </div>

        {/* License Type */}
        <div>
          <label className="block text-sm font-medium mb-2">License Type</label>
          <select
            value={formData.license_type}
            onChange={(e) => setFormData(prev => ({ ...prev, license_type: e.target.value }))}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="exclusive">Exclusive License</option>
            <option value="non_exclusive">Non-Exclusive License</option>
            <option value="rights_managed">Rights Managed</option>
            <option value="royalty_free">Royalty Free</option>
          </select>
        </div>

        {/* Pricing */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Base Price (USD)</label>
            <input
              type="number"
              min="1"
              step="0.01"
              value={formData.base_price}
              onChange={(e) => setFormData(prev => ({ ...prev, base_price: parseFloat(e.target.value) }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Duration (months)</label>
            <input
              type="number"
              min="1"
              placeholder="Leave empty for perpetual"
              value={formData.duration_months || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, duration_months: e.target.value ? parseInt(e.target.value) : null }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
        </div>

        {/* Royalty Splits */}
        <div>
          <label className="block text-sm font-medium mb-2">Royalty Splits</label>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Agency</span>
              <div className="flex items-center">
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.royalty_splits.agency}
                  onChange={(e) => updateRoyaltySplit('agency', e.target.value)}
                  className="w-20 border border-gray-300 rounded px-2 py-1 text-sm mr-2"
                />
                <span className="text-sm text-gray-600">({Math.round(formData.royalty_splits.agency * 100)}%)</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Talent</span>
              <div className="flex items-center">
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.royalty_splits.talent}
                  onChange={(e) => updateRoyaltySplit('talent', e.target.value)}
                  className="w-20 border border-gray-300 rounded px-2 py-1 text-sm mr-2"
                />
                <span className="text-sm text-gray-600">({Math.round(formData.royalty_splits.talent * 100)}%)</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Platform</span>
              <div className="flex items-center">
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.01"
                  value={formData.royalty_splits.platform}
                  onChange={(e) => updateRoyaltySplit('platform', e.target.value)}
                  className="w-20 border border-gray-300 rounded px-2 py-1 text-sm mr-2"
                />
                <span className="text-sm text-gray-600">({Math.round(formData.royalty_splits.platform * 100)}%)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Usage Terms */}
        <div>
          <label className="block text-sm font-medium mb-2">Usage Rights</label>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(formData.usage_terms).map(([term, value]) => (
              <label key={term} className="flex items-center">
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => updateUsageTerm(term, e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm capitalize">{term.replace('_', ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Exclusivity */}
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.exclusivity}
              onChange={(e) => setFormData(prev => ({ ...prev, exclusivity: e.target.checked }))}
              className="mr-2"
            />
            <span className="text-sm font-medium">Exclusive License</span>
          </label>
          <p className="text-xs text-gray-600 mt-1">
            Check this box for exclusive licensing rights
          </p>
        </div>

        {/* Submit */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => onComplete && onComplete(null)}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create License Contract'}
          </button>
        </div>
      </form>
    </div>
  );
};

// Smart Contract Viewer
export const SmartContractViewer = ({ contractData }) => {
  const [blockchainInfo, setBlockchainInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (contractData && contractData.contract_address) {
      fetchBlockchainInfo();
    }
  }, [contractData]);

  const fetchBlockchainInfo = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would fetch actual blockchain data
      setBlockchainInfo({
        confirmations: 12,
        gas_used: 245000,
        block_number: 18500000,
        deployed_at: contractData.deployed_at
      });
    } catch (error) {
      console.error('Error fetching blockchain info:', error);
    } finally {
      setLoading(false);
    }
  };

  const getExplorerUrl = () => {
    if (!contractData.contract_address) return null;
    
    switch (contractData.blockchain_network) {
      case 'ethereum':
        return `https://etherscan.io/address/${contractData.contract_address}`;
      case 'solana':
        return `https://explorer.solana.com/address/${contractData.contract_address}`;
      default:
        return null;
    }
  };

  if (!contractData) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
        <p className="text-gray-500">No contract data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Smart Contract Details</h2>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          contractData.status === 'deployed' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-yellow-100 text-yellow-800'
        }`}>
          {contractData.status}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Contract Information */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contract Address</label>
            <div className="flex items-center">
              <code className="text-sm bg-gray-100 px-2 py-1 rounded mr-2 flex-1">
                {contractData.contract_address || 'Not deployed'}
              </code>
              {contractData.contract_address && (
                <button
                  onClick={() => navigator.clipboard.writeText(contractData.contract_address)}
                  className="text-purple-600 hover:text-purple-800"
                >
                  📋
                </button>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Token ID</label>
            <code className="text-sm bg-gray-100 px-2 py-1 rounded block">
              {contractData.token_id || 'Not minted'}
            </code>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Blockchain</label>
            <div className="flex items-center">
              <span className="capitalize text-sm">
                {contractData.blockchain_network}
              </span>
              <span className="ml-2 text-xs text-gray-500">
                ({contractData.contract_standard.toUpperCase()})
              </span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Transaction Hash</label>
            <code className="text-sm bg-gray-100 px-2 py-1 rounded block">
              {contractData.transaction_hash || 'Not available'}
            </code>
          </div>
        </div>

        {/* License Terms */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">License Type</label>
            <span className="text-sm capitalize">
              {contractData.license_type.replace('_', ' ')}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Base Price</label>
            <span className="text-sm font-medium">
              ${contractData.base_price} {contractData.currency || 'USD'}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Territory</label>
            <span className="text-sm">
              {contractData.territory.join(', ')}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Duration</label>
            <span className="text-sm">
              {contractData.duration_months ? `${contractData.duration_months} months` : 'Perpetual'}
            </span>
          </div>
        </div>
      </div>

      {/* Blockchain Info */}
      {blockchainInfo && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-medium mb-4">Blockchain Information</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Confirmations:</span>
              <div className="font-medium">{blockchainInfo.confirmations}</div>
            </div>
            <div>
              <span className="text-gray-600">Gas Used:</span>
              <div className="font-medium">{blockchainInfo.gas_used?.toLocaleString()}</div>
            </div>
            <div>
              <span className="text-gray-600">Block Number:</span>
              <div className="font-medium">{blockchainInfo.block_number?.toLocaleString()}</div>
            </div>
            <div>
              <span className="text-gray-600">Deployed:</span>
              <div className="font-medium">
                {blockchainInfo.deployed_at ? new Date(blockchainInfo.deployed_at).toLocaleDateString() : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200 flex space-x-4">
        {getExplorerUrl() && (
          <a
            href={getExplorerUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
          >
            View on Explorer
          </a>
        )}
        
        {contractData.metadata_uri && (
          <a
            href={contractData.metadata_uri}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 text-sm"
          >
            View Metadata
          </a>
        )}
      </div>
    </div>
  );
};

// Royalty Tracker Component
export const RoyaltyTracker = ({ agencyId }) => {
  const [royaltyData, setRoyaltyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    fetchRoyaltyData();
  }, [timeRange]);

  const fetchRoyaltyData = async () => {
    try {
      setLoading(true);
      // Mock royalty data - in real implementation, fetch from API
      const mockData = {
        total_earned: 2450.75,
        pending_payments: 892.30,
        paid_out: 1558.45,
        recent_payments: [
          {
            id: 1,
            contract_id: 'contract_123',
            amount: 125.50,
            currency: 'USD',
            date: '2024-01-15',
            status: 'completed',
            tx_hash: '0x7a2b...'
          },
          {
            id: 2,
            contract_id: 'contract_456',
            amount: 89.25,
            currency: 'USD',
            date: '2024-01-14',
            status: 'pending',
            tx_hash: null
          }
        ],
        earnings_chart: [
          { date: '2024-01-01', amount: 50 },
          { date: '2024-01-02', amount: 75 },
          { date: '2024-01-03', amount: 120 },
          { date: '2024-01-04', amount: 95 },
          { date: '2024-01-05', amount: 180 },
        ]
      };
      
      setRoyaltyData(mockData);
    } catch (error) {
      console.error('Error fetching royalty data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Royalty Tracker</h2>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="1y">Last year</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">
            ${royaltyData.total_earned.toFixed(2)}
          </div>
          <div className="text-sm text-green-800">Total Earned</div>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-yellow-600">
            ${royaltyData.pending_payments.toFixed(2)}
          </div>
          <div className="text-sm text-yellow-800">Pending Payments</div>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">
            ${royaltyData.paid_out.toFixed(2)}
          </div>
          <div className="text-sm text-blue-800">Paid Out</div>
        </div>
      </div>

      {/* Earnings Chart */}
      <div className="mb-8">
        <h3 className="text-lg font-medium mb-4">Earnings Timeline</h3>
        <div className="h-32 bg-gray-50 border border-gray-200 rounded-lg flex items-end justify-around p-4">
          {royaltyData.earnings_chart.map((point, index) => (
            <div key={index} className="flex flex-col items-center">
              <div
                className="bg-purple-600 rounded-t w-8"
                style={{ height: `${(point.amount / 200) * 80}px` }}
              />
              <div className="text-xs text-gray-600 mt-2">
                {new Date(point.date).getDate()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Payments */}
      <div>
        <h3 className="text-lg font-medium mb-4">Recent Payments</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contract
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Transaction
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {royaltyData.recent_payments.map((payment) => (
                <tr key={payment.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {payment.contract_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${payment.amount.toFixed(2)} {payment.currency}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(payment.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      payment.status === 'completed' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {payment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {payment.tx_hash ? (
                      <a
                        href={`https://etherscan.io/tx/${payment.tx_hash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-600 hover:text-purple-900"
                      >
                        {payment.tx_hash.substring(0, 10)}...
                      </a>
                    ) : (
                      'Pending'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default { LicenseBuilder, SmartContractViewer, RoyaltyTracker };