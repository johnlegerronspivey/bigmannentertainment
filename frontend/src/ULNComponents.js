import React, { useState, useEffect } from 'react';
import { BlockchainLedger } from './uln/BlockchainLedger';
import { AnalyticsDashboard } from './uln/AnalyticsDashboard';
import { OnboardingWizard } from './uln/OnboardingWizard';
import { InterLabelMessaging } from './uln/InterLabelMessaging';
import { LabelCatalog } from './uln/LabelCatalog';
import { LabelDistributionStatus } from './uln/LabelDistributionStatus';
import { LabelAuditSnapshot } from './uln/LabelAuditSnapshot';
import { LabelGovernance } from './uln/LabelGovernance';
import { LabelDisputes } from './uln/LabelDisputes';
import { LabelMembers } from './uln/LabelMembers';
import { ULNOverview } from './uln/ULNOverview';
import { LabelHub } from './uln/LabelHub';
import { CrossLabelContentSharing } from './uln/CrossLabelContentSharing';
import { RoyaltyPoolManagement } from './uln/RoyaltyPoolManagement';
import { DAOGovernance } from './uln/DAOGovernance';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

export const ULNDashboard = () => {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [myLabels, setMyLabels] = useState([]);
  const [activeLabel, setActiveLabel] = useState(null);
  const [showLabelSwitcher, setShowLabelSwitcher] = useState(false);

  useEffect(() => {
    fetchDashboardStats();
    fetchMyLabels();
  }, []);

  const fetchMyLabels = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      const res = await fetch(`${API}/api/uln/me/labels`, {
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      if (res.ok) {
        const data = await res.json();
        setMyLabels(data.labels || []);
        if (data.labels?.length > 0 && !activeLabel) {
          setActiveLabel(data.labels[0]);
        }
      }
    } catch (e) {
      console.error('Failed to load labels:', e);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please log in.');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API}/api/uln/dashboard/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardStats(data.dashboard_stats);
        setError('');
      } else if (response.status === 401) {
        setError('Session expired. Please log in again.');
        localStorage.removeItem('token');
      } else {
        setError('Failed to load ULN dashboard data');
      }
    } catch (error) {
      console.error('ULN dashboard fetch error:', error);
      setError('Error connecting to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header with Label Switcher */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Unified Label Network</h1>
            <p className="text-lg text-gray-600">
              Complete ecosystem for cross-label collaboration, content sharing, and royalty distribution
            </p>
          </div>
          {/* Label Switcher */}
          {myLabels.length > 0 && (
            <div className="relative" data-testid="label-switcher-container">
              <button
                onClick={() => setShowLabelSwitcher(!showLabelSwitcher)}
                className="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-4 py-2.5 shadow-sm hover:shadow transition min-w-[220px]"
                data-testid="label-switcher-btn"
              >
                <span className="w-8 h-8 rounded-lg bg-purple-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                  {(activeLabel?.name || '?')[0].toUpperCase()}
                </span>
                <div className="text-left flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">{activeLabel?.name || 'Select Label'}</p>
                  <p className="text-[10px] text-gray-500 capitalize">{activeLabel?.role || ''} &middot; {activeLabel?.member_count || 0} members</p>
                </div>
                <svg className={`w-4 h-4 text-gray-400 transition ${showLabelSwitcher ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              </button>
              {showLabelSwitcher && (
                <div className="absolute right-0 top-full mt-1 w-72 bg-white border border-gray-200 rounded-xl shadow-lg z-50 max-h-80 overflow-y-auto" data-testid="label-switcher-dropdown">
                  <div className="p-2">
                    <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wide px-2 py-1">My Labels ({myLabels.length})</p>
                    {myLabels.map((lbl) => (
                      <button
                        key={lbl.label_id}
                        onClick={() => { setActiveLabel(lbl); setShowLabelSwitcher(false); }}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition ${
                          activeLabel?.label_id === lbl.label_id ? 'bg-purple-50 ring-1 ring-purple-200' : 'hover:bg-gray-50'
                        }`}
                        data-testid={`label-switch-${lbl.label_id}`}
                      >
                        <span className="w-7 h-7 rounded-md bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-[10px] shrink-0">
                          {(lbl.name || '?')[0].toUpperCase()}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-gray-800 truncate">{lbl.name}</p>
                          <p className="text-[10px] text-gray-400 capitalize">{lbl.role} &middot; {lbl.label_type}</p>
                        </div>
                        {activeLabel?.label_id === lbl.label_id && (
                          <span className="w-2 h-2 rounded-full bg-purple-600 shrink-0"></span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <nav className="flex flex-wrap gap-2 px-6 py-4">
            {['overview', 'labels', 'members', 'catalog', 'distribution', 'governance', 'disputes', 'audit', 'content', 'royalties', 'dao', 'blockchain', 'analytics', 'onboarding', 'messaging'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                data-testid={`uln-tab-${tab}`}
                className={`capitalize font-medium py-2 px-4 rounded-md transition-colors ${
                  activeTab === tab 
                    ? 'bg-purple-100 text-purple-700' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab === 'dao' ? 'DAO Governance' : tab === 'onboarding' ? 'Register Label' : tab === 'messaging' ? 'Messages' : tab === 'members' ? 'Members' : tab === 'catalog' ? 'Catalog' : tab === 'distribution' ? 'Distribution' : tab === 'audit' ? 'Audit Snapshot' : tab === 'governance' ? 'Governance' : tab === 'disputes' ? 'Disputes' : tab.replace('_', ' ')}
              </button>
            ))}
          </nav>
        </div>

        {/* Dashboard Content */}
        {dashboardStats && (
          <>
            {activeTab === 'overview' && <ULNOverview stats={dashboardStats} />}
            {activeTab === 'labels' && <LabelHub />}
            {activeTab === 'members' && <LabelMembers activeLabel={activeLabel} onMemberChange={() => fetchMyLabels()} />}
            {activeTab === 'catalog' && <LabelCatalog activeLabel={activeLabel} />}
            {activeTab === 'distribution' && <LabelDistributionStatus activeLabel={activeLabel} />}
            {activeTab === 'governance' && <LabelGovernance activeLabel={activeLabel} />}
            {activeTab === 'disputes' && <LabelDisputes activeLabel={activeLabel} />}
            {activeTab === 'audit' && <LabelAuditSnapshot activeLabel={activeLabel} />}
            {activeTab === 'content' && <CrossLabelContentSharing />}
            {activeTab === 'royalties' && <RoyaltyPoolManagement />}
            {activeTab === 'dao' && <DAOGovernance />}
            {activeTab === 'blockchain' && (
              <div className="bg-slate-900 rounded-lg p-6"><BlockchainLedger /></div>
            )}
            {activeTab === 'analytics' && (
              <div className="bg-slate-900 rounded-lg p-6"><AnalyticsDashboard /></div>
            )}
            {activeTab === 'onboarding' && (
              <div className="bg-slate-900 rounded-lg p-6"><OnboardingWizard /></div>
            )}
            {activeTab === 'messaging' && (
              <div className="bg-slate-900 rounded-lg p-6"><InterLabelMessaging /></div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ULNDashboard;
