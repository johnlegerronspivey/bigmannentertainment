import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://label-network-1.preview.emergentagent.com';

// Global error handler utility
const handleApiError = (error, context) => {
  console.error(`Error in ${context}:`, error);
  
  if (error.response?.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    return;
  }
  
  console.error('API Error:', error.response?.data?.message || error.message || 'Unknown error');
};

// Safe API response handler
const handleApiResponse = (response, successCallback, errorMessage = 'API call failed') => {
  if (response?.data?.success) {
    if (successCallback) successCallback(response.data);
    return true;
  } else {
    console.error(errorMessage, response?.data?.message || 'Unknown error');
    return false;
  }
};

// Real-Time Transaction Processing Dashboard
const TransactionDashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [recentCalculations, setRecentCalculations] = useState([]);
  const [systemStats, setSystemStats] = useState({});
  const [newTransaction, setNewTransaction] = useState({
    asset_id: '',
    platform: '',
    territory: 'US',
    revenue_source: 'streaming',
    monetization_type: 'subscription',
    gross_revenue: '',
    currency: 'USD'
  });
  const [loading, setLoading] = useState(false);

  const revenueSourceOptions = [
    { value: 'streaming', label: 'Streaming' },
    { value: 'download', label: 'Digital Download' },
    { value: 'social_media', label: 'Social Media' },
    { value: 'sync_license', label: 'Sync License' },
    { value: 'broadcast', label: 'Broadcasting' },
    { value: 'ad_impression', label: 'Ad Impression' }
  ];

  const monetizationTypes = [
    { value: 'ad_supported', label: 'Ad-Supported' },
    { value: 'subscription', label: 'Subscription' },
    { value: 'purchase', label: 'Purchase' },
    { value: 'sync_fee', label: 'Sync License Fee' },
    { value: 'performance_royalty', label: 'Performance Royalty' }
  ];

  const fetchSystemStats = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await axios.get(
        `${API}/api/royalty-engine/status/comprehensive`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        setSystemStats(data.status);
      });
    } catch (error) {
      handleApiError(error, 'fetchSystemStats');
    }
  };

  const processTransaction = async () => {
    if (!newTransaction.asset_id || !newTransaction.gross_revenue) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const transactionData = {
        ...newTransaction,
        gross_revenue: parseFloat(newTransaction.gross_revenue),
        timestamp: new Date().toISOString()
      };

      const response = await axios.post(
        `${API}/api/royalty-engine/events/process`,
        transactionData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        alert(`Transaction processed successfully! Total royalty: $${data.total_royalty.toFixed(2)}`);
        setNewTransaction({
          asset_id: '',
          platform: '',
          territory: 'US',
          revenue_source: 'streaming',
          monetization_type: 'subscription',
          gross_revenue: '',
          currency: 'USD'
        });
        fetchSystemStats();
      });
    } catch (error) {
      handleApiError(error, 'processTransaction');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemStats();
    const interval = setInterval(fetchSystemStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">💰 Real-Time Transaction Processing</h3>
        
        {/* System Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium text-blue-800">Today's Events</h4>
            <p className="text-2xl font-bold text-blue-900">
              {systemStats.transaction_events?.last_24h || 0}
            </p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-medium text-green-800">Calculations</h4>
            <p className="text-2xl font-bold text-green-900">
              {systemStats.royalty_calculations?.last_24h || 0}
            </p>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <h4 className="font-medium text-purple-800">Pending Payouts</h4>
            <p className="text-2xl font-bold text-purple-900">
              {(systemStats.pending_payouts?.crypto || 0) + (systemStats.pending_payouts?.traditional || 0)}
            </p>
          </div>
          
          <div className="bg-orange-50 p-4 rounded-lg">
            <h4 className="font-medium text-orange-800">Active Contracts</h4>
            <p className="text-2xl font-bold text-orange-900">
              {systemStats.contract_terms?.active || 0}
            </p>
          </div>
        </div>

        {/* Transaction Input Form */}
        <div className="border-t pt-6">
          <h4 className="font-medium mb-4">Process New Transaction</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Asset ID"
              value={newTransaction.asset_id}
              onChange={(e) => setNewTransaction({...newTransaction, asset_id: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <input
              type="text"
              placeholder="Platform (e.g., Spotify)"
              value={newTransaction.platform}
              onChange={(e) => setNewTransaction({...newTransaction, platform: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <select
              value={newTransaction.territory}
              onChange={(e) => setNewTransaction({...newTransaction, territory: e.target.value})}
              className="border rounded-lg px-3 py-2"
            >
              <option value="US">United States</option>
              <option value="CA">Canada</option>
              <option value="GB">United Kingdom</option>
              <option value="DE">Germany</option>
              <option value="FR">France</option>
              <option value="AU">Australia</option>
            </select>
            
            <select
              value={newTransaction.revenue_source}
              onChange={(e) => setNewTransaction({...newTransaction, revenue_source: e.target.value})}
              className="border rounded-lg px-3 py-2"
            >
              {revenueSourceOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
            
            <select
              value={newTransaction.monetization_type}
              onChange={(e) => setNewTransaction({...newTransaction, monetization_type: e.target.value})}
              className="border rounded-lg px-3 py-2"
            >
              {monetizationTypes.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
            
            <input
              type="number"
              step="0.01"
              placeholder="Gross Revenue ($)"
              value={newTransaction.gross_revenue}
              onChange={(e) => setNewTransaction({...newTransaction, gross_revenue: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
          </div>
          
          <button
            onClick={processTransaction}
            disabled={loading || !newTransaction.asset_id || !newTransaction.gross_revenue}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Process Transaction'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Contract Management Component
const ContractManagement = () => {
  const [contracts, setContracts] = useState([]);
  const [contributorSplits, setContributorSplits] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState('');
  const [newContract, setNewContract] = useState({
    asset_id: '',
    contract_type: 'percentage',
    base_rate: '',
    minimum_payout: '0.01',
    effective_date: new Date().toISOString().split('T')[0]
  });
  const [newSplit, setNewSplit] = useState({
    asset_id: '',
    contributor_id: '',
    contributor_type: 'artist',
    split_percentage: '',
    payout_method: 'ach_batch',
    wallet_address: ''
  });

  const contractTypes = [
    { value: 'percentage', label: 'Percentage-based' },
    { value: 'fixed_fee', label: 'Fixed Fee' },
    { value: 'tiered_rates', label: 'Tiered Rates' },
    { value: 'minimum_guarantee', label: 'Minimum Guarantee' }
  ];

  const contributorTypes = [
    { value: 'artist', label: 'Artist' },
    { value: 'producer', label: 'Producer' },
    { value: 'songwriter', label: 'Songwriter' },
    { value: 'label', label: 'Record Label' },
    { value: 'publisher', label: 'Publisher' }
  ];

  const payoutMethods = [
    { value: 'crypto_instant', label: 'Crypto Instant' },
    { value: 'stablecoin', label: 'Stablecoin' },
    { value: 'ach_batch', label: 'ACH (Monthly)' },
    { value: 'wire_transfer', label: 'Wire Transfer' },
    { value: 'paypal', label: 'PayPal' }
  ];

  const createContract = async () => {
    if (!newContract.asset_id || !newContract.base_rate) return;

    try {
      const token = localStorage.getItem('token');
      const contractData = {
        ...newContract,
        base_rate: parseFloat(newContract.base_rate),
        minimum_payout: parseFloat(newContract.minimum_payout),
        effective_date: new Date(newContract.effective_date).toISOString(),
        active: true
      };

      const response = await axios.post(
        `${API}/api/royalty-engine/contracts/create`,
        contractData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        alert('Contract created successfully!');
        setNewContract({
          asset_id: '',
          contract_type: 'percentage',
          base_rate: '',
          minimum_payout: '0.01',
          effective_date: new Date().toISOString().split('T')[0]
        });
      });
    } catch (error) {
      handleApiError(error, 'createContract');
    }
  };

  const createContributorSplit = async () => {
    if (!newSplit.asset_id || !newSplit.contributor_id || !newSplit.split_percentage) return;

    try {
      const token = localStorage.getItem('token');
      const splitData = {
        ...newSplit,
        split_percentage: parseFloat(newSplit.split_percentage),
        minimum_payout_threshold: 1.00,
        tax_jurisdiction: 'US',
        active: true
      };

      const response = await axios.post(
        `${API}/api/royalty-engine/splits/create`,
        splitData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        alert('Contributor split created successfully!');
        setNewSplit({
          asset_id: '',
          contributor_id: '',
          contributor_type: 'artist',
          split_percentage: '',
          payout_method: 'ach_batch',
          wallet_address: ''
        });
        if (selectedAsset) {
          fetchContributorSplits(selectedAsset);
        }
      });
    } catch (error) {
      handleApiError(error, 'createContributorSplit');
    }
  };

  const fetchContractTerms = async (assetId) => {
    if (!assetId) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/royalty-engine/contracts/${assetId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        setContracts([data.contract]);
      });
    } catch (error) {
      if (error.response?.status !== 404) {
        handleApiError(error, 'fetchContractTerms');
      }
      setContracts([]);
    }
  };

  const fetchContributorSplits = async (assetId) => {
    if (!assetId) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/royalty-engine/splits/${assetId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        setContributorSplits(data.splits || []);
      });
    } catch (error) {
      handleApiError(error, 'fetchContributorSplits');
      setContributorSplits([]);
    }
  };

  const handleAssetSelection = (assetId) => {
    setSelectedAsset(assetId);
    if (assetId) {
      fetchContractTerms(assetId);
      fetchContributorSplits(assetId);
    } else {
      setContracts([]);
      setContributorSplits([]);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">📋 Contract & Split Management</h3>
        
        {/* Asset Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Select Asset to Manage</label>
          <input
            type="text"
            placeholder="Enter Asset ID"
            value={selectedAsset}
            onChange={(e) => handleAssetSelection(e.target.value)}
            className="border rounded-lg px-3 py-2 w-full md:w-96"
          />
        </div>

        {/* Contract Creation */}
        <div className="border-b pb-6 mb-6">
          <h4 className="font-medium mb-4">Create Contract Terms</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Asset ID"
              value={newContract.asset_id}
              onChange={(e) => setNewContract({...newContract, asset_id: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <select
              value={newContract.contract_type}
              onChange={(e) => setNewContract({...newContract, contract_type: e.target.value})}
              className="border rounded-lg px-3 py-2"
            >
              {contractTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
            
            <input
              type="number"
              step="0.01"
              placeholder="Base Rate (%)"
              value={newContract.base_rate}
              onChange={(e) => setNewContract({...newContract, base_rate: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <input
              type="number"
              step="0.01"
              placeholder="Minimum Payout ($)"
              value={newContract.minimum_payout}
              onChange={(e) => setNewContract({...newContract, minimum_payout: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <input
              type="date"
              value={newContract.effective_date}
              onChange={(e) => setNewContract({...newContract, effective_date: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
          </div>
          
          <button
            onClick={createContract}
            disabled={!newContract.asset_id || !newContract.base_rate}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Create Contract
          </button>
        </div>

        {/* Contributor Split Creation */}
        <div className="border-b pb-6 mb-6">
          <h4 className="font-medium mb-4">Add Contributor Split</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Asset ID"
              value={newSplit.asset_id}
              onChange={(e) => setNewSplit({...newSplit, asset_id: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <input
              type="text"
              placeholder="Contributor ID/Name"
              value={newSplit.contributor_id}
              onChange={(e) => setNewSplit({...newSplit, contributor_id: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <select
              value={newSplit.contributor_type}
              onChange={(e) => setNewSplit({...newSplit, contributor_type: e.target.value})}
              className="border rounded-lg px-3 py-2"
            >
              {contributorTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
            
            <input
              type="number"
              step="0.01"
              placeholder="Split Percentage"
              value={newSplit.split_percentage}
              onChange={(e) => setNewSplit({...newSplit, split_percentage: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <select
              value={newSplit.payout_method}
              onChange={(e) => setNewSplit({...newSplit, payout_method: e.target.value})}
              className="border rounded-lg px-3 py-2"
            >
              {payoutMethods.map(method => (
                <option key={method.value} value={method.value}>{method.label}</option>
              ))}
            </select>
            
            <input
              type="text"
              placeholder="Wallet Address (for crypto)"
              value={newSplit.wallet_address}
              onChange={(e) => setNewSplit({...newSplit, wallet_address: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
          </div>
          
          <button
            onClick={createContributorSplit}
            disabled={!newSplit.asset_id || !newSplit.contributor_id || !newSplit.split_percentage}
            className="mt-4 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            Add Contributor
          </button>
        </div>

        {/* Display Current Splits */}
        {selectedAsset && contributorSplits.length > 0 && (
          <div>
            <h4 className="font-medium mb-4">Current Contributors for {selectedAsset}</h4>
            <div className="space-y-2">
              {contributorSplits.map((split, index) => (
                <div key={index} className="border rounded-lg p-3 bg-gray-50">
                  <div className="flex justify-between items-center">
                    <div>
                      <h5 className="font-medium">{split.contributor_id}</h5>
                      <p className="text-sm text-gray-600">
                        {split.contributor_type} • {split.split_percentage}% • {split.payout_method}
                      </p>
                      {split.wallet_address && (
                        <p className="text-xs text-gray-500">Wallet: {split.wallet_address}</p>
                      )}
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${split.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {split.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              ))}
              
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  Total Split: {contributorSplits.reduce((sum, split) => sum + parseFloat(split.split_percentage), 0).toFixed(2)}%
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Payout Management Component
const PayoutManagement = () => {
  const [pendingPayouts, setPendingPayouts] = useState([]);
  const [payoutStats, setPayoutStats] = useState({});
  const [selectedMethod, setSelectedMethod] = useState('all');
  const [processing, setProcessing] = useState({});

  const fetchPendingPayouts = async () => {
    try {
      const token = localStorage.getItem('token');
      const methodParam = selectedMethod !== 'all' ? `payout_method=${selectedMethod}&` : '';
      
      const response = await axios.get(
        `${API}/api/royalty-engine/payouts/pending?${methodParam}limit=100`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        setPendingPayouts(data.payouts || []);
        setPayoutStats(data.summary || {});
      });
    } catch (error) {
      handleApiError(error, 'fetchPendingPayouts');
    }
  };

  const processPayout = async (payoutId) => {
    setProcessing(prev => ({...prev, [payoutId]: true}));
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/royalty-engine/payouts/${payoutId}/process`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        alert('Payout processing initiated successfully!');
        fetchPendingPayouts(); // Refresh the list
      });
    } catch (error) {
      handleApiError(error, 'processPayout');
    } finally {
      setProcessing(prev => ({...prev, [payoutId]: false}));
    }
  };

  useEffect(() => {
    fetchPendingPayouts();
  }, [selectedMethod]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">💳 Payout Management</h3>
        
        {/* Payout Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-purple-50 p-4 rounded-lg">
            <h4 className="font-medium text-purple-800">Total Pending</h4>
            <p className="text-2xl font-bold text-purple-900">
              {payoutStats.total_payouts || 0}
            </p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-medium text-green-800">Total Amount</h4>
            <p className="text-2xl font-bold text-green-900">
              ${(payoutStats.total_amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}
            </p>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium text-blue-800">Crypto Payouts</h4>
            <p className="text-2xl font-bold text-blue-900">
              {(payoutStats.by_method?.crypto_instant?.count || 0) + (payoutStats.by_method?.stablecoin?.count || 0)}
            </p>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Filter by Payout Method</label>
          <select
            value={selectedMethod}
            onChange={(e) => setSelectedMethod(e.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="all">All Methods</option>
            <option value="crypto_instant">Crypto Instant</option>
            <option value="stablecoin">Stablecoin</option>
            <option value="ach_batch">ACH Batch</option>
            <option value="wire_transfer">Wire Transfer</option>
            <option value="paypal">PayPal</option>
          </select>
        </div>

        {/* Pending Payouts List */}
        <div>
          <h4 className="font-medium mb-4">Pending Payouts ({pendingPayouts.length})</h4>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {pendingPayouts.length > 0 ? pendingPayouts.map((payout, index) => (
              <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div>
                    <h5 className="font-medium">{payout.contributor_id}</h5>
                    <p className="text-sm text-gray-600">
                      Amount: ${parseFloat(payout.amount).toFixed(2)} • Method: {payout.payout_method}
                    </p>
                    <p className="text-xs text-gray-500">
                      Created: {new Date(payout.created_at).toLocaleString()} • 
                      Scheduled: {new Date(payout.scheduled_at).toLocaleString()}
                    </p>
                    {payout.wallet_address && (
                      <p className="text-xs text-gray-500">
                        Wallet: {payout.wallet_address}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      payout.status === 'pending_crypto' ? 'bg-blue-100 text-blue-800' :
                      payout.status === 'pending_batch' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {payout.status}
                    </span>
                    
                    <button
                      onClick={() => processPayout(payout.id)}
                      disabled={processing[payout.id]}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50"
                    >
                      {processing[payout.id] ? 'Processing...' : 'Process'}
                    </button>
                  </div>
                </div>
              </div>
            )) : (
              <div className="text-center py-8 text-gray-500">
                <p>No pending payouts found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Analytics and Forecasting Component
const RoyaltyAnalytics = () => {
  const [selectedAsset, setSelectedAsset] = useState('');
  const [analyticsPeriod, setAnalyticsPeriod] = useState(30);
  const [assetSummary, setAssetSummary] = useState({});
  const [forecast, setForecast] = useState({});
  const [loading, setLoading] = useState(false);

  const fetchAssetSummary = async () => {
    if (!selectedAsset) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/royalty-engine/analytics/asset/${selectedAsset}/summary?days=${analyticsPeriod}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        setAssetSummary(data);
      });
    } catch (error) {
      handleApiError(error, 'fetchAssetSummary');
    } finally {
      setLoading(false);
    }
  };

  const fetchForecast = async () => {
    if (!selectedAsset) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/royalty-engine/analytics/forecast/${selectedAsset}?months_ahead=6`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        setForecast(data.forecast);
      });
    } catch (error) {
      handleApiError(error, 'fetchForecast');
    }
  };

  const handleAssetChange = (assetId) => {
    setSelectedAsset(assetId);
    if (assetId) {
      fetchAssetSummary();
      fetchForecast();
    } else {
      setAssetSummary({});
      setForecast({});
    }
  };

  useEffect(() => {
    if (selectedAsset) {
      fetchAssetSummary();
      fetchForecast();
    }
  }, [analyticsPeriod]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">📈 Royalty Analytics & Forecasting</h3>
        
        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-2">Asset ID</label>
            <input
              type="text"
              placeholder="Enter Asset ID for analysis"
              value={selectedAsset}
              onChange={(e) => handleAssetChange(e.target.value)}
              className="border rounded-lg px-3 py-2 w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Analysis Period</label>
            <select
              value={analyticsPeriod}
              onChange={(e) => setAnalyticsPeriod(parseInt(e.target.value))}
              className="border rounded-lg px-3 py-2 w-full"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
        </div>

        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-500">Loading analytics...</p>
          </div>
        )}

        {/* Asset Summary */}
        {assetSummary.summary && (
          <div className="mb-6">
            <h4 className="font-medium mb-4">Performance Summary</h4>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h5 className="font-medium text-blue-800">Total Revenue</h5>
                <p className="text-xl font-bold text-blue-900">
                  ${assetSummary.summary.total_revenue?.toFixed(2) || '0.00'}
                </p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h5 className="font-medium text-green-800">Total Royalties</h5>
                <p className="text-xl font-bold text-green-900">
                  ${assetSummary.summary.total_royalties?.toFixed(2) || '0.00'}
                </p>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <h5 className="font-medium text-purple-800">Events</h5>
                <p className="text-xl font-bold text-purple-900">
                  {assetSummary.summary.total_events?.toLocaleString() || 0}
                </p>
              </div>
              
              <div className="bg-orange-50 p-4 rounded-lg">
                <h5 className="font-medium text-orange-800">Royalty Rate</h5>
                <p className="text-xl font-bold text-orange-900">
                  {assetSummary.summary.royalty_rate?.toFixed(1) || 0}%
                </p>
              </div>
            </div>

            {/* Revenue Breakdown */}
            {assetSummary.breakdown && (
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-medium mb-3">Revenue by Source</h5>
                  <div className="space-y-2">
                    {Object.entries(assetSummary.breakdown.by_revenue_source).map(([source, amount]) => (
                      <div key={source} className="flex justify-between items-center">
                        <span className="capitalize text-sm">{source.replace('_', ' ')}</span>
                        <span className="font-medium">${amount.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h5 className="font-medium mb-3">Revenue by Platform</h5>
                  <div className="space-y-2">
                    {Object.entries(assetSummary.breakdown.by_platform).map(([platform, amount]) => (
                      <div key={platform} className="flex justify-between items-center">
                        <span className="text-sm">{platform}</span>
                        <span className="font-medium">${amount.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Forecast */}
        {forecast.forecast && (
          <div className="border-t pt-6">
            <h4 className="font-medium mb-4">6-Month Forecast</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium text-gray-800">Historical Average</h5>
                <p className="text-lg font-bold text-gray-900">
                  ${forecast.historical_average?.toFixed(2) || '0.00'}
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium text-gray-800">Trend Direction</h5>
                <p className="text-lg font-bold text-gray-900 capitalize">
                  {forecast.trend_direction || 'stable'}
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium text-gray-800">Confidence</h5>
                <p className="text-lg font-bold text-gray-900">
                  {(forecast.confidence * 100)?.toFixed(0) || 0}%
                </p>
              </div>
            </div>
            
            <div className="space-y-2">
              {forecast.forecast.map((month, index) => (
                <div key={index} className="flex justify-between items-center border rounded p-3">
                  <span className="font-medium">{month.month}</span>
                  <div className="text-right">
                    <div className="font-bold">${month.projected_revenue?.toFixed(2)}</div>
                    <div className="text-sm text-gray-500">
                      {(month.confidence * 100)?.toFixed(0)}% confidence
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Main Real-Time Royalty Dashboard
export const RealTimeRoyaltyDashboard = () => {
  const [activeTab, setActiveTab] = useState('transactions');
  const [blockchainStatus, setBlockchainStatus] = useState({});

  const tabs = [
    { id: 'transactions', name: 'Transaction Processing', icon: '💰', component: TransactionDashboard },
    { id: 'contracts', name: 'Contract Management', icon: '📋', component: ContractManagement },
    { id: 'payouts', name: 'Payout Management', icon: '💳', component: PayoutManagement },
    { id: 'analytics', name: 'Analytics & Forecasting', icon: '📈', component: RoyaltyAnalytics }
  ];

  const fetchBlockchainStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/royalty-engine/health`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      handleApiResponse(response, (data) => {
        setBlockchainStatus(data.services);
      });
    } catch (error) {
      // Don't show error for this optional feature
      console.log('Blockchain status not available');
    }
  };

  useEffect(() => {
    fetchBlockchainStatus();
  }, []);

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || TransactionDashboard;

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Real-Time Royalty Engine</h1>
        <p className="text-gray-600">Enterprise-grade royalty calculation and distribution with blockchain integration</p>
      </div>

      {/* System Health Status */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">System Health Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
          {Object.entries(blockchainStatus).map(([service, status]) => (
            <div key={service} className="text-center">
              <div className="font-medium capitalize">{service.replace('_', ' ')}</div>
              <div className={`text-xs mt-1 px-2 py-1 rounded ${status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                {status || 'unknown'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Active Tab Content */}
      <ActiveComponent />
    </div>
  );
};

export default RealTimeRoyaltyDashboard;