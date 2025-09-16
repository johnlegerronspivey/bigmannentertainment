import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://musicdao-platform.preview.emergentagent.com';

// Main MDE Integration Component
export const MDEIntegration = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [activeTab, setActiveTab] = useState('overview');
  const [analytics, setAnalytics] = useState(null);
  const [metadata, setMetadata] = useState([]);
  const [validations, setValidations] = useState([]);
  const [qualitySummary, setQualitySummary] = useState(null);
  const [standards, setStandards] = useState([]);
  const [loading, setLoading] = useState(false);

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '🏠' },
    { id: 'metadata', name: 'Metadata', icon: '📋' },
    { id: 'validation', name: 'Validation', icon: '✅' },
    { id: 'quality', name: 'Quality Reports', icon: '📊' },
    { id: 'standards', name: 'Standards', icon: '📐' },
    { id: 'submit', name: 'Submit Metadata', icon: '➕' }
  ];

  const fetchMDEData = async () => {
    setLoading(true);
    try {
      const [analyticsRes, metadataRes, validationsRes, qualityRes, standardsRes] = await Promise.all([
        axios.get(`${API}/api/mde/analytics?user_id=user_123`),
        axios.get(`${API}/api/mde/metadata?user_id=user_123&limit=10`),
        axios.get(`${API}/api/mde/validations?user_id=user_123`),
        axios.get(`${API}/api/mde/quality/summary?user_id=user_123`),
        axios.get(`${API}/api/mde/standards?user_id=user_123`)
      ]);

      if (analyticsRes.data.success) setAnalytics(analyticsRes.data.analytics);
      if (metadataRes.data.success) setMetadata(metadataRes.data.metadata);
      if (validationsRes.data.success) setValidations(validationsRes.data.validations);
      if (qualityRes.data.success) setQualitySummary(qualityRes.data.summary);
      if (standardsRes.data.success) setStandards(standardsRes.data.standards);
    } catch (error) {
      console.error('Error fetching MDE data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMDEData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Music Data Exchange</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Industry metadata standardization and data quality management</p>
        </div>
        <div className="flex space-x-2">
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
            📐 Industry Standard
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            📊 Data Quality
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && analytics && (
        <div className="space-y-6">
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Metadata Entries</p>
                  <p className="text-2xl font-bold text-blue-600">{analytics.overview.total_metadata_entries}</p>
                </div>
                <span className="text-2xl">📋</span>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Quality Score</p>
                  <p className="text-2xl font-bold text-green-600">{analytics.overview.average_quality_score}/100</p>
                </div>
                <span className="text-2xl">⭐</span>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Validations</p>
                  <p className="text-2xl font-bold text-purple-600">{analytics.overview.total_validations}</p>
                </div>
                <span className="text-2xl">✅</span>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Data Exchanges</p>
                  <p className="text-2xl font-bold text-orange-600">{analytics.overview.total_data_exchanges}</p>
                </div>
                <span className="text-2xl">🔄</span>
              </div>
            </div>
          </div>

          {/* Quality Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Data Quality Metrics</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Average Completeness</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${analytics.overview.average_completeness}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{analytics.overview.average_completeness}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Average Accuracy</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${analytics.overview.average_accuracy}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{analytics.overview.average_accuracy}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">High Quality Entries</span>
                  <span className="font-semibold text-green-600">
                    {analytics.quality_metrics.high_quality_entries}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Entries with Issues</span>
                  <span className="font-semibold text-yellow-600">
                    {analytics.quality_metrics.entries_with_issues}
                  </span>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Standard Adoption</h3>
              <div className="space-y-4">
                {Object.entries(analytics.standard_adoption || {}).map(([standard, count]) => (
                  <div key={standard} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">
                      {standard.replace('_', ' ')}
                    </span>
                    <span className="font-semibold text-purple-600">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Validation Statistics */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Validation Results</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {analytics.validation_statistics.valid}
                </div>
                <div className="text-sm text-green-700 dark:text-green-300">Valid</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {analytics.validation_statistics.warning}
                </div>
                <div className="text-sm text-yellow-700 dark:text-yellow-300">Warnings</div>
              </div>
              <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {analytics.validation_statistics.invalid}
                </div>
                <div className="text-sm text-red-700 dark:text-red-300">Invalid</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Metadata Tab */}
      {activeTab === 'metadata' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Metadata Entries ({metadata.length})</h3>
            <button 
              onClick={() => setActiveTab('submit')}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Submit New Metadata
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {metadata.map((entry) => (
              <div key={entry.metadata_id} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">{entry.title}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">by {entry.artist}</p>
                    {entry.album && (
                      <p className="text-sm text-gray-500 dark:text-gray-500">Album: {entry.album}</p>
                    )}
                  </div>
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    Submitted
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">ISRC:</span>
                    <span className="text-gray-900 dark:text-white font-mono">{entry.isrc || 'Not assigned'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">UPC:</span>
                    <span className="text-gray-900 dark:text-white font-mono">{entry.upc || 'Not assigned'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Duration:</span>
                    <span className="text-gray-900 dark:text-white">
                      {entry.duration_ms ? `${Math.floor(entry.duration_ms / 60000)}:${((entry.duration_ms % 60000) / 1000).toFixed(0).padStart(2, '0')}` : 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Genres:</span>
                    <span className="text-gray-900 dark:text-white">{entry.genre?.join(', ') || 'None'}</span>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 text-sm">
                    Validate
                  </button>
                  <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 text-sm">
                    Quality Report
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Standards Tab */}
      {activeTab === 'standards' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Supported Industry Standards</h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {standards.map((standard) => (
              <div key={standard.standard} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">{standard.name}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Version {standard.version}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${standard.adoption_rate}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-600">{standard.adoption_rate}%</span>
                  </div>
                </div>

                <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">{standard.description}</p>

                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Supported Formats:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {standard.supported_formats?.map((format, index) => (
                        <span key={index} className="inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
                          {format}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Use Cases:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {standard.use_cases?.map((useCase, index) => (
                        <span key={index} className="inline-block px-2 py-1 text-xs bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-400 rounded">
                          {useCase}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quality Reports Tab */}
      {activeTab === 'quality' && qualitySummary && (
        <div className="space-y-6">
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Data Quality Summary</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{qualitySummary.total_entries}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Entries</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{qualitySummary.average_quality}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Avg Quality</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{qualitySummary.high_quality_count}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">High Quality</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{qualitySummary.quality_rate}%</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Quality Rate</div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 dark:text-white">Completeness</h4>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full"
                    style={{ width: `${qualitySummary.average_completeness}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">{qualitySummary.average_completeness}%</p>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 dark:text-white">Accuracy</h4>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-green-600 h-3 rounded-full"
                    style={{ width: `${qualitySummary.average_accuracy}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">{qualitySummary.average_accuracy}%</p>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 dark:text-white">Consistency</h4>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-purple-600 h-3 rounded-full"
                    style={{ width: `${qualitySummary.average_consistency}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">{qualitySummary.average_consistency}%</p>
              </div>
            </div>
          </div>

          {qualitySummary.common_issues && qualitySummary.common_issues.length > 0 && (
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Common Issues</h4>
              <div className="space-y-3">
                {qualitySummary.common_issues.map((issue, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <span className="text-gray-700 dark:text-gray-300">{issue.issue}</span>
                    <span className="font-semibold text-yellow-600">{issue.count} occurrences</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Submit Metadata Tab */}
      {activeTab === 'submit' && (
        <SubmitMetadataForm 
          onSuccess={() => { fetchMDEData(); setActiveTab('metadata'); }}
          onCancel={() => setActiveTab('metadata')}
        />
      )}
    </div>
  );
};

// Submit Metadata Form Component
const SubmitMetadataForm = ({ onSuccess, onCancel }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [formData, setFormData] = useState({
    title: '',
    artist: '',
    album: '',
    duration_ms: 0,
    genre: [''],
    explicit: false,
    contributors: [{ name: '', role: '' }],
    rights_holders: [{ name: '', type: '' }],
    language: 'en',
    label: '',
    catalog_number: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Convert duration from minutes:seconds to milliseconds
      const [minutes, seconds] = (formData.duration || '0:0').split(':');
      const totalMs = (parseInt(minutes) * 60 + parseInt(seconds || 0)) * 1000;

      const metadataData = {
        ...formData,
        duration_ms: totalMs,
        genre: formData.genre.filter(g => g.trim()),
        contributors: formData.contributors.filter(c => c.name.trim()),
        rights_holders: formData.rights_holders.filter(rh => rh.name.trim())
      };

      const response = await axios.post(`${API}/api/mde/metadata/submit?user_id=user_123`, metadataData);
      if (response.data.success) {
        alert('Metadata submitted successfully to MDE!');
        onSuccess();
      } else {
        alert('Error: ' + response.data.error);
      }
    } catch (error) {
      console.error('Error submitting metadata:', error);
      alert('Error submitting metadata');
    } finally {
      setLoading(false);
    }
  };

  const addField = (field) => {
    if (field === 'genre') {
      setFormData({
        ...formData,
        [field]: [...formData[field], '']
      });
    } else if (field === 'contributors') {
      setFormData({
        ...formData,
        [field]: [...formData[field], { name: '', role: '' }]
      });
    } else if (field === 'rights_holders') {
      setFormData({
        ...formData,
        [field]: [...formData[field], { name: '', type: '' }]
      });
    }
  };

  const removeField = (field, index) => {
    const newArray = formData[field].filter((_, i) => i !== index);
    setFormData({
      ...formData,
      [field]: newArray
    });
  };

  const updateField = (field, index, key, value) => {
    if (field === 'genre') {
      const newArray = [...formData[field]];
      newArray[index] = value;
      setFormData({
        ...formData,
        [field]: newArray
      });
    } else {
      const newArray = [...formData[field]];
      newArray[index][key] = value;
      setFormData({
        ...formData,
        [field]: newArray
      });
    }
  };

  return (
    <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Submit Metadata to MDE</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Title *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Artist *
            </label>
            <input
              type="text"
              required
              value={formData.artist}
              onChange={(e) => setFormData({...formData, artist: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Album
            </label>
            <input
              type="text"
              value={formData.album}
              onChange={(e) => setFormData({...formData, album: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Duration (MM:SS)
            </label>
            <input
              type="text"
              placeholder="3:30"
              value={formData.duration}
              onChange={(e) => setFormData({...formData, duration: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Label
            </label>
            <input
              type="text"
              value={formData.label}
              onChange={(e) => setFormData({...formData, label: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Catalog Number
            </label>
            <input
              type="text"
              value={formData.catalog_number}
              onChange={(e) => setFormData({...formData, catalog_number: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>
        </div>

        {/* Genres */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Genres *
          </label>
          {formData.genre.map((genre, index) => (
            <div key={index} className="flex space-x-2 mb-2">
              <input
                type="text"
                required
                value={genre}
                onChange={(e) => updateField('genre', index, null, e.target.value)}
                className={`flex-1 px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
              />
              {formData.genre.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeField('genre', index)}
                  className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addField('genre')}
            className="text-purple-600 hover:text-purple-700 text-sm"
          >
            + Add Genre
          </button>
        </div>

        {/* Explicit Content Checkbox */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="explicit"
            checked={formData.explicit}
            onChange={(e) => setFormData({...formData, explicit: e.target.checked})}
            className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
          />
          <label htmlFor="explicit" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
            Explicit Content
          </label>
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Submitting...' : 'Submit to MDE'}
          </button>
        </div>
      </form>
    </div>
  );
};