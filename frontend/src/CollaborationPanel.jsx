import React, { useState, useEffect, useRef } from 'react';
import { toast } from 'sonner';
import {
  Users, MessageCircle, Clock, Activity, ChevronDown, ChevronRight,
  Check, Send, RotateCcw, Eye, Circle
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// ==================== Collaboration Panel ====================
export const CollaborationPanel = ({ projectId, onVersionRestore }) => {
  const [activeSection, setActiveSection] = useState('presence');
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [versions, setVersions] = useState([]);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!projectId) return;
    fetchCollabData();
    connectWebSocket();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [projectId]);

  const connectWebSocket = () => {
    try {
      const wsUrl = API.replace('https://', 'wss://').replace('http://', 'ws://');
      const ws = new WebSocket(`${wsUrl}/api/creative-studio/collab/ws/${projectId}?user_id=user_001&user_name=You`);
      ws.onopen = () => {
        console.log('Collaboration WS connected');
      };
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWSMessage(data);
      };
      ws.onerror = () => {};
      ws.onclose = () => {};
      wsRef.current = ws;
    } catch (e) {
      console.log('WS connection failed, using REST fallback');
    }
  };

  const handleWSMessage = (data) => {
    switch (data.type) {
      case 'presence_state':
      case 'user_joined':
      case 'user_left':
        setOnlineUsers(data.active_users || []);
        break;
      case 'activity':
        setActivities(prev => [data, ...prev].slice(0, 50));
        break;
      case 'comment_added':
        setComments(prev => [...prev, data.comment]);
        break;
      case 'comment_resolved':
        setComments(prev => prev.map(c =>
          c.id === data.comment_id ? { ...c, is_resolved: true } : c
        ));
        break;
      default:
        break;
    }
  };

  const fetchCollabData = async () => {
    setLoading(true);
    try {
      const [actRes, verRes, comRes] = await Promise.all([
        fetch(`${API}/api/creative-studio/collab/activity/${projectId}`),
        fetch(`${API}/api/creative-studio/collab/versions/${projectId}`),
        fetch(`${API}/api/creative-studio/collab/comments/${projectId}`)
      ]);
      if (actRes.ok) { const d = await actRes.json(); setActivities(d.activities || []); }
      if (verRes.ok) { const d = await verRes.json(); setVersions(d.versions || []); }
      if (comRes.ok) { const d = await comRes.json(); setComments(d.comments || []); }
    } catch (e) {
      console.error('Failed to fetch collab data:', e);
    }
    setLoading(false);
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    try {
      const res = await fetch(`${API}/api/creative-studio/collab/comments/${projectId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: newComment, user_id: 'user_001', user_name: 'You' })
      });
      if (res.ok) {
        const comment = await res.json();
        setComments(prev => [...prev, comment]);
        setNewComment('');
        toast.success('Comment added');
      }
    } catch (e) {
      toast.error('Failed to add comment');
    }
  };

  const handleResolveComment = async (commentId) => {
    try {
      const res = await fetch(`${API}/api/creative-studio/collab/comments/${projectId}/${commentId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'user_001' })
      });
      if (res.ok) {
        setComments(prev => prev.map(c => c.id === commentId ? { ...c, is_resolved: true } : c));
        toast.success('Comment resolved');
      }
    } catch (e) {
      toast.error('Failed to resolve comment');
    }
  };

  const handleRestoreVersion = async (versionId) => {
    try {
      const res = await fetch(`${API}/api/creative-studio/collab/versions/${projectId}/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ version_id: versionId, user_id: 'user_001' })
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`Restored to version ${data.version_number}`);
        if (onVersionRestore && data.elements) {
          onVersionRestore(data.elements);
        }
        fetchCollabData();
      }
    } catch (e) {
      toast.error('Failed to restore version');
    }
  };

  const sections = [
    { id: 'presence', label: 'Online', icon: Users, count: onlineUsers.length },
    { id: 'comments', label: 'Comments', icon: MessageCircle, count: comments.filter(c => !c.is_resolved).length },
    { id: 'versions', label: 'Versions', icon: Clock, count: versions.length },
    { id: 'activity', label: 'Activity', icon: Activity, count: activities.length }
  ];

  return (
    <div className="flex flex-col h-full" data-testid="collaboration-panel">
      {/* Section Tabs */}
      <div className="flex border-b border-slate-700/50">
        {sections.map(s => (
          <button
            key={s.id}
            data-testid={`collab-tab-${s.id}`}
            onClick={() => setActiveSection(s.id)}
            className={`flex-1 py-2 px-1 text-[10px] font-medium flex flex-col items-center gap-0.5 transition-colors
              ${activeSection === s.id ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-500 hover:text-gray-300'}`}
          >
            <s.icon size={14} />
            <span>{s.label}</span>
            {s.count > 0 && (
              <span className={`text-[9px] px-1.5 rounded-full ${activeSection === s.id ? 'bg-purple-500/30 text-purple-300' : 'bg-slate-700 text-gray-400'}`}>
                {s.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {loading && <div className="text-center text-gray-500 text-xs py-4">Loading...</div>}

        {/* Online Users */}
        {activeSection === 'presence' && (
          <div data-testid="presence-section">
            <p className="text-gray-400 text-[10px] uppercase font-bold mb-2">Currently Editing</p>
            {onlineUsers.length === 0 && (
              <div className="text-center py-4">
                <Users size={20} className="text-gray-600 mx-auto mb-1" />
                <p className="text-gray-500 text-xs">Only you are here</p>
                <p className="text-gray-600 text-[10px]">Share project to collaborate</p>
              </div>
            )}
            {onlineUsers.map((user, i) => (
              <div key={user.user_id || i} className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-700/30" data-testid={`online-user-${i}`}>
                <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold"
                     style={{ backgroundColor: user.color || '#8b5cf6' }}>
                  {(user.name || 'U')[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-xs truncate">{user.name || 'Unknown'}</p>
                  <p className="text-gray-500 text-[10px]">Active now</p>
                </div>
                <Circle size={8} className="text-green-400 fill-green-400" />
              </div>
            ))}
            {/* Self indicator */}
            <div className="flex items-center gap-2 p-2 rounded-lg bg-purple-500/10 border border-purple-500/20">
              <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center text-white text-xs font-bold">Y</div>
              <div className="flex-1">
                <p className="text-purple-300 text-xs">You</p>
                <p className="text-purple-400/50 text-[10px]">Currently editing</p>
              </div>
              <Circle size={8} className="text-green-400 fill-green-400" />
            </div>
          </div>
        )}

        {/* Comments */}
        {activeSection === 'comments' && (
          <div data-testid="comments-section">
            <div className="space-y-2 mb-3">
              {comments.length === 0 && (
                <div className="text-center py-4">
                  <MessageCircle size={20} className="text-gray-600 mx-auto mb-1" />
                  <p className="text-gray-500 text-xs">No comments yet</p>
                </div>
              )}
              {comments.map((c, i) => (
                <div key={c.id || i} className={`p-2 rounded-lg border ${c.is_resolved ? 'bg-green-500/5 border-green-500/20 opacity-60' : 'bg-slate-700/30 border-slate-600/30'}`}
                     data-testid={`comment-${i}`}>
                  <div className="flex items-center gap-1.5 mb-1">
                    <div className="w-5 h-5 rounded-full bg-blue-600 flex items-center justify-center text-white text-[9px] font-bold">
                      {(c.user_name || 'U')[0].toUpperCase()}
                    </div>
                    <span className="text-gray-300 text-[10px] font-medium">{c.user_name || 'User'}</span>
                    {c.is_resolved && <Check size={10} className="text-green-400 ml-auto" />}
                  </div>
                  <p className="text-gray-200 text-xs leading-relaxed">{c.content}</p>
                  {!c.is_resolved && (
                    <button onClick={() => handleResolveComment(c.id)}
                            className="mt-1.5 text-[10px] text-purple-400 hover:text-purple-300" data-testid={`resolve-comment-${i}`}>
                      Resolve
                    </button>
                  )}
                </div>
              ))}
            </div>
            {/* Add Comment */}
            <div className="flex gap-1.5 mt-2">
              <input value={newComment} onChange={e => setNewComment(e.target.value)}
                     onKeyDown={e => e.key === 'Enter' && handleAddComment()}
                     placeholder="Add a comment..."
                     className="flex-1 bg-slate-700 text-white text-xs rounded px-2 py-1.5 border border-slate-600 focus:border-purple-500 outline-none"
                     data-testid="comment-input" />
              <button onClick={handleAddComment} disabled={!newComment.trim()}
                      className="bg-purple-600 text-white p-1.5 rounded hover:bg-purple-500 disabled:opacity-40"
                      data-testid="add-comment-btn">
                <Send size={12} />
              </button>
            </div>
          </div>
        )}

        {/* Version History */}
        {activeSection === 'versions' && (
          <div data-testid="versions-section">
            <p className="text-gray-400 text-[10px] uppercase font-bold mb-2">Version History</p>
            {versions.length === 0 && (
              <div className="text-center py-4">
                <Clock size={20} className="text-gray-600 mx-auto mb-1" />
                <p className="text-gray-500 text-xs">No saved versions</p>
                <p className="text-gray-600 text-[10px]">Save a version to track changes</p>
              </div>
            )}
            {versions.map((v, i) => (
              <div key={v.id || i} className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-700/30 group border border-transparent hover:border-slate-600/30"
                   data-testid={`version-${i}`}>
                <div className="w-7 h-7 rounded bg-slate-700 flex items-center justify-center text-purple-400 text-[10px] font-bold">
                  v{v.version_number}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-gray-200 text-xs truncate">{v.name || `Version ${v.version_number}`}</p>
                  <p className="text-gray-500 text-[10px]">
                    {v.created_at ? new Date(v.created_at).toLocaleDateString() : 'Unknown date'}
                  </p>
                </div>
                <button onClick={() => handleRestoreVersion(v.id)}
                        className="opacity-0 group-hover:opacity-100 text-[10px] text-purple-400 hover:text-purple-300 flex items-center gap-0.5 transition-opacity"
                        data-testid={`restore-version-${i}`}>
                  <RotateCcw size={10} /> Restore
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Activity Feed */}
        {activeSection === 'activity' && (
          <div data-testid="activity-section">
            <p className="text-gray-400 text-[10px] uppercase font-bold mb-2">Recent Activity</p>
            {activities.length === 0 && (
              <div className="text-center py-4">
                <Activity size={20} className="text-gray-600 mx-auto mb-1" />
                <p className="text-gray-500 text-xs">No activity yet</p>
              </div>
            )}
            {activities.map((a, i) => (
              <div key={a.id || i} className="flex items-start gap-2 p-1.5 rounded hover:bg-slate-700/20" data-testid={`activity-${i}`}>
                <div className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-1.5 shrink-0" />
                <div>
                  <p className="text-gray-300 text-[11px]">
                    <span className="text-purple-300 font-medium">{a.user_name || 'User'}</span>
                    {' '}{formatAction(a.action)}
                  </p>
                  <p className="text-gray-600 text-[9px]">
                    {a.created_at ? timeAgo(a.created_at) : ''}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

function formatAction(action) {
  const map = {
    'comment_added': 'added a comment',
    'version_restored': 'restored a version',
    'element_added': 'added an element',
    'element_updated': 'updated an element',
    'element_deleted': 'deleted an element',
    'project_saved': 'saved the project',
    'collaborator_added': 'added a collaborator'
  };
  return map[action] || action?.replace(/_/g, ' ') || 'performed an action';
}

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default CollaborationPanel;
