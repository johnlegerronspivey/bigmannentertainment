import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

// Main Dashboard Component
const MacieDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [findings, setFindings] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [identifiers, setIdentifiers] = useState([]);
  const [buckets, setBuckets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateJobModal, setShowCreateJobModal] = useState(false);
  const [showCreateIdentifierModal, setShowCreateIdentifierModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, findingsRes, jobsRes, identifiersRes, bucketsRes] = await Promise.all([
        fetch(`${API}/api/macie/dashboard`),
        fetch(`${API}/api/macie/findings`),
        fetch(`${API}/api/macie/jobs`),
        fetch(`${API}/api/macie/custom-identifiers`),
        fetch(`${API}/api/macie/buckets`)
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (findingsRes.ok) {
        const data = await findingsRes.json();
        setFindings(data.findings || []);
      }
      if (jobsRes.ok) {
        const data = await jobsRes.json();
        setJobs(data.jobs || []);
      }
      if (identifiersRes.ok) setIdentifiers(await identifiersRes.json());
      if (bucketsRes.ok) setBuckets(await bucketsRes.json());
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load Macie dashboard data');
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'findings', label: 'Findings', icon: '🔍' },
    { id: 'jobs', label: 'Scan Jobs', icon: '⚙️' },
    { id: 'identifiers', label: 'Custom Identifiers', icon: '🎯' },
    { id: 'buckets', label: 'S3 Buckets', icon: '🪣' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-red-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Macie Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/30 border-b border-red-500/30">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span className="text-4xl">🔒</span>
                AWS Macie PII Detection
              </h1>
              <p className="text-red-300 mt-1">Automated sensitive data discovery and compliance monitoring</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateJobModal(true)}
                className="px-4 py-2 bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-lg hover:from-red-600 hover:to-orange-700 transition-all flex items-center gap-2"
                data-testid="new-scan-btn"
              >
                <span>🔍</span> New Scan
              </button>
              <button
                onClick={fetchData}
                className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all"
                data-testid="refresh-btn"
              >
                ↻ Refresh
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mt-6 overflow-x-auto pb-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'bg-red-600 text-white'
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'overview' && (
          <OverviewTab stats={stats} findings={findings} jobs={jobs} />
        )}
        {activeTab === 'findings' && (
          <FindingsTab findings={findings} onRefresh={fetchData} />
        )}
        {activeTab === 'jobs' && (
          <JobsTab jobs={jobs} onRefresh={fetchData} onCreateNew={() => setShowCreateJobModal(true)} />
        )}
        {activeTab === 'identifiers' && (
          <IdentifiersTab 
            identifiers={identifiers} 
            onRefresh={fetchData}
            onCreateNew={() => setShowCreateIdentifierModal(true)}
          />
        )}
        {activeTab === 'buckets' && (
          <BucketsTab buckets={buckets} onRefresh={fetchData} />
        )}
      </div>

      {/* Modals */}
      {showCreateJobModal && (
        <CreateJobModal
          buckets={buckets}
          identifiers={identifiers}
          onClose={() => setShowCreateJobModal(false)}
          onSuccess={() => {
            setShowCreateJobModal(false);
            fetchData();
            toast.success('Scan job created successfully!');
          }}
        />
      )}
      {showCreateIdentifierModal && (
        <CreateIdentifierModal
          onClose={() => setShowCreateIdentifierModal(false)}
          onSuccess={() => {
            setShowCreateIdentifierModal(false);
            fetchData();
            toast.success('Custom identifier created successfully!');
          }}
        />
      )}
    </div>
  );
};

// Overview Tab
const OverviewTab = ({ stats, findings, jobs }) => {
  const highSeverityFindings = findings?.filter(f => f.severity === 'High') || [];
  const recentJobs = jobs?.slice(0, 3) || [];

  return (
    <div className="space-y-6" data-testid="overview-tab">
      {/* Alert Banner */}
      {stats?.high_severity_findings > 0 && (
        <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4 flex items-center gap-4">
          <div className="text-4xl">⚠️</div>
          <div>
            <h3 className="text-white font-semibold">Critical Findings Detected</h3>
            <p className="text-red-300">
              {stats.high_severity_findings} high-severity finding(s) require immediate attention. 
              {stats.unacknowledged_findings > 0 && ` ${stats.unacknowledged_findings} unacknowledged.`}
            </p>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Findings" 
          value={stats?.total_findings || 0} 
          icon="🔍" 
          color="from-red-500 to-rose-600"
        />
        <StatCard 
          title="High Severity" 
          value={stats?.high_severity_findings || 0} 
          icon="🚨" 
          color="from-red-600 to-red-700"
          highlight={stats?.high_severity_findings > 0}
        />
        <StatCard 
          title="Objects Scanned" 
          value={stats?.total_objects_scanned?.toLocaleString() || 0} 
          icon="📄" 
          color="from-blue-500 to-cyan-500"
        />
        <StatCard 
          title="Monitored Buckets" 
          value={stats?.monitored_buckets || 0} 
          icon="🪣" 
          color="from-green-500 to-emerald-500"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MiniStatCard title="Running Jobs" value={stats?.running_jobs || 0} icon="⚙️" />
        <MiniStatCard title="Completed Jobs" value={stats?.completed_jobs || 0} icon="✅" />
        <MiniStatCard title="Medium Severity" value={stats?.medium_severity_findings || 0} icon="⚡" />
        <MiniStatCard title="Low Severity" value={stats?.low_severity_findings || 0} icon="ℹ️" />
        <MiniStatCard title="Custom Identifiers" value={stats?.total_custom_identifiers || 0} icon="🎯" />
        <MiniStatCard title="Sensitive Objects" value={stats?.total_sensitive_objects || 0} icon="🔐" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PII Types Detected */}
        <div className="bg-white/5 rounded-xl p-6 border border-red-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>🔐</span> PII Types Detected
          </h3>
          {stats?.pii_types_detected?.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {stats.pii_types_detected.map((type, idx) => (
                <span 
                  key={idx}
                  className="px-3 py-1 bg-red-500/20 text-red-300 rounded-full text-sm"
                >
                  {type.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No PII types detected yet</p>
          )}
        </div>

        {/* Recent Scan Activity */}
        <div className="bg-white/5 rounded-xl p-6 border border-red-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>⚙️</span> Recent Scan Activity
          </h3>
          {recentJobs.length > 0 ? (
            <div className="space-y-3">
              {recentJobs.map(job => (
                <div key={job.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div>
                    <p className="text-white font-medium">{job.name}</p>
                    <p className="text-gray-400 text-sm">{job.objects_scanned?.toLocaleString()} objects scanned</p>
                  </div>
                  <StatusBadge status={job.status} />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No scan jobs yet</p>
          )}
        </div>
      </div>

      {/* High Severity Findings */}
      {highSeverityFindings.length > 0 && (
        <div className="bg-white/5 rounded-xl p-6 border border-red-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>🚨</span> High Severity Findings
          </h3>
          <div className="space-y-3">
            {highSeverityFindings.slice(0, 5).map(finding => (
              <FindingCard key={finding.id} finding={finding} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Findings Tab
const FindingsTab = ({ findings, onRefresh }) => {
  const [severityFilter, setSeverityFilter] = useState('all');
  const [acknowledgedFilter, setAcknowledgedFilter] = useState('all');

  const filteredFindings = findings?.filter(f => {
    if (severityFilter !== 'all' && f.severity !== severityFilter) return false;
    if (acknowledgedFilter === 'acknowledged' && !f.is_acknowledged) return false;
    if (acknowledgedFilter === 'unacknowledged' && f.is_acknowledged) return false;
    return true;
  }) || [];

  const handleAcknowledge = async (findingId) => {
    try {
      const response = await fetch(`${API}/api/macie/findings/${findingId}/acknowledge`, {
        method: 'POST'
      });
      if (response.ok) {
        toast.success('Finding acknowledged');
        onRefresh();
      }
    } catch (error) {
      toast.error('Failed to acknowledge finding');
    }
  };

  return (
    <div className="space-y-6" data-testid="findings-tab">
      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="text-gray-400 text-sm block mb-2">Severity</label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-white/10 text-white border border-red-500/30 rounded-lg px-4 py-2"
          >
            <option value="all" className="bg-slate-800">All Severities</option>
            <option value="High" className="bg-slate-800">High</option>
            <option value="Medium" className="bg-slate-800">Medium</option>
            <option value="Low" className="bg-slate-800">Low</option>
          </select>
        </div>
        <div>
          <label className="text-gray-400 text-sm block mb-2">Status</label>
          <select
            value={acknowledgedFilter}
            onChange={(e) => setAcknowledgedFilter(e.target.value)}
            className="bg-white/10 text-white border border-red-500/30 rounded-lg px-4 py-2"
          >
            <option value="all" className="bg-slate-800">All</option>
            <option value="unacknowledged" className="bg-slate-800">Unacknowledged</option>
            <option value="acknowledged" className="bg-slate-800">Acknowledged</option>
          </select>
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {filteredFindings.length > 0 ? (
          filteredFindings.map(finding => (
            <FindingCard 
              key={finding.id} 
              finding={finding} 
              detailed
              onAcknowledge={() => handleAcknowledge(finding.id)}
            />
          ))
        ) : (
          <div className="text-center py-16 bg-white/5 rounded-xl border border-dashed border-red-500/30">
            <div className="text-6xl mb-4">✅</div>
            <h3 className="text-white text-xl font-semibold mb-2">No Findings</h3>
            <p className="text-gray-400">No sensitive data findings match your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Jobs Tab
const JobsTab = ({ jobs, onRefresh, onCreateNew }) => {
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredJobs = jobs?.filter(j => 
    statusFilter === 'all' || j.status === statusFilter
  ) || [];

  return (
    <div className="space-y-6" data-testid="jobs-tab">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {['all', 'RUNNING', 'COMPLETE', 'CANCELLED'].map(status => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1 rounded-lg text-sm ${
                statusFilter === status
                  ? 'bg-red-600 text-white'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }`}
            >
              {status === 'all' ? 'All' : status}
            </button>
          ))}
        </div>
        <button
          onClick={onCreateNew}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          + New Scan Job
        </button>
      </div>

      <div className="space-y-4">
        {filteredJobs.length > 0 ? (
          filteredJobs.map(job => (
            <JobCard key={job.id} job={job} />
          ))
        ) : (
          <div className="text-center py-16 bg-white/5 rounded-xl border border-dashed border-red-500/30">
            <div className="text-6xl mb-4">⚙️</div>
            <h3 className="text-white text-xl font-semibold mb-2">No Scan Jobs</h3>
            <p className="text-gray-400 mb-4">Create your first scan job to detect sensitive data</p>
            <button
              onClick={onCreateNew}
              className="px-6 py-3 bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-lg"
            >
              Create Scan Job
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Identifiers Tab
const IdentifiersTab = ({ identifiers, onRefresh, onCreateNew }) => {
  return (
    <div className="space-y-6" data-testid="identifiers-tab">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Custom Data Identifiers</h2>
        <button
          onClick={onCreateNew}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          data-testid="create-identifier-btn"
        >
          + New Identifier
        </button>
      </div>

      <p className="text-gray-400">
        Custom data identifiers allow you to detect proprietary sensitive data patterns specific to your organization.
      </p>

      {identifiers?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {identifiers.map(identifier => (
            <IdentifierCard key={identifier.id} identifier={identifier} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white/5 rounded-xl border border-dashed border-red-500/30">
          <div className="text-6xl mb-4">🎯</div>
          <h3 className="text-white text-xl font-semibold mb-2">No Custom Identifiers</h3>
          <p className="text-gray-400 mb-4">Create custom identifiers to detect organization-specific data</p>
          <button
            onClick={onCreateNew}
            className="px-6 py-3 bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-lg"
          >
            Create Identifier
          </button>
        </div>
      )}
    </div>
  );
};

// Buckets Tab
const BucketsTab = ({ buckets, onRefresh }) => {
  return (
    <div className="space-y-6" data-testid="buckets-tab">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Monitored S3 Buckets</h2>
        <span className="text-gray-400">{buckets?.length || 0} buckets</span>
      </div>

      {buckets?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {buckets.map(bucket => (
            <BucketCard key={bucket.name} bucket={bucket} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white/5 rounded-xl border border-dashed border-red-500/30">
          <div className="text-6xl mb-4">🪣</div>
          <h3 className="text-white text-xl font-semibold mb-2">No Buckets Monitored</h3>
          <p className="text-gray-400">Add S3 buckets to start monitoring for sensitive data</p>
        </div>
      )}
    </div>
  );
};

// Component Cards
const StatCard = ({ title, value, icon, color, highlight = false }) => (
  <div className={`bg-gradient-to-br ${color} p-6 rounded-xl shadow-lg ${highlight ? 'ring-2 ring-white/50 animate-pulse' : ''}`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-white/80 text-sm">{title}</p>
        <p className="text-3xl font-bold text-white">{value}</p>
      </div>
      <div className="text-4xl opacity-80">{icon}</div>
    </div>
  </div>
);

const MiniStatCard = ({ title, value, icon }) => (
  <div className="bg-white/5 p-4 rounded-xl border border-red-500/20">
    <div className="flex items-center gap-3">
      <span className="text-2xl">{icon}</span>
      <div>
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="text-gray-400 text-xs">{title}</p>
      </div>
    </div>
  </div>
);

const StatusBadge = ({ status }) => {
  const statusConfig = {
    RUNNING: { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Running' },
    COMPLETE: { bg: 'bg-green-500/20', text: 'text-green-400', label: 'Complete' },
    CANCELLED: { bg: 'bg-gray-500/20', text: 'text-gray-400', label: 'Cancelled' },
    PAUSED: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'Paused' },
    IDLE: { bg: 'bg-gray-500/20', text: 'text-gray-400', label: 'Idle' }
  };

  const config = statusConfig[status] || statusConfig.IDLE;

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
      {config.label}
    </span>
  );
};

const SeverityBadge = ({ severity }) => {
  const severityConfig = {
    High: { bg: 'bg-red-500', text: 'text-white' },
    Medium: { bg: 'bg-yellow-500', text: 'text-black' },
    Low: { bg: 'bg-green-500', text: 'text-white' }
  };

  const config = severityConfig[severity] || severityConfig.Low;

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.text}`}>
      {severity}
    </span>
  );
};

const FindingCard = ({ finding, detailed = false, onAcknowledge }) => (
  <div className={`bg-white/5 rounded-xl p-4 border ${
    finding.severity === 'High' ? 'border-red-500/50' : 
    finding.severity === 'Medium' ? 'border-yellow-500/30' : 'border-green-500/20'
  }`}>
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-2">
          <SeverityBadge severity={finding.severity} />
          {!finding.is_acknowledged && (
            <span className="px-2 py-0.5 bg-orange-500/20 text-orange-400 rounded text-xs">
              Unacknowledged
            </span>
          )}
          {finding.resource?.public_access && (
            <span className="px-2 py-0.5 bg-red-500/30 text-red-400 rounded text-xs">
              PUBLIC ACCESS
            </span>
          )}
        </div>
        <h4 className="text-white font-semibold">{finding.type}</h4>
        {finding.resource && (
          <p className="text-gray-400 text-sm mt-1">
            <span className="text-gray-500">Bucket:</span> {finding.resource.bucket_name}
            {finding.resource.object_key && (
              <span className="block"><span className="text-gray-500">Object:</span> {finding.resource.object_key}</span>
            )}
          </p>
        )}
        
        {detailed && finding.sensitive_data_occurrences?.length > 0 && (
          <div className="mt-3">
            <p className="text-gray-400 text-sm mb-2">Detected Data Types:</p>
            <div className="flex flex-wrap gap-2">
              {finding.sensitive_data_occurrences.map((occ, idx) => (
                <span key={idx} className="px-2 py-1 bg-red-500/20 text-red-300 rounded text-xs">
                  {occ.type.replace(/_/g, ' ')} ({occ.count})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {detailed && !finding.is_acknowledged && onAcknowledge && (
        <button
          onClick={onAcknowledge}
          className="px-3 py-1 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
        >
          Acknowledge
        </button>
      )}
    </div>
    
    <div className="mt-3 text-xs text-gray-500 flex items-center justify-between">
      <span>{finding.total_detections} total detections</span>
      <span>Score: {finding.severity_score}</span>
    </div>
  </div>
);

const JobCard = ({ job }) => (
  <div className="bg-white/5 rounded-xl p-4 border border-red-500/20">
    <div className="flex items-start justify-between">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h4 className="text-white font-semibold">{job.name}</h4>
          <StatusBadge status={job.status} />
        </div>
        {job.description && (
          <p className="text-gray-400 text-sm">{job.description}</p>
        )}
        <div className="flex flex-wrap gap-2 mt-2">
          {job.buckets?.map((bucket, idx) => (
            <span key={idx} className="px-2 py-1 bg-white/10 text-gray-300 rounded text-xs">
              {bucket}
            </span>
          ))}
        </div>
      </div>
      <div className="text-right">
        <p className="text-2xl font-bold text-white">{job.objects_scanned?.toLocaleString()}</p>
        <p className="text-gray-400 text-xs">objects scanned</p>
      </div>
    </div>
    
    <div className="mt-4 grid grid-cols-3 gap-4 text-center">
      <div className="bg-white/5 rounded-lg p-2">
        <p className="text-lg font-semibold text-white">{job.objects_matched}</p>
        <p className="text-gray-500 text-xs">Matched</p>
      </div>
      <div className="bg-white/5 rounded-lg p-2">
        <p className="text-lg font-semibold text-white">{job.findings_count}</p>
        <p className="text-gray-500 text-xs">Findings</p>
      </div>
      <div className="bg-white/5 rounded-lg p-2">
        <p className="text-lg font-semibold text-white">{job.sampling_percentage}%</p>
        <p className="text-gray-500 text-xs">Sampling</p>
      </div>
    </div>
  </div>
);

const IdentifierCard = ({ identifier }) => (
  <div className="bg-white/5 rounded-xl p-4 border border-red-500/20">
    <div className="flex items-center gap-3 mb-2">
      <span className="text-2xl">🎯</span>
      <div>
        <h4 className="text-white font-semibold">{identifier.name}</h4>
        {identifier.is_active && (
          <span className="px-2 py-0.5 bg-green-500/20 text-green-400 rounded text-xs">Active</span>
        )}
      </div>
    </div>
    
    {identifier.description && (
      <p className="text-gray-400 text-sm mb-3">{identifier.description}</p>
    )}
    
    <div className="bg-black/30 rounded-lg p-3 font-mono text-sm text-red-300 overflow-x-auto">
      {identifier.regex}
    </div>
    
    {identifier.keywords?.length > 0 && (
      <div className="mt-3">
        <p className="text-gray-500 text-xs mb-1">Keywords:</p>
        <div className="flex flex-wrap gap-1">
          {identifier.keywords.map((kw, idx) => (
            <span key={idx} className="px-2 py-0.5 bg-white/10 text-gray-300 rounded text-xs">
              {kw}
            </span>
          ))}
        </div>
      </div>
    )}
  </div>
);

const BucketCard = ({ bucket }) => (
  <div className={`bg-white/5 rounded-xl p-4 border ${
    bucket.public_access_blocked ? 'border-green-500/20' : 'border-red-500/50'
  }`}>
    <div className="flex items-center gap-3 mb-3">
      <span className="text-3xl">🪣</span>
      <div>
        <h4 className="text-white font-semibold">{bucket.name}</h4>
        <p className="text-gray-400 text-xs">{bucket.region}</p>
      </div>
    </div>
    
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-sm">Objects</span>
        <span className="text-white">{bucket.object_count?.toLocaleString()}</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-sm">Findings</span>
        <span className={`font-semibold ${bucket.findings_count > 0 ? 'text-red-400' : 'text-green-400'}`}>
          {bucket.findings_count}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-sm">Public Access</span>
        <span className={`px-2 py-0.5 rounded text-xs ${
          bucket.public_access_blocked 
            ? 'bg-green-500/20 text-green-400' 
            : 'bg-red-500/20 text-red-400'
        }`}>
          {bucket.public_access_blocked ? 'Blocked' : 'OPEN'}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-sm">Encryption</span>
        <span className="text-gray-300 text-sm">{bucket.encryption_type || 'None'}</span>
      </div>
    </div>
  </div>
);

// Modals
const CreateJobModal = ({ buckets, identifiers, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    bucket_names: [],
    job_type: 'ONE_TIME',
    sampling_percentage: 100,
    custom_data_identifier_ids: []
  });
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim() || formData.bucket_names.length === 0) {
      toast.error('Please provide a name and select at least one bucket');
      return;
    }

    setCreating(true);
    try {
      const response = await fetch(`${API}/api/macie/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onSuccess();
      } else {
        throw new Error('Failed to create job');
      }
    } catch (error) {
      toast.error('Failed to create scan job');
    }
    setCreating(false);
  };

  const toggleBucket = (bucketName) => {
    setFormData(prev => ({
      ...prev,
      bucket_names: prev.bucket_names.includes(bucketName)
        ? prev.bucket_names.filter(b => b !== bucketName)
        : [...prev.bucket_names, bucketName]
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Create Scan Job</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">&times;</button>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="text-gray-300 text-sm block mb-2">Job Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="Weekly PII Scan"
              data-testid="job-name-input"
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="Scan for sensitive data..."
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Select Buckets *</label>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {buckets?.map(bucket => (
                <label key={bucket.name} className="flex items-center gap-3 p-2 bg-slate-700 rounded cursor-pointer hover:bg-slate-600">
                  <input
                    type="checkbox"
                    checked={formData.bucket_names.includes(bucket.name)}
                    onChange={() => toggleBucket(bucket.name)}
                    className="rounded"
                  />
                  <span className="text-white">{bucket.name}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-gray-300 text-sm block mb-2">Job Type</label>
              <select
                value={formData.job_type}
                onChange={(e) => setFormData({ ...formData, job_type: e.target.value })}
                className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              >
                <option value="ONE_TIME">One Time</option>
                <option value="SCHEDULED">Scheduled</option>
              </select>
            </div>

            <div>
              <label className="text-gray-300 text-sm block mb-2">Sampling %</label>
              <input
                type="number"
                value={formData.sampling_percentage}
                onChange={(e) => setFormData({ ...formData, sampling_percentage: parseInt(e.target.value) || 100 })}
                className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
                min="1"
                max="100"
              />
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              data-testid="submit-job-btn"
            >
              {creating ? 'Creating...' : 'Create Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const CreateIdentifierModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    regex: '',
    keywords: '',
    ignore_words: '',
    maximum_match_distance: 50
  });
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.regex.trim()) {
      toast.error('Please provide a name and regex pattern');
      return;
    }

    setCreating(true);
    try {
      const response = await fetch(`${API}/api/macie/custom-identifiers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          keywords: formData.keywords ? formData.keywords.split(',').map(k => k.trim()) : [],
          ignore_words: formData.ignore_words ? formData.ignore_words.split(',').map(w => w.trim()) : []
        })
      });

      if (response.ok) {
        onSuccess();
      } else {
        throw new Error('Failed to create identifier');
      }
    } catch (error) {
      toast.error('Failed to create custom identifier');
    }
    setCreating(false);
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Create Custom Identifier</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">&times;</button>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="text-gray-300 text-sm block mb-2">Identifier Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="Employee ID"
              data-testid="identifier-name-input"
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="Detects employee IDs in format..."
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Regex Pattern *</label>
            <textarea
              value={formData.regex}
              onChange={(e) => setFormData({ ...formData, regex: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2 font-mono"
              placeholder="[A-Z]-\d{8}"
              rows="2"
              data-testid="identifier-regex-input"
            />
            <p className="text-gray-500 text-xs mt-1">Use standard regex syntax</p>
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Keywords (comma-separated)</label>
            <input
              type="text"
              value={formData.keywords}
              onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="employee, staff, id"
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Ignore Words (comma-separated)</label>
            <input
              type="text"
              value={formData.ignore_words}
              onChange={(e) => setFormData({ ...formData, ignore_words: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="test, example, sample"
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Maximum Match Distance</label>
            <input
              type="number"
              value={formData.maximum_match_distance}
              onChange={(e) => setFormData({ ...formData, maximum_match_distance: parseInt(e.target.value) || 50 })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              min="0"
              max="300"
            />
            <p className="text-gray-500 text-xs mt-1">Characters between keyword and match (0-300)</p>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              data-testid="submit-identifier-btn"
            >
              {creating ? 'Creating...' : 'Create Identifier'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MacieDashboard;
