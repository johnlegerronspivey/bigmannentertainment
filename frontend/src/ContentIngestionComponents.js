import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://music-rights-hub-2.preview.emergentagent.com';

// Main Content Ingestion Dashboard
export const ContentIngestionDashboard = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/content-ingestion/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(response.data.dashboard);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'upload', name: 'Upload & Metadata', icon: '📤' },
    { id: 'transcoding', name: 'Transcoding & Optimization', icon: '🎬' },
    { id: 'distribution', name: 'Distribution & Delivery', icon: '🌐' },
    { id: 'analytics', name: 'Analytics & Performance', icon: '📊' },
    { id: 'lifecycle', name: 'Lifecycle Management', icon: '🔄' },
    { id: 'content', name: 'Content Library', icon: '📚' },
    { id: 'compliance', name: 'Compliance', icon: '✅' },
    { id: 'ddex', name: 'DDEX Management', icon: '🔄' }
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Ingestion & Metadata Enrichment</h1>
        <p className="text-gray-600">Upload content, enrich with DDEX-compliant metadata, and manage compliance</p>
      </div>

      {/* Dashboard Stats */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="text-blue-600 text-2xl mr-3">📁</div>
              <div>
                <p className="text-sm font-medium text-gray-600">Total Content</p>
                <p className="text-2xl font-semibold text-gray-900">{dashboardData.total_content}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="text-green-600 text-2xl mr-3">✅</div>
              <div>
                <p className="text-sm font-medium text-gray-600">Approved</p>
                <p className="text-2xl font-semibold text-gray-900">{dashboardData.by_compliance.approved}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border-l-4 border-purple-500">
            <div className="flex items-center">
              <div className="text-purple-600 text-2xl mr-3">🚀</div>
              <div>
                <p className="text-sm font-medium text-gray-600">Ready for Distribution</p>
                <p className="text-2xl font-semibold text-gray-900">{dashboardData.by_status.ready_for_distribution}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border-l-4 border-orange-500">
            <div className="flex items-center">
              <div className="text-orange-600 text-2xl mr-3">💾</div>
              <div>
                <p className="text-sm font-medium text-gray-600">Storage Used</p>
                <p className="text-2xl font-semibold text-gray-900">{Math.round(dashboardData.storage_usage.total_size_mb)}MB</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
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
      <div className="tab-content">
        {activeTab === 'upload' && <UploadMetadataTab onUploadComplete={fetchDashboardData} />}
        {activeTab === 'transcoding' && <TranscodingTab />}
        {activeTab === 'distribution' && <DistributionTab />}
        {activeTab === 'analytics' && <AdvancedAnalyticsTab />}
        {activeTab === 'lifecycle' && <AdvancedLifecycleTab />}
        {activeTab === 'content' && <ContentLibraryTab dashboardData={dashboardData} />}
        {activeTab === 'compliance' && <ComplianceTab />}
        {activeTab === 'ddex' && <DDEXManagementTab />}
      </div>
    </div>
  );
};

// Upload & Metadata Tab Component
const UploadMetadataTab = ({ onUploadComplete }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [metadataForm, setMetadataForm] = useState({
    title: '',
    main_artist: '',
    release_date: new Date().toISOString().split('T')[0],
    genre: [],
    contributors: [],
    licensing_terms: null,
    additional_metadata: {}
  });
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileUpload = async (files) => {
    setUploading(true);
    const formData = new FormData();
    
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/content-ingestion/upload-multiple`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        setUploadedFiles(response.data.uploaded_files);
        alert(`Successfully uploaded ${response.data.total_files} files`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files);
    }
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const addContributor = () => {
    setMetadataForm(prev => ({
      ...prev,
      contributors: [...prev.contributors, {
        name: '',
        role: 'artist',
        percentage: 0,
        email: '',
        phone: ''
      }]
    }));
  };

  const updateContributor = (index, field, value) => {
    setMetadataForm(prev => ({
      ...prev,
      contributors: prev.contributors.map((contrib, i) => 
        i === index ? { ...contrib, [field]: value } : contrib
      )
    }));
  };

  const removeContributor = (index) => {
    setMetadataForm(prev => ({
      ...prev,
      contributors: prev.contributors.filter((_, i) => i !== index)
    }));
  };

  const addGenre = (genre) => {
    if (genre && !metadataForm.genre.includes(genre)) {
      setMetadataForm(prev => ({
        ...prev,
        genre: [...prev.genre, genre]
      }));
    }
  };

  const removeGenre = (genre) => {
    setMetadataForm(prev => ({
      ...prev,
      genre: prev.genre.filter(g => g !== genre)
    }));
  };

  const createContentRecord = async () => {
    if (!metadataForm.title || !metadataForm.main_artist || uploadedFiles.length === 0) {
      alert('Please provide title, main artist, and upload at least one file');
      return;
    }

    const formData = new FormData();
    formData.append('title', metadataForm.title);
    formData.append('main_artist', metadataForm.main_artist);
    formData.append('release_date', metadataForm.release_date);
    formData.append('genre', JSON.stringify(metadataForm.genre));
    formData.append('contributors', JSON.stringify(metadataForm.contributors));
    formData.append('file_ids', JSON.stringify(uploadedFiles.map(f => f.file_id)));
    
    if (metadataForm.licensing_terms) {
      formData.append('licensing_terms', JSON.stringify(metadataForm.licensing_terms));
    }
    
    formData.append('additional_metadata', JSON.stringify(metadataForm.additional_metadata));

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/content-ingestion/create`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('Content record created successfully!');
        // Reset form
        setMetadataForm({
          title: '',
          main_artist: '',
          release_date: new Date().toISOString().split('T')[0],
          genre: [],
          contributors: [],
          licensing_terms: null,
          additional_metadata: {}
        });
        setUploadedFiles([]);
        onUploadComplete();
      }
    } catch (error) {
      console.error('Create content error:', error);
      alert('Failed to create content record');
    }
  };

  const genreOptions = [
    'Rock', 'Pop', 'Hip Hop', 'R&B', 'Country', 'Electronic', 'Jazz', 'Classical', 
    'Folk', 'Reggae', 'Blues', 'Gospel', 'Alternative', 'Indie', 'Funk', 'Soul'
  ];

  const contributorRoles = [
    'artist', 'producer', 'songwriter', 'composer', 'performer', 'engineer', 
    'publisher', 'label', 'manager', 'featured_artist'
  ];

  return (
    <div className="space-y-8">
      {/* File Upload Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📤 File Upload</h3>
        
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragOver 
              ? 'border-purple-500 bg-purple-50' 
              : 'border-gray-300 hover:border-purple-400'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {uploading ? (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mb-4"></div>
              <p className="text-gray-600">Uploading files...</p>
            </div>
          ) : (
            <div>
              <div className="text-4xl mb-4">☁️</div>
              <p className="text-lg font-medium text-gray-900 mb-2">
                Drag and drop files here, or click to select
              </p>
              <p className="text-gray-600 mb-4">
                Supports audio, video, image files up to 100MB each
              </p>
              <input
                type="file"
                multiple
                accept="audio/*,video/*,image/*"
                onChange={(e) => handleFileUpload(e.target.files)}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="bg-purple-600 text-white px-6 py-2 rounded-lg cursor-pointer hover:bg-purple-700 transition-colors"
              >
                Select Files
              </label>
            </div>
          )}
        </div>

        {/* Uploaded Files Preview */}
        {uploadedFiles.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold mb-3">Uploaded Files:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {uploadedFiles.map((file) => (
                <div key={file.file_id} className="border rounded-lg p-3 bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="text-2xl mr-3">
                        {file.content_type === 'audio' && '🎵'}
                        {file.content_type === 'video' && '🎬'}
                        {file.content_type === 'image' && '🖼️'}
                        {file.content_type === 'document' && '📄'}
                      </div>
                      <div>
                        <p className="font-medium">{file.original_filename}</p>
                        <p className="text-sm text-gray-600">
                          {(file.file_size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <span className="text-green-600 text-sm">✅ Uploaded</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* DDEX Metadata Form */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔄 DDEX Metadata</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Basic Information */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input
              type="text"
              value={metadataForm.title}
              onChange={(e) => setMetadataForm(prev => ({ ...prev, title: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter song/content title"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Main Artist *</label>
            <input
              type="text"
              value={metadataForm.main_artist}
              onChange={(e) => setMetadataForm(prev => ({ ...prev, main_artist: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter main artist name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Release Date *</label>
            <input
              type="date"
              value={metadataForm.release_date}
              onChange={(e) => setMetadataForm(prev => ({ ...prev, release_date: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Label Name</label>
            <input
              type="text"
              value={metadataForm.additional_metadata.label_name || 'Big Mann Entertainment'}
              onChange={(e) => setMetadataForm(prev => ({ 
                ...prev, 
                additional_metadata: { ...prev.additional_metadata, label_name: e.target.value }
              }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>

        {/* Genre Selection */}
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Genres</label>
          <div className="flex flex-wrap gap-2 mb-3">
            {metadataForm.genre.map((genre) => (
              <span
                key={genre}
                className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm flex items-center"
              >
                {genre}
                <button
                  onClick={() => removeGenre(genre)}
                  className="ml-2 text-purple-600 hover:text-purple-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <div className="flex flex-wrap gap-2">
            {genreOptions.map((genre) => (
              <button
                key={genre}
                onClick={() => addGenre(genre)}
                className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                  metadataForm.genre.includes(genre)
                    ? 'bg-purple-100 text-purple-800 border-purple-300'
                    : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
                }`}
                disabled={metadataForm.genre.includes(genre)}
              >
                {genre}
              </button>
            ))}
          </div>
        </div>

        {/* Contributors Section */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">Contributors</label>
            <button
              onClick={addContributor}
              className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
            >
              + Add Contributor
            </button>
          </div>

          {metadataForm.contributors.map((contributor, index) => (
            <div key={index} className="border rounded-lg p-4 mb-3 bg-gray-50">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <input
                  type="text"
                  placeholder="Name"
                  value={contributor.name}
                  onChange={(e) => updateContributor(index, 'name', e.target.value)}
                  className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                
                <select
                  value={contributor.role}
                  onChange={(e) => updateContributor(index, 'role', e.target.value)}
                  className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {contributorRoles.map((role) => (
                    <option key={role} value={role}>{role.replace('_', ' ').toUpperCase()}</option>
                  ))}
                </select>
                
                <input
                  type="number"
                  placeholder="Percentage"
                  value={contributor.percentage}
                  onChange={(e) => updateContributor(index, 'percentage', parseFloat(e.target.value) || 0)}
                  className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  min="0"
                  max="100"
                  step="0.1"
                />
                
                <input
                  type="email"
                  placeholder="Email"
                  value={contributor.email}
                  onChange={(e) => updateContributor(index, 'email', e.target.value)}
                  className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                
                <button
                  onClick={() => removeContributor(index)}
                  className="bg-red-600 text-white px-3 py-2 rounded hover:bg-red-700"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}

          {metadataForm.contributors.length > 0 && (
            <div className="text-sm text-gray-600 mt-2">
              Total percentage: {metadataForm.contributors.reduce((sum, c) => sum + c.percentage, 0).toFixed(1)}%
              {Math.abs(metadataForm.contributors.reduce((sum, c) => sum + c.percentage, 0) - 100) > 0.1 && (
                <span className="text-red-600 ml-2">⚠️ Should total 100%</span>
              )}
            </div>
          )}
        </div>

        {/* Additional Metadata */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">P-Line (Copyright)</label>
            <input
              type="text"
              value={metadataForm.additional_metadata.p_line || ''}
              onChange={(e) => setMetadataForm(prev => ({ 
                ...prev, 
                additional_metadata: { ...prev.additional_metadata, p_line: e.target.value }
              }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="℗ 2024 Big Mann Entertainment"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">C-Line (Composition)</label>
            <input
              type="text"
              value={metadataForm.additional_metadata.c_line || ''}
              onChange={(e) => setMetadataForm(prev => ({ 
                ...prev, 
                additional_metadata: { ...prev.additional_metadata, c_line: e.target.value }
              }))}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="© 2024 Big Mann Entertainment"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="explicit_content"
              checked={metadataForm.additional_metadata.explicit_content || false}
              onChange={(e) => setMetadataForm(prev => ({ 
                ...prev, 
                additional_metadata: { ...prev.additional_metadata, explicit_content: e.target.checked }
              }))}
              className="mr-2"
            />
            <label htmlFor="explicit_content" className="text-sm font-medium text-gray-700">
              Explicit Content
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="parental_warning"
              checked={metadataForm.additional_metadata.parental_warning || false}
              onChange={(e) => setMetadataForm(prev => ({ 
                ...prev, 
                additional_metadata: { ...prev.additional_metadata, parental_warning: e.target.checked }
              }))}
              className="mr-2"
            />
            <label htmlFor="parental_warning" className="text-sm font-medium text-gray-700">
              Parental Advisory Required
            </label>
          </div>
        </div>

        {/* Description */}
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            value={metadataForm.additional_metadata.description || ''}
            onChange={(e) => setMetadataForm(prev => ({ 
              ...prev, 
              additional_metadata: { ...prev.additional_metadata, description: e.target.value }
            }))}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 h-20"
            placeholder="Describe the content..."
          />
        </div>

        {/* Create Content Button */}
        <div className="mt-8">
          <button
            onClick={createContentRecord}
            disabled={!metadataForm.title || !metadataForm.main_artist || uploadedFiles.length === 0}
            className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Create Content Record with DDEX Metadata
          </button>
        </div>
      </div>
    </div>
  );
};

// Content Library Tab Component
const ContentLibraryTab = ({ dashboardData }) => {
  const [contentList, setContentList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContent, setSelectedContent] = useState(null);

  useEffect(() => {
    fetchContentList();
  }, []);

  const fetchContentList = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/content-ingestion/content`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setContentList(response.data.content_records);
    } catch (error) {
      console.error('Error fetching content list:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewContentDetails = async (contentId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/content-ingestion/content/${contentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedContent(response.data.content_record);
    } catch (error) {
      console.error('Error fetching content details:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'processing': 'bg-yellow-100 text-yellow-800',
      'processed': 'bg-blue-100 text-blue-800',
      'ready_for_distribution': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800',
      'approved': 'bg-green-100 text-green-800',
      'needs_review': 'bg-yellow-100 text-yellow-800',
      'rejected': 'bg-red-100 text-red-800',
      'pending': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return <div className="text-center">Loading content library...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Recent Uploads Summary */}
      {dashboardData && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📚 Content Library Overview</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold mb-2">By Processing Status</h4>
              <div className="space-y-1 text-sm">
                {Object.entries(dashboardData.by_status).map(([status, count]) => (
                  <div key={status} className="flex justify-between">
                    <span className="capitalize">{status.replace('_', ' ')}:</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">By Compliance Status</h4>
              <div className="space-y-1 text-sm">
                {Object.entries(dashboardData.by_compliance).map(([status, count]) => (
                  <div key={status} className="flex justify-between">
                    <span className="capitalize">{status.replace('_', ' ')}:</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">By Content Type</h4>
              <div className="space-y-1 text-sm">
                {Object.entries(dashboardData.by_content_type).map(([type, count]) => (
                  <div key={type} className="flex justify-between">
                    <span className="capitalize">{type}:</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content List */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">All Content</h3>
        
        {contentList.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No content uploaded yet. Upload your first content in the Upload & Metadata tab!</p>
        ) : (
          <div className="space-y-4">
            {contentList.map((content) => (
              <div key={content.content_id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{content.ddex_metadata.title}</h4>
                    <p className="text-gray-600">by {content.ddex_metadata.main_artist}</p>
                    
                    <div className="mt-2 flex flex-wrap gap-2">
                      <span className={`px-2 py-1 rounded text-xs ${getStatusColor(content.processing_status)}`}>
                        {content.processing_status.replace('_', ' ')}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs ${getStatusColor(content.compliance_status)}`}>
                        {content.compliance_status.replace('_', ' ')}
                      </span>
                      {content.distribution_ready && (
                        <span className="px-2 py-1 rounded text-xs bg-purple-100 text-purple-800">
                          Distribution Ready
                        </span>
                      )}
                    </div>

                    <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div>
                        <strong>Release Date:</strong> {new Date(content.ddex_metadata.release_date).toLocaleDateString()}
                      </div>
                      <div>
                        <strong>Files:</strong> {content.content_files.length}
                      </div>
                      <div>
                        <strong>Contributors:</strong> {content.ddex_metadata.contributors.length}
                      </div>
                    </div>

                    {content.ddex_metadata.genre.length > 0 && (
                      <div className="mt-2">
                        <div className="flex flex-wrap gap-1">
                          {content.ddex_metadata.genre.map((genre) => (
                            <span key={genre} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                              {genre}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="ml-4 flex flex-col space-y-2">
                    <button
                      onClick={() => viewContentDetails(content.content_id)}
                      className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                    >
                      View Details
                    </button>
                    <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                      Generate DDEX
                    </button>
                    <button className="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700">
                      Distribute
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Content Details Modal */}
      {selectedContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">Content Details</h3>
              <button
                onClick={() => setSelectedContent(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-2">Basic Information</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Title:</strong> {selectedContent.ddex_metadata.title}</div>
                  <div><strong>Main Artist:</strong> {selectedContent.ddex_metadata.main_artist}</div>
                  <div><strong>Release Date:</strong> {new Date(selectedContent.ddex_metadata.release_date).toLocaleDateString()}</div>
                  <div><strong>Label:</strong> {selectedContent.ddex_metadata.label_name}</div>
                  <div><strong>ISRC:</strong> {selectedContent.ddex_metadata.isrc || 'Not assigned'}</div>
                  <div><strong>ISWC:</strong> {selectedContent.ddex_metadata.iswc || 'Not assigned'}</div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Contributors</h4>
                <div className="space-y-1 text-sm">
                  {selectedContent.ddex_metadata.contributors.map((contrib, index) => (
                    <div key={index} className="flex justify-between">
                      <span>{contrib.name} ({contrib.role})</span>
                      <span>{contrib.percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Content Files</h4>
                <div className="space-y-1 text-sm">
                  {selectedContent.content_files.map((file) => (
                    <div key={file.file_id} className="flex justify-between">
                      <span>{file.original_filename}</span>
                      <span>{(file.file_size / (1024 * 1024)).toFixed(2)} MB</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Status Information</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <strong>Processing:</strong>
                    <span className={`ml-2 px-2 py-1 rounded text-xs ${getStatusColor(selectedContent.processing_status)}`}>
                      {selectedContent.processing_status}
                    </span>
                  </div>
                  <div>
                    <strong>Compliance:</strong>
                    <span className={`ml-2 px-2 py-1 rounded text-xs ${getStatusColor(selectedContent.compliance_status)}`}>
                      {selectedContent.compliance_status}
                    </span>
                  </div>
                  <div><strong>Created:</strong> {new Date(selectedContent.created_at).toLocaleString()}</div>
                  <div><strong>Updated:</strong> {new Date(selectedContent.updated_at).toLocaleString()}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Compliance Tab Component
const ComplianceTab = () => {
  const [complianceRules, setComplianceRules] = useState(null);
  const [contentValidation, setContentValidation] = useState(null);
  const [selectedContentId, setSelectedContentId] = useState('');
  const [validating, setValidating] = useState(false);

  useEffect(() => {
    fetchComplianceRules();
  }, []);

  const fetchComplianceRules = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/content-ingestion/compliance/rules`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setComplianceRules(response.data.compliance_summary);
    } catch (error) {
      console.error('Error fetching compliance rules:', error);
    }
  };

  const validateContent = async () => {
    if (!selectedContentId) {
      alert('Please enter a content ID');
      return;
    }

    setValidating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/content-ingestion/compliance/validate/${selectedContentId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setContentValidation(response.data.validation_results);
    } catch (error) {
      console.error('Error validating content:', error);
      alert('Validation failed. Please check the content ID and try again.');
    } finally {
      setValidating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Compliance Rules Overview */}
      {complianceRules && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">✅ Compliance Rules Overview</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Rules by Type</h4>
              <div className="space-y-1 text-sm">
                {Object.entries(complianceRules.rules_by_type).map(([type, count]) => (
                  <div key={type} className="flex justify-between">
                    <span className="capitalize">{type.replace('_', ' ')}:</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Rules by Severity</h4>
              <div className="space-y-1 text-sm">
                {Object.entries(complianceRules.rules_by_severity).map(([severity, count]) => (
                  <div key={severity} className="flex justify-between">
                    <span className="capitalize">{severity}:</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Supported Territories</h4>
              <div className="text-sm">
                <div className="flex flex-wrap gap-1">
                  {complianceRules.supported_territories.map((territory) => (
                    <span key={territory} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                      {territory}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            <strong>Total Rules:</strong> {complianceRules.total_rules} | 
            <strong> Last Updated:</strong> {new Date(complianceRules.last_updated).toLocaleString()}
          </div>
        </div>
      )}

      {/* Content Validation */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 Content Compliance Validation</h3>
        
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            value={selectedContentId}
            onChange={(e) => setSelectedContentId(e.target.value)}
            placeholder="Enter Content ID"
            className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={validateContent}
            disabled={validating || !selectedContentId}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {validating ? 'Validating...' : 'Validate Compliance'}
          </button>
        </div>

        {/* Validation Results */}
        {contentValidation && (
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold">Validation Results</h4>
              <div className="flex items-center space-x-4">
                <span className={`px-3 py-1 rounded text-sm ${
                  contentValidation.overall_status === 'approved' ? 'bg-green-100 text-green-800' :
                  contentValidation.overall_status === 'needs_review' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {contentValidation.overall_status.replace('_', ' ').toUpperCase()}
                </span>
                <span className="text-sm text-gray-600">
                  Score: {contentValidation.compliance_score.toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{contentValidation.passed_rules.length}</div>
                <div className="text-sm text-gray-600">Passed Rules</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{contentValidation.total_issues_count}</div>
                <div className="text-sm text-gray-600">Total Issues</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{contentValidation.blocking_issues_count}</div>
                <div className="text-sm text-gray-600">Blocking Issues</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{contentValidation.auto_fixes_applied.length}</div>
                <div className="text-sm text-gray-600">Auto-fixes Applied</div>
              </div>
            </div>

            {/* Issues */}
            {contentValidation.issues.length > 0 && (
              <div className="mb-6">
                <h5 className="font-semibold mb-3 text-red-600">Critical Issues</h5>
                <div className="space-y-3">
                  {contentValidation.issues.map((issue, index) => (
                    <div key={index} className="border-l-4 border-red-500 pl-4 bg-red-50 p-3 rounded">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h6 className="font-semibold text-red-800">{issue.title}</h6>
                          <p className="text-red-700 text-sm mt-1">{issue.description}</p>
                          <p className="text-red-600 text-sm mt-2 italic">{issue.suggested_fix}</p>
                          {issue.affected_fields.length > 0 && (
                            <div className="mt-2">
                              <span className="text-xs text-red-600">Affected fields: </span>
                              <span className="text-xs text-red-800">{issue.affected_fields.join(', ')}</span>
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          <span className={`px-2 py-1 rounded text-xs ${
                            issue.severity === 'critical' ? 'bg-red-100 text-red-800' :
                            issue.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {issue.severity}
                          </span>
                          {issue.blocking && (
                            <span className="block mt-1 px-2 py-1 rounded text-xs bg-red-200 text-red-900">
                              BLOCKING
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Warnings */}
            {contentValidation.warnings.length > 0 && (
              <div className="mb-6">
                <h5 className="font-semibold mb-3 text-yellow-600">Warnings</h5>
                <div className="space-y-3">
                  {contentValidation.warnings.map((warning, index) => (
                    <div key={index} className="border-l-4 border-yellow-500 pl-4 bg-yellow-50 p-3 rounded">
                      <h6 className="font-semibold text-yellow-800">{warning.title}</h6>
                      <p className="text-yellow-700 text-sm mt-1">{warning.description}</p>
                      <p className="text-yellow-600 text-sm mt-2 italic">{warning.suggested_fix}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Auto-fixes Applied */}
            {contentValidation.auto_fixes_applied.length > 0 && (
              <div className="mb-6">
                <h5 className="font-semibold mb-3 text-blue-600">Auto-fixes Applied</h5>
                <div className="space-y-2">
                  {contentValidation.auto_fixes_applied.map((fix, index) => (
                    <div key={index} className="bg-blue-50 p-3 rounded">
                      <p className="text-blue-800 text-sm">{fix.fix_description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Passed Rules */}
            {contentValidation.passed_rules.length > 0 && (
              <div>
                <h5 className="font-semibold mb-3 text-green-600">Passed Rules</h5>
                <div className="flex flex-wrap gap-2">
                  {contentValidation.passed_rules.map((rule, index) => (
                    <span key={index} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                      {rule.rule_name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// DDEX Management Tab Component
const DDEXManagementTab = () => {
  const [selectedContentId, setSelectedContentId] = useState('');
  const [ddexXml, setDdexXml] = useState('');
  const [validationResults, setValidationResults] = useState(null);
  const [catalogXml, setCatalogXml] = useState('');
  const [loading, setLoading] = useState(false);

  const generateDDEXXml = async () => {
    if (!selectedContentId) {
      alert('Please enter a content ID');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/content-ingestion/ddex/generate-xml/${selectedContentId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setDdexXml(response.data.ddex_xml);
    } catch (error) {
      console.error('Error generating DDEX XML:', error);
      alert('Failed to generate DDEX XML. Please check the content ID.');
    } finally {
      setLoading(false);
    }
  };

  const validateDDEXXml = async () => {
    if (!ddexXml) {
      alert('Please generate or enter DDEX XML first');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/content-ingestion/ddex/validate-xml`,
        ddexXml,
        { 
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'text/plain'
          } 
        }
      );
      setValidationResults(response.data.validation_results);
    } catch (error) {
      console.error('Error validating DDEX XML:', error);
      alert('Failed to validate DDEX XML');
    } finally {
      setLoading(false);
    }
  };

  const generateCatalogXml = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/content-ingestion/ddex/catalog`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setCatalogXml(response.data.catalog_xml);
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      console.error('Error generating catalog XML:', error);
      alert('Failed to generate catalog XML');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* DDEX XML Generation */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔄 Generate DDEX ERN XML</h3>
        
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            value={selectedContentId}
            onChange={(e) => setSelectedContentId(e.target.value)}
            placeholder="Enter Content ID"
            className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={generateDDEXXml}
            disabled={loading || !selectedContentId}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate DDEX XML'}
          </button>
        </div>

        {ddexXml && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold">Generated DDEX XML</h4>
              <div className="space-x-2">
                <button
                  onClick={validateDDEXXml}
                  className="bg-blue-600 text-white px-4 py-1 rounded text-sm hover:bg-blue-700"
                >
                  Validate XML
                </button>
                <button
                  onClick={() => navigator.clipboard.writeText(ddexXml)}
                  className="bg-gray-600 text-white px-4 py-1 rounded text-sm hover:bg-gray-700"
                >
                  Copy XML
                </button>
              </div>
            </div>
            <textarea
              value={ddexXml}
              onChange={(e) => setDdexXml(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md font-mono text-sm h-60"
              placeholder="DDEX XML will appear here..."
            />
          </div>
        )}

        {/* Validation Results */}
        {validationResults && (
          <div className={`border rounded-lg p-4 ${
            validationResults.is_valid ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
          }`}>
            <div className="flex items-center mb-3">
              <span className={`text-2xl mr-2 ${validationResults.is_valid ? 'text-green-600' : 'text-red-600'}`}>
                {validationResults.is_valid ? '✅' : '❌'}
              </span>
              <h4 className={`font-semibold ${validationResults.is_valid ? 'text-green-800' : 'text-red-800'}`}>
                DDEX XML {validationResults.is_valid ? 'Valid' : 'Invalid'}
              </h4>
            </div>

            {validationResults.errors.length > 0 && (
              <div className="mb-3">
                <h5 className="font-semibold text-red-700 mb-2">Errors:</h5>
                <ul className="list-disc list-inside text-red-600 text-sm space-y-1">
                  {validationResults.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}

            {validationResults.warnings.length > 0 && (
              <div className="mb-3">
                <h5 className="font-semibold text-yellow-700 mb-2">Warnings:</h5>
                <ul className="list-disc list-inside text-yellow-600 text-sm space-y-1">
                  {validationResults.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}

            {validationResults.info.length > 0 && (
              <div>
                <h5 className="font-semibold text-blue-700 mb-2">Information:</h5>
                <ul className="list-disc list-inside text-blue-600 text-sm space-y-1">
                  {validationResults.info.map((info, index) => (
                    <li key={index}>{info}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Catalog Generation */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Generate DDEX Catalog XML</h3>
        
        <div className="mb-4">
          <button
            onClick={generateCatalogXml}
            disabled={loading}
            className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Catalog XML'}
          </button>
        </div>

        {catalogXml && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold">Generated Catalog XML</h4>
              <button
                onClick={() => navigator.clipboard.writeText(catalogXml)}
                className="bg-gray-600 text-white px-4 py-1 rounded text-sm hover:bg-gray-700"
              >
                Copy XML
              </button>
            </div>
            <textarea
              value={catalogXml}
              readOnly
              className="w-full p-3 border border-gray-300 rounded-md font-mono text-sm h-60 bg-gray-50"
              placeholder="Catalog XML will appear here..."
            />
          </div>
        )}
      </div>

      {/* DDEX Standards Information */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📚 DDEX Standards Information</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold mb-2">Supported DDEX Standards</h4>
            <ul className="text-sm space-y-1 text-gray-700">
              <li>• ERN (Electronic Release Notification) v4.1</li>
              <li>• Catalog List Message v4.1</li>
              <li>• Sales Report Message (Coming Soon)</li>
              <li>• DDEX Music Industry Metadata Standards</li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-2">Required Metadata Fields</h4>
            <ul className="text-sm space-y-1 text-gray-700">
              <li>• Title and Main Artist</li>
              <li>• Release Date and Label Information</li>
              <li>• ISRC and ISWC Codes</li>
              <li>• Contributor Information with Roles</li>
              <li>• Copyright (P-Line and C-Line)</li>
              <li>• Genre and Territory Information</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-semibold text-blue-800 mb-2">💡 Best Practices</h4>
          <ul className="text-sm space-y-1 text-blue-700">
            <li>• Ensure all contributor percentages total 100%</li>
            <li>• Use proper ISRC format (CC-XXX-YY-NNNNN)</li>
            <li>• Include complete copyright information</li>
            <li>• Validate XML before distribution</li>
            <li>• Keep metadata consistent across platforms</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// Analytics Tab Component
const AnalyticsTab = ({ dashboardData }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [selectedContentId, setSelectedContentId] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchContentAnalytics = async () => {
    if (!selectedContentId) {
      alert('Please enter a content ID');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/content-ingestion/analytics/${selectedContentId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAnalyticsData(response.data.analytics);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      alert('Failed to fetch analytics. Please check the content ID.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Analytics Overview */}
      {dashboardData && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Content Analytics Overview</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{dashboardData.total_content}</div>
              <div className="text-sm text-gray-600">Total Content Pieces</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{dashboardData.by_status.ready_for_distribution}</div>
              <div className="text-sm text-gray-600">Distribution Ready</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{dashboardData.storage_usage.total_files}</div>
              <div className="text-sm text-gray-600">Total Files</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{Math.round(dashboardData.storage_usage.total_size_mb)}</div>
              <div className="text-sm text-gray-600">Storage Used (MB)</div>
            </div>
          </div>
        </div>
      )}

      {/* Content Analytics */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 Individual Content Analytics</h3>
        
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            value={selectedContentId}
            onChange={(e) => setSelectedContentId(e.target.value)}
            placeholder="Enter Content ID"
            className="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={fetchContentAnalytics}
            disabled={loading || !selectedContentId}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Get Analytics'}
          </button>
        </div>

        {analyticsData && (
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-3">Basic Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div><strong>Title:</strong> {analyticsData.title}</div>
                <div><strong>Main Artist:</strong> {analyticsData.main_artist}</div>
                <div><strong>Upload Date:</strong> {new Date(analyticsData.upload_date).toLocaleDateString()}</div>
                <div><strong>Processing Status:</strong> 
                  <span className={`ml-2 px-2 py-1 rounded text-xs ${
                    analyticsData.processing_status === 'processed' ? 'bg-green-100 text-green-800' :
                    analyticsData.processing_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {analyticsData.processing_status}
                  </span>
                </div>
                <div><strong>Compliance Status:</strong>
                  <span className={`ml-2 px-2 py-1 rounded text-xs ${
                    analyticsData.compliance_status === 'approved' ? 'bg-green-100 text-green-800' :
                    analyticsData.compliance_status === 'needs_review' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {analyticsData.compliance_status}
                  </span>
                </div>
                <div><strong>Distribution Ready:</strong> {analyticsData.distribution_readiness ? '✅ Yes' : '❌ No'}</div>
              </div>
            </div>

            {/* File Statistics */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-3">File Statistics</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div><strong>Total Files:</strong> {analyticsData.file_stats.total_files}</div>
                <div><strong>Total Size:</strong> {analyticsData.file_stats.total_size_mb.toFixed(2)} MB</div>
                <div><strong>File Types:</strong> {analyticsData.file_stats.file_types.join(', ')}</div>
              </div>
            </div>

            {/* Metadata Completeness */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-3">Metadata Completeness</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="flex items-center">
                  <span className={analyticsData.metadata_completeness.isrc_assigned ? 'text-green-600' : 'text-red-600'}>
                    {analyticsData.metadata_completeness.isrc_assigned ? '✅' : '❌'}
                  </span>
                  <span className="ml-2">ISRC Assigned</span>
                </div>
                <div className="flex items-center">
                  <span className={analyticsData.metadata_completeness.iswc_assigned ? 'text-green-600' : 'text-red-600'}>
                    {analyticsData.metadata_completeness.iswc_assigned ? '✅' : '❌'}
                  </span>
                  <span className="ml-2">ISWC Assigned</span>
                </div>
                <div><strong>Contributors:</strong> {analyticsData.metadata_completeness.contributors_count}</div>
                <div><strong>Genres:</strong> {analyticsData.metadata_completeness.genres_count}</div>
                <div className="flex items-center">
                  <span className={analyticsData.metadata_completeness.licensing_terms_defined ? 'text-green-600' : 'text-red-600'}>
                    {analyticsData.metadata_completeness.licensing_terms_defined ? '✅' : '❌'}
                  </span>
                  <span className="ml-2">Licensing Terms Defined</span>
                </div>
              </div>
            </div>

            {/* Optimization Suggestions */}
            {analyticsData.optimization_suggestions.length > 0 && (
              <div className="border rounded-lg p-4">
                <h4 className="font-semibold mb-3">💡 Optimization Suggestions</h4>
                <ul className="space-y-2 text-sm">
                  {analyticsData.optimization_suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-blue-600 mr-2">•</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Revenue Potential */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-3">📈 Revenue Potential Analysis</h4>
              <div className="text-center">
                <div className={`text-3xl font-bold mb-2 ${
                  analyticsData.estimated_revenue_potential === 'high' ? 'text-green-600' :
                  analyticsData.estimated_revenue_potential === 'medium' ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {analyticsData.estimated_revenue_potential.toUpperCase()}
                </div>
                <div className="text-sm text-gray-600">Estimated Revenue Potential</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Common Issues */}
      {dashboardData && dashboardData.compliance_issues_summary.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">⚠️ Common Compliance Issues</h3>
          
          <div className="space-y-3">
            {dashboardData.compliance_issues_summary.map((issue, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <span className="text-yellow-800">{issue.issue}</span>
                <span className="bg-yellow-200 text-yellow-800 px-2 py-1 rounded text-sm font-semibold">
                  {issue.count} occurrence{issue.count !== 1 ? 's' : ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Transcoding Tab Component - Function 2: Transcoding & Format Optimization
const TranscodingTab = () => {
  const [activeTranscodingTab, setActiveTranscodingTab] = useState('jobs');
  const [transcodingJobs, setTranscodingJobs] = useState([]);
  const [presets, setPresets] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newJobForm, setNewJobForm] = useState({
    content_id: '',
    input_file_path: '',
    input_format: '',
    output_format: 'mp4',
    quality_preset: 'medium',
    platform_target: '',
    custom_settings: {}
  });
  const [selectedPlatform, setSelectedPlatform] = useState('youtube');
  const [contentMetadata, setContentMetadata] = useState({
    format: 'mp4',
    file_size: 50000000,
    duration: 180,
    resolution: '1920x1080',
    content_type: 'video'
  });
  const [optimizationRecommendations, setOptimizationRecommendations] = useState(null);

  useEffect(() => {
    fetchTranscodingData();
  }, []);

  const fetchTranscodingData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch transcoding jobs
      const jobsResponse = await axios.get(`${API}/api/transcoding/jobs`, { headers });
      setTranscodingJobs(jobsResponse.data.transcoding_jobs || []);

      // Fetch available presets
      const presetsResponse = await axios.get(`${API}/api/transcoding/presets`, { headers });
      setPresets(Object.values(presetsResponse.data.presets || {}));

      // Fetch platform requirements
      const platformsResponse = await axios.get(`${API}/api/transcoding/platforms`, { headers });
      setPlatforms(Object.values(platformsResponse.data.platforms || {}));

    } catch (error) {
      console.error('Error fetching transcoding data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTranscodingJob = async () => {
    if (!newJobForm.content_id || !newJobForm.input_file_path) {
      alert('Please provide content ID and input file path');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/transcoding/jobs/create`, newJobForm, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('Transcoding job created successfully!');
        setNewJobForm({
          content_id: '',
          input_file_path: '',
          input_format: '',
          output_format: 'mp4',
          quality_preset: 'medium',
          platform_target: '',
          custom_settings: {}
        });
        fetchTranscodingData();
      }
    } catch (error) {
      console.error('Error creating transcoding job:', error);
      alert('Failed to create transcoding job');
    }
  };

  const startTranscodingJob = async (jobId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/transcoding/jobs/${jobId}/start`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Transcoding job started!');
      fetchTranscodingData();
    } catch (error) {
      console.error('Error starting transcoding job:', error);
      alert('Failed to start transcoding job');
    }
  };

  const getOptimizationRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/transcoding/optimize/recommendations?platform_name=${selectedPlatform}`,
        contentMetadata,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setOptimizationRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error getting optimization recommendations:', error);
      alert('Failed to get optimization recommendations');
    }
  };

  const transcodingTabs = [
    { id: 'jobs', name: 'Transcoding Jobs', icon: '⚙️' },
    { id: 'presets', name: 'Quality Presets', icon: '🎛️' },
    { id: 'platforms', name: 'Platform Requirements', icon: '📱' },
    { id: 'optimization', name: 'Format Optimization', icon: '🚀' }
  ];

  const getStatusColor = (status) => {
    const colors = {
      'pending': 'bg-gray-100 text-gray-800',
      'processing': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800',
      'cancelled': 'bg-yellow-100 text-yellow-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">🎬 Transcoding & Format Optimization</h3>
        <p className="text-gray-600">Convert media to different formats and optimize for various platforms</p>
      </div>

      {/* Sub-navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {transcodingTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTranscodingTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTranscodingTab === tab.id
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

      {/* Jobs Tab */}
      {activeTranscodingTab === 'jobs' && (
        <div className="space-y-6">
          {/* Create New Job */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">⚙️ Create Transcoding Job</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content ID *</label>
                <input
                  type="text"
                  value={newJobForm.content_id}
                  onChange={(e) => setNewJobForm(prev => ({ ...prev, content_id: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter content ID"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Input File Path *</label>
                <input
                  type="text"
                  value={newJobForm.input_file_path}
                  onChange={(e) => setNewJobForm(prev => ({ ...prev, input_file_path: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Path to input file"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Input Format</label>
                <input
                  type="text"
                  value={newJobForm.input_format}
                  onChange={(e) => setNewJobForm(prev => ({ ...prev, input_format: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="e.g., mp4, avi, mov"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Output Format</label>
                <select
                  value={newJobForm.output_format}
                  onChange={(e) => setNewJobForm(prev => ({ ...prev, output_format: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="mp4">MP4</option>
                  <option value="webm">WebM</option>
                  <option value="avi">AVI</option>
                  <option value="mov">MOV</option>
                  <option value="mp3">MP3</option>
                  <option value="aac">AAC</option>
                  <option value="ogg">OGG</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quality Preset</label>
                <select
                  value={newJobForm.quality_preset}
                  onChange={(e) => setNewJobForm(prev => ({ ...prev, quality_preset: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="low">Low (480p)</option>
                  <option value="medium">Medium (720p)</option>
                  <option value="high">High (1080p)</option>
                  <option value="ultra">Ultra (4K)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Platform Target</label>
                <select
                  value={newJobForm.platform_target}
                  onChange={(e) => setNewJobForm(prev => ({ ...prev, platform_target: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">No specific platform</option>
                  <option value="youtube">YouTube</option>
                  <option value="tiktok">TikTok</option>
                  <option value="instagram">Instagram</option>
                  <option value="facebook">Facebook</option>
                  <option value="twitter">Twitter</option>
                  <option value="spotify">Spotify</option>
                  <option value="apple_music">Apple Music</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={createTranscodingJob}
                className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700"
              >
                Create Transcoding Job
              </button>
            </div>
          </div>

          {/* Jobs List */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">📋 Transcoding Jobs</h4>
            
            {loading ? (
              <div className="text-center py-8">Loading transcoding jobs...</div>
            ) : transcodingJobs.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No transcoding jobs yet. Create your first job above!</p>
            ) : (
              <div className="space-y-4">
                {transcodingJobs.map((job) => (
                  <div key={job.job_id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h5 className="font-semibold">Job ID: {job.job_id}</h5>
                        <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div><strong>Content:</strong> {job.content_id}</div>
                          <div><strong>Format:</strong> {job.input_format} → {job.output_format}</div>
                          <div><strong>Quality:</strong> {job.quality_preset}</div>
                        </div>
                        {job.platform_target && (
                          <div className="mt-2 text-sm text-gray-600">
                            <strong>Platform:</strong> {job.platform_target}
                          </div>
                        )}
                        <div className="mt-2 flex items-center space-x-4">
                          <span className={`px-2 py-1 rounded text-xs ${getStatusColor(job.status)}`}>
                            {job.status}
                          </span>
                          {job.progress_percentage > 0 && (
                            <div className="flex items-center space-x-2">
                              <div className="w-20 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-purple-600 h-2 rounded-full" 
                                  style={{ width: `${job.progress_percentage}%` }}
                                ></div>
                              </div>
                              <span className="text-xs text-gray-600">{job.progress_percentage.toFixed(1)}%</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="ml-4">
                        {job.status === 'pending' && (
                          <button
                            onClick={() => startTranscodingJob(job.job_id)}
                            className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                          >
                            Start Job
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Presets Tab */}
      {activeTranscodingTab === 'presets' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">🎛️ Quality Presets</h4>
          
          {loading ? (
            <div className="text-center py-8">Loading presets...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {presets.map((preset) => (
                <div key={preset.preset_id} className="border rounded-lg p-4">
                  <h5 className="font-semibold text-lg mb-2">{preset.name}</h5>
                  <p className="text-gray-600 text-sm mb-3">{preset.description}</p>
                  
                  <div className="space-y-2 text-sm">
                    <div><strong>Format:</strong> {preset.output_format.toUpperCase()}</div>
                    <div><strong>Quality:</strong> {preset.quality_level}</div>
                    {preset.resolution && <div><strong>Resolution:</strong> {preset.resolution}</div>}
                    {preset.video_bitrate && <div><strong>Video Bitrate:</strong> {preset.video_bitrate}</div>}
                    {preset.audio_bitrate && <div><strong>Audio Bitrate:</strong> {preset.audio_bitrate}</div>}
                    {preset.frame_rate && <div><strong>Frame Rate:</strong> {preset.frame_rate} fps</div>}
                  </div>

                  {preset.platform_optimized && preset.platform_optimized.length > 0 && (
                    <div className="mt-3">
                      <div className="text-sm font-medium text-gray-700 mb-1">Optimized for:</div>
                      <div className="flex flex-wrap gap-1">
                        {preset.platform_optimized.map((platform) => (
                          <span key={platform} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                            {platform}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Platforms Tab */}
      {activeTranscodingTab === 'platforms' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">📱 Platform Requirements</h4>
          
          {loading ? (
            <div className="text-center py-8">Loading platform requirements...</div>
          ) : (
            <div className="space-y-6">
              {platforms.map((platform) => (
                <div key={platform.platform_name} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h5 className="font-semibold text-lg">{platform.platform_name.replace('_', ' ').toUpperCase()}</h5>
                      <span className="text-sm text-gray-600 capitalize">{platform.platform_type.replace('_', ' ')}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                    <div>
                      <strong>Supported Formats:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {platform.supported_formats?.map((format) => (
                          <span key={format} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                            {format.toUpperCase()}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <strong>Preferred Formats:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {platform.preferred_formats?.map((format) => (
                          <span key={format} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                            {format.toUpperCase()}
                          </span>
                        ))}
                      </div>
                    </div>

                    {platform.max_file_size && (
                      <div>
                        <strong>Max File Size:</strong>
                        <span className="ml-2">{(platform.max_file_size / (1024 * 1024)).toFixed(0)} MB</span>
                      </div>
                    )}

                    {platform.max_duration && (
                      <div>
                        <strong>Max Duration:</strong>
                        <span className="ml-2">{Math.floor(platform.max_duration / 60)}:{String(platform.max_duration % 60).padStart(2, '0')}</span>
                      </div>
                    )}

                    {platform.aspect_ratios && platform.aspect_ratios.length > 0 && (
                      <div>
                        <strong>Aspect Ratios:</strong>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {platform.aspect_ratios.map((ratio) => (
                            <span key={ratio} className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                              {ratio}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {platform.frame_rates && platform.frame_rates.length > 0 && (
                      <div>
                        <strong>Frame Rates:</strong>
                        <span className="ml-2">{platform.frame_rates.join(', ')} fps</span>
                      </div>
                    )}
                  </div>

                  {platform.special_requirements && Object.keys(platform.special_requirements).length > 0 && (
                    <div className="mt-4 p-3 bg-yellow-50 rounded">
                      <strong className="text-yellow-800">Special Requirements:</strong>
                      <ul className="mt-1 text-sm text-yellow-700">
                        {Object.entries(platform.special_requirements).map(([key, value]) => (
                          <li key={key}>• {key.replace('_', ' ')}: {String(value)}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Optimization Tab */}
      {activeTranscodingTab === 'optimization' && (
        <div className="space-y-6">
          {/* Content Metadata Input */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">🚀 Format Optimization</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
                <select
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="youtube">YouTube</option>
                  <option value="tiktok">TikTok</option>
                  <option value="instagram">Instagram</option>
                  <option value="facebook">Facebook</option>
                  <option value="twitter">Twitter</option>
                  <option value="spotify">Spotify</option>
                  <option value="apple_music">Apple Music</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
                <select
                  value={contentMetadata.content_type}
                  onChange={(e) => setContentMetadata(prev => ({ ...prev, content_type: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="video">Video</option>
                  <option value="audio">Audio</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Format</label>
                <input
                  type="text"
                  value={contentMetadata.format}
                  onChange={(e) => setContentMetadata(prev => ({ ...prev, format: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">File Size (bytes)</label>
                <input
                  type="number"
                  value={contentMetadata.file_size}
                  onChange={(e) => setContentMetadata(prev => ({ ...prev, file_size: parseInt(e.target.value) || 0 }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Duration (seconds)</label>
                <input
                  type="number"
                  value={contentMetadata.duration}
                  onChange={(e) => setContentMetadata(prev => ({ ...prev, duration: parseInt(e.target.value) || 0 }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Resolution</label>
                <input
                  type="text"
                  value={contentMetadata.resolution}
                  onChange={(e) => setContentMetadata(prev => ({ ...prev, resolution: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="1920x1080"
                />
              </div>
            </div>

            <button
              onClick={getOptimizationRecommendations}
              className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700"
            >
              Get Optimization Recommendations
            </button>
          </div>

          {/* Optimization Results */}
          {optimizationRecommendations && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">📊 Optimization Recommendations</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Format Changes */}
                {optimizationRecommendations.format_changes && Object.keys(optimizationRecommendations.format_changes).length > 0 && (
                  <div className="border rounded-lg p-4">
                    <h5 className="font-semibold mb-3">Format Changes</h5>
                    {Object.entries(optimizationRecommendations.format_changes).map(([key, value]) => (
                      <div key={key} className="text-sm">
                        <strong>{key.replace('_', ' ')}:</strong> {value}
                      </div>
                    ))}
                  </div>
                )}

                {/* Quality Adjustments */}
                {optimizationRecommendations.quality_adjustments && Object.keys(optimizationRecommendations.quality_adjustments).length > 0 && (
                  <div className="border rounded-lg p-4">
                    <h5 className="font-semibold mb-3">Quality Adjustments</h5>
                    {Object.entries(optimizationRecommendations.quality_adjustments).map(([key, value]) => (
                      <div key={key} className="text-sm">
                        <strong>{key.replace('_', ' ')}:</strong> {value}
                      </div>
                    ))}
                  </div>
                )}

                {/* Optimizations */}
                {optimizationRecommendations.optimizations && Object.keys(optimizationRecommendations.optimizations).length > 0 && (
                  <div className="border rounded-lg p-4">
                    <h5 className="font-semibold mb-3">Optimizations</h5>
                    {Object.entries(optimizationRecommendations.optimizations).map(([key, value]) => (
                      <div key={key} className="text-sm">
                        <strong>{key.replace('_', ' ')}:</strong> {value}
                      </div>
                    ))}
                  </div>
                )}

                {/* Impact Estimation */}
                <div className="border rounded-lg p-4">
                  <h5 className="font-semibold mb-3">Impact Estimation</h5>
                  <div className="space-y-2 text-sm">
                    <div><strong>File Size Reduction:</strong> {(optimizationRecommendations.estimated_file_size_reduction / (1024*1024)).toFixed(2)} MB</div>
                    <div><strong>Quality Impact:</strong> {optimizationRecommendations.estimated_quality_impact.replace('_', ' ')}</div>
                    <div><strong>Processing Time:</strong> {optimizationRecommendations.processing_time_estimate}</div>
                  </div>
                </div>
              </div>

              {/* Special Requirements */}
              {optimizationRecommendations.special_requirements && Object.keys(optimizationRecommendations.special_requirements).length > 0 && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h5 className="font-semibold text-blue-800 mb-3">Special Requirements</h5>
                  <div className="space-y-1 text-sm text-blue-700">
                    {Object.entries(optimizationRecommendations.special_requirements).map(([key, value]) => (
                      <div key={key}>• {key.replace('_', ' ')}: {String(value)}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Distribution Tab Component - Function 3: Content Distribution & Delivery Management
const DistributionTab = () => {
  const [activeDistributionTab, setActiveDistributionTab] = useState('plans');
  const [deliveryPlans, setDeliveryPlans] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newPlanForm, setNewPlanForm] = useState({
    content_id: '',
    target_platforms: [],
    strategy: 'optimized_timing',
    optimization_goal: 'max_reach',
    target_timezone: 'UTC',
    content_type: 'music'
  });

  useEffect(() => {
    fetchDistributionData();
  }, []);

  const fetchDistributionData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch delivery plans
      const plansResponse = await axios.get(`${API}/api/distribution/delivery-plans`, { headers });
      setDeliveryPlans(plansResponse.data.delivery_plans || []);

      // Fetch available platforms
      const platformsResponse = await axios.get(`${API}/api/distribution/platforms`, { headers });
      setPlatforms(Object.values(platformsResponse.data.platforms || {}));

      // Fetch analytics
      const analyticsResponse = await axios.get(`${API}/api/distribution/analytics/delivery-performance`, { headers });
      setAnalytics(analyticsResponse.data.analytics);

    } catch (error) {
      console.error('Error fetching distribution data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createDeliveryPlan = async () => {
    if (!newPlanForm.content_id || newPlanForm.target_platforms.length === 0) {
      alert('Please provide content ID and select at least one platform');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/distribution/delivery-plans/create`, newPlanForm, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('Delivery plan created successfully!');
        setNewPlanForm({
          content_id: '',
          target_platforms: [],
          strategy: 'optimized_timing',
          optimization_goal: 'max_reach',
          target_timezone: 'UTC',
          content_type: 'music'
        });
        fetchDistributionData();
      }
    } catch (error) {
      console.error('Error creating delivery plan:', error);
      alert('Failed to create delivery plan');
    }
  };

  const getRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/distribution/recommendations/platforms?content_type=${newPlanForm.content_type}&target_audience=general&budget_level=medium`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRecommendations(response.data.recommendations || []);
    } catch (error) {
      console.error('Error getting recommendations:', error);
    }
  };

  const distributionTabs = [
    { id: 'plans', name: 'Delivery Plans', icon: '📋' },
    { id: 'platforms', name: 'Platform Management', icon: '🏢' },
    { id: 'analytics', name: 'Distribution Analytics', icon: '📈' },
    { id: 'recommendations', name: 'Platform Recommendations', icon: '💡' }
  ];

  const strategies = {
    'immediate': { name: 'Immediate', desc: 'All platforms simultaneously' },
    'optimized_timing': { name: 'Optimized Timing', desc: 'Peak audience hours' },
    'staggered_release': { name: 'Staggered Release', desc: 'Fastest platforms first' },
    'regional_rollout': { name: 'Regional Rollout', desc: 'By geographic reach' },
    'test_and_scale': { name: 'Test & Scale', desc: 'High-success platforms first' }
  };

  const goals = {
    'max_reach': { name: 'Maximum Reach', desc: 'Largest audience' },
    'max_revenue': { name: 'Maximum Revenue', desc: 'Best revenue sharing' },
    'fastest_delivery': { name: 'Fastest Delivery', desc: 'Quick processing' },
    'quality_focused': { name: 'Quality Focused', desc: 'High engagement' },
    'cost_effective': { name: 'Cost Effective', desc: 'Best ROI' }
  };

  const handlePlatformToggle = (platformId) => {
    setNewPlanForm(prev => ({
      ...prev,
      target_platforms: prev.target_platforms.includes(platformId)
        ? prev.target_platforms.filter(p => p !== platformId)
        : [...prev.target_platforms, platformId]
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">🌐 Content Distribution & Delivery Management</h3>
        <p className="text-gray-600">Optimize content distribution across multiple platforms with intelligent delivery strategies</p>
      </div>

      {/* Sub-navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {distributionTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveDistributionTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeDistributionTab === tab.id
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

      {/* Plans Tab */}
      {activeDistributionTab === 'plans' && (
        <div className="space-y-6">
          {/* Create New Plan */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">📋 Create Delivery Plan</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content ID *</label>
                <input
                  type="text"
                  value={newPlanForm.content_id}
                  onChange={(e) => setNewPlanForm(prev => ({ ...prev, content_id: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter content ID"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
                <select
                  value={newPlanForm.content_type}
                  onChange={(e) => setNewPlanForm(prev => ({ ...prev, content_type: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="music">Music</option>
                  <option value="video">Video</option>
                  <option value="podcast">Podcast</option>
                  <option value="audiobook">Audiobook</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Distribution Strategy</label>
                <select
                  value={newPlanForm.strategy}
                  onChange={(e) => setNewPlanForm(prev => ({ ...prev, strategy: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {Object.entries(strategies).map(([key, strategy]) => (
                    <option key={key} value={key}>{strategy.name} - {strategy.desc}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Optimization Goal</label>
                <select
                  value={newPlanForm.optimization_goal}
                  onChange={(e) => setNewPlanForm(prev => ({ ...prev, optimization_goal: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {Object.entries(goals).map(([key, goal]) => (
                    <option key={key} value={key}>{goal.name} - {goal.desc}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Platform Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Target Platforms *</label>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {platforms.slice(0, 12).map((platform) => (
                  <div key={platform.id} className="flex items-center">
                    <input
                      id={platform.id}
                      type="checkbox"
                      checked={newPlanForm.target_platforms.includes(platform.id)}
                      onChange={() => handlePlatformToggle(platform.id)}
                      className="mr-2"
                    />
                    <label htmlFor={platform.id} className="text-sm text-gray-700 cursor-pointer">
                      {platform.name}
                    </label>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-600 mt-2">
                Selected: {newPlanForm.target_platforms.length} platforms
              </p>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={createDeliveryPlan}
                className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700"
              >
                Create Delivery Plan
              </button>
              <button
                onClick={getRecommendations}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
              >
                Get Platform Recommendations
              </button>
            </div>
          </div>

          {/* Delivery Plans List */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">📋 Your Delivery Plans</h4>
            
            {loading ? (
              <div className="text-center py-8">Loading delivery plans...</div>
            ) : deliveryPlans.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No delivery plans yet. Create your first plan above!</p>
            ) : (
              <div className="space-y-4">
                {deliveryPlans.map((plan) => (
                  <div key={plan.plan_id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h5 className="font-semibold">Content: {plan.content_id}</h5>
                        <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div><strong>Strategy:</strong> {strategies[plan.strategy]?.name || plan.strategy}</div>
                          <div><strong>Goal:</strong> {goals[plan.optimization_goal]?.name || plan.optimization_goal}</div>
                          <div><strong>Platforms:</strong> {plan.delivery_windows?.length || 0}</div>
                        </div>
                        <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div><strong>Est. Reach:</strong> {plan.total_estimated_reach?.toLocaleString() || 'N/A'}</div>
                          <div><strong>Est. Revenue:</strong> ${plan.total_estimated_revenue || 0}</div>
                          <div><strong>Confidence:</strong> {plan.confidence_score || 0}%</div>
                        </div>
                        {plan.recommended_sequence && plan.recommended_sequence.length > 0 && (
                          <div className="mt-2">
                            <strong className="text-sm text-gray-700">Platform Sequence:</strong>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {plan.recommended_sequence.map((platform, index) => (
                                <span key={platform} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                                  {index + 1}. {platform}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {plan.risk_factors && plan.risk_factors.length > 0 && (
                          <div className="mt-2">
                            <strong className="text-sm text-red-700">Risk Factors:</strong>
                            <ul className="text-xs text-red-600 mt-1">
                              {plan.risk_factors.map((risk, index) => (
                                <li key={index}>• {risk}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                      <div className="ml-4 text-right">
                        <div className="text-xs text-gray-500">
                          Created: {new Date(plan.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Platforms Tab */}
      {activeDistributionTab === 'platforms' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">🏢 Platform Management</h4>
          
          {loading ? (
            <div className="text-center py-8">Loading platforms...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {platforms.map((platform) => (
                <div key={platform.id} className="border rounded-lg p-4">
                  <h5 className="font-semibold text-lg mb-2">{platform.name}</h5>
                  
                  <div className="space-y-2 text-sm">
                    <div><strong>Engagement Score:</strong> {platform.engagement_score}%</div>
                    <div><strong>Success Rate:</strong> {platform.success_rate}%</div>
                    <div><strong>Global Reach:</strong> {(platform.global_reach / 1000000).toFixed(1)}M users</div>
                    <div><strong>Processing Time:</strong> {platform.avg_processing_time} hours</div>
                    <div><strong>Revenue Multiplier:</strong> {platform.revenue_multiplier}x</div>
                    <div><strong>Delivery Cost:</strong> ${platform.delivery_cost}</div>
                  </div>

                  {platform.peak_hours && platform.peak_hours.length > 0 && (
                    <div className="mt-3">
                      <div className="text-sm font-medium text-gray-700 mb-1">Peak Hours:</div>
                      <div className="flex flex-wrap gap-1">
                        {platform.peak_hours.map((hour) => (
                          <span key={hour} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                            {hour}:00
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {platform.content_preferences && platform.content_preferences.length > 0 && (
                    <div className="mt-3">
                      <div className="text-sm font-medium text-gray-700 mb-1">Content Types:</div>
                      <div className="flex flex-wrap gap-1">
                        {platform.content_preferences.map((type) => (
                          <span key={type} className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                            {type}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeDistributionTab === 'analytics' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">📈 Distribution Analytics</h4>
            
            {analytics ? (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{analytics.total_deliveries}</div>
                  <div className="text-sm text-gray-600">Total Deliveries</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{analytics.successful_deliveries}</div>
                  <div className="text-sm text-gray-600">Successful</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-600">{analytics.failed_deliveries}</div>
                  <div className="text-sm text-gray-600">Failed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">{analytics.success_rate}%</div>
                  <div className="text-sm text-gray-600">Success Rate</div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No analytics data available yet.</p>
            )}
          </div>

          {analytics && analytics.total_reach > 0 && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h5 className="font-semibold mb-3">Performance Metrics</h5>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{(analytics.total_reach / 1000000).toFixed(1)}M</div>
                  <div className="text-sm text-gray-600">Total Reach</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">${analytics.total_revenue?.toFixed(2) || '0.00'}</div>
                  <div className="text-sm text-gray-600">Total Revenue</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{analytics.average_delivery_time?.toFixed(1) || 'N/A'}</div>
                  <div className="text-sm text-gray-600">Avg Delivery Time (hrs)</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommendations Tab */}
      {activeDistributionTab === 'recommendations' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">💡 Platform Recommendations</h4>
          
          <div className="mb-4">
            <button
              onClick={getRecommendations}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Get Recommendations for {newPlanForm.content_type}
            </button>
          </div>

          {recommendations.length > 0 ? (
            <div className="space-y-4">
              {recommendations.map((rec) => (
                <div key={rec.platform} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h5 className="font-semibold text-lg">{rec.platform.replace('_', ' ').toUpperCase()}</h5>
                      <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div><strong>Recommendation Score:</strong> {rec.recommendation_score}/100</div>
                        <div><strong>Engagement:</strong> {rec.engagement_score}%</div>
                        <div><strong>Success Rate:</strong> {rec.success_rate}%</div>
                      </div>
                      <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div><strong>Est. Reach:</strong> {(rec.estimated_reach / 1000000).toFixed(1)}M</div>
                        <div><strong>Cost:</strong> ${rec.cost_per_delivery}</div>
                        <div><strong>Processing:</strong> {rec.processing_time_hours}h</div>
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-gray-600">{rec.reasoning}</p>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className={`px-3 py-1 rounded text-sm ${
                        rec.recommendation_score >= 80 ? 'bg-green-100 text-green-800' :
                        rec.recommendation_score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {rec.recommendation_score >= 80 ? 'Highly Recommended' :
                         rec.recommendation_score >= 60 ? 'Recommended' : 'Consider Carefully'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Click "Get Recommendations" to see platform suggestions for your content type.</p>
          )}
        </div>
      )}
    </div>
  );
};

// Advanced Analytics Tab Component - Function 4: Content Analytics & Performance Monitoring
const AdvancedAnalyticsTab = () => {
  const [activeAnalyticsTab, setActiveAnalyticsTab] = useState('dashboard');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [contentPerformances, setContentPerformances] = useState([]);
  const [platformAnalytics, setPlatformAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [eventForm, setEventForm] = useState({
    content_id: '',
    platform: 'spotify',
    metric_type: 'views',
    value: ''
  });
  const [roiForm, setRoiForm] = useState({
    content_id: '',
    production_cost: '',
    marketing_cost: '',
    distribution_cost: '',
    platform_fees: ''
  });

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch analytics dashboard
      const dashboardResponse = await axios.get(`${API}/api/analytics/dashboard`, { headers });
      setAnalyticsData(dashboardResponse.data.dashboard);

      // Fetch content performances
      const performanceResponse = await axios.get(`${API}/api/analytics/content/performance/all`, { headers });
      setContentPerformances(performanceResponse.data.content_performances || []);

      // Fetch platform analytics
      const platformResponse = await axios.get(`${API}/api/analytics/platforms/analytics/all`, { headers });
      setPlatformAnalytics(platformResponse.data.platform_analytics || {});

    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const trackEvent = async () => {
    if (!eventForm.content_id || !eventForm.value) {
      alert('Please provide content ID and value');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/analytics/events/track`, {
        ...eventForm,
        value: parseFloat(eventForm.value)
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('Event tracked successfully!');
        setEventForm({
          content_id: '',
          platform: 'spotify',
          metric_type: 'views',
          value: ''
        });
        fetchAnalyticsData();
      }
    } catch (error) {
      console.error('Error tracking event:', error);
      alert('Failed to track event');
    }
  };

  const calculateROI = async () => {
    if (!roiForm.content_id) {
      alert('Please provide content ID');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/analytics/roi/calculate`, {
        ...roiForm,
        production_cost: parseFloat(roiForm.production_cost) || 0,
        marketing_cost: parseFloat(roiForm.marketing_cost) || 0,
        distribution_cost: parseFloat(roiForm.distribution_cost) || 0,
        platform_fees: parseFloat(roiForm.platform_fees) || 0
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('ROI calculated successfully!');
        const roi = response.data.roi_analysis;
        alert(`ROI: ${roi.roi_percentage}% | Net Profit: $${roi.net_profit} | Payback: ${roi.payback_period_days} days`);
      }
    } catch (error) {
      console.error('Error calculating ROI:', error);
      alert('Failed to calculate ROI');
    }
  };

  const analyticsTabs = [
    { id: 'dashboard', name: 'Dashboard', icon: '📊' },
    { id: 'performance', name: 'Content Performance', icon: '📈' },
    { id: 'platforms', name: 'Platform Analytics', icon: '🏢' },
    { id: 'tracking', name: 'Event Tracking', icon: '📋' },
    { id: 'roi', name: 'ROI Analysis', icon: '💰' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">📊 Content Analytics & Performance Monitoring</h3>
        <p className="text-gray-600">Track performance, analyze metrics, and optimize content strategy with comprehensive analytics</p>
      </div>

      {/* Sub-navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {analyticsTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveAnalyticsTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeAnalyticsTab === tab.id
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

      {/* Dashboard Tab */}
      {activeAnalyticsTab === 'dashboard' && (
        <div className="space-y-6">
          {analyticsData ? (
            <>
              {/* Key Metrics */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">📊 Key Metrics</h4>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{analyticsData.total_views?.toLocaleString() || 0}</div>
                    <div className="text-sm text-gray-600">Total Views</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{analyticsData.total_streams?.toLocaleString() || 0}</div>
                    <div className="text-sm text-gray-600">Total Streams</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">${analyticsData.total_revenue?.toFixed(2) || '0.00'}</div>
                    <div className="text-sm text-gray-600">Total Revenue</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-600">{analyticsData.average_engagement_rate?.toFixed(1) || '0.0'}%</div>
                    <div className="text-sm text-gray-600">Avg Engagement</div>
                  </div>
                </div>
              </div>

              {/* Top Content */}
              {analyticsData.top_performing_content && analyticsData.top_performing_content.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">🏆 Top Performing Content</h4>
                  <div className="space-y-3">
                    {analyticsData.top_performing_content.slice(0, 5).map((content, index) => (
                      <div key={content.content_id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                        <div className="flex items-center space-x-3">
                          <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                          <div>
                            <div className="font-medium">{content.content_title}</div>
                            <div className="text-sm text-gray-600">ID: {content.content_id}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-semibold">{content.total_views?.toLocaleString()} views</div>
                          <div className="text-sm text-gray-600">{content.engagement_rate?.toFixed(1)}% engagement</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Platform Breakdown */}
              {analyticsData.platform_breakdown && Object.keys(analyticsData.platform_breakdown).length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">🏢 Platform Breakdown</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(analyticsData.platform_breakdown).slice(0, 6).map(([platform, metrics]) => (
                      <div key={platform} className="p-4 border rounded-lg">
                        <h5 className="font-semibold capitalize">{platform.replace('_', ' ')}</h5>
                        <div className="mt-2 space-y-1 text-sm">
                          <div>Views: {metrics.views?.toLocaleString() || 0}</div>
                          <div>Revenue: ${metrics.revenue?.toFixed(2) || '0.00'}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white p-6 rounded-lg shadow text-center">
              <p className="text-gray-500">No analytics data available yet. Start tracking events to see performance metrics.</p>
            </div>
          )}
        </div>
      )}

      {/* Performance Tab */}
      {activeAnalyticsTab === 'performance' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">📈 Content Performance</h4>
          
          {contentPerformances.length > 0 ? (
            <div className="space-y-4">
              {contentPerformances.map((performance) => (
                <div key={performance.content_id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h5 className="font-semibold">{performance.content_title}</h5>
                      <div className="text-sm text-gray-600 mb-2">ID: {performance.content_id}</div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div><strong>Views:</strong> {performance.total_views?.toLocaleString()}</div>
                        <div><strong>Streams:</strong> {performance.total_streams?.toLocaleString()}</div>
                        <div><strong>Revenue:</strong> ${performance.total_revenue?.toFixed(2)}</div>
                        <div><strong>Engagement:</strong> {performance.engagement_rate?.toFixed(1)}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No content performance data available yet.</p>
          )}
        </div>
      )}

      {/* Platforms Tab */}
      {activeAnalyticsTab === 'platforms' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">🏢 Platform Analytics</h4>
          
          {Object.keys(platformAnalytics).length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(platformAnalytics).map(([platform, analytics]) => (
                <div key={platform} className="border rounded-lg p-4">
                  <h5 className="font-semibold text-lg mb-3">{analytics.platform_name}</h5>
                  <div className="space-y-2 text-sm">
                    <div><strong>Content Pieces:</strong> {analytics.total_content_pieces}</div>
                    <div><strong>Total Views:</strong> {analytics.total_views?.toLocaleString()}</div>
                    <div><strong>Total Revenue:</strong> ${analytics.total_revenue?.toFixed(2)}</div>
                    <div><strong>Avg Engagement:</strong> {analytics.average_engagement_rate?.toFixed(1)}%</div>
                    <div><strong>Success Rate:</strong> {analytics.content_success_rate?.toFixed(1)}%</div>
                  </div>
                  {analytics.optimization_suggestions && analytics.optimization_suggestions.length > 0 && (
                    <div className="mt-3">
                      <strong className="text-sm">Suggestions:</strong>
                      <ul className="text-xs text-gray-600 mt-1">
                        {analytics.optimization_suggestions.slice(0, 2).map((suggestion, index) => (
                          <li key={index}>• {suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No platform analytics data available yet.</p>
          )}
        </div>
      )}

      {/* Event Tracking Tab */}
      {activeAnalyticsTab === 'tracking' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">📋 Event Tracking</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content ID *</label>
              <input
                type="text"
                value={eventForm.content_id}
                onChange={(e) => setEventForm(prev => ({ ...prev, content_id: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter content ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
              <select
                value={eventForm.platform}
                onChange={(e) => setEventForm(prev => ({ ...prev, platform: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="spotify">Spotify</option>
                <option value="apple_music">Apple Music</option>
                <option value="youtube">YouTube</option>
                <option value="instagram">Instagram</option>
                <option value="tiktok">TikTok</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Metric Type</label>
              <select
                value={eventForm.metric_type}
                onChange={(e) => setEventForm(prev => ({ ...prev, metric_type: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="views">Views</option>
                <option value="streams">Streams</option>
                <option value="downloads">Downloads</option>
                <option value="likes">Likes</option>
                <option value="shares">Shares</option>
                <option value="comments">Comments</option>
                <option value="revenue">Revenue</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Value *</label>
              <input
                type="number"
                value={eventForm.value}
                onChange={(e) => setEventForm(prev => ({ ...prev, value: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter metric value"
              />
            </div>
          </div>

          <button
            onClick={trackEvent}
            className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700"
          >
            Track Event
          </button>
        </div>
      )}

      {/* ROI Tab */}
      {activeAnalyticsTab === 'roi' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">💰 ROI Analysis</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content ID *</label>
              <input
                type="text"
                value={roiForm.content_id}
                onChange={(e) => setRoiForm(prev => ({ ...prev, content_id: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter content ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Production Cost ($)</label>
              <input
                type="number"
                step="0.01"
                value={roiForm.production_cost}
                onChange={(e) => setRoiForm(prev => ({ ...prev, production_cost: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Marketing Cost ($)</label>
              <input
                type="number"
                step="0.01"
                value={roiForm.marketing_cost}
                onChange={(e) => setRoiForm(prev => ({ ...prev, marketing_cost: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Distribution Cost ($)</label>
              <input
                type="number"
                step="0.01"
                value={roiForm.distribution_cost}
                onChange={(e) => setRoiForm(prev => ({ ...prev, distribution_cost: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Platform Fees ($)</label>
              <input
                type="number"
                step="0.01"
                value={roiForm.platform_fees}
                onChange={(e) => setRoiForm(prev => ({ ...prev, platform_fees: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="0.00"
              />
            </div>
          </div>

          <button
            onClick={calculateROI}
            className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700"
          >
            Calculate ROI
          </button>
        </div>
      )}
    </div>
  );
};

// Advanced Lifecycle Tab Component - Function 5: Content Lifecycle Management & Automation
const AdvancedLifecycleTab = () => {
  const [activeLifecycleTab, setActiveLifecycleTab] = useState('overview');
  const [lifecycles, setLifecycles] = useState([]);
  const [automationRules, setAutomationRules] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [newLifecycleForm, setNewLifecycleForm] = useState({
    content_id: '',
    title: '',
    file_path: '',
    file_format: 'mp3',
    description: ''
  });
  const [newRuleForm, setNewRuleForm] = useState({
    rule_name: '',
    description: '',
    trigger_type: 'time_based',
    action_type: 'send_notification'
  });

  useEffect(() => {
    fetchLifecycleData();
  }, []);

  const fetchLifecycleData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch lifecycles
      const lifecyclesResponse = await axios.get(`${API}/api/lifecycle/`, { headers });
      setLifecycles(lifecyclesResponse.data.lifecycles || []);

      // Fetch automation rules
      const rulesResponse = await axios.get(`${API}/api/lifecycle/automation/rules`, { headers });
      setAutomationRules(rulesResponse.data.automation_rules || []);

      // Fetch dashboard data
      try {
        const dashboardResponse = await axios.get(`${API}/api/lifecycle/dashboard`, { headers });
        setDashboardData(dashboardResponse.data.dashboard);
      } catch (dashboardError) {
        console.log('Dashboard endpoint not available yet');
      }

    } catch (error) {
      console.error('Error fetching lifecycle data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createLifecycle = async () => {
    if (!newLifecycleForm.content_id || !newLifecycleForm.title || !newLifecycleForm.file_path) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/lifecycle/create`, {
        content_id: newLifecycleForm.content_id,
        initial_version: {
          title: newLifecycleForm.title,
          file_path: newLifecycleForm.file_path,
          file_format: newLifecycleForm.file_format,
          description: newLifecycleForm.description,
          file_size: 1024000, // Default 1MB
          metadata: {
            content_type: "music",
            created_date: new Date().toISOString()
          }
        }
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('Content lifecycle created successfully!');
        setNewLifecycleForm({
          content_id: '',
          title: '',
          file_path: '',
          file_format: 'mp3',
          description: ''
        });
        fetchLifecycleData();
      }
    } catch (error) {
      console.error('Error creating lifecycle:', error);
      alert('Failed to create lifecycle');
    }
  };

  const createAutomationRule = async () => {
    if (!newRuleForm.rule_name) {
      alert('Please provide a rule name');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/lifecycle/automation/rules`, {
        ...newRuleForm,
        trigger_conditions: {
          interval_days: 30
        },
        action_parameters: {
          message: "Automated action triggered"
        }
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert('Automation rule created successfully!');
        setNewRuleForm({
          rule_name: '',
          description: '',
          trigger_type: 'time_based',
          action_type: 'send_notification'
        });
        fetchLifecycleData();
      }
    } catch (error) {
      console.error('Error creating automation rule:', error);
      alert('Failed to create automation rule');
    }
  };

  const updateContentStatus = async (contentId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/lifecycle/status/update`, {
        content_id: contentId,
        new_status: newStatus,
        notes: `Status updated to ${newStatus} via UI`
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert(`Content status updated to ${newStatus}!`);
        fetchLifecycleData();
      }
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status');
    }
  };

  const lifecycleTabs = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'content', name: 'Content Lifecycles', icon: '🔄' },
    { id: 'automation', name: 'Automation Rules', icon: '⚙️' },
    { id: 'create', name: 'Create New', icon: '➕' }
  ];

  const contentStatuses = ['draft', 'pending_review', 'approved', 'published', 'live', 'paused', 'archived'];
  const triggerTypes = ['time_based', 'performance_based', 'engagement_based', 'user_action'];
  const actionTypes = ['send_notification', 'archive_content', 'promote_content', 'update_metadata'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">🔄 Content Lifecycle Management & Automation</h3>
        <p className="text-gray-600">Manage content lifecycles, automate workflows, and track version history</p>
      </div>

      {/* Sub-navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {lifecycleTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveLifecycleTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeLifecycleTab === tab.id
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

      {/* Overview Tab */}
      {activeLifecycleTab === 'overview' && (
        <div className="space-y-6">
          {dashboardData ? (
            <>
              {/* Summary Stats */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">📊 Lifecycle Overview</h4>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{dashboardData.total_content_pieces || 0}</div>
                    <div className="text-sm text-gray-600">Total Content</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{dashboardData.active_automations || 0}</div>
                    <div className="text-sm text-gray-600">Active Automations</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">{dashboardData.automation_summary?.total_executions || 0}</div>
                    <div className="text-sm text-gray-600">Total Executions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-600">{dashboardData.automation_summary?.active_rules || 0}</div>
                    <div className="text-sm text-gray-600">Active Rules</div>
                  </div>
                </div>
              </div>

              {/* Status Distribution */}
              {dashboardData.status_distribution && Object.keys(dashboardData.status_distribution).length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">📋 Status Distribution</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(dashboardData.status_distribution).map(([status, count]) => (
                      <div key={status} className="text-center p-3 bg-gray-50 rounded">
                        <div className="text-xl font-bold text-gray-700">{count}</div>
                        <div className="text-sm text-gray-600 capitalize">{status.replace('_', ' ')}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white p-6 rounded-lg shadow text-center">
              <p className="text-gray-500">No lifecycle data available yet. Create your first content lifecycle to get started.</p>
            </div>
          )}
        </div>
      )}

      {/* Content Lifecycles Tab */}
      {activeLifecycleTab === 'content' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">🔄 Content Lifecycles</h4>
          
          {lifecycles.length > 0 ? (
            <div className="space-y-4">
              {lifecycles.map((lifecycle) => (
                <div key={lifecycle.lifecycle_id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h5 className="font-semibold">Content: {lifecycle.content_id}</h5>
                      <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div><strong>Status:</strong> 
                          <span className={`ml-2 px-2 py-1 rounded text-xs ${
                            lifecycle.current_status === 'live' ? 'bg-green-100 text-green-800' :
                            lifecycle.current_status === 'published' ? 'bg-blue-100 text-blue-800' :
                            lifecycle.current_status === 'draft' ? 'bg-gray-100 text-gray-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {lifecycle.current_status}
                          </span>
                        </div>
                        <div><strong>Stage:</strong> {lifecycle.current_stage}</div>
                        <div><strong>Versions:</strong> {lifecycle.version_history?.length || 0}</div>
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        <strong>Updated:</strong> {new Date(lifecycle.updated_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="ml-4">
                      <select
                        onChange={(e) => updateContentStatus(lifecycle.content_id, e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1"
                        defaultValue=""
                      >
                        <option value="" disabled>Change Status</option>
                        {contentStatuses.map((status) => (
                          <option key={status} value={status}>
                            {status.replace('_', ' ').toUpperCase()}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No content lifecycles yet. Create your first lifecycle in the Create New tab.</p>
          )}
        </div>
      )}

      {/* Automation Rules Tab */}
      {activeLifecycleTab === 'automation' && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">⚙️ Automation Rules</h4>
          
          {automationRules.length > 0 ? (
            <div className="space-y-4">
              {automationRules.map((rule) => (
                <div key={rule.rule_id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h5 className="font-semibold">{rule.rule_name}</h5>
                      <p className="text-sm text-gray-600 mt-1">{rule.description}</p>
                      <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div><strong>Trigger:</strong> {rule.trigger_type.replace('_', ' ')}</div>
                        <div><strong>Action:</strong> {rule.action_type.replace('_', ' ')}</div>
                        <div><strong>Executions:</strong> {rule.execution_count}</div>
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        <strong>Status:</strong> 
                        <span className={`ml-2 px-2 py-1 rounded text-xs ${
                          rule.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {rule.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No automation rules yet. Create your first rule in the Create New tab.</p>
          )}
        </div>
      )}

      {/* Create New Tab */}
      {activeLifecycleTab === 'create' && (
        <div className="space-y-6">
          {/* Create Lifecycle */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">➕ Create Content Lifecycle</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Content ID *</label>
                <input
                  type="text"
                  value={newLifecycleForm.content_id}
                  onChange={(e) => setNewLifecycleForm(prev => ({ ...prev, content_id: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter unique content ID"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  value={newLifecycleForm.title}
                  onChange={(e) => setNewLifecycleForm(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter content title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">File Path *</label>
                <input
                  type="text"
                  value={newLifecycleForm.file_path}
                  onChange={(e) => setNewLifecycleForm(prev => ({ ...prev, file_path: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="/path/to/content/file"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">File Format</label>
                <select
                  value={newLifecycleForm.file_format}
                  onChange={(e) => setNewLifecycleForm(prev => ({ ...prev, file_format: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="mp3">MP3</option>
                  <option value="mp4">MP4</option>
                  <option value="wav">WAV</option>
                  <option value="flac">FLAC</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newLifecycleForm.description}
                  onChange={(e) => setNewLifecycleForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="Enter content description"
                />
              </div>
            </div>

            <button
              onClick={createLifecycle}
              className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700"
            >
              Create Lifecycle
            </button>
          </div>

          {/* Create Automation Rule */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">⚙️ Create Automation Rule</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rule Name *</label>
                <input
                  type="text"
                  value={newRuleForm.rule_name}
                  onChange={(e) => setNewRuleForm(prev => ({ ...prev, rule_name: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter rule name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Trigger Type</label>
                <select
                  value={newRuleForm.trigger_type}
                  onChange={(e) => setNewRuleForm(prev => ({ ...prev, trigger_type: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {triggerTypes.map((type) => (
                    <option key={type} value={type}>
                      {type.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
                <select
                  value={newRuleForm.action_type}
                  onChange={(e) => setNewRuleForm(prev => ({ ...prev, action_type: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {actionTypes.map((type) => (
                    <option key={type} value={type}>
                      {type.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input
                  type="text"
                  value={newRuleForm.description}
                  onChange={(e) => setNewRuleForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter rule description"
                />
              </div>
            </div>

            <button
              onClick={createAutomationRule}
              className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700"
            >
              Create Automation Rule
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentIngestionDashboard;