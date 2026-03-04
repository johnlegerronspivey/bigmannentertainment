import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const PlatformsPage = () => {
  const [allPlatforms, setAllPlatforms] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
                description: platformConfig.description,
                type: platformConfig.type,
                supported_formats: platformConfig.supported_formats,
                max_file_size: platformConfig.max_file_size
              });
            });
          }
          
          Object.keys(organizedPlatforms).forEach(category => {
            organizedPlatforms[category].sort((a, b) => a.name.localeCompare(b.name));
          });
          
          setAllPlatforms(organizedPlatforms);
        } else {
          setError('Failed to load platforms');
        }
      } catch (error) {
        console.error('Error fetching platforms:', error);
        setError('Error loading platforms');
      } finally {
        setLoading(false);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading platforms...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-red-600">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  const totalPlatforms = Object.values(allPlatforms).reduce((sum, category) => sum + category.length, 0);

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="text-center mb-8">
        <img 
          src="/big-mann-logo.png" 
          alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
          className="w-20 h-20 object-contain mx-auto mb-4 shadow-lg rounded-lg"
        />
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Distribution Platforms</h1>
        <p className="text-xl text-gray-600 mb-2">Distribute your content across <span className="font-bold text-purple-600">{totalPlatforms} platforms</span> worldwide</p>
        <p className="text-gray-500">Complete Media Distribution Empire by Big Mann Entertainment - John LeGerron Spivey, Founder & CEO</p>
      </div>
      
      {/* Platform Categories Grid */}
      <div className="grid lg:grid-cols-3 md:grid-cols-2 gap-8 mb-8">
        {Object.entries(allPlatforms).map(([category, platforms]) => (
          <div key={category} className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-purple-500">
            <div className="flex items-center mb-4">
              <h3 className="text-xl font-semibold text-purple-700">{category}</h3>
              <span className="ml-2 bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                {platforms.length}
              </span>
            </div>
            <div className="space-y-2">
              {platforms.map((platform) => (
                <div key={platform.id || platform.name} className="flex items-center text-sm text-gray-700">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                  <div>
                    <div className="font-medium">{platform.name || platform}</div>
                    {platform.description && (
                      <div className="text-xs text-gray-500">{platform.description}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {/* Platform Statistics */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-lg text-center">
          <div className="text-3xl font-bold">{totalPlatforms}</div>
          <div className="text-purple-100">Total Platforms</div>
        </div>
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-lg text-center">
          <div className="text-3xl font-bold">{allPlatforms["Social Media"]?.length || 0}</div>
          <div className="text-blue-100">Social Media</div>
        </div>
        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-lg text-center">
          <div className="text-3xl font-bold">{allPlatforms["Music Streaming"]?.length || 0}</div>
          <div className="text-green-100">Music Streaming</div>
        </div>
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-lg text-center">
          <div className="text-3xl font-bold">{allPlatforms["Model Agencies & Photography"]?.length || 0}</div>
          <div className="text-orange-100">Model Agencies</div>
        </div>
      </div>

      {/* Platform Types Overview */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-8 rounded-lg">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Platform Coverage</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-4xl mb-2">🌐</div>
            <h3 className="font-semibold text-gray-800">Global Reach</h3>
            <p className="text-sm text-gray-600">Platforms spanning North America, Europe, Asia, Africa, and more</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-2">🎵</div>
            <h3 className="font-semibold text-gray-800">Music Focus</h3>
            <p className="text-sm text-gray-600">Comprehensive music streaming and audio platform coverage</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-2">📱</div>
            <h3 className="font-semibold text-gray-800">Multi-Format</h3>
            <p className="text-sm text-gray-600">Support for audio, video, images, and multimedia content</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-2">🚀</div>
            <h3 className="font-semibold text-gray-800">Emerging Tech</h3>
            <p className="text-sm text-gray-600">Web3, blockchain, and NFT marketplace integration</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-2">📺</div>
            <h3 className="font-semibold text-gray-800">Video & TV</h3>
            <p className="text-sm text-gray-600">Major streaming services and television networks</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-2">⚖️</div>
            <h3 className="font-semibold text-gray-800">Rights Management</h3>
            <p className="text-sm text-gray-600">Music rights organizations and royalty collection</p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-2">📸</div>
            <h3 className="font-semibold text-gray-800">Model Agencies</h3>
            <p className="text-sm text-gray-600">Premier modeling agencies and photography platforms</p>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="text-center mt-8 bg-white p-8 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready to Distribute?</h2>
        <p className="text-gray-600 mb-6">
          Start distributing your content across all {totalPlatforms} platforms with Big Mann Entertainment
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link 
            to="/distribute" 
            className="bg-purple-600 text-white px-8 py-3 rounded-lg hover:bg-purple-700 transition font-semibold"
          >
            Start Distribution
          </Link>
          <Link 
            to="/register" 
            className="bg-white text-purple-600 border-2 border-purple-600 px-8 py-3 rounded-lg hover:bg-purple-50 transition font-semibold"
          >
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PlatformsPage;
