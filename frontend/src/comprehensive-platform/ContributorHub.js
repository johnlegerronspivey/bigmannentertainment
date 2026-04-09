import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';

const ContributorHub = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [contributors, setContributors] = useState([]);
  const [collaborationRequests, setCollaborationRequests] = useState([]);
  const [collaborations, setCollaborations] = useState([]);
  const [contributorStats, setContributorStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('discover');

  useEffect(() => {
    fetchContributorData();
  }, []);

  const fetchContributorData = async () => {
    setLoading(true);
    try {
      const [contributorsRes, requestsRes, collaborationsRes, statsRes] = await Promise.all([
        axios.get(`${API}/api/platform/contributors/search?user_id=user_123`),
        axios.get(`${API}/api/platform/contributors/requests?user_id=user_123`),
        axios.get(`${API}/api/platform/contributors/collaborations?user_id=user_123`),
        axios.get(`${API}/api/platform/contributors/stats?user_id=user_123`)
      ]);

      if (contributorsRes.data.success) setContributors(contributorsRes.data.contributors || []);
      if (requestsRes.data.success) setCollaborationRequests(requestsRes.data.requests || []);
      if (collaborationsRes.data.success) setCollaborations(collaborationsRes.data.collaborations || []);
      if (statsRes.data.success) setContributorStats(statsRes.data.stats || {});
    } catch (error) {
      handleApiError(error, 'fetchContributorData');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'discover', name: 'Discover', icon: '🔍' },
    { id: 'requests', name: 'Requests', icon: '📩' },
    { id: 'collaborations', name: 'Active Collaborations', icon: '🤝' },
    { id: 'payments', name: 'Payments', icon: '💳' },
    { id: 'profile', name: 'My Profile', icon: '👤' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Contributor Hub</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Connect and collaborate with creators</p>
        </div>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2">
          <span>➕</span>
          <span>Send Request</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Collaborations</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contributorStats.profile?.total_collaborations || '0'}</p>
            </div>
            <span className="text-2xl">🤝</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-green-600">{contributorStats.profile?.success_rate || '0'}%</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Earned</p>
              <p className="text-2xl font-bold text-blue-600">${contributorStats.earnings?.total_earned?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">💰</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Average Rating</p>
              <p className="text-2xl font-bold text-yellow-600">{contributorStats.profile?.average_rating || '0'}⭐</p>
            </div>
            <span className="text-2xl">⭐</span>
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
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-green-500 text-green-600 dark:text-green-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
              {tab.id === 'requests' && collaborationRequests.length > 0 && (
                <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 ml-1">
                  {collaborationRequests.filter(r => r.status === 'pending').length}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'discover' && (
          <div className="space-y-4">
            {/* Search and Filters */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <input
                type="text"
                placeholder="Search contributors..."
                className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
              />
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Roles</option>
                <option>Producer</option>
                <option>Vocalist</option>
                <option>Instrumentalist</option>
                <option>Songwriter</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Genres</option>
                <option>Hip-Hop</option>
                <option>Pop</option>
                <option>R&B</option>
                <option>Electronic</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>Any Budget</option>
                <option>Under $500</option>
                <option>$500 - $1000</option>
                <option>$1000+</option>
              </select>
            </div>

            {/* Contributors Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {contributors.length > 0 ? contributors.map((contributor, index) => (
                <div key={contributor.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                      {contributor.stage_name ? contributor.stage_name.charAt(0) : 'C'}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{contributor.stage_name || 'Unknown'}</h3>
                      <div className="flex items-center space-x-2">
                        <span className="text-yellow-500">⭐</span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">{contributor.rating || '0.0'}</span>
                        <span className="text-sm text-gray-500">({contributor.total_collaborations || 0} collaborations)</span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{contributor.bio || 'No bio available'}</p>
                  
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Roles</p>
                    <div className="flex flex-wrap gap-1">
                      {contributor.roles?.map((role, idx) => (
                        <span key={idx} className="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 text-xs rounded">
                          {role}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Skills</p>
                    <div className="flex flex-wrap gap-1">
                      {contributor.skills?.slice(0, 3).map((skill, idx) => (
                        <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-xs rounded">
                          {skill}
                        </span>
                      ))}
                      {contributor.skills?.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200 text-xs rounded">
                          +{contributor.skills.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div>
                      {contributor.hourly_rate && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">${contributor.hourly_rate}/hr</p>
                      )}
                      <p className="text-xs text-gray-500">{contributor.location || 'Location not specified'}</p>
                    </div>
                    <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                      Contact
                    </button>
                  </div>
                </div>
              )) : (
                <div className="col-span-full text-center py-8">
                  <div className="text-4xl mb-4">👥</div>
                  <p className="text-gray-600 dark:text-gray-400">No contributors found. Try adjusting your search filters.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'requests' && (
          <div className="space-y-4">
            {collaborationRequests.length > 0 ? collaborationRequests.map((request, index) => (
              <div key={request.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{request.project_title}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        request.status === 'pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        request.status === 'accepted' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        request.status === 'completed' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                      }`}>
                        {request.status}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{request.project_description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Roles: {request.required_roles?.join(', ')}</span>
                      {request.budget_range && (
                        <span>Budget: ${request.budget_range.min} - ${request.budget_range.max}</span>
                      )}
                      <span>Timeline: {request.timeline || 'Not specified'}</span>
                    </div>
                  </div>
                  {request.status === 'pending' && (
                    <div className="flex space-x-2 ml-4">
                      <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Accept
                      </button>
                      <button className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700">
                        Decline
                      </button>
                    </div>
                  )}
                </div>
                
                {request.message && (
                  <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p className="text-sm text-gray-700 dark:text-gray-300">"{request.message}"</p>
                  </div>
                )}
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📩</div>
                <p className="text-gray-600 dark:text-gray-400">No collaboration requests at the moment.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'collaborations' && (
          <div className="space-y-4">
            {collaborations.length > 0 ? collaborations.map((collaboration, index) => (
              <div key={collaboration.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{collaboration.project_title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {collaboration.participants?.length || 0} participants • Started {collaboration.start_date ? new Date(collaboration.start_date).toLocaleDateString() : 'Recently'}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    collaboration.status === 'in_progress' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                    collaboration.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                  }`}>
                    {collaboration.status?.replace('_', ' ')}
                  </span>
                </div>
                
                {collaboration.milestones && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Milestones</h4>
                    <div className="space-y-2">
                      {collaboration.milestones.map((milestone, idx) => (
                        <div key={idx} className="flex items-center space-x-3">
                          <span className={`w-4 h-4 rounded-full flex-shrink-0 ${
                            milestone.status === 'completed' ? 'bg-green-500' :
                            milestone.status === 'in_progress' ? 'bg-blue-500' :
                            'bg-gray-300 dark:bg-gray-600'
                          }`}></span>
                          <span className="text-sm text-gray-700 dark:text-gray-300">{milestone.title}</span>
                          <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">
                            {milestone.due_date || milestone.date}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Budget: ${collaboration.budget_total?.toLocaleString() || '0'}
                  </div>
                  <div className="flex space-x-2">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">View Details</button>
                    <button className="text-green-600 hover:text-green-700 text-sm font-medium">Message</button>
                  </div>
                </div>
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🤝</div>
                <p className="text-gray-600 dark:text-gray-400">No active collaborations. Start your first collaboration!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'payments' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`${isDarkMode ? 'bg-green-800 border-green-700' : 'bg-green-50 border-green-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-green-900 dark:text-green-100">Total Earned</h3>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-2">
                  ${contributorStats.earnings?.total_earned?.toLocaleString() || '0'}
                </p>
              </div>
              <div className={`${isDarkMode ? 'bg-blue-800 border-blue-700' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">This Month</h3>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-2">
                  ${contributorStats.earnings?.this_month?.toLocaleString() || '1,850'}
                </p>
              </div>
              <div className={`${isDarkMode ? 'bg-yellow-800 border-yellow-700' : 'bg-yellow-50 border-yellow-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">Pending</h3>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100 mt-2">
                  ${contributorStats.earnings?.pending?.toLocaleString() || '650'}
                </p>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Payment History</h3>
              <div className="space-y-4">
                {[
                  { project: 'Pop Single Vocals', amount: 480.00, date: '2024-01-15', status: 'Paid', method: 'PayPal' },
                  { project: 'Hip-Hop Beat Production', amount: 650.00, date: '2024-01-10', status: 'Processing', method: 'Bank Transfer' },
                  { project: 'Acoustic Guitar Session', amount: 150.00, date: '2024-01-05', status: 'Paid', method: 'Crypto' }
                ].map((payment, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{payment.project}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{payment.date} • {payment.method}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900 dark:text-white">${payment.amount}</p>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        payment.status === 'Paid' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      }`}>
                        {payment.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Profile Statistics</h3>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  Edit Profile
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Performance Metrics</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Success Rate</span>
                      <span className="font-medium text-green-600">{contributorStats.profile?.success_rate || '0'}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Response Rate</span>
                      <span className="font-medium text-blue-600">{contributorStats.profile?.response_rate || '98.5'}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Avg Response Time</span>
                      <span className="font-medium text-gray-900 dark:text-white">{contributorStats.profile?.average_response_time || '2.3 hours'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Total Reviews</span>
                      <span className="font-medium text-gray-900 dark:text-white">{contributorStats.profile?.total_reviews || '12'}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Skills Performance</h4>
                  <div className="space-y-3">
                    {contributorStats.skills_performance?.skill_ratings && Object.entries(contributorStats.skills_performance.skill_ratings).map(([skill, rating]) => (
                      <div key={skill} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{skill}</span>
                        <div className="flex items-center space-x-1">
                          <span className="text-yellow-500">⭐</span>
                          <span className="font-medium text-gray-900 dark:text-white">{rating}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Achievements</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { title: 'Early Member', description: 'Joined within first 100 users', icon: '🏆' },
                  { title: 'Top Collaborator', description: '90%+ success rate', icon: '⭐' },
                  { title: 'Fast Responder', description: 'Avg response under 4 hours', icon: '⚡' },
                  { title: 'Highly Rated', description: '4.5+ star average', icon: '🌟' }
                ].map((achievement, index) => (
                  <div key={index} className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl mb-2">{achievement.icon}</div>
                    <h4 className="font-medium text-gray-900 dark:text-white text-sm">{achievement.title}</h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{achievement.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { ContributorHub };
