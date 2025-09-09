import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://bme-media-hub-1.preview.emergentagent.com';

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
    { id: 'content', name: 'Content Library', icon: '📚' },
    { id: 'compliance', name: 'Compliance', icon: '✅' },
    { id: 'ddex', name: 'DDEX Management', icon: '🔄' },
    { id: 'analytics', name: 'Analytics', icon: '📊' }
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
        {activeTab === 'content' && <ContentLibraryTab dashboardData={dashboardData} />}
        {activeTab === 'compliance' && <ComplianceTab />}
        {activeTab === 'ddex' && <DDEXManagementTab />}
        {activeTab === 'analytics' && <AnalyticsTab dashboardData={dashboardData} />}
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

export default ContentIngestionDashboard;