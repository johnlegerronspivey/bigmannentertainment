import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';

const RoyaltyEngine = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [royaltyData, setRoyaltyData] = useState({});
  const [revenueAnalytics, setRevenueAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    fetchRoyaltyData();
  }, []);

  const fetchRoyaltyData = async () => {
    setLoading(true);
    try {
      const [revenueRes] = await Promise.all([
        axios.get(`${API}/api/platform/analytics/revenue?user_id=user_123`)
      ]);

      if (revenueRes.data.success) setRevenueAnalytics(revenueRes.data.revenue_breakdown || {});
    } catch (error) {
      handleApiError(error, 'fetchRoyaltyData');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: '💰' },
    { id: 'payments', name: 'Payments', icon: '💳' },
    { id: 'splits', name: 'Royalty Splits', icon: '📊' },
    { id: 'analytics', name: 'Analytics', icon: '📈' }
  ];

  return (
    <div data-testid="royalty-engine" className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Royalty Engine</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Real-time royalty tracking and distribution</p>
        </div>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2">
          <span>💸</span>
          <span>Process Payouts</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">${revenueAnalytics.total_revenue?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">💰</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pending Payouts</p>
              <p className="text-2xl font-bold text-yellow-600">$0</p>
            </div>
            <span className="text-2xl">⏳</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Growth</p>
              <p className="text-2xl font-bold text-green-600">{revenueAnalytics.growth_rate ?? 0}%</p>
            </div>
            <span className="text-2xl">📈</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Contributors</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{revenueAnalytics.contributors || '0'}</p>
            </div>
            <span className="text-2xl">👥</span>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-green-500 text-green-600 dark:text-green-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="space-y-4">
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Revenue by Platform</h3>
              <div className="space-y-4">
                {revenueAnalytics.by_platform && Object.entries(revenueAnalytics.by_platform).map(([platform, amount]) => (
                  <div key={platform} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{platform}</span>
                    <span className="font-semibold text-gray-900 dark:text-white">${amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Assets</h3>
              <div className="space-y-4">
                {revenueAnalytics.by_asset && Object.entries(revenueAnalytics.by_asset).slice(0, 5).map(([asset, amount]) => (
                  <div key={asset} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 truncate">{asset}</span>
                    <span className="font-semibold text-gray-900 dark:text-white">${amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'payments' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`${isDarkMode ? 'bg-green-800 border-green-700' : 'bg-green-50 border-green-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-green-900 dark:text-green-100">Instant Payouts</h3>
                <p className="text-green-700 dark:text-green-300 text-sm mt-1">Crypto & Digital Wallets</p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-2">$0</p>
              </div>
              <div className={`${isDarkMode ? 'bg-blue-800 border-blue-700' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">Scheduled Payouts</h3>
                <p className="text-blue-700 dark:text-blue-300 text-sm mt-1">Bank Transfers & ACH</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-2">$0</p>
              </div>
              <div className={`${isDarkMode ? 'bg-yellow-800 border-yellow-700' : 'bg-yellow-50 border-yellow-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">Pending Review</h3>
                <p className="text-yellow-700 dark:text-yellow-300 text-sm mt-1">Manual Approval Required</p>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100 mt-2">$0</p>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Payments</h3>
              <div className="space-y-4">
                {[
                  { contributor: 'BeatMaster Pro', amount: 1250.00, date: '2024-01-15', method: 'PayPal', status: 'Completed' },
                  { contributor: 'VocalQueen', amount: 890.50, date: '2024-01-14', method: 'Bank Transfer', status: 'Processing' },
                  { contributor: 'GuitarGuru', amount: 456.75, date: '2024-01-13', method: 'Crypto', status: 'Completed' }
                ].map((payment, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{payment.contributor}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{payment.date} • {payment.method}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900 dark:text-white">${payment.amount.toLocaleString()}</p>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        payment.status === 'Completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      }`}>
                        {payment.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'splits' && (
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Royalty Split Configuration</h3>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Add New Split</button>
            </div>
            <div className="space-y-4">
              {[
                { asset: 'Summer Vibes Instrumental', contributors: [
                  { name: 'Producer', percentage: 50, amount: '$11,728' },
                  { name: 'Artist', percentage: 30, amount: '$7,037' },
                  { name: 'Label', percentage: 20, amount: '$4,691' }
                ]},
                { asset: 'Midnight Dreams', contributors: [
                  { name: 'Songwriter', percentage: 40, amount: '$7,294' },
                  { name: 'Vocalist', percentage: 35, amount: '$6,382' },
                  { name: 'Producer', percentage: 25, amount: '$4,559' }
                ]}
              ].map((split, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">{split.asset}</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {split.contributors.map((contributor, idx) => (
                      <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{contributor.name}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{contributor.percentage}%</p>
                        </div>
                        <p className="font-semibold text-gray-900 dark:text-white">{contributor.amount}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Revenue Trends</h3>
              <div className="space-y-3">
                {revenueAnalytics.by_time_period && Object.entries(revenueAnalytics.by_time_period).map(([period, amount]) => (
                  <div key={period} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{period}</span>
                    <span className="font-medium text-gray-900 dark:text-white">${amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Geographic Distribution</h3>
              <div className="space-y-3">
                {revenueAnalytics.by_region && Object.entries(revenueAnalytics.by_region).map(([region, amount]) => (
                  <div key={region} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{region}</span>
                    <span className="font-medium text-gray-900 dark:text-white">${amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { RoyaltyEngine };
