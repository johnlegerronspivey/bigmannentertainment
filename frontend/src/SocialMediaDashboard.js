import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const SocialMediaDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [scheduledPosts, setScheduledPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [newPost, setNewPost] = useState({
    content: '',
    platforms: [],
    scheduledFor: '',
    mediaUrl: ''
  });

  useEffect(() => {
    fetchDashboardData();
    fetchScheduledPosts();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/profile/social/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(response.data);
    } catch (err) {
      console.error('Failed to load social dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchScheduledPosts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/profile/social/posts/scheduled`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setScheduledPosts(response.data.scheduled_posts);
    } catch (err) {
      console.error('Failed to load scheduled posts:', err);
    }
  };

  const handleSchedulePost = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/profile/social/posts/schedule`,
        {
          content: newPost.content,
          platforms: newPost.platforms,
          scheduled_for: newPost.scheduledFor,
          media_url: newPost.mediaUrl || null
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      alert('Post scheduled successfully!');
      setNewPost({ content: '', platforms: [], scheduledFor: '', mediaUrl: '' });
      fetchScheduledPosts();
      setActiveTab('scheduled');
    } catch (err) {
      alert('Failed to schedule post: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCancelPost = async (postId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `${BACKEND_URL}/api/profile/social/posts/scheduled/${postId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      alert('Post cancelled successfully!');
      fetchScheduledPosts();
    } catch (err) {
      alert('Failed to cancel post');
    }
  };

  const togglePlatform = (platform) => {
    setNewPost(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter(p => p !== platform)
        : [...prev.platforms, platform]
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-white">Loading social media dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Social Media Dashboard</h1>
          <p className="text-gray-400">Manage your social media presence across all platforms</p>
        </div>

        {/* Tabs */}
        <div className="bg-gray-800 rounded-xl shadow-xl mb-6">
          <div className="flex border-b border-gray-700">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'analytics', label: 'Analytics', icon: '📈' },
              { id: 'schedule', label: 'Schedule Post', icon: '📅' },
              { id: 'scheduled', label: 'Scheduled Posts', icon: '🗓️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-semibold text-sm transition-colors flex items-center gap-2 ${
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

        {/* Tab Content */}
        {activeTab === 'overview' && dashboardData && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Followers</div>
                <div className="text-4xl font-bold">{dashboardData.total_followers.toLocaleString()}</div>
              </div>
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Total Posts</div>
                <div className="text-4xl font-bold">{dashboardData.total_posts}</div>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-6 text-white">
                <div className="text-sm opacity-90 mb-2">Avg Engagement</div>
                <div className="text-4xl font-bold">{dashboardData.avg_engagement.toFixed(1)}%</div>
              </div>
            </div>

            {/* Platform Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {dashboardData.platforms.map((platform) => (
                <div key={platform.platform} className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-4xl">{platform.icon}</span>
                      <div>
                        <h3 className="text-xl font-bold text-white">{platform.name}</h3>
                        {platform.username && (
                          <p className="text-sm text-gray-400">{platform.username}</p>
                        )}
                      </div>
                    </div>
                    {platform.connected ? (
                      <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                        Connected
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-gray-500/20 text-gray-400 rounded-full text-sm">
                        Not Connected
                      </span>
                    )}
                  </div>

                  {platform.connected && (
                    <>
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-400">
                            {platform.followers.toLocaleString()}
                          </div>
                          <div className="text-xs text-gray-400">Followers</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-400">{platform.posts}</div>
                          <div className="text-xs text-gray-400">Posts</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-400">
                            {platform.engagement_rate}%
                          </div>
                          <div className="text-xs text-gray-400">Engagement</div>
                        </div>
                      </div>

                      {platform.recent_stats && Object.keys(platform.recent_stats).length > 0 && (
                        <div className="bg-gray-900 rounded-lg p-4">
                          <div className="text-sm font-semibold text-gray-300 mb-2">Recent Stats</div>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            {Object.entries(platform.recent_stats).map(([key, value]) => (
                              <div key={key} className="text-gray-400">
                                {key}: <span className="text-white font-semibold">{value.toLocaleString()}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-2xl font-bold text-white mb-6">Platform Analytics</h3>
            <div className="space-y-6">
              <div className="bg-gray-900 rounded-lg p-6">
                <h4 className="text-lg font-semibold text-purple-400 mb-4">Engagement Trends</h4>
                <div className="h-64 flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <div className="text-6xl mb-4">📈</div>
                    <p>Analytics visualization coming soon</p>
                    <p className="text-sm mt-2">Track your growth across all platforms</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'schedule' && (
          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-2xl font-bold text-white mb-6">Schedule New Post</h3>
            <form onSubmit={handleSchedulePost} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Post Content</label>
                <textarea
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                  rows="4"
                  placeholder="What's on your mind?"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Select Platforms</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['facebook', 'tiktok', 'youtube', 'twitter'].map((platform) => (
                    <button
                      key={platform}
                      type="button"
                      onClick={() => togglePlatform(platform)}
                      className={`px-4 py-3 rounded-lg font-semibold transition-colors ${
                        newPost.platforms.includes(platform)
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {platform.charAt(0).toUpperCase() + platform.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Schedule For</label>
                <input
                  type="datetime-local"
                  value={newPost.scheduledFor}
                  onChange={(e) => setNewPost({ ...newPost, scheduledFor: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Media URL (Optional)</label>
                <input
                  type="url"
                  value={newPost.mediaUrl}
                  onChange={(e) => setNewPost({ ...newPost, mediaUrl: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
                  placeholder="https://..."
                />
              </div>

              <button
                type="submit"
                className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors"
              >
                Schedule Post
              </button>
            </form>
          </div>
        )}

        {activeTab === 'scheduled' && (
          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-2xl font-bold text-white mb-6">Scheduled Posts</h3>
            {scheduledPosts.length > 0 ? (
              <div className="space-y-4">
                {scheduledPosts.map((post) => (
                  <div key={post.id} className="bg-gray-900 rounded-lg p-6 border border-gray-700">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <p className="text-white mb-2">{post.content}</p>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span>📅 {new Date(post.scheduled_for).toLocaleString()}</span>
                          <span className="flex items-center gap-2">
                            Platforms: {post.platforms.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(', ')}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleCancelPost(post.id)}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                    {post.media_url && (
                      <div className="mt-3">
                        <img src={post.media_url} alt="Post media" className="rounded-lg max-h-48" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                No scheduled posts
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialMediaDashboard;