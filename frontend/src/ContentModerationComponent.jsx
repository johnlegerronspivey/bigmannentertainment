import React, { useState } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const ContentModerationComponent = () => {
  const [activeTab, setActiveTab] = useState('text'); // 'text' or 'image'
  const [textInput, setTextInput] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleTextModeration = async () => {
    if (!textInput.trim()) {
      toast.error('Please enter text to moderate');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${API}/api/moderation/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textInput })
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('Text analysis complete');
      } else {
        throw new Error('Moderation failed');
      }
    } catch (error) {
      console.error('Moderation error:', error);
      toast.error('Failed to moderate text');
    }
    setLoading(false);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
      setResult(null);
    }
  };

  const handleImageModeration = async () => {
    if (!imageFile) {
      toast.error('Please select an image');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await fetch(`${API}/api/moderation/image`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        toast.success('Image analysis complete');
      } else {
        throw new Error('Moderation failed');
      }
    } catch (error) {
      console.error('Moderation error:', error);
      toast.error('Failed to moderate image');
    }
    setLoading(false);
  };

  const renderResult = () => {
    if (!result) return null;

    // Parse the result string if it's a JSON string inside 'result'
    let analysis = null;
    try {
      if (typeof result.result === 'string') {
          // Remove markdown code blocks if present
          const cleanJson = result.result.replace(/```json\n|\n```/g, '');
          analysis = JSON.parse(cleanJson);
      } else {
          analysis = result.result; // Should not happen given current backend but handling safe
      }
    } catch (e) {
      console.error("Error parsing result:", e);
      return <div className="text-red-400">Error parsing moderation result</div>;
    }

    if (!analysis) return null;

    const isSafe = analysis.safe;
    const confidence = analysis.confidence ? Math.round(analysis.confidence * 100) : null;

    return (
      <div className={`mt-6 p-6 rounded-xl border ${isSafe ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
        <div className="flex items-center gap-4 mb-4">
          <div className={`text-4xl ${isSafe ? 'text-green-500' : 'text-red-500'}`}>
            {isSafe ? '✅' : '🚨'}
          </div>
          <div>
            <h3 className={`text-xl font-bold ${isSafe ? 'text-green-400' : 'text-red-400'}`}>
              {isSafe ? 'Content is Safe' : 'Content Flagged'}
            </h3>
            {confidence && <p className="text-gray-400 text-sm">Confidence: {confidence}%</p>}
          </div>
        </div>

        {!isSafe && analysis.categories && analysis.categories.length > 0 && (
          <div className="mb-4">
            <h4 className="text-white font-semibold mb-2">Flagged Categories:</h4>
            <div className="flex flex-wrap gap-2">
              {analysis.categories.map((cat, idx) => (
                <span key={idx} className="px-3 py-1 bg-red-500/20 text-red-300 rounded-full text-sm border border-red-500/30">
                  {cat}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="bg-black/20 p-4 rounded-lg">
          <h4 className="text-gray-300 font-semibold mb-2">Analysis Reason:</h4>
          <p className="text-gray-400">{analysis.reason || "No specific reason provided."}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6" data-testid="content-moderation-component">
      <div className="bg-white/5 rounded-xl p-6 border border-purple-500/20">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <span>🛡️</span> AI Content Moderation
            </h2>
            <p className="text-gray-400 mt-1">Check content safety using Gemini AI</p>
          </div>
          
          <div className="flex bg-black/30 rounded-lg p-1">
            <button
              onClick={() => { setActiveTab('text'); setResult(null); }}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'text' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              📝 Text
            </button>
            <button
              onClick={() => { setActiveTab('image'); setResult(null); }}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'image' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              🖼️ Image
            </button>
          </div>
        </div>

        {activeTab === 'text' ? (
          <div className="space-y-4">
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Enter text to analyze for safety..."
              className="w-full h-40 bg-black/20 text-white border border-purple-500/30 rounded-lg p-4 focus:border-purple-500 focus:outline-none resize-none"
            />
            <button
              onClick={handleTextModeration}
              disabled={loading || !textInput.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  Analyzing...
                </>
              ) : (
                <><span>🔍</span> Check Text Safety</>
              )}
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="border-2 border-dashed border-purple-500/30 rounded-xl p-8 text-center hover:border-purple-500/50 transition-all bg-black/20">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer block">
                {imagePreview ? (
                  <div className="relative inline-block">
                    <img 
                      src={imagePreview} 
                      alt="Preview" 
                      className="max-h-64 rounded-lg shadow-lg mx-auto"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg">
                      <span className="text-white font-medium">Change Image</span>
                    </div>
                  </div>
                ) : (
                  <div className="py-8">
                    <div className="text-5xl mb-4">🖼️</div>
                    <p className="text-white font-medium text-lg mb-2">Click to Upload Image</p>
                    <p className="text-gray-400 text-sm">Supports JPG, PNG, WEBP</p>
                  </div>
                )}
              </label>
            </div>

            {imagePreview && (
              <button
                onClick={handleImageModeration}
                disabled={loading}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    Analyzing Image...
                  </>
                ) : (
                  <><span>🔍</span> Check Image Safety</>
                )}
              </button>
            )}
          </div>
        )}

        {renderResult()}
      </div>
    </div>
  );
};

export default ContentModerationComponent;
