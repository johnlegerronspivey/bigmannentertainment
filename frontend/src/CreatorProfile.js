import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { QRCodeDisplay } from './CreatorProfileComponents';

const CreatorProfilePage = () => {
  const { username } = useParams();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('assets');
  const [showQRModal, setShowQRModal] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${backendUrl}/api/profile/${username}`);
        setProfileData(response.data);
      } catch (err) {
        console.error('Failed to load profile:', err);
        setError(err.response?.data?.detail || 'Profile not found');
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchProfile();
    }
  }, [username, backendUrl]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
          <p className="text-white mt-4">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Profile Not Found</h2>
          <p className="text-gray-300 mb-6">{error}</p>
          <a href="/" className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            Go Home
          </a>
        </div>
      </div>
    );
  }

  const { identity, assets, traceability, royalties, dao, sidebar, stats } = profileData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Profile Header */}
        <div className="bg-gray-800 rounded-xl shadow-2xl p-8 mb-8 border border-purple-500/30">
          <div className="flex items-start gap-6">
            {/* Avatar */}
            <div className="flex-shrink-0">
              {identity.avatarUrl ? (
                <img
                  src={identity.avatarUrl}
                  alt={identity.displayName}
                  className="w-32 h-32 rounded-full border-4 border-purple-500"
                />
              ) : (
                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-4xl font-bold text-white border-4 border-purple-500">
                  {identity.displayName?.charAt(0) || 'U'}
                </div>
              )}
            </div>

            {/* Info */}
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-white mb-2">{identity.displayName}</h1>
              <p className="text-lg text-purple-300 mb-3">@{identity.username}</p>
              {identity.tagline && (
                <p className="text-gray-300 text-lg mb-4">{identity.tagline}</p>
              )}
              {identity.bio && (
                <p className="text-gray-400 mb-4">{identity.bio}</p>
              )}
              
              {/* Location & GS1 */}
              <div className="flex flex-wrap gap-4 mb-4">
                {identity.location && (
                  <div className="flex items-center gap-2 text-gray-300">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                    <span>{identity.location}</span>
                  </div>
                )}
                {identity.gln && (
                  <div className="flex items-center gap-2 text-purple-300 font-mono text-sm">
                    <span className="font-semibold">GLN:</span>
                    <span>{identity.gln}</span>
                  </div>
                )}
              </div>

              {/* Social Links */}
              {identity.socials && identity.socials.length > 0 && (
                <div className="flex flex-wrap gap-3">
                  {identity.socials.map((social, idx) => (
                    <a
                      key={idx}
                      href={social.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
                    >
                      {social.icon && <img src={social.icon} alt={social.name} className="w-5 h-5" />}
                      <span>{social.name}</span>
                      {social.connected && <span className="text-green-400">✓</span>}
                    </a>
                  ))}
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="hidden lg:block">
              <div className="bg-gray-900 rounded-lg p-4 space-y-3">
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-400">{stats.totalAssets}</div>
                  <div className="text-sm text-gray-400">Assets</div>
                </div>
                {royalties.showPublic && (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-400">${stats.totalRoyalties.toFixed(2)}</div>
                    <div className="text-sm text-gray-400">Royalties</div>
                  </div>
                )}
                {dao.showActivity && (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-400">{stats.daoProposals}</div>
                    <div className="text-sm text-gray-400">Proposals</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-gray-800 rounded-xl shadow-2xl border border-purple-500/30 mb-8">
          <div className="flex border-b border-gray-700">
            {['assets', 'traceability', 'dao', 'about'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 font-semibold text-sm uppercase tracking-wider transition-colors ${
                  activeTab === tab
                    ? 'text-purple-400 border-b-2 border-purple-500'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="p-6">
            {/* Assets Tab */}
            {activeTab === 'assets' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {assets.length > 0 ? (
                  assets.map((asset) => (
                    <div key={asset.id} className="bg-gray-900 rounded-lg overflow-hidden hover:shadow-xl transition-shadow border border-gray-700">
                      {asset.thumbnail && (
                        <img src={asset.thumbnail} alt={asset.title} className="w-full h-48 object-cover" />
                      )}
                      <div className="p-4">
                        <h3 className="text-lg font-bold text-white mb-2">{asset.title}</h3>
                        {asset.description && (
                          <p className="text-sm text-gray-400 mb-3">{asset.description}</p>
                        )}
                        
                        {/* GS1 Metadata */}
                        <div className="space-y-1 mb-3 text-xs font-mono">
                          {asset.gtin && (
                            <div className="text-purple-300">
                              <span className="text-gray-500">GTIN:</span> {asset.gtin}
                            </div>
                          )}
                          {asset.isrc && (
                            <div className="text-blue-300">
                              <span className="text-gray-500">ISRC:</span> {asset.isrc}
                            </div>
                          )}
                          {asset.isan && (
                            <div className="text-green-300">
                              <span className="text-gray-500">ISAN:</span> {asset.isan}
                            </div>
                          )}
                        </div>

                        {/* Engagement */}
                        <div className="flex items-center gap-4 text-sm text-gray-400 mb-3">
                          <span>👁 {asset.engagement.views}</span>
                          <span>❤️ {asset.engagement.likes}</span>
                          <span>↗️ {asset.engagement.shares}</span>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2">
                          {asset.gs1_digital_link && (
                            <a
                              href={asset.gs1_digital_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded transition-colors text-center"
                            >
                              View GS1 Link
                            </a>
                          )}
                          {asset.qr_code && (
                            <button
                              onClick={() => {
                                // Show QR code modal
                                alert('QR Code feature coming soon');
                              }}
                              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded transition-colors"
                            >
                              QR
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="col-span-3 text-center py-12 text-gray-400">
                    No assets yet
                  </div>
                )}
              </div>
            )}

            {/* Traceability Tab */}
            {activeTab === 'traceability' && (
              <div className="space-y-4">
                {traceability.length > 0 ? (
                  traceability.map((event) => (
                    <div key={event.id} className="bg-gray-900 rounded-lg p-4 border-l-4 border-purple-500">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold text-white mb-1">{event.description}</h4>
                          <div className="flex items-center gap-4 text-sm text-gray-400">
                            {event.platform && <span>📱 {event.platform}</span>}
                            {event.location && <span>📍 {event.location}</span>}
                            <span className="text-purple-300">{event.eventType}</span>
                          </div>
                        </div>
                        <span className="text-sm text-gray-500">
                          {new Date(event.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    No traceability events yet
                  </div>
                )}
              </div>
            )}

            {/* DAO Tab */}
            {activeTab === 'dao' && dao.showActivity && (
              <div className="space-y-4">
                {dao.proposals.length > 0 ? (
                  dao.proposals.map((proposal) => (
                    <div key={proposal.id} className="bg-gray-900 rounded-lg p-6 border border-gray-700">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                          <h4 className="text-xl font-bold text-white mb-2">{proposal.title}</h4>
                          <p className="text-gray-400 mb-3">{proposal.description}</p>
                          <span className={`inline-block px-3 py-1 rounded-full text-sm ${
                            proposal.status === 'open' ? 'bg-green-500/20 text-green-400' :
                            proposal.status === 'approved' ? 'bg-blue-500/20 text-blue-400' :
                            proposal.status === 'rejected' ? 'bg-red-500/20 text-red-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {proposal.status}
                          </span>
                        </div>
                      </div>
                      
                      {/* Vote Counts */}
                      <div className="grid grid-cols-3 gap-4 bg-gray-800 rounded-lg p-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-400">{proposal.votes.yes}</div>
                          <div className="text-sm text-gray-400">Yes</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-400">{proposal.votes.no}</div>
                          <div className="text-sm text-gray-400">No</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-gray-400">{proposal.votes.abstain}</div>
                          <div className="text-sm text-gray-400">Abstain</div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    No proposals yet
                  </div>
                )}
              </div>
            )}

            {/* About Tab */}
            {activeTab === 'about' && (
              <div className="space-y-6">
                {sidebar.campaign && (
                  <div className="bg-gray-900 rounded-lg p-6 border border-purple-500/30">
                    <h3 className="text-xl font-bold text-purple-400 mb-3">Current Campaign</h3>
                    <h4 className="text-lg font-semibold text-white mb-2">{sidebar.campaign.title}</h4>
                    {sidebar.campaign.description && (
                      <p className="text-gray-400">{sidebar.campaign.description}</p>
                    )}
                  </div>
                )}

                {sidebar.sponsors.length > 0 && (
                  <div className="bg-gray-900 rounded-lg p-6">
                    <h3 className="text-xl font-bold text-purple-400 mb-4">Sponsors</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {sidebar.sponsors.map((sponsor, idx) => (
                        <div key={idx} className="text-center">
                          {sponsor.logo ? (
                            <img src={sponsor.logo} alt={sponsor.name} className="h-16 mx-auto mb-2" />
                          ) : (
                            <div className="h-16 bg-gray-700 rounded flex items-center justify-center mb-2">
                              <span className="text-gray-400 text-sm">{sponsor.name}</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {sidebar.comments.length > 0 && (
                  <div className="bg-gray-900 rounded-lg p-6">
                    <h3 className="text-xl font-bold text-purple-400 mb-4">Recent Comments</h3>
                    <div className="space-y-3">
                      {sidebar.comments.map((comment) => (
                        <div key={comment.id} className="border-l-2 border-purple-500 pl-4">
                          <p className="text-white mb-1">{comment.text}</p>
                          <div className="flex items-center gap-2 text-sm text-gray-400">
                            <span>{comment.commenterName}</span>
                            <span>•</span>
                            <span>{new Date(comment.timestamp).toLocaleDateString()}</span>
                            <span>•</span>
                            <span>❤️ {comment.likes}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreatorProfilePage;
