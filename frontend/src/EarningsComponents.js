import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// Earnings Dashboard Component
export const EarningsDashboard = () => {
  const [earnings, setEarnings] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showPayoutForm, setShowPayoutForm] = useState(false);

  useEffect(() => {
    fetchEarnings();
  }, []);

  const fetchEarnings = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setError('Please log in to view earnings');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API}/api/payments/earnings`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEarnings(data.earnings || {});
        setTransactions(data.recent_transactions || []);
        setError('');
      } else if (response.status === 401) {
        setError('Session expired. Please log in again.');
        localStorage.removeItem('accessToken');
      } else {
        setError('Failed to load earnings data');
      }
    } catch (error) {
      console.error('Earnings fetch error:', error);
      setError('Error loading earnings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) return <div className="text-center py-8">Loading earnings...</div>;
  if (error) return <div className="text-red-500 text-center py-8">{error}</div>;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Earnings Dashboard</h1>
        <button
          onClick={() => setShowPayoutForm(true)}
          disabled={!earnings?.available_balance || earnings.available_balance < earnings.minimum_payout_threshold}
          className="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Request Payout
        </button>
      </div>

      {/* Earnings Summary Cards */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Earnings</h3>
          <p className="text-2xl font-bold text-green-600 mt-2">
            {formatCurrency(earnings?.total_earnings)}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Available Balance</h3>
          <p className="text-2xl font-bold text-blue-600 mt-2">
            {formatCurrency(earnings?.available_balance)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Min payout: {formatCurrency(earnings?.minimum_payout_threshold)}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Pending Balance</h3>
          <p className="text-2xl font-bold text-yellow-600 mt-2">
            {formatCurrency(earnings?.pending_balance)}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Paid Out</h3>
          <p className="text-2xl font-bold text-gray-600 mt-2">
            {formatCurrency(earnings?.total_paid_out)}
          </p>
        </div>
      </div>

      {/* Payout Settings */}
      <div className="bg-white p-6 rounded-lg shadow border mb-8">
        <h2 className="text-xl font-bold mb-4">Payout Settings</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Payout Schedule
            </label>
            <select 
              value={earnings?.payout_schedule || 'monthly'}
              className="w-full border rounded px-3 py-2"
            >
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="on_demand">On Demand Only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Payout Threshold
            </label>
            <input
              type="number"
              value={earnings?.minimum_payout_threshold || 10}
              min="10"
              max="1000"
              step="5"
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
        <div className="mt-4">
          <button className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
            Update Settings
          </button>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white rounded-lg shadow border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold">Recent Earnings</h2>
        </div>
        <div className="overflow-x-auto">
          {transactions.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Media
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Split %
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(transaction.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {transaction.media_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                      {formatCurrency(transaction.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {transaction.split_percentage}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        transaction.status === 'completed' 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {transaction.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-6 text-center text-gray-500">
              No earnings transactions yet. Start uploading content to earn royalties!
            </div>
          )}
        </div>
      </div>

      {/* Payout Request Modal */}
      {showPayoutForm && (
        <PayoutRequestModal
          availableBalance={earnings?.available_balance}
          minThreshold={earnings?.minimum_payout_threshold}
          onClose={() => setShowPayoutForm(false)}
          onSuccess={() => {
            setShowPayoutForm(false);
            fetchEarnings();
          }}
        />
      )}
    </div>
  );
};

// Payout Request Modal Component
const PayoutRequestModal = ({ availableBalance, minThreshold, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    amount: minThreshold || 10,
    payout_method: 'bank_transfer',
    bank_account_id: '',
    wallet_id: ''
  });
  const [bankAccounts, setBankAccounts] = useState([]);
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPayoutMethods();
  }, []);

  const fetchPayoutMethods = async () => {
    try {
      // Fetch bank accounts
      const bankResponse = await fetch(`${API}/api/payments/bank-accounts`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
      });
      if (bankResponse.ok) {
        const bankData = await bankResponse.json();
        setBankAccounts(bankData.accounts);
      }

      // Fetch wallets
      const walletResponse = await fetch(`${API}/api/payments/wallets`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('accessToken')}` }
      });
      if (walletResponse.ok) {
        const walletData = await walletResponse.json();
        setWallets(walletData.wallets);
      }
    } catch (error) {
      console.error('Error fetching payout methods:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API}/api/payments/payouts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onSuccess();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to request payout');
      }
    } catch (error) {
      setError('Error requesting payout');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Request Payout</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Amount</label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleInputChange}
              min={minThreshold}
              max={availableBalance}
              step="0.01"
              required
              className="w-full border rounded px-3 py-2"
            />
            <p className="text-xs text-gray-500 mt-1">
              Available: ${availableBalance?.toFixed(2)} • Min: ${minThreshold?.toFixed(2)}
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Payout Method</label>
            <select
              name="payout_method"
              value={formData.payout_method}
              onChange={handleInputChange}
              className="w-full border rounded px-3 py-2"
            >
              <option value="bank_transfer">Bank Transfer</option>
              <option value="paypal">PayPal</option>
              <option value="crypto">Cryptocurrency</option>
            </select>
          </div>

          {formData.payout_method === 'bank_transfer' && (
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Bank Account</label>
              <select
                name="bank_account_id"
                value={formData.bank_account_id}
                onChange={handleInputChange}
                required
                className="w-full border rounded px-3 py-2"
              >
                <option value="">Select bank account</option>
                {bankAccounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_name} - ****{account.account_number.slice(-4)}
                  </option>
                ))}
              </select>
            </div>
          )}

          {formData.payout_method !== 'bank_transfer' && (
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Digital Wallet</label>
              <select
                name="wallet_id"
                value={formData.wallet_id}
                onChange={handleInputChange}
                required
                className="w-full border rounded px-3 py-2"
              >
                <option value="">Select wallet</option>
                {wallets
                  .filter(wallet => wallet.wallet_type === formData.payout_method.replace('_transfer', ''))
                  .map((wallet) => (
                    <option key={wallet.id} value={wallet.id}>
                      {wallet.wallet_name} - {wallet.wallet_address}
                    </option>
                  ))}
              </select>
            </div>
          )}

          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Request Payout'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Royalty Split Manager Component
export const RoyaltySplitManager = ({ mediaId, mediaTitle }) => {
  const [splits, setSplits] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    recipient_email: '',
    recipient_name: '',
    split_type: 'percentage',
    percentage: 0,
    fixed_amount: 0,
    role: 'artist'
  });

  useEffect(() => {
    if (mediaId) {
      fetchRoyaltySplits();
    }
  }, [mediaId]);

  const fetchRoyaltySplits = async () => {
    try {
      const response = await fetch(`${API}/api/payments/royalty-splits/${mediaId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSplits(data.splits);
      } else {
        setError('Failed to load royalty splits');
      }
    } catch (error) {
      setError('Error loading royalty splits');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const splitData = {
        ...formData,
        media_id: mediaId
      };

      const response = await fetch(`${API}/api/payments/royalty-splits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(splitData)
      });

      if (response.ok) {
        setShowAddForm(false);
        setFormData({
          recipient_email: '',
          recipient_name: '',
          split_type: 'percentage',
          percentage: 0,
          fixed_amount: 0,
          role: 'artist'
        });
        fetchRoyaltySplits();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create royalty split');
      }
    } catch (error) {
      setError('Error creating royalty split');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
  };

  const getTotalPercentage = () => {
    return splits
      .filter(split => split.split_type === 'percentage')
      .reduce((total, split) => total + (split.percentage || 0), 0);
  };

  if (loading && splits.length === 0) {
    return <div className="text-center py-4">Loading royalty splits...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">Royalty Splits</h2>
          {mediaTitle && <p className="text-gray-600">{mediaTitle}</p>}
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
        >
          Add Split
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Total Percentage Warning */}
      {getTotalPercentage() > 100 && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
          Warning: Total percentage splits exceed 100% ({getTotalPercentage()}%)
        </div>
      )}

      {showAddForm && (
        <div className="bg-white border rounded-lg p-6 mb-6">
          <h3 className="text-xl font-bold mb-4">Add Royalty Split</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Recipient Email</label>
                <input
                  type="email"
                  name="recipient_email"
                  value={formData.recipient_email}
                  onChange={handleInputChange}
                  required
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Recipient Name</label>
                <input
                  type="text"
                  name="recipient_name"
                  value={formData.recipient_name}
                  onChange={handleInputChange}
                  required
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Split Type</label>
                <select
                  name="split_type"
                  value={formData.split_type}
                  onChange={handleInputChange}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Role</label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="artist">Artist</option>
                  <option value="producer">Producer</option>
                  <option value="songwriter">Songwriter</option>
                  <option value="label">Label</option>
                  <option value="other">Other</option>
                </select>
              </div>
              {formData.split_type === 'percentage' ? (
                <div>
                  <label className="block text-sm font-medium mb-2">Percentage (%)</label>
                  <input
                    type="number"
                    name="percentage"
                    value={formData.percentage}
                    onChange={handleInputChange}
                    min="0"
                    max="100"
                    step="0.1"
                    required
                    className="w-full border rounded px-3 py-2"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Current total: {getTotalPercentage() + formData.percentage}%
                  </p>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium mb-2">Fixed Amount ($)</label>
                  <input
                    type="number"
                    name="fixed_amount"
                    value={formData.fixed_amount}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    required
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
              )}
            </div>
            <div className="flex space-x-4 mt-6">
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Adding...' : 'Add Split'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="bg-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Existing Splits */}
      <div className="space-y-4">
        {splits.map((split) => (
          <div key={split.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold">{split.recipient_name}</h3>
                <p className="text-gray-600">{split.recipient_email}</p>
                <p className="text-sm text-gray-500 capitalize">{split.role}</p>
                <div className="mt-2">
                  {split.split_type === 'percentage' ? (
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                      {split.percentage}%
                    </span>
                  ) : (
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                      ${split.fixed_amount}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex space-x-2">
                <button className="text-blue-600 hover:text-blue-800">Edit</button>
                <button className="text-red-600 hover:text-red-800">Remove</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {splits.length === 0 && !showAddForm && (
        <div className="text-center py-8 text-gray-500">
          No royalty splits configured. Add splits to share earnings with collaborators.
        </div>
      )}
    </div>
  );
};