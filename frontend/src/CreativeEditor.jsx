import React, { useState, useRef, useEffect } from 'react';
import { toast } from 'sonner';
import { 
  Type, Square, Circle, Image as ImageIcon, 
  Move, Trash2, Save, X, Download, 
  AlignLeft, AlignCenter, AlignRight,
  Bold, Italic, Palette
} from 'lucide-react';

const CreativeEditor = ({ project, onClose, onSave }) => {
  const [elements, setElements] = useState(project?.elements || []);
  const [selectedId, setSelectedId] = useState(null);
  const [canvasSize, setCanvasSize] = useState({ 
    width: project?.width || 800, 
    height: project?.height || 600 
  });
  
  // Added missing state variables
  const [dragState, setDragState] = useState(null);
  const [zoom, setZoom] = useState(1);
  const fileInputRef = useRef(null);

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        // Create an image element
        const id = Date.now().toString();
        const aspectRatio = img.width / img.height;
        const newElement = {
          id,
          type: 'image',
          x: canvasSize.width / 2 - 100,
          y: canvasSize.height / 2 - (100 / aspectRatio),
          width: 200,
          height: 200 / aspectRatio,
          content: event.target.result, // Data URL
          style: {
            borderWidth: 0,
            borderColor: 'transparent'
          }
        };
        setElements([...elements, newElement]);
        setSelectedId(id);
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
    e.target.value = ''; // Reset input
  };

  // --- Element Management ---

  const addElement = (type, content = '') => {
    const id = Date.now().toString();
    const newElement = {
      id,
      type,
      x: canvasSize.width / 2 - 50,
      y: canvasSize.height / 2 - 50,
      width: type === 'text' ? 200 : 100,
      height: type === 'text' ? 50 : 100,
      content,
      style: {
        backgroundColor: type === 'rect' ? '#6366f1' : type === 'circle' ? '#ec4899' : 'transparent',
        color: '#ffffff',
        fontSize: 24,
        borderRadius: type === 'circle' ? '50%' : '0px',
        borderWidth: 0,
        borderColor: '#ffffff',
        textAlign: 'center',
        fontWeight: 'normal',
        fontStyle: 'normal'
      }
    };
    
    setElements([...elements, newElement]);
    setSelectedId(id);
  };

  const updateElement = (id, updates) => {
    setElements(elements.map(el => el.id === id ? { ...el, ...updates } : el));
  };

  const updateStyle = (id, styleUpdates) => {
    setElements(elements.map(el => 
      el.id === id ? { ...el, style: { ...el.style, ...styleUpdates } } : el
    ));
  };

  const deleteElement = (id) => {
    setElements(elements.filter(el => el.id !== id));
    setSelectedId(null);
  };

  // --- Drag & Drop Logic ---

  const handleMouseDown = (e, id) => {
    e.stopPropagation();
    setSelectedId(id);
    const element = elements.find(el => el.id === id);
    if (!element) return;

    setDragState({
      id,
      startX: e.clientX,
      startY: e.clientY,
      initialX: element.x,
      initialY: element.y
    });
  };

  const handleMouseMove = (e) => {
    if (!dragState) return;

    const dx = (e.clientX - dragState.startX) / zoom;
    const dy = (e.clientY - dragState.startY) / zoom;

    updateElement(dragState.id, {
      x: dragState.initialX + dx,
      y: dragState.initialY + dy
    });
  };

  const handleMouseUp = () => {
    setDragState(null);
  };

  // --- Render Helpers ---

  const selectedElement = elements.find(el => el.id === selectedId);

  return (
    <div 
      className="fixed inset-0 bg-slate-900 z-50 flex flex-col"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
    >
      {/* Toolbar */}
      <div className="h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <button onClick={onClose} className="p-2 hover:bg-slate-700 rounded-lg text-gray-400 hover:text-white">
            <X size={20} />
          </button>
          <div>
            <h2 className="text-white font-semibold">{project?.name || 'Untitled Project'}</h2>
            <p className="text-xs text-gray-400">Canva-like Editor</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button 
            onClick={() => onSave && onSave(elements)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
          >
            <Save size={18} /> Save
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Tools */}
        <div className="w-20 bg-slate-800 border-r border-slate-700 flex flex-col items-center py-4 gap-4">
          <ToolButton icon={<Type size={24} />} label="Text" onClick={() => addElement('text', 'Double click to edit')} />
          <ToolButton icon={<Square size={24} />} label="Box" onClick={() => addElement('rect')} />
          <ToolButton icon={<Circle size={24} />} label="Circle" onClick={() => addElement('circle')} />
          <ToolButton icon={<ImageIcon size={24} />} label="Image" onClick={() => fileInputRef.current?.click()} />
          <input 
            type="file" 
            ref={fileInputRef} 
            className="hidden" 
            accept="image/*" 
            onChange={handleImageUpload} 
          />
        </div>

        {/* Canvas Area */}
        <div className="flex-1 bg-slate-900 overflow-auto flex items-center justify-center p-8 relative">
          <div 
            className="bg-white shadow-2xl relative overflow-hidden transition-transform duration-200"
            style={{ 
              width: canvasSize.width, 
              height: canvasSize.height,
              transform: `scale(${zoom})`,
              backgroundColor: '#ffffff' 
            }}
            ref={canvasRef}
            onClick={() => setSelectedId(null)}
          >
            {elements.map(el => (
              <div
                key={el.id}
                style={{
                  position: 'absolute',
                  left: el.x,
                  top: el.y,
                  width: el.width,
                  height: el.height, // Allow auto height for text later
                  cursor: dragState?.id === el.id ? 'grabbing' : 'grab',
                  border: selectedId === el.id ? '2px solid #8b5cf6' : '1px dashed transparent',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  ...el.style
                }}
                onMouseDown={(e) => handleMouseDown(e, el.id)}
              >
                {el.type === 'image' && (
                  <img 
                    src={el.content} 
                    alt="element" 
                    className="w-full h-full object-contain pointer-events-none"
                    style={{ borderRadius: el.style.borderRadius }} 
                  />
                )}
                {el.type === 'text' ? (
                  <div 
                    contentEditable={selectedId === el.id}
                    suppressContentEditableWarning
                    className="outline-none w-full h-full flex items-center justify-center"
                    onBlur={(e) => updateElement(el.id, { content: e.target.innerText })}
                  >
                    {el.content}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
          
          {/* Zoom Controls */}
          <div className="absolute bottom-4 right-4 bg-slate-800 rounded-lg p-2 flex gap-2">
            <button onClick={() => setZoom(z => Math.max(0.1, z - 0.1))} className="text-white px-2 hover:bg-slate-700 rounded">-</button>
            <span className="text-white text-sm py-1 min-w-[3ch] text-center">{Math.round(zoom * 100)}%</span>
            <button onClick={() => setZoom(z => Math.min(3, z + 0.1))} className="text-white px-2 hover:bg-slate-700 rounded">+</button>
          </div>
        </div>

        {/* Properties Panel */}
        {selectedElement && (
          <div className="w-64 bg-slate-800 border-l border-slate-700 p-4">
            <h3 className="text-white font-semibold mb-4 border-b border-slate-700 pb-2">Properties</h3>
            
            <div className="space-y-4">
              {/* Common Properties */}
              <div>
                <label className="text-gray-400 text-xs block mb-1">Position</label>
                <div className="grid grid-cols-2 gap-2">
                  <input 
                    type="number" 
                    value={Math.round(selectedElement.x)} 
                    onChange={(e) => updateElement(selectedElement.id, { x: parseInt(e.target.value) })}
                    className="bg-slate-700 text-white rounded px-2 py-1 text-sm"
                  />
                  <input 
                    type="number" 
                    value={Math.round(selectedElement.y)} 
                    onChange={(e) => updateElement(selectedElement.id, { y: parseInt(e.target.value) })}
                    className="bg-slate-700 text-white rounded px-2 py-1 text-sm"
                  />
                </div>
              </div>

              {/* Style Properties */}
              <div>
                <label className="text-gray-400 text-xs block mb-1">Background</label>
                <div className="flex gap-2">
                  <input 
                    type="color" 
                    value={selectedElement.style.backgroundColor} 
                    onChange={(e) => updateStyle(selectedElement.id, { backgroundColor: e.target.value })}
                    className="w-8 h-8 rounded cursor-pointer"
                  />
                  <span className="text-white text-sm py-1">{selectedElement.style.backgroundColor}</span>
                </div>
              </div>

              {selectedElement.type === 'text' && (
                <>
                  <div>
                    <label className="text-gray-400 text-xs block mb-1">Text Color</label>
                    <input 
                      type="color" 
                      value={selectedElement.style.color} 
                      onChange={(e) => updateStyle(selectedElement.id, { color: e.target.value })}
                      className="w-full h-8 rounded cursor-pointer"
                    />
                  </div>
                  <div>
                    <label className="text-gray-400 text-xs block mb-1">Font Size</label>
                    <input 
                      type="range" 
                      min="12" 
                      max="72" 
                      value={selectedElement.style.fontSize} 
                      onChange={(e) => updateStyle(selectedElement.id, { fontSize: parseInt(e.target.value) })}
                      className="w-full"
                    />
                    <div className="text-right text-gray-400 text-xs">{selectedElement.style.fontSize}px</div>
                  </div>
                </>
              )}

              <div className="pt-4 border-t border-slate-700">
                <button 
                  onClick={() => deleteElement(selectedElement.id)}
                  className="w-full py-2 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 flex items-center justify-center gap-2"
                >
                  <Trash2 size={16} /> Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const ToolButton = ({ icon, label, onClick }) => (
  <button 
    onClick={onClick}
    className="flex flex-col items-center gap-1 text-gray-400 hover:text-white p-2 hover:bg-slate-700 rounded-lg transition-colors w-full"
  >
    {icon}
    <span className="text-[10px]">{label}</span>
  </button>
);

export default CreativeEditor;