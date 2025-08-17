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

// Industry Identifiers Management Component (IPI, ISNI, AARC)
export const IndustryIdentifiersManagement = () => {
  const [identifiers, setIdentifiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedEntityType, setSelectedEntityType] = useState('');
  const [selectedIdentifierType, setSelectedIdentifierType] = useState('');

  useEffect(() => {
    fetchIndustryIdentifiers();
  }, [selectedEntityType, selectedIdentifierType]);

  const fetchIndustryIdentifiers = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedEntityType) params.append('entity_type', selectedEntityType);
      if (selectedIdentifierType) params.append('identifier_type', selectedIdentifierType);

      const response = await axios.get(`${API}/industry/identifiers?${params}`);
      setIdentifiers(response.data.identifiers);
    } catch (error) {
      setError('Failed to load industry identifiers');
      console.error('Error fetching industry identifiers:', error);
    } finally {
      setLoading(false);
    }
  };

  const entityTypes = [
    { value: 'company', label: 'Company' },
    { value: 'individual', label: 'Individual' },
    { value: 'band', label: 'Band' },
    { value: 'organization', label: 'Organization' }
  ];

  const identifierTypes = [
    { value: 'ipi', label: 'IPI Numbers' },
    { value: 'isni', label: 'ISNI Numbers' },
    { value: 'aarc', label: 'AARC Numbers' }
  ];

  return (
    <div className="space-y-6">
      {/* Industry Identifiers Overview */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg p-6">
        <div className="flex items-center">
          <div className="p-3 bg-white bg-opacity-20 rounded-full mr-4">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold">Industry Identifiers Management</h2>
            <p className="text-purple-100">IPI, ISNI, and AARC identifiers for Big Mann Entertainment</p>
          </div>
        </div>
      </div>

      {/* Big Mann Entertainment Comprehensive Identifier Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Big Mann Entertainment Company Card */}
        <div className="bg-white shadow-lg rounded-lg p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Big Mann Entertainment</h3>
              <p className="text-sm text-gray-600">Company - Record Label & Publisher</p>
            </div>
            <div className="text-purple-600">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
          
          <div className="space-y-3">
            {/* IPI Number */}
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
              <div>
                <div className="text-sm font-medium text-gray-700">IPI Number</div>
                <div className="text-lg font-bold text-purple-600">813048171</div>
              </div>
              <div className="text-xs text-gray-500">Publisher Rights</div>
            </div>
            
            {/* AARC Number */}
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <div>
                <div className="text-sm font-medium text-gray-700">AARC Number</div>
                <div className="text-lg font-bold text-blue-600">RC00002057</div>
              </div>
              <div className="text-xs text-gray-500">Record Company</div>
            </div>
            
            {/* ISNI - Not Applicable */}
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div>
                <div className="text-sm font-medium text-gray-700">ISNI Number</div>
                <div className="text-sm text-gray-500">Not Applicable</div>
              </div>
              <div className="text-xs text-gray-400">Company Entity</div>
            </div>
          </div>
          
          <div className="mt-4 text-sm text-gray-600">
            <div>📍 1314 Lincoln Heights Street, Alexander City, AL 35010</div>
            <div>📞 334-669-8638</div>
            <div>🏢 Sound Recording Industries (NAICS: 512200)</div>
          </div>
          <div className="mt-3">
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Active Status</span>
          </div>
        </div>

        {/* John LeGerron Spivey Individual Card */}
        <div className="bg-white shadow-lg rounded-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">John LeGerron Spivey</h3>
              <p className="text-sm text-gray-600">Individual - Songwriter & Artist</p>
            </div>
            <div className="text-blue-600">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
          
          <div className="space-y-3">
            {/* IPI Number */}
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <div>
                <div className="text-sm font-medium text-gray-700">IPI Number</div>
                <div className="text-lg font-bold text-green-600">578413032</div>
              </div>
              <div className="text-xs text-gray-500">Songwriter</div>
            </div>
            
            {/* ISNI Number */}
            <div className="flex justify-between items-center p-3 bg-indigo-50 rounded-lg">
              <div>
                <div className="text-sm font-medium text-gray-700">ISNI Number</div>
                <div className="text-lg font-bold text-indigo-600">0000000491551894</div>
              </div>
              <div className="text-xs text-gray-500">Name Identifier</div>
            </div>
            
            {/* AARC Number */}
            <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
              <div>
                <div className="text-sm font-medium text-gray-700">AARC Number</div>
                <div className="text-lg font-bold text-orange-600">FA02933539</div>
              </div>
              <div className="text-xs text-gray-500">Featured Artist</div>
            </div>
          </div>
          
          <div className="mt-4 text-sm text-gray-600">
            <div>📍 1314 Lincoln Heights Street, Alexander City, AL 35010</div>
            <div>📞 334-669-8638</div>
            <div>🎵 Primary Role: Vocals</div>
            <div>🎼 PRO: ASCAP</div>
          </div>
          <div className="mt-3">
            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">Active Songwriter</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filter Industry Identifiers</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={selectedEntityType}
            onChange={(e) => setSelectedEntityType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Entity Types</option>
            {entityTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
          
          <select
            value={selectedIdentifierType}
            onChange={(e) => setSelectedIdentifierType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Identifier Types</option>
            {identifierTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>

          <button
            onClick={() => {
              setSelectedEntityType('');
              setSelectedIdentifierType('');
            }}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            Clear Filters
          </button>
          
          <button
            onClick={fetchIndustryIdentifiers}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
          >
            Refresh Data
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Industry Identifiers List */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      ) : identifiers.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No industry identifiers found with current filters</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IPI Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ISNI Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  AARC Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {identifiers.map((identifier) => (
                <tr key={identifier.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{identifier.entity_name}</div>
                    {identifier.contact_info?.phone && (
                      <div className="text-xs text-gray-500">📞 {identifier.contact_info.phone}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {identifier.entity_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {identifier.ipi_number ? (
                      <div>
                        <div className="text-sm font-bold text-purple-600">{identifier.ipi_number}</div>
                        <div className="text-xs text-gray-500">{identifier.ipi_role}</div>
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {identifier.isni_number ? (
                      <div className="text-sm font-bold text-indigo-600">{identifier.isni_number}</div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {identifier.aarc_number ? (
                      <div>
                        <div className="text-sm font-bold text-orange-600">{identifier.aarc_number}</div>
                        <div className="text-xs text-gray-500">{identifier.aarc_type}</div>
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      identifier.status === 'active' ? 'bg-green-100 text-green-800' :
                      identifier.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {identifier.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Industry Identifiers Information */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* IPI Information */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
          <div className="flex items-center mb-3">
            <div className="p-2 bg-purple-100 rounded-full mr-3">
              <svg className="h-5 w-5 text-purple-600" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-sm font-medium text-purple-800">IPI Numbers</h3>
          </div>
          <div className="text-sm text-purple-700">
            <p>Interested Parties Information numbers identify writers, composers, publishers, and other parties involved in musical works for proper royalty distribution.</p>
            <div className="mt-2 font-medium">Big Mann Entertainment IPI Numbers:</div>
            <ul className="list-disc list-inside mt-1 text-xs">
              <li>813048171 - Big Mann Entertainment (Publisher)</li>
              <li>578413032 - John LeGerron Spivey (Songwriter)</li>
            </ul>
          </div>
        </div>

        {/* ISNI Information */}
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
          <div className="flex items-center mb-3">
            <div className="p-2 bg-indigo-100 rounded-full mr-3">
              <svg className="h-5 w-5 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <h3 className="text-sm font-medium text-indigo-800">ISNI Numbers</h3>
          </div>
          <div className="text-sm text-indigo-700">
            <p>International Standard Name Identifier provides unique identification for contributors to creative works across multiple domains including music, literature, and film.</p>
            <div className="mt-2 font-medium">John LeGerron Spivey ISNI:</div>
            <ul className="list-disc list-inside mt-1 text-xs">
              <li>0000000491551894 - Individual Creator Identifier</li>
            </ul>
          </div>
        </div>

        {/* AARC Information */}
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
          <div className="flex items-center mb-3">
            <div className="p-2 bg-orange-100 rounded-full mr-3">
              <svg className="h-5 w-5 text-orange-600" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 className="text-sm font-medium text-orange-800">AARC Numbers</h3>
          </div>
          <div className="text-sm text-orange-700">
            <p>Alliance of Artists and Recording Companies identifiers manage neighboring rights for performers and record companies in sound recordings.</p>
            <div className="mt-2 font-medium">Big Mann Entertainment AARC:</div>
            <ul className="list-disc list-inside mt-1 text-xs">
              <li>RC00002057 - Big Mann Entertainment (Record Company)</li>
              <li>FA02933539 - John LeGerron Spivey (Featured Artist)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Enhanced Entertainment Industry Dashboard Component
export const EnhancedEntertainmentDashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    fetchEntertainmentDashboard();
  }, []);

  const fetchEntertainmentDashboard = async () => {
    try {
      const response = await axios.get(`${API}/industry/entertainment/dashboard`);
      setDashboardData(response.data.dashboard);
    } catch (error) {
      setError('Failed to load entertainment dashboard');
      console.error('Error fetching entertainment dashboard:', error);
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

  return (
    <div className="space-y-6">
      {/* Enhanced Entertainment Overview */}
      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 text-white rounded-lg p-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">Big Mann Entertainment</h2>
            <p className="text-purple-100 text-lg">Comprehensive Entertainment Ecosystem</p>
            <div className="mt-2 text-sm">
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full mr-2">Global Reach</span>
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full mr-2">Multi-Platform</span>
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full">Full-Service</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{dashboardData.big_mann_entertainment?.total_industry_reach || 0}</div>
            <div className="text-sm text-purple-100">Industry Connections</div>
          </div>
        </div>
      </div>

      {/* Entertainment Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Photography Services */}
        <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-pink-500">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-pink-100 rounded-full">
              <svg className="w-6 h-6 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">{dashboardData.photography_service?.count || 0}</div>
              <div className="text-xs text-gray-500">Photography Services</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Album Covers:</span>
              <span className="font-semibold">{dashboardData.photography_breakdown?.album_cover || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Promotional:</span>
              <span className="font-semibold">{dashboardData.photography_breakdown?.promotional || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Event Photography:</span>
              <span className="font-semibold">{dashboardData.photography_breakdown?.event || 0}</span>
            </div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-pink-100 text-pink-800 text-xs rounded-full">Professional Services</span>
          </div>
        </div>

        {/* Video Production */}
        <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-red-500">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-red-100 rounded-full">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">{dashboardData.video_production?.count || 0}</div>
              <div className="text-xs text-gray-500">Video Production</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Music Videos:</span>
              <span className="font-semibold">{dashboardData.video_breakdown?.music_videos || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Production Companies:</span>
              <span className="font-semibold">{dashboardData.video_breakdown?.production_companies || 0}</span>
            </div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">Professional Video</span>
          </div>
        </div>

        {/* Live Streaming */}
        <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-purple-500">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z" />
              </svg>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">{dashboardData.live_streaming?.count || 0}</div>
              <div className="text-xs text-gray-500">Streaming Platforms</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-sm text-gray-600">
              Live performance streaming, interactive content, and real-time audience engagement.
            </div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">Live Content</span>
          </div>
        </div>

        {/* Gaming & Esports */}
        <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-green-500">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">{dashboardData.gaming_esports?.count || 0}</div>
              <div className="text-xs text-gray-500">Gaming Platforms</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-sm text-gray-600">
              Game soundtracks, esports content, and interactive gaming experiences.
            </div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Gaming Content</span>
          </div>
        </div>

        {/* Podcast Platforms */}
        <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-yellow-500">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-yellow-100 rounded-full">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 016 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">{dashboardData.podcast_platform?.count || 0}</div>
              <div className="text-xs text-gray-500">Podcast Platforms</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-sm text-gray-600">
              Audio content distribution, podcast hosting, and voice-over services.
            </div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">Audio Content</span>
          </div>
        </div>

        {/* Stock Photography */}
        <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-indigo-500">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-indigo-100 rounded-full">
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">{dashboardData.stock_photography?.count || 0}</div>
              <div className="text-xs text-gray-500">Stock Platforms</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-sm text-gray-600">
              Licensed photography, stock images, and commercial photo distribution.
            </div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full">Stock Content</span>
          </div>
        </div>
      </div>

      {/* Monetization Summary */}
      <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4">Revenue Optimization Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{dashboardData.monetization_summary?.total_platforms || 0}</div>
            <div className="text-sm text-green-100">Total Platforms</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{dashboardData.monetization_summary?.categories_covered || 0}</div>
            <div className="text-sm text-green-100">Revenue Categories</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{dashboardData.monetization_summary?.estimated_monthly_potential || '$0'}</div>
            <div className="text-sm text-green-100">Monthly Potential</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button className="px-4 py-2 bg-pink-600 text-white rounded-md hover:bg-pink-700 transition-colors">
            📸 Photography Services
          </button>
          <button className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
            🎬 Video Production
          </button>
          <button className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors">
            🎙️ Podcast Hosting
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
            💰 Monetization Strategy
          </button>
        </div>
      </div>
    </div>
  );
};

// Photography Services Management Component
export const PhotographyServices = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedServiceType, setSelectedServiceType] = useState('');
  const [selectedPriceRange, setSelectedPriceRange] = useState('');

  useEffect(() => {
    fetchPhotographyServices();
  }, [selectedServiceType, selectedPriceRange]);

  const fetchPhotographyServices = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedServiceType) params.append('service_type', selectedServiceType);
      if (selectedPriceRange) params.append('price_range', selectedPriceRange);

      const response = await axios.get(`${API}/industry/photography/services?${params}`);
      setServices(response.data.services);
    } catch (error) {
      setError('Failed to load photography services');
      console.error('Error fetching photography services:', error);
    } finally {
      setLoading(false);
    }
  };

  const serviceTypes = ['album_cover', 'promotional', 'event', 'fashion', 'commercial'];
  const priceRanges = ['$0-500', '$500-1500', '$1500-5000', '$5000+'];

  return (
    <div className="space-y-6">
      {/* Photography Services Header */}
      <div className="bg-gradient-to-r from-pink-600 to-purple-600 text-white rounded-lg p-6">
        <div className="flex items-center">
          <div className="p-3 bg-white bg-opacity-20 rounded-full mr-4">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold">Photography Services</h2>
            <p className="text-pink-100">Professional photography for Big Mann Entertainment</p>
          </div>
        </div>
      </div>

      {/* Service Type Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow-lg rounded-lg p-6 border-l-4 border-pink-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Album Cover Photography</h3>
          <p className="text-sm text-gray-600 mb-4">Professional album covers, single covers, and EP artwork that captures your musical vision.</p>
          <div className="space-y-2 text-xs text-gray-500">
            <div>• Conceptual design and photography</div>
            <div>• High-resolution digital delivery</div>
            <div>• Multiple format options</div>
            <div>• Revision rounds included</div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-pink-100 text-pink-800 text-xs rounded-full">$500-$3000</span>
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-lg p-6 border-l-4 border-purple-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Promotional Photography</h3>
          <p className="text-sm text-gray-600 mb-4">Professional headshots, press photos, and promotional content for marketing campaigns.</p>
          <div className="space-y-2 text-xs text-gray-500">
            <div>• Professional headshots</div>
            <div>• Press kit photography</div>
            <div>• Social media content</div>
            <div>• Marketing campaign visuals</div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">$300-$2500</span>
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-lg p-6 border-l-4 border-indigo-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Event Photography</h3>
          <p className="text-sm text-gray-600 mb-4">Live concert photography, backstage moments, and event documentation.</p>
          <div className="space-y-2 text-xs text-gray-500">
            <div>• Live performance shots</div>
            <div>• Backstage photography</div>
            <div>• Audience and venue capture</div>
            <div>• Event documentation</div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full">$200-$1200</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filter Photography Services</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={selectedServiceType}
            onChange={(e) => setSelectedServiceType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
          >
            <option value="">All Service Types</option>
            {serviceTypes.map(type => (
              <option key={type} value={type}>{type.replace('_', ' ').toUpperCase()}</option>
            ))}
          </select>
          
          <select
            value={selectedPriceRange}
            onChange={(e) => setSelectedPriceRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
          >
            <option value="">All Price Ranges</option>
            {priceRanges.map(range => (
              <option key={range} value={range}>{range}</option>
            ))}
          </select>

          <button
            onClick={() => {
              setSelectedServiceType('');
              setSelectedPriceRange('');
            }}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            Clear Filters
          </button>
          
          <button
            onClick={fetchPhotographyServices}
            className="px-4 py-2 bg-pink-600 text-white rounded-md hover:bg-pink-700 transition-colors"
          >
            Refresh Services
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Services List */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
        </div>
      ) : services.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No photography services found with current filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, index) => (
            <div key={index} className="bg-white shadow rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">{service.name}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    service.tier === 'album_cover' ? 'bg-pink-100 text-pink-800' :
                    service.tier === 'promotional' ? 'bg-purple-100 text-purple-800' :
                    service.tier === 'event' ? 'bg-indigo-100 text-indigo-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {service.tier?.replace('_', ' ')}
                  </span>
                </div>
                
                {service.specialties && (
                  <div className="mb-3">
                    <div className="text-sm text-gray-600 mb-2">Specialties:</div>
                    <div className="flex flex-wrap gap-1">
                      {service.specialties.map((specialty, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                          {specialty.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {service.price_range && (
                  <div className="mb-3">
                    <span className="text-sm text-gray-600">Price Range: </span>
                    <span className="font-semibold text-green-600">{service.price_range}</span>
                  </div>
                )}
                
                {service.territories && (
                  <div className="mb-3">
                    <span className="text-sm text-gray-600">Available in: </span>
                    <span className="text-sm">{service.territories.join(', ')}</span>
                  </div>
                )}
                
                <button className="w-full px-4 py-2 bg-pink-600 text-white rounded-md hover:bg-pink-700 transition-colors">
                  Request Quote
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Video Production Services Component
export const VideoProductionServices = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedProductionType, setSelectedProductionType] = useState('');

  useEffect(() => {
    fetchVideoServices();
  }, [selectedProductionType]);

  const fetchVideoServices = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedProductionType) params.append('production_type', selectedProductionType);

      const response = await axios.get(`${API}/industry/video/production?${params}`);
      setServices(response.data.services);
    } catch (error) {
      setError('Failed to load video production services');
      console.error('Error fetching video services:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Video Production Header */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-lg p-6">
        <div className="flex items-center">
          <div className="p-3 bg-white bg-opacity-20 rounded-full mr-4">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold">Video Production Services</h2>
            <p className="text-red-100">Professional video production for Big Mann Entertainment</p>
          </div>
        </div>
      </div>

      {/* Production Type Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white shadow-lg rounded-lg p-6 border-l-4 border-red-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Music Video Production</h3>
          <p className="text-sm text-gray-600 mb-4">High-quality music videos, lyric videos, and promotional content for artists.</p>
          <div className="space-y-2 text-xs text-gray-500">
            <div>• Concept development and storyboarding</div>
            <div>• Professional filming equipment (4K/8K)</div>
            <div>• Post-production and editing</div>
            <div>• Color grading and sound design</div>
            <div>• Multiple format delivery</div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">$5,000-$50,000</span>
          </div>
        </div>

        <div className="bg-white shadow-lg rounded-lg p-6 border-l-4 border-orange-500">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Commercial Production</h3>
          <p className="text-sm text-gray-600 mb-4">Corporate videos, commercials, and brand content for business promotion.</p>
          <div className="space-y-2 text-xs text-gray-500">
            <div>• Brand storytelling</div>
            <div>• Commercial advertisements</div>
            <div>• Corporate documentaries</div>
            <div>• Training and educational videos</div>
            <div>• Social media content</div>
          </div>
          <div className="mt-4">
            <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">$2,000-$25,000</span>
          </div>
        </div>
      </div>

      {/* Filter and Services List */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Available Services</h3>
          <select
            value={selectedProductionType}
            onChange={(e) => setSelectedProductionType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="">All Production Types</option>
            <option value="music_videos">Music Videos</option>
            <option value="production_companies">Production Companies</option>
            <option value="commercial">Commercial</option>
            <option value="documentary">Documentary</option>
          </select>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
          </div>
        ) : services.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No video production services found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {services.map((service, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-lg font-semibold text-gray-900">{service.name}</h4>
                  <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                    {service.tier?.replace('_', ' ')}
                  </span>
                </div>
                
                {service.specialties && (
                  <div className="mb-3">
                    <div className="flex flex-wrap gap-1">
                      {service.specialties.map((specialty, idx) => (
                        <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                          {specialty.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {service.price_range && (
                  <div className="mb-3">
                    <span className="text-sm text-gray-600">Budget: </span>
                    <span className="font-semibold text-green-600">{service.price_range}</span>
                  </div>
                )}
                
                <button className="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors">
                  Get Proposal
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Monetization Opportunities Component
export const MonetizationOpportunities = () => {
  const [opportunities, setOpportunities] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedContentType, setSelectedContentType] = useState('all');

  useEffect(() => {
    fetchMonetizationOpportunities();
  }, [selectedContentType]);

  const fetchMonetizationOpportunities = async () => {
    try {
      const response = await axios.get(`${API}/industry/monetization/opportunities?content_type=${selectedContentType}`);
      setOpportunities(response.data.monetization_opportunities);
    } catch (error) {
      setError('Failed to load monetization opportunities');
      console.error('Error fetching monetization opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Monetization Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg p-6">
        <div className="flex items-center">
          <div className="p-3 bg-white bg-opacity-20 rounded-full mr-4">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold">Monetization Opportunities</h2>
            <p className="text-green-100">Revenue optimization across all entertainment platforms</p>
          </div>
        </div>
      </div>

      {/* Content Type Filter */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Select Content Type</h3>
          <select
            value={selectedContentType}
            onChange={(e) => setSelectedContentType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="all">All Content Types</option>
            <option value="photography">Photography</option>
            <option value="video">Video</option>
            <option value="audio">Audio/Music</option>
            <option value="gaming">Gaming</option>
          </select>
        </div>
      </div>

      {/* Revenue Opportunities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {opportunities.photography && (
          <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-pink-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Photography Revenue</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Stock Platforms:</span>
                <span className="font-semibold">{opportunities.photography.stock_platforms}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Social Media:</span>
                <span className="font-semibold">{opportunities.photography.social_media}</span>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-xl font-bold text-green-600">{opportunities.photography.estimated_revenue_range}</div>
              <div className="text-xs text-gray-500">Monthly Potential</div>
            </div>
          </div>
        )}

        {opportunities.video && (
          <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-red-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Video Revenue</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Production Services:</span>
                <span className="font-semibold">{opportunities.video.production_services}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Streaming Platforms:</span>
                <span className="font-semibold">{opportunities.video.streaming_platforms}</span>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-xl font-bold text-green-600">{opportunities.video.estimated_revenue_range}</div>
              <div className="text-xs text-gray-500">Per Project</div>
            </div>
          </div>
        )}

        {opportunities.audio && (
          <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-purple-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Audio Revenue</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Streaming Platforms:</span>
                <span className="font-semibold">{opportunities.audio.streaming_platforms}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Podcast Platforms:</span>
                <span className="font-semibold">{opportunities.audio.podcast_platforms}</span>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-xl font-bold text-green-600">{opportunities.audio.estimated_revenue_range}</div>
              <div className="text-xs text-gray-500">Per Stream</div>
            </div>
          </div>
        )}

        {opportunities.gaming && (
          <div className="bg-white shadow-lg rounded-lg p-6 border-t-4 border-indigo-500">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Gaming Revenue</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Gaming Platforms:</span>
                <span className="font-semibold">{opportunities.gaming.platforms}</span>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-xl font-bold text-green-600">{opportunities.gaming.estimated_revenue_range}</div>
              <div className="text-xs text-gray-500">Per License</div>
            </div>
          </div>
        )}
      </div>

      {/* Summary Card */}
      {opportunities.summary && (
        <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg p-6">
          <h3 className="text-xl font-bold mb-4">Total Revenue Potential</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold">{opportunities.summary.total_platforms}</div>
              <div className="text-sm text-blue-100">Total Platforms</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{opportunities.summary.categories_covered}</div>
              <div className="text-sm text-blue-100">Revenue Categories</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{opportunities.summary.estimated_monthly_potential}</div>
              <div className="text-sm text-blue-100">Monthly Potential</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Music Data Exchange (MDX) Integration Component
export const MusicDataExchange = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [newTrack, setNewTrack] = useState({
    title: '',
    artist_name: 'Big Mann Entertainment',
    album_title: '',
    duration: '',
    isrc: '',
    upc: ''
  });

  useEffect(() => {
    fetchMDXDashboard();
    fetchMDXTracks();
  }, []);

  const fetchMDXDashboard = async () => {
    try {
      const response = await axios.get(`${API}/industry/mdx/dashboard`);
      setDashboardData(response.data.mdx_dashboard);
    } catch (error) {
      console.error('Error fetching MDX dashboard:', error);
      setError('Failed to load MDX dashboard');
    }
  };

  const fetchMDXTracks = async () => {
    try {
      const response = await axios.get(`${API}/industry/mdx/tracks?big_mann_release=true`);
      setTracks(response.data.tracks);
    } catch (error) {
      console.error('Error fetching MDX tracks:', error);
      setError('Failed to load MDX tracks');
    } finally {
      setLoading(false);
    }
  };

  const handleTrackSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/industry/mdx/track/sync`, newTrack);
      if (response.data.success) {
        setNewTrack({
          title: '',
          artist_name: 'Big Mann Entertainment',
          album_title: '',
          duration: '',
          isrc: '',
          upc: ''
        });
        fetchMDXTracks();
        fetchMDXDashboard();
      }
    } catch (error) {
      console.error('Error syncing track:', error);
      setError('Failed to sync track with MDX');
    }
  };

  const initializeMDX = async () => {
    try {
      const response = await axios.post(`${API}/industry/mdx/initialize`);
      if (response.data.success) {
        fetchMDXDashboard();
        setError('');
      }
    } catch (error) {
      console.error('Error initializing MDX:', error);
      setError('Failed to initialize MDX integration');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* MDX Header */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white rounded-lg p-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">Music Data Exchange (MDX)</h2>
            <p className="text-blue-100 text-lg">Comprehensive metadata and rights management for Big Mann Entertainment</p>
            <div className="mt-2">
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm mr-2">Real-Time Sync</span>
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm mr-2">Rights Management</span>
              <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">DDEX Compliant</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{dashboardData.big_mann_entertainment?.total_mdx_tracks || 0}</div>
            <div className="text-sm text-blue-100">Managed Tracks</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {['dashboard', 'tracks', 'upload', 'rights'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-6 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Analytics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold">{dashboardData.analytics?.total_tracks_managed || 0}</div>
                      <div className="text-sm text-blue-100">Total Tracks</div>
                    </div>
                    <svg className="w-8 h-8 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12 6.5v.5M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-6.5c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2z" />
                    </svg>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold">{Math.round(dashboardData.analytics?.rights_clearance_rate || 0)}%</div>
                      <div className="text-sm text-green-100">Rights Cleared</div>
                    </div>
                    <svg className="w-8 h-8 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold">{Math.round(dashboardData.analytics?.metadata_completeness || 0)}%</div>
                      <div className="text-sm text-purple-100">Metadata Quality</div>
                    </div>
                    <svg className="w-8 h-8 text-purple-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-2xl font-bold">${(dashboardData.big_mann_entertainment?.big_mann_revenue_impact || 0).toLocaleString()}</div>
                      <div className="text-sm text-orange-100">Revenue Impact</div>
                    </div>
                    <svg className="w-8 h-8 text-orange-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* MDX Status */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">MDX Integration Status</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Platform Status</div>
                    <div className="text-lg font-semibold text-green-600">✅ Fully Operational</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Real-Time Sync</div>
                    <div className="text-lg font-semibold text-green-600">✅ Active</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Rights Management</div>
                    <div className="text-lg font-semibold text-green-600">✅ Automated</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Revenue Optimization</div>
                    <div className="text-lg font-semibold text-green-600">✅ Active</div>
                  </div>
                </div>
              </div>

              {/* Initialize MDX Button */}
              <div className="text-center">
                <button
                  onClick={initializeMDX}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                >
                  🔄 Refresh MDX Integration
                </button>
              </div>
            </div>
          )}

          {activeTab === 'tracks' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">MDX Managed Tracks</h3>
                <div className="text-sm text-gray-600">{tracks.length} tracks in system</div>
              </div>

              {tracks.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12 6.5v.5M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-6.5c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No tracks found</h3>
                  <p className="mt-1 text-sm text-gray-500">Get started by uploading your first track.</p>
                </div>
              ) : (
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Track</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Artist</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ISRC</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rights Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MDX Status</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {tracks.map((track, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{track.title}</div>
                            <div className="text-sm text-gray-500">{track.album_title}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {track.artist_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {track.isrc || 'Pending'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              track.rights_clearance_status === 'cleared'
                                ? 'bg-green-100 text-green-800'
                                : track.rights_clearance_status === 'pending'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {track.rights_clearance_status || 'unknown'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                              {track.mdx_track_id ? 'Synced' : 'Pending'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Upload New Track to MDX</h3>
              
              <form onSubmit={handleTrackSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Track Title</label>
                    <input
                      type="text"
                      value={newTrack.title}
                      onChange={(e) => setNewTrack({...newTrack, title: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Artist Name</label>
                    <input
                      type="text"
                      value={newTrack.artist_name}
                      onChange={(e) => setNewTrack({...newTrack, artist_name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Album Title</label>
                    <input
                      type="text"
                      value={newTrack.album_title}
                      onChange={(e) => setNewTrack({...newTrack, album_title: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Duration (seconds)</label>
                    <input
                      type="number"
                      value={newTrack.duration}
                      onChange={(e) => setNewTrack({...newTrack, duration: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">ISRC Code</label>
                    <input
                      type="text"
                      value={newTrack.isrc}
                      onChange={(e) => setNewTrack({...newTrack, isrc: e.target.value})}
                      placeholder="e.g., QZ9H82400001"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">UPC Code</label>
                    <input
                      type="text"
                      value={newTrack.upc}
                      onChange={(e) => setNewTrack({...newTrack, upc: e.target.value})}
                      placeholder="e.g., 860004340201"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setNewTrack({
                      title: '',
                      artist_name: 'Big Mann Entertainment',
                      album_title: '',
                      duration: '',
                      isrc: '',
                      upc: ''
                    })}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Clear
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Sync with MDX
                  </button>
                </div>
              </form>

              {/* Information Card */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div className="flex">
                  <svg className="h-5 w-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div className="text-sm text-blue-700">
                    <h4 className="font-medium mb-2">MDX Integration Benefits</h4>
                    <ul className="space-y-1 text-xs">
                      <li>• Automated metadata distribution across platforms</li>
                      <li>• Real-time rights clearance and management</li>
                      <li>• DDEX compliant data exchange</li>
                      <li>• Revenue optimization through proper attribution</li>
                      <li>• Global territory and licensing management</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'rights' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Rights Management</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h4 className="font-semibold text-green-800 mb-3">Big Mann Entertainment Rights</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Publishing Rights:</span>
                      <span className="font-semibold text-green-700">100%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Mechanical Rights:</span>
                      <span className="font-semibold text-green-700">100%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Performance Rights:</span>
                      <span className="font-semibold text-green-700">50%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Sync Rights:</span>
                      <span className="font-semibold text-green-700">100%</span>
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-green-600">
                    IPI: 813048171 (Publisher)
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h4 className="font-semibold text-blue-800 mb-3">John LeGerron Spivey Rights</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Songwriter Rights:</span>
                      <span className="font-semibold text-blue-700">100%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Performance Rights:</span>
                      <span className="font-semibold text-blue-700">50%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Composer Credits:</span>
                      <span className="font-semibold text-blue-700">100%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Lyricist Credits:</span>
                      <span className="font-semibold text-blue-700">100%</span>
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-blue-600">
                    IPI: 578413032 (Songwriter) | ISNI: 0000000491551894
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h4 className="font-semibold text-yellow-800 mb-3">Rights Management Features</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-yellow-700">
                  <div>
                    <div className="font-medium">✅ Automated Clearance</div>
                    <div className="text-xs">Real-time rights verification and clearance</div>
                  </div>
                  <div>
                    <div className="font-medium">✅ Global Management</div>
                    <div className="text-xs">Multi-territory rights administration</div>
                  </div>
                  <div>
                    <div className="font-medium">✅ Revenue Tracking</div>
                    <div className="text-xs">Comprehensive royalty monitoring</div>
                  </div>
                  <div>
                    <div className="font-medium">✅ Compliance Monitoring</div>
                    <div className="text-xs">DDEX and industry standard compliance</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
    </div>
  );
};

// Backward compatibility - IPIManagement is now an alias for IndustryIdentifiersManagement  
export const IPIManagement = IndustryIdentifiersManagement;