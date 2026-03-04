import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [resetData, setResetData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { forgotPassword } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    setResetData(null);

    const result = await forgotPassword(email);
    
    if (result.success) {
      setMessage(result.message);
      if (result.data && result.data.reset_url) {
        setResetData(result.data);
      }
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleCopyResetUrl = () => {
    if (resetData && resetData.reset_url) {
      navigator.clipboard.writeText(resetData.reset_url);
      alert('Reset URL copied to clipboard!');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <img 
            src="/big-mann-logo.png" 
            alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
            className="w-20 h-20 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Reset your password
          </h2>
          <p className="text-gray-600">Enter your email to receive a reset link</p>
        </div>

        <div className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {message && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {message}
            </div>
          )}

          {/* Development Reset Data Display - Only show if email service failed */}
          {resetData && resetData.reset_token && (
            <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded space-y-3">
              <div className="font-semibold">Email Service Unavailable - Development Fallback</div>
              <div className="text-sm">
                <p className="mb-2">{resetData.instructions}</p>
                <div className="bg-blue-50 p-3 rounded border break-all">
                  <div className="font-mono text-xs">{resetData.reset_url}</div>
                </div>
                <div className="flex space-x-2 mt-3">
                  <button
                    onClick={handleCopyResetUrl}
                    className="bg-blue-600 text-white px-3 py-1 text-sm rounded hover:bg-blue-700"
                  >
                    Copy URL
                  </button>
                  <a
                    href={resetData.reset_url}
                    className="bg-green-600 text-white px-3 py-1 text-sm rounded hover:bg-green-700 inline-block"
                  >
                    Go to Reset Page
                  </a>
                </div>
                <p className="text-xs mt-2">Expires in {resetData.expires_in_hours} hours</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter your email"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>

          <div className="text-center">
            <Link to="/login" className="text-purple-600 hover:text-purple-500">
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
