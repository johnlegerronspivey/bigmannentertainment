import React from 'react';

export const ULNAnalytics = ({ stats }) => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-2">📊 ULN Analytics</h2>
        <p className="text-gray-600">Deep insights into the Unified Label Network performance</p>
      </div>

      {/* Network Growth */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">📈 Network Growth</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Label Registrations Over Time</h4>
            <div className="h-48 bg-gray-100 rounded flex items-center justify-center">
              <span className="text-gray-500">Chart: Label registration trends</span>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Content Sharing Activity</h4>
            <div className="h-48 bg-gray-100 rounded flex items-center justify-center">
              <span className="text-gray-500">Chart: Cross-label content sharing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Financial Analytics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">💰 Financial Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">${(stats.total_revenue_processed || 0).toLocaleString()}</div>
            <div className="text-gray-600">Total Revenue Processed</div>
            <div className="text-sm text-green-600 mt-1">↗️ +15% from last quarter</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">${(stats.pending_distributions || 0).toLocaleString()}</div>
            <div className="text-gray-600">Pending Distributions</div>
            <div className="text-sm text-blue-600 mt-1">Ready for payout</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">2.5%</div>
            <div className="text-gray-600">Platform Fee</div>
            <div className="text-sm text-purple-600 mt-1">Transparent & competitive</div>
          </div>
        </div>
      </div>

      {/* Governance Analytics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">🗳️ Governance Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Proposal Success Rate</h4>
            <div className="flex items-center justify-center h-32">
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600">73%</div>
                <div className="text-gray-600">of proposals passed</div>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-3">Average Participation</h4>
            <div className="flex items-center justify-center h-32">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600">68%</div>
                <div className="text-gray-600">voter participation</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
