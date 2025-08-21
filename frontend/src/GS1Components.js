import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// GS1 Business Information Dashboard
export const GS1BusinessDashboard = () => {
  const [businessInfo, setBusinessInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBusinessInfo();
  }, []);

  const fetchBusinessInfo = async () => {
    try {
      const response = await fetch(`${API}/api/gs1/business-info`);
      
      if (response.ok) {
        const data = await response.json();
        setBusinessInfo(data);
        setError('');
      } else {
        setError('Failed to load business information');
      }
    } catch (error) {
      console.error('Business info fetch error:', error);
      setError('Error loading business information.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-white">Loading GS1 business information...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-400">{error}</div>;
  }

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
      <h3 className="text-xl font-bold text-white mb-4">GS1 Business Information</h3>
      
      {businessInfo && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Business Entity:</span>
              <span className="text-white font-semibold">{businessInfo.business_entity}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Business Owner:</span>
              <span className="text-white font-semibold">{businessInfo.business_owner}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Industry:</span>
              <span className="text-white font-semibold">{businessInfo.industry}</span>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-purple-200">EIN:</span>
              <span className="text-white font-semibold">{businessInfo.ein}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">TIN:</span>
              <span className="text-white font-semibold">{businessInfo.tin}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-purple-200">Business Type:</span>
              <span className="text-white font-semibold">{businessInfo.business_type}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// UPC/GTIN Product Management
export const UPCProductManager = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newProduct, setNewProduct] = useState({
    title: '',
    artist_name: '',
    label_name: '',
    release_date: '',
    genre: '',
    duration_seconds: '',
    isrc: '',
    catalog_number: '',
    distribution_format: 'Digital'
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API}/api/gs1/products`);
      
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products || []);
        setError('');
      } else {
        setError('Failed to load products');
      }
    } catch (error) {
      console.error('Products fetch error:', error);
      setError('Error loading products.');
    } finally {
      setLoading(false);
    }
  };

  const createProduct = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/gs1/products`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...newProduct,
          release_date: new Date(newProduct.release_date).toISOString(),
          duration_seconds: newProduct.duration_seconds ? parseInt(newProduct.duration_seconds) : null
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Successfully created product with UPC: ${data.product.upc} and GTIN: ${data.product.gtin}`);
        setShowCreateForm(false);
        setNewProduct({
          title: '',
          artist_name: '',
          label_name: '',
          release_date: '',
          genre: '',
          duration_seconds: '',
          isrc: '',
          catalog_number: '',
          distribution_format: 'Digital'
        });
        fetchProducts(); // Refresh list
        setError('');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create product');
      }
    } catch (error) {
      console.error('Product creation error:', error);
      setError('Error creating product. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-bold text-white">UPC/GTIN Product Management</h3>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-2 px-4 rounded transition duration-300"
        >
          {showCreateForm ? '✕ Cancel' : '➕ Create Product'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Create Product Form */}
      {showCreateForm && (
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
          <h4 className="text-lg font-semibold text-white mb-4">Create New Music Product</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-purple-200 mb-2">Title *</label>
              <input
                type="text"
                value={newProduct.title}
                onChange={(e) => setNewProduct({...newProduct, title: e.target.value})}
                className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
                required
              />
            </div>
            
            <div>
              <label className="block text-purple-200 mb-2">Artist Name *</label>
              <input
                type="text"
                value={newProduct.artist_name}
                onChange={(e) => setNewProduct({...newProduct, artist_name: e.target.value})}
                className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
                required
              />
            </div>
            
            <div>
              <label className="block text-purple-200 mb-2">Label Name *</label>
              <input
                type="text"
                value={newProduct.label_name}
                onChange={(e) => setNewProduct({...newProduct, label_name: e.target.value})}
                className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
                required
              />
            </div>
            
            <div>
              <label className="block text-purple-200 mb-2">Release Date *</label>
              <input
                type="date"
                value={newProduct.release_date}
                onChange={(e) => setNewProduct({...newProduct, release_date: e.target.value})}
                className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
                required
              />
            </div>
            
            <div>
              <label className="block text-purple-200 mb-2">Genre</label>
              <input
                type="text"
                value={newProduct.genre}
                onChange={(e) => setNewProduct({...newProduct, genre: e.target.value})}
                className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
              />
            </div>
            
            <div>
              <label className="block text-purple-200 mb-2">Duration (seconds)</label>
              <input
                type="number"
                value={newProduct.duration_seconds}
                onChange={(e) => setNewProduct({...newProduct, duration_seconds: e.target.value})}
                className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
              />
            </div>
            
            <div>
              <label className="block text-purple-200 mb-2">ISRC</label>
              <input
                type="text"
                value={newProduct.isrc}
                onChange={(e) => setNewProduct({...newProduct, isrc: e.target.value})}
                className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
                placeholder="e.g., USTEST2500001"
              />
            </div>
            
            <div>
              <label className="block text-purple-200 mb-2">Catalog Number</label>
              <input
                type="text"
                value={newProduct.catalog_number}
                onChange={(e) => setNewProduct({...newProduct, catalog_number: e.target.value})}
                className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
              />
            </div>
          </div>
          
          <div className="mt-4 flex gap-4">
            <button
              onClick={createProduct}
              disabled={loading || !newProduct.title || !newProduct.artist_name || !newProduct.label_name || !newProduct.release_date}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300 disabled:opacity-50"
            >
              {loading ? 'Creating...' : '🎵 Create Product'}
            </button>
          </div>
        </div>
      )}

      {/* Products List */}
      <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
        <h4 className="text-lg font-semibold text-white mb-4">Music Products</h4>
        
        {loading && products.length === 0 ? (
          <div className="text-center py-8 text-white">Loading products...</div>
        ) : products.length === 0 ? (
          <div className="text-center py-8 text-purple-200">
            No products created yet. Create your first music product to get started.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-purple-400/30">
                  <th className="text-left text-purple-200 py-2">UPC</th>
                  <th className="text-left text-purple-200 py-2">GTIN</th>
                  <th className="text-left text-purple-200 py-2">Title</th>
                  <th className="text-left text-purple-200 py-2">Artist</th>
                  <th className="text-left text-purple-200 py-2">Label</th>
                  <th className="text-left text-purple-200 py-2">Release Date</th>
                  <th className="text-left text-purple-200 py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product, index) => (
                  <tr key={index} className="border-b border-white/10">
                    <td className="text-green-400 py-2 font-mono">{product.upc}</td>
                    <td className="text-blue-400 py-2 font-mono">{product.gtin}</td>
                    <td className="text-white py-2">{product.title}</td>
                    <td className="text-white py-2">{product.artist_name}</td>
                    <td className="text-white py-2">{product.label_name}</td>
                    <td className="text-white py-2">{new Date(product.release_date).toLocaleDateString()}</td>
                    <td className="py-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        product.gtin_status === 'ACTIVE' ? 'bg-green-500/20 text-green-300' : 'bg-gray-500/20 text-gray-300'
                      }`}>
                        {product.gtin_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

// Barcode Generator Component
export const BarcodeGenerator = () => {
  const [upcCode, setUpcCode] = useState('');
  const [formatType, setFormatType] = useState('PNG');
  const [barcodeData, setBarcodeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateBarcode = async () => {
    if (!upcCode || upcCode.length !== 12) {
      setError('UPC code must be exactly 12 digits');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(`${API}/api/gs1/barcode/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          upc_code: upcCode,
          format_type: formatType
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setBarcodeData(data);
      } else {
        setError('Failed to generate barcode');
      }
    } catch (error) {
      console.error('Barcode generation error:', error);
      setError('Error generating barcode. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const downloadBarcode = () => {
    if (!barcodeData) return;
    
    const link = document.createElement('a');
    link.href = `data:${barcodeData.content_type};base64,${barcodeData.data}`;
    link.download = `barcode_${barcodeData.upc_code}.${formatType.toLowerCase()}`;
    link.click();
  };

  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
      <h3 className="text-xl font-bold text-white mb-4">Barcode Generator</h3>
      
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-purple-200 mb-2">UPC Code (12 digits):</label>
          <input
            type="text"
            value={upcCode}
            onChange={(e) => setUpcCode(e.target.value.replace(/\D/g, '').slice(0, 12))}
            className="w-full bg-white/10 text-white border border-purple-400 rounded px-3 py-2 font-mono"
            placeholder="860004340201"
            maxLength={12}
          />
        </div>
        
        <div>
          <label className="block text-purple-200 mb-2">Format:</label>
          <select
            value={formatType}
            onChange={(e) => setFormatType(e.target.value)}
            className="bg-white/10 text-white border border-purple-400 rounded px-3 py-2"
          >
            <option value="PNG">PNG</option>
            <option value="JPEG">JPEG</option>
            <option value="SVG">SVG</option>
          </select>
        </div>
        
        <button
          onClick={generateBarcode}
          disabled={loading || !upcCode || upcCode.length !== 12}
          className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300 disabled:opacity-50"
        >
          {loading ? 'Generating...' : '📊 Generate Barcode'}
        </button>
      </div>

      {barcodeData && (
        <div className="mt-6 p-4 bg-white/5 rounded-lg">
          <h4 className="text-lg font-semibold text-white mb-3">Generated Barcode</h4>
          
          <div className="text-center mb-4">
            <img
              src={`data:${barcodeData.content_type};base64,${barcodeData.data}`}
              alt={`Barcode for ${barcodeData.upc_code}`}
              className="mx-auto bg-white p-2 rounded"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm mb-4">
            <div>
              <span className="text-purple-200">UPC Code:</span>
              <span className="text-white font-mono ml-2">{barcodeData.upc_code}</span>
            </div>
            <div>
              <span className="text-purple-200">Format:</span>
              <span className="text-white ml-2">{barcodeData.format_type}</span>
            </div>
            <div>
              <span className="text-purple-200">Size:</span>
              <span className="text-white ml-2">{(barcodeData.size_bytes / 1024).toFixed(1)} KB</span>
            </div>
            <div>
              <span className="text-purple-200">Type:</span>
              <span className="text-white ml-2">{barcodeData.content_type}</span>
            </div>
          </div>
          
          <button
            onClick={downloadBarcode}
            className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-2 px-4 rounded transition duration-300"
          >
            📥 Download Barcode
          </button>
        </div>
      )}
    </div>
  );
};

// Main GS1 Dashboard Component
export const GS1Dashboard = () => {
  const [activeTab, setActiveTab] = useState('business');

  const tabs = [
    { id: 'business', label: '🏢 Business Info', component: GS1BusinessDashboard },
    { id: 'products', label: '🎵 Products', component: UPCProductManager },
    { id: 'barcode', label: '📊 Barcode Generator', component: BarcodeGenerator }
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || GS1BusinessDashboard;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">GS1 US Data Hub Integration</h1>
          <p className="text-purple-200">Big Mann Entertainment - UPC/GTIN & GLN Management</p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="flex flex-wrap justify-center gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg font-semibold transition duration-300 ${
                  activeTab === tab.id
                    ? 'bg-white text-purple-900'
                    : 'bg-white/10 text-purple-200 hover:bg-white/20'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div>
          <ActiveComponent />
        </div>
      </div>
    </div>
  );
};

export default GS1Dashboard;