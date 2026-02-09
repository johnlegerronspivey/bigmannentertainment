import React, { useState, useRef, useEffect } from 'react';
import { toast } from 'sonner';
import { 
  Type, Square, Circle, Image as ImageIcon, 
  Move, Trash2, Save, X, Download, 
  AlignLeft, AlignCenter, AlignRight,
  Bold, Italic, Palette, Layers, ChevronUp, ChevronDown
} from 'lucide-react';

const CreativeEditor = ({ project, onClose, onSave }) => {
  const [elements, setElements] = useState(project?.elements || []);
  const [selectedId, setSelectedId] = useState(null);
  const [canvasSize, setCanvasSize] = useState({ 
    width: project?.width || 800, 
    height: project?.height || 600 
  });
  const [dragState, setDragState] = useState(null);
  const [zoom, setZoom] = useState(1);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);

  // --- Element Management ---

  const addElement = (type, content = '') => {
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
        backgroundColor: type === 'rect' ? '#6366f1' : type === 'circle' ? '#ec4899' : 'transparent',
        color: '#000000',
        fontSize: 24,
        borderRadius: type === 'circle' ? '50%' : '0px',
        borderWidth: 0,
        borderColor: '#000000',
        textAlign: 'center',
        fontWeight: 'normal',
        fontStyle: 'normal'
      }
    };
    
    setElements([...elements, newElement]);
    setSelectedId(id);
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
          id,
          type: 'image',
          x: canvasSize.width / 2 - width / 2,
          y: canvasSize.height / 2 - height / 2,
          width,
          height,
          content: event.target.result,
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
    e.target.value = '';
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

  const moveLayer = (id, direction) => {
    const index = elements.findIndex(el => el.id === id);
    if (index === -1) return;
    
    const newElements = [...elements];
    const element = newElements[index];
    newElements.splice(index, 1);
    
    if (direction === 'front') {
      newElements.push(element);
    } else if (direction === 'back') {
      newElements.unshift(element);
    } else if (direction === 'forward') {
      newElements.splice(Math.min(index + 1, newElements.length), 0, element);
    } else if (direction === 'backward') {
      newElements.splice(Math.max(index - 1, 0), 0, element);
    }
    
    setElements(newElements);
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
            className="p-2 hover:bg-slate-700 rounded text-gray-400"
            onClick={() => setZoom(z => Math.max(0.1, z - 0.1))}
          >
            -
          </button>
          <span className="text-gray-400 text-sm">{Math.round(zoom * 100)}%</span>
          <button 
            className="p-2 hover:bg-slate-700 rounded text-gray-400"
            onClick={() => setZoom(z => Math.min(3, z + 0.1))}
          >
            +
          </button>
          <div className="h-6 w-px bg-slate-700 mx-2" />
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
        <div className="flex-1 bg-slate-900 overflow-auto flex items-center justify-center p-8 relative" onClick={() => setSelectedId(null)}>
          <div 
            className="bg-white shadow-2xl relative overflow-hidden transition-transform duration-200"
            style={{ 
              width: canvasSize.width, 
              height: canvasSize.height,
              transform: `scale(${zoom})`,
              backgroundColor: '#ffffff' 
            }}
            ref={canvasRef}
            onClick={(e) => e.stopPropagation()} 
          >
            {elements.map(el => (
              <div
                key={el.id}
                style={{
                  position: 'absolute',
                  left: el.x,
                  top: el.y,
                  width: el.width,
                  height: el.height,
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
                    style={{
                      cursor: selectedId === el.id ? 'text' : 'inherit'
                    }}
                    onBlur={(e) => updateElement(el.id, { content: e.target.innerText })}
                    onMouseDown={(e) => {
                       if(selectedId === el.id) e.stopPropagation();
                    }}
                  >
                    {el.content}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </div>

        {/* Properties Panel */}
        {selectedElement && (
          <div className="w-64 bg-slate-800 border-l border-slate-700 p-4 overflow-y-auto">
            <h3 className="text-white font-semibold mb-4 border-b border-slate-700 pb-2">Properties</h3>
            
            <div className="space-y-6">
              {/* Position */}
              <div>
                <label className="text-gray-400 text-xs uppercase font-bold block mb-2">Dimensions & Position</label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-gray-500 text-[10px] block">X</span>
                    <input 
                      type="number" 
                      value={Math.round(selectedElement.x)} 
                      onChange={(e) => updateElement(selectedElement.id, { x: parseInt(e.target.value) || 0 })}
                      className="bg-slate-700 text-white rounded px-2 py-1 text-sm w-full"
                    />
                  </div>
                  <div>
                    <span className="text-gray-500 text-[10px] block">Y</span>
                    <input 
                      type="number" 
                      value={Math.round(selectedElement.y)} 
                      onChange={(e) => updateElement(selectedElement.id, { y: parseInt(e.target.value) || 0 })}
                      className="bg-slate-700 text-white rounded px-2 py-1 text-sm w-full"
                    />
                  </div>
                   <div>
                    <span className="text-gray-500 text-[10px] block">W</span>
                    <input 
                      type="number" 
                      value={Math.round(selectedElement.width)} 
                      onChange={(e) => updateElement(selectedElement.id, { width: parseInt(e.target.value) || 10 })}
                      className="bg-slate-700 text-white rounded px-2 py-1 text-sm w-full"
                    />
                  </div>
                   <div>
                    <span className="text-gray-500 text-[10px] block">H</span>
                    <input 
                      type="number" 
                      value={Math.round(selectedElement.height)} 
                      onChange={(e) => updateElement(selectedElement.id, { height: parseInt(e.target.value) || 10 })}
                      className="bg-slate-700 text-white rounded px-2 py-1 text-sm w-full"
                    />
                  </div>
                </div>
              </div>

              {/* Style */}
              <div>
                <label className="text-gray-400 text-xs uppercase font-bold block mb-2">Appearance</label>
                
                {selectedElement.type !== 'image' && (
                  <div className="mb-3">
                    <label className="text-gray-500 text-[10px] block mb-1">Fill Color</label>
                    <div className="flex gap-2 items-center">
                      <input 
                        type="color" 
                        value={selectedElement.style.backgroundColor} 
                        onChange={(e) => updateStyle(selectedElement.id, { backgroundColor: e.target.value })}
                        className="w-8 h-8 rounded cursor-pointer border-0 p-0"
                      />
                      <span className="text-gray-400 text-xs font-mono">{selectedElement.style.backgroundColor}</span>
                    </div>
                  </div>
                )}
              </div>

              {selectedElement.type === 'text' && (
                <div>
                   <label className="text-gray-400 text-xs uppercase font-bold block mb-2">Typography</label>
                   
                   <div className="space-y-3">
                      <div>
                        <label className="text-gray-500 text-[10px] block mb-1">Color</label>
                        <div className="flex gap-2 items-center">
                          <input 
                            type="color" 
                            value={selectedElement.style.color} 
                            onChange={(e) => updateStyle(selectedElement.id, { color: e.target.value })}
                            className="w-8 h-8 rounded cursor-pointer border-0 p-0"
                          />
                          <span className="text-gray-400 text-xs font-mono">{selectedElement.style.color}</span>
                        </div>
                      </div>

                      <div>
                        <label className="text-gray-500 text-[10px] block mb-1">Font Size: {selectedElement.style.fontSize}px</label>
                        <input 
                          type="range" 
                          min="12" 
                          max="120" 
                          value={selectedElement.style.fontSize} 
                          onChange={(e) => updateStyle(selectedElement.id, { fontSize: parseInt(e.target.value) })}
                          className="w-full h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>

                      <div className="flex gap-2">
                        <button 
                          onClick={() => updateStyle(selectedElement.id, { fontWeight: selectedElement.style.fontWeight === 'bold' ? 'normal' : 'bold' })}
                          className={`p-2 rounded ${selectedElement.style.fontWeight === 'bold' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-gray-400'}`}
                        >
                          <Bold size={16} />
                        </button>
                        <button 
                          onClick={() => updateStyle(selectedElement.id, { fontStyle: selectedElement.style.fontStyle === 'italic' ? 'normal' : 'italic' })}
                          className={`p-2 rounded ${selectedElement.style.fontStyle === 'italic' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-gray-400'}`}
                        >
                          <Italic size={16} />
                        </button>
                        <button 
                           onClick={() => updateStyle(selectedElement.id, { textAlign: 'left' })}
                           className={`p-2 rounded ${selectedElement.style.textAlign === 'left' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-gray-400'}`}
                        >
                          <AlignLeft size={16} />
                        </button>
                        <button 
                           onClick={() => updateStyle(selectedElement.id, { textAlign: 'center' })}
                           className={`p-2 rounded ${selectedElement.style.textAlign === 'center' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-gray-400'}`}
                        >
                          <AlignCenter size={16} />
                        </button>
                         <button 
                           onClick={() => updateStyle(selectedElement.id, { textAlign: 'right' })}
                           className={`p-2 rounded ${selectedElement.style.textAlign === 'right' ? 'bg-purple-600 text-white' : 'bg-slate-700 text-gray-400'}`}
                        >
                          <AlignRight size={16} />
                        </button>
                      </div>
                   </div>
                </div>
              )}

              <div className="pt-4 border-t border-slate-700">
                <label className="text-gray-400 text-xs uppercase font-bold block mb-2">Actions</label>
                <div className="grid grid-cols-4 gap-2 mb-4">
                  <button onClick={() => moveLayer(selectedElement.id, 'back')} className="p-2 bg-slate-700 hover:bg-slate-600 rounded text-white flex justify-center" title="Send to Back">
                    <Layers size={16} />
                  </button>
                  <button onClick={() => moveLayer(selectedElement.id, 'backward')} className="p-2 bg-slate-700 hover:bg-slate-600 rounded text-white flex justify-center" title="Send Backward">
                    <ChevronDown size={16} />
                  </button>
                  <button onClick={() => moveLayer(selectedElement.id, 'forward')} className="p-2 bg-slate-700 hover:bg-slate-600 rounded text-white flex justify-center" title="Bring Forward">
                    <ChevronUp size={16} />
                  </button>
                  <button onClick={() => moveLayer(selectedElement.id, 'front')} className="p-2 bg-slate-700 hover:bg-slate-600 rounded text-white flex justify-center" title="Bring to Front">
                    <Layers size={16} className="rotate-180" />
                  </button>
                </div>

                <button 
                  onClick={() => deleteElement(selectedElement.id)}
                  className="w-full py-2 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 flex items-center justify-center gap-2 border border-red-500/30"
                >
                  <Trash2 size={16} /> Delete Element
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
