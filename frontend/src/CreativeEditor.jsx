import React, { useState, useRef, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { 
  Type, Square, Circle, Image as ImageIcon, 
  Trash2, Save, X, Download, Copy,
  AlignLeft, AlignCenter, AlignRight,
  Bold, Italic, Layers, ChevronUp, ChevronDown,
  Undo2, Redo2, Grid3x3, Minus, Plus,
  Triangle, Star, Hexagon, ArrowRight,
  Sparkles
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

// Canvas presets for social media
const CANVAS_PRESETS = [
  { label: 'Instagram Post', w: 1080, h: 1080 },
  { label: 'Instagram Story', w: 1080, h: 1920 },
  { label: 'Twitter Post', w: 1200, h: 675 },
  { label: 'Facebook Post', w: 1200, h: 630 },
  { label: 'YouTube Thumbnail', w: 1280, h: 720 },
  { label: 'LinkedIn Banner', w: 1584, h: 396 },
  { label: 'Pinterest Pin', w: 1000, h: 1500 },
  { label: 'Custom', w: 800, h: 600 },
];

const CreativeEditor = ({ project, onClose, onSave }) => {
  const [elements, setElements] = useState(project?.elements || []);
  const [selectedId, setSelectedId] = useState(null);
  const [canvasSize, setCanvasSize] = useState({ 
    width: project?.width || 800, 
    height: project?.height || 600 
  });
  const [canvasBg, setCanvasBg] = useState('#ffffff');
  const [dragState, setDragState] = useState(null);
  const [resizeState, setResizeState] = useState(null);
  const [zoom, setZoom] = useState(0.6);
  const [showGrid, setShowGrid] = useState(false);
  const [history, setHistory] = useState([[]]);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [showPresetsPanel, setShowPresetsPanel] = useState(false);
  const [showAIPanel, setShowAIPanel] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiGenerating, setAiGenerating] = useState(false);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);

  // Push state to history on element changes
  const pushHistory = useCallback((newElements) => {
    setHistory(prev => {
      const trimmed = prev.slice(0, historyIndex + 1);
      return [...trimmed, JSON.parse(JSON.stringify(newElements))];
    });
    setHistoryIndex(prev => prev + 1);
  }, [historyIndex]);

  const undo = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      setElements(JSON.parse(JSON.stringify(history[newIndex])));
      setSelectedId(null);
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      setElements(JSON.parse(JSON.stringify(history[newIndex])));
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
        e.preventDefault();
        if (e.shiftKey) redo(); else undo();
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'd' && selectedId) {
        e.preventDefault();
        duplicateElement(selectedId);
      }
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedId && document.activeElement?.contentEditable !== 'true' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
          deleteElement(selectedId);
        }
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  });

  // --- Element Management ---
  const addElement = (type, content = '', extraStyle = {}) => {
    const id = Date.now().toString();
    const newElement = {
      id,
      type,
      x: canvasSize.width / 2 - (type === 'text' ? 100 : 50),
      y: canvasSize.height / 2 - (type === 'text' ? 25 : 50),
      width: type === 'text' ? 200 : 100,
      height: type === 'text' ? 50 : 100,
      content,
      style: {
        backgroundColor: type === 'rect' ? '#6366f1' : type === 'circle' ? '#ec4899' : type === 'triangle' ? '#f59e0b' : type === 'star' ? '#ef4444' : type === 'line' ? '#10b981' : 'transparent',
        color: '#000000',
        fontSize: 24,
        borderRadius: type === 'circle' ? '50%' : '0px',
        borderWidth: 0,
        borderColor: '#000000',
        textAlign: 'center',
        fontWeight: 'normal',
        fontStyle: 'normal',
        opacity: 1,
        ...extraStyle
      }
    };
    if (type === 'line') {
      newElement.width = 200;
      newElement.height = 4;
    }
    if (type === 'triangle') {
      newElement.style.clipPath = 'polygon(50% 0%, 0% 100%, 100% 100%)';
    }
    if (type === 'star') {
      newElement.style.clipPath = 'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)';
    }
    
    const newEls = [...elements, newElement];
    setElements(newEls);
    setSelectedId(id);
    pushHistory(newEls);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        const id = Date.now().toString();
        const aspectRatio = img.width / img.height;
        const width = 300;
        const height = width / aspectRatio;
        const newElement = {
          id, type: 'image',
          x: canvasSize.width / 2 - width / 2,
          y: canvasSize.height / 2 - height / 2,
          width, height,
          content: event.target.result,
          style: { borderWidth: 0, borderColor: 'transparent', opacity: 1, borderRadius: '0px' }
        };
        const newEls = [...elements, newElement];
        setElements(newEls);
        setSelectedId(id);
        pushHistory(newEls);
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const updateElement = (id, updates) => {
    setElements(prev => prev.map(el => el.id === id ? { ...el, ...updates } : el));
  };

  const updateStyle = (id, styleUpdates) => {
    const newEls = elements.map(el => 
      el.id === id ? { ...el, style: { ...el.style, ...styleUpdates } } : el
    );
    setElements(newEls);
    pushHistory(newEls);
  };

  const deleteElement = (id) => {
    const newEls = elements.filter(el => el.id !== id);
    setElements(newEls);
    setSelectedId(null);
    pushHistory(newEls);
  };

  const duplicateElement = (id) => {
    const el = elements.find(e => e.id === id);
    if (!el) return;
    const newEl = { ...JSON.parse(JSON.stringify(el)), id: Date.now().toString(), x: el.x + 20, y: el.y + 20 };
    const newEls = [...elements, newEl];
    setElements(newEls);
    setSelectedId(newEl.id);
    pushHistory(newEls);
  };

  const moveLayer = (id, direction) => {
    const index = elements.findIndex(el => el.id === id);
    if (index === -1) return;
    const newElements = [...elements];
    const element = newElements[index];
    newElements.splice(index, 1);
    if (direction === 'front') newElements.push(element);
    else if (direction === 'back') newElements.unshift(element);
    else if (direction === 'forward') newElements.splice(Math.min(index + 1, newElements.length), 0, element);
    else if (direction === 'backward') newElements.splice(Math.max(index - 1, 0), 0, element);
    setElements(newElements);
    pushHistory(newElements);
  };

  // --- Drag Logic ---
  const handleMouseDown = (e, id) => {
    e.stopPropagation();
    setSelectedId(id);
    const element = elements.find(el => el.id === id);
    if (!element) return;
    setDragState({ id, startX: e.clientX, startY: e.clientY, initialX: element.x, initialY: element.y });
  };

  const handleMouseMove = (e) => {
    if (resizeState) {
      const dx = (e.clientX - resizeState.startX) / zoom;
      const dy = (e.clientY - resizeState.startY) / zoom;
      const el = elements.find(el => el.id === resizeState.id);
      if (!el) return;

      let newW = resizeState.initialW;
      let newH = resizeState.initialH;
      let newX = resizeState.initialX;
      let newY = resizeState.initialY;
      const handle = resizeState.handle;

      if (handle.includes('e')) newW = Math.max(20, resizeState.initialW + dx);
      if (handle.includes('w')) { newW = Math.max(20, resizeState.initialW - dx); newX = resizeState.initialX + dx; }
      if (handle.includes('s')) newH = Math.max(20, resizeState.initialH + dy);
      if (handle.includes('n')) { newH = Math.max(20, resizeState.initialH - dy); newY = resizeState.initialY + dy; }

      updateElement(resizeState.id, { width: newW, height: newH, x: newX, y: newY });
      return;
    }
    if (!dragState) return;
    const dx = (e.clientX - dragState.startX) / zoom;
    const dy = (e.clientY - dragState.startY) / zoom;
    updateElement(dragState.id, { x: dragState.initialX + dx, y: dragState.initialY + dy });
  };

  const handleMouseUp = () => {
    if (dragState || resizeState) {
      pushHistory(elements);
    }
    setDragState(null);
    setResizeState(null);
  };

  const startResize = (e, id, handle) => {
    e.stopPropagation();
    e.preventDefault();
    const el = elements.find(el => el.id === id);
    if (!el) return;
    setResizeState({
      id, handle,
      startX: e.clientX, startY: e.clientY,
      initialW: el.width, initialH: el.height,
      initialX: el.x, initialY: el.y
    });
  };

  // --- Export ---
  const exportCanvas = () => {
    const canvas = document.createElement('canvas');
    canvas.width = canvasSize.width;
    canvas.height = canvasSize.height;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = canvasBg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const drawPromises = elements.map(el => {
      return new Promise((resolve) => {
        if (el.type === 'image' && el.content) {
          const img = new Image();
          img.crossOrigin = 'anonymous';
          img.onload = () => {
            ctx.globalAlpha = el.style.opacity ?? 1;
            ctx.drawImage(img, el.x, el.y, el.width, el.height);
            ctx.globalAlpha = 1;
            resolve();
          };
          img.onerror = resolve;
          img.src = el.content;
        } else if (el.type === 'text') {
          ctx.globalAlpha = el.style.opacity ?? 1;
          ctx.fillStyle = el.style.color || '#000';
          ctx.font = `${el.style.fontStyle === 'italic' ? 'italic ' : ''}${el.style.fontWeight === 'bold' ? 'bold ' : ''}${el.style.fontSize || 24}px sans-serif`;
          ctx.textAlign = el.style.textAlign || 'center';
          const tx = el.style.textAlign === 'left' ? el.x : el.style.textAlign === 'right' ? el.x + el.width : el.x + el.width / 2;
          ctx.fillText(el.content || '', tx, el.y + el.height / 2 + (el.style.fontSize || 24) / 3);
          ctx.globalAlpha = 1;
          resolve();
        } else {
          ctx.globalAlpha = el.style.opacity ?? 1;
          ctx.fillStyle = el.style.backgroundColor || '#6366f1';
          if (el.type === 'circle') {
            ctx.beginPath();
            ctx.ellipse(el.x + el.width / 2, el.y + el.height / 2, el.width / 2, el.height / 2, 0, 0, Math.PI * 2);
            ctx.fill();
          } else if (el.type === 'line') {
            ctx.strokeStyle = el.style.backgroundColor || '#10b981';
            ctx.lineWidth = el.height;
            ctx.beginPath();
            ctx.moveTo(el.x, el.y + el.height / 2);
            ctx.lineTo(el.x + el.width, el.y + el.height / 2);
            ctx.stroke();
          } else {
            ctx.fillRect(el.x, el.y, el.width, el.height);
          }
          ctx.globalAlpha = 1;
          resolve();
        }
      });
    });

    Promise.all(drawPromises).then(() => {
      const link = document.createElement('a');
      link.download = `${project?.name || 'design'}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      toast.success('Design exported as PNG');
    });
  };

  // --- AI Generation ---
  const handleAIGenerate = async () => {
    if (!aiPrompt.trim()) return;
    setAiGenerating(true);
    try {
      const res = await fetch(`${API}/api/creative-studio/ai/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: aiPrompt, style: 'photorealistic', width: canvasSize.width, height: canvasSize.height })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.image_url) {
          const id = Date.now().toString();
          const newEl = {
            id, type: 'image',
            x: 0, y: 0, width: canvasSize.width, height: canvasSize.height,
            content: data.image_url,
            style: { borderWidth: 0, borderColor: 'transparent', opacity: 1, borderRadius: '0px' }
          };
          const newEls = [...elements, newEl];
          setElements(newEls);
          setSelectedId(id);
          pushHistory(newEls);
          toast.success('AI image added to canvas');
        } else {
          toast.info('AI generated - no image data returned');
        }
      } else {
        toast.error('AI generation failed');
      }
    } catch (err) {
      console.error('AI generation error:', err);
      toast.error('AI generation failed');
    }
    setAiGenerating(false);
    setShowAIPanel(false);
    setAiPrompt('');
  };

  const selectedElement = elements.find(el => el.id === selectedId);

  const resizeHandles = ['nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'];
  const handleCursors = { nw: 'nw-resize', ne: 'ne-resize', sw: 'sw-resize', se: 'se-resize', n: 'n-resize', s: 's-resize', e: 'e-resize', w: 'w-resize' };
  const handlePositions = (el) => ({
    nw: { left: -4, top: -4 }, ne: { left: el.width - 4, top: -4 },
    sw: { left: -4, top: el.height - 4 }, se: { left: el.width - 4, top: el.height - 4 },
    n: { left: el.width / 2 - 4, top: -4 }, s: { left: el.width / 2 - 4, top: el.height - 4 },
    e: { left: el.width - 4, top: el.height / 2 - 4 }, w: { left: -4, top: el.height / 2 - 4 }
  });

  return (
    <div 
      data-testid="creative-editor"
      className="fixed inset-0 bg-slate-900 z-50 flex flex-col"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
    >
      {/* Top Toolbar */}
      <div className="h-14 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <button data-testid="editor-close-btn" onClick={onClose} className="p-2 hover:bg-slate-700 rounded-lg text-gray-400 hover:text-white"><X size={18} /></button>
          <div>
            <h2 className="text-white font-semibold text-sm">{project?.name || 'Untitled'}</h2>
            <p className="text-[10px] text-gray-500">{canvasSize.width} x {canvasSize.height}px</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button data-testid="undo-btn" onClick={undo} disabled={historyIndex <= 0} className="p-2 hover:bg-slate-700 rounded text-gray-400 disabled:text-gray-600" title="Undo (Ctrl+Z)"><Undo2 size={16} /></button>
          <button data-testid="redo-btn" onClick={redo} disabled={historyIndex >= history.length - 1} className="p-2 hover:bg-slate-700 rounded text-gray-400 disabled:text-gray-600" title="Redo (Ctrl+Shift+Z)"><Redo2 size={16} /></button>
          <div className="h-5 w-px bg-slate-700 mx-1" />
          <button onClick={() => setShowGrid(!showGrid)} className={`p-2 rounded ${showGrid ? 'bg-purple-600/30 text-purple-300' : 'text-gray-400 hover:bg-slate-700'}`} title="Toggle Grid"><Grid3x3 size={16} /></button>
          <div className="h-5 w-px bg-slate-700 mx-1" />
          <button className="p-1.5 hover:bg-slate-700 rounded text-gray-400" onClick={() => setZoom(z => Math.max(0.1, z - 0.1))}><Minus size={14} /></button>
          <span className="text-gray-400 text-xs w-10 text-center">{Math.round(zoom * 100)}%</span>
          <button className="p-1.5 hover:bg-slate-700 rounded text-gray-400" onClick={() => setZoom(z => Math.min(3, z + 0.1))}><Plus size={14} /></button>
          <div className="h-5 w-px bg-slate-700 mx-1" />
          <button data-testid="export-btn" onClick={exportCanvas} className="px-3 py-1.5 bg-slate-700 text-gray-300 rounded hover:bg-slate-600 flex items-center gap-1.5 text-xs"><Download size={14} /> Export PNG</button>
          <button data-testid="save-btn" onClick={() => onSave && onSave(elements)} className="px-3 py-1.5 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center gap-1.5 text-xs"><Save size={14} /> Save</button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Tools */}
        <div className="w-16 bg-slate-800 border-r border-slate-700 flex flex-col items-center py-3 gap-1 shrink-0 overflow-y-auto">
          <ToolButton icon={<Type size={20} />} label="Text" onClick={() => addElement('text', 'Edit me')} testId="tool-text" />
          <ToolButton icon={<Square size={20} />} label="Box" onClick={() => addElement('rect')} testId="tool-rect" />
          <ToolButton icon={<Circle size={20} />} label="Circle" onClick={() => addElement('circle')} testId="tool-circle" />
          <ToolButton icon={<Triangle size={20} />} label="Triangle" onClick={() => addElement('triangle')} testId="tool-triangle" />
          <ToolButton icon={<Star size={20} />} label="Star" onClick={() => addElement('star')} testId="tool-star" />
          <ToolButton icon={<Minus size={20} />} label="Line" onClick={() => addElement('line')} testId="tool-line" />
          <ToolButton icon={<ImageIcon size={20} />} label="Image" onClick={() => fileInputRef.current?.click()} testId="tool-image" />
          <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={handleImageUpload} />
          <div className="w-10 h-px bg-slate-700 my-1" />
          <ToolButton icon={<Sparkles size={20} />} label="AI" onClick={() => setShowAIPanel(!showAIPanel)} testId="tool-ai" />
          <div className="w-10 h-px bg-slate-700 my-1" />
          {/* Canvas preset toggle */}
          <button
            data-testid="canvas-presets-toggle"
            onClick={() => setShowPresetsPanel(!showPresetsPanel)}
            className="flex flex-col items-center gap-0.5 text-gray-400 hover:text-white p-2 hover:bg-slate-700 rounded-lg transition-colors w-full text-[10px]"
          >
            <span className="text-lg">📐</span>
            <span>Size</span>
          </button>
        </div>

        {/* Secondary panel (presets / AI) */}
        {(showPresetsPanel || showAIPanel) && (
          <div className="w-56 bg-slate-800/95 border-r border-slate-700 p-3 overflow-y-auto shrink-0">
            {showPresetsPanel && (
              <div>
                <h3 className="text-white text-xs font-bold mb-3 uppercase tracking-wider">Canvas Size</h3>
                <div className="space-y-1">
                  {CANVAS_PRESETS.map(p => (
                    <button
                      key={p.label}
                      data-testid={`preset-${p.label.toLowerCase().replace(/\s/g, '-')}`}
                      onClick={() => { setCanvasSize({ width: p.w, height: p.h }); setShowPresetsPanel(false); }}
                      className={`w-full text-left px-3 py-2 rounded text-xs transition-colors ${
                        canvasSize.width === p.w && canvasSize.height === p.h
                          ? 'bg-purple-600/30 text-purple-300'
                          : 'text-gray-400 hover:bg-slate-700 hover:text-white'
                      }`}
                    >
                      <span className="block font-medium">{p.label}</span>
                      <span className="text-[10px] text-gray-500">{p.w} x {p.h}</span>
                    </button>
                  ))}
                </div>
                <div className="mt-4 border-t border-slate-700 pt-3">
                  <label className="text-gray-500 text-[10px] block mb-1">Background Color</label>
                  <div className="flex gap-2 items-center">
                    <input type="color" value={canvasBg} onChange={e => setCanvasBg(e.target.value)} className="w-8 h-8 rounded cursor-pointer border-0 p-0" data-testid="canvas-bg-color" />
                    <span className="text-gray-400 text-xs font-mono">{canvasBg}</span>
                  </div>
                </div>
              </div>
            )}
            {showAIPanel && (
              <div>
                <h3 className="text-white text-xs font-bold mb-3 uppercase tracking-wider">AI Generate</h3>
                <textarea
                  data-testid="ai-prompt-input"
                  value={aiPrompt}
                  onChange={e => setAiPrompt(e.target.value)}
                  placeholder="Describe the image you want..."
                  className="w-full bg-slate-700 text-white rounded px-3 py-2 text-xs min-h-[80px] placeholder-gray-500 border border-slate-600 focus:border-purple-500 focus:outline-none"
                />
                <button
                  data-testid="ai-generate-btn"
                  onClick={handleAIGenerate}
                  disabled={aiGenerating || !aiPrompt.trim()}
                  className="w-full mt-2 px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded text-xs font-medium hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {aiGenerating ? 'Generating...' : 'Generate Image'}
                </button>
                <p className="text-[10px] text-gray-500 mt-2">Powered by Gemini AI. Image will be added to your canvas.</p>
              </div>
            )}
          </div>
        )}

        {/* Canvas Area */}
        <div className="flex-1 bg-slate-900/80 overflow-auto flex items-center justify-center p-8 relative" onClick={() => setSelectedId(null)}>
          <div 
            ref={canvasRef}
            className="relative shadow-2xl"
            style={{ 
              width: canvasSize.width, 
              height: canvasSize.height,
              transform: `scale(${zoom})`,
              transformOrigin: 'center center',
              backgroundColor: canvasBg,
              backgroundImage: showGrid ? 'linear-gradient(rgba(128,128,128,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.15) 1px, transparent 1px)' : 'none',
              backgroundSize: showGrid ? '20px 20px' : 'auto'
            }}
            onClick={(e) => e.stopPropagation()} 
          >
            {elements.map(el => (
              <div
                key={el.id}
                data-testid={`canvas-element-${el.id}`}
                style={{
                  position: 'absolute',
                  left: el.x,
                  top: el.y,
                  width: el.width,
                  height: el.height,
                  cursor: dragState?.id === el.id ? 'grabbing' : 'grab',
                  outline: selectedId === el.id ? '2px solid #8b5cf6' : 'none',
                  outlineOffset: '2px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: el.style.opacity ?? 1,
                  backgroundColor: el.type !== 'image' && el.type !== 'text' ? el.style.backgroundColor : 'transparent',
                  borderRadius: el.style.borderRadius || '0px',
                  clipPath: el.style.clipPath || 'none',
                  borderWidth: el.style.borderWidth || 0,
                  borderStyle: el.style.borderWidth ? 'solid' : 'none',
                  borderColor: el.style.borderColor || 'transparent',
                }}
                onMouseDown={(e) => handleMouseDown(e, el.id)}
              >
                {el.type === 'image' && (
                  <img src={el.content} alt="" className="w-full h-full object-contain pointer-events-none" style={{ borderRadius: el.style.borderRadius }} />
                )}
                {el.type === 'text' && (
                  <div 
                    contentEditable={selectedId === el.id}
                    suppressContentEditableWarning
                    className="outline-none w-full h-full flex items-center"
                    style={{
                      cursor: selectedId === el.id ? 'text' : 'inherit',
                      color: el.style.color,
                      fontSize: el.style.fontSize,
                      fontWeight: el.style.fontWeight,
                      fontStyle: el.style.fontStyle,
                      textAlign: el.style.textAlign,
                      justifyContent: el.style.textAlign === 'center' ? 'center' : el.style.textAlign === 'right' ? 'flex-end' : 'flex-start',
                    }}
                    onBlur={(e) => { updateElement(el.id, { content: e.target.innerText }); pushHistory(elements); }}
                    onMouseDown={(e) => { if (selectedId === el.id) e.stopPropagation(); }}
                  >
                    {el.content}
                  </div>
                )}
                {el.type === 'line' && (
                  <div className="w-full h-full" style={{ backgroundColor: el.style.backgroundColor }} />
                )}

                {/* Resize Handles */}
                {selectedId === el.id && resizeHandles.map(h => {
                  const pos = handlePositions(el)[h];
                  return (
                    <div
                      key={h}
                      style={{
                        position: 'absolute', left: pos.left, top: pos.top,
                        width: 8, height: 8, backgroundColor: '#8b5cf6', border: '1px solid white',
                        cursor: handleCursors[h], zIndex: 10, borderRadius: 2
                      }}
                      onMouseDown={(e) => startResize(e, el.id, h)}
                    />
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel - Properties */}
        {selectedElement && (
          <div className="w-60 bg-slate-800 border-l border-slate-700 p-4 overflow-y-auto shrink-0">
            <h3 className="text-white font-semibold mb-3 text-sm">Properties</h3>
            
            {/* Position & Size */}
            <Section title="Position & Size">
              <div className="grid grid-cols-2 gap-2">
                <NumInput label="X" value={Math.round(selectedElement.x)} onChange={v => { updateElement(selectedElement.id, { x: v }); pushHistory(elements); }} />
                <NumInput label="Y" value={Math.round(selectedElement.y)} onChange={v => { updateElement(selectedElement.id, { y: v }); pushHistory(elements); }} />
                <NumInput label="W" value={Math.round(selectedElement.width)} onChange={v => { updateElement(selectedElement.id, { width: Math.max(10, v) }); pushHistory(elements); }} />
                <NumInput label="H" value={Math.round(selectedElement.height)} onChange={v => { updateElement(selectedElement.id, { height: Math.max(10, v) }); pushHistory(elements); }} />
              </div>
            </Section>

            {/* Opacity */}
            <Section title="Opacity">
              <input 
                data-testid="opacity-slider"
                type="range" min="0" max="1" step="0.05"
                value={selectedElement.style.opacity ?? 1}
                onChange={(e) => updateStyle(selectedElement.id, { opacity: parseFloat(e.target.value) })}
                className="w-full h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-gray-500 text-[10px]">{Math.round((selectedElement.style.opacity ?? 1) * 100)}%</span>
            </Section>

            {/* Fill Color */}
            {selectedElement.type !== 'image' && (
              <Section title="Fill Color">
                <div className="flex gap-2 items-center">
                  <input type="color" value={selectedElement.style.backgroundColor || '#000000'} onChange={(e) => updateStyle(selectedElement.id, { backgroundColor: e.target.value })} className="w-7 h-7 rounded cursor-pointer border-0 p-0" data-testid="fill-color" />
                  <span className="text-gray-400 text-[10px] font-mono">{selectedElement.style.backgroundColor}</span>
                </div>
              </Section>
            )}

            {/* Border */}
            <Section title="Border">
              <div className="flex gap-2 items-center mb-2">
                <input type="color" value={selectedElement.style.borderColor || '#000000'} onChange={(e) => updateStyle(selectedElement.id, { borderColor: e.target.value })} className="w-7 h-7 rounded cursor-pointer border-0 p-0" data-testid="border-color" />
                <input type="number" min="0" max="20" value={selectedElement.style.borderWidth || 0} onChange={(e) => updateStyle(selectedElement.id, { borderWidth: parseInt(e.target.value) || 0 })} className="bg-slate-700 text-white rounded px-2 py-1 text-xs w-16" data-testid="border-width" />
                <span className="text-gray-500 text-[10px]">px</span>
              </div>
            </Section>

            {/* Typography */}
            {selectedElement.type === 'text' && (
              <Section title="Typography">
                <div className="space-y-2">
                  <div className="flex gap-2 items-center">
                    <input type="color" value={selectedElement.style.color || '#000000'} onChange={(e) => updateStyle(selectedElement.id, { color: e.target.value })} className="w-7 h-7 rounded cursor-pointer border-0 p-0" data-testid="text-color" />
                    <span className="text-gray-400 text-[10px] font-mono">{selectedElement.style.color}</span>
                  </div>
                  <div>
                    <label className="text-gray-500 text-[10px]">Size: {selectedElement.style.fontSize}px</label>
                    <input type="range" min="12" max="120" value={selectedElement.style.fontSize} onChange={(e) => updateStyle(selectedElement.id, { fontSize: parseInt(e.target.value) })} className="w-full h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer" />
                  </div>
                  <div className="flex gap-1">
                    <StyleToggle active={selectedElement.style.fontWeight === 'bold'} onClick={() => updateStyle(selectedElement.id, { fontWeight: selectedElement.style.fontWeight === 'bold' ? 'normal' : 'bold' })} icon={<Bold size={14} />} />
                    <StyleToggle active={selectedElement.style.fontStyle === 'italic'} onClick={() => updateStyle(selectedElement.id, { fontStyle: selectedElement.style.fontStyle === 'italic' ? 'normal' : 'italic' })} icon={<Italic size={14} />} />
                    <StyleToggle active={selectedElement.style.textAlign === 'left'} onClick={() => updateStyle(selectedElement.id, { textAlign: 'left' })} icon={<AlignLeft size={14} />} />
                    <StyleToggle active={selectedElement.style.textAlign === 'center'} onClick={() => updateStyle(selectedElement.id, { textAlign: 'center' })} icon={<AlignCenter size={14} />} />
                    <StyleToggle active={selectedElement.style.textAlign === 'right'} onClick={() => updateStyle(selectedElement.id, { textAlign: 'right' })} icon={<AlignRight size={14} />} />
                  </div>
                </div>
              </Section>
            )}

            {/* Layer + Actions */}
            <Section title="Actions">
              <div className="grid grid-cols-4 gap-1 mb-2">
                <button onClick={() => moveLayer(selectedElement.id, 'back')} className="p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-white flex justify-center" title="Send to Back"><Layers size={14} /></button>
                <button onClick={() => moveLayer(selectedElement.id, 'backward')} className="p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-white flex justify-center" title="Back"><ChevronDown size={14} /></button>
                <button onClick={() => moveLayer(selectedElement.id, 'forward')} className="p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-white flex justify-center" title="Forward"><ChevronUp size={14} /></button>
                <button onClick={() => moveLayer(selectedElement.id, 'front')} className="p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-white flex justify-center" title="Front"><Layers size={14} className="rotate-180" /></button>
              </div>
              <button data-testid="duplicate-btn" onClick={() => duplicateElement(selectedElement.id)} className="w-full py-1.5 bg-slate-700 text-gray-300 rounded hover:bg-slate-600 flex items-center justify-center gap-1.5 text-xs mb-2"><Copy size={14} /> Duplicate</button>
              <button data-testid="delete-btn" onClick={() => deleteElement(selectedElement.id)} className="w-full py-1.5 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 flex items-center justify-center gap-1.5 text-xs border border-red-500/30"><Trash2 size={14} /> Delete</button>
            </Section>
          </div>
        )}
      </div>
    </div>
  );
};

// --- Small UI Components ---
const ToolButton = ({ icon, label, onClick, testId }) => (
  <button 
    data-testid={testId}
    onClick={onClick}
    className="flex flex-col items-center gap-0.5 text-gray-400 hover:text-white p-2 hover:bg-slate-700 rounded-lg transition-colors w-full"
  >
    {icon}
    <span className="text-[10px]">{label}</span>
  </button>
);

const Section = ({ title, children }) => (
  <div className="mb-4 pb-3 border-b border-slate-700/50">
    <label className="text-gray-400 text-[10px] uppercase font-bold block mb-2">{title}</label>
    {children}
  </div>
);

const NumInput = ({ label, value, onChange }) => (
  <div>
    <span className="text-gray-500 text-[10px] block">{label}</span>
    <input type="number" value={value} onChange={(e) => onChange(parseInt(e.target.value) || 0)} className="bg-slate-700 text-white rounded px-2 py-1 text-xs w-full" />
  </div>
);

const StyleToggle = ({ active, onClick, icon }) => (
  <button onClick={onClick} className={`p-1.5 rounded ${active ? 'bg-purple-600 text-white' : 'bg-slate-700 text-gray-400 hover:bg-slate-600'}`}>{icon}</button>
);

export default CreativeEditor;
