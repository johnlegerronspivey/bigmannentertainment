import React, { useState, useEffect, useCallback } from 'react';
import { Bell, Check, CheckCheck, Trash2, Filter, Settings, RefreshCw, ChevronDown, AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const TYPE_META = {
  member_added: { label: 'Member Added', icon: 'user-plus', color: 'text-blue-600 bg-blue-50' },
  member_removed: { label: 'Member Removed', icon: 'user-minus', color: 'text-red-600 bg-red-50' },
  governance_rule_created: { label: 'Governance', icon: 'shield', color: 'text-indigo-600 bg-indigo-50' },
  governance_rule_updated: { label: 'Governance', icon: 'shield', color: 'text-indigo-600 bg-indigo-50' },
  governance_rule_deleted: { label: 'Governance', icon: 'shield', color: 'text-red-600 bg-red-50' },
  dispute_filed: { label: 'Dispute', icon: 'alert-triangle', color: 'text-amber-600 bg-amber-50' },
  dispute_updated: { label: 'Dispute', icon: 'alert-triangle', color: 'text-amber-600 bg-amber-50' },
  dispute_resolved: { label: 'Resolved', icon: 'check-circle', color: 'text-emerald-600 bg-emerald-50' },
  catalog_asset_added: { label: 'Catalog', icon: 'music', color: 'text-purple-600 bg-purple-50' },
  distribution_updated: { label: 'Distribution', icon: 'share-2', color: 'text-cyan-600 bg-cyan-50' },
  royalty_payout: { label: 'Royalty', icon: 'dollar-sign', color: 'text-green-600 bg-green-50' },
  label_registered: { label: 'Label', icon: 'tag', color: 'text-violet-600 bg-violet-50' },
  system: { label: 'System', icon: 'info', color: 'text-gray-600 bg-gray-50' },
};

const SEVERITY_CONFIG = {
  info: { icon: Info, color: 'text-blue-500', bg: 'border-l-blue-400' },
  warning: { icon: AlertTriangle, color: 'text-amber-500', bg: 'border-l-amber-400' },
  success: { icon: CheckCircle, color: 'text-emerald-500', bg: 'border-l-emerald-400' },
  error: { icon: XCircle, color: 'text-red-500', bg: 'border-l-red-400' },
};

const ALL_TYPES = [
  'member_added', 'member_removed',
  'governance_rule_created', 'governance_rule_updated', 'governance_rule_deleted',
  'dispute_filed', 'dispute_updated', 'dispute_resolved',
  'catalog_asset_added', 'distribution_updated', 'royalty_payout',
  'label_registered', 'system',
];

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

const NotificationCard = ({ notif, onMarkRead, onDelete }) => {
  const typeMeta = TYPE_META[notif.type] || TYPE_META.system;
  const sevConfig = SEVERITY_CONFIG[notif.severity] || SEVERITY_CONFIG.info;
  const SevIcon = sevConfig.icon;

  return (
    <div
      data-testid={`notification-card-${notif.notification_id}`}
      className={`group relative border-l-4 ${sevConfig.bg} rounded-lg p-4 transition-all duration-200 ${
        notif.is_read
          ? 'bg-white opacity-70 hover:opacity-100'
          : 'bg-white shadow-sm hover:shadow-md'
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`shrink-0 mt-0.5 w-8 h-8 rounded-full flex items-center justify-center ${typeMeta.color}`}>
          <SevIcon className={`w-4 h-4 ${sevConfig.color}`} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full ${typeMeta.color}`}>
              {typeMeta.label}
            </span>
            {!notif.is_read && (
              <span className="w-2 h-2 rounded-full bg-purple-500 shrink-0" data-testid="unread-dot" />
            )}
            <span className="text-[11px] text-gray-400 ml-auto shrink-0">{timeAgo(notif.created_at)}</span>
          </div>

          <h4 className={`text-sm font-semibold ${notif.is_read ? 'text-gray-500' : 'text-gray-900'}`}>
            {notif.title}
          </h4>
          <p className={`text-xs mt-0.5 ${notif.is_read ? 'text-gray-400' : 'text-gray-600'}`}>
            {notif.message}
          </p>
        </div>

        {/* Actions */}
        <div className="shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {!notif.is_read && (
            <button
              onClick={() => onMarkRead(notif.notification_id)}
              className="p-1.5 rounded-md hover:bg-gray-100 text-gray-400 hover:text-gray-600"
              title="Mark as read"
              data-testid={`mark-read-${notif.notification_id}`}
            >
              <Check className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={() => onDelete(notif.notification_id)}
            className="p-1.5 rounded-md hover:bg-red-50 text-gray-400 hover:text-red-500"
            title="Delete"
            data-testid={`delete-notif-${notif.notification_id}`}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};


export const ULNNotifications = ({ activeLabel }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [filterType, setFilterType] = useState('');
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showPrefs, setShowPrefs] = useState(false);
  const [prefs, setPrefs] = useState({ enabled: true, muted_types: [] });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const labelId = activeLabel?.label_id || '';

  const fetchNotifications = useCallback(async (pg = 1) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (labelId) params.set('label_id', labelId);
      if (filterType) params.set('type', filterType);
      if (unreadOnly) params.set('unread_only', 'true');
      params.set('page', pg);
      params.set('limit', '30');

      const res = await fetch(`${API}/api/uln/notifications?${params}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.notifications || []);
        setTotal(data.total || 0);
        setHasMore(data.has_more || false);
        setPage(pg);
      }
    } catch (e) {
      console.error('Failed to fetch notifications:', e);
    }
    setLoading(false);
  }, [labelId, filterType, unreadOnly]);

  const fetchUnreadCount = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (labelId) params.set('label_id', labelId);
      const res = await fetch(`${API}/api/uln/notifications/unread-count?${params}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setUnreadCount(data.unread_count || 0);
      }
    } catch (e) { /* silent */ }
  }, [labelId]);

  const fetchPrefs = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/uln/notifications/preferences`, { headers });
      if (res.ok) {
        const data = await res.json();
        setPrefs(data.preferences || { enabled: true, muted_types: [] });
      }
    } catch (e) { /* silent */ }
  }, []);

  useEffect(() => {
    fetchNotifications(1);
    fetchUnreadCount();
    fetchPrefs();
  }, [fetchNotifications, fetchUnreadCount, fetchPrefs]);

  const markRead = async (id) => {
    try {
      await fetch(`${API}/api/uln/notifications/${id}/read`, { method: 'PUT', headers });
      setNotifications(prev => prev.map(n => n.notification_id === id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (e) { console.error(e); }
  };

  const markAllRead = async () => {
    try {
      const params = new URLSearchParams();
      if (labelId) params.set('label_id', labelId);
      await fetch(`${API}/api/uln/notifications/read-all?${params}`, { method: 'PUT', headers });
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (e) { console.error(e); }
  };

  const deleteNotif = async (id) => {
    try {
      await fetch(`${API}/api/uln/notifications/${id}`, { method: 'DELETE', headers });
      setNotifications(prev => prev.filter(n => n.notification_id !== id));
      setTotal(prev => prev - 1);
      fetchUnreadCount();
    } catch (e) { console.error(e); }
  };

  const clearAll = async () => {
    if (!window.confirm('Delete all notifications? This cannot be undone.')) return;
    try {
      const params = new URLSearchParams();
      if (labelId) params.set('label_id', labelId);
      await fetch(`${API}/api/uln/notifications/clear?${params}`, { method: 'DELETE', headers });
      setNotifications([]);
      setTotal(0);
      setUnreadCount(0);
    } catch (e) { console.error(e); }
  };

  const toggleMutedType = async (type) => {
    const muted = prefs.muted_types || [];
    const newMuted = muted.includes(type) ? muted.filter(t => t !== type) : [...muted, type];
    setPrefs(prev => ({ ...prev, muted_types: newMuted }));
    try {
      await fetch(`${API}/api/uln/notifications/preferences`, {
        method: 'PUT', headers,
        body: JSON.stringify({ muted_types: newMuted }),
      });
    } catch (e) { console.error(e); }
  };

  const toggleEnabled = async () => {
    const newVal = !prefs.enabled;
    setPrefs(prev => ({ ...prev, enabled: newVal }));
    try {
      await fetch(`${API}/api/uln/notifications/preferences`, {
        method: 'PUT', headers,
        body: JSON.stringify({ enabled: newVal }),
      });
    } catch (e) { console.error(e); }
  };

  return (
    <div className="space-y-6" data-testid="uln-notifications-panel">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Bell className="w-5 h-5 text-purple-600" />
            Notifications
            {unreadCount > 0 && (
              <span className="ml-1 text-xs font-bold bg-purple-600 text-white px-2 py-0.5 rounded-full" data-testid="unread-badge">
                {unreadCount}
              </span>
            )}
          </h2>
          <p className="text-sm text-gray-500 mt-1">{total} total notification{total !== 1 ? 's' : ''}{labelId ? ` for this label` : ''}</p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => fetchNotifications(1)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition"
            data-testid="refresh-notifications-btn"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          {unreadCount > 0 && (
            <button
              onClick={markAllRead}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-purple-50 text-purple-700 hover:bg-purple-100 transition"
              data-testid="mark-all-read-btn"
            >
              <CheckCheck className="w-3.5 h-3.5" />
              Mark all read
            </button>
          )}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition ${
              showFilters ? 'border-purple-300 bg-purple-50 text-purple-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
            data-testid="toggle-filters-btn"
          >
            <Filter className="w-3.5 h-3.5" />
            Filters
            <ChevronDown className={`w-3 h-3 transition ${showFilters ? 'rotate-180' : ''}`} />
          </button>
          <button
            onClick={() => setShowPrefs(!showPrefs)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition ${
              showPrefs ? 'border-purple-300 bg-purple-50 text-purple-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
            data-testid="toggle-prefs-btn"
          >
            <Settings className="w-3.5 h-3.5" />
            Preferences
          </button>
          {notifications.length > 0 && (
            <button
              onClick={clearAll}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition"
              data-testid="clear-all-btn"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Clear all
            </button>
          )}
        </div>
      </div>

      {/* Filters panel */}
      {showFilters && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-3" data-testid="filters-panel">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Type:</span>
            <button
              onClick={() => setFilterType('')}
              className={`text-xs px-2.5 py-1 rounded-full transition ${!filterType ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              data-testid="filter-type-all"
            >
              All
            </button>
            {ALL_TYPES.map(t => (
              <button
                key={t}
                onClick={() => setFilterType(t === filterType ? '' : t)}
                className={`text-xs px-2.5 py-1 rounded-full transition ${filterType === t ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                data-testid={`filter-type-${t}`}
              >
                {(TYPE_META[t] || {}).label || t}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={unreadOnly}
                onChange={(e) => setUnreadOnly(e.target.checked)}
                className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                data-testid="unread-only-checkbox"
              />
              <span className="text-xs text-gray-600">Unread only</span>
            </label>
          </div>
        </div>
      )}

      {/* Preferences panel */}
      {showPrefs && (
        <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-4" data-testid="preferences-panel">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-gray-900">Notifications enabled</h4>
              <p className="text-xs text-gray-500">Toggle to pause all notifications</p>
            </div>
            <button
              onClick={toggleEnabled}
              className={`relative w-11 h-6 rounded-full transition-colors ${prefs.enabled ? 'bg-purple-600' : 'bg-gray-300'}`}
              data-testid="toggle-enabled-btn"
            >
              <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${prefs.enabled ? 'translate-x-5' : ''}`} />
            </button>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Muted notification types</h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {ALL_TYPES.map(t => {
                const muted = (prefs.muted_types || []).includes(t);
                return (
                  <label key={t} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={!muted}
                      onChange={() => toggleMutedType(t)}
                      className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      data-testid={`pref-type-${t}`}
                    />
                    <span className={`text-xs ${muted ? 'text-gray-400 line-through' : 'text-gray-700'}`}>
                      {(TYPE_META[t] || {}).label || t}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Notification list */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" />
        </div>
      ) : notifications.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center" data-testid="no-notifications">
          <Bell className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-gray-600">No notifications</h3>
          <p className="text-sm text-gray-400 mt-1">
            {unreadOnly ? 'All caught up! No unread notifications.' : 'Notifications from label activity will appear here.'}
          </p>
        </div>
      ) : (
        <div className="space-y-2" data-testid="notifications-list">
          {notifications.map(n => (
            <NotificationCard key={n.notification_id} notif={n} onMarkRead={markRead} onDelete={deleteNotif} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {hasMore && (
        <div className="flex justify-center pt-2">
          <button
            onClick={() => fetchNotifications(page + 1)}
            className="px-4 py-2 text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg transition"
            data-testid="load-more-btn"
          >
            Load more
          </button>
        </div>
      )}
    </div>
  );
};
