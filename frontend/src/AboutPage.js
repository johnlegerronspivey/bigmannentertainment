import React from 'react';

const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-6">About Big Mann Entertainment</h1>
            <p className="text-xl max-w-3xl mx-auto">
              Founded by visionary entrepreneur John LeGerron Spivey, Big Mann Entertainment is revolutionizing 
              the music distribution industry with cutting-edge technology and comprehensive platform coverage.
            </p>
          </div>
        </div>
      </div>

      {/* Founder Section */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Meet Our Founder & CEO</h2>
              <h3 className="text-2xl font-semibold text-purple-600 mb-4">John LeGerron Spivey</h3>
              <p className="text-lg text-gray-700 mb-6">
                John LeGerron Spivey is the visionary founder and CEO of Big Mann Entertainment, bringing years of 
                industry expertise and innovative thinking to the music distribution landscape. Under his leadership, 
                the platform has grown to serve artists across 114+ global distribution platforms.
              </p>
              <div className="space-y-4">
                <div className="flex items-center">
                  <span className="text-purple-600 font-semibold mr-3">📍 Location:</span>
                  <span>Alexander City, Alabama</span>
                </div>
                <div className="flex items-center">
                  <span className="text-purple-600 font-semibold mr-3">📧 Contact:</span>
                  <span>owner@bigmannentertainment.com</span>
                </div>
                <div className="flex items-center">
                  <span className="text-purple-600 font-semibold mr-3">📞 Phone:</span>
                  <span>(334) 669-8638</span>
                </div>
              </div>
            </div>
            <div className="text-center">
              <div className="bg-white rounded-full w-64 h-64 mx-auto flex items-center justify-center shadow-lg border-4 border-purple-600">
                <span className="text-8xl">👤</span>
              </div>
              <p className="text-gray-600 mt-4 italic">"Empowering artists with comprehensive distribution solutions"</p>
            </div>
          </div>
        </div>
      </div>

      {/* Company Information */}
      <div className="bg-slate-800 py-20 border-t border-slate-700">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Company Information</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Big Mann Entertainment is a legally registered entertainment company specializing in 
              comprehensive media distribution and rights management.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Business Details */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">📋 Business Details</h3>
              <div className="space-y-2 text-gray-700">
                <p><strong>Legal Name:</strong> Big Mann Entertainment</p>
                <p><strong>Owner:</strong> John LeGerron Spivey</p>
                <p><strong>Business Type:</strong> Sole Proprietorship</p>
                <p><strong>EIN:</strong> 27-0658077</p>
                <p><strong>Established:</strong> 2020</p>
              </div>
            </div>

            {/* Industry Information */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">🎵 Industry Focus</h3>
              <div className="space-y-2 text-gray-700">
                <p><strong>Industry:</strong> Sound Recording Industries</p>
                <p><strong>NAICS Code:</strong> 512200</p>
                <p><strong>Services:</strong> Music Distribution</p>
                <p><strong>Specialty:</strong> Digital Rights Management</p>
                <p><strong>Coverage:</strong> Global Distribution</p>
              </div>
            </div>

            {/* Contact Information */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">📍 Contact Information</h3>
              <div className="space-y-2 text-gray-700">
                <p><strong>Address:</strong></p>
                <p>1314 Lincoln Heights Street</p>
                <p>Alexander City, AL 35010</p>
                <p>United States</p>
                <p><strong>Email:</strong> owner@bigmannentertainment.com</p>
                <p><strong>Phone:</strong> (334) 669-8638</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mission & Vision */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12">
            <div className="text-center">
              <div className="bg-purple-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">🎯</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Our Mission</h3>
              <p className="text-gray-700">
                To empower independent artists and creators with comprehensive distribution solutions, 
                ensuring their music reaches every corner of the digital world while maximizing their 
                revenue potential through innovative technology and industry expertise.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">👁️</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Our Vision</h3>
              <p className="text-gray-700">
                To become the leading platform for music distribution and rights management, 
                setting new industry standards for artist empowerment, technological innovation, 
                and global reach in the entertainment industry.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Achievements & Stats */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-6">Our Achievements</h2>
            <p className="text-xl">Under John LeGerron Spivey's leadership, we've built something extraordinary</p>
          </div>

          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-5xl font-bold mb-2">114+</div>
              <div className="text-lg">Distribution Platforms</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">5+</div>
              <div className="text-lg">Years of Innovation</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">∞</div>
              <div className="text-lg">Artists Empowered</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">🌍</div>
              <div className="text-lg">Global Reach</div>
            </div>
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Technology & Innovation</h2>
            <p className="text-xl text-gray-600">
              Built with cutting-edge technology to ensure the best experience for our artists
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Advanced Distribution</h3>
              <p className="text-gray-700">
                Automated distribution to 114+ platforms with DDEX standards and real-time sync capabilities.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🔗</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Blockchain Integration</h3>
              <p className="text-gray-700">
                DAO governance and smart contracts for transparent rights management and royalty distribution.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Comprehensive Analytics</h3>
              <p className="text-gray-700">
                Real-time analytics, performance tracking, and revenue optimization across all platforms.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">Ready to Join Our Family?</h2>
          <p className="text-xl text-gray-600 mb-8">
            Experience the Big Mann Entertainment difference. Join thousands of artists who trust 
            John LeGerron Spivey's vision and our comprehensive distribution platform.
          </p>
          <div className="space-x-4">
            <button className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-lg">
              Get Started Today
            </button>
            <button className="border border-purple-600 text-purple-600 hover:bg-purple-600 hover:text-white font-bold py-3 px-8 rounded-lg">
              Contact John LeGerron Spivey
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;