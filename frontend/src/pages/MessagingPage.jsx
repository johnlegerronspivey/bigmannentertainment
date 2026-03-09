import React, { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../utils/apiClient";
import { toast } from "sonner";
import { MessageCircle, Send, ArrowLeft, Search, Check, CheckCheck, Trash2, Users } from "lucide-react";

function MessagingPage() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageText, setMessageText] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [searchUsers, setSearchUsers] = useState("");
  const [userResults, setUserResults] = useState([]);
  const [showNewChat, setShowNewChat] = useState(false);
  const [otherUser, setOtherUser] = useState(null);
  const messagesEndRef = useRef(null);

  const userId = user?.id;

  const loadConversations = useCallback(async () => {
    try {
      const data = await api.get("/messages/conversations");
      setConversations(data.conversations || []);
    } catch {
      setConversations([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadConversations(); }, [loadConversations]);

  const openConversation = async (otherUserId, otherUserInfo) => {
    setSelectedUserId(otherUserId);
    setOtherUser(otherUserInfo);
    setShowNewChat(false);
    try {
      const data = await api.get(`/messages/conversation/${otherUserId}`);
      setMessages(data.messages || []);
      // Mark as read
      await api.put(`/messages/read/${otherUserId}`, {});
      loadConversations();
    } catch {
      setMessages([]);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Poll for new messages when in conversation
  useEffect(() => {
    if (!selectedUserId) return;
    const interval = setInterval(async () => {
      try {
        const data = await api.get(`/messages/conversation/${selectedUserId}`);
        setMessages(data.messages || []);
      } catch { /* ignore */ }
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedUserId]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!messageText.trim() || !selectedUserId) return;
    setSending(true);
    try {
      await api.post("/messages/send", { recipient_id: selectedUserId, content: messageText.trim() });
      setMessageText("");
      const data = await api.get(`/messages/conversation/${selectedUserId}`);
      setMessages(data.messages || []);
      loadConversations();
    } catch (err) {
      toast.error(err.message || "Failed to send");
    } finally {
      setSending(false);
    }
  };

  const handleDeleteMessage = async (msgId) => {
    try {
      await api.delete(`/messages/${msgId}`);
      setMessages((prev) => prev.filter((m) => m.id !== msgId));
      toast.success("Message deleted");
    } catch (err) {
      toast.error(err.message || "Cannot delete");
    }
  };

  const searchForUsers = async () => {
    if (!searchUsers.trim()) return;
    try {
      const data = await api.get(`/creator-profiles/browse?search=${encodeURIComponent(searchUsers)}`);
      setUserResults((data.profiles || []).filter((p) => p.user_id !== userId));
    } catch {
      setUserResults([]);
    }
  };

  const startChatWithUser = (profile) => {
    openConversation(profile.user_id, { user_id: profile.user_id, name: profile.display_name || profile.username });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="messaging-page">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold" data-testid="messaging-page-title">Messages</h1>
            <p className="text-gray-400 mt-1">Direct conversations with creators and users</p>
          </div>
          <button
            onClick={() => { setShowNewChat(!showNewChat); setSelectedUserId(null); }}
            className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium transition-colors"
            data-testid="new-chat-btn"
          >
            <MessageCircle className="w-4 h-4" /> New Conversation
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar: Conversations */}
          <div className="lg:col-span-1 bg-gray-900 border border-gray-800 rounded-xl overflow-hidden" data-testid="conversation-list">
            <div className="p-4 border-b border-gray-800">
              <h2 className="font-semibold text-sm text-gray-300">Conversations</h2>
            </div>
            <div className="max-h-[600px] overflow-y-auto">
              {conversations.length === 0 && (
                <div className="p-6 text-center text-gray-500 text-sm" data-testid="no-conversations">
                  <Users className="w-8 h-8 mx-auto mb-2 text-gray-700" />
                  No conversations yet
                </div>
              )}
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => openConversation(conv.other_user?.user_id, conv.other_user)}
                  className={`w-full text-left px-4 py-3.5 border-b border-gray-800/50 hover:bg-gray-800/50 transition-colors ${selectedUserId === conv.other_user?.user_id ? "bg-gray-800/70" : ""}`}
                  data-testid="conversation-item"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-sm font-bold flex-shrink-0">
                        {(conv.other_user?.name || "?")[0].toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-sm truncate">{conv.other_user?.name || "Unknown"}</p>
                        <p className="text-xs text-gray-500 truncate">{conv.last_message || ""}</p>
                      </div>
                    </div>
                    {conv.my_unread > 0 && (
                      <span className="bg-purple-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0" data-testid="unread-badge">
                        {conv.my_unread}
                      </span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Main: Chat or New Chat */}
          <div className="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl flex flex-col" style={{ minHeight: 500 }}>
            {showNewChat && !selectedUserId ? (
              <div className="p-6" data-testid="new-chat-panel">
                <h2 className="font-semibold mb-4">Start a New Conversation</h2>
                <div className="flex gap-3 mb-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="text"
                      placeholder="Search creators by name..."
                      value={searchUsers}
                      onChange={(e) => setSearchUsers(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && searchForUsers()}
                      className="w-full pl-10 pr-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                      data-testid="user-search-input"
                    />
                  </div>
                  <button onClick={searchForUsers} className="px-4 py-2.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm" data-testid="user-search-btn">Search</button>
                </div>
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  {userResults.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => startChatWithUser(p)}
                      className="w-full text-left px-4 py-3 bg-gray-800/50 hover:bg-gray-800 rounded-lg flex items-center gap-3 transition-colors"
                      data-testid="user-result-item"
                    >
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-sm font-bold">
                        {(p.display_name || p.username || "?")[0].toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium text-sm">{p.display_name}</p>
                        <p className="text-xs text-gray-500">@{p.username}</p>
                      </div>
                    </button>
                  ))}
                  {userResults.length === 0 && searchUsers && <p className="text-gray-500 text-sm text-center py-4">No creators found</p>}
                </div>
              </div>
            ) : selectedUserId ? (
              <>
                {/* Chat Header */}
                <div className="flex items-center gap-3 p-4 border-b border-gray-800" data-testid="chat-header">
                  <button onClick={() => setSelectedUserId(null)} className="lg:hidden p-1 text-gray-400 hover:text-white">
                    <ArrowLeft className="w-5 h-5" />
                  </button>
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-sm font-bold">
                    {(otherUser?.name || "?")[0].toUpperCase()}
                  </div>
                  <p className="font-medium text-sm">{otherUser?.name || "User"}</p>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3" data-testid="messages-container">
                  {messages.length === 0 && (
                    <p className="text-center text-gray-600 text-sm py-8" data-testid="no-messages">No messages yet. Say hello!</p>
                  )}
                  {messages.map((msg) => {
                    const isMine = msg.sender_id === userId;
                    return (
                      <div key={msg.id} className={`flex ${isMine ? "justify-end" : "justify-start"}`} data-testid="message-bubble">
                        <div className={`max-w-[70%] px-4 py-2.5 rounded-2xl ${isMine ? "bg-purple-600 rounded-br-md" : "bg-gray-800 rounded-bl-md"}`}>
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                          <div className={`flex items-center gap-1 mt-1 ${isMine ? "justify-end" : "justify-start"}`}>
                            <span className="text-[10px] text-gray-400">
                              {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
                            </span>
                            {isMine && (msg.read ? <CheckCheck className="w-3 h-3 text-blue-400" /> : <Check className="w-3 h-3 text-gray-400" />)}
                            {isMine && (
                              <button onClick={() => handleDeleteMessage(msg.id)} className="ml-1 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-400">
                                <Trash2 className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <form onSubmit={handleSend} className="p-4 border-t border-gray-800 flex gap-3" data-testid="message-input-form">
                  <input
                    type="text"
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    placeholder="Type a message..."
                    className="flex-1 px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-full text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    data-testid="message-text-input"
                  />
                  <button
                    type="submit"
                    disabled={sending || !messageText.trim()}
                    className="w-10 h-10 flex items-center justify-center bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-full transition-colors"
                    data-testid="send-message-btn"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-600" data-testid="chat-placeholder">
                <div className="text-center">
                  <MessageCircle className="w-12 h-12 mx-auto mb-3 text-gray-700" />
                  <p className="text-sm">Select a conversation or start a new one</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MessagingPage;
