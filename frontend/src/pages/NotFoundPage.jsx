import React from "react";
import { Link } from "react-router-dom";

const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <img 
            src="/logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-24 h-24 object-contain mx-auto mb-6"
            onError={(e) => {
              e.target.style.display = 'none';
              const fallback = document.createElement('div');
              fallback.className = 'w-24 h-24 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-6';
              fallback.innerHTML = '<span class="text-white font-bold text-xl">BME</span>';
              e.target.parentNode.appendChild(fallback);
            }}
          />
        </div>
        <h1 className="text-6xl font-bold text-purple-600 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Page Not Found</h2>
        <p className="text-gray-600 mb-8">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <div className="space-y-4">
          <Link 
            to="/" 
            className="block bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition-colors"
          >
            Return Home
          </Link>
          <Link 
            to="/platforms" 
            className="block border-2 border-purple-600 text-purple-600 hover:bg-purple-600 hover:text-white font-bold py-3 px-6 rounded-md transition-colors"
          >
            View Platforms
          </Link>
        </div>
        
        <div className="mt-8 text-sm text-gray-500">
          <p>If you believe this is an error, please contact our support team.</p>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
