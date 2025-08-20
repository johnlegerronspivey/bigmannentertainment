import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// Statutory Rates Management Component
export const StatutoryRatesManager = () => {
  const [rates, setRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStatutoryRates();
  }, []);

  const fetchStatutoryRates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/licensing/statutory-rates`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRates(data.statutory_rates || []);
        setError('');
      } else {
        setError('Failed to load statutory rates');
      }
    } catch (error) {
      console.error('Statutory rates fetch error:', error);
      setError('Error loading statutory rates.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-white">Loading statutory rates...</div>;
  }

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
      <h3 className="text-xl font-bold text-white mb-4">Current Statutory Rates (2025)</h3>
      
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {rates.map((rate) => (
          <div key={rate.id} className="bg-white/5 rounded-lg p-4 border border-purple-400/30">
            <div className="flex justify-between items-start mb-2">
              <h4 className="text-lg font-semibold text-white">{rate.rate_name}</h4>
              <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm font-semibold">
                {rate.royalty_type?.toUpperCase()}
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-purple-200">Rate per Unit:</span>
                <span className="text-white font-semibold ml-2">
                  ${rate.rate_per_unit?.toFixed(4)} {rate.unit_type}
                </span>
              </div>
              
              <div>
                <span className="text-purple-200">Minimum Fee:</span>
                <span className="text-white font-semibold ml-2">
                  ${rate.minimum_fee?.toFixed(4)}
                </span>
              </div>
              
              <div>
                <span className="text-purple-200">Source:</span>
                <span className="text-white font-semibold ml-2">{rate.rate_source}</span>
              </div>
            </div>

            {rate.rate_percentage && (
              <div className="mt-2 text-sm">
                <span className="text-purple-200">Alternative Rate:</span>
                <span className="text-white font-semibold ml-2">{rate.rate_percentage}% of revenue</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {rates.length === 0 && (
        <div className="text-center py-8 text-purple-200">
          No statutory rates configured. Please contact system administrator.
        </div>
      )}
    </div>
  );
};

// Daily Compensation Dashboard Component
export const DailyCompensationDashboard = () => {
  const [compensationData, setCompensationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const calculateDailyCompensation = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/licensing/daily-compensation`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          compensation_date: selectedDate + 'T00:00:00Z'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setCompensationData(data.compensation_data);
        setError('');
      } else {
        setError('Failed to calculate daily compensation');
      }
    } catch (error) {
      console.error('Compensation calculation error:', error);
      setError('Error calculating compensation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const processDailyPayouts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/licensing/daily-payouts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          minimum_amount: 1.00
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Successfully processed ${data.payout_data.total_payouts_processed} payouts totaling $${data.payout_data.total_payout_amount.toFixed(2)}`);
        setError('');
      } else {
        setError('Failed to process daily payouts');
      }
    } catch (error) {
      console.error('Payout processing error:', error);
      setError('Error processing payouts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
      <h3 className="text-xl font-bold text-white mb-4">Daily Compensation Calculator</h3>
      
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Date Selection and Controls */}
      <div className="mb-6 space-y-4">
        <div>
          <label className="block text-purple-200 mb-2">Compensation Date:</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
          />
        </div>
        
        <div className="flex gap-4">
          <button
            onClick={calculateDailyCompensation}
            disabled={loading}
            className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300 disabled:opacity-50"
          >
            {loading ? 'Calculating...' : '📊 Calculate Daily Compensation'}
          </button>
          
          <button
            onClick={processDailyPayouts}
            disabled={loading || !compensationData}
            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-2 px-4 rounded transition duration-300 disabled:opacity-50"
          >
            {loading ? 'Processing...' : '💰 Process Daily Payouts'}
          </button>
        </div>
      </div>

      {/* Compensation Results */}
      {compensationData && (
        <div className="space-y-4">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/5 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-400 mb-1">
                {compensationData.total_platforms_processed}
              </div>
              <div className="text-purple-200 text-sm">Platforms Processed</div>
            </div>
            
            <div className="bg-white/5 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-400 mb-1">
                ${compensationData.total_compensation_amount?.toFixed(2)}
              </div>
              <div className="text-purple-200 text-sm">Total Compensation</div>
            </div>
            
            <div className="bg-white/5 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-yellow-400 mb-1">
                {compensationData.calculation_status === 'completed' ? '✅' : '⏳'}
              </div>
              <div className="text-purple-200 text-sm">Calculation Status</div>
            </div>
          </div>

          {/* Statutory Rates Applied */}
          <div className="bg-white/5 rounded-lg p-4">
            <h4 className="text-lg font-semibold text-white mb-3">Statutory Rates Applied</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-purple-200">Mechanical:</span>
                <span className="text-white font-semibold ml-2">
                  ${compensationData.statutory_rates_applied?.mechanical?.toFixed(4)}
                </span>
              </div>
              <div>
                <span className="text-purple-200">Performance:</span>
                <span className="text-white font-semibold ml-2">
                  ${compensationData.statutory_rates_applied?.performance?.toFixed(4)}
                </span>
              </div>
              <div>
                <span className="text-purple-200">Sync:</span>
                <span className="text-white font-semibold ml-2">
                  ${compensationData.statutory_rates_applied?.sync?.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="text-purple-200">Digital Performance:</span>
                <span className="text-white font-semibold ml-2">
                  ${compensationData.statutory_rates_applied?.digital_performance?.toFixed(4)}
                </span>
              </div>
            </div>
          </div>

          {/* Platform Compensations Preview */}
          {compensationData.platform_compensations && compensationData.platform_compensations.length > 0 && (
            <div className="bg-white/5 rounded-lg p-4">
              <h4 className="text-lg font-semibold text-white mb-3">Platform Compensations (Preview)</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-purple-400/30">
                      <th className="text-left text-purple-200 py-2">Platform</th>
                      <th className="text-right text-purple-200 py-2">Streams</th>
                      <th className="text-right text-purple-200 py-2">Revenue</th>
                      <th className="text-right text-purple-200 py-2">Compensation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {compensationData.platform_compensations.slice(0, 5).map((comp, index) => (
                      <tr key={index} className="border-b border-white/10">
                        <td className="text-white py-2">{comp.platform_name}</td>
                        <td className="text-right text-white py-2">{comp.total_streams?.toLocaleString()}</td>
                        <td className="text-right text-green-400 py-2">${comp.gross_revenue?.toFixed(2)}</td>
                        <td className="text-right text-blue-400 py-2">${comp.total_compensation?.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Compensation Dashboard Component
export const CompensationOverviewDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [periodDays, setPeriodDays] = useState(30);

  useEffect(() => {
    fetchCompensationDashboard();
  }, [periodDays]);

  const fetchCompensationDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/licensing/compensation-dashboard?period_days=${periodDays}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data.compensation_dashboard);
        setError('');
      } else {
        setError('Failed to load compensation dashboard');
      }
    } catch (error) {
      console.error('Dashboard fetch error:', error);
      setError('Error loading compensation dashboard.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-white">Loading compensation dashboard...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-400">{error}</div>;
  }

  const { period_summary, statutory_rates, compensation_breakdown, platform_performance, recent_payouts } = dashboardData || {};

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <div className="flex items-center gap-4 mb-6">
        <label className="text-purple-200">Period:</label>
        <select
          value={periodDays}
          onChange={(e) => setPeriodDays(parseInt(e.target.value))}
          className="bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={365}>Last year</option>
        </select>
      </div>

      {/* Period Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">
            ${period_summary?.total_compensation_calculated?.toFixed(2) || '0.00'}
          </div>
          <div className="text-purple-200">Total Compensation</div>
        </div>
        
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">
            ${period_summary?.total_payouts_processed?.toFixed(2) || '0.00'}
          </div>
          <div className="text-purple-200">Payouts Processed</div>
        </div>
        
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
          <div className="text-3xl font-bold text-yellow-400 mb-2">
            ${period_summary?.pending_compensation?.toFixed(2) || '0.00'}
          </div>
          <div className="text-purple-200">Pending Compensation</div>
        </div>
      </div>

      {/* Compensation Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Compensation Breakdown</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Artist Share</span>
              <span className="text-green-400 font-semibold">{compensation_breakdown?.artist_percentage}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Songwriter Share</span>
              <span className="text-blue-400 font-semibold">{compensation_breakdown?.songwriter_percentage}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Publisher Share</span>
              <span className="text-yellow-400 font-semibold">{compensation_breakdown?.publisher_percentage}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Big Mann Commission</span>
              <span className="text-purple-400 font-semibold">{compensation_breakdown?.big_mann_commission}%</span>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Current Statutory Rates</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Mechanical</span>
              <span className="text-white font-semibold">${statutory_rates?.mechanical_rate?.toFixed(4)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Performance</span>
              <span className="text-white font-semibold">${statutory_rates?.performance_rate?.toFixed(4)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Sync</span>
              <span className="text-white font-semibold">${statutory_rates?.sync_rate?.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Digital Performance</span>
              <span className="text-white font-semibold">${statutory_rates?.digital_performance_rate?.toFixed(4)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Performance */}
      {platform_performance && Object.keys(platform_performance).length > 0 && (
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Top Platform Performance</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-purple-400/30">
                  <th className="text-left text-purple-200 py-2">Platform</th>
                  <th className="text-right text-purple-200 py-2">Streams</th>
                  <th className="text-right text-purple-200 py-2">Revenue</th>
                  <th className="text-right text-purple-200 py-2">Compensation</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(platform_performance).slice(0, 5).map(([platform, metrics]) => (
                  <tr key={platform} className="border-b border-white/10">
                    <td className="text-white py-2">{platform}</td>
                    <td className="text-right text-white py-2">{metrics.total_streams?.toLocaleString()}</td>
                    <td className="text-right text-green-400 py-2">${metrics.total_revenue?.toFixed(2)}</td>
                    <td className="text-right text-blue-400 py-2">${metrics.total_compensation?.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Payouts */}
      {recent_payouts && recent_payouts.length > 0 && (
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">Recent Payouts</h3>
          <div className="space-y-3">
            {recent_payouts.slice(0, 5).map((payout, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b border-white/10">
                <div>
                  <div className="text-white font-semibold">{payout.recipient}</div>
                  <div className="text-purple-200 text-sm">
                    {new Date(payout.date).toLocaleDateString()}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-green-400 font-semibold">${payout.amount?.toFixed(2)}</div>
                  <div className={`text-sm px-2 py-1 rounded ${
                    payout.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                    payout.status === 'processing' ? 'bg-yellow-500/20 text-yellow-300' :
                    'bg-gray-500/20 text-gray-300'
                  }`}>
                    {payout.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Platform Licensing Dashboard Component
export const LicensingDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchLicensingDashboard();
  }, []);

  const fetchLicensingDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please log in to view licensing dashboard');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API}/api/licensing/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
        setError('');
      } else if (response.status === 401) {
        setError('Session expired. Please log in again.');
        localStorage.removeItem('token');
      } else {
        setError('Failed to load licensing dashboard');
      }
    } catch (error) {
      console.error('Dashboard fetch error:', error);
      setError('Error loading licensing dashboard. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const initializeAllPlatformLicenses = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/licensing/initialize-all-platforms`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Successfully licensed ${result.platforms_licensed} platforms!`);
        fetchLicensingDashboard(); // Refresh dashboard
      } else {
        setError('Failed to initialize platform licenses');
      }
    } catch (error) {
      console.error('License initialization error:', error);
      setError('Error initializing licenses. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading licensing dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">{error}</div>
      </div>
    );
  }

  const { licensing_overview, platform_categories, business_info, financial_summary } = dashboardData || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Platform Licensing Dashboard</h1>
          <p className="text-purple-200">{business_info?.business_entity} - Comprehensive License Management</p>
        </div>

        {/* Quick Actions */}
        <div className="mb-8 text-center">
          <button
            onClick={initializeAllPlatformLicenses}
            className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300 shadow-lg"
          >
            🚀 License All 83+ Platforms
          </button>
        </div>

        {/* Licensing Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
            <div className="text-3xl font-bold text-white mb-2">
              {licensing_overview?.total_platforms_licensed || 0}
            </div>
            <div className="text-purple-200">Total Platforms Licensed</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">
              {licensing_overview?.active_licenses || 0}
            </div>
            <div className="text-purple-200">Active Licenses</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
            <div className="text-3xl font-bold text-yellow-400 mb-2">
              {licensing_overview?.pending_licenses || 0}
            </div>
            <div className="text-purple-200">Pending Licenses</div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
            <div className="text-3xl font-bold text-blue-400 mb-2">
              {licensing_overview?.licensing_compliance_rate?.toFixed(1) || 100}%
            </div>
            <div className="text-purple-200">Compliance Rate</div>
          </div>
        </div>

        {/* Platform Categories */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Platform Categories</h3>
            <div className="space-y-3">
              {platform_categories && Object.entries(platform_categories).map(([category, count]) => (
                <div key={category} className="flex justify-between items-center">
                  <span className="text-purple-200">{category}</span>
                  <span className="text-white font-semibold">{count} platforms</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Financial Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-purple-200">Total Licensing Fees</span>
                <span className="text-green-400 font-semibold">${financial_summary?.total_licensing_fees?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-purple-200">Monthly Recurring</span>
                <span className="text-green-400 font-semibold">${financial_summary?.monthly_recurring_revenue?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="text-sm text-purple-300 mt-2">
                {financial_summary?.revenue_share_potential}
              </div>
            </div>
          </div>
        </div>

        {/* Business Information */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
          <h3 className="text-xl font-bold text-white mb-4">License Holder Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-purple-200">Business Entity:</span>
                  <span className="text-white font-semibold">{business_info?.business_entity}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-200">Business Owner:</span>
                  <span className="text-white font-semibold">{business_info?.business_owner}</span>
                </div>
              </div>
            </div>
            <div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-purple-200">EIN:</span>
                  <span className="text-white font-semibold">{business_info?.ein}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-200">TIN:</span>
                  <span className="text-white font-semibold">{business_info?.tin}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Platform License Management Component
export const PlatformLicenseManager = () => {
  const [licenses, setLicenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchPlatformLicenses();
  }, [statusFilter]);

  const fetchPlatformLicenses = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (statusFilter) params.append('status', statusFilter);

      const response = await fetch(`${API}/api/licensing/platforms?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setLicenses(data.licenses || []);
        setError('');
      } else {
        setError('Failed to load platform licenses');
      }
    } catch (error) {
      console.error('Licenses fetch error:', error);
      setError('Error loading platform licenses.');
    } finally {
      setLoading(false);
    }
  };

  const activateLicense = async (platformId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/licensing/platforms/${platformId}/activate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        alert(`License for ${platformId} activated successfully!`);
        fetchPlatformLicenses(); // Refresh list
      } else {
        alert('Failed to activate license');
      }
    } catch (error) {
      console.error('License activation error:', error);
      alert('Error activating license');
    }
  };

  const deactivateLicense = async (platformId) => {
    const reason = prompt('Enter reason for deactivation:');
    if (!reason) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/licensing/platforms/${platformId}/deactivate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason })
      });
      
      if (response.ok) {
        alert(`License for ${platformId} deactivated`);
        fetchPlatformLicenses(); // Refresh list
      } else {
        alert('Failed to deactivate license');
      }
    } catch (error) {
      console.error('License deactivation error:', error);
      alert('Error deactivating license');
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-white">Loading platform licenses...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold text-white mb-6">Platform License Management</h2>

        {/* Filter Controls */}
        <div className="mb-6">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-white/10 text-white border border-purple-400 rounded-lg px-4 py-2"
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="pending">Pending</option>
            <option value="expired">Expired</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* License Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {licenses.map((license) => (
            <div key={license.platform_id} className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold text-white">{license.platform_name}</h3>
                <span className={`px-2 py-1 rounded text-sm font-semibold ${
                  license.license_status === 'active' ? 'bg-green-500 text-white' :
                  license.license_status === 'pending' ? 'bg-yellow-500 text-black' :
                  license.license_status === 'expired' ? 'bg-red-500 text-white' :
                  'bg-gray-500 text-white'
                }`}>
                  {license.license_status?.toUpperCase()}
                </span>
              </div>

              <div className="space-y-2 mb-4 text-sm text-purple-200">
                <div>Type: {license.license_type}</div>
                <div>Monthly Limit: {license.monthly_limit} uploads</div>
                <div>Revenue Share: {license.revenue_share_percentage}%</div>
                <div>Usage: {license.usage_count || 0} uploads</div>
              </div>

              <div className="flex gap-2">
                {license.license_status === 'active' ? (
                  <button
                    onClick={() => deactivateLicense(license.platform_id)}
                    className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm"
                  >
                    Deactivate
                  </button>
                ) : (
                  <button
                    onClick={() => activateLicense(license.platform_id)}
                    className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm"
                  >
                    Activate
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {licenses.length === 0 && (
          <div className="text-center py-8 text-purple-200">
            No platform licenses found. Initialize platform licensing to get started.
          </div>
        )}
      </div>
    </div>
  );
};

// Licensing Status Component
export const LicensingStatus = () => {
  const [statusData, setStatusData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchLicensingStatus();
  }, []);

  const fetchLicensingStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/licensing/status`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStatusData(data);
        setError('');
      } else {
        setError('Failed to load licensing status');
      }
    } catch (error) {
      console.error('Status fetch error:', error);
      setError('Error loading licensing status.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-white">Loading licensing status...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-400">{error}</div>;
  }

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
      <h3 className="text-xl font-bold text-white mb-4">Overall Licensing Status</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-purple-200">Business Entity:</span>
            <span className="text-white font-semibold">{statusData?.business_entity}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-purple-200">Business Owner:</span>
            <span className="text-white font-semibold">{statusData?.business_owner}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-purple-200">Total Platforms:</span>
            <span className="text-white font-semibold">{statusData?.total_platforms_licensed}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-purple-200">Active Licenses:</span>
            <span className="text-green-400 font-semibold">{statusData?.active_licenses}</span>
          </div>
        </div>
        
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-purple-200">Health Score:</span>
            <span className={`font-semibold ${statusData?.licensing_health_score > 90 ? 'text-green-400' : 'text-yellow-400'}`}>
              {statusData?.licensing_health_score}%
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-purple-200">Compliance Rate:</span>
            <span className="text-blue-400 font-semibold">{statusData?.compliance_rate?.toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-purple-200">Status:</span>
            <span className={`font-semibold ${statusData?.licensing_status === 'Fully Licensed' ? 'text-green-400' : 'text-yellow-400'}`}>
              {statusData?.licensing_status}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-purple-200">Master Agreement:</span>
            <span className="text-green-400 font-semibold">
              {statusData?.master_agreement_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="mt-4 text-sm text-purple-300">
        Last Updated: {new Date(statusData?.last_updated).toLocaleString()}
      </div>
    </div>
  );
};