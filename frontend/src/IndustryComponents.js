import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Industry Dashboard Overview Component
export const IndustryDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/industry/dashboard`);
      setDashboardData(response.data.dashboard);
    } catch (error) {
      setError('Failed to load industry dashboard');
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  const partnerStats = dashboardData?.partner_statistics || {};
  const distributionStats = dashboardData?.distribution_statistics || {};
  const analyticsStats = dashboardData?.analytics_summary || {};

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-purple-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Partners</p>
              <p className="text-3xl font-bold text-gray-900">{partnerStats.total_partners || 0}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Active Distributions</p>
              <p className="text-3xl font-bold text-gray-900">{distributionStats.total_distributions || 0}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Plays</p>
              <p className="text-3xl font-bold text-gray-900">{analyticsStats.total_plays?.toLocaleString() || 0}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-yellow-500">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <p className="text-3xl font-bold text-gray-900">${analyticsStats.total_revenue?.toFixed(2) || '0.00'}</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-full">
              <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Partners by Category */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Industry Partners by Category</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(partnerStats.by_category || {}).map(([category, count]) => (
            <div key={category} className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{count}</div>
              <div className="text-sm text-gray-600 capitalize">
                {category.replace(/_/g, ' ')}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Distribution Status */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Distribution Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {Object.entries(distributionStats.by_status || {}).map(([status, count]) => (
            <div key={status} className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className={`w-3 h-3 rounded-full mr-3 ${
                status === 'live' ? 'bg-green-500' :
                status === 'processing' ? 'bg-yellow-500' :
                status === 'failed' ? 'bg-red-500' : 'bg-gray-500'
              }`}></div>
              <div>
                <div className="text-lg font-semibold">{count}</div>
                <div className="text-sm text-gray-600 capitalize">{status}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Industry Partners Component
export const IndustryPartners = () => {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedTier, setSelectedTier] = useState('');

  useEffect(() => {
    fetchPartners();
  }, [selectedCategory, selectedTier]);

  const fetchPartners = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (selectedTier) params.append('tier', selectedTier);

      const response = await axios.get(`${API}/industry/partners?${params}`);
      setPartners(response.data.partners);
    } catch (error) {
      setError('Failed to load industry partners');
      console.error('Error fetching partners:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { value: 'streaming_platform', label: 'Streaming Platforms' },
    { value: 'record_label', label: 'Record Labels' },
    { value: 'radio_station', label: 'Radio Stations' },
    { value: 'tv_network', label: 'TV Networks' },
    { value: 'venue', label: 'Venues' },
    { value: 'booking_agency', label: 'Booking Agencies' }
  ];

  const tiers = [
    { value: 'major', label: 'Major' },
    { value: 'independent', label: 'Independent' },
    { value: 'regional', label: 'Regional' },
    { value: 'local', label: 'Local' }
  ];

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filter Partners</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>{cat.label}</option>
            ))}
          </select>
          
          <select
            value={selectedTier}
            onChange={(e) => setSelectedTier(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Tiers</option>
            {tiers.map(tier => (
              <option key={tier.value} value={tier.value}>{tier.label}</option>
            ))}
          </select>

          <button
            onClick={() => {
              setSelectedCategory('');
              setSelectedTier('');
            }}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Partners List */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      ) : partners.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No partners found with current filters</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Partner
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tier
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Territories
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {partners.map((partner) => (
                <tr key={partner.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{partner.name}</div>
                    {partner.supported_formats && (
                      <div className="text-xs text-gray-500">
                        Formats: {partner.supported_formats.join(', ')}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {partner.category.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      partner.tier === 'major' ? 'bg-purple-100 text-purple-800' :
                      partner.tier === 'independent' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {partner.tier}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {partner.territories ? partner.territories.join(', ') : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      partner.status === 'active' ? 'bg-green-100 text-green-800' :
                      partner.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {partner.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Global Distribution Component
export const GlobalDistribution = () => {
  const [products, setProducts] = useState([]);
  const [distributions, setDistributions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('');

  useEffect(() => {
    fetchProducts();
    fetchDistributions();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/business/products`);
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchDistributions = async () => {
    try {
      const response = await axios.get(`${API}/industry/distributions`);
      setDistributions(response.data.distributions || []);
    } catch (error) {
      console.error('Error fetching distributions:', error);
    }
  };

  const handleGlobalDistribution = async () => {
    if (!selectedProduct) {
      setError('Please select a product to distribute');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post(`${API}/industry/distribute/${selectedProduct}`);
      setSuccess(response.data.message);
      fetchDistributions(); // Refresh distributions list
    } catch (error) {
      setError(error.response?.data?.detail || 'Distribution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Distribution Control */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Global Distribution</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Product to Distribute
            </label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Select a product...</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.product_name} - {product.artist_name || 'Unknown Artist'}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleGlobalDistribution}
            disabled={loading || !selectedProduct}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Distributing to All Platforms...
              </>
            ) : (
              '🌍 Distribute to ALL Industry Partners'
            )}
          </button>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}
        </div>
      </div>

      {/* Distribution History */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Distributions</h3>
        
        {distributions.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No distributions yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Partner
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {distributions.slice(0, 10).map((distribution) => (
                  <tr key={distribution.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {distribution.product_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {distribution.partner_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        distribution.distribution_status === 'live' ? 'bg-green-100 text-green-800' :
                        distribution.distribution_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        distribution.distribution_status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {distribution.distribution_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(distribution.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

// Industry Coverage Component
export const IndustryCoverage = () => {
  const [coverage, setCoverage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCoverage();
  }, []);

  const fetchCoverage = async () => {
    try {
      const response = await axios.get(`${API}/industry/coverage`);
      setCoverage(response.data.coverage);
    } catch (error) {
      setError('Failed to load industry coverage');
      console.error('Error fetching coverage:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Coverage Overview */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Industry Ecosystem Coverage</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <div className="text-2xl font-bold text-purple-600">{coverage?.streaming_platforms || 0}</div>
            <div className="text-sm text-gray-600">Streaming Platforms</div>
            <div className="text-xs text-purple-500 mt-1">Global reach for audio distribution</div>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="text-2xl font-bold text-blue-600">{coverage?.record_labels || 0}</div>
            <div className="text-sm text-gray-600">Record Labels</div>
            <div className="text-xs text-blue-500 mt-1">Major and independent labels</div>
          </div>

          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="text-2xl font-bold text-green-600">{coverage?.radio_stations || 0}</div>
            <div className="text-sm text-gray-600">Radio Stations</div>
            <div className="text-xs text-green-500 mt-1">Broadcast and online radio</div>
          </div>

          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <div className="text-2xl font-bold text-red-600">{coverage?.tv_networks || 0}</div>
            <div className="text-sm text-gray-600">TV Networks</div>
            <div className="text-xs text-red-500 mt-1">Music video and content placement</div>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <div className="text-2xl font-bold text-yellow-600">{coverage?.venues || 0}</div>
            <div className="text-sm text-gray-600">Venues</div>
            <div className="text-xs text-yellow-500 mt-1">Live performance opportunities</div>
          </div>

          <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
            <div className="text-2xl font-bold text-indigo-600">{coverage?.booking_agencies || 0}</div>
            <div className="text-sm text-gray-600">Booking Agencies</div>
            <div className="text-xs text-indigo-500 mt-1">Live event coordination</div>
          </div>
        </div>
      </div>

      {/* Global Reach */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Global Reach</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-3">Coverage Statistics</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Partners:</span>
                <span className="font-semibold">{coverage?.total_partners || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Global Partners:</span>
                <span className="font-semibold">{coverage?.global_reach || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Categories Covered:</span>
                <span className="font-semibold">{coverage?.categories_covered?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Territories:</span>
                <span className="font-semibold">{coverage?.territories_covered?.length || 0}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-medium text-gray-700 mb-3">Territory Coverage</h4>
            <div className="space-y-1">
              {coverage?.territories_covered?.slice(0, 10).map((territory, index) => (
                <div key={index} className="text-sm text-gray-600">
                  🌍 {territory}
                </div>
              ))}
              {coverage?.territories_covered?.length > 10 && (
                <div className="text-sm text-gray-500">
                  ... and {coverage.territories_covered.length - 10} more territories
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Success Message */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800">
              Complete Industry Ecosystem Connected
            </h3>
            <div className="mt-2 text-sm text-green-700">
              <p>
                Big Mann Entertainment is now connected to the entire music and entertainment industry ecosystem.
                Your content can reach every major platform, venue, and media outlet globally.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};