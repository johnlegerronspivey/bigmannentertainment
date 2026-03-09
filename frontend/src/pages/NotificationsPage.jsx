import React, { useState, useEffect, useCallback } from "react";
import { api } from "../utils/apiClient";
import { toast } from "sonner";
import { Bell, Check, CheckCheck, Trash2, MessageSquare, CreditCard, Filter, MessageCircle } from "lucide-react";

function NotificationsPage() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filterUnread, setFilterUnread] = useState(false);
  const [page, setPage] = useState(0);
  const limit = 20;

  const load = useCallback(async () => {
    try {
      const data = await api.get(`/notifications?skip=${page * limit}&limit=${limit}${filterUnread ? "&unread_only=true" : ""}`);
      setItems(data.items || []);
      setTotal(data.total || 0);
      setUnread(data.unread || 0);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [page, filterUnread]);

  useEffect(() => { load(); }, [load]);

  const markRead = async (id) => {
    try {
      await api.put(`/notifications/${id}/read`);
      setItems((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
      setUnread((prev) => Math.max(0, prev - 1));
    } catch (err) {
      toast.error("Failed to mark as read");
    }
  };

  const markAllRead = async () => {
    try {
      await api.put("/notifications/read-all");
      setItems((prev) => prev.map((n) => ({ ...n, read: true })));
      setUnread(0);
      toast.success("All marked as read");
    } catch (err) {
      toast.error("Failed to mark all as read");
    }
  };

  const deleteNotif = async (id) => {
    try {
      await api.delete(`/notifications/${id}`);
      const removed = items.find((n) => n.id === id);
      setItems((prev) => prev.filter((n) => n.id !== id));
      setTotal((prev) => prev - 1);
      if (removed && !removed.read) setUnread((prev) => Math.max(0, prev - 1));
      toast.success("Notification deleted");
    } catch (err) {
      toast.error("Delete failed");
    }
  };

  const typeIcon = (type) => {
    if (type === "new_message") return <MessageSquare className="w-5 h-5 text-blue-400" />;
    if (type === "new_subscriber") return <CreditCard className="w-5 h-5 text-green-400" />;
    if (type === "new_comment") return <MessageCircle className="w-5 h-5 text-amber-400" />;
    return <Bell className="w-5 h-5 text-purple-400" />;
  };

  const formatDate = (iso) => {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" });
  };

  const totalPages = Math.ceil(total / limit);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="notifications-page">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold" data-testid="notifications-page-title">Notifications</h1>
            <p className="text-gray-400 mt-1">{unread} unread of {total} total</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => { setFilterUnread(!filterUnread); setPage(0); }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filterUnread ? "bg-purple-600 text-white" : "bg-gray-800 text-gray-300 hover:bg-gray-700"}`}
              data-testid="filter-unread-btn"
            >
              <Filter className="w-4 h-4" /> {filterUnread ? "Show All" : "Unread Only"}
            </button>
            {unread > 0 && (
              <button
                onClick={markAllRead}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium"
                data-testid="mark-all-read-page-btn"
              >
                <CheckCheck className="w-4 h-4" /> Mark All Read
              </button>
            )}
          </div>
        </div>

        {items.length === 0 ? (
          <div className="text-center py-20" data-testid="notifications-empty">
            <Bell className="w-14 h-14 text-gray-700 mx-auto mb-4" />
            <p className="text-gray-500">{filterUnread ? "No unread notifications" : "No notifications yet"}</p>
          </div>
        ) : (
          <div className="space-y-2" data-testid="notifications-list">
            {items.map((n) => (
              <div
                key={n.id}
                className={`flex items-start gap-4 p-4 rounded-xl border transition-colors ${!n.read ? "bg-purple-500/5 border-purple-500/20" : "bg-gray-900 border-gray-800"}`}
                data-testid="notification-page-item"
              >
                <div className="mt-1 shrink-0">{typeIcon(n.type)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className={`text-sm ${!n.read ? "text-white font-semibold" : "text-gray-300"}`}>{n.title}</p>
                    {!n.read && <span className="w-2 h-2 bg-purple-500 rounded-full shrink-0" />}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{n.message}</p>
                  {n.sender_name && <p className="text-xs text-gray-600 mt-1">From: {n.sender_name}</p>}
                  <p className="text-xs text-gray-600 mt-1">{formatDate(n.created_at)}</p>
                </div>
                <div className="flex gap-1 shrink-0">
                  {!n.read && (
                    <button
                      onClick={() => markRead(n.id)}
                      className="p-2 text-gray-500 hover:text-green-400 rounded-lg hover:bg-gray-800"
                      title="Mark as read"
                      data-testid="page-mark-read-btn"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => deleteNotif(n.id)}
                    className="p-2 text-gray-500 hover:text-red-400 rounded-lg hover:bg-gray-800"
                    title="Delete"
                    data-testid="page-delete-notification-btn"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-3 mt-8" data-testid="notifications-pagination">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 rounded-lg text-sm"
            >
              Previous
            </button>
            <span className="text-sm text-gray-400">Page {page + 1} of {totalPages}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 rounded-lg text-sm"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default NotificationsPage;
