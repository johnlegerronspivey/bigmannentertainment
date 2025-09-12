import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://royaltyhub.preview.emergentagent.com';

// Main MLC Integration Component
export const MLCIntegration = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [activeTab, setActiveTab] = useState('overview');
  const [analytics, setAnalytics] = useState(null);
  const [works, setWorks] = useState([]);
  const [distributionRequests, setDistributionRequests] = useState([]);
  const [complianceStatus, setComplianceStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '🏠' },
    { id: 'works', name: 'Registered Works', icon: '🎵' },
    { id: 'distribution', name: 'Distribution', icon: '📡' },
    { id: 'royalties', name: 'Royalties', icon: '💰' },
    { id: 'compliance', name: 'Compliance', icon: '✅' },
    { id: 'register', name: 'Register Work', icon: '➕' }
  ];

  const fetchMLCData = async () => {
    setLoading(true);
    try {
      const [analyticsRes, worksRes, distributionRes, complianceRes] = await Promise.all([
        axios.get(`${API}/api/mlc/analytics?user_id=user_123`),
        axios.get(`${API}/api/mlc/works?user_id=user_123`),
        axios.get(`${API}/api/mlc/distribution/requests?user_id=user_123`),
        axios.get(`${API}/api/mlc/compliance/status?user_id=user_123`)
      ]);

      if (analyticsRes.data.success) setAnalytics(analyticsRes.data.analytics);
      if (worksRes.data.success) setWorks(worksRes.data.works);
      if (distributionRes.data.success) setDistributionRequests(distributionRes.data.requests);
      if (complianceRes.data.success) setComplianceStatus(complianceRes.data.compliance_status);
    } catch (error) {
      console.error('Error fetching MLC data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMLCData();
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
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">MLC Integration</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Mechanical Licensing Collective management and distribution</p>
        </div>
        <div className="flex space-x-2">
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            🏛️ Official MLC
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            ✅ Compliant
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
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
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
                  <p className="text-sm text-gray-600 dark:text-gray-400">Registered Works</p>
                  <p className="text-2xl font-bold text-blue-600">{analytics.overview.total_registered_works}</p>
                </div>
                <span className="text-2xl">🎵</span>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Plays</p>
                  <p className="text-2xl font-bold text-green-600">{analytics.overview.total_plays?.toLocaleString()}</p>
                </div>
                <span className="text-2xl">▶️</span>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Mechanical Royalties</p>
                  <p className="text-2xl font-bold text-purple-600">${analytics.overview.total_mechanical_royalties}</p>
                </div>
                <span className="text-2xl">💰</span>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Active DSPs</p>
                  <p className="text-2xl font-bold text-orange-600">{analytics.overview.active_dsps}</p>
                </div>
                <span className="text-2xl">📡</span>
              </div>
            </div>
          </div>

          {/* DSP Performance */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">DSP Performance</h3>
            <div className="space-y-4">
              {Object.entries(analytics.dsp_performance || {}).map(([dsp, performance]) => (
                <div key={dsp} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{dsp}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {performance.plays?.toLocaleString()} plays
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-600">
                      ${performance.mechanical_royalties?.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      ${performance.revenue?.toFixed(2)} revenue
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Performing Works */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Works</h3>
            <div className="space-y-3">
              {analytics.top_performing_works?.map((work, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{work.title}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {work.plays?.toLocaleString()} plays
                      </p>
                    </div>
                  </div>
                  <p className="font-semibold text-green-600">
                    ${work.mechanical_royalties?.toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Registered Works Tab */}
      {activeTab === 'works' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Registered Works ({works.length})</h3>
            <button 
              onClick={() => setActiveTab('register')}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Register New Work
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {works.map((work) => (
              <div key={work.work_id} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">{work.title}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      ISWC: {work.iswc} | ISRC: {work.isrc}
                    </p>
                  </div>
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    Registered
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Composers:</span>
                    <span className="text-sm text-gray-900 dark:text-white">{work.composers?.join(', ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Publishers:</span>
                    <span className="text-sm text-gray-900 dark:text-white">{work.publishers?.join(', ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Duration:</span>
                    <span className="text-sm text-gray-900 dark:text-white">
                      {Math.floor(work.duration_seconds / 60)}:{(work.duration_seconds % 60).toString().padStart(2, '0')}
                    </span>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 text-sm">
                    Distribute
                  </button>
                  <button className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 text-sm">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Register Work Tab */}
      {activeTab === 'register' && (
        <RegisterWorkForm onSuccess={() => { fetchMLCData(); setActiveTab('works'); }} />
      )}

      {/* Compliance Tab */}
      {activeTab === 'compliance' && complianceStatus && (
        <div className="space-y-6">
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">MLC Compliance Status</h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-700 dark:text-gray-300">MLC Registration Current</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  complianceStatus.mlc_registration_current 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {complianceStatus.mlc_registration_current ? '✅ Current' : '❌ Expired'}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-gray-700 dark:text-gray-300">Usage Reporting Up to Date</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  complianceStatus.usage_reporting_up_to_date 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {complianceStatus.usage_reporting_up_to_date ? '✅ Up to Date' : '❌ Behind'}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-gray-700 dark:text-gray-300">Mechanical Licenses Valid</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  complianceStatus.mechanical_licenses_valid 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {complianceStatus.mechanical_licenses_valid ? '✅ Valid' : '❌ Invalid'}
                </span>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-600">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700 dark:text-gray-300">Last Audit Date</span>
                  <span className="text-gray-900 dark:text-white">{complianceStatus.last_audit_date}</span>
                </div>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-gray-700 dark:text-gray-300">Next Audit Due</span>
                  <span className="text-gray-900 dark:text-white">{complianceStatus.next_audit_due}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Register Work Form Component
const RegisterWorkForm = ({ onSuccess }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [formData, setFormData] = useState({
    title: '',
    composers: [''],
    publishers: [''],
    duration_seconds: 0,
    genres: [''],
    copyright_owner: '',
    mechanical_rights_owner: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Convert duration from minutes:seconds to seconds
      const [minutes, seconds] = (formData.duration || '0:0').split(':');
      const totalSeconds = parseInt(minutes) * 60 + parseInt(seconds || 0);

      const workData = {
        ...formData,
        duration_seconds: totalSeconds,
        composers: formData.composers.filter(c => c.trim()),
        publishers: formData.publishers.filter(p => p.trim()),
        genres: formData.genres.filter(g => g.trim())
      };

      const response = await axios.post(`${API}/api/mlc/works/register?user_id=user_123`, workData);
      if (response.data.success) {
        alert('Work registered successfully with MLC!');
        onSuccess();
      } else {
        alert('Error: ' + response.data.error);
      }
    } catch (error) {
      console.error('Error registering work:', error);
      alert('Error registering work');
    } finally {
      setLoading(false);
    }
  };

  const addField = (field) => {
    setFormData({
      ...formData,
      [field]: [...formData[field], '']
    });
  };

  const removeField = (field, index) => {
    const newArray = formData[field].filter((_, i) => i !== index);
    setFormData({
      ...formData,
      [field]: newArray
    });
  };

  const updateField = (field, index, value) => {
    const newArray = [...formData[field]];
    newArray[index] = value;
    setFormData({
      ...formData,
      [field]: newArray
    });
  };

  return (
    <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Register New Musical Work with MLC</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Work Title *
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
        </div>

        {/* Composers */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Composers *
          </label>
          {formData.composers.map((composer, index) => (
            <div key={index} className="flex space-x-2 mb-2">
              <input
                type="text"
                required
                value={composer}
                onChange={(e) => updateField('composers', index, e.target.value)}
                className={`flex-1 px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
              />
              {formData.composers.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeField('composers', index)}
                  className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addField('composers')}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            + Add Composer
          </button>
        </div>

        {/* Publishers */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Publishers *
          </label>
          {formData.publishers.map((publisher, index) => (
            <div key={index} className="flex space-x-2 mb-2">
              <input
                type="text"
                required
                value={publisher}
                onChange={(e) => updateField('publishers', index, e.target.value)}
                className={`flex-1 px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
              />
              {formData.publishers.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeField('publishers', index)}
                  className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={() => addField('publishers')}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            + Add Publisher
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Copyright Owner *
            </label>
            <input
              type="text"
              required
              value={formData.copyright_owner}
              onChange={(e) => setFormData({...formData, copyright_owner: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Mechanical Rights Owner *
            </label>
            <input
              type="text"
              required
              value={formData.mechanical_rights_owner}
              onChange={(e) => setFormData({...formData, mechanical_rights_owner: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => setActiveTab('works')}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Registering...' : 'Register with MLC'}
          </button>
        </div>
      </form>
    </div>
  );
};