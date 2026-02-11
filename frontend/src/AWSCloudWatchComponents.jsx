import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATE_COLORS = {
  OK: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  ALARM: 'bg-red-100 text-red-800 border-red-300',
  INSUFFICIENT_DATA: 'bg-amber-100 text-amber-800 border-amber-300',
};

const STATE_DOT = {
  OK: 'bg-emerald-500',
  ALARM: 'bg-red-500',
  INSUFFICIENT_DATA: 'bg-amber-500',
};

export default function AWSCloudWatchDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [snsModal, setSnsModal] = useState(null);
  const [snsMsg, setSnsMsg] = useState({ subject: '', message: '' });
  const [publishing, setPublishing] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [dashRes, healthRes] = await Promise.all([
        fetch(`${API}/cloudwatch/dashboard`),
        fetch(`${API}/cloudwatch/health`),
      ]);
      if (dashRes.ok) setDashboard(await dashRes.json());
      if (healthRes.ok) setHealth(await healthRes.json());
    } catch (e) {
      console.error('Error fetching CloudWatch data:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handlePublish = async () => {
    if (!snsModal || !snsMsg.message) return;
    setPublishing(true);
    try {
      const res = await fetch(`${API}/cloudwatch/sns/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic_arn: snsModal, subject: snsMsg.subject, message: snsMsg.message }),
      });
      const data = await res.json();
      if (data.success) {
        toast.success('Message published to SNS');
        setSnsModal(null);
        setSnsMsg({ subject: '', message: '' });
      } else {
        toast.error(data.error || 'Failed to publish');
      }
    } catch {
      toast.error('Failed to publish message');
    } finally {
      setPublishing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center" data-testid="cloudwatch-loading">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4" />
          <p className="text-slate-400">Connecting to AWS CloudWatch...</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'alarms', label: `Alarms (${dashboard?.total_alarms || 0})` },
    { id: 'sns', label: `SNS (${dashboard?.total_sns_topics || 0})` },
    { id: 'eventbridge', label: `EventBridge (${dashboard?.total_eventbridge_rules || 0})` },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100" data-testid="cloudwatch-dashboard">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">AWS CloudWatch Monitoring</h1>
              <p className="text-sm text-slate-400 mt-1">
                Real-time monitoring &middot; Account {health?.account_id || ''} &middot; {health?.region || 'us-east-1'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${health?.aws_connected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/10 text-red-400 border border-red-500/30'}`}
                data-testid="aws-connection-status">
                <span className={`w-2 h-2 rounded-full ${health?.aws_connected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
                {health?.aws_connected ? 'LIVE' : 'DISCONNECTED'}
              </span>
              <button onClick={fetchData}
                className="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors"
                data-testid="refresh-btn">
                Refresh
              </button>
            </div>
          </div>
          {/* Tabs */}
          <div className="flex gap-1 mt-4" data-testid="cloudwatch-tabs">
            {tabs.map(t => (
              <button key={t.id} onClick={() => setActiveTab(t.id)}
                data-testid={`tab-${t.id}`}
                className={`px-4 py-2 text-sm rounded-t-lg transition-colors ${activeTab === t.id ? 'bg-slate-800 text-white font-medium border-b-2 border-cyan-500' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === 'overview' && <OverviewTab dashboard={dashboard} />}
        {activeTab === 'alarms' && <AlarmsTab alarms={dashboard?.alarms || []} />}
        {activeTab === 'sns' && <SNSTab topics={dashboard?.sns_topics || []} onPublish={setSnsModal} />}
        {activeTab === 'eventbridge' && <EventBridgeTab rules={dashboard?.eventbridge_rules || []} />}
      </div>

      {/* SNS Publish Modal */}
      {snsModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" data-testid="sns-publish-modal">
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Publish SNS Message</h3>
            <p className="text-xs text-slate-400 mb-4 break-all">{snsModal}</p>
            <input value={snsMsg.subject} onChange={e => setSnsMsg(p => ({ ...p, subject: e.target.value }))}
              placeholder="Subject (optional)" className="w-full mb-3 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500"
              data-testid="sns-subject-input" />
            <textarea value={snsMsg.message} onChange={e => setSnsMsg(p => ({ ...p, message: e.target.value }))}
              placeholder="Message body..." rows={4}
              className="w-full mb-4 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 resize-none"
              data-testid="sns-message-input" />
            <div className="flex gap-3">
              <button onClick={() => setSnsModal(null)} className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors">Cancel</button>
              <button onClick={handlePublish} disabled={!snsMsg.message || publishing}
                className="flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
                data-testid="sns-publish-btn">
                {publishing ? 'Publishing...' : 'Publish'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function OverviewTab({ dashboard }) {
  if (!dashboard) return null;
  const stats = [
    { label: 'CloudWatch Alarms', value: dashboard.total_alarms, sub: `${dashboard.ok_alarms} OK, ${dashboard.alarm_state} Active`, color: 'cyan' },
    { label: 'SNS Topics', value: dashboard.total_sns_topics, sub: 'Notification channels', color: 'violet' },
    { label: 'EventBridge Rules', value: dashboard.total_eventbridge_rules, sub: `${dashboard.enabled_rules} enabled`, color: 'amber' },
    { label: 'Region', value: dashboard.region, sub: `Account ${dashboard.account_id}`, color: 'emerald' },
  ];

  return (
    <div data-testid="overview-tab">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((s, i) => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-5" data-testid={`stat-card-${i}`}>
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{s.label}</p>
            <p className={`text-3xl font-bold text-${s.color}-400`}>{s.value}</p>
            <p className="text-xs text-slate-500 mt-1">{s.sub}</p>
          </div>
        ))}
      </div>

      {/* Alarms Summary */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-6">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Alarm Status</h3>
        <div className="space-y-3">
          {(dashboard.alarms || []).map((a, i) => (
            <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <span className={`w-3 h-3 rounded-full ${STATE_DOT[a.state_value] || 'bg-slate-500'}`} />
                <div>
                  <p className="text-sm font-medium text-white">{a.alarm_name}</p>
                  <p className="text-xs text-slate-500">{a.metric_name} &middot; {a.namespace}</p>
                </div>
              </div>
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${STATE_COLORS[a.state_value] || 'bg-slate-700 text-slate-300'}`}>
                {a.state_value}
              </span>
            </div>
          ))}
          {(!dashboard.alarms || dashboard.alarms.length === 0) && (
            <p className="text-sm text-slate-500">No alarms configured</p>
          )}
        </div>
      </div>

      {/* SNS + EventBridge Quick View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">SNS Topics</h3>
          <div className="space-y-2">
            {(dashboard.sns_topics || []).map((t, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-slate-800/50 rounded-lg">
                <span className="text-sm text-slate-300 truncate max-w-[70%]">{t.display_name}</span>
                <span className="text-xs text-slate-500">{t.subscription_count} subs</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">EventBridge Rules</h3>
          <div className="space-y-2">
            {(dashboard.eventbridge_rules || []).map((r, i) => (
              <div key={i} className="flex items-center justify-between p-2 bg-slate-800/50 rounded-lg">
                <span className="text-sm text-slate-300 truncate max-w-[70%]">{r.name}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.state === 'ENABLED' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-700 text-slate-400'}`}>
                  {r.state}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Last synced */}
      {dashboard.last_synced && (
        <p className="text-xs text-slate-600 mt-6 text-right">Last synced: {new Date(dashboard.last_synced).toLocaleString()}</p>
      )}
    </div>
  );
}

function AlarmsTab({ alarms }) {
  return (
    <div data-testid="alarms-tab">
      <h2 className="text-lg font-semibold mb-4">CloudWatch Alarms</h2>
      {alarms.length === 0 ? (
        <p className="text-slate-500">No alarms found</p>
      ) : (
        <div className="space-y-4">
          {alarms.map((a, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-5" data-testid={`alarm-card-${i}`}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${STATE_DOT[a.state_value] || 'bg-slate-500'}`} />
                    <h3 className="font-semibold text-white">{a.alarm_name}</h3>
                  </div>
                  {a.alarm_description && <p className="text-sm text-slate-400 mt-1">{a.alarm_description}</p>}
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${STATE_COLORS[a.state_value] || ''}`}>
                  {a.state_value}
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div><span className="text-slate-500">Metric:</span> <span className="text-slate-300">{a.metric_name}</span></div>
                <div><span className="text-slate-500">Namespace:</span> <span className="text-slate-300">{a.namespace}</span></div>
                <div><span className="text-slate-500">Threshold:</span> <span className="text-slate-300">{a.threshold} ({a.comparison_operator})</span></div>
                <div><span className="text-slate-500">Period:</span> <span className="text-slate-300">{a.period}s</span></div>
              </div>
              {a.state_reason && (
                <p className="text-xs text-slate-500 mt-3 bg-slate-800/50 p-2 rounded">{a.state_reason}</p>
              )}
              {a.dimensions?.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {a.dimensions.map((d, j) => (
                    <span key={j} className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded">{d.name}: {d.value}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SNSTab({ topics, onPublish }) {
  return (
    <div data-testid="sns-tab">
      <h2 className="text-lg font-semibold mb-4">SNS Topics</h2>
      {topics.length === 0 ? (
        <p className="text-slate-500">No SNS topics found</p>
      ) : (
        <div className="space-y-4">
          {topics.map((t, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-5" data-testid={`sns-topic-${i}`}>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-white">{t.display_name}</h3>
                  <p className="text-xs text-slate-500 mt-1 break-all font-mono">{t.topic_arn}</p>
                  <div className="flex gap-4 mt-2 text-sm text-slate-400">
                    <span>{t.subscription_count} subscriptions</span>
                    <span>Region: {t.region}</span>
                  </div>
                </div>
                <button onClick={() => onPublish(t.topic_arn)}
                  className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 rounded-lg text-xs font-medium transition-colors"
                  data-testid={`publish-btn-${i}`}>
                  Publish Message
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function EventBridgeTab({ rules }) {
  return (
    <div data-testid="eventbridge-tab">
      <h2 className="text-lg font-semibold mb-4">EventBridge Rules</h2>
      {rules.length === 0 ? (
        <p className="text-slate-500">No EventBridge rules found</p>
      ) : (
        <div className="space-y-4">
          {rules.map((r, i) => (
            <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-5" data-testid={`eb-rule-${i}`}>
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-white">{r.name}</h3>
                  {r.description && <p className="text-sm text-slate-400 mt-1">{r.description}</p>}
                </div>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${r.state === 'ENABLED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-slate-700 text-slate-400 border border-slate-600'}`}>
                  {r.state}
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm mt-3">
                <div><span className="text-slate-500">Event Bus:</span> <span className="text-slate-300">{r.event_bus_name}</span></div>
                <div><span className="text-slate-500">Targets:</span> <span className="text-slate-300">{r.targets_count}</span></div>
                {r.managed_by && <div><span className="text-slate-500">Managed By:</span> <span className="text-slate-300 text-xs">{r.managed_by}</span></div>}
              </div>
              {r.event_pattern && (
                <details className="mt-3">
                  <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-400">View Event Pattern</summary>
                  <pre className="text-xs text-slate-400 bg-slate-800/50 p-2 rounded mt-2 overflow-x-auto">{r.event_pattern}</pre>
                </details>
              )}
              {r.schedule_expression && (
                <p className="text-xs text-slate-500 mt-2">Schedule: <span className="text-cyan-400">{r.schedule_expression}</span></p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
