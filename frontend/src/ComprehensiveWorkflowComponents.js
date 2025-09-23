import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://support-desk-30.preview.emergentagent.com';

// Main Comprehensive Workflow Dashboard
export const ComprehensiveWorkflowDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [workflowData, setWorkflowData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWorkflowData();
  }, []);

  const fetchWorkflowData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/workflow/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setWorkflowData(response.data.dashboard);
    } catch (error) {
      console.error('Error fetching workflow data:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', name: 'Workflow Overview', icon: '📊' },
    { id: 'intake', name: 'Master Intake', icon: '📥' },
    { id: 'versioning', name: 'Content Versioning', icon: '🔄' },
    { id: 'qc', name: 'Technical QC', icon: '🔍' },
    { id: 'transcoding', name: 'Transcoding Hub', icon: '🎬' },
    { id: 'distribution', name: 'Distribution Center', icon: '🌐' },
    { id: 'monitoring', name: 'Performance Monitor', icon: '📈' }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎯 End-to-End Content Distribution Workflow
        </h1>
        <p className="text-gray-600">
          Comprehensive content workflow from master intake to global distribution
        </p>
      </div>

      {/* Dashboard Stats */}
      {workflowData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <span className="text-2xl">📁</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Master Content</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {workflowData.content_summary?.master_content_pieces || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <span className="text-2xl">✅</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">QC Passed</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {workflowData.quality_assurance?.passed || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <span className="text-2xl">🌐</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Channels</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {workflowData.distribution_channels?.available_channels || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <span className="text-2xl">💾</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Storage (GB)</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {workflowData.content_summary?.storage_used_gb?.toFixed(1) || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <WorkflowOverviewTab workflowData={workflowData} />}
      {activeTab === 'intake' && <MasterIntakeTab />}
      {activeTab === 'versioning' && <ContentVersioningTab />}
      {activeTab === 'qc' && <TechnicalQCTab />}
      {activeTab === 'transcoding' && <TranscodingHubTab />}
      {activeTab === 'distribution' && <DistributionCenterTab />}
      {activeTab === 'monitoring' && <PerformanceMonitorTab />}
    </div>
  );
};

// Workflow Overview Tab
const WorkflowOverviewTab = ({ workflowData }) => {
  return (
    <div className="space-y-6">
      {/* Workflow Pipeline */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔄 Workflow Pipeline</h3>
        
        <div className="flex items-center justify-between">
          {[
            { stage: 'Intake', icon: '📥', status: 'active' },
            { stage: 'Versioning', icon: '🔄', status: 'pending' },
            { stage: 'QC', icon: '🔍', status: 'pending' },
            { stage: 'Transcoding', icon: '🎬', status: 'pending' },
            { stage: 'Distribution', icon: '🌐', status: 'pending' },
            { stage: 'Monitor', icon: '📈', status: 'pending' }
          ].map((stage, index) => (
            <div key={stage.stage} className="flex flex-col items-center">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                stage.status === 'active' 
                  ? 'bg-purple-100 text-purple-600 border-2 border-purple-500' 
                  : 'bg-gray-100 text-gray-400'
              }`}>
                <span className="text-xl">{stage.icon}</span>
              </div>
              <p className="text-sm font-medium text-gray-600 mt-2">{stage.stage}</p>
              {index < 5 && (
                <div className="absolute mt-6 ml-12 w-8 h-0.5 bg-gray-300"></div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Distribution Channels Summary */}
      {workflowData?.distribution_channels && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🌐 Distribution Channels</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(workflowData.distribution_channels.channels_by_type || {}).map(([type, count]) => (
              <div key={type} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-gray-900 capitalize">
                    {type.replace('_', ' ')}
                  </h4>
                  <span className="text-2xl font-bold text-purple-600">{count}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">Available channels</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quality Assurance Summary */}
      {workflowData?.quality_assurance && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 Quality Assurance</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {workflowData.quality_assurance.passed || 0}
              </div>
              <div className="text-sm text-gray-600">Passed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">
                {workflowData.quality_assurance.failed || 0}
              </div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600">
                {workflowData.quality_assurance.warnings || 0}
              </div>
              <div className="text-sm text-gray-600">Warnings</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {workflowData.quality_assurance.total_qc_runs || 0}
              </div>
              <div className="text-sm text-gray-600">Total QC</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Master Intake Tab
const MasterIntakeTab = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [metadata, setMetadata] = useState({
    title: '',
    description: '',
    content_type: 'video_longform'
  });

  const contentTypes = [
    { value: 'video_longform', label: 'Video Longform/Episodic' },
    { value: 'video_episodic', label: 'Video Episodic Series' },
    { value: 'audio_music', label: 'Audio Music' },
    { value: 'audio_radio', label: 'Audio Radio/Podcast' },
    { value: 'social_short', label: 'Social Media Short' },
    { value: 'ott_streaming', label: 'OTT Streaming' }
  ];

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
  };

  const handleIngest = async () => {
    if (!selectedFile || !metadata.title) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('content_type', metadata.content_type);
      formData.append('title', metadata.title);
      formData.append('description', metadata.description);

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/workflow/ingest`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      if (response.data.success) {
        alert('Master content ingested successfully!');
        setSelectedFile(null);
        setMetadata({ title: '', description: '', content_type: 'video_longform' });
        setUploadProgress(0);
      }
    } catch (error) {
      console.error('Error ingesting content:', error);
      alert('Failed to ingest content');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Master Intake Guidelines */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">📥 Master Intake Guidelines</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-blue-800 mb-2">Supported Video Formats</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• ProRes (all variants)</li>
              <li>• DNxHR/DNxHD</li>
              <li>• High-rate H.264/HEVC</li>
              <li>• Uncompressed formats</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-blue-800 mb-2">Supported Audio Formats</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• WAV (uncompressed)</li>
              <li>• AIFF (uncompressed)</li>
              <li>• BWF (Broadcast Wave)</li>
              <li>• High-quality lossless formats</li>
            </ul>
          </div>
        </div>
      </div>

      {/* File Upload */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📤 Upload Master Content</h3>
        
        {/* File Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Master File
          </label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
            <div className="space-y-1 text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <div className="flex text-sm text-gray-600">
                <label className="relative cursor-pointer bg-white rounded-md font-medium text-purple-600 hover:text-purple-500 focus-within:outline-none">
                  <span>Upload a file</span>
                  <input type="file" className="sr-only" onChange={handleFileSelect} accept="video/*,audio/*" />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">Video or Audio files up to 10GB</p>
            </div>
          </div>
          {selectedFile && (
            <div className="mt-3 text-sm text-gray-600">
              Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </div>
          )}
        </div>

        {/* Metadata Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content Type
            </label>
            <select
              value={metadata.content_type}
              onChange={(e) => setMetadata({...metadata, content_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {contentTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title *
            </label>
            <input
              type="text"
              value={metadata.title}
              onChange={(e) => setMetadata({...metadata, title: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter content title"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={metadata.description}
              onChange={(e) => setMetadata({...metadata, description: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              rows="3"
              placeholder="Enter content description"
            />
          </div>
        </div>

        {/* Upload Progress */}
        {uploading && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Uploading...</span>
              <span className="text-sm text-gray-600">{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-purple-600 h-2 rounded-full transition-all duration-300" style={{width: `${uploadProgress}%`}}></div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="mt-6">
          <button
            onClick={handleIngest}
            disabled={!selectedFile || !metadata.title || uploading}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Ingesting...' : 'Ingest Master Content'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Content Versioning Tab
const ContentVersioningTab = () => {
  const [userContent, setUserContent] = useState([]);
  const [selectedContent, setSelectedContent] = useState('');
  const [versionRequest, setVersionRequest] = useState({
    quality_profile: 'broadcast_hd',
    version_name: '',
    changes_summary: ''
  });
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState([]);

  const qualityProfiles = [
    { value: 'broadcast_hd', label: 'Broadcast HD - ProRes/XDCAM' },
    { value: 'broadcast_4k', label: 'Broadcast 4K - Ultra HD' },
    { value: 'streaming_premium', label: 'Streaming Premium - Multi-bitrate' },
    { value: 'streaming_standard', label: 'Streaming Standard - Optimized' },
    { value: 'social_optimized', label: 'Social Media Optimized' },
    { value: 'radio_master', label: 'Radio Master - Audio' }
  ];

  useEffect(() => {
    fetchUserContent();
  }, []);

  const fetchUserContent = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/workflow/content`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setUserContent(response.data.data.content);
      }
    } catch (error) {
      console.error('Error fetching content:', error);
    }
  };

  const fetchContentVersions = async (contentId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/workflow/content/${contentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setVersions(response.data.data.versions || []);
      }
    } catch (error) {
      console.error('Error fetching versions:', error);
    }
  };

  const handleContentSelect = (contentId) => {
    setSelectedContent(contentId);
    if (contentId) {
      fetchContentVersions(contentId);
    } else {
      setVersions([]);
    }
  };

  const createVersion = async () => {
    if (!selectedContent || !versionRequest.quality_profile) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/workflow/content/${selectedContent}/version`,
        versionRequest,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        alert('Content version created successfully!');
        setVersionRequest({ quality_profile: 'broadcast_hd', version_name: '', changes_summary: '' });
        fetchContentVersions(selectedContent);
      }
    } catch (error) {
      console.error('Error creating version:', error);
      alert('Failed to create version');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Version Creation */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔄 Create New Version</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Content
            </label>
            <select
              value={selectedContent}
              onChange={(e) => handleContentSelect(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Select content to version...</option>
              {userContent.map(content => (
                <option key={content.content_id} value={content.content_id}>
                  {content.title}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quality Profile
            </label>
            <select
              value={versionRequest.quality_profile}
              onChange={(e) => setVersionRequest({...versionRequest, quality_profile: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {qualityProfiles.map(profile => (
                <option key={profile.value} value={profile.value}>{profile.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Version Name
            </label>
            <input
              type="text"
              value={versionRequest.version_name}
              onChange={(e) => setVersionRequest({...versionRequest, version_name: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="e.g., Broadcast Master, Social Edit"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Changes Summary
            </label>
            <input
              type="text"
              value={versionRequest.changes_summary}
              onChange={(e) => setVersionRequest({...versionRequest, changes_summary: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Describe what changed in this version"
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={createVersion}
            disabled={!selectedContent || loading}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Version...' : 'Create Version'}
          </button>
        </div>
      </div>

      {/* Version History */}
      {selectedContent && versions.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📚 Version History</h3>
          
          <div className="space-y-4">
            {versions.map((version) => (
              <div key={version.version_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4">
                      <h4 className="font-semibold text-lg">
                        {version.version_name || `Version ${version.version_number}`}
                      </h4>
                      <span className="text-sm text-gray-600">v{version.version_number}</span>
                      {version.is_current && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                          Current
                        </span>
                      )}
                    </div>
                    
                    <div className="mt-2 text-sm text-gray-600">
                      <p><strong>Quality Profile:</strong> {version.quality_profile}</p>
                      <p><strong>File Size:</strong> {(version.file_size / 1024 / 1024).toFixed(2)} MB</p>
                      <p><strong>Created:</strong> {new Date(version.created_at).toLocaleString()}</p>
                      {version.changes_summary && (
                        <p><strong>Changes:</strong> {version.changes_summary}</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="ml-4 flex flex-col space-y-2">
                    <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                      Download
                    </button>
                    <button className="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700">
                      Run QC
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Versioning Guidelines */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-yellow-900 mb-3">💡 Versioning Guidelines</h3>
        <div className="text-sm text-yellow-800 space-y-2">
          <p><strong>Semantic Versioning:</strong> Major.Minor.Patch (e.g., 2.1.3)</p>
          <p><strong>Major Version:</strong> Significant content changes, new scenes, complete re-edit</p>
          <p><strong>Minor Version:</strong> Moderate changes, color correction, audio adjustments</p>
          <p><strong>Patch Version:</strong> Small fixes, typo corrections, minor tweaks</p>
          <p><strong>Immutable Storage:</strong> All versions are stored permanently with checksums</p>
        </div>
      </div>
    </div>
  );
};

// Technical QC Tab
const TechnicalQCTab = () => {
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState('');
  const [targetProfile, setTargetProfile] = useState('');
  const [qcResults, setQcResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const qualityProfiles = [
    { value: 'broadcast_hd', label: 'Broadcast HD Standards' },
    { value: 'streaming_premium', label: 'Streaming Premium' },
    { value: 'social_optimized', label: 'Social Media Optimized' }
  ];

  useEffect(() => {
    fetchVersions();
  }, []);

  const fetchVersions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/workflow/content`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        // Get all versions from all content
        const allVersions = [];
        for (const content of response.data.data.content) {
          const versionResponse = await axios.get(`${API}/api/workflow/content/${content.content_id}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (versionResponse.data.success) {
            const contentVersions = versionResponse.data.data.versions || [];
            contentVersions.forEach(version => {
              version.content_title = content.title;
            });
            allVersions.push(...contentVersions);
          }
        }
        setVersions(allVersions);
      }
    } catch (error) {
      console.error('Error fetching versions:', error);
    }
  };

  const runQC = async () => {
    if (!selectedVersion) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/workflow/qc/${selectedVersion}`,
        { target_profile: targetProfile || null },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        setQcResults(response.data.data);
      }
    } catch (error) {
      console.error('Error running QC:', error);
      alert('Failed to run QC');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* QC Controls */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 Technical Quality Control</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Version to Test
            </label>
            <select
              value={selectedVersion}
              onChange={(e) => setSelectedVersion(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Select version...</option>
              {versions.map(version => (
                <option key={version.version_id} value={version.version_id}>
                  {version.content_title} - v{version.version_number}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Profile (Optional)
            </label>
            <select
              value={targetProfile}
              onChange={(e) => setTargetProfile(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Auto-detect standards</option>
              {qualityProfiles.map(profile => (
                <option key={profile.value} value={profile.value}>{profile.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={runQC}
            disabled={!selectedVersion || loading}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Running QC...' : 'Run Technical QC'}
          </button>
        </div>
      </div>

      {/* QC Results */}
      {qcResults && (
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">📊 QC Results</h3>
            <div className="flex items-center space-x-4">
              <span className={`px-3 py-1 rounded text-sm font-medium ${
                qcResults.overall_status === 'passed' ? 'bg-green-100 text-green-800' :
                qcResults.overall_status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {qcResults.overall_status.toUpperCase()}
              </span>
              <span className="text-lg font-semibold text-gray-900">
                Score: {qcResults.qc_score.toFixed(1)}%
              </span>
            </div>
          </div>

          {/* QC Checks Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {Object.entries(qcResults.checks).map(([check, passed]) => (
              <div key={check} className="flex items-center space-x-2">
                <span className={`text-lg ${passed ? 'text-green-600' : 'text-red-600'}`}>
                  {passed ? '✅' : '❌'}
                </span>
                <span className="text-sm font-medium capitalize">
                  {check.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>

          {/* Critical Issues */}
          {qcResults.critical_issues && qcResults.critical_issues.length > 0 && (
            <div className="mb-6">
              <h4 className="font-semibold text-red-800 mb-3">🚨 Critical Issues</h4>
              <div className="space-y-3">
                {qcResults.critical_issues.map((issue, index) => (
                  <div key={index} className="border-l-4 border-red-500 pl-4 bg-red-50 p-3 rounded">
                    <h5 className="font-semibold text-red-800">{issue.issue}</h5>
                    <p className="text-red-700 text-sm mt-1">{issue.details}</p>
                    <p className="text-red-600 text-sm mt-2 italic">{issue.suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Warnings */}
          {qcResults.warnings && qcResults.warnings.length > 0 && (
            <div className="mb-6">
              <h4 className="font-semibold text-yellow-800 mb-3">⚠️ Warnings</h4>
              <div className="space-y-3">
                {qcResults.warnings.map((warning, index) => (
                  <div key={index} className="border-l-4 border-yellow-500 pl-4 bg-yellow-50 p-3 rounded">
                    <h5 className="font-semibold text-yellow-800">{warning.issue}</h5>
                    <p className="text-yellow-700 text-sm mt-1">{warning.details}</p>
                    <p className="text-yellow-600 text-sm mt-2 italic">{warning.suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Suggestions */}
          {qcResults.suggestions && qcResults.suggestions.length > 0 && (
            <div>
              <h4 className="font-semibold text-blue-800 mb-3">💡 Optimization Suggestions</h4>
              <ul className="list-disc list-inside text-blue-700 text-sm space-y-1">
                {qcResults.suggestions.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* QC Standards Reference */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">📋 QC Standards Reference</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-blue-800 mb-2">Video Standards</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Frame rate: Standard broadcast rates</li>
              <li>• Resolution: HD/4K compliance</li>
              <li>• Color range: Broadcast safe (16-235)</li>
              <li>• Bit rate: Minimum quality thresholds</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-blue-800 mb-2">Audio Standards</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Loudness: ATSC A/85, EBU R128</li>
              <li>• True peak: -2dBTP (US), -1dBTP (EU)</li>
              <li>• Sample rate: 44.1/48 kHz</li>
              <li>• PSE safe: Flash detection</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Transcoding Hub Tab  
const TranscodingHubTab = () => {
  const [transcodingJobs, setTranscodingJobs] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [newJob, setNewJob] = useState({
    content_id: '',
    version_id: '',
    source_file_path: '',
    profile: 'tv_prores_hd',
    audio_standard: 'streaming'
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTranscodingProfiles();
    fetchTranscodingJobs();
  }, []);

  const fetchTranscodingProfiles = async () => {
    try {
      const response = await axios.get(`${API}/api/transcoding/profiles`);
      if (response.data.success) {
        setProfiles(response.data.data.profiles);
      }
    } catch (error) {
      console.error('Error fetching profiles:', error);
    }
  };

  const fetchTranscodingJobs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/transcoding/jobs`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setTranscodingJobs(response.data.data.jobs);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const createTranscodingJob = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/transcoding/jobs`, newJob, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('Transcoding job created successfully!');
        setNewJob({
          content_id: '',
          version_id: '',
          source_file_path: '',
          profile: 'tv_prores_hd',
          audio_standard: 'streaming'
        });
        fetchTranscodingJobs();
      }
    } catch (error) {
      console.error('Error creating job:', error);
      alert('Failed to create transcoding job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Transcoding Job Creation */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎬 Create Transcoding Job</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content ID
            </label>
            <input
              type="text"
              value={newJob.content_id}
              onChange={(e) => setNewJob({...newJob, content_id: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter content ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Version ID
            </label>
            <input
              type="text"
              value={newJob.version_id}
              onChange={(e) => setNewJob({...newJob, version_id: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter version ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Transcoding Profile
            </label>
            <select
              value={newJob.profile}
              onChange={(e) => setNewJob({...newJob, profile: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {profiles.map(profile => (
                <option key={profile.profile} value={profile.profile}>
                  {profile.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Audio Standard
            </label>
            <select
              value={newJob.audio_standard}
              onChange={(e) => setNewJob({...newJob, audio_standard: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="streaming">Streaming (-16 LUFS)</option>
              <option value="atsc_a85">ATSC A/85 (-24 LKFS)</option>
              <option value="ebu_r128">EBU R128 (-23 LUFS)</option>
              <option value="radio">Radio (Conservative)</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source File Path
            </label>
            <input
              type="text"
              value={newJob.source_file_path}
              onChange={(e) => setNewJob({...newJob, source_file_path: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter source file path"
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={createTranscodingJob}
            disabled={loading}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Job...' : 'Create Transcoding Job'}
          </button>
        </div>
      </div>

      {/* Active Jobs */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ Active Transcoding Jobs</h3>
        
        {transcodingJobs.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No transcoding jobs found</p>
        ) : (
          <div className="space-y-4">
            {transcodingJobs.map((job) => (
              <div key={job.job_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4">
                      <h4 className="font-semibold">{job.profile}</h4>
                      <span className={`px-2 py-1 rounded text-xs ${
                        job.status === 'completed' ? 'bg-green-100 text-green-800' :
                        job.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        job.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {job.status}
                      </span>
                    </div>
                    
                    <div className="mt-2 text-sm text-gray-600">
                      <p>Content: {job.content_id}</p>
                      <p>Created: {new Date(job.created_at).toLocaleString()}</p>
                      {job.processing_time_seconds && (
                        <p>Processing Time: {job.processing_time_seconds.toFixed(1)}s</p>
                      )}
                    </div>

                    {job.status === 'processing' && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-600">Progress</span>
                          <span className="text-sm text-gray-600">{job.progress_percentage.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                            style={{width: `${job.progress_percentage}%`}}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="ml-4">
                    {job.output_files_count > 0 && (
                      <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Download ({job.output_files_count})
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Transcoding Profiles Reference */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Available Transcoding Profiles</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {profiles.slice(0, 6).map((profile) => (
            <div key={profile.profile} className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-gray-900 mb-2">{profile.name}</h4>
              <div className="text-sm text-gray-600 space-y-1">
                {profile.video_specs && (
                  <p><strong>Video:</strong> {profile.video_specs.codec} - {profile.video_specs.resolution}</p>
                )}
                {profile.audio_specs && (
                  <p><strong>Audio:</strong> {profile.audio_specs.codec} - {profile.audio_specs.sample_rate}Hz</p>
                )}
                <p><strong>Container:</strong> {profile.container}</p>
                {profile.features && profile.features.length > 0 && (
                  <p><strong>Features:</strong> {profile.features.join(', ')}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Distribution Center Tab
const DistributionCenterTab = () => {
  const [distributionJobs, setDistributionJobs] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [newDistribution, setNewDistribution] = useState({
    content_id: '',
    version_id: '',
    platform_name: '',
    delivery_profile_id: '',
    metadata: {}
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPlatforms();
    fetchDistributionJobs();
  }, []);

  const fetchPlatforms = async () => {
    try {
      const response = await axios.get(`${API}/api/distribution/platforms`);
      if (response.data.success) {
        setPlatforms(response.data.data.connectors);
      }
    } catch (error) {
      console.error('Error fetching platforms:', error);
    }
  };

  const fetchDistributionJobs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/distribution/jobs`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setDistributionJobs(response.data.data.jobs);
      }
    } catch (error) {
      console.error('Error fetching distribution jobs:', error);
    }
  };

  const createDistributionJob = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const distributionData = {
        ...newDistribution,
        source_files: [
          {
            type: 'primary',
            path: '/tmp/placeholder.mp4',
            format: 'mp4',
            size_bytes: 1024000
          }
        ]
      };

      const response = await axios.post(`${API}/api/distribution/jobs`, distributionData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('Distribution job created successfully!');
        setNewDistribution({
          content_id: '',
          version_id: '',
          platform_name: '',
          delivery_profile_id: '',
          metadata: {}
        });
        fetchDistributionJobs();
      }
    } catch (error) {
      console.error('Error creating distribution job:', error);
      alert('Failed to create distribution job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Distribution Job Creation */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🌐 Create Distribution Job</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content ID
            </label>
            <input
              type="text"
              value={newDistribution.content_id}
              onChange={(e) => setNewDistribution({...newDistribution, content_id: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter content ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Version ID
            </label>
            <input
              type="text"
              value={newDistribution.version_id}
              onChange={(e) => setNewDistribution({...newDistribution, version_id: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter version ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Platform
            </label>
            <select
              value={newDistribution.platform_name}
              onChange={(e) => setNewDistribution({...newDistribution, platform_name: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Select platform...</option>
              {platforms.map(platform => (
                <option key={platform.platform_name} value={platform.platform_name}>
                  {platform.platform_name} ({platform.platform_type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Delivery Profile ID
            </label>
            <input
              type="text"
              value={newDistribution.delivery_profile_id}
              onChange={(e) => setNewDistribution({...newDistribution, delivery_profile_id: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Auto-generated if empty"
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={createDistributionJob}
            disabled={!newDistribution.content_id || !newDistribution.version_id || !newDistribution.platform_name || loading}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Distribution...' : 'Create Distribution Job'}
          </button>
        </div>
      </div>

      {/* Active Distributions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Active Distributions</h3>
        
        {distributionJobs.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No distribution jobs found</p>
        ) : (
          <div className="space-y-4">
            {distributionJobs.map((job) => (
              <div key={job.distribution_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4">
                      <h4 className="font-semibold">{job.platform_name}</h4>
                      <span className={`px-2 py-1 rounded text-xs ${
                        job.status === 'verified' ? 'bg-green-100 text-green-800' :
                        job.status === 'delivered' ? 'bg-blue-100 text-blue-800' :
                        job.status === 'delivering' ? 'bg-yellow-100 text-yellow-800' :
                        job.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {job.status}
                      </span>
                    </div>
                    
                    <div className="mt-2 text-sm text-gray-600">
                      <p>Content: {job.content_id}</p>
                      <p>Platform Type: {job.platform_type}</p>
                      <p>Created: {new Date(job.created_at).toLocaleString()}</p>
                      {job.platform_content_id && (
                        <p>Platform ID: {job.platform_content_id}</p>
                      )}
                    </div>

                    {job.status === 'delivering' && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-600">Progress</span>
                          <span className="text-sm text-gray-600">{job.progress_percentage.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full transition-all duration-300" 
                            style={{width: `${job.progress_percentage}%`}}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="ml-4 flex flex-col space-y-2">
                    {job.platform_content_id && (
                      <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                        View on Platform
                      </button>
                    )}
                    {job.status === 'failed' && (
                      <button className="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700">
                        Retry
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Platform Connectors */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔌 Available Platform Connectors</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {platforms.slice(0, 9).map((platform) => (
            <div key={platform.platform_name} className="bg-white p-4 rounded-lg border">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-gray-900">{platform.platform_name}</h4>
                <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded">
                  {platform.platform_type}
                </span>
              </div>
              <div className="text-sm text-gray-600 space-y-1">
                <p><strong>Auth:</strong> {platform.authentication_method}</p>
                <p><strong>Max Size:</strong> {platform.max_file_size_mb}MB</p>
                <p><strong>Formats:</strong> {platform.supported_formats.join(', ')}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Performance Monitor Tab
const PerformanceMonitorTab = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch transcoding stats
      const transcodingResponse = await axios.get(`${API}/api/transcoding/statistics`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Fetch distribution stats  
      const distributionResponse = await axios.get(`${API}/api/distribution/statistics`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setStats({
        transcoding: transcodingResponse.data.success ? transcodingResponse.data.data : {},
        distribution: distributionResponse.data.success ? distributionResponse.data.data : {}
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-2xl">🎬</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Jobs</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats?.transcoding?.total_jobs || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats?.transcoding?.success_rate?.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-2xl">🌐</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Distributions</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats?.distribution?.total_distributions || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <span className="text-2xl">📈</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Dist. Success</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats?.distribution?.overall_success_rate?.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Transcoding Performance */}
      {stats?.transcoding && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🎬 Transcoding Performance</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Job Status Breakdown</h4>
              <div className="space-y-2">
                {Object.entries(stats.transcoding.status_breakdown || {}).map(([status, data]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="capitalize text-gray-600">{status.replace('_', ' ')}</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">{data.count || 0}</span>
                      {data.avg_processing_time_seconds && (
                        <span className="text-sm text-gray-500">
                          (avg: {data.avg_processing_time_seconds.toFixed(1)}s)
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-3">Profile Usage</h4>
              <div className="space-y-2">
                {Object.entries(stats.transcoding.profile_usage || {}).map(([profile, count]) => (
                  <div key={profile} className="flex items-center justify-between">
                    <span className="text-gray-600">{profile.replace('_', ' ')}</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Distribution Performance */}
      {stats?.distribution && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🌐 Distribution Performance</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Status Breakdown</h4>
              <div className="space-y-2">
                {Object.entries(stats.distribution.status_breakdown || {}).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="capitalize text-gray-600">{status.replace('_', ' ')}</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-3">Platform Performance</h4>
              <div className="space-y-2">
                {Object.entries(stats.distribution.platform_performance || {}).slice(0, 5).map(([platform, data]) => (
                  <div key={platform} className="flex items-center justify-between">
                    <span className="text-gray-600">{platform}</span>
                    <div className="text-right">
                      <div className="font-semibold">{data.success_rate?.toFixed(1) || 0}%</div>
                      <div className="text-xs text-gray-500">{data.total_distributions || 0} total</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Health */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💚 System Health</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-4xl mb-2">🟢</div>
            <div className="font-semibold text-gray-900">Transcoding Service</div>
            <div className="text-sm text-gray-600">Operational</div>
          </div>
          
          <div className="text-center">
            <div className="text-4xl mb-2">🟢</div>
            <div className="font-semibold text-gray-900">Distribution Service</div>
            <div className="text-sm text-gray-600">Operational</div>
          </div>
          
          <div className="text-center">
            <div className="text-4xl mb-2">🟢</div>
            <div className="font-semibold text-gray-900">Quality Control</div>
            <div className="text-sm text-gray-600">Operational</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComprehensiveWorkflowDashboard;