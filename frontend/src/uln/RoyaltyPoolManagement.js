import React, { useState } from 'react';

const RoyaltyPoolsList = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🏊 Active Royalty Pools</h3>
    
    <div className="space-y-3">
      <div className="border border-gray-200 rounded-lg p-4">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Q1 2025 Pool</h4>
            <p className="text-sm text-gray-600">5 participating labels</p>
            <p className="text-sm text-gray-500">Period: Jan 1 - Mar 31, 2025</p>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-green-600">$125,430</div>
            <div className="text-sm text-gray-500">Total collected</div>
            <span className="inline-block px-2 py-1 mt-1 bg-green-100 text-green-800 text-xs rounded-full">
              Ready to distribute
            </span>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Distribution method: Proportional</span>
            <button className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 text-sm rounded">
              Distribute
            </button>
          </div>
        </div>
      </div>

      <div className="border border-gray-200 rounded-lg p-4">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-medium">Q4 2024 Pool</h4>
            <p className="text-sm text-gray-600">8 participating labels</p>
            <p className="text-sm text-gray-500">Period: Oct 1 - Dec 31, 2024</p>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-gray-600">$98,765</div>
            <div className="text-sm text-gray-500">Distributed</div>
            <span className="inline-block px-2 py-1 mt-1 bg-gray-100 text-gray-800 text-xs rounded-full">
              Completed
            </span>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Distributed on: Jan 15, 2025</span>
            <button className="bg-gray-500 text-white px-3 py-1 text-sm rounded">
              View Report
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const EarningsProcessing = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">💸 Earnings Processing</h3>
    <p className="text-gray-600">Process incoming royalty earnings for multi-label distribution</p>
    
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h4 className="font-medium text-blue-900 mb-2">Processing Status</h4>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">1,234</div>
          <div className="text-sm text-blue-700">Earnings processed today</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">$45,678</div>
          <div className="text-sm text-green-700">Total amount processed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">23</div>
          <div className="text-sm text-purple-700">Labels involved</div>
        </div>
      </div>
    </div>

    <div className="space-y-3">
      <h4 className="font-medium">Recent Processing Activity</h4>
      <div className="space-y-2">
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
          <div>
            <div className="font-medium">Spotify Q1 Earnings</div>
            <div className="text-sm text-gray-600">Processed 15 minutes ago</div>
          </div>
          <div className="text-green-600 font-medium">$12,345</div>
        </div>
        
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
          <div>
            <div className="font-medium">Apple Music Batch #1247</div>
            <div className="text-sm text-gray-600">Processed 1 hour ago</div>
          </div>
          <div className="text-green-600 font-medium">$8,901</div>
        </div>
        
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
          <div>
            <div className="font-medium">YouTube Content ID</div>
            <div className="text-sm text-gray-600">Processed 2 hours ago</div>
          </div>
          <div className="text-green-600 font-medium">$3,456</div>
        </div>
      </div>
    </div>
  </div>
);

const PayoutLedger = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">📋 Transparent Payout Ledger</h3>
    <p className="text-gray-600">Complete breakdown of all payouts by label, creator, and investor</p>
    
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recipient</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gross Amount</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deductions</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Net Amount</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Atlantic Records</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Label</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$25,000.00</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$2,625.00</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">$22,375.00</td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Completed</span>
            </td>
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Def Jam Recordings</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Label</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$18,500.00</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$1,942.50</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">$16,557.50</td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">Processing</span>
            </td>
          </tr>
          <tr>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Artist Collective LLC</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Creator</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$12,000.00</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">$1,200.00</td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">$10,800.00</td>
            <td className="px-6 py-4 whitespace-nowrap">
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">Pending</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
);

const DistributionManagement = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🎯 Distribution Management</h3>
    <p className="text-gray-600">Manage royalty distribution methods and DAO overrides</p>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Distribution Methods</h4>
        <div className="space-y-3">
          <div className="flex items-center">
            <input type="radio" name="distribution" id="proportional" className="mr-2" defaultChecked />
            <label htmlFor="proportional" className="text-sm">
              <div className="font-medium">Proportional</div>
              <div className="text-gray-600">Based on revenue contribution</div>
            </label>
          </div>
          
          <div className="flex items-center">
            <input type="radio" name="distribution" id="equal" className="mr-2" />
            <label htmlFor="equal" className="text-sm">
              <div className="font-medium">Equal Split</div>
              <div className="text-gray-600">Even distribution among labels</div>
            </label>
          </div>
          
          <div className="flex items-center">
            <input type="radio" name="distribution" id="custom" className="mr-2" />
            <label htmlFor="custom" className="text-sm">
              <div className="font-medium">Custom Splits</div>
              <div className="text-gray-600">Manually defined percentages</div>
            </label>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">DAO Overrides</h4>
        <div className="space-y-3">
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
            <div className="flex items-center">
              <span className="text-yellow-600 text-sm">⚠️</span>
              <span className="ml-2 text-sm font-medium">Pending Override</span>
            </div>
            <div className="text-xs text-yellow-700 mt-1">
              Proposal #123: Adjust split for Q1 2025
            </div>
          </div>
          
          <div className="p-3 bg-green-50 border border-green-200 rounded">
            <div className="flex items-center">
              <span className="text-green-600 text-sm">✅</span>
              <span className="ml-2 text-sm font-medium">Override Applied</span>
            </div>
            <div className="text-xs text-green-700 mt-1">
              Dispute resolution for content ABC123
            </div>
          </div>
        </div>

        <button className="w-full mt-4 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          View All DAO Actions
        </button>
      </div>
    </div>
  </div>
);

export const RoyaltyPoolManagement = () => {
  const [activeSection, setActiveSection] = useState('pools');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">💰 Multi-Label Royalty Engine</h2>
          <p className="text-gray-600">Aggregate and distribute royalties across labels</p>
        </div>
        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors">
          + Create Pool
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['pools', 'earnings', 'ledger', 'distribution'].map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`capitalize py-2 px-4 rounded-md font-medium transition-colors ${
                activeSection === section 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {section.replace('_', ' ')}
            </button>
          ))}
        </nav>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        {activeSection === 'pools' && <RoyaltyPoolsList />}
        {activeSection === 'earnings' && <EarningsProcessing />}
        {activeSection === 'ledger' && <PayoutLedger />}
        {activeSection === 'distribution' && <DistributionManagement />}
      </div>
    </div>
  );
};
