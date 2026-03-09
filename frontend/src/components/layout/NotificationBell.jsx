import React, { useState, useEffect, useRef, useCallback } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { api } from "../../utils/apiClient";
import { Bell, Check, CheckCheck, Trash2, MessageSquare, CreditCard, X } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function NotificationBell() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const ref = useRef(null);
  const wsRef = useRef(null);

  const fetchNotifications = useCallback(async () => {
    try {
      const data = await api.get("/notifications?limit=10");
      setItems(data.items || []);
      setUnread(data.unread || 0);
    } catch {
      /* ignore */
    }
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Initial fetch + poll every 30s
  useEffect(() => {
    if (!user) return;
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [user, fetchNotifications]);

  // WebSocket for real-time push
  useEffect(() => {
    if (!user) return;
    const userId = user.id || user.user_id;
    if (!userId) return;
    const wsUrl = BACKEND_URL.replace(/^http/, "ws") + `/api/ws/notifications?user_id=${userId}`;
    let ws;
    try {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          if (data.type === "new_notification" && data.notification) {
            setItems((prev) => [data.notification, ...prev].slice(0, 10));
            setUnread((prev) => prev + 1);
          }
        } catch {
          /* ignore */
        }
      };
      ws.onclose = () => {};
      wsRef.current = ws;
    } catch {
      /* ignore */
    }
    return () => {
      if (ws) ws.close();
    };
  }, [user]);

  const markRead = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      setItems((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
      setUnread((prev) => Math.max(0, prev - 1));
    } catch {
      /* ignore */
    }
  };

  const markAllRead = async () => {
    try {
      await api.put("/notifications/read-all");
      setItems((prev) => prev.map((n) => ({ ...n, read: true })));
      setUnread(0);
    } catch {
      /* ignore */
    }
  };

  const deleteNotif = async (id) => {
    try {
      await api.delete(`/notifications/${id}`);
      const removed = items.find((n) => n.id === id);
      setItems((prev) => prev.filter((n) => n.id !== id));
      if (removed && !removed.read) setUnread((prev) => Math.max(0, prev - 1));
    } catch {
      /* ignore */
    }
  };

  const typeIcon = (type) => {
    if (type === "new_message") return <MessageSquare className="w-4 h-4 text-blue-400" />;
    if (type === "new_subscriber") return <CreditCard className="w-4 h-4 text-green-400" />;
    return <Bell className="w-4 h-4 text-purple-400" />;
  };

  const timeAgo = (iso) => {
    if (!iso) return "";
    const diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  if (!user) return null;

  return (
    <div className="relative" ref={ref} data-testid="notification-bell-wrapper">
      <button
        onClick={() => { setOpen(!open); if (!open) fetchNotifications(); }}
        className="relative p-1.5 rounded-lg hover:bg-purple-700/50 transition-colors"
        data-testid="notification-bell-btn"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unread > 0 && (
          <span
            className="absolute -top-0.5 -right-0.5 flex items-center justify-center w-4.5 h-4.5 min-w-[18px] px-1 text-[10px] font-bold bg-red-500 text-white rounded-full leading-none"
            data-testid="notification-unread-badge"
          >
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl z-50 overflow-hidden" data-testid="notification-dropdown">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
            <h3 className="text-sm font-semibold text-white">Notifications</h3>
            <div className="flex items-center gap-2">
              {unread > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1"
                  data-testid="mark-all-read-btn"
                >
                  <CheckCheck className="w-3.5 h-3.5" /> Mark all read
                </button>
              )}
              <button onClick={() => setOpen(false)} className="text-gray-500 hover:text-gray-300">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* List */}
          <div className="max-h-80 overflow-y-auto" data-testid="notification-list">
            {items.length === 0 ? (
              <div className="py-10 text-center text-gray-500 text-sm" data-testid="notification-empty">
                No notifications yet
              </div>
            ) : (
              items.map((n) => (
                <div
                  key={n.id}
                  className={`flex items-start gap-3 px-4 py-3 border-b border-gray-800/50 hover:bg-gray-800/40 transition-colors ${!n.read ? "bg-purple-500/5" : ""}`}
                  data-testid="notification-item"
                >
                  <div className="mt-0.5">{typeIcon(n.type)}</div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm leading-snug ${!n.read ? "text-white font-medium" : "text-gray-400"}`}>
                      {n.title}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5 truncate">{n.message}</p>
                    <p className="text-[10px] text-gray-600 mt-1">{timeAgo(n.created_at)}</p>
                  </div>
                  <div className="flex gap-1 shrink-0">
                    {!n.read && (
                      <button
                        onClick={() => markRead(n.id)}
                        className="p-1 text-gray-600 hover:text-green-400"
                        title="Mark as read"
                        data-testid="mark-read-btn"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button
                      onClick={() => deleteNotif(n.id)}
                      className="p-1 text-gray-600 hover:text-red-400"
                      title="Delete"
                      data-testid="delete-notification-btn"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <Link
            to="/notifications"
            onClick={() => setOpen(false)}
            className="block text-center text-xs text-purple-400 hover:text-purple-300 py-2.5 border-t border-gray-800"
            data-testid="view-all-notifications-link"
          >
            View all notifications
          </Link>
        </div>
      )}
    </div>
  );
}

export default NotificationBell;
