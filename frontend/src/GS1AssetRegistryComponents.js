import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'https://support-desk-30.preview.emergentagent.com';

// GS1 Asset Registry Components
export const GS1AssetRegistry = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [assets, setAssets] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'assets', name: 'Assets', icon: '📁' },
    { id: 'identifiers', name: 'Identifiers', icon: '🏷️' },
    { id: 'digital-links', name: 'Digital Links', icon: '🔗' },
    { id: 'validation', name: 'Validation', icon: '✅' },
    { id: 'analytics', name: 'Analytics', icon: '📈' }
  ];

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE}/api/gs1/analytics`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        setAnalytics(response.data);
      }
    } catch (error) {
      console.error('Error fetching GS1 analytics:', error);
      setError('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAssets = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE}/api/gs1/assets`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data && response.data.assets) {
        setAssets(response.data.assets);
      }
    } catch (error) {
      console.error('Error fetching GS1 assets:', error);
      setError('Failed to load assets');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'overview' || activeTab === 'analytics') {
      fetchAnalytics();
    }
    if (activeTab === 'assets') {
      fetchAssets();
    }
  }, [activeTab, fetchAnalytics, fetchAssets]);

  return (
    <div className="gs1-asset-registry bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-t-lg">
        <div className="flex items-center space-x-3">
          <div className="text-3xl">🏷️</div>
          <div>
            <h1 className="text-2xl font-bold">GS1 Asset Registry</h1>
            <p className="text-purple-100">Global Trade Item Numbers & Digital Link Management</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6 py-3">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-purple-100 text-purple-700'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            <p className="mt-2 text-gray-600">Loading...</p>
          </div>
        )}

        {activeTab === 'overview' && <GS1OverviewTab analytics={analytics} />}
        {activeTab === 'assets' && <GS1AssetsTab assets={assets} onRefresh={fetchAssets} />}
        {activeTab === 'identifiers' && <GS1IdentifiersTab />}
        {activeTab === 'digital-links' && <GS1DigitalLinksTab />}
        {activeTab === 'validation' && <GS1ValidationTab />}
        {activeTab === 'analytics' && <GS1AnalyticsTab analytics={analytics} />}
      </div>
    </div>
  );
};

// Overview Tab
const GS1OverviewTab = ({ analytics }) => {
  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
          <div className="flex items-center">
            <div className="text-blue-600 text-2xl mr-3">📁</div>
            <div>
              <p className="text-sm text-blue-600 font-medium">Total Assets</p>
              <p className="text-2xl font-bold text-blue-900">{analytics?.total_assets || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
          <div className="flex items-center">
            <div className="text-green-600 text-2xl mr-3">🏷️</div>
            <div>
              <p className="text-sm text-green-600 font-medium">Generated IDs</p>
              <p className="text-2xl font-bold text-green-900">
                {Object.values(analytics?.identifiers_by_type || {}).reduce((a, b) => a + b, 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg border border-purple-200">
          <div className="flex items-center">
            <div className="text-purple-600 text-2xl mr-3">🔗</div>
            <div>
              <p className="text-sm text-purple-600 font-medium">Digital Links</p>
              <p className="text-2xl font-bold text-purple-900">{analytics?.digital_link_scans || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-lg border border-orange-200">
          <div className="flex items-center">
            <div className="text-orange-600 text-2xl mr-3">📊</div>
            <div>
              <p className="text-sm text-orange-600 font-medium">Asset Types</p>
              <p className="text-2xl font-bold text-orange-900">
                {Object.keys(analytics?.assets_by_type || {}).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="mr-2">🚀</span>
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="bg-white border border-gray-200 rounded-lg p-4 text-center hover:bg-gray-50 transition-colors">
            <div className="text-2xl mb-2">🎵</div>
            <div className="text-sm font-medium text-gray-900">Create Music Asset</div>
          </button>
          <button className="bg-white border border-gray-200 rounded-lg p-4 text-center hover:bg-gray-50 transition-colors">
            <div className="text-2xl mb-2">🎬</div>
            <div className="text-sm font-medium text-gray-900">Create Video Asset</div>
          </button>
          <button className="bg-white border border-gray-200 rounded-lg p-4 text-center hover:bg-gray-50 transition-colors">
            <div className="text-2xl mb-2">🖼️</div>
            <div className="text-sm font-medium text-gray-900">Create Image Asset</div>
          </button>
          <button className="bg-white border border-gray-200 rounded-lg p-4 text-center hover:bg-gray-50 transition-colors">
            <div className="text-2xl mb-2">👕</div>
            <div className="text-sm font-medium text-gray-900">Create Merchandise</div>
          </button>
        </div>
      </div>

      {/* GS1 Standards Compliance */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
          <span className="mr-2">✅</span>
          GS1 Standards Compliance
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-700">GTIN (Global Trade Item Number)</span>
              <span className="text-sm font-medium text-green-600">✅ Compliant</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-700">GLN (Global Location Number)</span>
              <span className="text-sm font-medium text-green-600">✅ Compliant</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-700">GDTI (Global Document Type Identifier)</span>
              <span className="text-sm font-medium text-green-600">✅ Compliant</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-700">ISRC (International Standard Recording Code)</span>
              <span className="text-sm font-medium text-green-600">✅ Compliant</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-700">ISAN (International Standard Audiovisual Number)</span>
              <span className="text-sm font-medium text-green-600">✅ Compliant</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-blue-700">GS1 Digital Link</span>
              <span className="text-sm font-medium text-green-600">✅ Compliant</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Assets Tab
const GS1AssetsTab = ({ assets, onRefresh }) => {
  const [showCreateModal, setShowCreateModal] = useState(false);

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">GS1 Assets</h3>
        <div className="flex space-x-3">
          <button
            onClick={onRefresh}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            🔄 Refresh
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700"
          >
            ➕ Create Asset
          </button>
        </div>
      </div>

      {/* Assets Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Asset
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Identifiers
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {assets.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                  <div className="text-4xl mb-2">📁</div>
                  <p>No assets found. Create your first GS1 asset to get started.</p>
                </td>
              </tr>
            ) : (
              assets.map((asset) => (
                <tr key={asset.asset_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-2xl mr-3">
                        {asset.asset_type === 'music' && '🎵'}
                        {asset.asset_type === 'video' && '🎬'}
                        {asset.asset_type === 'image' && '🖼️'}
                        {asset.asset_type === 'merchandise' && '👕'}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {asset.metadata?.title || 'Untitled'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {asset.metadata?.description?.substring(0, 50)}...
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {asset.asset_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="space-y-1">
                      {Object.keys(asset.identifiers || {}).map((type) => (
                        <span key={type} className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800 mr-1">
                          {type.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      asset.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {asset.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(asset.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-purple-600 hover:text-purple-900 mr-3">View</button>
                    <button className="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                    <button className="text-green-600 hover:text-green-900">Digital Link</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Asset Modal */}
      {showCreateModal && (
        <CreateAssetModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            onRefresh();
          }}
        />
      )}
    </div>
  );
};

// Identifiers Tab
const GS1IdentifiersTab = () => {
  const [selectedType, setSelectedType] = useState('gtin');
  const [identifierValue, setIdentifierValue] = useState('');
  const [validationResult, setValidationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const identifierTypes = [
    { id: 'gtin', name: 'GTIN', description: 'Global Trade Item Number', icon: '🏷️' },
    { id: 'gln', name: 'GLN', description: 'Global Location Number', icon: '📍' },
    { id: 'gdti', name: 'GDTI', description: 'Global Document Type Identifier', icon: '📄' },
    { id: 'isrc', name: 'ISRC', description: 'International Standard Recording Code', icon: '🎵' },
    { id: 'isan', name: 'ISAN', description: 'International Standard Audiovisual Number', icon: '🎬' }
  ];

  const validateIdentifier = async () => {
    if (!identifierValue.trim()) return;

    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_BASE}/api/gs1/identifiers/validate`, {
        identifier_value: identifierValue,
        identifier_type: selectedType
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setValidationResult(response.data);
    } catch (error) {
      console.error('Error validating identifier:', error);
      setValidationResult({
        is_valid: false,
        errors: ['Failed to validate identifier'],
        suggestions: []
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Identifier Types */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Supported Identifier Types</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {identifierTypes.map((type) => (
            <div
              key={type.id}
              className={`bg-white border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedType === type.id ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedType(type.id)}
            >
              <div className="flex items-center">
                <div className="text-2xl mr-3">{type.icon}</div>
                <div>
                  <div className="font-medium text-gray-900">{type.name}</div>
                  <div className="text-sm text-gray-600">{type.description}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Identifier Validation */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Validate Identifier</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {identifierTypes.find(t => t.id === selectedType)?.name} Value
            </label>
            <div className="flex space-x-3">
              <input
                type="text"
                value={identifierValue}
                onChange={(e) => setIdentifierValue(e.target.value)}
                placeholder={`Enter ${selectedType.toUpperCase()} value`}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <button
                onClick={validateIdentifier}
                disabled={loading || !identifierValue.trim()}
                className="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 disabled:opacity-50"
              >
                {loading ? '⏳' : '✅'} Validate
              </button>
            </div>
          </div>

          {validationResult && (
            <div className={`p-4 rounded-lg border ${
              validationResult.is_valid
                ? 'bg-green-50 border-green-200'
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-center mb-2">
                <span className="text-xl mr-2">
                  {validationResult.is_valid ? '✅' : '❌'}
                </span>
                <span className={`font-medium ${
                  validationResult.is_valid ? 'text-green-800' : 'text-red-800'
                }`}>
                  {validationResult.is_valid ? 'Valid Identifier' : 'Invalid Identifier'}
                </span>
              </div>
              
              {validationResult.errors && validationResult.errors.length > 0 && (
                <div className="mt-2">
                  <p className="text-sm font-medium text-red-700 mb-1">Errors:</p>
                  <ul className="text-sm text-red-600 list-disc list-inside">
                    {validationResult.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {validationResult.suggestions && validationResult.suggestions.length > 0 && (
                <div className="mt-2">
                  <p className="text-sm font-medium text-blue-700 mb-1">Suggestions:</p>
                  <ul className="text-sm text-blue-600 list-disc list-inside">
                    {validationResult.suggestions.map((suggestion, index) => (
                      <li key={index}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {validationResult.is_valid && (
                <div className="mt-2">
                  <p className="text-sm text-green-700">
                    <strong>Formatted Value:</strong> {validationResult.formatted_value}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Digital Links Tab
const GS1DigitalLinksTab = () => {
  return (
    <div className="space-y-6">
      <div className="text-center py-8">
        <div className="text-4xl mb-4">🔗</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">GS1 Digital Links</h3>
        <p className="text-gray-600">Create and manage GS1 Digital Link URIs and QR codes</p>
        <button className="mt-4 px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700">
          Create Digital Link
        </button>
      </div>
    </div>
  );
};

// Validation Tab
const GS1ValidationTab = () => {
  return (
    <div className="space-y-6">
      <div className="text-center py-8">
        <div className="text-4xl mb-4">✅</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Identifier Validation</h3>
        <p className="text-gray-600">Batch validation and compliance checking</p>
      </div>
    </div>
  );
};

// Analytics Tab
const GS1AnalyticsTab = ({ analytics }) => {
  return (
    <div className="space-y-6">
      {analytics && (
        <>
          {/* Asset Type Distribution */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Assets by Type</h3>
            <div className="space-y-3">
              {Object.entries(analytics.assets_by_type || {}).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="text-xl mr-3">
                      {type === 'music' && '🎵'}
                      {type === 'video' && '🎬'}
                      {type === 'image' && '🖼️'}
                      {type === 'merchandise' && '👕'}
                    </div>
                    <span className="font-medium text-gray-900 capitalize">{type}</span>
                  </div>
                  <span className="text-lg font-semibold text-gray-700">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Identifier Type Distribution */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Identifiers by Type</h3>
            <div className="space-y-3">
              {Object.entries(analytics.identifiers_by_type || {}).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="text-xl mr-3">🏷️</div>
                    <span className="font-medium text-gray-900 uppercase">{type}</span>
                  </div>
                  <span className="text-lg font-semibold text-gray-700">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Create Asset Modal
const CreateAssetModal = ({ onClose, onSuccess }) => {
  const [assetType, setAssetType] = useState('music');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    // Music-specific
    artist: '',
    album: '',
    genre: '',
    duration_seconds: '',
    // Video-specific
    director: '',
    producer: '',
    runtime_minutes: '',
    resolution: '',
    // Image-specific
    photographer: '',
    width_pixels: '',
    height_pixels: '',
    dpi: '',
    // Merchandise-specific
    brand: '',
    size: '',
    color: '',
    material: '',
    price: ''
  });
  const [selectedIdentifiers, setSelectedIdentifiers] = useState(['gtin']);
  const [loading, setLoading] = useState(false);

  const assetTypes = [
    { id: 'music', name: 'Music', icon: '🎵' },
    { id: 'video', name: 'Video', icon: '🎬' },
    { id: 'image', name: 'Image', icon: '🖼️' },
    { id: 'merchandise', name: 'Merchandise', icon: '👕' }
  ];

  const identifierTypes = [
    { id: 'gtin', name: 'GTIN', description: 'Global Trade Item Number' },
    { id: 'gln', name: 'GLN', description: 'Global Location Number' },
    { id: 'gdti', name: 'GDTI', description: 'Global Document Type Identifier' },
    { id: 'isrc', name: 'ISRC', description: 'International Standard Recording Code' },
    { id: 'isan', name: 'ISAN', description: 'International Standard Audiovisual Number' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Prepare metadata based on asset type
      const metadata = { ...formData };
      
      // Convert numeric fields
      if (metadata.duration_seconds) metadata.duration_seconds = parseInt(metadata.duration_seconds);
      if (metadata.runtime_minutes) metadata.runtime_minutes = parseInt(metadata.runtime_minutes);
      if (metadata.width_pixels) metadata.width_pixels = parseInt(metadata.width_pixels);
      if (metadata.height_pixels) metadata.height_pixels = parseInt(metadata.height_pixels);
      if (metadata.dpi) metadata.dpi = parseInt(metadata.dpi);
      if (metadata.price) metadata.price = parseFloat(metadata.price);

      const response = await axios.post(`${API_BASE}/api/gs1/assets`, {
        asset_type: assetType,
        metadata: metadata,
        generate_identifiers: selectedIdentifiers
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        onSuccess();
      }
    } catch (error) {
      console.error('Error creating asset:', error);
      alert('Failed to create asset');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-90vh overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Create GS1 Asset</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Asset Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Asset Type</label>
              <div className="grid grid-cols-2 gap-3">
                {assetTypes.map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setAssetType(type.id)}
                    className={`flex items-center justify-center p-3 border rounded-lg transition-colors ${
                      assetType === type.id
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <span className="text-xl mr-2">{type.icon}</span>
                    <span className="font-medium">{type.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            {/* Asset-specific fields */}
            {assetType === 'music' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Artist</label>
                  <input
                    type="text"
                    value={formData.artist}
                    onChange={(e) => setFormData({...formData, artist: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Album</label>
                  <input
                    type="text"
                    value={formData.album}
                    onChange={(e) => setFormData({...formData, album: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Genre</label>
                  <input
                    type="text"
                    value={formData.genre}
                    onChange={(e) => setFormData({...formData, genre: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Duration (seconds)</label>
                  <input
                    type="number"
                    value={formData.duration_seconds}
                    onChange={(e) => setFormData({...formData, duration_seconds: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
            )}

            {assetType === 'video' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Director</label>
                  <input
                    type="text"
                    value={formData.director}
                    onChange={(e) => setFormData({...formData, director: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Producer</label>
                  <input
                    type="text"
                    value={formData.producer}
                    onChange={(e) => setFormData({...formData, producer: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Runtime (minutes)</label>
                  <input
                    type="number"
                    value={formData.runtime_minutes}
                    onChange={(e) => setFormData({...formData, runtime_minutes: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Resolution</label>
                  <select
                    value={formData.resolution}
                    onChange={(e) => setFormData({...formData, resolution: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Select Resolution</option>
                    <option value="720p">720p HD</option>
                    <option value="1080p">1080p Full HD</option>
                    <option value="4K">4K Ultra HD</option>
                    <option value="8K">8K</option>
                  </select>
                </div>
              </div>
            )}

            {assetType === 'image' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Photographer</label>
                  <input
                    type="text"
                    value={formData.photographer}
                    onChange={(e) => setFormData({...formData, photographer: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">DPI</label>
                  <input
                    type="number"
                    value={formData.dpi}
                    onChange={(e) => setFormData({...formData, dpi: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Width (pixels)</label>
                  <input
                    type="number"
                    value={formData.width_pixels}
                    onChange={(e) => setFormData({...formData, width_pixels: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Height (pixels)</label>
                  <input
                    type="number"
                    value={formData.height_pixels}
                    onChange={(e) => setFormData({...formData, height_pixels: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
            )}

            {assetType === 'merchandise' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Brand</label>
                  <input
                    type="text"
                    value={formData.brand}
                    onChange={(e) => setFormData({...formData, brand: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Size</label>
                  <input
                    type="text"
                    value={formData.size}
                    onChange={(e) => setFormData({...formData, size: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
                  <input
                    type="text"
                    value={formData.color}
                    onChange={(e) => setFormData({...formData, color: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Material</label>
                  <input
                    type="text"
                    value={formData.material}
                    onChange={(e) => setFormData({...formData, material: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.price}
                    onChange={(e) => setFormData({...formData, price: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
            )}

            {/* Identifier Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Generate Identifiers</label>
              <div className="space-y-2">
                {identifierTypes.map((type) => (
                  <label key={type.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedIdentifiers.includes(type.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedIdentifiers([...selectedIdentifiers, type.id]);
                        } else {
                          setSelectedIdentifiers(selectedIdentifiers.filter(id => id !== type.id));
                        }
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm">
                      <strong>{type.name}</strong> - {type.description}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !formData.title.trim()}
                className="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 disabled:opacity-50"
              >
                {loading ? '⏳ Creating...' : '✅ Create Asset'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default GS1AssetRegistry;