import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// ============================================
// DIGITAL TWIN CREATION
// ============================================

export const CreateDigitalTwin = ({ modelId, modelData, onCreated }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: modelData?.name || '',
    hair_color: '',
    eye_color: '',
    skin_tone: '',
    face_shape: '',
    height: '',
    build: '',
    distinctive_features: '',
    style_keywords: ''
  });
  const [twinType, setTwinType] = useState('avatar_2d');
  const [style, setStyle] = useState('photorealistic');

  const twinTypes = [
    { value: 'avatar_2d', label: '2D Avatar', desc: 'Social media & campaigns' },
    { value: 'avatar_3d', label: '3D Avatar', desc: 'AR, VR & Metaverse ready' },
    { value: 'full_body', label: 'Full Body', desc: 'Fashion & e-commerce' },
    { value: 'headshot', label: 'Headshot', desc: 'Corporate & editorial' },
    { value: 'stylized', label: 'Stylized', desc: 'Unique brand collaborations' },
    { value: 'realistic', label: 'Realistic', desc: 'Indistinguishable from photos' }
  ];

  const styles = [
    { value: 'photorealistic', label: 'Photorealistic' },
    { value: 'fashion_editorial', label: 'Fashion Editorial' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'artistic', label: 'Artistic' },
    { value: 'anime', label: 'Anime' },
    { value: 'cyberpunk', label: 'Cyberpunk' },
    { value: 'minimal', label: 'Minimal' },
    { value: 'luxury', label: 'Luxury' }
  ];

  const createTwin = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const modelPayload = {
        name: formData.name,
        hair_color: formData.hair_color,
        eye_color: formData.eye_color,
        skin_tone: formData.skin_tone,
        face_shape: formData.face_shape,
        height: formData.height,
        build: formData.build,
        distinctive_features: formData.distinctive_features.split(',').map(f => f.trim()).filter(Boolean),
        style_keywords: formData.style_keywords.split(',').map(k => k.trim()).filter(Boolean)
      };

      const response = await fetch(
        `${API}/digital-twin/create?model_id=${modelId}&twin_type=${twinType}&style=${style}&generate_immediately=true`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(modelPayload)
        }
      );

      if (response.ok) {
        const twin = await response.json();
        toast.success('Digital Twin created successfully!');
        onCreated?.(twin);
      } else {
        toast.error('Failed to create Digital Twin');
      }
    } catch (error) {
      toast.error('Error creating Digital Twin');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6" data-testid="create-digital-twin">
      <h2 className="text-2xl font-bold text-white mb-6">Create Digital Twin</h2>
      
      <div className="grid md:grid-cols-2 gap-6">
        {/* Model Features */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-purple-400 mb-3">Model Features</h3>
          
          <div>
            <label className="block text-sm text-slate-400 mb-1">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
              placeholder="Model name"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Hair Color</label>
              <input
                type="text"
                value={formData.hair_color}
                onChange={(e) => setFormData({...formData, hair_color: e.target.value})}
                className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600"
                placeholder="e.g., dark brown"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Eye Color</label>
              <input
                type="text"
                value={formData.eye_color}
                onChange={(e) => setFormData({...formData, eye_color: e.target.value})}
                className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600"
                placeholder="e.g., blue"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Skin Tone</label>
              <input
                type="text"
                value={formData.skin_tone}
                onChange={(e) => setFormData({...formData, skin_tone: e.target.value})}
                className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600"
                placeholder="e.g., olive"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Face Shape</label>
              <input
                type="text"
                value={formData.face_shape}
                onChange={(e) => setFormData({...formData, face_shape: e.target.value})}
                className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600"
                placeholder="e.g., oval"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Height</label>
              <input
                type="text"
                value={formData.height}
                onChange={(e) => setFormData({...formData, height: e.target.value})}
                className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600"
                placeholder="e.g., 5ft 10in"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Build</label>
              <input
                type="text"
                value={formData.build}
                onChange={(e) => setFormData({...formData, build: e.target.value})}
                className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg border border-slate-600"
                placeholder="e.g., athletic"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Distinctive Features (comma-separated)</label>
            <input
              type="text"
              value={formData.distinctive_features}
              onChange={(e) => setFormData({...formData, distinctive_features: e.target.value})}
              className="w-full bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
              placeholder="e.g., high cheekbones, dimples"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Style Keywords (comma-separated)</label>
            <input
              type="text"
              value={formData.style_keywords}
              onChange={(e) => setFormData({...formData, style_keywords: e.target.value})}
              className="w-full bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
              placeholder="e.g., elegant, sophisticated, modern"
            />
          </div>
        </div>

        {/* Twin Configuration */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-purple-400 mb-3">Twin Configuration</h3>
          
          <div>
            <label className="block text-sm text-slate-400 mb-2">Twin Type</label>
            <div className="grid grid-cols-2 gap-2">
              {twinTypes.map(type => (
                <button
                  key={type.value}
                  onClick={() => setTwinType(type.value)}
                  className={`p-3 rounded-lg text-left transition-all ${
                    twinType === type.value
                      ? 'bg-purple-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  <div className="font-medium text-sm">{type.label}</div>
                  <div className="text-xs opacity-70">{type.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">Visual Style</label>
            <div className="grid grid-cols-2 gap-2">
              {styles.map(s => (
                <button
                  key={s.value}
                  onClick={() => setStyle(s.value)}
                  className={`px-4 py-2 rounded-lg text-sm transition-all ${
                    style === s.value
                      ? 'bg-amber-500 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 p-4 bg-slate-700/50 rounded-lg">
            <h4 className="font-medium text-white mb-2">Twin Capabilities</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className={twinType === 'avatar_3d' || twinType === 'full_body' ? 'text-green-400' : 'text-slate-500'}>
                  {twinType === 'avatar_3d' || twinType === 'full_body' ? '✓' : '○'}
                </span>
                <span className="text-slate-300">AR Try-On Compatible</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={twinType === 'avatar_3d' ? 'text-green-400' : 'text-slate-500'}>
                  {twinType === 'avatar_3d' ? '✓' : '○'}
                </span>
                <span className="text-slate-300">Metaverse Ready</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={twinType === 'avatar_3d' || twinType === 'full_body' ? 'text-green-400' : 'text-slate-500'}>
                  {twinType === 'avatar_3d' || twinType === 'full_body' ? '✓' : '○'}
                </span>
                <span className="text-slate-300">Motion Capture Ready</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✓</span>
                <span className="text-slate-300">Virtual Campaigns</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 flex justify-end">
        <button
          onClick={createTwin}
          disabled={loading || !formData.name}
          className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-3 rounded-lg font-semibold disabled:opacity-50 flex items-center gap-2"
          data-testid="create-twin-btn"
        >
          {loading ? (
            <>
              <span className="animate-spin">⟳</span>
              Generating Twin...
            </>
          ) : (
            <>
              <span>✨</span>
              Create Digital Twin
            </>
          )}
        </button>
      </div>
    </div>
  );
};

// ============================================
// DIGITAL TWIN CARD
// ============================================

export const DigitalTwinCard = ({ twin, onSelect }) => {
  return (
    <div 
      className="bg-slate-800 rounded-xl overflow-hidden hover:ring-2 hover:ring-purple-500 transition-all cursor-pointer"
      onClick={() => onSelect?.(twin)}
      data-testid={`twin-card-${twin.twin_id}`}
    >
      {/* Avatar Image */}
      <div className="aspect-square bg-slate-700 relative">
        {twin.base_avatar_url ? (
          <img 
            src={twin.base_avatar_url} 
            alt={twin.model_name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-500">
            <span className="text-4xl">👤</span>
          </div>
        )}
        
        {/* Status Badge */}
        <div className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium ${
          twin.status === 'active' ? 'bg-green-500 text-white' :
          twin.status === 'generating' ? 'bg-yellow-500 text-black' :
          'bg-slate-600 text-slate-300'
        }`}>
          {twin.status}
        </div>
        
        {/* Capabilities Icons */}
        <div className="absolute bottom-2 left-2 flex gap-1">
          {twin.ar_compatible && (
            <span className="bg-blue-500/80 text-white text-xs px-2 py-0.5 rounded" title="AR Compatible">AR</span>
          )}
          {twin.metaverse_compatible && (
            <span className="bg-purple-500/80 text-white text-xs px-2 py-0.5 rounded" title="Metaverse Ready">🌐</span>
          )}
        </div>
      </div>
      
      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold text-white truncate">{twin.model_name}</h3>
        <p className="text-sm text-slate-400 capitalize">{twin.style?.replace('_', ' ')} • {twin.twin_type?.replace('_', ' ')}</p>
        
        <div className="mt-3 flex justify-between items-center text-sm">
          <span className="text-slate-400">{twin.total_campaigns || 0} campaigns</span>
          <span className="text-green-400 font-medium">${(twin.total_revenue || 0).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};

// ============================================
// DIGITAL TWIN DETAIL VIEW
// ============================================

export const DigitalTwinDetail = ({ twin, onBack }) => {
  const [analytics, setAnalytics] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (twin?.twin_id) {
      fetchAnalytics();
      fetchRecommendations();
    }
  }, [twin]);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/digital-twin/${twin.twin_id}/analytics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/digital-twin/${twin.twin_id}/recommendations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations');
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'photoshoots', label: 'Virtual Photoshoots' },
    { id: 'licenses', label: 'Licenses' },
    { id: 'ar', label: 'AR Assets' },
    { id: 'metaverse', label: 'Metaverse' }
  ];

  return (
    <div className="space-y-6" data-testid="digital-twin-detail">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button 
          onClick={onBack}
          className="text-slate-400 hover:text-white"
        >
          ← Back
        </button>
        <h2 className="text-2xl font-bold text-white">{twin.model_name}'s Digital Twin</h2>
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Avatar Section */}
        <div className="lg:col-span-1">
          <div className="bg-slate-800 rounded-xl overflow-hidden">
            <div className="aspect-square bg-slate-700">
              {twin.base_avatar_url ? (
                <img 
                  src={twin.base_avatar_url} 
                  alt={twin.model_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-500">
                  <span className="text-6xl">👤</span>
                </div>
              )}
            </div>
            <div className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Status</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  twin.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-slate-600 text-slate-300'
                }`}>
                  {twin.status}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Type</span>
                <span className="text-white capitalize">{twin.twin_type?.replace('_', ' ')}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Style</span>
                <span className="text-white capitalize">{twin.style?.replace('_', ' ')}</span>
              </div>
              <div className="border-t border-slate-700 pt-3 mt-3">
                <div className="flex flex-wrap gap-2">
                  {twin.ar_compatible && (
                    <span className="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded">AR Ready</span>
                  )}
                  {twin.metaverse_compatible && (
                    <span className="bg-purple-500/20 text-purple-400 text-xs px-2 py-1 rounded">Metaverse</span>
                  )}
                  {twin.motion_capture_compatible && (
                    <span className="bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded">Motion Capture</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Details Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Stats */}
          {analytics && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Total Campaigns" value={analytics.total_campaigns || 0} />
              <StatCard label="Total Revenue" value={`$${(analytics.total_revenue || 0).toLocaleString()}`} />
              <StatCard label="Active Licenses" value={analytics.active_licenses || 0} />
              <StatCard label="Photoshoots" value={analytics.total_photoshoots || 0} />
            </div>
          )}

          {/* Tabs */}
          <div className="bg-slate-800 rounded-xl">
            <div className="flex border-b border-slate-700 overflow-x-auto">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
                    activeTab === tab.id
                      ? 'text-purple-400 border-b-2 border-purple-400'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="p-6">
              {activeTab === 'overview' && (
                <TwinOverviewTab twin={twin} recommendations={recommendations} />
              )}
              {activeTab === 'photoshoots' && (
                <VirtualPhotoshootTab twinId={twin.twin_id} />
              )}
              {activeTab === 'licenses' && (
                <LicensesTab twinId={twin.twin_id} />
              )}
              {activeTab === 'ar' && (
                <ARAssetsTab twinId={twin.twin_id} arCompatible={twin.ar_compatible} />
              )}
              {activeTab === 'metaverse' && (
                <MetaverseTab twinId={twin.twin_id} metaverseCompatible={twin.metaverse_compatible} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ label, value }) => (
  <div className="bg-slate-800 rounded-lg p-4">
    <div className="text-sm text-slate-400">{label}</div>
    <div className="text-xl font-bold text-white mt-1">{value}</div>
  </div>
);

// ============================================
// TAB COMPONENTS
// ============================================

const TwinOverviewTab = ({ twin, recommendations }) => (
  <div className="space-y-6">
    {/* Preserved Features */}
    <div>
      <h4 className="font-medium text-white mb-3">Preserved Features</h4>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {Object.entries(twin.preserved_features || {}).map(([key, value]) => (
          value && (
            <div key={key} className="bg-slate-700/50 rounded-lg p-3">
              <div className="text-xs text-slate-400 capitalize">{key.replace('_', ' ')}</div>
              <div className="text-sm text-white mt-1">
                {Array.isArray(value) ? value.join(', ') : value}
              </div>
            </div>
          )
        ))}
      </div>
    </div>

    {/* AI Recommendations */}
    {recommendations && !recommendations.error && (
      <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
        <h4 className="font-medium text-purple-400 mb-3">AI Revenue Recommendations</h4>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Revenue Potential:</span>
            <span className={`font-medium ${
              recommendations.revenue_potential === 'high' ? 'text-green-400' :
              recommendations.revenue_potential === 'medium' ? 'text-yellow-400' : 'text-slate-400'
            }`}>
              {recommendations.revenue_potential?.toUpperCase()}
            </span>
          </div>
          {recommendations.recommended_uses?.length > 0 && (
            <div>
              <span className="text-slate-400 text-sm">Recommended Uses:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {recommendations.recommended_uses.map((use, i) => (
                  <span key={i} className="bg-slate-700 text-slate-300 text-xs px-2 py-1 rounded">
                    {use}
                  </span>
                ))}
              </div>
            </div>
          )}
          {recommendations.pricing_suggestions?.length > 0 && (
            <div>
              <span className="text-slate-400 text-sm">Pricing Tips:</span>
              <ul className="mt-1 space-y-1">
                {recommendations.pricing_suggestions.map((tip, i) => (
                  <li key={i} className="text-sm text-slate-300">• {tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    )}

    {/* Allowed Uses */}
    <div>
      <h4 className="font-medium text-white mb-3">Allowed Usage Contexts</h4>
      <div className="flex flex-wrap gap-2">
        {(twin.allowed_uses || []).map((use, i) => (
          <span key={i} className="bg-green-500/20 text-green-400 text-sm px-3 py-1 rounded-full">
            {use.replace('_', ' ')}
          </span>
        ))}
      </div>
    </div>
  </div>
);

const VirtualPhotoshootTab = ({ twinId }) => {
  const [photoshoots, setPhotoshoots] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPhotoshoots();
  }, [twinId]);

  const fetchPhotoshoots = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/digital-twin/${twinId}/photoshoots`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setPhotoshoots(data);
      }
    } catch (error) {
      console.error('Failed to fetch photoshoots');
    } finally {
      setLoading(false);
    }
  };

  if (showCreate) {
    return (
      <CreateVirtualPhotoshoot 
        twinId={twinId} 
        onBack={() => setShowCreate(false)}
        onCreated={() => {
          setShowCreate(false);
          fetchPhotoshoots();
        }}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h4 className="font-medium text-white">Virtual Photoshoots</h4>
        <button
          onClick={() => setShowCreate(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm"
        >
          + New Photoshoot
        </button>
      </div>

      {loading ? (
        <div className="animate-pulse space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-16 bg-slate-700 rounded" />
          ))}
        </div>
      ) : photoshoots.length === 0 ? (
        <div className="text-center py-8 text-slate-400">
          No virtual photoshoots yet. Create your first one!
        </div>
      ) : (
        <div className="space-y-3">
          {photoshoots.map((ps) => (
            <div key={ps.photoshoot_id} className="bg-slate-700/50 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h5 className="font-medium text-white">{ps.concept}</h5>
                  <p className="text-sm text-slate-400">{ps.images_generated} images generated</p>
                </div>
                <div className="text-right">
                  <span className={`text-xs px-2 py-1 rounded ${
                    ps.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    ps.status === 'generating' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-slate-600 text-slate-400'
                  }`}>
                    {ps.status}
                  </span>
                  <p className="text-sm text-green-400 mt-1">${ps.total_price}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const CreateVirtualPhotoshoot = ({ twinId, onBack, onCreated }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    concept: '',
    style: 'fashion_editorial',
    background_setting: 'professional studio',
    outfit_description: 'elegant fashion attire',
    poses: 'confident stance, natural smile, profile view, dynamic pose, relaxed pose',
    num_images: 5
  });

  const createPhotoshoot = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const poses = formData.poses.split(',').map(p => p.trim()).filter(Boolean);
      
      const response = await fetch(
        `${API}/digital-twin/${twinId}/photoshoot?client_id=demo&client_name=Demo%20Client&style=${formData.style}&background_setting=${encodeURIComponent(formData.background_setting)}&outfit_description=${encodeURIComponent(formData.outfit_description)}&num_images=${formData.num_images}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(formData.concept)
        }
      );

      if (response.ok) {
        toast.success('Virtual photoshoot created!');
        onCreated();
      } else {
        toast.error('Failed to create photoshoot');
      }
    } catch (error) {
      toast.error('Error creating photoshoot');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <button onClick={onBack} className="text-slate-400 hover:text-white">←</button>
        <h4 className="font-medium text-white">Create Virtual Photoshoot</h4>
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-sm text-slate-400 mb-1">Concept</label>
          <input
            type="text"
            value={formData.concept}
            onChange={(e) => setFormData({...formData, concept: e.target.value})}
            className="w-full bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
            placeholder="e.g., Summer beach fashion campaign"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Background</label>
            <input
              type="text"
              value={formData.background_setting}
              onChange={(e) => setFormData({...formData, background_setting: e.target.value})}
              className="w-full bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Number of Images</label>
            <input
              type="number"
              min="1"
              max="10"
              value={formData.num_images}
              onChange={(e) => setFormData({...formData, num_images: parseInt(e.target.value) || 5})}
              className="w-full bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-1">Outfit Description</label>
          <input
            type="text"
            value={formData.outfit_description}
            onChange={(e) => setFormData({...formData, outfit_description: e.target.value})}
            className="w-full bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
          />
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-1">Poses (comma-separated)</label>
          <input
            type="text"
            value={formData.poses}
            onChange={(e) => setFormData({...formData, poses: e.target.value})}
            className="w-full bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
          />
        </div>
      </div>

      <button
        onClick={createPhotoshoot}
        disabled={loading || !formData.concept}
        className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg font-medium disabled:opacity-50"
      >
        {loading ? 'Generating Photoshoot...' : `Create Photoshoot ($${formData.num_images * 50})`}
      </button>
    </div>
  );
};

const LicensesTab = ({ twinId }) => {
  const [licenses, setLicenses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLicenses();
  }, [twinId]);

  const fetchLicenses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/digital-twin/${twinId}/licenses`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setLicenses(data);
      }
    } catch (error) {
      console.error('Failed to fetch licenses');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="animate-pulse h-32 bg-slate-700 rounded" />;

  return (
    <div className="space-y-4">
      <h4 className="font-medium text-white">Active Licenses</h4>
      {licenses.length === 0 ? (
        <div className="text-center py-8 text-slate-400">
          No licenses yet. License this twin to start earning!
        </div>
      ) : (
        <div className="space-y-3">
          {licenses.map((license) => (
            <div key={license.license_id} className="bg-slate-700/50 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h5 className="font-medium text-white">{license.licensee_name}</h5>
                  <p className="text-sm text-slate-400 capitalize">{license.license_type?.replace('_', ' ')}</p>
                </div>
                <span className="text-green-400 font-medium">${license.license_fee}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const ARAssetsTab = ({ twinId, arCompatible }) => {
  if (!arCompatible) {
    return (
      <div className="text-center py-8">
        <p className="text-slate-400">This twin is not AR compatible.</p>
        <p className="text-sm text-slate-500 mt-2">Upgrade to a 3D or Full Body twin to enable AR features.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h4 className="font-medium text-white">AR Try-On Assets</h4>
      <p className="text-slate-400 text-sm">Create AR-compatible assets for virtual try-on experiences.</p>
      <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm">
        + Create AR Asset
      </button>
    </div>
  );
};

const MetaverseTab = ({ twinId, metaverseCompatible }) => {
  if (!metaverseCompatible) {
    return (
      <div className="text-center py-8">
        <p className="text-slate-400">This twin is not metaverse compatible.</p>
        <p className="text-sm text-slate-500 mt-2">Upgrade to a 3D Avatar twin to enable metaverse features.</p>
      </div>
    );
  }

  const platforms = [
    { name: 'Decentraland', icon: '🏝️' },
    { name: 'The Sandbox', icon: '🎮' },
    { name: 'Roblox', icon: '🧱' },
    { name: 'Meta Horizon', icon: '🥽' }
  ];

  return (
    <div className="space-y-4">
      <h4 className="font-medium text-white">Metaverse Avatars</h4>
      <p className="text-slate-400 text-sm">Create avatars for various metaverse platforms.</p>
      <div className="grid grid-cols-2 gap-3">
        {platforms.map((platform) => (
          <button 
            key={platform.name}
            className="bg-slate-700/50 hover:bg-slate-700 p-4 rounded-lg text-left transition-colors"
          >
            <span className="text-2xl">{platform.icon}</span>
            <p className="text-white font-medium mt-2">{platform.name}</p>
            <p className="text-xs text-slate-400">Create Avatar</p>
          </button>
        ))}
      </div>
    </div>
  );
};

// ============================================
// DIGITAL TWIN GALLERY
// ============================================

export const DigitalTwinGallery = ({ agencyId }) => {
  const [twins, setTwins] = useState([]);
  const [selectedTwin, setSelectedTwin] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTwins();
  }, [agencyId]);

  const fetchTwins = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = agencyId 
        ? `${API}/digital-twin/agency/${agencyId}`
        : `${API}/digital-twin/model/demo-model`;
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTwins(data);
      }
    } catch (error) {
      console.error('Failed to fetch twins');
    } finally {
      setLoading(false);
    }
  };

  if (selectedTwin) {
    return (
      <DigitalTwinDetail 
        twin={selectedTwin} 
        onBack={() => setSelectedTwin(null)} 
      />
    );
  }

  if (showCreate) {
    return (
      <div className="space-y-4">
        <button 
          onClick={() => setShowCreate(false)}
          className="text-slate-400 hover:text-white"
        >
          ← Back to Gallery
        </button>
        <CreateDigitalTwin 
          modelId="demo-model"
          modelData={{ name: 'New Model' }}
          onCreated={(twin) => {
            setShowCreate(false);
            setTwins([twin, ...twins]);
          }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="digital-twin-gallery">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Digital Twins</h2>
        <button
          onClick={() => setShowCreate(true)}
          className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2"
        >
          <span>✨</span>
          Create Twin
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="animate-pulse bg-slate-800 rounded-xl h-64" />
          ))}
        </div>
      ) : twins.length === 0 ? (
        <div className="text-center py-16 bg-slate-800 rounded-xl">
          <span className="text-6xl">👤</span>
          <h3 className="text-xl font-semibold text-white mt-4">No Digital Twins Yet</h3>
          <p className="text-slate-400 mt-2">Create your first digital twin to unlock virtual campaigns!</p>
          <button
            onClick={() => setShowCreate(true)}
            className="mt-4 bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg"
          >
            Create Your First Twin
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {twins.map((twin) => (
            <DigitalTwinCard 
              key={twin.twin_id} 
              twin={twin} 
              onSelect={setSelectedTwin}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// MAIN DIGITAL TWIN DASHBOARD
// ============================================

export const DigitalTwinDashboard = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Digital Twin Studio</h1>
          <p className="text-slate-400 mt-2">
            Create AI-powered digital twins for virtual campaigns, AR try-ons, and metaverse presence
          </p>
        </div>
        
        <DigitalTwinGallery />
      </div>
    </div>
  );
};

export default DigitalTwinDashboard;
