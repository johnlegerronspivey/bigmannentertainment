import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const HomePage = () => {
  const { user } = useAuth();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-16 sm:py-24">
          <div className="text-center">
            <div className="mb-8">
              <img 
                src="/big-mann-logo.png" 
                alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
                className="w-32 h-32 object-contain mx-auto mb-6 shadow-2xl rounded-lg"
              />
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Big Mann Entertainment
            </h1>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
              Complete Media Distribution Empire
            </p>
            <p className="text-lg mb-8 max-w-4xl mx-auto">
              Distribute your content across 117+ platforms worldwide including music streaming, social media, video platforms, podcast networks, and premier model agencies
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {!user ? (
                <>
                  <Link 
                    to="/register" 
                    className="bg-white text-purple-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                  >
                    Start Creating
                  </Link>
                  <Link 
                    to="/platforms" 
                    className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-700 transition-colors"
                  >
                    View Platforms
                  </Link>
                </>
              ) : (
                <>
                  <Link 
                    to="/upload" 
                    className="bg-white text-purple-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                  >
                    Upload Content
                  </Link>
                  <Link 
                    to="/distribute" 
                    className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-700 transition-colors"
                  >
                    Start Distribution
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Media Distribution
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From content creation to global distribution, we provide the complete ecosystem for entertainment professionals
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Multi-Format Upload</h3>
              <p className="text-gray-600">Upload audio, video, and images with support for all major formats and high-quality processing.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">117+ Platforms</h3>
              <p className="text-gray-600">Distribute to social media, streaming services, radio stations, TV networks, and emerging Web3 platforms.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Revenue Management</h3>
              <p className="text-gray-600">Track earnings, manage royalty splits, and optimize your revenue streams across all platforms.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Industry Compliance</h3>
              <p className="text-gray-600">DDEX metadata standards, business identifiers, tax management, and full regulatory compliance.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Blockchain & NFTs</h3>
              <p className="text-gray-600">Mint NFTs, deploy smart contracts, and leverage Web3 technologies for next-generation distribution.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Professional Tools</h3>
              <p className="text-gray-600">Advanced analytics, content management, sponsorship opportunities, and label services.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-purple-50 py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl md:text-4xl font-bold text-purple-700 mb-2">117+</div>
              <div className="text-gray-600">Distribution Platforms</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-purple-700 mb-2">24/7</div>
              <div className="text-gray-600">Global Support</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-purple-700 mb-2">100%</div>
              <div className="text-gray-600">Rights Ownership</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-purple-700 mb-2">∞</div>
              <div className="text-gray-600">Upload Capacity</div>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Showcase */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Distribute Everywhere
            </h2>
            <p className="text-xl text-gray-600">
              Reach your audience across all major platforms and emerging networks
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {['Instagram', 'Twitter', 'Facebook', 'TikTok', 'YouTube', 'Spotify', 'Apple Music', 'Netflix', 'CNN', 'MTV', 'OpenSea', 'Billboard'].map((platform) => (
              <div key={platform} className="bg-white p-4 rounded-lg shadow text-center">
                <div className="font-semibold text-gray-800">{platform}</div>
              </div>
            ))}
          </div>

          <div className="text-center mt-8">
            <Link 
              to="/platforms" 
              className="text-purple-600 hover:text-purple-700 font-semibold"
            >
              View all 117+ platforms →
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-purple-600 to-indigo-700 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Distribute Your Content?
          </h2>
          <p className="text-xl mb-8">
            Join thousands of creators who trust Big Mann Entertainment for their media distribution needs
          </p>
          {!user ? (
            <Link 
              to="/register" 
              className="bg-white text-purple-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block"
            >
              Get Started Today
            </Link>
          ) : (
            <Link 
              to="/upload" 
              className="bg-white text-purple-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block"
            >
              Upload Your First Content
            </Link>
          )}
        </div>
      </section>
    </div>
  );
};

export default HomePage;
