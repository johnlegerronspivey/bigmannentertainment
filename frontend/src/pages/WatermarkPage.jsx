import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiRequest } from "../utils/apiClient";
import { toast } from "sonner";
import { Droplets, Upload, Settings, Eye, Download, RotateCcw } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

function WatermarkPage() {
  const { user } = useAuth();
  const fileInputRef = useRef(null);
  const [settings, setSettings] = useState({
    text: "BIG MANN ENTERTAINMENT",
    position: "center",
    opacity: 0.3,
    font_size: 36,
    color: "#FFFFFF",
    rotation: -30,
    enabled: true,
  });
  const [originalImage, setOriginalImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await apiRequest("/watermark/settings");
      if (data) setSettings((prev) => ({ ...prev, ...data }));
    } catch {}
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      await apiRequest("/watermark/settings", { method: "PUT", body: JSON.stringify(settings) });
      toast.success("Watermark settings saved");
    } catch (err) {
      toast.error(err.message || "Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error("Please select an image file");
      return;
    }
    setSelectedFile(file);
    setOriginalImage(URL.createObjectURL(file));
    setPreviewUrl(null);
  };

  const generatePreview = async () => {
    if (!selectedFile) {
      toast.error("Please upload an image first");
      return;
    }
    setPreviewLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("text", settings.text);
      formData.append("position", settings.position);
      formData.append("opacity", settings.opacity.toString());
      formData.append("font_size", settings.font_size.toString());
      formData.append("color", settings.color);
      formData.append("rotation", settings.rotation.toString());

      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/api/watermark/preview`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!res.ok) throw new Error("Preview failed");
      const blob = await res.blob();
      setPreviewUrl(URL.createObjectURL(blob));
    } catch (err) {
      toast.error(err.message || "Preview failed");
    } finally {
      setPreviewLoading(false);
    }
  };

  const downloadWatermarked = () => {
    if (!previewUrl) return;
    const a = document.createElement("a");
    a.href = previewUrl;
    a.download = `watermarked_${selectedFile?.name || "image"}.png`;
    a.click();
  };

  const positions = [
    { value: "center", label: "Center" },
    { value: "top-left", label: "Top Left" },
    { value: "top-right", label: "Top Right" },
    { value: "bottom-left", label: "Bottom Left" },
    { value: "bottom-right", label: "Bottom Right" },
    { value: "tiled", label: "Tiled (Repeat)" },
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="watermark-page">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center gap-3 mb-2">
          <Droplets className="w-7 h-7 text-purple-400" />
          <h1 className="text-3xl font-bold">Content Watermarking</h1>
        </div>
        <p className="text-gray-400 mb-8">Protect your media with customizable watermarks</p>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Settings Panel */}
          <div className="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="watermark-settings">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Settings className="w-4 h-4 text-gray-400" /> Watermark Settings
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Watermark Text</label>
                <input
                  value={settings.text}
                  onChange={(e) => setSettings((s) => ({ ...s, text: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  data-testid="watermark-text-input"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Position</label>
                <select
                  value={settings.position}
                  onChange={(e) => setSettings((s) => ({ ...s, position: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
                  data-testid="watermark-position-select"
                >
                  {positions.map((p) => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Opacity: {Math.round(settings.opacity * 100)}%</label>
                <input
                  type="range"
                  min="0.05"
                  max="1"
                  step="0.05"
                  value={settings.opacity}
                  onChange={(e) => setSettings((s) => ({ ...s, opacity: parseFloat(e.target.value) }))}
                  className="w-full accent-purple-500"
                  data-testid="watermark-opacity-slider"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Font Size: {settings.font_size}px</label>
                <input
                  type="range"
                  min="12"
                  max="120"
                  step="2"
                  value={settings.font_size}
                  onChange={(e) => setSettings((s) => ({ ...s, font_size: parseInt(e.target.value) }))}
                  className="w-full accent-purple-500"
                  data-testid="watermark-fontsize-slider"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Color</label>
                  <input
                    type="color"
                    value={settings.color}
                    onChange={(e) => setSettings((s) => ({ ...s, color: e.target.value }))}
                    className="w-full h-10 rounded-lg cursor-pointer bg-gray-800 border border-gray-700"
                    data-testid="watermark-color-input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Rotation: {settings.rotation}°</label>
                  <input
                    type="range"
                    min="-90"
                    max="90"
                    step="5"
                    value={settings.rotation}
                    onChange={(e) => setSettings((s) => ({ ...s, rotation: parseInt(e.target.value) }))}
                    className="w-full accent-purple-500"
                    data-testid="watermark-rotation-slider"
                  />
                </div>
              </div>

              <button
                onClick={saveSettings}
                disabled={saving}
                className="w-full py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
                data-testid="save-settings-btn"
              >
                {saving ? "Saving..." : "Save Settings"}
              </button>
            </div>
          </div>

          {/* Preview Panel */}
          <div className="lg:col-span-3 space-y-5">
            {/* Upload */}
            <div
              className="bg-gray-900 border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-purple-500/50 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
              data-testid="upload-area"
            >
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" data-testid="file-input" />
              <Upload className="w-10 h-10 text-gray-500 mx-auto mb-3" />
              <p className="text-gray-400 text-sm">Click to upload an image or drag and drop</p>
              <p className="text-gray-600 text-xs mt-1">PNG, JPG, WebP up to 10MB</p>
            </div>

            {/* Image comparison */}
            {(originalImage || previewUrl) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {originalImage && (
                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                    <p className="text-sm text-gray-400 mb-2">Original</p>
                    <img src={originalImage} alt="Original" className="w-full rounded-lg object-contain max-h-80" data-testid="original-image" />
                  </div>
                )}
                {previewUrl && (
                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                    <p className="text-sm text-gray-400 mb-2">Watermarked</p>
                    <img src={previewUrl} alt="Watermarked" className="w-full rounded-lg object-contain max-h-80" data-testid="watermarked-image" />
                  </div>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={generatePreview}
                disabled={!selectedFile || previewLoading}
                className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
                data-testid="preview-btn"
              >
                {previewLoading ? <RotateCcw className="w-4 h-4 animate-spin" /> : <Eye className="w-4 h-4" />}
                {previewLoading ? "Generating..." : "Preview Watermark"}
              </button>
              {previewUrl && (
                <button
                  onClick={downloadWatermarked}
                  className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium transition-colors"
                  data-testid="download-btn"
                >
                  <Download className="w-4 h-4" /> Download
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WatermarkPage;
