import React, { useState } from "react";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AdminNotificationsPage = () => {
  const [singleNotification, setSingleNotification] = useState({
    email: '',
    subject: '',
    message: '',
    user_name: ''
  });
  const [bulkNotification, setBulkNotification] = useState({
    subject: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSingleNotification = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      await axios.post(`${API}/admin/send-notification`, singleNotification);
      setMessage('Notification sent successfully!');
      setSingleNotification({ email: '', subject: '', message: '', user_name: '' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send notification');
    }

    setLoading(false);
  };

  const handleBulkNotification = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('subject', bulkNotification.subject);
      formData.append('message', bulkNotification.message);

      const response = await axios.post(`${API}/admin/send-bulk-notification`, formData);
      setMessage(`Bulk notification completed! ${response.data.successful} successful, ${response.data.failed} failed out of ${response.data.total_users} users.`);
      setBulkNotification({ subject: '', message: '' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send bulk notification');
    }

    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Notifications</h1>
        <p className="text-gray-600">Send email notifications to users from no-reply@bigmannentertainment.com</p>
      </div>

      {message && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
          {message}
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-8">
        {/* Single Notification */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Send Single Notification</h2>
          <form onSubmit={handleSingleNotification} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">User Email</label>
              <input
                type="email"
                required
                value={singleNotification.email}
                onChange={(e) => setSingleNotification({ ...singleNotification, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="user@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">User Name (Optional)</label>
              <input
                type="text"
                value={singleNotification.user_name}
                onChange={(e) => setSingleNotification({ ...singleNotification, user_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <input
                type="text"
                required
                value={singleNotification.subject}
                onChange={(e) => setSingleNotification({ ...singleNotification, subject: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Important Update"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                required
                rows="4"
                value={singleNotification.message}
                onChange={(e) => setSingleNotification({ ...singleNotification, message: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Your notification message..."
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Notification'}
            </button>
          </form>
        </div>

        {/* Bulk Notification */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Send Bulk Notification</h2>
          <p className="text-sm text-gray-600 mb-4">Send notification to all active users</p>
          <form onSubmit={handleBulkNotification} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <input
                type="text"
                required
                value={bulkNotification.subject}
                onChange={(e) => setBulkNotification({ ...bulkNotification, subject: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Platform Update"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                required
                rows="6"
                value={bulkNotification.message}
                onChange={(e) => setBulkNotification({ ...bulkNotification, message: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Your message to all users..."
              />
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    This will send the notification to ALL active users in the system. Use with caution.
                  </p>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Sending to All Users...' : 'Send Bulk Notification'}
            </button>
          </form>
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-md p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Email Configuration</h3>
        <p className="text-blue-700 mb-2">
          All notifications are sent from: <strong>no-reply@bigmannentertainment.com</strong>
        </p>
        <p className="text-blue-700 text-sm">
          Emails include professional Big Mann Entertainment branding (owned by John LeGerron Spivey) and are sent using secure SMTP protocols.
          If email service is unavailable, users will receive fallback notifications through the platform.
        </p>
      </div>
    </div>
  );
};

export default AdminNotificationsPage;
