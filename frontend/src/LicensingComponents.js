import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

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