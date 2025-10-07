import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ProposalDetail = () => {
  const { proposalId } = useParams();
  const navigate = useNavigate();
  const [proposal, setProposal] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [votingOn, setVotingOn] = useState(false);

  useEffect(() => {
    fetchProposal();
    fetchComments();
  }, [proposalId]);

  const fetchProposal = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/profile/dao/proposals/${proposalId}`);
      setProposal(response.data);
    } catch (err) {
      console.error('Failed to load proposal:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/profile/dao/proposals/${proposalId}/comments`);
      setComments(response.data.comments);
    } catch (err) {
      console.error('Failed to load comments:', err);
    }
  };

  const handleVote = async (choice) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/profile/dao/proposals/${proposalId}/vote`,
        { choice, comment: '' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      alert('Vote recorded successfully!');
      setVotingOn(false);
      fetchProposal();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to vote');
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/profile/dao/proposals/${proposalId}/comments`,
        { comment_text: newComment },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setNewComment('');
      fetchComments();
    } catch (err) {
      alert('Failed to add comment: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-white">Loading proposal...</div>
      </div>
    );
  }

  if (!proposal) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Proposal Not Found</h2>
          <button
            onClick={() => navigate('/dao')}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Back to DAO
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Back Button */}
        <button
          onClick={() => navigate('/dao')}
          className="mb-6 text-gray-400 hover:text-white flex items-center gap-2"
        >
          ← Back to DAO
        </button>

        {/* Proposal Card */}
        <div className="bg-gray-800 rounded-xl p-8 mb-6 border border-purple-500/30">
          <div className="flex justify-between items-start mb-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-white mb-3">{proposal.title}</h1>
              <div className="flex items-center gap-4 text-sm">
                <span className={`px-3 py-1 rounded-full ${
                  proposal.status === 'open' ? 'bg-green-500/20 text-green-400' :
                  proposal.status === 'approved' ? 'bg-blue-500/20 text-blue-400' :
                  proposal.status === 'rejected' ? 'bg-red-500/20 text-red-400' :
                  'bg-gray-500/20 text-gray-400'
                }`}>
                  {proposal.status}
                </span>
                <span className="text-gray-400">
                  {proposal.type?.replace('_', ' ').toUpperCase()}
                </span>
                <span className="text-gray-500">
                  Created {new Date(proposal.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          <p className="text-gray-300 mb-6 text-lg leading-relaxed">{proposal.description}</p>

          {/* Vote Stats */}
          <div className="bg-gray-900 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-white mb-4">Voting Results</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400">{proposal.votes.yes}</div>
                <div className="text-sm text-gray-400">Yes</div>
                <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{width: `${proposal.votes.total > 0 ? (proposal.votes.yes / proposal.votes.total) * 100 : 0}%`}}
                  ></div>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-400">{proposal.votes.no}</div>
                <div className="text-sm text-gray-400">No</div>
                <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                  <div 
                    className="bg-red-500 h-2 rounded-full" 
                    style={{width: `${proposal.votes.total > 0 ? (proposal.votes.no / proposal.votes.total) * 100 : 0}%`}}
                  ></div>
                </div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-400">{proposal.votes.total}</div>
                <div className="text-sm text-gray-400">Total Votes</div>
              </div>
            </div>
          </div>

          {/* Voting Buttons */}
          {proposal.status === 'open' && (
            <div>
              {votingOn ? (
                <div className="flex gap-3">
                  <button
                    onClick={() => handleVote('yes')}
                    className="flex-1 px-4 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
                  >
                    ✓ Vote Yes
                  </button>
                  <button
                    onClick={() => handleVote('no')}
                    className="flex-1 px-4 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
                  >
                    ✗ Vote No
                  </button>
                  <button
                    onClick={() => handleVote('abstain')}
                    className="flex-1 px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-lg transition-colors"
                  >
                    ― Abstain
                  </button>
                  <button
                    onClick={() => setVotingOn(false)}
                    className="px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setVotingOn(true)}
                  className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors"
                >
                  Cast Your Vote
                </button>
              )}
            </div>
          )}
        </div>

        {/* Discussion Section */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-6">Discussion ({comments.length})</h2>

          {/* Add Comment Form */}
          <form onSubmit={handleAddComment} className="mb-6">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 mb-3"
              rows="3"
              placeholder="Add your thoughts to the discussion..."
              required
            />
            <button
              type="submit"
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors"
            >
              Post Comment
            </button>
          </form>

          {/* Comments List */}
          <div className="space-y-4">
            {comments.length > 0 ? (
              comments.map((comment) => (
                <div key={comment.id} className="bg-gray-900 rounded-lg p-4 border-l-4 border-purple-500">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0">
                      {comment.author.avatarUrl ? (
                        <img
                          src={comment.author.avatarUrl}
                          alt={comment.author.displayName}
                          className="w-10 h-10 rounded-full"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">
                          {comment.author.displayName?.charAt(0) || 'U'}
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-white">{comment.author.displayName}</span>
                        <span className="text-sm text-gray-500">
                          @{comment.author.username}
                        </span>
                        <span className="text-sm text-gray-500">•</span>
                        <span className="text-sm text-gray-500">
                          {new Date(comment.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-gray-300">{comment.text}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <button className="text-sm text-gray-400 hover:text-purple-400 flex items-center gap-1">
                          ❤️ {comment.likes}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                No comments yet. Be the first to share your thoughts!
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProposalDetail;