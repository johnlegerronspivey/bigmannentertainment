import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DistributePage = () => {
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [userMedia, setUserMedia] = useState([]);
  const [loading, setLoading] = useState(false);
  const [distributions, setDistributions] = useState([]);
  const [loadingMedia, setLoadingMedia] = useState(true);
  const [error, setError] = useState(null);
  const [platforms, setPlatforms] = useState({});
  const [loadingPlatforms, setLoadingPlatforms] = useState(true);
  
  const location = useLocation();

  // Fetch platforms from API
  useEffect(() => {
    const fetchPlatforms = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/distribution/platforms`);
        if (response.ok) {
          const data = await response.json();
          
          const organizedPlatforms = {};
          
          if (data.platforms) {
            Object.entries(data.platforms).forEach(([platformId, platformConfig]) => {
              const category = getCategoryDisplayName(platformConfig.type);
              if (!organizedPlatforms[category]) {
                organizedPlatforms[category] = [];
              }
              organizedPlatforms[category].push({
                id: platformId,
                name: platformConfig.name,
                icon: getIconForPlatform(platformId),
                active: true,
                type: platformConfig.type,
                description: platformConfig.description,
                supported_formats: platformConfig.supported_formats,
                max_file_size: platformConfig.max_file_size
              });
            });
          }
          
          Object.keys(organizedPlatforms).forEach(category => {
            organizedPlatforms[category].sort((a, b) => a.name.localeCompare(b.name));
          });
          
          setPlatforms(organizedPlatforms);
        } else {
          setError('Failed to load platforms');
        }
      } catch (error) {
        console.error('Error fetching platforms:', error);
        setError('Error loading platforms');
      } finally {
        setLoadingPlatforms(false);
      }
    };
    
    fetchPlatforms();
  }, []);

  const getCategoryDisplayName = (type) => {
    const categoryMap = {
      'social_media': 'Social Media',
      'music_streaming': 'Music Streaming', 
      'podcast_platforms': 'Podcast Platforms',
      'radio_broadcast': 'Radio & Broadcasting',
      'television_video': 'Video Streaming',
      'rights_organizations': 'Rights Organizations',
      'web3_blockchain': 'Web3 & Blockchain',
      'international_music': 'International Music',
      'digital_platforms': 'Digital Platforms',
      'modeling_agencies': 'Model Agencies & Photography'
    };
    return categoryMap[type] || 'Other Platforms';
  };

  const getIconForPlatform = (platformId) => {
    const iconMap = {
      'instagram': '📸',
      'twitter': '🐦',
      'facebook': '👥',
      'tiktok': '🎵',
      'youtube': '📺',
      'snapchat': '👻',
      'snapchat_enhanced': '👻',
      'linkedin': '💼',
      'pinterest': '📌',
      'reddit': '🔗',
      'discord': '🎮',
      'telegram': '✈️',
      'whatsapp_business': '💬',
      'threads': '🧵',
      'tumblr': '📝',
      'theshaderoom': '🎭',
      'hollywoodunlocked': '🎬',
      'spotify': '🎶',
      'apple_music': '🍎',
      'amazon_music': '🛒',
      'livemixtapes': '🎤',
      'mymixtapez': '📻',
      'worldstarhiphop': '🌟',
      'tidal': '🌊',
      'deezer': '🎧',
      'pandora': '📻',
      'soundcloud': '☁️'
    };
    return iconMap[platformId] || '🎵';
  };

  useEffect(() => {
    loadUserMedia();
    loadDistributions();
    
    const urlParams = new URLSearchParams(location.search);
    const mediaId = urlParams.get('media');
    const mediaTitle = urlParams.get('title');
    
    if (mediaId) {
      setSelectedMedia({
        id: mediaId,
        title: decodeURIComponent(mediaTitle || 'Selected Media')
      });
    }
    // eslint-disable-next-line
  }, [location.search]);

  async function loadUserMedia() {
    setLoadingMedia(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please login.');
        setLoadingMedia(false);
        return;
      }

      let response;
      try {
        response = await axios.get(`${API}/media/library`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (firstError) {
        console.log('Library endpoint failed, trying user-media endpoint...');
        try {
          response = await axios.get(`${API}/media`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        } catch (secondError) {
          console.log('Media endpoint failed, trying list endpoint...');
          response = await axios.get(`${API}/media/list`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        }
      }

      let mediaItems = [];
      if (response.data?.media_items) {
        mediaItems = response.data.media_items;
      } else if (response.data?.media) {
        mediaItems = response.data.media;
      } else if (Array.isArray(response.data)) {
        mediaItems = response.data;
      } else if (response.data?.data) {
        mediaItems = response.data.data;
      }

      console.log('Loaded user media for distribution:', mediaItems);
      setUserMedia(mediaItems || []);
      
      const urlParams = new URLSearchParams(location.search);
      const preSelectedMediaId = urlParams.get('media');
      
      if (preSelectedMediaId && mediaItems.length > 0) {
        const preSelectedMedia = mediaItems.find(m => m.id === preSelectedMediaId);
        if (preSelectedMedia) {
          setSelectedMedia(preSelectedMedia);
        }
      }
      
    } catch (error) {
      console.error('Error loading user media:', error);
      
      if (error.response?.status === 401) {
        setError('Authentication expired. Please login again.');
      } else if (error.response?.status === 404) {
        setError('Media service not available. This may be temporary.');
      } else {
        setError(`Failed to load media: ${error.response?.data?.detail || error.message}`);
      }
    }
    setLoadingMedia(false);
  }

  const loadDistributions = async () => {
    try {
      const token = localStorage.getItem('token');
      
      let response;
      try {
        response = await axios.get(`${API}/distribution/history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (historyError) {
        console.log('History endpoint failed, trying distribution list...');
        try {
          response = await axios.get(`${API}/distribution`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        } catch (listError) {
          console.log('Distribution list failed, trying status endpoint...');
          response = await axios.get(`${API}/distribution/status`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        }
      }

      let distributionData = [];
      if (response.data?.distributions) {
        distributionData = response.data.distributions;
      } else if (Array.isArray(response.data)) {
        distributionData = response.data;
      } else if (response.data?.data) {
        distributionData = response.data.data;
      }

      console.log('Loaded distribution history:', distributionData);
      setDistributions(distributionData || []);
    } catch (error) {
      console.error('Error loading distributions:', error);
      
      if (error.response?.status === 401) {
        console.log('Authentication required for distribution history');
      }
    }
  };

  const handlePlatformToggle = (platformId) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const startDistribution = async () => {
    if (!selectedMedia || selectedPlatforms.length === 0) {
      alert('Please select media and at least one platform');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      const loadingMessage = `Starting distribution of "${selectedMedia.title}" to ${selectedPlatforms.length} platforms...`;
      console.log(loadingMessage);

      const response = await axios.post(`${API}/distribution/distribute`, {
        media_id: selectedMedia.id,
        platforms: selectedPlatforms,
        custom_message: `Distributing ${selectedMedia.title} to ${selectedPlatforms.length} platforms`,
        hashtags: []
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.data) {
        const distributionResult = response.data;
        
        let successMessage = `🎉 Distribution Successful!\n\n`;
        successMessage += `Content: "${selectedMedia.title}"\n`;
        successMessage += `Distribution ID: ${distributionResult.distribution_id}\n`;
        successMessage += `Platforms: ${selectedPlatforms.length} selected\n`;
        successMessage += `Status: ${distributionResult.status}\n\n`;
        
        if (distributionResult.results) {
          successMessage += `Platform Results:\n`;
          Object.entries(distributionResult.results).forEach(([platform, result]) => {
            const statusIcon = result.status === 'success' ? '✅' : '❌';
            successMessage += `${statusIcon} ${platform}: ${result.status}\n`;
            if (result.post_id || result.track_id || result.video_id) {
              successMessage += `   ID: ${result.post_id || result.track_id || result.video_id}\n`;
            }
          });
        }
        
        successMessage += `\nYou can track the delivery status in your Distribution History.`;
        
        alert(successMessage);
        
        loadDistributions();
        setSelectedPlatforms([]);
        
        console.log('Distribution Details:', distributionResult);
      }
    } catch (error) {
      console.error('Distribution error:', error);
      let errorMessage = `❌ Distribution Failed for "${selectedMedia.title}"\n\n`;
      
      if (error.response?.data?.detail) {
        errorMessage += `Error: ${error.response.data.detail}\n`;
      } else if (error.response?.status === 401) {
        errorMessage += 'Error: Authentication required. Please login again.\n';
      } else if (error.response?.status === 403) {
        errorMessage += 'Error: You do not have permission to distribute this content.\n';
      } else if (error.response?.status === 404) {
        errorMessage += 'Error: Content not found. Please refresh and try again.\n';
      } else if (error.message) {
        errorMessage += `Error: ${error.message}\n`;
      }
      
      errorMessage += '\nPlease check your content and platform selections, then try again.';
      alert(errorMessage);
    }
    setLoading(false);
  };

  const totalPlatforms = Object.values(platforms).reduce((sum, category) => sum + category.length, 0);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Distribute Content</h1>
        <p className="text-gray-600">Distribute your content across {totalPlatforms}+ platforms with a single click</p>
      </div>

      {/* Distribution Status Overview */}
      {distributions.length > 0 && (
        <div className="mb-6 bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-800">Distribution Overview</h3>
              <p className="text-sm text-gray-600">
                {distributions.length} distributions • {
                  distributions.filter(d => d.status === 'completed').length
                } completed • {
                  distributions.filter(d => d.status === 'processing').length
                } processing
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {distributions.filter(d => d.status === 'processing').length > 0 && (
                <div className="flex items-center text-yellow-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600 mr-2"></div>
                  <span className="text-sm">Processing...</span>
                </div>
              )}
              <button
                onClick={loadDistributions}
                className="text-purple-600 hover:text-purple-800 text-sm font-medium"
              >
                Refresh Status
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-red-600 mr-3">⚠️</div>
            <div>
              <h3 className="text-red-800 font-medium">Error Loading Content</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
              <button 
                onClick={loadUserMedia}
                className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Media Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Select Content</h3>
              <button
                onClick={loadUserMedia}
                className="text-purple-600 hover:text-purple-800 text-sm"
              >
                Refresh
              </button>
            </div>
            
            {loadingMedia ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                <p className="mt-2 text-gray-500 text-sm">Loading your content...</p>
              </div>
            ) : userMedia.length > 0 ? (
              <div className="space-y-3">
                {userMedia.map((media) => (
                  <div
                    key={media.id}
                    onClick={() => setSelectedMedia(media)}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedMedia?.id === media.id ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded flex items-center justify-center ${
                        media.content_type === 'audio' ? 'bg-blue-100 text-blue-600' :
                        media.content_type === 'video' ? 'bg-green-100 text-green-600' :
                        'bg-yellow-100 text-yellow-600'
                      }`}>
                        {media.content_type === 'audio' ? '🎵' :
                         media.content_type === 'video' ? '🎥' : '🖼️'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{media.title}</p>
                        <p className="text-sm text-gray-500">{media.content_type}</p>
                      </div>
                      {selectedMedia?.id === media.id && (
                        <div className="text-purple-600">
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <div className="text-gray-400 mb-3">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m4 0H3a1 1 0 00-1 1v13a1 1 0 001 1h18a1 1 0 001-1V5a1 1 0 00-1-1z" />
                  </svg>
                </div>
                <p className="mb-2">No content available for distribution</p>
                <Link to="/upload" className="text-purple-600 hover:text-purple-800">
                  Upload your first file
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Platform Selection */}
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Select Platforms ({selectedPlatforms.length} selected)</h3>
              <div className="space-x-2">
                <button
                  onClick={() => setSelectedPlatforms([])}
                  className="text-gray-600 hover:text-gray-800 px-3 py-1 text-sm"
                >
                  Clear All
                </button>
                <button
                  onClick={() => {
                    const allIds = Object.values(platforms).flat().map(p => p.id);
                    setSelectedPlatforms(allIds);
                  }}
                  className="text-purple-600 hover:text-purple-800 px-3 py-1 text-sm"
                  disabled={loadingPlatforms}
                >
                  Select All
                </button>
              </div>
            </div>

            {loadingPlatforms ? (
              <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                <span className="ml-3 text-gray-600">Loading platforms...</span>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <p className="text-red-600 mb-4">{error}</p>
                <button 
                  onClick={() => window.location.reload()} 
                  className="text-purple-600 hover:underline"
                >
                  Retry
                </button>
              </div>
            ) : Object.keys(platforms).length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No platforms available</p>
              </div>
            ) : (
              Object.entries(platforms).map(([category, platformList]) => (
                <div key={category} className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">
                    {category} ({platformList.length})
                  </h4>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {platformList.map((platform) => (
                      <div
                        key={platform.id}
                        onClick={() => handlePlatformToggle(platform.id)}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedPlatforms.includes(platform.id) 
                            ? 'border-purple-500 bg-purple-50' 
                            : 'border-gray-200 hover:border-purple-300'
                        }`}
                      >
                        <div className="flex items-center">
                          <div className="text-2xl mr-3">{platform.icon}</div>
                          <div className="flex-1">
                            <h5 className="text-sm font-medium">{platform.name}</h5>
                            {platform.description && (
                              <p className="text-xs text-gray-500 mt-1">{platform.description}</p>
                            )}
                            <p className={`text-xs ${platform.active ? 'text-green-600' : 'text-orange-600'} mt-1`}>
                              {platform.active ? 'Active' : 'Coming Soon'}
                            </p>
                          </div>
                          {selectedPlatforms.includes(platform.id) && (
                            <div className="ml-auto text-purple-600">
                              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}

            <div className="mt-6 pt-6 border-t">
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-600">
                  {selectedMedia ? `Selected: ${selectedMedia.title}` : 'No content selected'} • {selectedPlatforms.length} of {Object.values(platforms).reduce((sum, platformList) => sum + platformList.length, 0)} platforms selected
                </div>
                <button
                  onClick={startDistribution}
                  disabled={!selectedMedia || selectedPlatforms.length === 0 || loading}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Distributing...' : `Distribute to ${selectedPlatforms.length} Platforms`}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Distributions */}
      {distributions.length > 0 && (
        <div className="mt-8 bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Distribution History & Delivery Status</h3>
            <button
              onClick={loadDistributions}
              className="text-purple-600 hover:text-purple-800 text-sm"
            >
              Refresh Status
            </button>
          </div>
          <div className="space-y-4">
            {distributions.slice(0, 10).map((dist, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <p className="font-medium text-lg">{dist.media_title || 'Content'}</p>
                    <p className="text-sm text-gray-500 mb-1">
                      Distribution ID: {dist.id || `dist_${index + 1}`}
                    </p>
                    <p className="text-sm text-gray-600">
                      {dist.target_platforms?.length || 0} platforms • Created: {
                        dist.created_at ? new Date(dist.created_at).toLocaleString() : 'Unknown'
                      }
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    dist.status === 'completed' ? 'bg-green-100 text-green-800' :
                    dist.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    dist.status === 'partial' ? 'bg-orange-100 text-orange-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {dist.status === 'completed' ? '✅ Delivered' :
                     dist.status === 'processing' ? '⏳ Processing' :
                     dist.status === 'partial' ? '⚠️ Partial' :
                     '❌ Failed'}
                  </span>
                </div>

                {/* Platform Results */}
                {dist.results && Object.keys(dist.results).length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">Platform Delivery Results:</p>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-2">
                      {Object.entries(dist.results).map(([platform, result]) => (
                        <div
                          key={platform}
                          className={`p-2 rounded text-xs flex items-center justify-between ${
                            result.status === 'success' 
                              ? 'bg-green-50 text-green-800 border border-green-200' 
                              : 'bg-red-50 text-red-800 border border-red-200'
                          }`}
                        >
                          <span className="font-medium">
                            {result.status === 'success' ? '✅' : '❌'} {platform}
                          </span>
                          {(result.post_id || result.track_id || result.video_id || result.listing_id) && (
                            <span className="text-xs opacity-75">
                              {(result.post_id || result.track_id || result.video_id || result.listing_id).substring(0, 8)}...
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Selected Platforms List */}
                {dist.target_platforms && dist.target_platforms.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-1">Target Platforms:</p>
                    <div className="flex flex-wrap gap-1">
                      {dist.target_platforms.map((platform, pidx) => (
                        <span
                          key={pidx}
                          className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded"
                        >
                          {platform}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="mt-3 flex gap-2">
                  {dist.status === 'processing' && (
                    <button
                      onClick={loadDistributions}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Check Status
                    </button>
                  )}
                  {dist.status === 'completed' && (
                    <span className="text-green-600 text-sm">
                      ✅ Successfully delivered to all platforms
                    </span>
                  )}
                  {dist.status === 'partial' && (
                    <span className="text-orange-600 text-sm">
                      ⚠️ Delivered to some platforms, check results above
                    </span>
                  )}
                  {dist.status === 'failed' && (
                    <button
                      onClick={() => {
                        setSelectedMedia({ id: dist.media_id, title: dist.media_title || 'Content' });
                        setSelectedPlatforms(dist.target_platforms || []);
                      }}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Retry Distribution
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {distributions.length > 10 && (
            <div className="mt-4 text-center">
              <button
                onClick={() => {
                  alert('Pagination feature coming soon! Currently showing last 10 distributions.');
                }}
                className="text-purple-600 hover:text-purple-800 text-sm"
              >
                View All Distributions ({distributions.length} total)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DistributePage;
