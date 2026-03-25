import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const ProposalsList = ({ proposals }) => {
  const getProposalTypeColor = (type) => {
    switch (type) {
      case 'content_approval': return 'bg-blue-100 text-blue-800';
      case 'takedown_request': return 'bg-red-100 text-red-800';
      case 'royalty_split_change': return 'bg-green-100 text-green-800';
      case 'cross_label_agreement': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-yellow-100 text-yellow-800';
      case 'passed': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'executed': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (proposals.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">No active proposals</div>
        <p className="text-gray-400 mt-2">Create a new proposal to get started with DAO governance</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold mb-4">📋 Active Proposals</h3>
      {proposals.map((proposal, index) => (
        <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
          <div className="flex justify-between items-start mb-3">
            <div>
              <h4 className="font-medium text-lg">{proposal.title}</h4>
              <p className="text-sm text-gray-600 mt-1">{proposal.description}</p>
            </div>
            <div className="flex space-x-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getProposalTypeColor(proposal.proposal_type)}`}>
                {proposal.proposal_type.replace('_', ' ')}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(proposal.status)}`}>
                {proposal.status}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
            <div className="text-sm">
              <span className="font-medium">Proposer:</span> {proposal.proposer_id}
            </div>
            <div className="text-sm">
              <span className="font-medium">Voting Deadline:</span> {new Date(proposal.voting_deadline).toLocaleDateString()}
            </div>
            <div className="text-sm">
              <span className="font-medium">Affected Labels:</span> {proposal.affected_labels?.length || 0}
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-3 mb-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Voting Progress</span>
              <span className="text-sm text-gray-600">
                {((proposal.participation_rate || 0) * 100).toFixed(1)}% participation
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full" 
                style={{ width: `${(proposal.participation_rate || 0) * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="flex justify-between items-center">
            <div className="flex space-x-4 text-sm">
              <span className="text-green-600">
                👍 For: {Object.keys(proposal.votes_for || {}).length}
              </span>
              <span className="text-red-600">
                👎 Against: {Object.keys(proposal.votes_against || {}).length}
              </span>
              <span className="text-gray-600">
                🤷 Abstain: {Object.keys(proposal.votes_abstain || {}).length}
              </span>
            </div>
            
            {proposal.status === 'active' && (
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 text-sm rounded transition-colors">
                Vote
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

const VotingInterface = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🗳️ Voting Interface</h3>
    <p className="text-gray-600">Cast your vote on active proposals</p>
    
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h4 className="font-medium text-blue-900 mb-2">Your Voting Power</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">5.0</div>
          <div className="text-sm text-blue-700">Total voting power</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">3</div>
          <div className="text-sm text-green-700">Labels represented</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">12</div>
          <div className="text-sm text-purple-700">Votes cast this quarter</div>
        </div>
      </div>
    </div>
    
    <div className="p-4 border border-gray-200 rounded-lg">
      <h4 className="font-medium mb-2">How Voting Power is Calculated</h4>
      <div className="text-sm text-gray-600 space-y-1">
        <p>• Each label in the ULN receives base voting power of 1.0</p>
        <p>• Additional power based on revenue contribution (max +2.0)</p>
        <p>• Bonus for active participation in governance (+0.5)</p>
        <p>• Penalty for missed votes in previous quarter (-0.5)</p>
      </div>
    </div>
  </div>
);

const GovernanceRules = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">⚖️ Governance Rules</h3>
    <p className="text-gray-600">Rules and thresholds for DAO decision-making</p>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Voting Thresholds</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span>Content Approval:</span>
            <span className="font-medium">Simple majority (51%)</span>
          </div>
          <div className="flex justify-between">
            <span>Royalty Changes:</span>
            <span className="font-medium">Supermajority (67%)</span>
          </div>
          <div className="flex justify-between">
            <span>Takedown Requests:</span>
            <span className="font-medium">Simple majority (51%)</span>
          </div>
          <div className="flex justify-between">
            <span>System Changes:</span>
            <span className="font-medium">Supermajority (75%)</span>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Participation Requirements</h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span>Minimum participation:</span>
            <span className="font-medium">51% of voting power</span>
          </div>
          <div className="flex justify-between">
            <span>Voting period:</span>
            <span className="font-medium">7 days (standard)</span>
          </div>
          <div className="flex justify-between">
            <span>Emergency voting:</span>
            <span className="font-medium">24 hours</span>
          </div>
          <div className="flex justify-between">
            <span>Proposal bond:</span>
            <span className="font-medium">$1,000 (refundable)</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const GovernanceHistory = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">📜 Governance History</h3>
    <p className="text-gray-600">Historical record of all DAO decisions and votes</p>
    
    <div className="space-y-3">
      <div className="p-4 border border-gray-200 rounded-lg">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Cross-label content sharing for track XYZ123</h4>
            <p className="text-sm text-gray-600">Approved federated access across 5 labels</p>
            <p className="text-xs text-gray-500">Executed on: March 15, 2025</p>
          </div>
          <div className="text-right">
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              Passed (78% approval)
            </span>
            <div className="text-xs text-gray-500 mt-1">
              15 votes cast
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Q4 2024 Royalty Distribution Method</h4>
            <p className="text-sm text-gray-600">Change from equal split to proportional distribution</p>
            <p className="text-xs text-gray-500">Executed on: March 10, 2025</p>
          </div>
          <div className="text-right">
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              Passed (89% approval)
            </span>
            <div className="text-xs text-gray-500 mt-1">
              23 votes cast
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Content takedown request for track ABC456</h4>
            <p className="text-sm text-gray-600">Request to remove content due to rights dispute</p>
            <p className="text-xs text-gray-500">Rejected on: March 8, 2025</p>
          </div>
          <div className="text-right">
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
              Rejected (34% approval)
            </span>
            <div className="text-xs text-gray-500 mt-1">
              18 votes cast
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export const DAOGovernance = () => {
  const [activeSection, setActiveSection] = useState('proposals');
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchProposals = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/uln/dao/proposals`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setProposals(data.proposals || []);
      }
    } catch (error) {
      console.error('Error fetching proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeSection === 'proposals') {
      fetchProposals();
    }
  }, [activeSection]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">🗳️ DAO Governance</h2>
          <p className="text-gray-600">Decentralized decision-making for the Unified Label Network</p>
        </div>
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors">
          + Create Proposal
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['proposals', 'voting', 'governance', 'history'].map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`capitalize py-2 px-4 rounded-md font-medium transition-colors ${
                activeSection === section 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {section.replace('_', ' ')}
            </button>
          ))}
        </nav>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        {loading && (
          <div className="flex justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        )}

        {activeSection === 'proposals' && !loading && (
          <ProposalsList proposals={proposals} />
        )}

        {activeSection === 'voting' && (
          <VotingInterface />
        )}

        {activeSection === 'governance' && (
          <GovernanceRules />
        )}

        {activeSection === 'history' && (
          <GovernanceHistory />
        )}
      </div>
    </div>
  );
};
