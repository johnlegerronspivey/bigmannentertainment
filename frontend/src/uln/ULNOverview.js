import React from 'react';

const MetricCard = ({ title, value, subtitle, icon, color }) => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <div className="flex items-center">
      <div className={`${color} p-3 rounded-full text-white text-2xl`}>
        {icon}
      </div>
      <div className="ml-4">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
      </div>
    </div>
  </div>
);

export const ULNOverview = ({ stats }) => {
  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard 
          title="Connected Labels" 
          value={stats.total_labels} 
          subtitle={`${stats.active_labels} active`}
          icon="🏢" 
          color="bg-blue-500"
        />
        <MetricCard 
          title="Major Labels" 
          value={stats.major_labels || 0} 
          subtitle="Premium tier"
          icon="🌟" 
          color="bg-purple-500"
        />
        <MetricCard 
          title="Independent Labels" 
          value={stats.independent_labels || 0} 
          subtitle="Creative freedom"
          icon="🎵" 
          color="bg-green-500"
        />
        <MetricCard 
          title="Cross-Label Collaborations" 
          value={stats.cross_collaborations || 0} 
          subtitle="Active partnerships"
          icon="🤝" 
          color="bg-orange-500"
        />
        <MetricCard 
          title="Smart Contracts" 
          value={stats.smart_contracts || 0} 
          subtitle="Blockchain enabled"
          icon="📋" 
          color="bg-teal-500"
        />
        <MetricCard 
          title="DAO Proposals" 
          value={stats.total_dao_proposals} 
          subtitle="Governance actions"
          icon="🗳️" 
          color="bg-red-500"
        />
      </div>

      {/* Geographic Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">🌍 Global Distribution</h3>
          <div className="space-y-3">
            {Object.entries(stats.labels_by_territory || {}).map(([territory, count]) => (
              <div key={territory} className="flex justify-between items-center">
                <span className="font-medium">{territory}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full" 
                      style={{ width: `${(count / stats.total_labels * 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">📈 Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <div>
                <div className="font-medium">New Registrations</div>
                <div className="text-sm text-gray-600">Last 30 days</div>
              </div>
              <div className="text-blue-600 font-bold text-xl">
                {stats.recent_registrations || 0}
              </div>
            </div>
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
              <div>
                <div className="font-medium">Content Shares</div>
                <div className="text-sm text-gray-600">Last 30 days</div>
              </div>
              <div className="text-green-600 font-bold text-xl">
                {stats.recent_content_shares || 0}
              </div>
            </div>
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
              <div>
                <div className="font-medium">DAO Proposals</div>
                <div className="text-sm text-gray-600">Last 30 days</div>
              </div>
              <div className="text-purple-600 font-bold text-xl">
                {stats.recent_proposals || 0}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">⚙️ System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-green-600 text-xl">✓</span>
            </div>
            <div className="font-medium">Label Registry</div>
            <div className="text-sm text-green-600">Operational</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-green-600 text-xl">✓</span>
            </div>
            <div className="font-medium">Royalty Engine</div>
            <div className="text-sm text-green-600">Processing</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <span className="text-yellow-600 text-xl">⚠</span>
            </div>
            <div className="font-medium">Blockchain</div>
            <div className="text-sm text-yellow-600">Development Mode</div>
          </div>
        </div>
      </div>
    </div>
  );
};
