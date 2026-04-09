import React, { useState } from 'react';

const KPISnapshotCards = ({ kpiData, onCardClick }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  const kpis = [
    {
      id: 'assets-live',
      title: '🎬 Assets Live',
      value: kpiData?.assetsLive || '0',
      status: '✅',
      statusColor: 'text-green-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'platforms-connected',
      title: '🌐 Platforms Connected',
      value: kpiData?.platformsConnected || '0',
      status: '🔄',
      statusColor: 'text-blue-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'royalties-today',
      title: '💸 Royalties Today',
      value: kpiData?.royaltiesToday || '$0.00',
      status: '📈',
      statusColor: 'text-green-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'pending-payouts',
      title: '⏳ Pending Payouts',
      value: kpiData?.pendingPayouts || '$0.00',
      status: '⚠️',
      statusColor: 'text-yellow-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'compliance-flags',
      title: '🛡️ Compliance Flags',
      value: kpiData?.complianceFlags || '2',
      status: '🔍',
      statusColor: 'text-red-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'forecast-roi',
      title: '📈 Forecast ROI (30d)',
      value: kpiData?.forecastROI || '0%',
      status: '📊',
      statusColor: 'text-purple-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    }
  ];

  return (
    <div data-testid="kpi-snapshot-cards" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
      {kpis.map((kpi) => (
        <div
          key={kpi.id}
          onClick={() => onCardClick(kpi.id)}
          data-testid={`kpi-card-${kpi.id}`}
          className={`${kpi.bgColor} ${isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-200 hover:bg-gray-50'} border rounded-lg p-4 cursor-pointer transition-colors shadow-sm`}
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              {kpi.title}
            </h3>
            <span className={`text-lg ${kpi.statusColor}`}>
              {kpi.status}
            </span>
          </div>
          <p className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            {kpi.value}
          </p>
        </div>
      ))}
    </div>
  );
};

export { KPISnapshotCards };
