import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { RefreshCw, MessageSquare, Send, ArrowLeft, Circle, Inbox } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const getToken = () => localStorage.getItem('token');

const api = async (path, opts = {}) => {
  const res = await fetch(`${API}/api/uln-enhanced${path}`, {
    ...opts,
    headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json', ...opts.headers },
  });
  return res.json();
};

export const InterLabelMessaging = () => {
  const [labels, setLabels] = useState([]);
  const [selectedLabel, setSelectedLabel] = useState(null);
  const [threads, setThreads] = useState([]);
  const [activeThread, setActiveThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMsg, setNewMsg] = useState('');
  const [sending, setSending] = useState(false);
  const [showNewThread, setShowNewThread] = useState(false);
  const [newThread, setNewThread] = useState({ recipient: '', subject: '' });
  const [loading, setLoading] = useState(true);

  // Fetch labels for selection
  useEffect(() => {
    (async () => {
      const res = await fetch(`${API}/api/uln/labels/directory`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      const data = await res.json();
      if (data.success) setLabels(data.labels || data.label_hub_entries || []);
      setLoading(false);
    })();
  }, []);

  const loadThreads = useCallback(async (labelId) => {
    if (!labelId) return;
    const data = await api(`/messaging/threads?label_id=${labelId}`);
    setThreads(data.threads || []);
  }, []);

  const openThread = async (threadId) => {
    const data = await api(`/messaging/threads/${threadId}`);
    if (data.success) {
      setActiveThread(data.thread);
      setMessages(data.messages || []);
      // Mark as read
      if (selectedLabel) await api(`/messaging/threads/${threadId}/read?label_id=${selectedLabel}`, { method: 'PUT' });
    }
  };

  const sendMessage = async () => {
    if (!newMsg.trim() || !activeThread || !selectedLabel) return;
    setSending(true);
    const label = labels.find((l) => l.global_id === selectedLabel);
    await api('/messaging/messages', {
      method: 'POST',
      body: JSON.stringify({ thread_id: activeThread.thread_id, sender_label_id: selectedLabel, sender_name: label?.name || selectedLabel, content: newMsg }),
    });
    setNewMsg('');
    await openThread(activeThread.thread_id);
    setSending(false);
  };

  const createThread = async () => {
    if (!newThread.recipient || !newThread.subject || !selectedLabel) return;
    const res = await api('/messaging/threads', {
      method: 'POST',
      body: JSON.stringify({ sender_label_id: selectedLabel, recipient_label_id: newThread.recipient, subject: newThread.subject }),
    });
    if (res.success) {
      setShowNewThread(false);
      setNewThread({ recipient: '', subject: '' });
      await loadThreads(selectedLabel);
    }
  };

  const selectLabel = (labelId) => {
    setSelectedLabel(labelId);
    setActiveThread(null);
    setMessages([]);
    loadThreads(labelId);
  };

  if (loading) return <div className="flex justify-center py-16"><RefreshCw className="w-8 h-8 animate-spin text-violet-500" /></div>;

  // Label selector
  if (!selectedLabel) {
    return (
      <div data-testid="messaging-label-select">
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Select Your Label</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-slate-400 mb-4">Choose which label you want to message as:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[400px] overflow-y-auto">
              {labels.map((l) => (
                <button key={l.global_id} onClick={() => selectLabel(l.global_id)}
                  className="p-3 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-left transition-colors" data-testid={`label-select-${l.global_id}`}>
                  <p className="text-white font-medium text-sm">{l.name}</p>
                  <p className="text-xs text-slate-400">{l.label_type} | {l.territory}</p>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Thread view (active conversation)
  if (activeThread) {
    return (
      <div data-testid="messaging-thread-view">
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" onClick={() => { setActiveThread(null); setMessages([]); loadThreads(selectedLabel); }} className="text-slate-400 hover:text-white p-1">
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <CardTitle className="text-white text-base">{activeThread.subject}</CardTitle>
                <p className="text-xs text-slate-400">{activeThread.participants?.join(' & ')}</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Messages */}
            <div className="space-y-3 max-h-[400px] overflow-y-auto mb-4 p-2">
              {messages.map((m) => (
                <div key={m.message_id} className={`flex ${m.sender_label_id === selectedLabel ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] p-3 rounded-lg ${m.sender_label_id === selectedLabel ? 'bg-violet-600 text-white' : 'bg-slate-700 text-slate-200'}`}>
                    <p className="text-xs opacity-70 mb-1">{m.sender_name}</p>
                    <p className="text-sm">{m.content}</p>
                    <p className="text-[10px] opacity-50 mt-1">{new Date(m.timestamp).toLocaleTimeString()}</p>
                  </div>
                </div>
              ))}
              {messages.length === 0 && <p className="text-center text-slate-500 text-sm py-8">No messages yet. Start the conversation!</p>}
            </div>
            {/* Input */}
            <div className="flex gap-2">
              <Input placeholder="Type a message..." value={newMsg} onChange={(e) => setNewMsg(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                className="bg-slate-700 border-slate-600 text-white" data-testid="message-input" />
              <Button onClick={sendMessage} disabled={sending || !newMsg.trim()} className="bg-violet-600 hover:bg-violet-700" data-testid="send-message-btn">
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Thread list
  const currentLabel = labels.find((l) => l.global_id === selectedLabel);
  return (
    <div data-testid="messaging-threads-list">
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-white text-base">
                <MessageSquare className="w-4 h-4 inline mr-2" />Messages — {currentLabel?.name}
              </CardTitle>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => selectLabel(null)} className="border-slate-600 text-slate-300 hover:bg-slate-700 text-xs">Switch Label</Button>
              <Button size="sm" onClick={() => setShowNewThread(true)} className="bg-violet-600 hover:bg-violet-700 text-xs" data-testid="new-thread-btn">New Thread</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* New thread form */}
          {showNewThread && (
            <div className="mb-4 p-4 rounded-lg bg-slate-700/50 space-y-3">
              <p className="text-sm text-slate-300 font-medium">New Conversation</p>
              <select value={newThread.recipient} onChange={(e) => setNewThread({ ...newThread, recipient: e.target.value })} className="w-full bg-slate-700 border border-slate-600 text-white rounded px-3 py-2 text-sm">
                <option value="">Select recipient label...</option>
                {labels.filter((l) => l.global_id !== selectedLabel).map((l) => (
                  <option key={l.global_id} value={l.global_id}>{l.name}</option>
                ))}
              </select>
              <Input placeholder="Subject" value={newThread.subject} onChange={(e) => setNewThread({ ...newThread, subject: e.target.value })} className="bg-slate-700 border-slate-600 text-white" />
              <div className="flex gap-2">
                <Button onClick={createThread} className="bg-violet-600 hover:bg-violet-700" data-testid="create-thread-btn">Create</Button>
                <Button variant="outline" onClick={() => setShowNewThread(false)} className="border-slate-600 text-slate-300 hover:bg-slate-700">Cancel</Button>
              </div>
            </div>
          )}

          {/* Thread list */}
          <div className="space-y-2">
            {threads.map((t) => (
              <button key={t.thread_id} onClick={() => openThread(t.thread_id)}
                className="w-full p-3 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-left transition-colors flex items-start gap-3">
                <MessageSquare className="w-5 h-5 text-violet-400 mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center">
                    <p className="text-white font-medium text-sm truncate">{t.subject}</p>
                    {t.unread_count > 0 && <span className="ml-2 px-2 py-0.5 text-xs bg-violet-600 text-white rounded-full">{t.unread_count}</span>}
                  </div>
                  <p className="text-xs text-slate-400 truncate mt-0.5">{t.last_message_preview || 'No messages yet'}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">{t.message_count} messages</p>
                </div>
              </button>
            ))}
            {threads.length === 0 && !showNewThread && (
              <div className="text-center py-8">
                <Inbox className="w-10 h-10 text-slate-600 mx-auto mb-2" />
                <p className="text-slate-500 text-sm">No conversations yet</p>
                <Button size="sm" onClick={() => setShowNewThread(true)} className="mt-2 bg-violet-600 hover:bg-violet-700 text-xs">Start a Conversation</Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
