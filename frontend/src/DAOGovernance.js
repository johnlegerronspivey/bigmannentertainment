import React, { useState } from 'react';
import { ProposalCreator, ProposalList } from './CreatorProfileComponents';

const DAOGovernance = () => {
  const [activeTab, setActiveTab] = useState('proposals');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleProposalCreated = () => {
    setRefreshTrigger(prev => prev + 1);
    setActiveTab('proposals');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">DAO Governance</h1>
          <p className="text-gray-400">
            Participate in platform decisions through decentralized voting
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-xl p-6 mb-8">
          <div className="flex items-start gap-4">
            <span className="text-4xl">🏛️</span>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-2">About DAO Governance</h3>
              <p className="text-gray-300 mb-4">
                The Big Mann Entertainment DAO allows all creators to participate in platform decisions.
                Vote on royalty adjustments, new platform additions, policy changes, and more.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <div className="text-purple-400 font-semibold mb-1">📊 Weighted Voting</div>
                  <div className="text-gray-400">Your vote weight is based on platform activity</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <div className="text-purple-400 font-semibold mb-1">⚡ Automatic Execution</div>
                  <div className="text-gray-400">Approved proposals are automatically implemented</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <div className="text-purple-400 font-semibold mb-1">🔒 Transparent</div>
                  <div className="text-gray-400">All votes and proposals are publicly visible</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-gray-800 rounded-xl shadow-xl mb-6">
          <div className="flex border-b border-gray-700">
            {[
              { id: 'proposals', label: 'Active Proposals', icon: '📋' },
              { id: 'create', label: 'Create Proposal', icon: '✨' },
              { id: 'history', label: 'History', icon: '📜' }
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
        <div key={refreshTrigger}>
          {activeTab === 'proposals' && <ProposalList />}
          
          {activeTab === 'create' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ProposalCreator onSuccess={handleProposalCreated} />
              </div>
              <div className="space-y-4">
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">📝 Proposal Guidelines</h3>
                  <ul className="space-y-3 text-sm text-gray-300">
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>Be clear and specific about what you're proposing</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>Provide detailed reasoning and expected benefits</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>Consider the impact on all platform stakeholders</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>Include relevant data or examples when possible</span>
                    </li>
                  </ul>
                </div>

                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">⚙️ Proposal Types</h3>
                  <div className="space-y-3 text-sm">
                    <div>
                      <div className="text-purple-400 font-semibold">Royalty Adjustment</div>
                      <div className="text-gray-400">Changes to royalty split percentages</div>
                    </div>
                    <div>
                      <div className="text-purple-400 font-semibold">Platform Addition</div>
                      <div className="text-gray-400">Request new distribution platforms</div>
                    </div>
                    <div>
                      <div className="text-purple-400 font-semibold">Policy Change</div>
                      <div className="text-gray-400">Modifications to platform policies</div>
                    </div>
                    <div>
                      <div className="text-purple-400 font-semibold">Feature Request</div>
                      <div className="text-gray-400">New features or improvements</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'history' && (
            <div className="bg-gray-800 rounded-xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-white mb-6">Governance History</h3>
              <div className="space-y-4">
                <div className="bg-gray-900 rounded-lg p-4 border-l-4 border-green-500">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-white">Add ESPN to Distribution Platforms</h4>
                    <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                      Approved
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">
                    Proposal to integrate ESPN as a distribution platform in the Television & Video Streaming section.
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>👍 85% Yes</span>
                    <span>•</span>
                    <span>📅 Implemented Dec 2024</span>
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-4 border-l-4 border-blue-500">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-white">Comprehensive Licensing System</h4>
                    <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
                      Approved
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">
                    Implement comprehensive platform licensing with automated workflows and GS1 integration.
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>👍 92% Yes</span>
                    <span>•</span>
                    <span>📅 Implemented Nov 2024</span>
                  </div>
                </div>

                <div className="bg-gray-900 rounded-lg p-4 border-l-4 border-red-500">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-white">Reduce Platform Upload Fees</h4>
                    <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm">
                      Rejected
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">
                    Proposal to reduce platform upload fees by 50% across all tiers.
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>👎 68% No</span>
                    <span>•</span>
                    <span>📅 Voted Oct 2024</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DAOGovernance;