import React, { useState } from 'react';
import { useAuth } from './contexts/AuthContext';
import { ProfileEditor, SocialMediaConnections } from './CreatorProfileComponents';

const ProfileSettings = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [saveMessage, setSaveMessage] = useState('');

  const handleSave = () => {
    setSaveMessage('Profile updated successfully!');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Profile Settings</h1>
          <p className="text-gray-400">Manage your creator profile and connections</p>
        </div>

        {saveMessage && (
          <div className="bg-green-500/20 border border-green-500 text-green-200 px-6 py-4 rounded-lg mb-6">
            {saveMessage}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-gray-800 rounded-xl shadow-xl mb-6">
          <div className="flex border-b border-gray-700">
            {[
              { id: 'profile', label: 'Profile Info', icon: '👤' },
              { id: 'social', label: 'Social Media', icon: '🔗' },
              { id: 'privacy', label: 'Privacy', icon: '🔒' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-semibold text-sm transition-colors flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'text-purple-400 border-b-2 border-purple-500 bg-gray-900/50'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'profile' && (
            <ProfileEditor user={user} onSave={handleSave} />
          )}

          {activeTab === 'social' && (
            <>
              <SocialMediaConnections />
              
              <div className="bg-gray-800 rounded-xl shadow-xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">Connected Accounts</h3>
                <p className="text-gray-400 mb-4">
                  Connect your social media accounts to display insights and activity on your creator profile.
                </p>
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">ℹ️</span>
                    <div>
                      <p className="text-blue-300 font-semibold mb-1">About OAuth Connections</p>
                      <p className="text-sm text-blue-200/70">
                        Your credentials are securely managed through OAuth. We never store your passwords.
                        You can disconnect at any time.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'privacy' && (
            <div className="bg-gray-800 rounded-xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-white mb-6">Privacy Settings</h3>
              
              <div className="space-y-6">
                <div className="flex items-start justify-between py-4 border-b border-gray-700">
                  <div>
                    <h4 className="text-white font-semibold mb-1">Public Profile</h4>
                    <p className="text-sm text-gray-400">
                      Make your profile visible to everyone on the platform
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>

                <div className="flex items-start justify-between py-4 border-b border-gray-700">
                  <div>
                    <h4 className="text-white font-semibold mb-1">Show Earnings</h4>
                    <p className="text-sm text-gray-400">
                      Display your earnings and royalty information publicly
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>

                <div className="flex items-start justify-between py-4 border-b border-gray-700">
                  <div>
                    <h4 className="text-white font-semibold mb-1">DAO Activity</h4>
                    <p className="text-sm text-gray-400">
                      Show your DAO proposals and voting history
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>

                <div className="flex items-start justify-between py-4">
                  <div>
                    <h4 className="text-white font-semibold mb-1">Social Media Insights</h4>
                    <p className="text-sm text-gray-400">
                      Display connected social media metrics on your profile
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;