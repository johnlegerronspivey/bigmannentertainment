import React, { useState } from 'react';
import { KPISnapshotCards } from './KPISnapshotCards';

const MainDashboard = ({ kpiData, recentActivities, systemAlerts }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  return (
    <div data-testid="main-dashboard" className="space-y-6">
      {/* KPI Snapshot */}
      <KPISnapshotCards 
        kpiData={kpiData} 
        onCardClick={(id) => console.log('KPI clicked:', id)} 
      />

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivities && recentActivities.length > 0 ? recentActivities.map((activity, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></div>
                <div className="flex-1">
                  <p className={`text-sm ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{activity.description}</p>
                  <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>{activity.time}</p>
                </div>
              </div>
            )) : (
              <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>No recent activities to display</p>
            )}
          </div>
        </div>

        {/* System Alerts */}
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Alerts</h2>
          <div className="space-y-4">
            {systemAlerts && systemAlerts.length > 0 ? systemAlerts.map((alert, index) => (
              <div key={index} className={`p-3 rounded-lg ${
                alert.severity === 'critical' ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' :
                alert.severity === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800' :
                'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
              }`}>
                <p className={`text-sm font-medium ${
                  alert.severity === 'critical' ? 'text-red-900 dark:text-red-100' :
                  alert.severity === 'warning' ? 'text-yellow-900 dark:text-yellow-100' :
                  'text-blue-900 dark:text-blue-100'
                }`}>{alert.title}</p>
                <p className={`text-xs mt-1 ${
                  alert.severity === 'critical' ? 'text-red-700 dark:text-red-300' :
                  alert.severity === 'warning' ? 'text-yellow-700 dark:text-yellow-300' :
                  'text-blue-700 dark:text-blue-300'
                }`}>{alert.message}</p>
              </div>
            )) : (
              <div className="text-center py-4">
                <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>✅ All systems operational</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export { MainDashboard };
