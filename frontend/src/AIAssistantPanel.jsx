import React, { useState } from 'react';
import { toast } from 'sonner';
import {
  Type, Palette, Layout, Maximize2, Sparkles, Copy, Check,
  ChevronDown, Loader2
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// ==================== AI Assistant Panel ====================
export const AIAssistantPanel = ({ projectId, canvasSize, onApplyLayout, onApplyPalette }) => {
  const [activeTab, setActiveTab] = useState('text');
  const [loading, setLoading] = useState(false);

  // Text generation state
  const [textPrompt, setTextPrompt] = useState('');
  const [textType, setTextType] = useState('headline');
  const [textTone, setTextTone] = useState('professional');
  const [textResults, setTextResults] = useState([]);
  const [copiedIdx, setCopiedIdx] = useState(null);

  // Palette state
  const [palettePrompt, setPalettePrompt] = useState('');
  const [paletteMood, setPaletteMood] = useState('modern');
  const [paletteResults, setPaletteResults] = useState([]);

  // Layout state
  const [layoutPlatform, setLayoutPlatform] = useState('instagram_post');
  const [layoutResults, setLayoutResults] = useState([]);

  // Resize state
  const [resizePlatforms, setResizePlatforms] = useState([]);
  const [resizeResults, setResizeResults] = useState([]);

  const textTypes = [
    { id: 'headline', label: 'Headlines' },
    { id: 'caption', label: 'Captions' },
    { id: 'tagline', label: 'Taglines' },
    { id: 'cta', label: 'CTA Buttons' },
    { id: 'hashtags', label: 'Hashtags' },
    { id: 'description', label: 'Descriptions' }
  ];

  const tones = ['professional', 'casual', 'playful', 'bold', 'luxury', 'minimal'];
  const moods = ['modern', 'warm', 'cool', 'luxury'];
  const platforms = [
    { id: 'instagram_post', label: 'Instagram Post' },
    { id: 'instagram_story', label: 'Instagram Story' },
    { id: 'twitter_post', label: 'Twitter Post' },
    { id: 'facebook_post', label: 'Facebook Post' },
    { id: 'youtube_thumbnail', label: 'YouTube Thumbnail' },
    { id: 'linkedin_post', label: 'LinkedIn Post' }
  ];

  // ==================== Handlers ====================
  const handleGenerateText = async () => {
    if (!textPrompt.trim()) return;
    setLoading(true);
    setTextResults([]);
    try {
      const res = await fetch(`${API}/api/creative-studio/ai-assets/generate-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: textPrompt, text_type: textType, tone: textTone, count: 5 })
      });
      if (res.ok) {
        const data = await res.json();
        setTextResults(data.results || []);
      } else {
        toast.error('Text generation failed');
      }
    } catch (e) {
      toast.error('Failed to generate text');
    }
    setLoading(false);
  };

  const handleGeneratePalette = async () => {
    if (!palettePrompt.trim()) return;
    setLoading(true);
    setPaletteResults([]);
    try {
      const res = await fetch(`${API}/api/creative-studio/ai-assets/generate-palette`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: palettePrompt, mood: paletteMood, count: 5 })
      });
      if (res.ok) {
        const data = await res.json();
        setPaletteResults(data.colors || []);
      }
    } catch (e) {
      toast.error('Failed to generate palette');
    }
    setLoading(false);
  };

  const handleSuggestLayouts = async () => {
    setLoading(true);
    setLayoutResults([]);
    try {
      const res = await fetch(`${API}/api/creative-studio/ai-assets/suggest-layouts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content_type: 'promotional', platform: layoutPlatform })
      });
      if (res.ok) {
        const data = await res.json();
        setLayoutResults(data.layouts || []);
      }
    } catch (e) {
      toast.error('Failed to suggest layouts');
    }
    setLoading(false);
  };

  const handleSmartResize = async () => {
    if (!projectId || resizePlatforms.length === 0) return;
    setLoading(true);
    setResizeResults([]);
    try {
      const res = await fetch(`${API}/api/creative-studio/ai-assets/smart-resize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, target_platforms: resizePlatforms })
      });
      if (res.ok) {
        const data = await res.json();
        setResizeResults(data.resized_versions || []);
        toast.success(`Generated ${data.resized_versions?.length || 0} resized versions`);
      }
    } catch (e) {
      toast.error('Smart resize failed');
    }
    setLoading(false);
  };

  const copyToClipboard = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
    toast.success('Copied to clipboard');
  };

  const toggleResizePlatform = (p) => {
    setResizePlatforms(prev =>
      prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]
    );
  };

  const tabs = [
    { id: 'text', label: 'Text', icon: Type },
    { id: 'palette', label: 'Colors', icon: Palette },
    { id: 'layout', label: 'Layouts', icon: Layout },
    { id: 'resize', label: 'Resize', icon: Maximize2 }
  ];

  return (
    <div className="flex flex-col h-full" data-testid="ai-assistant-panel">
      {/* Header */}
      <div className="flex items-center gap-1.5 px-3 py-2 border-b border-slate-700/50">
        <Sparkles size={14} className="text-amber-400" />
        <span className="text-white text-xs font-semibold">AI Assistant</span>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-700/50">
        {tabs.map(t => (
          <button key={t.id} data-testid={`ai-tab-${t.id}`}
                  onClick={() => setActiveTab(t.id)}
                  className={`flex-1 py-2 px-1 text-[10px] font-medium flex flex-col items-center gap-0.5 transition-colors
                    ${activeTab === t.id ? 'text-amber-400 border-b-2 border-amber-400' : 'text-gray-500 hover:text-gray-300'}`}>
            <t.icon size={13} />
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">

        {/* Text Generation */}
        {activeTab === 'text' && (
          <div data-testid="ai-text-section">
            <p className="text-gray-400 text-[10px] uppercase font-bold mb-1.5">Generate Text</p>

            {/* Type selector */}
            <div className="flex flex-wrap gap-1 mb-2">
              {textTypes.map(t => (
                <button key={t.id} onClick={() => setTextType(t.id)}
                        className={`text-[10px] px-2 py-0.5 rounded-full transition-colors
                          ${textType === t.id ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-slate-700 text-gray-400 border border-transparent hover:bg-slate-600'}`}
                        data-testid={`text-type-${t.id}`}>
                  {t.label}
                </button>
              ))}
            </div>

            {/* Tone selector */}
            <div className="flex flex-wrap gap-1 mb-2">
              {tones.map(t => (
                <button key={t} onClick={() => setTextTone(t)}
                        className={`text-[9px] px-1.5 py-0.5 rounded transition-colors capitalize
                          ${textTone === t ? 'bg-purple-500/20 text-purple-300' : 'bg-slate-800 text-gray-500 hover:text-gray-300'}`}>
                  {t}
                </button>
              ))}
            </div>

            {/* Prompt input */}
            <textarea value={textPrompt} onChange={e => setTextPrompt(e.target.value)}
                      placeholder="Describe what you need text for..."
                      className="w-full bg-slate-700 text-white text-xs rounded px-2 py-1.5 border border-slate-600 focus:border-amber-500 outline-none resize-none h-16"
                      data-testid="ai-text-prompt" />

            <button onClick={handleGenerateText} disabled={loading || !textPrompt.trim()}
                    className="w-full mt-1.5 bg-gradient-to-r from-amber-600 to-orange-600 text-white text-xs py-1.5 rounded font-medium hover:from-amber-500 hover:to-orange-500 disabled:opacity-40 flex items-center justify-center gap-1.5"
                    data-testid="generate-text-btn">
              {loading ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
              Generate {textType}s
            </button>

            {/* Results */}
            {textResults.length > 0 && (
              <div className="mt-2 space-y-1" data-testid="text-results">
                {textResults.map((r, i) => (
                  <div key={i} className="flex items-start gap-1.5 p-1.5 bg-slate-700/50 rounded group hover:bg-slate-700"
                       data-testid={`text-result-${i}`}>
                    <p className="text-gray-200 text-[11px] flex-1 leading-relaxed">{r}</p>
                    <button onClick={() => copyToClipboard(r, i)}
                            className="shrink-0 opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-slate-600 transition-opacity"
                            data-testid={`copy-text-${i}`}>
                      {copiedIdx === i ? <Check size={10} className="text-green-400" /> : <Copy size={10} className="text-gray-400" />}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Color Palette */}
        {activeTab === 'palette' && (
          <div data-testid="ai-palette-section">
            <p className="text-gray-400 text-[10px] uppercase font-bold mb-1.5">AI Color Palette</p>

            {/* Mood selector */}
            <div className="flex gap-1 mb-2">
              {moods.map(m => (
                <button key={m} onClick={() => setPaletteMood(m)}
                        className={`text-[10px] px-2 py-0.5 rounded-full capitalize transition-colors
                          ${paletteMood === m ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-slate-700 text-gray-400 border border-transparent hover:bg-slate-600'}`}>
                  {m}
                </button>
              ))}
            </div>

            <input value={palettePrompt} onChange={e => setPalettePrompt(e.target.value)}
                   placeholder="e.g. fashion brand, tech startup..."
                   className="w-full bg-slate-700 text-white text-xs rounded px-2 py-1.5 border border-slate-600 focus:border-amber-500 outline-none"
                   data-testid="palette-prompt" />

            <button onClick={handleGeneratePalette} disabled={loading || !palettePrompt.trim()}
                    className="w-full mt-1.5 bg-gradient-to-r from-amber-600 to-orange-600 text-white text-xs py-1.5 rounded font-medium hover:from-amber-500 hover:to-orange-500 disabled:opacity-40 flex items-center justify-center gap-1.5"
                    data-testid="generate-palette-btn">
              {loading ? <Loader2 size={12} className="animate-spin" /> : <Palette size={12} />}
              Generate Palette
            </button>

            {/* Palette Results */}
            {paletteResults.length > 0 && (
              <div className="mt-2 space-y-1" data-testid="palette-results">
                <div className="flex gap-0.5 h-10 rounded-lg overflow-hidden">
                  {paletteResults.map((c, i) => (
                    <div key={i} className="flex-1 cursor-pointer group relative"
                         style={{ backgroundColor: c.hex }}
                         onClick={() => copyToClipboard(c.hex, `pal-${i}`)}
                         data-testid={`palette-color-${i}`}>
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 bg-black/40 transition-opacity">
                        <span className="text-white text-[9px] font-mono">{c.hex}</span>
                      </div>
                    </div>
                  ))}
                </div>
                {paletteResults.map((c, i) => (
                  <div key={i} className="flex items-center gap-2 px-1">
                    <div className="w-4 h-4 rounded" style={{ backgroundColor: c.hex }} />
                    <span className="text-gray-300 text-[10px] flex-1">{c.name}</span>
                    <span className="text-gray-500 text-[9px] font-mono">{c.hex}</span>
                    <span className="text-gray-600 text-[9px] capitalize">{c.usage}</span>
                  </div>
                ))}
                {onApplyPalette && (
                  <button onClick={() => onApplyPalette(paletteResults)}
                          className="w-full mt-1 text-[10px] text-amber-400 hover:text-amber-300 py-1 border border-amber-500/30 rounded hover:bg-amber-500/10"
                          data-testid="apply-palette-btn">
                    Apply to Brand Kit
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Layout Suggestions */}
        {activeTab === 'layout' && (
          <div data-testid="ai-layout-section">
            <p className="text-gray-400 text-[10px] uppercase font-bold mb-1.5">Layout Suggestions</p>

            <select value={layoutPlatform} onChange={e => setLayoutPlatform(e.target.value)}
                    className="w-full bg-slate-700 text-white text-xs rounded px-2 py-1.5 border border-slate-600 mb-1.5"
                    data-testid="layout-platform-select">
              {platforms.map(p => (
                <option key={p.id} value={p.id}>{p.label}</option>
              ))}
            </select>

            <button onClick={handleSuggestLayouts} disabled={loading}
                    className="w-full bg-gradient-to-r from-amber-600 to-orange-600 text-white text-xs py-1.5 rounded font-medium hover:from-amber-500 hover:to-orange-500 disabled:opacity-40 flex items-center justify-center gap-1.5"
                    data-testid="suggest-layouts-btn">
              {loading ? <Loader2 size={12} className="animate-spin" /> : <Layout size={12} />}
              Get Layout Ideas
            </button>

            {/* Layout Results */}
            {layoutResults.length > 0 && (
              <div className="mt-2 space-y-2" data-testid="layout-results">
                {layoutResults.map((layout, i) => (
                  <div key={i} className="bg-slate-700/50 rounded-lg p-2 border border-slate-600/30 hover:border-purple-500/30 cursor-pointer"
                       onClick={() => onApplyLayout && onApplyLayout(layout)}
                       data-testid={`layout-option-${i}`}>
                    {/* Mini preview */}
                    <div className="w-full h-16 rounded mb-1.5 relative overflow-hidden bg-slate-800">
                      {layout.elements?.slice(0, 3).map((el, j) => (
                        <div key={j} className="absolute rounded-sm"
                             style={{
                               left: `${(el.x / 1080) * 100}%`,
                               top: `${(el.y / 1080) * 100}%`,
                               width: `${(el.width / 1080) * 100}%`,
                               height: `${(el.height / 1080) * 100}%`,
                               backgroundColor: el.style?.backgroundColor || (el.type === 'text' ? 'transparent' : '#8b5cf6'),
                               opacity: 0.7
                             }} />
                      ))}
                    </div>
                    <p className="text-white text-xs font-medium">{layout.name}</p>
                    <p className="text-gray-500 text-[10px]">{layout.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Smart Resize */}
        {activeTab === 'resize' && (
          <div data-testid="ai-resize-section">
            <p className="text-gray-400 text-[10px] uppercase font-bold mb-1.5">Smart Resize</p>
            <p className="text-gray-500 text-[10px] mb-2">Adapt your design for multiple platforms</p>

            <div className="space-y-1 mb-2">
              {platforms.map(p => (
                <label key={p.id} className="flex items-center gap-2 p-1.5 rounded hover:bg-slate-700/30 cursor-pointer"
                       data-testid={`resize-platform-${p.id}`}>
                  <input type="checkbox" checked={resizePlatforms.includes(p.id)}
                         onChange={() => toggleResizePlatform(p.id)}
                         className="accent-amber-500 w-3 h-3" />
                  <span className="text-gray-300 text-xs">{p.label}</span>
                </label>
              ))}
            </div>

            <button onClick={handleSmartResize}
                    disabled={loading || !projectId || resizePlatforms.length === 0}
                    className="w-full bg-gradient-to-r from-amber-600 to-orange-600 text-white text-xs py-1.5 rounded font-medium hover:from-amber-500 hover:to-orange-500 disabled:opacity-40 flex items-center justify-center gap-1.5"
                    data-testid="smart-resize-btn">
              {loading ? <Loader2 size={12} className="animate-spin" /> : <Maximize2 size={12} />}
              Resize for {resizePlatforms.length} Platform{resizePlatforms.length !== 1 ? 's' : ''}
            </button>

            {/* Resize Results */}
            {resizeResults.length > 0 && (
              <div className="mt-2 space-y-1.5" data-testid="resize-results">
                {resizeResults.map((r, i) => (
                  <div key={i} className="bg-slate-700/50 rounded p-2 border border-slate-600/30"
                       data-testid={`resize-result-${i}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-200 text-xs capitalize">{r.platform?.replace(/_/g, ' ')}</span>
                      <span className="text-gray-500 text-[10px]">{r.width}x{r.height}</span>
                    </div>
                    <p className="text-gray-500 text-[10px]">{r.elements?.length || 0} elements adapted</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIAssistantPanel;
