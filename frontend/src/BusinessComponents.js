import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Business Identifiers Overview Component
export const BusinessIdentifiers = () => {
  const [businessInfo, setBusinessInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBusinessInfo();
  }, []);

  const fetchBusinessInfo = async () => {
    try {
      const response = await axios.get(`${API}/business/identifiers`);
      setBusinessInfo(response.data);
    } catch (error) {
      setError('Failed to load business information');
      console.error('Error fetching business info:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Business Legal Information */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Business Legal Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Legal Business Name</label>
            <p className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
              {businessInfo?.business_legal_name}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Employer Identification Number (EIN)</label>
            <p className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
              {businessInfo?.business_ein}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Taxpayer Identification Number (TIN)</label>
            <p className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
              {businessInfo?.business_tin}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">NAICS Code</label>
            <p className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
              {businessInfo?.business_naics_code} - {businessInfo?.naics_description}
            </p>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Business Contact Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Business Address</label>
            <p className="mt-1 text-sm text-gray-900 bg-gray-50 p-2 rounded">
              {businessInfo?.business_address}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Business Phone</label>
            <p className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
              {businessInfo?.business_phone}
            </p>
          </div>
        </div>
      </div>

      {/* Global Product Identification */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Global Product Identification Numbers
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">U.P.C. Company Prefix</label>
            <p className="mt-1 text-lg text-purple-600 font-mono bg-purple-50 p-3 rounded border-2 border-purple-200">
              {businessInfo?.upc_company_prefix}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Used for generating UPC barcodes for physical products
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Global Location Number (GLN)</label>
            <p className="mt-1 text-lg text-purple-600 font-mono bg-purple-50 p-3 rounded border-2 border-purple-200">
              {businessInfo?.global_location_number}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Legal entity identification for global commerce
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">ISRC Prefix</label>
            <p className="mt-1 text-lg text-purple-600 font-mono bg-purple-50 p-3 rounded border-2 border-purple-200">
              US-{businessInfo?.isrc_prefix}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              International Standard Recording Code prefix for sound recordings
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Publisher Number</label>
            <p className="mt-1 text-lg text-purple-600 font-mono bg-purple-50 p-3 rounded border-2 border-purple-200">
              {businessInfo?.publisher_number}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Music publishing rights identification number
            </p>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <strong>Your UPC Range:</strong> {businessInfo?.upc_company_prefix}00000 - {businessInfo?.upc_company_prefix}99999 (100,000 unique product codes)
                <br />
                <strong>Your ISRC Format:</strong> US-{businessInfo?.isrc_prefix}-YY-NNNNN (unlimited sound recording codes)
                <br />
                <strong>Your Publisher Number:</strong> {businessInfo?.publisher_number} (music publishing rights identifier)
                <br />
                These identifiers enable complete global distribution, tracking, and rights management of your media products.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Music Publishing & Rights Management */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Music Publishing & Rights Management
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Publisher Number</label>
            <p className="mt-1 text-lg text-green-600 font-mono bg-green-50 p-3 rounded border-2 border-green-200">
              {businessInfo?.publisher_number}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Unique identifier for music publishing rights management
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Publishing Entity</label>
            <p className="mt-1 text-sm text-gray-900 bg-gray-50 p-3 rounded">
              {businessInfo?.business_legal_name}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Legal entity responsible for publishing rights
            </p>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-green-700">
                <strong>Publisher Rights Capabilities:</strong>
                <br />
                • Mechanical royalty collection
                <br />
                • Performance royalty management
                <br />
                • Synchronization licensing
                <br />
                • International rights administration
                <br />
                • Digital streaming royalties
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ISRC Code Generator Component
export const ISRCGenerator = () => {
  const [year, setYear] = useState(new Date().getFullYear().toString().slice(-2));
  const [designationCode, setDesignationCode] = useState('');
  const [generatedISRC, setGeneratedISRC] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateISRC = async () => {
    if (!year || year.length !== 2 || !/^\d+$/.test(year)) {
      setError('Year must be exactly 2 digits (e.g., 25 for 2025)');
      return;
    }

    if (!designationCode || designationCode.length !== 5 || !/^\d+$/.test(designationCode)) {
      setError('Designation code must be exactly 5 digits');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API}/business/isrc/generate/${year}/${designationCode}`);
      setGeneratedISRC(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to generate ISRC code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        ISRC Code Generator
      </h3>
      
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Year of Reference (2 digits)
            </label>
            <input
              type="text"
              value={year}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, '').slice(0, 2);
                setYear(value);
                setGeneratedISRC(null);
                setError('');
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="25"
              maxLength="2"
            />
            <p className="text-xs text-gray-500 mt-1">
              Current year: {new Date().getFullYear().toString().slice(-2)}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Designation Code (5 digits)
            </label>
            <input
              type="text"
              value={designationCode}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, '').slice(0, 5);
                setDesignationCode(value);
                setGeneratedISRC(null);
                setError('');
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="00001"
              maxLength="5"
            />
            <p className="text-xs text-gray-500 mt-1">
              Unique recording number (e.g., 00001, 12345)
            </p>
          </div>
        </div>

        <button
          onClick={generateISRC}
          disabled={loading || year.length !== 2 || designationCode.length !== 5}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate ISRC Code'}
        </button>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {generatedISRC && (
          <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
            <h4 className="text-md font-medium text-green-800 mb-4">Generated ISRC Code</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Country Code</label>
                <p className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded border">
                  {generatedISRC.country_code}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Registrant Code</label>
                <p className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded border">
                  {generatedISRC.registrant_code}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Year of Reference</label>
                <p className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded border">
                  {generatedISRC.year_of_reference}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Designation Code</label>
                <p className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded border">
                  {generatedISRC.designation_code}
                </p>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700">Complete ISRC Code</label>
              <p className="mt-1 text-2xl text-green-600 font-mono bg-white p-4 rounded border-2 border-green-300 text-center">
                {generatedISRC.full_isrc_code}
              </p>
              <p className="text-xs text-gray-600 text-center mt-2">
                Compact Format: {generatedISRC.compact_format}
              </p>
            </div>

            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm text-blue-700">
                <strong>Ready for use:</strong> This ISRC code uniquely identifies your sound recording 
                globally and can be used for digital distribution, royalty collection, and music tracking.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// UPC Code Generator Component
export const UPCGenerator = () => {
  const [productCode, setProductCode] = useState('');
  const [generatedUPC, setGeneratedUPC] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateUPC = async () => {
    if (!productCode || productCode.length !== 5 || !/^\d+$/.test(productCode)) {
      setError('Product code must be exactly 5 digits');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API}/business/upc/generate/${productCode}`);
      setGeneratedUPC(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to generate UPC code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        UPC Code Generator
      </h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product Code (5 digits)
          </label>
          <div className="flex space-x-3">
            <input
              type="text"
              value={productCode}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, '').slice(0, 5);
                setProductCode(value);
                setGeneratedUPC(null);
                setError('');
              }}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="00001"
              maxLength="5"
            />
            <button
              onClick={generateUPC}
              disabled={loading || productCode.length !== 5}
              className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate UPC'}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Enter a unique 5-digit product code (e.g., 00001, 12345)
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {generatedUPC && (
          <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
            <h4 className="text-md font-medium text-green-800 mb-4">Generated UPC Code</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Company Prefix</label>
                <p className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded border">
                  {generatedUPC.upc_company_prefix}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Code</label>
                <p className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded border">
                  {generatedUPC.product_code}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Check Digit</label>
                <p className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded border">
                  {generatedUPC.check_digit}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Barcode Format</label>
                <p className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded border">
                  {generatedUPC.barcode_format}
                </p>
              </div>
            </div>
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700">Complete UPC Code</label>
              <p className="mt-1 text-2xl text-green-600 font-mono bg-white p-4 rounded border-2 border-green-300 text-center">
                {generatedUPC.full_upc_code}
              </p>
              <p className="text-xs text-gray-600 text-center mt-2">
                GTIN-12: {generatedUPC.gtin}
              </p>
            </div>

            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm text-blue-700">
                <strong>Ready for use:</strong> This UPC code can now be used for product labeling, 
                inventory management, and retail distribution.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Product Management Component
export const ProductManagement = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);

  const [newProduct, setNewProduct] = useState({
    product_name: '',
    upc_full_code: '',
    gtin: '',
    isrc_code: '',
    product_category: 'Album',
    artist_name: '',
    album_title: '',
    track_title: '',
    release_date: '',
    duration_seconds: '',
    record_label: 'Big Mann Entertainment LLC',
    publisher_name: 'Big Mann Entertainment LLC',
    publisher_number: 'PA04UV',
    songwriter_credits: '',
    publishing_rights: 'All rights reserved'
  });

  useEffect(() => {
    fetchProducts();
  }, [page, search, category]);

  const fetchProducts = async () => {
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('limit', '10');
      if (search) params.append('search', search);
      if (category) params.append('category', category);

      const response = await axios.get(`${API}/business/products?${params}`);
      setProducts(response.data.products);
      setPagination(response.data.pagination);
    } catch (error) {
      setError('Failed to load products');
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const createProduct = async () => {
    try {
      const productData = {
        ...newProduct,
        release_date: newProduct.release_date ? new Date(newProduct.release_date).toISOString() : null
      };

      await axios.post(`${API}/business/products`, productData);
      
      setShowCreateForm(false);
      setNewProduct({
        product_name: '',
        upc_full_code: '',
        gtin: '',
        isrc_code: '',
        product_category: 'Album',
        artist_name: '',
        album_title: '',
        track_title: '',
        release_date: '',
        duration_seconds: '',
        record_label: 'Big Mann Entertainment LLC',
        publisher_name: 'Big Mann Entertainment LLC',
        publisher_number: 'PA04UV',
        songwriter_credits: '',
        publishing_rights: 'All rights reserved'
      });
      fetchProducts();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create product');
    }
  };

  const deleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) {
      return;
    }

    try {
      await axios.delete(`${API}/business/products/${productId}`);
      fetchProducts();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to delete product');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Product Management</h3>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors"
        >
          Add Product
        </button>
      </div>

      {/* Search and Filter */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="Search products..."
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">All Categories</option>
          <option value="Album">Album</option>
          <option value="Single">Single</option>
          <option value="EP">EP</option>
          <option value="Compilation">Compilation</option>
          <option value="Merchandise">Merchandise</option>
        </select>
        <button
          onClick={() => {
            setPage(1);
            fetchProducts();
          }}
          className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-md transition-colors"
        >
          Search
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Create Product Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Add New Product</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Product Name</label>
                <input
                  type="text"
                  value={newProduct.product_name}
                  onChange={(e) => setNewProduct({ ...newProduct, product_name: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Category</label>
                <select
                  value={newProduct.product_category}
                  onChange={(e) => setNewProduct({ ...newProduct, product_category: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="Album">Album</option>
                  <option value="Single">Single</option>
                  <option value="EP">EP</option>
                  <option value="Compilation">Compilation</option>
                  <option value="Merchandise">Merchandise</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">UPC Code</label>
                <input
                  type="text"
                  value={newProduct.upc_full_code}
                  onChange={(e) => setNewProduct({ ...newProduct, upc_full_code: e.target.value, gtin: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="860004340200"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">ISRC Code (for audio recordings)</label>
                <input
                  type="text"
                  value={newProduct.isrc_code}
                  onChange={(e) => setNewProduct({ ...newProduct, isrc_code: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="US-QZ9H8-25-00001"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Artist Name</label>
                <input
                  type="text"
                  value={newProduct.artist_name}
                  onChange={(e) => setNewProduct({ ...newProduct, artist_name: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Album Title</label>
                <input
                  type="text"
                  value={newProduct.album_title}
                  onChange={(e) => setNewProduct({ ...newProduct, album_title: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Track Title (if applicable)</label>
                <input
                  type="text"
                  value={newProduct.track_title}
                  onChange={(e) => setNewProduct({ ...newProduct, track_title: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Duration (seconds)</label>
                <input
                  type="number"
                  value={newProduct.duration_seconds}
                  onChange={(e) => setNewProduct({ ...newProduct, duration_seconds: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="240"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Record Label</label>
                <input
                  type="text"
                  value={newProduct.record_label}
                  onChange={(e) => setNewProduct({ ...newProduct, record_label: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700">Release Date</label>
                <input
                  type="date"
                  value={newProduct.release_date}
                  onChange={(e) => setNewProduct({ ...newProduct, release_date: e.target.value })}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCreateForm(false)}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createProduct}
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors"
              >
                Create Product
              </button>
            </div>
          </div>
        </div>            
      )}

      {/* Products List */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No products found</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  UPC Code
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {products.map((product) => (
                <tr key={product.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{product.product_name}</div>
                      {product.artist_name && (
                        <div className="text-sm text-gray-500">by {product.artist_name}</div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-mono text-gray-900">{product.upc_full_code}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                      {product.product_category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(product.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => deleteProduct(product.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          {pagination && pagination.pages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
              <div className="flex-1 flex justify-between">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page <= 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="relative inline-flex items-center px-4 py-2 text-sm text-gray-700">
                  Page {page} of {pagination.pages}
                </span>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page >= pagination.pages}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};