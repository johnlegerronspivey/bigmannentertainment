import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [resetData, setResetData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { forgotPassword } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResetData(null);

    const result = await forgotPassword(email);
    
    if (result.success) {
      setSubmitted(true);
      if (result.data?.reset_url) {
        setResetData(result.data);
      }
      if (result.data?.email_sent) {
        toast.success("Reset link sent to your email!");
      }
    } else {
      toast.error(result.error || "Something went wrong");
    }
    
    setLoading(false);
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
          <h2 data-testid="forgot-password-title" className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Reset your password
          </h2>
          <p className="text-gray-600">Enter your email to receive a reset link</p>
        </div>

        <div className="mt-8 space-y-6">
          {/* Success state with reset link */}
          {submitted && resetData?.reset_url && (
            <div data-testid="reset-link-box" className="bg-blue-50 border border-blue-300 text-blue-800 px-5 py-4 rounded-lg space-y-3">
              <p className="font-semibold">{resetData.instructions}</p>
              {resetData.email_sent && (
                <p className="text-sm text-blue-600">We also sent a link to your email.</p>
              )}
              <div className="bg-white p-3 rounded border border-blue-200 break-all">
                <p className="font-mono text-xs text-blue-700">{resetData.reset_url}</p>
              </div>
              <div className="flex gap-2 mt-3">
                <a
                  href={resetData.reset_url}
                  data-testid="reset-link-go-btn"
                  className="bg-purple-600 text-white px-4 py-2 text-sm rounded-md hover:bg-purple-700 inline-block font-medium"
                >
                  Reset Password Now
                </a>
                <button
                  data-testid="reset-link-copy-btn"
                  onClick={() => {
                    navigator.clipboard.writeText(resetData.reset_url);
                    toast.success("Reset URL copied!");
                  }}
                  className="bg-gray-200 text-gray-700 px-4 py-2 text-sm rounded-md hover:bg-gray-300 font-medium"
                >
                  Copy Link
                </button>
              </div>
              <p className="text-xs text-blue-500">Expires in {resetData.expires_in_hours} hours</p>
            </div>
          )}

          {/* Generic success (no link data - e.g. email not found) */}
          {submitted && !resetData?.reset_url && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              If the email exists, a reset link has been sent.
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="email"
                required
                data-testid="forgot-password-email-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter your email"
              />
            </div>

            <button
              type="submit"
              data-testid="forgot-password-submit-btn"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Sending...' : submitted ? 'Resend Reset Link' : 'Send Reset Link'}
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
