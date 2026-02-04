import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';

import ContentModerationComponent from './ContentModerationComponent';
import CreativeEditor from './CreativeEditor';
const API = process.env.REACT_APP_BACKEND_URL;

// Creative Studio Dashboard Component
const CreativeStudioDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [projects, setProjects] = useState([]);
  const [brandKits, setBrandKits] = useState([]);
  const [aiHistory, setAiHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showBrandKitModal, setShowBrandKitModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [editingProject, setEditingProject] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, templatesRes, projectsRes, brandKitsRes] = await Promise.all([
        fetch(`${API}/api/creative-studio/stats`),
        fetch(`${API}/api/creative-studio/templates`),
        fetch(`${API}/api/creative-studio/projects`),
        fetch(`${API}/api/creative-studio/brand-kits`)
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (templatesRes.ok) setTemplates(await templatesRes.json());
      if (projectsRes.ok) {
        const data = await projectsRes.json();
        setProjects(data.projects || []);
      }
      if (brandKitsRes.ok) setBrandKits(await brandKitsRes.json());
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load Creative Studio data');
    }
    setLoading(false);
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '🎨' },
    { id: 'projects', label: 'Projects', icon: '📁' },
    { id: 'templates', label: 'Templates', icon: '📋' },
    { id: 'brand-kits', label: 'Brand Kits', icon: '🎯' },
    { id: 'ai-studio', label: 'AI Studio', icon: '🤖' },
    { id: 'moderation', label: 'Moderation', icon: '🛡️' },
    { id: 'publish', label: 'Publish', icon: '🚀' }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Creative Studio...</p>
        </div>
      </div>
    );
  if (editingProject) {
    return (
      <CreativeEditor 
        project={editingProject} 
        onClose={() => {
          setEditingProject(null);
          fetchData();
        }}
        onSave={(elements) => {
          toast.success('Project saved locally');
          setEditingProject(null);
        }}
      />
    );
  }

  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-black/30 border-b border-purple-500/30">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <span className="text-4xl">🎨</span>
                Creative Studio for Agencies
              </h1>
              <p className="text-purple-300 mt-1">AI-powered design creation and brand management</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowAIModal(true)}
                className="px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg hover:from-pink-600 hover:to-purple-700 transition-all flex items-center gap-2"
                data-testid="ai-generate-btn"
              >
                <span>🤖</span> AI Generate
              </button>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-lg hover:from-purple-600 hover:to-indigo-700 transition-all flex items-center gap-2"
                data-testid="create-project-btn"
              >
                <span>+</span> New Project
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
                    ? 'bg-purple-600 text-white'
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
          <OverviewTab stats={stats} projects={projects} templates={templates} />
        )}
        {activeTab === 'projects' && (
          <ProjectsTab 
            projects={projects} 
            onRefresh={fetchData}
            onCreateNew={() => setShowCreateModal(true)}
            onEdit={(project) => setEditingProject(project)}
          />
        )}
        {activeTab === 'templates' && (
          <TemplatesTab 
            templates={templates}
            selectedCategory={selectedCategory}
            setSelectedCategory={setSelectedCategory}
            selectedPlatform={selectedPlatform}
            setSelectedPlatform={setSelectedPlatform}
          />
        )}
        {activeTab === 'brand-kits' && (
          <BrandKitsTab 
            brandKits={brandKits}
            onRefresh={fetchData}
            onCreateNew={() => setShowBrandKitModal(true)}
          />
        )}
        {activeTab === 'ai-studio' && (
          <AIStudioTab 
            aiHistory={aiHistory}
            setAiHistory={setAiHistory}
          />
        )}
        {activeTab === 'moderation' && (
          <ContentModerationComponent />
        )}
        {activeTab === 'publish' && (
          <PublishTab projects={projects} />
        )}
      </div>

      {/* Modals */}
      {showCreateModal && (
        <CreateProjectModal 
          templates={templates}
          brandKits={brandKits}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchData();
            toast.success('Project created successfully!');
          }}
        />
      )}
      {showBrandKitModal && (
        <CreateBrandKitModal 
          onClose={() => setShowBrandKitModal(false)}
          onSuccess={() => {
            setShowBrandKitModal(false);
            fetchData();
            toast.success('Brand kit created successfully!');
          }}
        />
      )}
      {showAIModal && (
        <AIGenerateModal 
          brandKits={brandKits}
          onClose={() => setShowAIModal(false)}
        />
      )}
    </div>
  );
};

// Overview Tab
const OverviewTab = ({ stats, projects, templates }) => {
  const recentProjects = projects?.slice(0, 4) || [];
  const popularTemplates = templates?.slice(0, 4) || [];

  return (
    <div className="space-y-6" data-testid="overview-tab">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Projects" 
          value={stats?.total_projects || 0} 
          icon="📁" 
          color="from-blue-500 to-cyan-500"
        />
        <StatCard 
          title="In Progress" 
          value={stats?.projects_in_progress || 0} 
          icon="🔄" 
          color="from-yellow-500 to-orange-500"
        />
        <StatCard 
          title="Published" 
          value={stats?.projects_published || 0} 
          icon="✅" 
          color="from-green-500 to-emerald-500"
        />
        <StatCard 
          title="Brand Kits" 
          value={stats?.total_brand_kits || 0} 
          icon="🎯" 
          color="from-purple-500 to-pink-500"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
        <h3 className="text-white font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickActionCard title="Instagram Post" icon="📸" dims="1080x1080" />
          <QuickActionCard title="Story/Reel" icon="📱" dims="1080x1920" />
          <QuickActionCard title="YouTube Thumbnail" icon="🎬" dims="1280x720" />
          <QuickActionCard title="Twitter Post" icon="🐦" dims="1200x675" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Projects */}
        <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>📁</span> Recent Projects
          </h3>
          {recentProjects.length > 0 ? (
            <div className="space-y-3">
              {recentProjects.map(project => (
                <ProjectCard key={project.id} project={project} compact />
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">No projects yet. Create your first project!</p>
          )}
        </div>

        {/* Popular Templates */}
        <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>📋</span> Popular Templates
          </h3>
          {popularTemplates.length > 0 ? (
            <div className="grid grid-cols-2 gap-3">
              {popularTemplates.map(template => (
                <TemplateCard key={template.id} template={template} compact />
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">Templates loading...</p>
          )}
        </div>
      </div>
    </div>
  );
};

// Projects Tab
const ProjectsTab = ({ projects, onRefresh, onCreateNew, onEdit }) => {
  const [filter, setFilter] = useState('all');
  
  const filteredProjects = projects?.filter(p => 
    filter === 'all' || p.status === filter
  ) || [];

  return (
    <div className="space-y-6" data-testid="projects-tab">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {['all', 'draft', 'in_progress', 'review', 'published'].map(status => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1 rounded-lg text-sm ${
                filter === status
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }`}
            >
              {status === 'all' ? 'All' : status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
        <button
          onClick={onCreateNew}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          + New Project
        </button>
      </div>

      {filteredProjects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredProjects.map(project => (
            <ProjectCard key={project.id} project={project} onClick={() => onEdit && onEdit(project)} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white/5 rounded-xl border border-dashed border-purple-500/30">
          <div className="text-6xl mb-4">📁</div>
          <h3 className="text-white text-xl font-semibold mb-2">No Projects Yet</h3>
          <p className="text-gray-400 mb-4">Create your first project to get started</p>
          <button
            onClick={onCreateNew}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-lg"
          >
            Create Project
          </button>
        </div>
      )}
    </div>
  );
};

// Templates Tab
const TemplatesTab = ({ templates, selectedCategory, setSelectedCategory, selectedPlatform, setSelectedPlatform }) => {
  const categories = ['all', 'social_media', 'marketing', 'advertising', 'video_thumbnails', 'banners'];
  const platforms = ['all', 'instagram_post', 'instagram_story', 'twitter_post', 'youtube_thumbnail', 'facebook_post', 'linkedin_banner'];

  const filteredTemplates = templates?.filter(t => 
    (selectedCategory === 'all' || t.category === selectedCategory) &&
    (selectedPlatform === 'all' || t.platform === selectedPlatform)
  ) || [];

  return (
    <div className="space-y-6" data-testid="templates-tab">
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="text-gray-400 text-sm block mb-2">Category</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-white/10 text-white border border-purple-500/30 rounded-lg px-4 py-2"
          >
            {categories.map(cat => (
              <option key={cat} value={cat} className="bg-slate-800">
                {cat === 'all' ? 'All Categories' : cat.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-gray-400 text-sm block mb-2">Platform</label>
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="bg-white/10 text-white border border-purple-500/30 rounded-lg px-4 py-2"
          >
            {platforms.map(plat => (
              <option key={plat} value={plat} className="bg-slate-800">
                {plat === 'all' ? 'All Platforms' : plat.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredTemplates.map(template => (
          <TemplateCard key={template.id} template={template} />
        ))}
      </div>
    </div>
  );
};

// Brand Kits Tab
const BrandKitsTab = ({ brandKits, onRefresh, onCreateNew }) => {
  return (
    <div className="space-y-6" data-testid="brand-kits-tab">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">Brand Kits</h2>
        <button
          onClick={onCreateNew}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          data-testid="create-brand-kit-btn"
        >
          + New Brand Kit
        </button>
      </div>

      {brandKits?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {brandKits.map(kit => (
            <BrandKitCard key={kit.id} kit={kit} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-white/5 rounded-xl border border-dashed border-purple-500/30">
          <div className="text-6xl mb-4">🎯</div>
          <h3 className="text-white text-xl font-semibold mb-2">No Brand Kits Yet</h3>
          <p className="text-gray-400 mb-4">Create a brand kit to maintain consistent branding</p>
          <button
            onClick={onCreateNew}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-lg"
          >
            Create Brand Kit
          </button>
        </div>
      )}
    </div>
  );
};

// AI Studio Tab
const AIStudioTab = ({ aiHistory, setAiHistory }) => {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('photorealistic');
  const [generating, setGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);

  const styles = [
    { id: 'photorealistic', name: 'Photorealistic' },
    { id: 'illustration', name: 'Illustration' },
    { id: 'minimal', name: 'Minimal' },
    { id: '3d_render', name: '3D Render' },
    { id: 'watercolor', name: 'Watercolor' },
    { id: 'pop_art', name: 'Pop Art' },
    { id: 'vintage', name: 'Vintage' },
    { id: 'neon', name: 'Neon' },
    { id: 'gradient', name: 'Gradient' },
    { id: 'abstract', name: 'Abstract' }
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch(`${API}/api/creative-studio/ai/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, style, width: 1024, height: 1024 })
      });

      if (response.ok) {
        const result = await response.json();
        setGeneratedImage(result);
        setAiHistory(prev => [result, ...prev]);
        toast.success('Image generated successfully!');
      } else {
        throw new Error('Generation failed');
      }
    } catch (error) {
      console.error('AI generation error:', error);
      toast.error('Failed to generate image');
    }
    setGenerating(false);
  };

  return (
    <div className="space-y-6" data-testid="ai-studio-tab">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generation Panel */}
        <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>🤖</span> AI Image Generation
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="text-gray-400 text-sm block mb-2">Prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the image you want to create..."
                className="w-full bg-white/10 text-white border border-purple-500/30 rounded-lg px-4 py-3 min-h-[100px] resize-none"
                data-testid="ai-prompt-input"
              />
            </div>

            <div>
              <label className="text-gray-400 text-sm block mb-2">Style</label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {styles.map(s => (
                  <button
                    key={s.id}
                    onClick={() => setStyle(s.id)}
                    className={`px-3 py-2 rounded-lg text-sm ${
                      style === s.id
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/10 text-gray-300 hover:bg-white/20'
                    }`}
                  >
                    {s.name}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={generating}
              className="w-full px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
              data-testid="generate-ai-btn"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                  Generating...
                </>
              ) : (
                <>
                  <span>✨</span> Generate Image
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>🖼️</span> Preview
          </h3>
          
          {generatedImage ? (
            <div className="space-y-4">
              <div className="aspect-square bg-black/30 rounded-lg overflow-hidden flex items-center justify-center">
                <img 
                  src={generatedImage.image_url} 
                  alt="Generated" 
                  className="max-w-full max-h-full object-contain"
                />
              </div>
              <div className="text-gray-400 text-sm">
                <p><strong>Prompt:</strong> {generatedImage.prompt}</p>
                <p><strong>Size:</strong> {generatedImage.width}x{generatedImage.height}</p>
                <p><strong>Time:</strong> {generatedImage.generation_time_ms}ms</p>
              </div>
              <div className="flex gap-2">
                <button className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                  Add to Project
                </button>
                <button className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20">
                  Download
                </button>
              </div>
            </div>
          ) : (
            <div className="aspect-square bg-black/30 rounded-lg flex items-center justify-center">
              <div className="text-center text-gray-500">
                <div className="text-5xl mb-2">🎨</div>
                <p>Generated image will appear here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Generation History */}
      {aiHistory.length > 0 && (
        <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
          <h3 className="text-white font-semibold mb-4">Generation History</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {aiHistory.map((item, idx) => (
              <div key={idx} className="aspect-square bg-black/30 rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-purple-500">
                <img 
                  src={item.image_url} 
                  alt={item.prompt}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Publish Tab
const PublishTab = ({ projects }) => {
  const publishedProjects = projects?.filter(p => p.status === 'published') || [];
  const readyProjects = projects?.filter(p => p.status === 'approved' || p.status === 'review') || [];

  return (
    <div className="space-y-6" data-testid="publish-tab">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ready to Publish */}
        <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>📤</span> Ready to Publish
          </h3>
          {readyProjects.length > 0 ? (
            <div className="space-y-3">
              {readyProjects.map(project => (
                <div key={project.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div>
                    <h4 className="text-white font-medium">{project.name}</h4>
                    <p className="text-gray-400 text-sm">{project.platform?.replace('_', ' ')}</p>
                  </div>
                  <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                    Publish
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">No projects ready to publish</p>
          )}
        </div>

        {/* Recently Published */}
        <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <span>✅</span> Recently Published
          </h3>
          {publishedProjects.length > 0 ? (
            <div className="space-y-3">
              {publishedProjects.map(project => (
                <div key={project.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div>
                    <h4 className="text-white font-medium">{project.name}</h4>
                    <p className="text-gray-400 text-sm">{project.platform?.replace('_', ' ')}</p>
                  </div>
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                    Published
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">No published projects yet</p>
          )}
        </div>
      </div>

      {/* Platform Stats */}
      <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
        <h3 className="text-white font-semibold mb-4">Publishing Platforms</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            { name: 'Instagram', icon: '📸', connected: true },
            { name: 'Twitter/X', icon: '🐦', connected: true },
            { name: 'Facebook', icon: '📘', connected: false },
            { name: 'LinkedIn', icon: '💼', connected: true },
            { name: 'TikTok', icon: '🎵', connected: false },
            { name: 'YouTube', icon: '🎬', connected: true }
          ].map(platform => (
            <div 
              key={platform.name}
              className={`p-4 rounded-lg border text-center ${
                platform.connected 
                  ? 'bg-green-500/10 border-green-500/30' 
                  : 'bg-white/5 border-gray-600/30'
              }`}
            >
              <div className="text-3xl mb-2">{platform.icon}</div>
              <p className="text-white font-medium text-sm">{platform.name}</p>
              <p className={`text-xs ${platform.connected ? 'text-green-400' : 'text-gray-500'}`}>
                {platform.connected ? 'Connected' : 'Not Connected'}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Component Cards
const StatCard = ({ title, value, icon, color }) => (
  <div className={`bg-gradient-to-br ${color} p-6 rounded-xl shadow-lg`}>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-white/80 text-sm">{title}</p>
        <p className="text-3xl font-bold text-white">{value}</p>
      </div>
      <div className="text-4xl opacity-80">{icon}</div>
    </div>
  </div>
);

const QuickActionCard = ({ title, icon, dims }) => (
  <button className="p-4 bg-white/5 rounded-lg border border-purple-500/20 hover:bg-white/10 transition-all text-left">
    <div className="text-2xl mb-2">{icon}</div>
    <p className="text-white font-medium text-sm">{title}</p>
    <p className="text-gray-500 text-xs">{dims}</p>
  </button>
);

const ProjectCard = ({ project, compact = false, onClick }) => {
  const statusColors = {
    draft: 'bg-gray-500',
    in_progress: 'bg-yellow-500',
    review: 'bg-blue-500',
    approved: 'bg-purple-500',
    published: 'bg-green-500',
    archived: 'bg-gray-600'
  };

  if (compact) {
    return (
      <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all cursor-pointer">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white font-bold">
            {project.name?.charAt(0) || 'P'}
          </div>
          <div>
            <h4 className="text-white font-medium">{project.name}</h4>
            <p className="text-gray-400 text-sm">{project.category?.replace('_', ' ')}</p>
          </div>
        </div>
        <span className={`px-2 py-1 ${statusColors[project.status]} text-white text-xs rounded-full`}>
          {project.status?.replace('_', ' ')}
        </span>
      </div>
    );
  }

  return (
    <div className="bg-white/5 rounded-xl border border-purple-500/20 overflow-hidden hover:border-purple-500/40 transition-all cursor-pointer">
      <div className="aspect-video bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
        <div className="text-5xl opacity-50">🎨</div>
      </div>
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-white font-semibold">{project.name}</h4>
          <span className={`px-2 py-1 ${statusColors[project.status]} text-white text-xs rounded-full`}>
            {project.status?.replace('_', ' ')}
          </span>
        </div>
        <p className="text-gray-400 text-sm mb-3">{project.description || 'No description'}</p>
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{project.width}x{project.height}</span>
          <span>{project.platform?.replace('_', ' ') || project.category?.replace('_', ' ')}</span>
        </div>
      </div>
    </div>
  );
};

const TemplateCard = ({ template, compact = false }) => {
  if (compact) {
    return (
      <div className="p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all cursor-pointer">
        <div className="aspect-video bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-lg mb-2 flex items-center justify-center">
          <span className="text-2xl">📋</span>
        </div>
        <p className="text-white text-sm font-medium truncate">{template.name}</p>
        <p className="text-gray-500 text-xs">{template.width}x{template.height}</p>
      </div>
    );
  }

  return (
    <div className="bg-white/5 rounded-xl border border-purple-500/20 overflow-hidden hover:border-purple-500/40 transition-all cursor-pointer">
      <div className="aspect-video bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center">
        <div className="text-4xl opacity-50">📋</div>
      </div>
      <div className="p-4">
        <h4 className="text-white font-semibold mb-1">{template.name}</h4>
        <p className="text-gray-400 text-sm mb-2">{template.description || 'Design template'}</p>
        <div className="flex items-center justify-between text-xs">
          <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full">
            {template.category?.replace('_', ' ')}
          </span>
          <span className="text-gray-500">{template.width}x{template.height}</span>
        </div>
      </div>
    </div>
  );
};

const BrandKitCard = ({ kit }) => (
  <div className="bg-white/5 rounded-xl border border-purple-500/20 p-6 hover:border-purple-500/40 transition-all cursor-pointer">
    <div className="flex items-center gap-3 mb-4">
      <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
        {kit.name?.charAt(0) || 'B'}
      </div>
      <div>
        <h4 className="text-white font-semibold">{kit.name}</h4>
        <p className="text-gray-400 text-sm">{kit.description || 'Brand kit'}</p>
      </div>
    </div>
    
    {/* Colors Preview */}
    {kit.colors?.length > 0 && (
      <div className="mb-4">
        <p className="text-gray-400 text-xs mb-2">Colors</p>
        <div className="flex gap-1">
          {kit.colors.slice(0, 5).map((color, idx) => (
            <div 
              key={idx}
              className="w-8 h-8 rounded-lg border border-white/20"
              style={{ backgroundColor: color.hex_code }}
              title={color.name}
            />
          ))}
        </div>
      </div>
    )}

    {/* Fonts Preview */}
    {kit.fonts?.length > 0 && (
      <div>
        <p className="text-gray-400 text-xs mb-2">Fonts</p>
        <div className="flex flex-wrap gap-2">
          {kit.fonts.slice(0, 3).map((font, idx) => (
            <span key={idx} className="px-2 py-1 bg-white/10 text-gray-300 rounded text-xs">
              {font.name}
            </span>
          ))}
        </div>
      </div>
    )}
  </div>
);

// Modals
const CreateProjectModal = ({ templates, brandKits, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: 'social_media',
    platform: 'instagram_post',
    template_id: '',
    brand_kit_id: ''
  });
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error('Please enter a project name');
      return;
    }

    setCreating(true);
    try {
      const response = await fetch(`${API}/api/creative-studio/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onSuccess();
      } else {
        throw new Error('Failed to create project');
      }
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project');
    }
    setCreating(false);
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Create New Project</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">&times;</button>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="text-gray-300 text-sm block mb-2">Project Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="My Awesome Design"
              data-testid="project-name-input"
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2 min-h-[80px]"
              placeholder="Optional description..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-gray-300 text-sm block mb-2">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              >
                <option value="social_media">Social Media</option>
                <option value="marketing">Marketing</option>
                <option value="advertising">Advertising</option>
                <option value="video_thumbnails">Video Thumbnails</option>
                <option value="banners">Banners</option>
              </select>
            </div>

            <div>
              <label className="text-gray-300 text-sm block mb-2">Platform</label>
              <select
                value={formData.platform}
                onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              >
                <option value="instagram_post">Instagram Post</option>
                <option value="instagram_story">Instagram Story</option>
                <option value="twitter_post">Twitter Post</option>
                <option value="youtube_thumbnail">YouTube Thumbnail</option>
                <option value="facebook_post">Facebook Post</option>
                <option value="linkedin_banner">LinkedIn Banner</option>
              </select>
            </div>
          </div>

          {templates?.length > 0 && (
            <div>
              <label className="text-gray-300 text-sm block mb-2">Start from Template (Optional)</label>
              <select
                value={formData.template_id}
                onChange={(e) => setFormData({ ...formData, template_id: e.target.value })}
                className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              >
                <option value="">Blank Canvas</option>
                {templates.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
          )}

          {brandKits?.length > 0 && (
            <div>
              <label className="text-gray-300 text-sm block mb-2">Brand Kit (Optional)</label>
              <select
                value={formData.brand_kit_id}
                onChange={(e) => setFormData({ ...formData, brand_kit_id: e.target.value })}
                className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              >
                <option value="">No Brand Kit</option>
                {brandKits.map(b => (
                  <option key={b.id} value={b.id}>{b.name}</option>
                ))}
              </select>
            </div>
          )}

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
              className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              data-testid="submit-project-btn"
            >
              {creating ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const CreateBrandKitModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    colors: [
      { name: 'Primary', hex_code: '#6366f1', usage: 'primary' },
      { name: 'Secondary', hex_code: '#8b5cf6', usage: 'secondary' },
      { name: 'Accent', hex_code: '#ec4899', usage: 'accent' }
    ],
    fonts: [
      { name: 'Inter', family: 'Inter', weight: 'regular', usage: 'heading' }
    ],
    tagline: '',
    voice_tone: ''
  });
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error('Please enter a brand kit name');
      return;
    }

    setCreating(true);
    try {
      const response = await fetch(`${API}/api/creative-studio/brand-kits`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onSuccess();
      } else {
        throw new Error('Failed to create brand kit');
      }
    } catch (error) {
      console.error('Error creating brand kit:', error);
      toast.error('Failed to create brand kit');
    }
    setCreating(false);
  };

  const updateColor = (index, field, value) => {
    const newColors = [...formData.colors];
    newColors[index] = { ...newColors[index], [field]: value };
    setFormData({ ...formData, colors: newColors });
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Create Brand Kit</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">&times;</button>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="text-gray-300 text-sm block mb-2">Brand Kit Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="My Brand"
              data-testid="brand-kit-name-input"
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="Brand description..."
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Brand Colors</label>
            <div className="space-y-2">
              {formData.colors.map((color, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <input
                    type="color"
                    value={color.hex_code}
                    onChange={(e) => updateColor(idx, 'hex_code', e.target.value)}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={color.name}
                    onChange={(e) => updateColor(idx, 'name', e.target.value)}
                    className="flex-1 bg-slate-700 text-white border border-slate-600 rounded-lg px-3 py-2 text-sm"
                    placeholder="Color name"
                  />
                  <span className="text-gray-400 text-sm">{color.hex_code}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Tagline</label>
            <input
              type="text"
              value={formData.tagline}
              onChange={(e) => setFormData({ ...formData, tagline: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="Your brand tagline..."
            />
          </div>

          <div>
            <label className="text-gray-300 text-sm block mb-2">Voice & Tone</label>
            <textarea
              value={formData.voice_tone}
              onChange={(e) => setFormData({ ...formData, voice_tone: e.target.value })}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              placeholder="Professional, friendly, innovative..."
            />
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
              className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              data-testid="submit-brand-kit-btn"
            >
              {creating ? 'Creating...' : 'Create Brand Kit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const AIGenerateModal = ({ brandKits, onClose }) => {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('photorealistic');
  const [brandKitId, setBrandKitId] = useState('');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch(`${API}/api/creative-studio/ai/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt, 
          style, 
          width: 1024, 
          height: 1024,
          brand_kit_id: brandKitId || undefined
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('Image generated!');
      } else {
        throw new Error('Generation failed');
      }
    } catch (error) {
      console.error('AI generation error:', error);
      toast.error('Failed to generate image');
    }
    setGenerating(false);
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span>🤖</span> AI Image Generation
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">&times;</button>
          </div>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="text-gray-300 text-sm block mb-2">Describe your image</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-3 min-h-[100px]"
              placeholder="A professional photo of a modern office with plants, warm lighting, minimalist design..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-gray-300 text-sm block mb-2">Style</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
              >
                <option value="photorealistic">Photorealistic</option>
                <option value="illustration">Illustration</option>
                <option value="minimal">Minimal</option>
                <option value="3d_render">3D Render</option>
                <option value="watercolor">Watercolor</option>
                <option value="pop_art">Pop Art</option>
              </select>
            </div>

            {brandKits?.length > 0 && (
              <div>
                <label className="text-gray-300 text-sm block mb-2">Apply Brand Colors</label>
                <select
                  value={brandKitId}
                  onChange={(e) => setBrandKitId(e.target.value)}
                  className="w-full bg-slate-700 text-white border border-slate-600 rounded-lg px-4 py-2"
                >
                  <option value="">No Brand Kit</option>
                  {brandKits.map(b => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {result && (
            <div className="bg-slate-700/50 rounded-lg p-4">
              <div className="aspect-square max-w-sm mx-auto bg-black/30 rounded-lg overflow-hidden mb-4">
                <img 
                  src={result.image_url} 
                  alt="Generated" 
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="text-gray-400 text-sm text-center">
                Generated in {result.generation_time_ms}ms
              </div>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600"
            >
              Close
            </button>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                  Generating...
                </>
              ) : (
                <>
                  <span>✨</span> Generate
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreativeStudioDashboard;
