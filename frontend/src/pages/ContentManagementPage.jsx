import React, { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../utils/apiClient";
import { toast } from "sonner";
import { Upload, FileAudio, FileVideo, Image, Trash2, Edit3, Search, Eye, Download, Heart, X, Save, Filter, Play, Pause, Volume2, MessageCircle, Send, ChevronDown, ChevronUp } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function ContentManagementPage() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showUpload, setShowUpload] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("");
  const [editForm, setEditForm] = useState({ title: "", description: "", tags: "", visibility: "public" });

  const loadContent = useCallback(async () => {
    try {
      let url = `/user-content?limit=20`;
      if (filterType) url += `&content_type=${filterType}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      const data = await api.get(url);
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [filterType, search]);

  useEffect(() => { loadContent(); }, [loadContent]);

  const handleUpload = async (e) => {
    e.preventDefault();
    const form = e.target;
    const file = form.file.files[0];
    if (!file) return toast.error("Please select a file");

    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", form.title.value || "");
    formData.append("description", form.description.value || "");
    formData.append("tags", form.tags.value || "");
    formData.append("visibility", form.visibility.value || "public");

    try {
      const token = localStorage.getItem("token");
      const xhr = new XMLHttpRequest();
      await new Promise((resolve, reject) => {
        xhr.upload.addEventListener("progress", (ev) => {
          if (ev.lengthComputable) setUploadProgress(Math.round((ev.loaded / ev.total) * 100));
        });
        xhr.addEventListener("load", () => {
          if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText));
          else reject(new Error(xhr.responseText || "Upload failed"));
        });
        xhr.addEventListener("error", () => reject(new Error("Network error")));
        xhr.open("POST", `${BACKEND_URL}/api/user-content/upload`);
        if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);
        xhr.send(formData);
      });
      toast.success("Content uploaded!");
      setShowUpload(false);
      form.reset();
      loadContent();
    } catch (err) {
      toast.error(err.message || "Upload failed");
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this content? This cannot be undone.")) return;
    try {
      await api.delete(`/user-content/${id}`);
      toast.success("Content deleted");
      loadContent();
    } catch (err) {
      toast.error(err.message || "Delete failed");
    }
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setEditForm({
      title: item.title || "",
      description: item.description || "",
      tags: (item.tags || []).join(", "),
      visibility: item.visibility || "public",
    });
  };

  const handleUpdate = async () => {
    try {
      await api.put(`/user-content/${editingId}`, {
        title: editForm.title,
        description: editForm.description,
        tags: editForm.tags.split(",").map((t) => t.trim()).filter(Boolean),
        visibility: editForm.visibility,
      });
      toast.success("Content updated");
      setEditingId(null);
      loadContent();
    } catch (err) {
      toast.error(err.message || "Update failed");
    }
  };

  const typeIcon = (type) => {
    if (type === "audio") return <FileAudio className="w-5 h-5 text-green-400" />;
    if (type === "video") return <FileVideo className="w-5 h-5 text-blue-400" />;
    return <Image className="w-5 h-5 text-pink-400" />;
  };

  const fileUrl = (fileId) => `${BACKEND_URL}/api/user-content/file/${fileId}`;

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  // ── Comment Section (inline per content item) ──
  const CommentSection = ({ contentId, commentCount }) => {
    const [open, setOpen] = useState(false);
    const [comments, setComments] = useState([]);
    const [total, setTotal] = useState(commentCount || 0);
    const [newComment, setNewComment] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [loadingComments, setLoadingComments] = useState(false);

    const loadComments = async () => {
      setLoadingComments(true);
      try {
        const data = await api.get(`/user-content/${contentId}/comments?limit=20`);
        setComments(data.items || []);
        setTotal(data.total || 0);
      } catch {
        setComments([]);
      } finally {
        setLoadingComments(false);
      }
    };

    const toggleOpen = () => {
      if (!open) loadComments();
      setOpen(!open);
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!newComment.trim()) return;
      setSubmitting(true);
      try {
        const created = await api.post(`/user-content/${contentId}/comments`, { text: newComment.trim() });
        setComments((prev) => [created, ...prev]);
        setTotal((prev) => prev + 1);
        setNewComment("");
        toast.success("Comment added");
      } catch (err) {
        toast.error(err.message || "Failed to add comment");
      } finally {
        setSubmitting(false);
      }
    };

    const handleDelete = async (commentId) => {
      try {
        await api.delete(`/user-content/comments/${commentId}`);
        setComments((prev) => prev.filter((c) => c.id !== commentId));
        setTotal((prev) => Math.max(0, prev - 1));
        toast.success("Comment deleted");
      } catch (err) {
        toast.error(err.message || "Delete failed");
      }
    };

    const timeAgo = (iso) => {
      if (!iso) return "";
      const diff = (Date.now() - new Date(iso).getTime()) / 1000;
      if (diff < 60) return "just now";
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
      return `${Math.floor(diff / 86400)}d ago`;
    };

    return (
      <div className="mt-3 border-t border-gray-800 pt-3" data-testid="comment-section">
        <button
          onClick={toggleOpen}
          className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-purple-300 transition-colors"
          data-testid="toggle-comments-btn"
        >
          <MessageCircle className="w-3.5 h-3.5" />
          <span>{total} comment{total !== 1 ? "s" : ""}</span>
          {open ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>

        {open && (
          <div className="mt-3 space-y-3" data-testid="comments-panel">
            {/* Add comment form */}
            <form onSubmit={handleSubmit} className="flex gap-2" data-testid="add-comment-form">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Write a comment..."
                className="flex-1 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-xs focus:ring-1 focus:ring-purple-500 focus:border-purple-500"
                maxLength={2000}
                data-testid="comment-input"
              />
              <button
                type="submit"
                disabled={submitting || !newComment.trim()}
                className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-40 rounded-lg text-xs flex items-center gap-1"
                data-testid="submit-comment-btn"
              >
                <Send className="w-3 h-3" />
              </button>
            </form>

            {/* Comments list */}
            {loadingComments ? (
              <p className="text-xs text-gray-600">Loading comments...</p>
            ) : comments.length === 0 ? (
              <p className="text-xs text-gray-600" data-testid="no-comments">No comments yet. Be the first!</p>
            ) : (
              <div className="space-y-2 max-h-48 overflow-y-auto" data-testid="comments-list">
                {comments.map((c) => (
                  <div key={c.id} className="flex items-start gap-2 bg-gray-800/40 rounded-lg px-3 py-2" data-testid="comment-item">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-purple-300" data-testid="comment-author">{c.user_name}</span>
                        <span className="text-[10px] text-gray-600">{timeAgo(c.created_at)}</span>
                      </div>
                      <p className="text-xs text-gray-300 mt-0.5 break-words" data-testid="comment-text">{c.text}</p>
                    </div>
                    {(c.user_id === (user?.id || user?.user_id)) && (
                      <button
                        onClick={() => handleDelete(c.id)}
                        className="p-1 text-gray-600 hover:text-red-400 shrink-0"
                        title="Delete comment"
                        data-testid="delete-comment-btn"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="content-management-page">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold" data-testid="content-page-title">Content Management</h1>
            <p className="text-gray-400 mt-1">Upload and manage your media content</p>
          </div>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium transition-colors"
            data-testid="toggle-upload-btn"
          >
            <Upload className="w-4 h-4" /> Upload Content
          </button>
        </div>

        {/* Upload Form */}
        {showUpload && (
          <form onSubmit={handleUpload} className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8" data-testid="upload-form">
            <h2 className="text-lg font-semibold mb-4">Upload New Content</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-400 mb-1">File *</label>
                <input type="file" name="file" required accept="audio/*,video/*,image/*,.mp3,.wav,.flac,.mp4,.mov,.avi,.jpg,.jpeg,.png,.gif,.webp" className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-600 file:text-white hover:file:bg-purple-700" data-testid="upload-file-input" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Title</label>
                <input name="title" placeholder="Content title" className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="upload-title-input" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Tags (comma separated)</label>
                <input name="tags" placeholder="hip-hop, beat, new" className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="upload-tags-input" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Visibility</label>
                <select name="visibility" defaultValue="public" className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="upload-visibility-select">
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                  <option value="subscribers">Subscribers Only</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description</label>
                <input name="description" placeholder="Optional description" className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="upload-desc-input" />
              </div>
            </div>
            {uploading && (
              <div className="mt-4">
                <div className="w-full bg-gray-800 rounded-full h-2.5">
                  <div className="bg-purple-600 h-2.5 rounded-full transition-all" style={{ width: `${uploadProgress}%` }} />
                </div>
                <p className="text-xs text-gray-400 mt-1">{uploadProgress}% uploaded</p>
              </div>
            )}
            <div className="flex gap-3 mt-4">
              <button type="submit" disabled={uploading} className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg text-sm font-medium" data-testid="upload-submit-btn">
                <Upload className="w-4 h-4" /> {uploading ? "Uploading..." : "Upload"}
              </button>
              <button type="button" onClick={() => setShowUpload(false)} className="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm">Cancel</button>
            </div>
          </form>
        )}

        {/* Filters */}
        <div className="flex gap-3 mb-6 flex-wrap" data-testid="content-filters">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search content..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadContent()}
              className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
              data-testid="content-search-input"
            />
          </div>
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="px-3 py-2.5 bg-gray-900 border border-gray-700 rounded-lg text-sm" data-testid="content-type-filter">
            <option value="">All Types</option>
            <option value="audio">Audio</option>
            <option value="video">Video</option>
            <option value="image">Image</option>
          </select>
          <button onClick={loadContent} className="px-4 py-2.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium" data-testid="content-search-btn">
            <Filter className="w-4 h-4" />
          </button>
        </div>

        <p className="text-sm text-gray-500 mb-4" data-testid="content-total-count">{total} item{total !== 1 ? "s" : ""} total</p>

        {/* Content Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5" data-testid="content-grid">
          {items.map((item) => (
            <div key={item.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-purple-500/30 transition-all" data-testid="content-item">
              {editingId === item.id ? (
                <div className="space-y-3">
                  <input value={editForm.title} onChange={(e) => setEditForm({ ...editForm, title: e.target.value })} className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm" data-testid="edit-title-input" />
                  <input value={editForm.description} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} placeholder="Description" className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm" data-testid="edit-desc-input" />
                  <input value={editForm.tags} onChange={(e) => setEditForm({ ...editForm, tags: e.target.value })} placeholder="Tags" className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm" data-testid="edit-tags-input" />
                  <select value={editForm.visibility} onChange={(e) => setEditForm({ ...editForm, visibility: e.target.value })} className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm" data-testid="edit-visibility-select">
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                    <option value="subscribers">Subscribers</option>
                  </select>
                  <div className="flex gap-2">
                    <button onClick={handleUpdate} className="flex items-center gap-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded-lg text-xs" data-testid="save-edit-btn"><Save className="w-3 h-3" /> Save</button>
                    <button onClick={() => setEditingId(null)} className="flex items-center gap-1 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-xs" data-testid="cancel-edit-btn"><X className="w-3 h-3" /> Cancel</button>
                  </div>
                </div>
              ) : (
                <>
                  {/* File Preview */}
                  <div className="mb-3 rounded-lg overflow-hidden bg-gray-800/50" data-testid="content-preview">
                    {item.content_type === "image" && (
                      <img
                        src={fileUrl(item.file_id)}
                        alt={item.title}
                        className="w-full h-40 object-cover"
                        loading="lazy"
                        data-testid="image-preview"
                      />
                    )}
                    {item.content_type === "audio" && (
                      <div className="p-3 flex flex-col items-center gap-2" data-testid="audio-preview">
                        <div className="w-full flex items-center justify-center h-20 bg-gradient-to-br from-green-900/30 to-gray-900 rounded-md">
                          <Volume2 className="w-8 h-8 text-green-400 opacity-60" />
                        </div>
                        <audio
                          controls
                          preload="metadata"
                          className="w-full h-8 [&::-webkit-media-controls-panel]:bg-gray-700 [&::-webkit-media-controls-panel]:rounded-md"
                          data-testid="audio-player"
                        >
                          <source src={fileUrl(item.file_id)} />
                        </audio>
                      </div>
                    )}
                    {item.content_type === "video" && (
                      <video
                        controls
                        preload="metadata"
                        className="w-full h-40 object-cover bg-black"
                        data-testid="video-preview"
                      >
                        <source src={fileUrl(item.file_id)} />
                      </video>
                    )}
                    {!["image", "audio", "video"].includes(item.content_type) && (
                      <div className="h-24 flex items-center justify-center">
                        {typeIcon(item.content_type)}
                      </div>
                    )}
                  </div>

                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {typeIcon(item.content_type)}
                      <h3 className="font-medium text-sm truncate max-w-[180px]" data-testid="content-item-title">{item.title}</h3>
                    </div>
                    <div className="flex gap-1">
                      <button onClick={() => startEdit(item)} className="p-1.5 text-gray-500 hover:text-purple-400" data-testid="edit-content-btn"><Edit3 className="w-3.5 h-3.5" /></button>
                      <button onClick={() => handleDelete(item.id)} className="p-1.5 text-gray-500 hover:text-red-400" data-testid="delete-content-btn"><Trash2 className="w-3.5 h-3.5" /></button>
                    </div>
                  </div>
                  {item.description && <p className="text-gray-500 text-xs mt-2 line-clamp-2">{item.description}</p>}
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {(item.tags || []).map((t) => (
                      <span key={t} className="text-xs bg-purple-500/10 text-purple-300 px-2 py-0.5 rounded-full">{t}</span>
                    ))}
                  </div>
                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-800">
                    <div className="flex gap-3 text-xs text-gray-500">
                      <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {item.stats?.views || 0}</span>
                      <span className="flex items-center gap-1"><Download className="w-3 h-3" /> {item.stats?.downloads || 0}</span>
                      <span className="flex items-center gap-1"><Heart className="w-3 h-3" /> {item.stats?.likes || 0}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${item.visibility === "public" ? "bg-green-500/10 text-green-400" : item.visibility === "private" ? "bg-red-500/10 text-red-400" : "bg-amber-500/10 text-amber-400"}`} data-testid="content-visibility-badge">
                        {item.visibility}
                      </span>
                      <span className="text-xs text-gray-600">{formatSize(item.file_size)}</span>
                    </div>
                  </div>
                  <CommentSection contentId={item.id} commentCount={item.stats?.comments || 0} />
                </>
              )}
            </div>
          ))}
          {items.length === 0 && (
            <div className="col-span-3 text-center py-16" data-testid="content-empty-state">
              <Upload className="w-12 h-12 text-gray-700 mx-auto mb-3" />
              <p className="text-gray-500">No content yet. Upload your first file to get started!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ContentManagementPage;
