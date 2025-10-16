import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const SocialMediaDashboardEnhanced = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [connections, setConnections] = useState([]);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [newPost, setNewPost] = useState({
    provider: 'twitter',
    content: '',
    mediaUrls: []
  });
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    fetchConnections();
    fetchPosts();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/social/metrics/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError('Failed to load dashboard data. Using mock data.');
      // Fallback to mock data
      setDashboardData({
        platforms: [],
        total_followers: 0,
        total_posts: 0,
        avg_engagement: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchConnections = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/social/connections`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConnections(response.data.connections || []);
    } catch (err) {
      console.error('Failed to load connections:', err);
      setConnections([]);
    }
  };

  const fetchPosts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/social/posts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPosts(response.data.posts || []);
    } catch (err) {
      console.error('Failed to load posts:', err);
      setPosts([]);
    }
  };

  const handleConnectPlatform = (provider) => {
    const token = localStorage.getItem('token');
    // Open OAuth flow in new window
    window.location.href = `${BACKEND_URL}/api/social/connect/${provider}`;
  };

  const handleDisconnect = async (provider) => {
    if (!window.confirm(`Disconnect ${provider}? You'll need to reconnect to post again.`)) {
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/social/disconnect/${provider}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(`${provider} disconnected successfully`);
      fetchConnections();
      fetchDashboardData();
    } catch (err) {
      alert('Failed to disconnect: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handlePost = async (e) => {
    e.preventDefault();
    setPosting(true);
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/social/post`,
        {
          provider: newPost.provider,
          content: newPost.content,
          media_urls: newPost.mediaUrls
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      alert('Posted successfully! 🎉');
      setNewPost({ provider: 'twitter', content: '', mediaUrls: [] });
      fetchPosts();
      setActiveTab('posts');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message;
      alert('Failed to post: ' + errorMsg);
      console.error('Post error:', err);
    } finally {
      setPosting(false);
    }
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      twitter: '🐦',
      facebook: '📘',
      instagram: '📷',
      tiktok: '🎵',
      linkedin: '💼',
      youtube: '▶️'
    };
    return icons[platform] || '🌐';
  };

  const isConnected = (provider) => {
    return connections.some(conn => conn.provider === provider);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>Loading social media dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">📱 Social Media Dashboard</h1>
          <p className="text-gray-400">Manage your social media presence with real-time data</p>
          {error && (
            <div className="mt-2 bg-yellow-500/20 border border-yellow-500 text-yellow-200 px-4 py-2 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="bg-gray-800 rounded-xl shadow-xl mb-6">
          <div className="flex border-b border-gray-700 overflow-x-auto">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'connections', label: 'Connections', icon: '🔗' },
              { id: 'post', label: 'Create Post', icon: '✍️' },
              { id: 'posts', label: 'My Posts', icon: '📝' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-semibold text-sm transition-colors flex items-center gap-2 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'text-purple-400 border-b-2 border-purple-500 bg-gray-900/50'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && dashboardData && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Followers</div>
                <div className="text-4xl font-bold">{dashboardData.total_followers?.toLocaleString() || 0}</div>
              </div>
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Posts</div>
                <div className="text-4xl font-bold">{dashboardData.total_posts || 0}</div>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Avg Engagement</div>
                <div className="text-4xl font-bold">{dashboardData.avg_engagement?.toFixed(1) || 0}%</div>
              </div>
            </div>

            {/* Platform Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {dashboardData.platforms && dashboardData.platforms.length > 0 ? (
                dashboardData.platforms.map((platform) => (
                  <div key={platform.platform} className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <span className="text-4xl">{getPlatformIcon(platform.platform)}</span>
                        <div>
                          <h3 className="text-xl font-bold text-white capitalize">{platform.platform}</h3>
                          {platform.username && (
                            <p className="text-sm text-gray-400">@{platform.username}</p>
                          )}
                        </div>
                      </div>
                      <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                        Connected
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">
                          {platform.followers?.toLocaleString() || 0}
                        </div>
                        <div className="text-xs text-gray-400">Followers</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">{platform.posts || 0}</div>
                        <div className="text-xs text-gray-400">Posts</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">
                          {platform.engagement_rate?.toFixed(1) || 0}%
                        </div>
                        <div className="text-xs text-gray-400">Engagement</div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-2 bg-gray-800 rounded-xl p-12 text-center border border-gray-700">
                  <div className="text-6xl mb-4">🔗</div>
                  <h3 className="text-xl font-bold text-white mb-2">No Platforms Connected</h3>
                  <p className="text-gray-400 mb-4">Connect your social media accounts to see analytics</p>
                  <button
                    onClick={() => setActiveTab('connections')}
                    className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
                  >
                    Connect Platforms
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Connections Tab */}
        {activeTab === 'connections' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-xl p-6">
              <h3 className="text-2xl font-bold text-white mb-6">🔗 Connect Social Media Platforms</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {['twitter', 'facebook', 'instagram', 'tiktok', 'linkedin', 'youtube'].map((platform) => {
                  const connected = isConnected(platform);
                  const connection = connections.find(c => c.provider === platform);
                  
                  return (
                    <div key={platform} className="bg-gray-900 rounded-lg p-6 border border-gray-700">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">{getPlatformIcon(platform)}</span>
                          <div>
                            <h4 className="text-lg font-bold text-white capitalize">{platform}</h4>
                            {connected && connection && (
                              <p className="text-sm text-gray-400">@{connection.username}</p>
                            )}
                          </div>
                        </div>
                        {connected ? (
                          <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs">
                            Connected
                          </span>
                        ) : (
                          <span className="px-3 py-1 bg-gray-500/20 text-gray-400 rounded-full text-xs">
                            Not Connected
                          </span>
                        )}
                      </div>
                      
                      {connected ? (
                        <button
                          onClick={() => handleDisconnect(platform)}
                          className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                        >
                          Disconnect
                        </button>
                      ) : (
                        <button
                          onClick={() => handleConnectPlatform(platform)}
                          className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                        >
                          Connect {(platform === 'twitter' || platform === 'tiktok') ? '(Available)' : '(Coming Soon)'}
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Create Post Tab */}
        {activeTab === 'post' && (
          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-2xl font-bold text-white mb-6">✍️ Create New Post</h3>
            
            {connections.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🔗</div>
                <h4 className="text-xl font-bold text-white mb-2">No Platforms Connected</h4>
                <p className="text-gray-400 mb-4">Connect a platform first to start posting</p>
                <button
                  onClick={() => setActiveTab('connections')}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
                >
                  Connect Platform
                </button>
              </div>
            ) : (
              <form onSubmit={handlePost} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Select Platform</label>
                  <select
                    value={newPost.provider}
                    onChange={(e) => setNewPost({ ...newPost, provider: e.target.value })}
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                    required
                  >
                    {connections.map((conn) => (
                      <option key={conn.provider} value={conn.provider}>
                        {getPlatformIcon(conn.provider)} {conn.provider.toUpperCase()} - @{conn.username}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Post Content</label>
                  <textarea
                    value={newPost.content}
                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                    rows="6"
                    placeholder="What's on your mind?"
                    required
                    maxLength={280}
                  />
                  <div className="text-right text-sm text-gray-400 mt-1">
                    {newPost.content.length} / 280 characters
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={posting || !newPost.content}
                  className={`w-full px-6 py-3 rounded-lg transition-colors font-semibold ${
                    posting || !newPost.content
                      ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                      : 'bg-purple-600 hover:bg-purple-700 text-white'
                  }`}
                >
                  {posting ? 'Posting...' : `Post to ${newPost.provider.toUpperCase()}`}
                </button>
              </form>
            )}
          </div>
        )}

        {/* Posts Tab */}
        {activeTab === 'posts' && (
          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-2xl font-bold text-white mb-6">📝 My Posts</h3>
            {posts.length > 0 ? (
              <div className="space-y-4">
                {posts.map((post) => (
                  <div key={post.id} className="bg-gray-900 rounded-lg p-6 border border-gray-700">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {post.platforms?.map(platform => (
                          <span key={platform} className="text-2xl">{getPlatformIcon(platform)}</span>
                        ))}
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs ${
                        post.status === 'posted' 
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {post.status}
                      </span>
                    </div>
                    <p className="text-white mb-3">{post.content}</p>
                    <div className="text-sm text-gray-400">
                      Posted: {post.posted_at ? new Date(post.posted_at).toLocaleString() : 'Pending'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <div className="text-6xl mb-4">📝</div>
                <p>No posts yet. Create your first post!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialMediaDashboardEnhanced;
