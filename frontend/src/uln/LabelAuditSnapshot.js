import React, { useState } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

export const LabelAuditSnapshot = ({ activeLabel }) => {
  const [downloading, setDownloading] = useState(false);
  const [lastDownload, setLastDownload] = useState(null);
  const token = localStorage.getItem('token');

  const handleDownload = async () => {
    if (!activeLabel) return;
    setDownloading(true);
    try {
      const res = await fetch(`${API}/api/uln/labels/${activeLabel.label_id}/audit-snapshot`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `label_${activeLabel.label_id}_audit_snapshot.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        setLastDownload(new Date().toLocaleString());
      }
    } catch (e) { console.error(e); }
    setDownloading(false);
  };

  if (!activeLabel) {
    return (
      <div className="bg-white rounded-xl shadow p-8 text-center" data-testid="audit-no-label">
        <p className="text-gray-500">Select a label from the switcher above to export an audit snapshot.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="label-audit-snapshot-panel">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Audit Snapshot</h2>
        <p className="text-sm text-gray-500 mt-1">
          Export a comprehensive JSON snapshot of <span className="font-medium text-purple-700">{activeLabel.name}</span> for compliance and record-keeping.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">Full Label Snapshot (v2.0)</h3>
            <p className="text-sm text-gray-500 mt-1">
              Includes label metadata, members, catalog assets, rights data, distribution endpoints, and audit trail.
            </p>
          </div>
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-2 bg-purple-600 text-white px-5 py-2.5 rounded-lg font-medium text-sm hover:bg-purple-700 transition disabled:opacity-50 shrink-0"
            data-testid="audit-download-btn"
          >
            {downloading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Generating...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                Download Snapshot
              </>
            )}
          </button>
        </div>
        {lastDownload && (
          <p className="text-xs text-gray-400 mt-3" data-testid="audit-last-download">Last downloaded: {lastDownload}</p>
        )}
      </div>

      <div className="bg-gray-50 rounded-xl p-5 border border-gray-200">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">What's included in the snapshot?</h4>
        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600">
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Label metadata & configuration</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> All team members & roles</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Catalog assets (titles, ISRCs, UPCs)</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Rights splits, territories & AI consent</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Distribution endpoint statuses</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Distribution health summary</li>
          <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Recent audit trail (up to 100 entries)</li>
        </ul>
      </div>
    </div>
  );
};
