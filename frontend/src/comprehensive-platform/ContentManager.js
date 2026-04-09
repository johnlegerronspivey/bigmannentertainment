import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';
import { GS1AssetRegistry } from '../GS1AssetRegistryComponents';

const ContentManager = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [assets, setAssets] = useState([]);
  const [folders, setFolders] = useState([]);
  const [selectedAssets, setSelectedAssets] = useState([]);
  const [contentStats, setContentStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('assets');

  useEffect(() => {
    fetchContentData();
  }, []);

  const fetchContentData = async () => {
    setLoading(true);
    try {
      const [assetsRes, foldersRes, statsRes] = await Promise.all([
        axios.get(`${API}/api/platform/content/assets?user_id=user_123`),
        axios.get(`${API}/api/platform/content/folders?user_id=user_123`),
        axios.get(`${API}/api/platform/content/stats?user_id=user_123`)
      ]);

      if (assetsRes.data.success) setAssets(assetsRes.data.assets || []);
      if (foldersRes.data.success) setFolders(foldersRes.data.folders || []);
      if (statsRes.data.success) setContentStats(statsRes.data.stats || {});
    } catch (error) {
      handleApiError(error, 'fetchContentData');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'assets', name: 'Assets', icon: '📁' },
    { id: 'folders', name: 'Folders', icon: '📂' },
    { id: 'gs1', name: 'GS1 Registry', icon: '🏷️' },
    { id: 'upload', name: 'Upload', icon: '⬆️' },
    { id: 'analytics', name: 'Analytics', icon: '📊' }
  ];

  return (
    <div data-testid="content-manager" className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Content Manager</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Organize and manage all your content assets</p>
        </div>
        <button data-testid="add-content-btn" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
          <span>➕</span>
          <span>Add Content</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Assets</p>
              <p data-testid="content-total-assets" className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.total_assets || '0'}</p>
            </div>
            <span className="text-2xl">📁</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.total_size || '0 B'}</p>
            </div>
            <span className="text-2xl">💾</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">This Month</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.this_month?.uploaded || '0'}</p>
            </div>
            <span className="text-2xl">📈</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Live Assets</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.by_status?.live || '0'}</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              data-testid={`content-tab-${tab.id}`}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'assets' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search assets..."
                  data-testid="content-search-input"
                  className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                />
              </div>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Types</option>
                <option>Audio</option>
                <option>Video</option>
                <option>Image</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Status</option>
                <option>Live</option>
                <option>Draft</option>
                <option>Pending Review</option>
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {assets.length > 0 ? assets.map((asset, index) => (
                <div key={asset.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4 hover:shadow-md transition-shadow`}>
                  <div className="aspect-w-16 aspect-h-9 mb-3">
                    <div className={`${isDarkMode ? 'bg-gray-700' : 'bg-gray-100'} rounded-lg flex items-center justify-center`}>
                      <span className="text-2xl">
                        {asset.content_type === 'audio' ? '🎵' : asset.content_type === 'video' ? '🎬' : '🖼️'}
                      </span>
                    </div>
                  </div>
                  <h3 className="font-medium text-gray-900 dark:text-white truncate">{asset.title || 'Untitled'}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{asset.content_type || 'Unknown'}</p>
                  <div className="flex justify-between items-center mt-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      asset.status === 'live' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                      asset.status === 'draft' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                    }`}>
                      {asset.status || 'unknown'}
                    </span>
                    <div className="flex space-x-1">
                      <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">✏️</button>
                      <button className="text-gray-400 hover:text-red-600">🗑️</button>
                    </div>
                  </div>
                </div>
              )) : (
                <div className="col-span-full text-center py-8">
                  <div className="text-4xl mb-4">📁</div>
                  <p className="text-gray-600 dark:text-gray-400">No assets found. Upload your first content to get started!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'folders' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {folders.length > 0 ? folders.map((folder, index) => (
                <div key={folder.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer`}>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{backgroundColor: folder.color || '#3B82F6'}}>
                      <span className="text-white text-lg">📂</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 dark:text-white">{folder.name}</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{folder.description || 'No description'}</p>
                    </div>
                  </div>
                </div>
              )) : (
                <div className="col-span-full text-center py-8">
                  <div className="text-4xl mb-4">📂</div>
                  <p className="text-gray-600 dark:text-gray-400">No folders created yet. Organize your content with folders!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'gs1' && (
          <GS1AssetRegistry />
        )}

        {activeTab === 'upload' && (
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-8`}>
            <div className="text-center">
              <div className="text-6xl mb-4">⬆️</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Upload Content</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">Drag and drop files here or click to browse</p>
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                Choose Files
              </button>
              <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
                Supported formats: MP3, WAV, MP4, MOV, JPG, PNG • Max size: 100MB
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Content by Type</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Audio</span>
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.audio || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Video</span>
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.video || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Image</span>
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.image || '0'}</span>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Content by Status</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Live</span>
                  <span className="font-medium text-green-600">{contentStats.by_status?.live || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Pending Review</span>
                  <span className="font-medium text-yellow-600">{contentStats.by_status?.pending_review || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Draft</span>
                  <span className="font-medium text-gray-600">{contentStats.by_status?.draft || '0'}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { ContentManager };
