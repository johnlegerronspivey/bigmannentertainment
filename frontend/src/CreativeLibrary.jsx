import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Image as ImageIcon, 
  Video, 
  FileText, 
  Download, 
  Eye, 
  Edit, 
  Trash2, 
  Search, 
  Filter, 
  Grid, 
  List, 
  Plus,
  Tag,
  Calendar,
  User,
  File,
  Folder,
  CheckCircle,
  AlertCircle,
  X,
  Save,
  Loader
} from 'lucide-react';

// AWS Amplify imports
import { API, Auth, Storage } from 'aws-amplify';

const CreativeLibrary = () => {
  const [assets, setAssets] = useState([]);
  const [filteredAssets, setFilteredAssets] = useState([]);
  const [selectedAssets, setSelectedAssets] = useState([]);
  const [viewMode, setViewMode] = useState('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showTagModal, setShowTagModal] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  // Asset metadata state
  const [assetMetadata, setAssetMetadata] = useState({
    title: '',
    description: '',
    tags: [],
    category: '',
    campaign: '',
    dimensions: '',
    duration: '',
    fileSize: '',
    format: ''
  });

  // Available tags and categories
  const availableTags = [
    'Music', 'Festival', 'Concert', 'Artist', 'Album', 'Tour', 'Promotion',
    'Summer', 'Winter', 'Holiday', 'Seasonal', 'Brand', 'Logo', 'Typography',
    'Animated', 'Static', 'Interactive', 'Location', 'Weather', 'Sports',
    'Night', 'Day', 'Urban', 'Outdoor', 'Indoor', 'Transit', 'Billboard'
  ];

  const categories = [
    { id: 'images', name: 'Images', icon: ImageIcon },
    { id: 'videos', name: 'Videos', icon: Video },
    { id: 'documents', name: 'Documents', icon: FileText },
    { id: 'templates', name: 'Templates', icon: Folder }
  ];

  useEffect(() => {
    loadAssets();
  }, []);

  useEffect(() => {
    filterAssets();
  }, [assets, searchTerm, activeFilter]);

  const loadAssets = async () => {
    setLoading(true);
    try {
      // Load assets from S3 and metadata from DynamoDB
      const response = await API.get('doohapi', '/assets', {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });
      setAssets(response.assets || []);
    } catch (error) {
      console.error('Error loading assets:', error);
      // Mock data for demonstration
      setAssets([
        {
          id: 'asset_001',
          title: 'Summer Festival Hero Image',
          description: 'Main promotional image for summer music festival',
          type: 'image',
          format: 'jpg',
          fileSize: '2.5 MB',
          dimensions: '1920x1080',
          url: '/api/placeholder/image/summer-festival.jpg',
          thumbnailUrl: '/api/placeholder/thumbnail/summer-festival.jpg',
          tags: ['Music', 'Festival', 'Summer', 'Outdoor'],
          category: 'images',
          campaign: 'Summer Music Festival 2025',
          createdAt: '2025-01-15T10:00:00Z',
          createdBy: 'artist_user_001',
          usageCount: 5,
          status: 'active'
        },
        {
          id: 'asset_002',
          title: 'Artist Spotlight Video',
          description: '30-second promotional video for new artist',
          type: 'video',
          format: 'mp4',
          fileSize: '15.2 MB',
          dimensions: '1920x1080',
          duration: '30s',
          url: '/api/placeholder/video/artist-spotlight.mp4',
          thumbnailUrl: '/api/placeholder/thumbnail/artist-spotlight.jpg',
          tags: ['Artist', 'Promotion', 'Animated'],
          category: 'videos',
          campaign: 'New Artist Launch',
          createdAt: '2025-01-12T14:30:00Z',
          createdBy: 'sponsor_user_002',
          usageCount: 3,
          status: 'active'
        },
        {
          id: 'asset_003',
          title: 'Concert Tour Template',
          description: 'Customizable template for concert tour promotions',
          type: 'template',
          format: 'psd',
          fileSize: '45.8 MB',
          dimensions: '1920x1080',
          url: '/api/placeholder/template/concert-tour.psd',
          thumbnailUrl: '/api/placeholder/thumbnail/concert-tour.jpg',
          tags: ['Concert', 'Tour', 'Template', 'Typography'],
          category: 'templates',
          campaign: 'Tour Templates',
          createdAt: '2025-01-10T09:15:00Z',
          createdBy: 'admin_user_001',
          usageCount: 12,
          status: 'active'
        }
      ]);
    }
    setLoading(false);
  };

  const filterAssets = () => {
    let filtered = [...assets];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(asset =>
        asset.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Apply category filter
    if (activeFilter !== 'all') {
      filtered = filtered.filter(asset => asset.category === activeFilter);
    }

    setFilteredAssets(filtered);
  };

  const handleFileUpload = async (files) => {
    if (!files.length) return;

    setUploading(true);
    
    for (const file of files) {
      try {
        // Upload to S3
        const key = `assets/${Date.now()}_${file.name}`;
        
        const uploadTask = Storage.put(key, file, {
          contentType: file.type,
          progressCallback: (progress) => {
            setUploadProgress((progress.loaded / progress.total) * 100);
          }
        });

        const result = await uploadTask;
        
        // Create asset metadata
        const assetData = {
          title: file.name.split('.')[0],
          description: '',
          type: file.type.startsWith('image/') ? 'image' : 
                file.type.startsWith('video/') ? 'video' : 'document',
          format: file.name.split('.').pop(),
          fileSize: formatFileSize(file.size),
          s3Key: key,
          url: await Storage.get(key),
          tags: [],
          category: file.type.startsWith('image/') ? 'images' : 
                   file.type.startsWith('video/') ? 'videos' : 'documents',
          createdAt: new Date().toISOString(),
          status: 'processing'
        };

        // Save metadata to DynamoDB
        const response = await API.post('doohapi', '/assets', {
          body: assetData,
          headers: {
            Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
          }
        });

        // Add to local state
        setAssets(prev => [...prev, response.asset]);

      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }

    setUploading(false);
    setUploadProgress(0);
    setShowUploadModal(false);
  };

  const updateAssetMetadata = async (assetId, metadata) => {
    try {
      const response = await API.put('doohapi', `/assets/${assetId}`, {
        body: metadata,
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setAssets(assets.map(asset => 
        asset.id === assetId ? { ...asset, ...metadata } : asset
      ));
      
      setShowTagModal(false);
      setSelectedAsset(null);
    } catch (error) {
      console.error('Error updating asset:', error);
    }
  };

  const deleteAsset = async (assetId) => {
    if (!window.confirm('Are you sure you want to delete this asset?')) return;

    try {
      const asset = assets.find(a => a.id === assetId);
      
      // Delete from S3
      if (asset.s3Key) {
        await Storage.remove(asset.s3Key);
      }

      // Delete metadata from DynamoDB
      await API.del('doohapi', `/assets/${assetId}`, {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setAssets(assets.filter(a => a.id !== assetId));
    } catch (error) {
      console.error('Error deleting asset:', error);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type, format) => {
    if (type === 'image') return ImageIcon;
    if (type === 'video') return Video;
    return FileText;
  };

  const renderAssetCard = (asset) => {
    const FileIcon = getFileIcon(asset.type, asset.format);
    const isSelected = selectedAssets.includes(asset.id);

    return (
      <div 
        key={asset.id} 
        className={`bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow ${
          isSelected ? 'ring-2 ring-blue-500' : ''
        }`}
      >
        {/* Thumbnail */}
        <div className="relative h-48 bg-gray-100 flex items-center justify-center">
          {asset.thumbnailUrl ? (
            <img 
              src={asset.thumbnailUrl} 
              alt={asset.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <FileIcon className="w-12 h-12 text-gray-400" />
          )}
          
          {/* Selection checkbox */}
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedAssets([...selectedAssets, asset.id]);
              } else {
                setSelectedAssets(selectedAssets.filter(id => id !== asset.id));
              }
            }}
            className="absolute top-2 left-2 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />

          {/* Status indicator */}
          <div className="absolute top-2 right-2">
            {asset.status === 'processing' && (
              <div className="bg-yellow-500 text-white px-2 py-1 rounded text-xs">
                Processing
              </div>
            )}
            {asset.status === 'active' && (
              <CheckCircle className="w-5 h-5 text-green-500" />
            )}
          </div>

          {/* Overlay actions */}
          <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-30 transition-opacity flex items-center justify-center opacity-0 hover:opacity-100">
            <div className="flex space-x-2">
              <button 
                onClick={() => window.open(asset.url, '_blank')}
                className="p-2 bg-white text-gray-800 rounded-full hover:bg-gray-100"
              >
                <Eye className="w-4 h-4" />
              </button>
              <button 
                onClick={() => {
                  setSelectedAsset(asset);
                  setAssetMetadata({...asset});
                  setShowTagModal(true);
                }}
                className="p-2 bg-white text-gray-800 rounded-full hover:bg-gray-100"
              >
                <Edit className="w-4 h-4" />
              </button>
              <button 
                onClick={() => deleteAsset(asset.id)}
                className="p-2 bg-white text-gray-800 rounded-full hover:bg-gray-100"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Asset Info */}
        <div className="p-4">
          <h3 className="font-semibold text-gray-900 mb-1 truncate">{asset.title}</h3>
          <p className="text-sm text-gray-600 mb-2 line-clamp-2">{asset.description}</p>
          
          {/* Tags */}
          <div className="flex flex-wrap gap-1 mb-3">
            {asset.tags.slice(0, 3).map((tag, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
              >
                {tag}
              </span>
            ))}
            {asset.tags.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                +{asset.tags.length - 3}
              </span>
            )}
          </div>

          {/* File info */}
          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>{asset.format.toUpperCase()}</span>
            <span>{asset.fileSize}</span>
          </div>
          
          {/* Usage count */}
          <div className="mt-2 text-xs text-gray-500">
            Used in {asset.usageCount} campaigns
          </div>
        </div>
      </div>
    );
  };

  const renderListView = (asset) => {
    const FileIcon = getFileIcon(asset.type, asset.format);
    const isSelected = selectedAssets.includes(asset.id);

    return (
      <div 
        key={asset.id}
        className={`bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow ${
          isSelected ? 'ring-2 ring-blue-500' : ''
        }`}
      >
        <div className="flex items-center space-x-4">
          {/* Selection */}
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedAssets([...selectedAssets, asset.id]);
              } else {
                setSelectedAssets(selectedAssets.filter(id => id !== asset.id));
              }
            }}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
          />

          {/* Thumbnail */}
          <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
            {asset.thumbnailUrl ? (
              <img 
                src={asset.thumbnailUrl} 
                alt={asset.title}
                className="w-full h-full object-cover rounded-lg"
              />
            ) : (
              <FileIcon className="w-6 h-6 text-gray-400" />
            )}
          </div>

          {/* Asset Info */}
          <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <h3 className="font-semibold text-gray-900">{asset.title}</h3>
              <p className="text-sm text-gray-600 truncate">{asset.description}</p>
            </div>
            
            <div className="text-sm text-gray-600">
              <div>{asset.format.toUpperCase()}</div>
              <div>{asset.fileSize}</div>
              {asset.dimensions && <div>{asset.dimensions}</div>}
            </div>

            <div className="flex flex-wrap gap-1">
              {asset.tags.slice(0, 2).map((tag, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                >
                  {tag}
                </span>
              ))}
              {asset.tags.length > 2 && (
                <span className="text-xs text-gray-500">+{asset.tags.length - 2}</span>
              )}
            </div>

            <div className="text-sm text-gray-500">
              <div>Used {asset.usageCount} times</div>
              <div>{new Date(asset.createdAt).toLocaleDateString()}</div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-2 flex-shrink-0">
            <button 
              onClick={() => window.open(asset.url, '_blank')}
              className="p-2 text-gray-400 hover:text-blue-600 rounded"
            >
              <Eye className="w-4 h-4" />
            </button>
            <button 
              onClick={() => {
                setSelectedAsset(asset);
                setAssetMetadata({...asset});
                setShowTagModal(true);
              }}
              className="p-2 text-gray-400 hover:text-green-600 rounded"
            >
              <Edit className="w-4 h-4" />
            </button>
            <button 
              onClick={() => deleteAsset(asset.id)}
              className="p-2 text-gray-400 hover:text-red-600 rounded"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Creative Library</h1>
          <p className="text-gray-600 mt-1">Manage your creative assets for DOOH campaigns</p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <Upload className="w-5 h-5" />
          <span>Upload Assets</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search assets..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Category Filter */}
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              activeFilter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All ({assets.length})
          </button>
          {categories.map((category) => {
            const count = assets.filter(a => a.category === category.id).length;
            return (
              <button
                key={category.id}
                onClick={() => setActiveFilter(category.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  activeFilter === category.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.name} ({count})
              </button>
            );
          })}
        </div>

        {/* View Mode */}
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded ${
              viewMode === 'grid' ? 'bg-white text-blue-600 shadow' : 'text-gray-600'
            }`}
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded ${
              viewMode === 'list' ? 'bg-white text-blue-600 shadow' : 'text-gray-600'
            }`}
          >
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedAssets.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <span className="text-blue-800">
              {selectedAssets.length} asset{selectedAssets.length > 1 ? 's' : ''} selected
            </span>
            <div className="flex space-x-2">
              <button className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                Bulk Tag
              </button>
              <button className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700">
                Delete Selected
              </button>
              <button 
                onClick={() => setSelectedAssets([])}
                className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
              >
                Clear Selection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assets Grid/List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className={
          viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
        }>
          {filteredAssets.length > 0 ? (
            filteredAssets.map(asset => 
              viewMode === 'grid' ? renderAssetCard(asset) : renderListView(asset)
            )
          ) : (
            <div className="col-span-full text-center py-12">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No assets found</h3>
              <p className="text-gray-600 mb-4">
                {searchTerm || activeFilter !== 'all' 
                  ? 'No assets match your current filters.' 
                  : 'Upload your first creative asset to get started.'
                }
              </p>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Assets</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Upload Creative Assets</h2>
              <button 
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Upload Area */}
            <div 
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Drop files here or click to browse
              </h3>
              <p className="text-gray-600 mb-4">
                Support for images, videos, and documents up to 100MB
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,video/*,.pdf,.doc,.docx,.psd"
                onChange={(e) => handleFileUpload(Array.from(e.target.files))}
                className="hidden"
              />
            </div>

            {/* Upload Progress */}
            {uploading && (
              <div className="mt-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Uploading...</span>
                  <span className="text-sm text-gray-600">{uploadProgress.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tag/Edit Modal */}
      {showTagModal && selectedAsset && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Edit Asset</h2>
              <button 
                onClick={() => setShowTagModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={assetMetadata.title}
                  onChange={(e) => setAssetMetadata({...assetMetadata, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={assetMetadata.description}
                  onChange={(e) => setAssetMetadata({...assetMetadata, description: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {assetMetadata.tags.map((tag, index) => (
                    <span 
                      key={index}
                      className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                    >
                      {tag}
                      <button
                        onClick={() => {
                          const newTags = assetMetadata.tags.filter((_, i) => i !== index);
                          setAssetMetadata({...assetMetadata, tags: newTags});
                        }}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  {availableTags
                    .filter(tag => !assetMetadata.tags.includes(tag))
                    .map(tag => (
                      <button
                        key={tag}
                        onClick={() => {
                          if (!assetMetadata.tags.includes(tag)) {
                            setAssetMetadata({
                              ...assetMetadata, 
                              tags: [...assetMetadata.tags, tag]
                            });
                          }
                        }}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded hover:bg-gray-200"
                      >
                        + {tag}
                      </button>
                    ))
                  }
                </div>
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={assetMetadata.category}
                  onChange={(e) => setAssetMetadata({...assetMetadata, category: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-4 mt-8">
              <button 
                onClick={() => setShowTagModal(false)}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button 
                onClick={() => updateAssetMetadata(selectedAsset.id, assetMetadata)}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>Save Changes</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreativeLibrary;