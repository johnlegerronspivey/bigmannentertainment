import React, { useState, useEffect } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// ============== AI-Powered Release Optimization Component ==============

export const AIReleaseOptimization = ({ token }) => {
  const [releaseData, setReleaseData] = useState({
    release_id: '',
    artist_name: '',
    track_title: '',
    genre: '',
    target_audience: '',
    budget: ''
  });
  const [optimization, setOptimization] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeRelease = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/enhanced/ai-optimization/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...releaseData,
          budget: releaseData.budget ? parseFloat(releaseData.budget) : null
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze release');
      }

      const data = await response.json();
      setOptimization(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <span className="mr-2">🤖</span> AI-Powered Release Optimization
      </h2>
      <p className="text-gray-600 mb-6">Get AI-generated platform recommendations and release strategy using GPT-5</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <input
          type="text"
          placeholder="Release ID"
          className="border rounded-lg p-2"
          value={releaseData.release_id}
          onChange={(e) => setReleaseData({...releaseData, release_id: e.target.value})}
        />
        <input
          type="text"
          placeholder="Artist Name"
          className="border rounded-lg p-2"
          value={releaseData.artist_name}
          onChange={(e) => setReleaseData({...releaseData, artist_name: e.target.value})}
        />
        <input
          type="text"
          placeholder="Track Title"
          className="border rounded-lg p-2"
          value={releaseData.track_title}
          onChange={(e) => setReleaseData({...releaseData, track_title: e.target.value})}
        />
        <input
          type="text"
          placeholder="Genre (e.g., Hip-Hop)"
          className="border rounded-lg p-2"
          value={releaseData.genre}
          onChange={(e) => setReleaseData({...releaseData, genre: e.target.value})}
        />
        <input
          type="text"
          placeholder="Target Audience (Optional)"
          className="border rounded-lg p-2"
          value={releaseData.target_audience}
          onChange={(e) => setReleaseData({...releaseData, target_audience: e.target.value})}
        />
        <input
          type="number"
          placeholder="Budget (Optional)"
          className="border rounded-lg p-2"
          value={releaseData.budget}
          onChange={(e) => setReleaseData({...releaseData, budget: e.target.value})}
        />
      </div>

      <button
        onClick={analyzeRelease}
        disabled={loading || !releaseData.release_id || !releaseData.artist_name || !releaseData.track_title}
        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Analyzing with AI...' : 'Analyze Release'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {optimization && (
        <div className="mt-6">
          <div className="bg-gradient-to-r from-purple-100 to-blue-100 p-6 rounded-lg mb-4">
            <h3 className="text-xl font-bold mb-2">AI Insights</h3>
            <p className="text-gray-700">{optimization.ai_insights}</p>
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-lg">
                <p className="text-sm text-gray-600">Estimated Reach</p>
                <p className="text-2xl font-bold text-blue-600">{optimization.estimated_total_reach.toLocaleString()}</p>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <p className="text-sm text-gray-600">Confidence Score</p>
                <p className="text-2xl font-bold text-green-600">{(optimization.confidence_score * 100).toFixed(0)}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">Platform Recommendations</h3>
            <div className="space-y-3">
              {optimization.platform_recommendations.map((platform, index) => (
                <div key={index} className={`border-l-4 p-4 rounded-lg ${
                  platform.priority === 'high' ? 'border-green-500 bg-green-50' :
                  platform.priority === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                  'border-gray-500 bg-gray-50'
                }`}>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-bold text-lg">{platform.platform_name}</h4>
                      <p className="text-sm text-gray-600">{platform.platform_type}</p>
                      <p className="text-sm mt-2">{platform.reasoning}</p>
                      {platform.optimal_timing && (
                        <p className="text-sm text-blue-600 mt-1">⏰ {platform.optimal_timing}</p>
                      )}
                    </div>
                    <div className="text-right ml-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        platform.priority === 'high' ? 'bg-green-200 text-green-800' :
                        platform.priority === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                        'bg-gray-200 text-gray-800'
                      }`}>
                        {platform.priority.toUpperCase()}
                      </span>
                      <p className="text-sm text-gray-600 mt-2">Est. Reach: {platform.estimated_reach.toLocaleString()}</p>
                      <p className="text-sm text-gray-600">Engagement: {(platform.estimated_engagement_rate * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 bg-blue-50 p-4 rounded-lg">
            <h3 className="font-bold mb-2">Optimal Release Strategy</h3>
            <p className="text-gray-700">{optimization.optimal_release_strategy}</p>
            <div className="mt-3">
              <p className="font-semibold">Target Markets:</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {optimization.target_markets.map((market, index) => (
                  <span key={index} className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm">
                    {market}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


// ============== Social Platform Native Distribution Component ==============

export const SocialPlatformDistribution = ({ token }) => {
  const [distributionData, setDistributionData] = useState({
    media_id: '',
    platforms: [],
    caption: '',
    hashtags: '',
    scheduled_time: ''
  });
  const [distributions, setDistributions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const platformOptions = [
    { value: 'tiktok', label: 'TikTok', icon: '🎵' },
    { value: 'youtube_shorts', label: 'YouTube Shorts', icon: '▶️' },
    { value: 'instagram_reels', label: 'Instagram Reels', icon: '📸' },
    { value: 'onlyfans', label: 'OnlyFans', icon: '💎' }
  ];

  const createDistribution = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const hashtags = distributionData.hashtags.split(',').map(tag => tag.trim()).filter(tag => tag);
      
      const response = await fetch(`${BACKEND_URL}/api/enhanced/social-distribution/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          media_id: distributionData.media_id,
          platforms: distributionData.platforms,
          caption: distributionData.caption,
          hashtags: hashtags,
          scheduled_time: distributionData.scheduled_time || null
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create distribution');
      }

      const data = await response.json();
      alert('Distribution created successfully!');
      setDistributionData({
        media_id: '',
        platforms: [],
        caption: '',
        hashtags: '',
        scheduled_time: ''
      });
      loadDistributions();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadDistributions = async () => {
    if (!distributionData.media_id) return;
    
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/enhanced/social-distribution/media/${distributionData.media_id}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDistributions(data.distributions || []);
      }
    } catch (err) {
      console.error('Failed to load distributions:', err);
    }
  };

  const togglePlatform = (platform) => {
    setDistributionData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter(p => p !== platform)
        : [...prev.platforms, platform]
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <span className="mr-2">🚀</span> Social Platform Native Distribution
      </h2>
      <p className="text-gray-600 mb-6">Direct distribution to TikTok, YouTube Shorts, Instagram Reels, and OnlyFans</p>

      <div className="space-y-4 mb-6">
        <input
          type="text"
          placeholder="Media ID"
          className="w-full border rounded-lg p-2"
          value={distributionData.media_id}
          onChange={(e) => setDistributionData({...distributionData, media_id: e.target.value})}
          onBlur={loadDistributions}
        />

        <div>
          <p className="font-semibold mb-2">Select Platforms:</p>
          <div className="flex flex-wrap gap-3">
            {platformOptions.map(platform => (
              <button
                key={platform.value}
                onClick={() => togglePlatform(platform.value)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all ${
                  distributionData.platforms.includes(platform.value)
                    ? 'border-blue-600 bg-blue-50 text-blue-600'
                    : 'border-gray-300 bg-white text-gray-600 hover:border-gray-400'
                }`}
              >
                <span>{platform.icon}</span>
                <span>{platform.label}</span>
              </button>
            ))}
          </div>
        </div>

        <textarea
          placeholder="Caption"
          className="w-full border rounded-lg p-2 h-24"
          value={distributionData.caption}
          onChange={(e) => setDistributionData({...distributionData, caption: e.target.value})}
        />

        <input
          type="text"
          placeholder="Hashtags (comma-separated)"
          className="w-full border rounded-lg p-2"
          value={distributionData.hashtags}
          onChange={(e) => setDistributionData({...distributionData, hashtags: e.target.value})}
        />

        <input
          type="datetime-local"
          placeholder="Scheduled Time (Optional)"
          className="w-full border rounded-lg p-2"
          value={distributionData.scheduled_time}
          onChange={(e) => setDistributionData({...distributionData, scheduled_time: e.target.value})}
        />
      </div>

      <button
        onClick={createDistribution}
        disabled={loading || !distributionData.media_id || distributionData.platforms.length === 0}
        className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Creating Distribution...' : 'Create Distribution'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {distributions.length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-bold mb-4">Recent Distributions</h3>
          <div className="space-y-3">
            {distributions.map((dist, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{dist.platform}</p>
                    <p className="text-sm text-gray-600">{dist.caption}</p>
                    <div className="flex gap-2 mt-2">
                      {dist.hashtags?.map((tag, i) => (
                        <span key={i} className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    dist.status === 'published' ? 'bg-green-200 text-green-800' :
                    dist.status === 'pending' ? 'bg-yellow-200 text-yellow-800' :
                    'bg-gray-200 text-gray-800'
                  }`}>
                    {dist.status}
                  </span>
                </div>
                {dist.platform_url && (
                  <a href={dist.platform_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 text-sm mt-2 inline-block">
                    View on {dist.platform} →
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};


// ============== Smart Royalty Routing Component ==============

export const SmartRoyaltyRouting = ({ token }) => {
  const [routingData, setRoutingData] = useState({
    release_id: '',
    track_title: '',
    splits: []
  });
  const [newSplit, setNewSplit] = useState({
    collaborator_name: '',
    value: '',
    split_type: 'percentage'
  });
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const addSplit = () => {
    if (!newSplit.collaborator_name || !newSplit.value) return;
    
    const split = {
      collaborator_id: `collab-${Date.now()}`,
      collaborator_name: newSplit.collaborator_name,
      split_type: newSplit.split_type,
      value: parseFloat(newSplit.value),
      notes: ''
    };

    setRoutingData(prev => ({
      ...prev,
      splits: [...prev.splits, split]
    }));

    setNewSplit({
      collaborator_name: '',
      value: '',
      split_type: 'percentage'
    });
  };

  const removeSplit = (index) => {
    setRoutingData(prev => ({
      ...prev,
      splits: prev.splits.filter((_, i) => i !== index)
    }));
  };

  const createRouting = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/enhanced/royalty-routing/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          id: `routing-${Date.now()}`,
          release_id: routingData.release_id,
          track_title: routingData.track_title,
          total_splits: routingData.splits.length,
          splits: routingData.splits,
          auto_reconciliation: true,
          reconciliation_frequency: 'daily',
          total_percentage: routingData.splits.reduce((sum, s) => 
            s.split_type === 'percentage' ? sum + s.value : sum, 0
          ),
          status: 'active'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create routing');
      }

      alert('Royalty routing created successfully!');
      setRoutingData({
        release_id: '',
        track_title: '',
        splits: []
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const totalPercentage = routingData.splits.reduce((sum, split) => 
    split.split_type === 'percentage' ? sum + split.value : sum, 0
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <span className="mr-2">💰</span> Smart Royalty Routing & Splits
      </h2>
      <p className="text-gray-600 mb-6">Configure automatic royalty splits with real-time reconciliation</p>

      <div className="space-y-4 mb-6">
        <input
          type="text"
          placeholder="Release ID"
          className="w-full border rounded-lg p-2"
          value={routingData.release_id}
          onChange={(e) => setRoutingData({...routingData, release_id: e.target.value})}
        />
        <input
          type="text"
          placeholder="Track Title"
          className="w-full border rounded-lg p-2"
          value={routingData.track_title}
          onChange={(e) => setRoutingData({...routingData, track_title: e.target.value})}
        />

        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-bold mb-3">Add Collaborator Split</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              type="text"
              placeholder="Collaborator Name"
              className="border rounded-lg p-2"
              value={newSplit.collaborator_name}
              onChange={(e) => setNewSplit({...newSplit, collaborator_name: e.target.value})}
            />
            <input
              type="number"
              placeholder="Value"
              className="border rounded-lg p-2"
              value={newSplit.value}
              onChange={(e) => setNewSplit({...newSplit, value: e.target.value})}
            />
            <select
              className="border rounded-lg p-2"
              value={newSplit.split_type}
              onChange={(e) => setNewSplit({...newSplit, split_type: e.target.value})}
            >
              <option value="percentage">Percentage (%)</option>
              <option value="fixed_amount">Fixed Amount ($)</option>
            </select>
            <button
              onClick={addSplit}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold"
            >
              Add Split
            </button>
          </div>
        </div>

        {routingData.splits.length > 0 && (
          <div>
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-bold">Configured Splits</h3>
              <div className={`px-3 py-1 rounded-lg font-semibold ${
                totalPercentage === 100 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                Total: {totalPercentage.toFixed(1)}%
              </div>
            </div>
            <div className="space-y-2">
              {routingData.splits.map((split, index) => (
                <div key={index} className="flex justify-between items-center border rounded-lg p-3">
                  <div>
                    <p className="font-semibold">{split.collaborator_name}</p>
                    <p className="text-sm text-gray-600">
                      {split.split_type === 'percentage' ? `${split.value}%` : `$${split.value}`}
                    </p>
                  </div>
                  <button
                    onClick={() => removeSplit(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
            {totalPercentage !== 100 && (
              <p className="text-yellow-600 text-sm mt-2">
                ⚠️ Total percentage should equal 100% for validation
              </p>
            )}
          </div>
        )}
      </div>

      <button
        onClick={createRouting}
        disabled={loading || !routingData.release_id || routingData.splits.length === 0}
        className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Creating Routing...' : 'Create Royalty Routing'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}
    </div>
  );
};


// ============== Metadata & Cover Art Automation Component ==============

export const MetadataAutomation = ({ token }) => {
  const [metadataRequest, setMetadataRequest] = useState({
    track_title: '',
    artist_name: '',
    genre: '',
    mood: '',
    color_preference: '',
    style: '',
    ai_enhance: true
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateMetadata = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/enhanced/metadata/auto-generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(metadataRequest)
      });

      if (!response.ok) {
        throw new Error('Failed to generate metadata');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <span className="mr-2">🎨</span> Metadata & Cover Art Automation
      </h2>
      <p className="text-gray-600 mb-6">AI-powered metadata generation and cover art using GPT-5 and gpt-image-1</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <input
          type="text"
          placeholder="Track Title"
          className="border rounded-lg p-2"
          value={metadataRequest.track_title}
          onChange={(e) => setMetadataRequest({...metadataRequest, track_title: e.target.value})}
        />
        <input
          type="text"
          placeholder="Artist Name"
          className="border rounded-lg p-2"
          value={metadataRequest.artist_name}
          onChange={(e) => setMetadataRequest({...metadataRequest, artist_name: e.target.value})}
        />
        <input
          type="text"
          placeholder="Genre"
          className="border rounded-lg p-2"
          value={metadataRequest.genre}
          onChange={(e) => setMetadataRequest({...metadataRequest, genre: e.target.value})}
        />
        <input
          type="text"
          placeholder="Mood (Optional)"
          className="border rounded-lg p-2"
          value={metadataRequest.mood}
          onChange={(e) => setMetadataRequest({...metadataRequest, mood: e.target.value})}
        />
        <input
          type="text"
          placeholder="Color Preference (Optional)"
          className="border rounded-lg p-2"
          value={metadataRequest.color_preference}
          onChange={(e) => setMetadataRequest({...metadataRequest, color_preference: e.target.value})}
        />
        <input
          type="text"
          placeholder="Style (Optional)"
          className="border rounded-lg p-2"
          value={metadataRequest.style}
          onChange={(e) => setMetadataRequest({...metadataRequest, style: e.target.value})}
        />
      </div>

      <div className="mb-6">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={metadataRequest.ai_enhance}
            onChange={(e) => setMetadataRequest({...metadataRequest, ai_enhance: e.target.checked})}
            className="mr-2"
          />
          <span>Generate AI Cover Art (gpt-image-1)</span>
        </label>
      </div>

      <button
        onClick={generateMetadata}
        disabled={loading || !metadataRequest.track_title || !metadataRequest.artist_name}
        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Generating with AI...' : 'Generate Metadata & Cover Art'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-6 space-y-4">
          {result.metadata?.cover_art_base64 && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-bold mb-3">AI-Generated Cover Art</h3>
              <img
                src={`data:image/png;base64,${result.metadata.cover_art_base64}`}
                alt="AI Generated Cover Art"
                className="w-full max-w-md mx-auto rounded-lg shadow-lg"
              />
            </div>
          )}

          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-bold mb-3">Generated Metadata</h3>
            <div className="space-y-2 text-sm">
              {result.suggestions?.mood && (
                <p><span className="font-semibold">Mood:</span> {result.suggestions.mood}</p>
              )}
              {result.suggestions?.description && (
                <p><span className="font-semibold">Description:</span> {result.suggestions.description}</p>
              )}
              {result.suggestions?.key_suggestion && (
                <p><span className="font-semibold">Suggested Key:</span> {result.suggestions.key_suggestion}</p>
              )}
              {result.suggestions?.bpm_range && (
                <p><span className="font-semibold">BPM Range:</span> {result.suggestions.bpm_range}</p>
              )}
            </div>

            {result.suggestions?.tags && result.suggestions.tags.length > 0 && (
              <div className="mt-3">
                <p className="font-semibold mb-2">AI-Generated Tags:</p>
                <div className="flex flex-wrap gap-2">
                  {result.suggestions.tags.map((tag, index) => (
                    <span key={index} className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};


// ============== Global Market Support Component ==============

export const GlobalMarketSupport = ({ token }) => {
  const [marketConfig, setMarketConfig] = useState({
    release_id: '',
    enabled_markets: [],
    primary_currency: 'USD'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const markets = [
    { value: 'north_america', label: 'North America', icon: '🇺🇸' },
    { value: 'europe', label: 'Europe', icon: '🇪🇺' },
    { value: 'china', label: 'China', icon: '🇨🇳' },
    { value: 'india', label: 'India', icon: '🇮🇳' },
    { value: 'africa', label: 'Africa', icon: '🌍' },
    { value: 'latin_america', label: 'Latin America', icon: '🌎' },
    { value: 'middle_east', label: 'Middle East', icon: '🏜️' },
    { value: 'southeast_asia', label: 'Southeast Asia', icon: '🌏' }
  ];

  const currencies = ['USD', 'EUR', 'GBP', 'CNY', 'INR', 'ZAR', 'BRL', 'AED'];

  const toggleMarket = (market) => {
    setMarketConfig(prev => ({
      ...prev,
      enabled_markets: prev.enabled_markets.includes(market)
        ? prev.enabled_markets.filter(m => m !== market)
        : [...prev.enabled_markets, market]
    }));
  };

  const configureMarkets = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/enhanced/global-market/configure`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          id: `market-config-${Date.now()}`,
          release_id: marketConfig.release_id,
          enabled_markets: marketConfig.enabled_markets,
          primary_currency: marketConfig.primary_currency,
          supported_currencies: [marketConfig.primary_currency],
          region_specific_platforms: {},
          localized_metadata: {},
          pricing_by_region: {},
          distribution_rights: {}
        })
      });

      if (!response.ok) {
        throw new Error('Failed to configure markets');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <span className="mr-2">🌍</span> Global Market Support
      </h2>
      <p className="text-gray-600 mb-6">Expand to global markets with region-specific platforms and localization</p>

      <div className="space-y-4 mb-6">
        <input
          type="text"
          placeholder="Release ID"
          className="w-full border rounded-lg p-2"
          value={marketConfig.release_id}
          onChange={(e) => setMarketConfig({...marketConfig, release_id: e.target.value})}
        />

        <div>
          <p className="font-semibold mb-3">Select Target Markets:</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {markets.map(market => (
              <button
                key={market.value}
                onClick={() => toggleMarket(market.value)}
                className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all ${
                  marketConfig.enabled_markets.includes(market.value)
                    ? 'border-green-600 bg-green-50 text-green-600'
                    : 'border-gray-300 bg-white text-gray-600 hover:border-gray-400'
                }`}
              >
                <span className="text-3xl">{market.icon}</span>
                <span className="text-sm font-semibold text-center">{market.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block font-semibold mb-2">Primary Currency:</label>
          <select
            className="w-full border rounded-lg p-2"
            value={marketConfig.primary_currency}
            onChange={(e) => setMarketConfig({...marketConfig, primary_currency: e.target.value})}
          >
            {currencies.map(currency => (
              <option key={currency} value={currency}>{currency}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        onClick={configureMarkets}
        disabled={loading || !marketConfig.release_id || marketConfig.enabled_markets.length === 0}
        className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Configuring Markets...' : 'Configure Global Markets'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {success && (
        <div className="mt-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
          ✅ Global markets configured successfully!
        </div>
      )}

      {marketConfig.enabled_markets.length > 0 && (
        <div className="mt-6 bg-gray-50 p-4 rounded-lg">
          <h3 className="font-bold mb-3">Selected Markets ({marketConfig.enabled_markets.length})</h3>
          <div className="flex flex-wrap gap-2">
            {marketConfig.enabled_markets.map(market => {
              const marketData = markets.find(m => m.value === market);
              return (
                <span key={market} className="bg-green-200 text-green-800 px-3 py-1 rounded-full text-sm flex items-center gap-1">
                  <span>{marketData?.icon}</span>
                  <span>{marketData?.label}</span>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};


// ============== Enhanced Features Dashboard ==============

export const EnhancedFeaturesDashboard = ({ token }) => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('ai-optimization');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/enhanced/dashboard?user_id=current-user`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDashboard(data);
      }
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'ai-optimization', label: '🤖 AI Optimization', component: AIReleaseOptimization },
    { id: 'social-distribution', label: '🚀 Social Distribution', component: SocialPlatformDistribution },
    { id: 'royalty-routing', label: '💰 Royalty Routing', component: SmartRoyaltyRouting },
    { id: 'metadata-automation', label: '🎨 Metadata & Art', component: MetadataAutomation },
    { id: 'global-markets', label: '🌍 Global Markets', component: GlobalMarketSupport }
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold mb-2">🚀 Enhanced Features Dashboard</h1>
          <p className="text-gray-600">AI-powered tools for release optimization, distribution, and global expansion</p>
        </div>

        {dashboard && !loading && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 text-white p-4 rounded-lg">
              <p className="text-sm opacity-90">AI Optimizations</p>
              <p className="text-3xl font-bold">{dashboard.ai_optimization_count}</p>
            </div>
            <div className="bg-gradient-to-br from-green-500 to-teal-600 text-white p-4 rounded-lg">
              <p className="text-sm opacity-90">Social Distributions</p>
              <p className="text-3xl font-bold">{dashboard.social_distributions_count}</p>
            </div>
            <div className="bg-gradient-to-br from-purple-500 to-pink-600 text-white p-4 rounded-lg">
              <p className="text-sm opacity-90">Royalty Routings</p>
              <p className="text-3xl font-bold">{dashboard.active_royalty_routings}</p>
            </div>
            <div className="bg-gradient-to-br from-indigo-500 to-blue-600 text-white p-4 rounded-lg">
              <p className="text-sm opacity-90">Auto Metadata</p>
              <p className="text-3xl font-bold">{dashboard.automated_metadata_count}</p>
            </div>
            <div className="bg-gradient-to-br from-green-600 to-emerald-700 text-white p-4 rounded-lg">
              <p className="text-sm opacity-90">Global Markets</p>
              <p className="text-3xl font-bold">{dashboard.enabled_global_markets}</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="flex flex-wrap border-b">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 font-semibold transition-colors ${
                  activeTab === tab.id
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          {ActiveComponent && <ActiveComponent token={token} />}
        </div>
      </div>
    </div>
  );
};

export default EnhancedFeaturesDashboard;
