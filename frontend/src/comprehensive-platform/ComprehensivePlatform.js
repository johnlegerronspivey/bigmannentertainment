import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from './utils';
import { GlobalHeader } from './GlobalHeader';
import { LeftSidebar } from './LeftSidebar';
import { MainDashboard } from './MainDashboard';
import { ContentManager } from './ContentManager';
import { DistributionTracker } from './DistributionTracker';
import { RoyaltyEngine } from './RoyaltyEngine';
import { AnalyticsForecasting } from './AnalyticsForecasting';
import { ComplianceCenter } from './ComplianceCenter';
import { SponsorshipCampaigns } from './SponsorshipCampaigns';
import { ContributorHub } from './ContributorHub';
import { SystemHealth } from './SystemHealth';
import { DAOGovernance } from './DAOGovernance';
import { AIRoyaltyForecasting, SmartContractBuilder, MultiCurrencyPayouts, PremiumDashboardOverview } from '../PremiumFeaturesComponents';
import { MLCIntegration } from '../MLCIntegrationComponents';
import { MDEIntegration } from '../MDEIntegrationComponents';
import PDOOHCampaignManager from '../PDOOHCampaignManager';

export const ComprehensivePlatform = () => {
  const [activeModule, setActiveModule] = useState('main-dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [kpiData, setKpiData] = useState({});
  const [recentActivities, setRecentActivities] = useState([]);
  const [systemAlerts, setSystemAlerts] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [user, setUser] = useState({ name: 'John LeGerron Spivey', email: 'owner@bigmannentertainment.com' });

  useEffect(() => {
    const fetchKpiData = async () => {
      try {
        const [contentRes, complianceRes, campaignRes, contributorRes] = await Promise.allSettled([
          axios.get(`${API}/api/platform/content/stats?user_id=user_123`),
          axios.get(`${API}/api/platform/compliance/status?user_id=user_123`),
          axios.get(`${API}/api/platform/sponsorship/analytics?user_id=user_123`),
          axios.get(`${API}/api/platform/contributors/stats?user_id=user_123`),
        ]);
        const content = contentRes.status === 'fulfilled' ? contentRes.value?.data : {};
        const compliance = complianceRes.status === 'fulfilled' ? complianceRes.value?.data : {};
        const campaign = campaignRes.status === 'fulfilled' ? campaignRes.value?.data : {};
        const contributor = contributorRes.status === 'fulfilled' ? contributorRes.value?.data : {};

        const totalAssets = content?.stats?.total_assets || 0;
        const liveAssets = content?.stats?.by_status?.live || 0;
        const compScore = compliance?.overall_compliance?.score || 0;
        const compFlags = (compliance?.overall_compliance?.needs_attention || 0) + (compliance?.overall_compliance?.non_compliant || 0);
        const totalCampaigns = campaign?.analytics?.overview?.total_campaigns || 0;
        const totalEarned = contributor?.stats?.earnings?.total_earned || 0;
        const pendingEarnings = contributor?.stats?.earnings?.pending || 0;

        setKpiData({
          assetsLive: liveAssets.toLocaleString(),
          platformsConnected: totalCampaigns.toString(),
          royaltiesToday: `$${totalEarned.toLocaleString()}`,
          pendingPayouts: `$${pendingEarnings.toLocaleString()}`,
          complianceFlags: compFlags.toString(),
          forecastROI: `${compScore}%`
        });
      } catch (e) {
        console.error('KPI fetch error:', e);
        setKpiData({
          assetsLive: '0', platformsConnected: '0', royaltiesToday: '$0',
          pendingPayouts: '$0', complianceFlags: '0', forecastROI: '0%'
        });
      }
    };
    fetchKpiData();
    setRecentActivities([]);
    setSystemAlerts([]);
    setNotifications([]);
  }, []);

  const handleSearch = (query) => {
    console.log('Search query:', query);
  };

  const handleNotificationClick = (notification) => {
    console.log('Notification clicked:', notification);
  };

  const handleModuleChange = (moduleId) => {
    setActiveModule(moduleId);
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <div data-testid="comprehensive-platform" className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <GlobalHeader
        user={user}
        notifications={notifications}
        onSearch={handleSearch}
        onNotificationClick={handleNotificationClick}
        onMobileMenuToggle={toggleMobileMenu}
      />

      <div className="flex">
        <LeftSidebar
          activeModule={activeModule}
          onModuleChange={handleModuleChange}
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={toggleSidebar}
          isMobileMenuOpen={mobileMenuOpen}
          onMobileMenuToggle={toggleMobileMenu}
        />

        <main className={`flex-1 p-4 lg:p-6 ${sidebarCollapsed ? 'lg:ml-0' : 'lg:ml-0'} transition-all duration-300`}>
          <div className="max-w-full">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white capitalize">
                {activeModule.replace('-', ' ')} Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Manage and monitor your {activeModule.replace('-', ' ')} operations
              </p>
            </div>

            {activeModule === 'content-manager' && <ContentManager />}
            {activeModule === 'distribution-tracker' && <DistributionTracker />}
            {activeModule === 'royalty-engine' && <RoyaltyEngine />}
            {activeModule === 'mlc-integration' && <MLCIntegration />}
            {activeModule === 'mde-integration' && <MDEIntegration />}
            {activeModule === 'ai-forecasting' && <AIRoyaltyForecasting />}
            {activeModule === 'smart-contracts' && <SmartContractBuilder />}
            {activeModule === 'multi-currency' && <MultiCurrencyPayouts />}
            {activeModule === 'pdooh' && <PDOOHCampaignManager />}
            {activeModule === 'compliance-center' && <ComplianceCenter />}
            {activeModule === 'analytics-forecasting' && <AnalyticsForecasting />}
            {activeModule === 'sponsorship-campaigns' && <SponsorshipCampaigns />}
            {activeModule === 'contributor-hub' && <ContributorHub />}
            {activeModule === 'system-health' && <SystemHealth />}
            {activeModule === 'dao-governance' && <DAOGovernance />}
            {activeModule === 'main-dashboard' && <PremiumDashboardOverview />}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ComprehensivePlatform;
