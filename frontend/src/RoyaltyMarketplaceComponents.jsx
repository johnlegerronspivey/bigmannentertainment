import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Helper function for API calls
const apiCall = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }
  
  return response.json();
};

// Format currency
const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

// Format date
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Time remaining for auctions
const getTimeRemaining = (endDate) => {
  const total = new Date(endDate) - new Date();
  if (total <= 0) return 'Ended';
  
  const days = Math.floor(total / (1000 * 60 * 60 * 24));
  const hours = Math.floor((total % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((total % (1000 * 60 * 60)) / (1000 * 60));
  
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const statusColors = {
    active: 'bg-green-100 text-green-800',
    draft: 'bg-gray-100 text-gray-800',
    sold: 'bg-blue-100 text-blue-800',
    expired: 'bg-red-100 text-red-800',
    cancelled: 'bg-red-100 text-red-800',
    pending: 'bg-yellow-100 text-yellow-800',
  };
  
  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status?.toUpperCase()}
    </span>
  );
};

// Listing Card Component
const ListingCard = ({ listing, onView, onBid, onWatch }) => {
  const isAuction = ['auction', 'reserve_auction', 'dutch_auction'].includes(listing.listing_type);
  
  return (
    <div 
      data-testid={`listing-card-${listing.id}`}
      className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-100 overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-gray-900 line-clamp-1">{listing.title}</h3>
          <StatusBadge status={listing.status} />
        </div>
        <p className="text-sm text-gray-500 line-clamp-2">{listing.description}</p>
      </div>
      
      {/* Details */}
      <div className="p-4 space-y-3">
        {/* Artist/Asset Info */}
        {listing.artist_name && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-500">Artist:</span>
            <span className="font-medium text-gray-800">{listing.artist_name}</span>
          </div>
        )}
        
        {/* Royalty Info */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Royalty Share:</span>
          <span className="font-semibold text-purple-600">{listing.royalty_percentage}%</span>
        </div>
        
        {/* Historical Revenue */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Historical Revenue:</span>
          <span className="font-medium">{formatCurrency(listing.historical_revenue || 0)}</span>
        </div>
        
        {/* Price Info */}
        <div className="pt-2 border-t border-gray-100">
          {isAuction ? (
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Current Bid:</span>
                <span className="font-bold text-lg text-purple-600">
                  {formatCurrency(listing.current_bid || listing.asking_price)}
                </span>
              </div>
              {listing.auction_end && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Ends in:</span>
                  <span className="font-medium text-orange-600">{getTimeRemaining(listing.auction_end)}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Price:</span>
              <span className="font-bold text-lg text-green-600">{formatCurrency(listing.asking_price)}</span>
            </div>
          )}
        </div>
        
        {/* Buy Now Option */}
        {listing.buy_now_price && (
          <div className="flex items-center justify-between text-sm bg-yellow-50 p-2 rounded">
            <span className="text-yellow-700">Buy Now:</span>
            <span className="font-bold text-yellow-700">{formatCurrency(listing.buy_now_price)}</span>
          </div>
        )}
      </div>
      
      {/* Actions */}
      <div className="p-4 bg-gray-50 flex gap-2">
        <button
          data-testid={`view-listing-${listing.id}`}
          onClick={() => onView(listing.id)}
          className="flex-1 px-3 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
        >
          View Details
        </button>
        {listing.status === 'active' && (
          <>
            {isAuction ? (
              <button
                data-testid={`bid-listing-${listing.id}`}
                onClick={() => onBid(listing)}
                className="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                Place Bid
              </button>
            ) : (
              <button
                data-testid={`buy-listing-${listing.id}`}
                onClick={() => onBid(listing)}
                className="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                Buy
              </button>
            )}
          </>
        )}
        <button
          onClick={() => onWatch(listing.id)}
          className="px-3 py-2 border border-gray-300 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-100 transition-colors"
        >
          ♥
        </button>
      </div>
    </div>
  );
};

// Create Listing Modal
const CreateListingModal = ({ isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    asset_id: '',
    listing_type: 'fixed_price',
    royalty_type: 'percentage_share',
    royalty_percentage: 10,
    asking_price: 0,
    buy_now_price: '',
    minimum_price: '',
    historical_revenue: 0,
    projected_revenue: 0,
    duration_months: '',
    artist_name: '',
    genre: '',
    tags: '',
  });
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const payload = {
        ...formData,
        asking_price: parseFloat(formData.asking_price) || 0,
        royalty_percentage: parseFloat(formData.royalty_percentage) || 10,
        historical_revenue: parseFloat(formData.historical_revenue) || 0,
        projected_revenue: parseFloat(formData.projected_revenue) || 0,
        buy_now_price: formData.buy_now_price ? parseFloat(formData.buy_now_price) : null,
        minimum_price: formData.minimum_price ? parseFloat(formData.minimum_price) : null,
        duration_months: formData.duration_months ? parseInt(formData.duration_months) : null,
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()) : [],
      };
      
      await onSubmit(payload);
      onClose();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Create Royalty Listing</h2>
          <p className="text-sm text-gray-500 mt-1">List your royalty rights on the marketplace</p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Basic Information</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input
                data-testid="listing-title-input"
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                placeholder="e.g., 10% Royalty Share - Summer Hits Album"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
              <textarea
                data-testid="listing-description-input"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                rows={3}
                placeholder="Describe the royalty rights being sold..."
                required
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Artist Name</label>
                <input
                  type="text"
                  value={formData.artist_name}
                  onChange={(e) => setFormData({ ...formData, artist_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Artist or Creator"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Genre</label>
                <input
                  type="text"
                  value={formData.genre}
                  onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="e.g., Hip-Hop, R&B"
                />
              </div>
            </div>
          </div>
          
          {/* Listing Type */}
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Listing Type</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sale Type *</label>
                <select
                  data-testid="listing-type-select"
                  value={formData.listing_type}
                  onChange={(e) => setFormData({ ...formData, listing_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="fixed_price">Fixed Price</option>
                  <option value="auction">Auction</option>
                  <option value="reserve_auction">Reserve Auction</option>
                  <option value="dutch_auction">Dutch Auction</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Royalty Type *</label>
                <select
                  value={formData.royalty_type}
                  onChange={(e) => setFormData({ ...formData, royalty_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="full_ownership">Full Ownership (100%)</option>
                  <option value="percentage_share">Percentage Share</option>
                  <option value="time_limited">Time Limited</option>
                  <option value="revenue_cap">Revenue Cap</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Royalty Details */}
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Royalty Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Royalty Percentage *</label>
                <input
                  data-testid="royalty-percentage-input"
                  type="number"
                  min="1"
                  max="100"
                  value={formData.royalty_percentage}
                  onChange={(e) => setFormData({ ...formData, royalty_percentage: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Historical Revenue (12mo)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.historical_revenue}
                  onChange={(e) => setFormData({ ...formData, historical_revenue: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="$0.00"
                />
              </div>
            </div>
            
            {formData.royalty_type === 'time_limited' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Duration (Months)</label>
                <input
                  type="number"
                  min="1"
                  value={formData.duration_months}
                  onChange={(e) => setFormData({ ...formData, duration_months: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="12"
                />
              </div>
            )}
          </div>
          
          {/* Pricing */}
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Pricing</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {formData.listing_type === 'fixed_price' ? 'Price *' : 'Starting Bid *'}
                </label>
                <input
                  data-testid="asking-price-input"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.asking_price}
                  onChange={(e) => setFormData({ ...formData, asking_price: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  required
                />
              </div>
              
              {formData.listing_type !== 'fixed_price' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Buy Now Price</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.buy_now_price}
                    onChange={(e) => setFormData({ ...formData, buy_now_price: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    placeholder="Optional"
                  />
                </div>
              )}
            </div>
            
            {formData.listing_type === 'reserve_auction' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reserve Price</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.minimum_price}
                  onChange={(e) => setFormData({ ...formData, minimum_price: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Minimum price to sell"
                />
              </div>
            )}
          </div>
          
          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              placeholder="hip-hop, streaming, catalog (comma separated)"
            />
          </div>
          
          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              data-testid="submit-listing-btn"
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Listing'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Bid Modal
const BidModal = ({ isOpen, onClose, listing, onSubmit }) => {
  const [bidAmount, setBidAmount] = useState('');
  const [maxBid, setMaxBid] = useState('');
  const [loading, setLoading] = useState(false);
  
  const isAuction = ['auction', 'reserve_auction', 'dutch_auction'].includes(listing?.listing_type);
  const minBid = listing ? (parseFloat(listing.current_bid || listing.asking_price) + parseFloat(listing.bid_increment || 100)) : 0;
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await onSubmit({
        amount: parseFloat(bidAmount),
        max_amount: maxBid ? parseFloat(maxBid) : null,
      });
      onClose();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  if (!isOpen || !listing) return null;
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-md w-full">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">
            {isAuction ? 'Place Bid' : 'Purchase Royalty'}
          </h2>
          <p className="text-sm text-gray-500 mt-1">{listing.title}</p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {isAuction ? (
            <>
              <div className="bg-gray-50 p-3 rounded-lg space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Current Bid:</span>
                  <span className="font-semibold">{formatCurrency(listing.current_bid || listing.asking_price)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Minimum Bid:</span>
                  <span className="font-semibold text-purple-600">{formatCurrency(minBid)}</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Your Bid *</label>
                <input
                  data-testid="bid-amount-input"
                  type="number"
                  min={minBid}
                  step="0.01"
                  value={bidAmount}
                  onChange={(e) => setBidAmount(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder={`Min: ${formatCurrency(minBid)}`}
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Auto-Bid (Optional)</label>
                <input
                  type="number"
                  min={bidAmount || minBid}
                  step="0.01"
                  value={maxBid}
                  onChange={(e) => setMaxBid(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Auto-bid up to this amount"
                />
                <p className="text-xs text-gray-500 mt-1">We'll bid on your behalf up to this maximum</p>
              </div>
            </>
          ) : (
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <p className="text-gray-600 mb-2">Purchase Price</p>
              <p className="text-3xl font-bold text-green-600">{formatCurrency(listing.asking_price)}</p>
            </div>
          )}
          
          {listing.buy_now_price && isAuction && (
            <div className="bg-yellow-50 p-3 rounded-lg">
              <p className="text-sm text-yellow-700">
                Skip the auction! Buy now for <strong>{formatCurrency(listing.buy_now_price)}</strong>
              </p>
            </div>
          )}
          
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              data-testid="submit-bid-btn"
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Processing...' : (isAuction ? 'Place Bid' : 'Purchase')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Stats Card Component
const StatsCard = ({ icon, label, value, change }) => (
  <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-xl">
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-xl font-bold text-gray-900">{value}</p>
        {change && (
          <p className={`text-xs ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change >= 0 ? '+' : ''}{change}% from last period
          </p>
        )}
      </div>
    </div>
  </div>
);

// Main Marketplace Dashboard
const RoyaltyMarketplaceDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('browse');
  const [listings, setListings] = useState([]);
  const [myListings, setMyListings] = useState([]);
  const [myBids, setMyBids] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [stats, setStats] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    listing_type: '',
    royalty_type: '',
    min_price: '',
    max_price: '',
    sort_by: 'created_at',
  });
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showBidModal, setShowBidModal] = useState(false);
  const [selectedListing, setSelectedListing] = useState(null);

  // Fetch listings
  const fetchListings = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      if (filters.listing_type) params.append('listing_type', filters.listing_type);
      if (filters.royalty_type) params.append('royalty_type', filters.royalty_type);
      if (filters.min_price) params.append('min_price', filters.min_price);
      if (filters.max_price) params.append('max_price', filters.max_price);
      params.append('sort_by', filters.sort_by);
      
      const result = await apiCall(`/marketplace/listings?${params.toString()}`);
      setListings(result.listings || []);
    } catch (error) {
      console.error('Failed to fetch listings:', error);
    }
  }, [searchQuery, filters]);

  // Fetch user data
  const fetchUserData = useCallback(async () => {
    try {
      const [myListingsRes, myBidsRes, watchlistRes, userStatsRes] = await Promise.all([
        apiCall('/marketplace/my-listings').catch(() => ({ listings: [] })),
        apiCall('/marketplace/my-bids').catch(() => ({ bids: [] })),
        apiCall('/marketplace/watchlist').catch(() => ({ watchlist: [] })),
        apiCall('/marketplace/my-stats').catch(() => ({ stats: {} })),
      ]);
      
      setMyListings(myListingsRes.listings || []);
      setMyBids(myBidsRes.bids || []);
      setWatchlist(watchlistRes.watchlist || []);
      setUserStats(userStatsRes.stats || {});
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    }
  }, []);

  // Fetch marketplace stats
  const fetchStats = useCallback(async () => {
    try {
      const result = await apiCall('/marketplace/stats');
      setStats(result.stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  }, []);

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchListings(), fetchUserData(), fetchStats()]);
      setLoading(false);
    };
    loadData();
  }, [fetchListings, fetchUserData, fetchStats]);

  // Handlers
  const handleCreateListing = async (data) => {
    const result = await apiCall('/marketplace/listings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    toast.success('Listing created successfully!');
    fetchUserData();
    
    // Optionally publish immediately
    if (window.confirm('Would you like to publish this listing now?')) {
      await apiCall(`/marketplace/listings/${result.listing_id}/publish`, { method: 'POST' });
      toast.success('Listing published!');
      fetchListings();
    }
  };

  const handlePlaceBid = async (listing) => {
    setSelectedListing(listing);
    setShowBidModal(true);
  };

  const handleSubmitBid = async (bidData) => {
    const isAuction = ['auction', 'reserve_auction', 'dutch_auction'].includes(selectedListing.listing_type);
    
    if (isAuction) {
      await apiCall(`/marketplace/listings/${selectedListing.id}/bids`, {
        method: 'POST',
        body: JSON.stringify(bidData),
      });
      toast.success('Bid placed successfully!');
    } else {
      await apiCall(`/marketplace/listings/${selectedListing.id}/buy-now`, {
        method: 'POST',
      });
      toast.success('Purchase initiated!');
    }
    
    fetchListings();
    fetchUserData();
  };

  const handleAddToWatchlist = async (listingId) => {
    try {
      await apiCall(`/marketplace/watchlist/${listingId}`, { method: 'POST' });
      toast.success('Added to watchlist');
      fetchUserData();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleViewListing = (listingId) => {
    navigate(`/marketplace/listing/${listingId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading marketplace...</p>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="royalty-marketplace" className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-700 text-white py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold">Royalty Marketplace</h1>
              <p className="text-purple-200 mt-1">Buy, sell, and trade royalty rights</p>
            </div>
            <button
              data-testid="create-listing-btn"
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-white text-purple-600 font-semibold rounded-lg hover:bg-gray-100 transition-colors"
            >
              + Create Listing
            </button>
          </div>
          
          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-white/10 rounded-lg p-3">
                <p className="text-purple-200 text-sm">Active Listings</p>
                <p className="text-2xl font-bold">{stats.active_listings || 0}</p>
              </div>
              <div className="bg-white/10 rounded-lg p-3">
                <p className="text-purple-200 text-sm">Total Volume</p>
                <p className="text-2xl font-bold">{formatCurrency(stats.total_volume || 0)}</p>
              </div>
              <div className="bg-white/10 rounded-lg p-3">
                <p className="text-purple-200 text-sm">Total Sales</p>
                <p className="text-2xl font-bold">{stats.total_sales || 0}</p>
              </div>
              <div className="bg-white/10 rounded-lg p-3">
                <p className="text-purple-200 text-sm">Avg Sale Price</p>
                <p className="text-2xl font-bold">{formatCurrency(stats.average_sale_price || 0)}</p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex space-x-8">
            {[
              { id: 'browse', label: 'Browse', icon: '🔍' },
              { id: 'my-listings', label: 'My Listings', icon: '📋' },
              { id: 'my-bids', label: 'My Bids', icon: '🎯' },
              { id: 'watchlist', label: 'Watchlist', icon: '♥' },
              { id: 'transactions', label: 'Transactions', icon: '💰' },
            ].map((tab) => (
              <button
                key={tab.id}
                data-testid={`tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div className="space-y-6">
            {/* Search and Filters */}
            <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <input
                    data-testid="search-input"
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search listings..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
                <select
                  value={filters.listing_type}
                  onChange={(e) => setFilters({ ...filters, listing_type: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="">All Types</option>
                  <option value="fixed_price">Fixed Price</option>
                  <option value="auction">Auction</option>
                  <option value="reserve_auction">Reserve Auction</option>
                </select>
                <select
                  value={filters.sort_by}
                  onChange={(e) => setFilters({ ...filters, sort_by: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="created_at">Newest</option>
                  <option value="asking_price">Price: Low to High</option>
                  <option value="view_count">Most Viewed</option>
                  <option value="bid_count">Most Bids</option>
                </select>
                <button
                  onClick={fetchListings}
                  className="px-6 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Search
                </button>
              </div>
            </div>
            
            {/* Listings Grid */}
            {listings.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {listings.map((listing) => (
                  <ListingCard
                    key={listing.id}
                    listing={listing}
                    onView={handleViewListing}
                    onBid={handlePlaceBid}
                    onWatch={handleAddToWatchlist}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-xl">
                <p className="text-gray-500 text-lg">No listings found</p>
                <p className="text-gray-400 mt-2">Be the first to list your royalty rights!</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Create Listing
                </button>
              </div>
            )}
          </div>
        )}
        
        {/* My Listings Tab */}
        {activeTab === 'my-listings' && (
          <div className="space-y-6">
            {userStats && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <StatsCard icon="📋" label="Total Listings" value={userStats.listings?.total || 0} />
                <StatsCard icon="✅" label="Active" value={userStats.listings?.active || 0} />
                <StatsCard icon="💰" label="Total Earned" value={formatCurrency(userStats.sales?.total_earned || 0)} />
              </div>
            )}
            
            {myListings.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {myListings.map((listing) => (
                  <ListingCard
                    key={listing.id}
                    listing={listing}
                    onView={handleViewListing}
                    onBid={() => {}}
                    onWatch={() => {}}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-xl">
                <p className="text-gray-500 text-lg">You haven't created any listings yet</p>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Create Your First Listing
                </button>
              </div>
            )}
          </div>
        )}
        
        {/* My Bids Tab */}
        {activeTab === 'my-bids' && (
          <div className="space-y-4">
            {myBids.length > 0 ? (
              <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Listing</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Your Bid</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Status</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {myBids.map((bid) => (
                      <tr key={bid.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <span className="font-medium text-gray-900">{bid.listing_info?.title || 'Unknown'}</span>
                        </td>
                        <td className="px-4 py-3 font-semibold text-purple-600">
                          {formatCurrency(bid.amount)}
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={bid.status} />
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-500">
                          {formatDate(bid.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-xl">
                <p className="text-gray-500 text-lg">You haven't placed any bids yet</p>
                <button
                  onClick={() => setActiveTab('browse')}
                  className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Browse Listings
                </button>
              </div>
            )}
          </div>
        )}
        
        {/* Watchlist Tab */}
        {activeTab === 'watchlist' && (
          <div className="space-y-4">
            {watchlist.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {watchlist.map((item) => item.listing && (
                  <ListingCard
                    key={item.id}
                    listing={item.listing}
                    onView={handleViewListing}
                    onBid={handlePlaceBid}
                    onWatch={handleAddToWatchlist}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-xl">
                <p className="text-gray-500 text-lg">Your watchlist is empty</p>
                <p className="text-gray-400 mt-2">Save listings you're interested in</p>
                <button
                  onClick={() => setActiveTab('browse')}
                  className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Browse Listings
                </button>
              </div>
            )}
          </div>
        )}
        
        {/* Transactions Tab */}
        {activeTab === 'transactions' && (
          <TransactionsTab />
        )}
      </div>
      
      {/* Modals */}
      <CreateListingModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateListing}
      />
      
      <BidModal
        isOpen={showBidModal}
        onClose={() => {
          setShowBidModal(false);
          setSelectedListing(null);
        }}
        listing={selectedListing}
        onSubmit={handleSubmitBid}
      />
    </div>
  );
};

// Transactions Tab Component
const TransactionsTab = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const result = await apiCall(`/marketplace/my-transactions?role=${filter}`);
        setTransactions(result.transactions || []);
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, [filter]);

  if (loading) {
    return <div className="text-center py-8">Loading transactions...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {['all', 'buyer', 'seller'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === f
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {transactions.length > 0 ? (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Transaction ID</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Amount</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {transactions.map((tx) => (
                <tr key={tx.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-sm">{tx.id.slice(0, 8)}...</td>
                  <td className="px-4 py-3 font-semibold text-green-600">
                    {formatCurrency(tx.sale_price)}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={tx.status} />
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {formatDate(tx.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-xl">
          <p className="text-gray-500 text-lg">No transactions found</p>
        </div>
      )}
    </div>
  );
};

// Listing Detail Page
export const ListingDetailPage = () => {
  const { listingId } = useParams();
  const navigate = useNavigate();
  const [listing, setListing] = useState(null);
  const [bids, setBids] = useState([]);
  const [priceHistory, setPriceHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showBidModal, setShowBidModal] = useState(false);

  useEffect(() => {
    const fetchListing = async () => {
      try {
        const result = await apiCall(`/marketplace/listings/${listingId}`);
        setListing(result.listing);
        setBids(result.recent_bids || []);
        setPriceHistory(result.price_history || []);
      } catch (error) {
        toast.error('Failed to load listing');
        navigate('/marketplace');
      } finally {
        setLoading(false);
      }
    };
    fetchListing();
  }, [listingId, navigate]);

  const handleBid = async (bidData) => {
    const isAuction = ['auction', 'reserve_auction', 'dutch_auction'].includes(listing.listing_type);
    
    if (isAuction) {
      await apiCall(`/marketplace/listings/${listingId}/bids`, {
        method: 'POST',
        body: JSON.stringify(bidData),
      });
      toast.success('Bid placed successfully!');
    } else {
      await apiCall(`/marketplace/listings/${listingId}/buy-now`, { method: 'POST' });
      toast.success('Purchase initiated!');
    }
    
    // Refresh listing data
    const result = await apiCall(`/marketplace/listings/${listingId}`);
    setListing(result.listing);
    setBids(result.recent_bids || []);
    setShowBidModal(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-gray-600">Listing not found</p>
          <button
            onClick={() => navigate('/marketplace')}
            className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg"
          >
            Back to Marketplace
          </button>
        </div>
      </div>
    );
  }

  const isAuction = ['auction', 'reserve_auction', 'dutch_auction'].includes(listing.listing_type);

  return (
    <div data-testid="listing-detail" className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Back Button */}
        <button
          onClick={() => navigate('/marketplace')}
          className="mb-6 text-purple-600 hover:text-purple-700 font-medium flex items-center gap-2"
        >
          ← Back to Marketplace
        </button>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Header */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{listing.title}</h1>
                  <div className="flex items-center gap-2 mt-2">
                    <StatusBadge status={listing.status} />
                    <span className="text-sm text-gray-500">
                      Listed {formatDate(listing.created_at)}
                    </span>
                  </div>
                </div>
                {listing.featured && (
                  <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm font-medium rounded-full">
                    ⭐ Featured
                  </span>
                )}
              </div>
              
              <p className="text-gray-600 mt-4">{listing.description}</p>
              
              {/* Tags */}
              {listing.tags && listing.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {listing.tags.map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
            
            {/* Royalty Details */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Royalty Details</h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Royalty Type</p>
                  <p className="font-semibold text-gray-900 capitalize">{listing.royalty_type?.replace('_', ' ')}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Royalty Share</p>
                  <p className="font-semibold text-purple-600 text-xl">{listing.royalty_percentage}%</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Historical Revenue (12mo)</p>
                  <p className="font-semibold text-gray-900">{formatCurrency(listing.historical_revenue || 0)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Projected Annual</p>
                  <p className="font-semibold text-gray-900">{formatCurrency(listing.projected_revenue || 0)}</p>
                </div>
                {listing.duration_months && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-500">Duration</p>
                    <p className="font-semibold text-gray-900">{listing.duration_months} months</p>
                  </div>
                )}
                {listing.artist_name && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-500">Artist</p>
                    <p className="font-semibold text-gray-900">{listing.artist_name}</p>
                  </div>
                )}
              </div>
            </div>
            
            {/* Bid History */}
            {isAuction && bids.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Bid History</h2>
                <div className="space-y-2">
                  {bids.map((bid, index) => (
                    <div key={bid.id} className={`flex justify-between items-center p-3 rounded-lg ${index === 0 ? 'bg-green-50' : 'bg-gray-50'}`}>
                      <div>
                        <span className="font-medium">{formatCurrency(bid.amount)}</span>
                        {index === 0 && <span className="ml-2 text-xs text-green-600 font-medium">LEADING</span>}
                      </div>
                      <span className="text-sm text-gray-500">{formatDate(bid.created_at)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Sidebar - Pricing & Actions */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-6 shadow-sm sticky top-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                {isAuction ? 'Auction Details' : 'Purchase'}
              </h2>
              
              {isAuction ? (
                <div className="space-y-4">
                  <div className="bg-purple-50 p-4 rounded-lg text-center">
                    <p className="text-sm text-purple-600">Current Bid</p>
                    <p className="text-3xl font-bold text-purple-700">
                      {formatCurrency(listing.current_bid || listing.asking_price)}
                    </p>
                    <p className="text-sm text-purple-500 mt-1">{listing.bid_count || 0} bids</p>
                  </div>
                  
                  {listing.auction_end && (
                    <div className="text-center">
                      <p className="text-sm text-gray-500">Auction Ends</p>
                      <p className="font-semibold text-orange-600">{getTimeRemaining(listing.auction_end)}</p>
                    </div>
                  )}
                  
                  {listing.buy_now_price && (
                    <div className="bg-yellow-50 p-4 rounded-lg text-center">
                      <p className="text-sm text-yellow-700">Buy Now Price</p>
                      <p className="text-2xl font-bold text-yellow-700">{formatCurrency(listing.buy_now_price)}</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <p className="text-sm text-green-600">Price</p>
                  <p className="text-3xl font-bold text-green-700">{formatCurrency(listing.asking_price)}</p>
                </div>
              )}
              
              {listing.status === 'active' && (
                <button
                  data-testid="listing-action-btn"
                  onClick={() => setShowBidModal(true)}
                  className="w-full mt-6 px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
                >
                  {isAuction ? 'Place Bid' : 'Buy Now'}
                </button>
              )}
              
              {/* View Stats */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Views</span>
                  <span className="font-medium">{listing.view_count || 0}</span>
                </div>
                <div className="flex justify-between text-sm mt-2">
                  <span className="text-gray-500">Watching</span>
                  <span className="font-medium">{listing.watchlist_count || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <BidModal
        isOpen={showBidModal}
        onClose={() => setShowBidModal(false)}
        listing={listing}
        onSubmit={handleBid}
      />
    </div>
  );
};

export default RoyaltyMarketplaceDashboard;
