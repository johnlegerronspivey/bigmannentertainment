import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { apiRequest } from "../utils/apiClient";
import { toast } from "sonner";
import { User, MapPin, Globe, Music, Edit3, Save, X, Search } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

function CreatorProfilesPage() {
  const { user } = useAuth();
  const [myProfile, setMyProfile] = useState(null);
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [tab, setTab] = useState("my-profile");

  const [form, setForm] = useState({
    display_name: "",
    username: "",
    bio: "",
    tagline: "",
    location: "",
    genres: "",
    website: "",
    profile_public: true,
    show_earnings: false,
  });

  useEffect(() => {
    loadMyProfile();
    loadProfiles();
  }, []);

  const loadMyProfile = async () => {
    try {
      const data = await apiRequest("/creator-profiles/me");
      setMyProfile(data);
      setForm({
        display_name: data.display_name || "",
        username: data.username || "",
        bio: data.bio || "",
        tagline: data.tagline || "",
        location: data.location || "",
        genres: (data.genres || []).join(", "),
        website: data.website || "",
        profile_public: data.profile_public ?? true,
        show_earnings: data.show_earnings ?? false,
      });
    } catch {
      setMyProfile(null);
      setShowCreate(true);
    } finally {
      setLoading(false);
    }
  };

  const loadProfiles = async (q) => {
    try {
      const search = q || searchQuery;
      const url = search ? `/creator-profiles/browse?search=${encodeURIComponent(search)}` : "/creator-profiles/browse";
      const data = await apiRequest(url);
      setProfiles(data.profiles || []);
    } catch {
      setProfiles([]);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        display_name: form.display_name,
        username: form.username,
        bio: form.bio,
        tagline: form.tagline,
        location: form.location,
        genres: form.genres.split(",").map((g) => g.trim()).filter(Boolean),
        profile_public: form.profile_public,
        show_earnings: form.show_earnings,
      };
      const data = await apiRequest("/creator-profiles", { method: "POST", body: JSON.stringify(payload) });
      setMyProfile(data);
      setShowCreate(false);
      toast.success("Profile created!");
      loadProfiles();
    } catch (err) {
      toast.error(err.message || "Failed to create profile");
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        display_name: form.display_name,
        bio: form.bio,
        tagline: form.tagline,
        location: form.location,
        website: form.website,
        genres: form.genres.split(",").map((g) => g.trim()).filter(Boolean),
        profile_public: form.profile_public,
        show_earnings: form.show_earnings,
      };
      const data = await apiRequest("/creator-profiles/me", { method: "PUT", body: JSON.stringify(payload) });
      setMyProfile(data);
      setEditing(false);
      toast.success("Profile updated!");
      loadProfiles();
    } catch (err) {
      toast.error(err.message || "Failed to update profile");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="creator-profiles-page">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Creator Profiles</h1>
        <p className="text-gray-400 mb-6">Build your public presence and connect with fans</p>

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-gray-800 pb-2" data-testid="profile-tabs">
          <button
            onClick={() => setTab("my-profile")}
            className={`pb-2 px-1 text-sm font-medium transition-colors ${tab === "my-profile" ? "text-purple-400 border-b-2 border-purple-400" : "text-gray-500 hover:text-gray-300"}`}
            data-testid="tab-my-profile"
          >
            My Profile
          </button>
          <button
            onClick={() => setTab("browse")}
            className={`pb-2 px-1 text-sm font-medium transition-colors ${tab === "browse" ? "text-purple-400 border-b-2 border-purple-400" : "text-gray-500 hover:text-gray-300"}`}
            data-testid="tab-browse"
          >
            Browse Creators
          </button>
        </div>

        {tab === "my-profile" && (
          <>
            {!myProfile && showCreate ? (
              <ProfileForm title="Create Your Profile" form={form} setForm={setForm} onSubmit={handleCreate} submitLabel="Create Profile" />
            ) : myProfile && editing ? (
              <ProfileForm title="Edit Profile" form={form} setForm={setForm} onSubmit={handleUpdate} submitLabel="Save Changes" onCancel={() => setEditing(false)} />
            ) : myProfile ? (
              <ProfileCard profile={myProfile} isOwner onEdit={() => setEditing(true)} />
            ) : null}
          </>
        )}

        {tab === "browse" && (
          <div>
            <div className="flex gap-3 mb-6" data-testid="profile-search">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search creators..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && loadProfiles()}
                  className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  data-testid="search-input"
                />
              </div>
              <button onClick={() => loadProfiles()} className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium" data-testid="search-btn">
                Search
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {profiles.map((p) => (
                <ProfileCard key={p.id} profile={p} />
              ))}
              {profiles.length === 0 && <p className="text-gray-500 col-span-3 text-center py-12">No creators found</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ProfileCard({ profile, isOwner, onEdit }) {
  const initials = (profile.display_name || "U").charAt(0).toUpperCase();
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-purple-500/50 transition-all" data-testid="profile-card">
      <div className="flex items-start gap-4">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-2xl font-bold flex-shrink-0">
          {profile.avatar_url ? <img src={profile.avatar_url} alt="" className="w-16 h-16 rounded-full object-cover" /> : initials}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-lg truncate">{profile.display_name}</h3>
            {profile.verified && <span className="text-blue-400 text-xs bg-blue-400/10 px-2 py-0.5 rounded-full">Verified</span>}
            {profile.subscription_tier !== "free" && (
              <span className="text-amber-400 text-xs bg-amber-400/10 px-2 py-0.5 rounded-full capitalize">{profile.subscription_tier}</span>
            )}
          </div>
          <p className="text-gray-500 text-sm">@{profile.username}</p>
          {profile.tagline && <p className="text-gray-300 text-sm mt-1">{profile.tagline}</p>}
        </div>
        {isOwner && onEdit && (
          <button onClick={onEdit} className="p-2 text-gray-400 hover:text-purple-400 transition-colors" data-testid="edit-profile-btn">
            <Edit3 className="w-4 h-4" />
          </button>
        )}
      </div>

      {profile.bio && <p className="text-gray-400 text-sm mt-4 line-clamp-3">{profile.bio}</p>}

      <div className="flex flex-wrap gap-2 mt-4">
        {(profile.genres || []).map((g) => (
          <span key={g} className="text-xs bg-purple-500/10 text-purple-300 px-2.5 py-1 rounded-full">{g}</span>
        ))}
      </div>

      {profile.location && (
        <div className="flex items-center gap-1.5 mt-3 text-gray-500 text-sm">
          <MapPin className="w-3.5 h-3.5" /> {profile.location}
        </div>
      )}

      {profile.stats && (
        <div className="grid grid-cols-3 gap-3 mt-5 pt-4 border-t border-gray-800">
          <div className="text-center">
            <div className="text-lg font-semibold">{profile.stats.total_assets || 0}</div>
            <div className="text-xs text-gray-500">Assets</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold">{profile.stats.total_streams || 0}</div>
            <div className="text-xs text-gray-500">Streams</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold">{profile.stats.total_followers || 0}</div>
            <div className="text-xs text-gray-500">Followers</div>
          </div>
        </div>
      )}
    </div>
  );
}

function ProfileForm({ title, form, setForm, onSubmit, submitLabel, onCancel }) {
  const change = (field, value) => setForm((prev) => ({ ...prev, [field]: value }));
  return (
    <form onSubmit={onSubmit} className="bg-gray-900 border border-gray-800 rounded-xl p-6 max-w-2xl" data-testid="profile-form">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">{title}</h2>
        {onCancel && (
          <button type="button" onClick={onCancel} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Display Name *</label>
            <input value={form.display_name} onChange={(e) => change("display_name", e.target.value)} required className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="input-display-name" />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Username *</label>
            <input value={form.username} onChange={(e) => change("username", e.target.value)} required className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="input-username" />
          </div>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Tagline</label>
          <input value={form.tagline} onChange={(e) => change("tagline", e.target.value)} placeholder="A short description of what you do" className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="input-tagline" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Bio</label>
          <textarea value={form.bio} onChange={(e) => change("bio", e.target.value)} rows={3} className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 resize-none" data-testid="input-bio" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Location</label>
            <input value={form.location} onChange={(e) => change("location", e.target.value)} className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="input-location" />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Website</label>
            <input value={form.website} onChange={(e) => change("website", e.target.value)} className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="input-website" />
          </div>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Genres (comma separated)</label>
          <input value={form.genres} onChange={(e) => change("genres", e.target.value)} placeholder="Hip Hop, R&B, Pop" className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-500" data-testid="input-genres" />
        </div>
        <div className="flex gap-6">
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.profile_public} onChange={(e) => change("profile_public", e.target.checked)} className="rounded bg-gray-800 border-gray-600" data-testid="check-public" />
            <span className="text-gray-300">Public profile</span>
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.show_earnings} onChange={(e) => change("show_earnings", e.target.checked)} className="rounded bg-gray-800 border-gray-600" data-testid="check-earnings" />
            <span className="text-gray-300">Show earnings</span>
          </label>
        </div>
      </div>
      <div className="flex gap-3 mt-6">
        <button type="submit" className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium transition-colors" data-testid="submit-profile-btn">
          <Save className="w-4 h-4" /> {submitLabel}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors">
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default CreatorProfilesPage;
