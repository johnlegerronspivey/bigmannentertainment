import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// Payment Package Selection Component
export const PaymentPackages = ({ onSelectPackage }) => {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchPackages();
  }, []);

  const handleSelectPackage = (pkg) => {
    if (onSelectPackage) {
      onSelectPackage(pkg);
    } else {
      // Navigate to checkout page
      navigate(`/checkout/${pkg.id}`);
    }
  };

  const fetchPackages = async () => {
    try {
      const response = await fetch(`${API}/api/payments/packages`);
      if (response.ok) {
        const data = await response.json();
        setPackages(data.packages);
      } else {
        setError('Failed to load packages');
      }
    } catch (error) {
      setError('Error loading packages');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading payment packages...</div>;
  if (error) return <div className="text-red-500 text-center py-8">{error}</div>;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-3xl font-bold text-center mb-8">Choose Your Plan</h2>
      <div className="grid md:grid-cols-3 gap-6">
        {packages.map((pkg) => (
          <div key={pkg.id} className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-bold mb-2">{pkg.name}</h3>
            <p className="text-gray-600 mb-4">{pkg.description}</p>
            <div className="text-2xl font-bold mb-4">
              ${pkg.amount}
              {pkg.is_subscription && <span className="text-sm">/{pkg.interval}</span>}
            </div>
            <ul className="mb-6 space-y-2">
              {pkg.features.map((feature, index) => (
                <li key={index} className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  {feature}
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleSelectPackage(pkg)}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
            >
              Select Plan
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Payment Checkout Component
export const PaymentCheckout = ({ packageId, mediaId, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const initiatePayment = async () => {
    setLoading(true);
    setError('');

    try {
      const originUrl = window.location.origin;
      const requestBody = {
        package_id: packageId,
        media_id: mediaId,
        origin_url: originUrl,
        metadata: {
          source: 'web_checkout',
          timestamp: new Date().toISOString()
        }
      };

      const response = await fetch(`${API}/api/payments/checkout/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create checkout session');
      }

      const data = await response.json();
      
      // Redirect to Stripe Checkout
      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error) {
      setError(error.message);
      console.error('Payment error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 border rounded-lg">
      <h3 className="text-xl font-bold mb-4">Complete Your Purchase</h3>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mb-6">
        <p className="text-gray-600 mb-2">You will be redirected to Stripe to complete your payment securely.</p>
      </div>

      <div className="flex space-x-4">
        <button
          onClick={initiatePayment}
          disabled={loading}
          className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Processing...' : 'Pay Now'}
        </button>
        <button
          onClick={onCancel}
          className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-400 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

// Payment Success/Status Component
export const PaymentStatus = () => {
  const [status, setStatus] = useState('checking');
  const [paymentDetails, setPaymentDetails] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId) {
      pollPaymentStatus(sessionId);
    } else {
      setStatus('error');
      setError('No session ID found');
    }
  }, []);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      setStatus('timeout');
      setError('Payment status check timed out. Please check your email for confirmation.');
      return;
    }

    try {
      const response = await fetch(`${API}/api/payments/checkout/status/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to check payment status');
      }

      const data = await response.json();
      setPaymentDetails(data);
      
      if (data.payment_status === 'paid') {
        setStatus('success');
        return;
      } else if (data.status === 'expired') {
        setStatus('expired');
        setError('Payment session expired. Please try again.');
        return;
      }

      // If payment is still pending, continue polling
      setStatus('pending');
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setStatus('error');
      setError('Error checking payment status. Please try again.');
    }
  };

  const getStatusDisplay = () => {
    switch (status) {
      case 'checking':
        return (
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Checking payment status...</p>
          </div>
        );
      case 'pending':
        return (
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600 mx-auto mb-4"></div>
            <p>Payment is being processed...</p>
          </div>
        );
      case 'success':
        return (
          <div className="text-center">
            <div className="text-green-500 text-6xl mb-4">✓</div>
            <h2 className="text-2xl font-bold text-green-600 mb-2">Payment Successful!</h2>
            <p className="text-gray-600 mb-4">Thank you for your purchase.</p>
            {paymentDetails && (
              <div className="bg-gray-100 p-4 rounded mb-4">
                <p><strong>Amount:</strong> ${paymentDetails.amount_total}</p>
                <p><strong>Currency:</strong> {paymentDetails.currency.toUpperCase()}</p>
              </div>
            )}
            <button
              onClick={() => window.location.href = '/dashboard'}
              className="bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700"
            >
              Continue to Dashboard
            </button>
          </div>
        );
      case 'expired':
      case 'error':
      case 'timeout':
        return (
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">✗</div>
            <h2 className="text-2xl font-bold text-red-600 mb-2">Payment Failed</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={() => window.location.href = '/pricing'}
              className="bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 border rounded-lg">
      {getStatusDisplay()}
    </div>
  );
};

// Bank Account Management Component
export const BankAccountManager = () => {
  const [accounts, setAccounts] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    account_name: '',
    account_number: '',
    routing_number: '',
    bank_name: '',
    account_type: 'checking',
    is_primary: false
  });

  useEffect(() => {
    fetchBankAccounts();
  }, []);

  const fetchBankAccounts = async () => {
    try {
      const response = await fetch(`${API}/api/payments/bank-accounts`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts);
      }
    } catch (error) {
      setError('Failed to load bank accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API}/api/payments/bank-accounts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setShowAddForm(false);
        setFormData({
          account_name: '',
          account_number: '',
          routing_number: '',
          bank_name: '',
          account_type: 'checking',
          is_primary: false
        });
        fetchBankAccounts();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to add bank account');
      }
    } catch (error) {
      setError('Error adding bank account');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  if (loading && accounts.length === 0) {
    return <div className="text-center py-8">Loading bank accounts...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Bank Accounts</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
        >
          Add Bank Account
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {showAddForm && (
        <div className="bg-white border rounded-lg p-6 mb-6">
          <h3 className="text-xl font-bold mb-4">Add New Bank Account</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Account Name</label>
                <input
                  type="text"
                  name="account_name"
                  value={formData.account_name}
                  onChange={handleInputChange}
                  required
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Bank Name</label>
                <input
                  type="text"
                  name="bank_name"
                  value={formData.bank_name}
                  onChange={handleInputChange}
                  required
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Account Number</label>
                <input
                  type="text"
                  name="account_number"
                  value={formData.account_number}
                  onChange={handleInputChange}
                  required
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Routing Number</label>
                <input
                  type="text"
                  name="routing_number"
                  value={formData.routing_number}
                  onChange={handleInputChange}
                  required
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Account Type</label>
                <select
                  name="account_type"
                  value={formData.account_type}
                  onChange={handleInputChange}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="checking">Checking</option>
                  <option value="savings">Savings</option>
                  <option value="business">Business</option>
                </select>
              </div>
              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_primary"
                    checked={formData.is_primary}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  Set as primary account
                </label>
              </div>
            </div>
            <div className="flex space-x-4 mt-6">
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Adding...' : 'Add Account'}
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

      <div className="space-y-4">
        {accounts.map((account) => (
          <div key={account.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold">{account.account_name}</h3>
                <p className="text-gray-600">{account.bank_name}</p>
                <p className="text-sm text-gray-500">
                  ****{account.account_number.slice(-4)} • {account.account_type}
                </p>
                {account.is_primary && (
                  <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    Primary
                  </span>
                )}
              </div>
              <div className="flex space-x-2">
                <button className="text-blue-600 hover:text-blue-800">Edit</button>
                <button className="text-red-600 hover:text-red-800">Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {accounts.length === 0 && !showAddForm && (
        <div className="text-center py-8 text-gray-500">
          No bank accounts added yet. Add one to receive payouts.
        </div>
      )}
    </div>
  );
};

// Digital Wallet Manager Component
export const DigitalWalletManager = () => {
  const [wallets, setWallets] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    wallet_type: 'paypal',
    wallet_address: '',
    wallet_name: '',
    is_primary: false
  });

  useEffect(() => {
    fetchWallets();
  }, []);

  const fetchWallets = async () => {
    try {
      const response = await fetch(`${API}/api/payments/wallets`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setWallets(data.wallets);
      }
    } catch (error) {
      setError('Failed to load wallets');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API}/api/payments/wallets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setShowAddForm(false);
        setFormData({
          wallet_type: 'paypal',
          wallet_address: '',
          wallet_name: '',
          is_primary: false
        });
        fetchWallets();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to add wallet');
      }
    } catch (error) {
      setError('Error adding wallet');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const getWalletIcon = (type) => {
    switch (type) {
      case 'paypal': return '💳';
      case 'venmo': return '💰';
      case 'cashapp': return '💵';
      case 'crypto': return '₿';
      default: return '🏦';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Digital Wallets</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
        >
          Add Wallet
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {showAddForm && (
        <div className="bg-white border rounded-lg p-6 mb-6">
          <h3 className="text-xl font-bold mb-4">Add New Digital Wallet</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Wallet Type</label>
                <select
                  name="wallet_type"
                  value={formData.wallet_type}
                  onChange={handleInputChange}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="paypal">PayPal</option>
                  <option value="venmo">Venmo</option>
                  <option value="cashapp">Cash App</option>
                  <option value="crypto">Cryptocurrency</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Wallet Name</label>
                <input
                  type="text"
                  name="wallet_name"
                  value={formData.wallet_name}
                  onChange={handleInputChange}
                  required
                  placeholder="My PayPal Account"
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2">
                  {formData.wallet_type === 'crypto' ? 'Wallet Address' : 'Email/Username'}
                </label>
                <input
                  type="text"
                  name="wallet_address"
                  value={formData.wallet_address}
                  onChange={handleInputChange}
                  required
                  placeholder={
                    formData.wallet_type === 'crypto' 
                      ? '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'
                      : 'user@example.com'
                  }
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div className="md:col-span-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_primary"
                    checked={formData.is_primary}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  Set as primary wallet
                </label>
              </div>
            </div>
            <div className="flex space-x-4 mt-6">
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Adding...' : 'Add Wallet'}
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

      <div className="space-y-4">
        {wallets.map((wallet) => (
          <div key={wallet.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div className="flex items-center">
                <span className="text-2xl mr-3">{getWalletIcon(wallet.wallet_type)}</span>
                <div>
                  <h3 className="font-bold">{wallet.wallet_name}</h3>
                  <p className="text-gray-600 capitalize">{wallet.wallet_type}</p>
                  <p className="text-sm text-gray-500">{wallet.wallet_address}</p>
                  {wallet.is_primary && (
                    <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      Primary
                    </span>
                  )}
                </div>
              </div>
              <div className="flex space-x-2">
                <button className="text-blue-600 hover:text-blue-800">Edit</button>
                <button className="text-red-600 hover:text-red-800">Delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {wallets.length === 0 && !showAddForm && (
        <div className="text-center py-8 text-gray-500">
          No digital wallets added yet. Add one to receive payouts.
        </div>
      )}
    </div>
  );
};