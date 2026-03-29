import React, { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const EXPECTED_HEADERS = ['title', 'type', 'artist', 'isrc', 'upc', 'release_date', 'genre', 'status', 'platforms', 'streams_total'];

const STATUS_BADGE = {
  released: 'bg-emerald-100 text-emerald-800',
  'pre-release': 'bg-amber-100 text-amber-800',
  draft: 'bg-gray-100 text-gray-600',
  taken_down: 'bg-red-100 text-red-800',
};

export default function CatalogImportPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [labelId, setLabelId] = useState('');
  const [labels, setLabels] = useState([]);
  const [labelsLoaded, setLabelsLoaded] = useState(false);

  // Upload state
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [skipDuplicates, setSkipDuplicates] = useState(true);

  // Preview state
  const [preview, setPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Import state
  const [importResult, setImportResult] = useState(null);
  const [importing, setImporting] = useState(false);

  // Step tracking
  const [step, setStep] = useState('upload'); // upload -> preview -> result

  const token = localStorage.getItem('token');
  const headers = { 'Authorization': `Bearer ${token}` };

  // Fetch labels on mount
  React.useEffect(() => {
    fetchLabels();
  }, []);

  const fetchLabels = async () => {
    try {
      const res = await fetch(`${API}/api/uln/me/labels`, {
        headers: { ...headers, 'Content-Type': 'application/json' },
      });
      if (res.ok) {
        const data = await res.json();
        const labelsList = data.labels || [];
        setLabels(labelsList);
        if (labelsList.length > 0) {
          setLabelId(labelsList[0].label_id);
        }
      }
    } catch (e) {
      console.error('Failed to fetch labels:', e);
    }
    setLabelsLoaded(true);
  };

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped && dropped.name.toLowerCase().endsWith('.csv')) {
      setFile(dropped);
      setPreview(null);
      setImportResult(null);
      setStep('upload');
    } else {
      toast.error('Please upload a CSV file');
    }
  }, []);

  const handleFileSelect = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreview(null);
      setImportResult(null);
      setStep('upload');
    }
  };

  const handlePreview = async () => {
    if (!file || !labelId) {
      toast.error('Please select a label and upload a CSV file');
      return;
    }
    setPreviewLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API}/api/uln/labels/${labelId}/catalog/preview-csv`, {
        method: 'POST',
        headers,
        body: formData,
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setPreview(data);
        setStep('preview');
      } else {
        toast.error(data.detail || data.error || 'Failed to preview CSV');
      }
    } catch (e) {
      toast.error('Network error during preview');
    }
    setPreviewLoading(false);
  };

  const handleImport = async () => {
    if (!file || !labelId) return;
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('skip_duplicates', skipDuplicates.toString());
      const res = await fetch(`${API}/api/uln/labels/${labelId}/catalog/import-csv`, {
        method: 'POST',
        headers,
        body: formData,
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setImportResult(data);
        setStep('result');
        toast.success(`Imported ${data.imported_count} assets successfully!`);
      } else {
        toast.error(data.detail || data.error || 'Import failed');
      }
    } catch (e) {
      toast.error('Network error during import');
    }
    setImporting(false);
  };

  const handleDownloadTemplate = async () => {
    if (!labelId) {
      toast.error('Please select a label first');
      return;
    }
    try {
      const res = await fetch(`${API}/api/uln/labels/${labelId}/catalog/csv-template`, { headers });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `catalog_import_template.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
        toast.success('Template downloaded!');
      }
    } catch (e) {
      toast.error('Failed to download template');
    }
  };

  const resetImport = () => {
    setFile(null);
    setPreview(null);
    setImportResult(null);
    setStep('upload');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const selectedLabel = labels.find(l => l.label_id === labelId);

  return (
    <div className="min-h-screen bg-slate-50" data-testid="catalog-import-page">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/uln')}
            className="text-sm text-purple-600 hover:text-purple-800 mb-3 flex items-center gap-1"
            data-testid="back-to-uln-btn"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
            Back to ULN
          </button>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Catalog CSV Import</h1>
          <p className="text-slate-500 mt-1 text-base">Bulk import assets into your label catalog from a CSV file</p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center gap-2 mb-8" data-testid="step-indicator">
          {['upload', 'preview', 'result'].map((s, i) => (
            <React.Fragment key={s}>
              {i > 0 && <div className={`flex-1 h-0.5 ${step === s || (s === 'result' && step === 'result') || (s === 'preview' && step !== 'upload') ? 'bg-purple-500' : 'bg-slate-200'}`} />}
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${step === s ? 'bg-purple-600 text-white' : i < ['upload', 'preview', 'result'].indexOf(step) ? 'bg-purple-100 text-purple-700' : 'bg-slate-200 text-slate-500'}`}>
                <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-[10px]">{i + 1}</span>
                {s === 'upload' ? 'Upload' : s === 'preview' ? 'Preview' : 'Results'}
              </div>
            </React.Fragment>
          ))}
        </div>

        {/* Label Selector */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6 shadow-sm" data-testid="label-selector-section">
          <label className="block text-sm font-semibold text-slate-700 mb-2">Target Label</label>
          {labelsLoaded && labels.length === 0 ? (
            <p className="text-sm text-slate-500">No labels found. Create a label in ULN first.</p>
          ) : (
            <select
              value={labelId}
              onChange={(e) => { setLabelId(e.target.value); resetImport(); }}
              className="w-full max-w-md border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              data-testid="label-select"
            >
              {labels.map(l => (
                <option key={l.label_id} value={l.label_id}>{l.name} ({l.label_id})</option>
              ))}
            </select>
          )}
        </div>

        {/* STEP 1: Upload */}
        {step === 'upload' && (
          <div className="space-y-5">
            {/* Template Download */}
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-slate-800">CSV Template</h3>
                  <p className="text-xs text-slate-500 mt-1">Download a pre-formatted template with example data. Fill in your catalog and upload it.</p>
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {EXPECTED_HEADERS.map(h => (
                      <span key={h} className="px-2 py-0.5 bg-slate-100 text-slate-600 text-[11px] font-mono rounded">{h}</span>
                    ))}
                  </div>
                </div>
                <button
                  onClick={handleDownloadTemplate}
                  disabled={!labelId}
                  className="shrink-0 ml-4 flex items-center gap-1.5 bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-700 disabled:opacity-40 transition"
                  data-testid="download-template-btn"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                  Download Template
                </button>
              </div>
            </div>

            {/* Drop Zone */}
            <div
              className={`bg-white rounded-xl border-2 border-dashed p-10 text-center transition-colors cursor-pointer ${dragActive ? 'border-purple-500 bg-purple-50' : file ? 'border-emerald-400 bg-emerald-50' : 'border-slate-300 hover:border-purple-400'}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              data-testid="csv-drop-zone"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                className="hidden"
                data-testid="csv-file-input"
              />
              {file ? (
                <div>
                  <svg className="w-10 h-10 mx-auto text-emerald-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  <p className="text-sm font-semibold text-slate-800">{file.name}</p>
                  <p className="text-xs text-slate-500 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                  <button
                    onClick={(e) => { e.stopPropagation(); resetImport(); }}
                    className="mt-3 text-xs text-red-500 hover:text-red-700 font-medium"
                    data-testid="remove-file-btn"
                  >
                    Remove file
                  </button>
                </div>
              ) : (
                <div>
                  <svg className="w-10 h-10 mx-auto text-slate-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                  <p className="text-sm font-medium text-slate-700">Drop your CSV file here, or click to browse</p>
                  <p className="text-xs text-slate-400 mt-1">Supports .csv files</p>
                </div>
              )}
            </div>

            {/* Options */}
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <label className="flex items-center gap-2.5 cursor-pointer" data-testid="skip-duplicates-toggle">
                <input
                  type="checkbox"
                  checked={skipDuplicates}
                  onChange={(e) => setSkipDuplicates(e.target.checked)}
                  className="rounded border-slate-300 text-purple-600 focus:ring-purple-500"
                />
                <div>
                  <span className="text-sm font-medium text-slate-700">Skip duplicates</span>
                  <p className="text-xs text-slate-400">Assets with matching ISRC or UPC will be skipped</p>
                </div>
              </label>
            </div>

            {/* Preview Button */}
            <div className="flex justify-end">
              <button
                onClick={handlePreview}
                disabled={!file || !labelId || previewLoading}
                className="flex items-center gap-2 bg-purple-600 text-white px-6 py-2.5 rounded-lg font-medium text-sm hover:bg-purple-700 disabled:opacity-40 transition"
                data-testid="preview-btn"
              >
                {previewLoading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                )}
                {previewLoading ? 'Parsing...' : 'Preview CSV'}
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: Preview */}
        {step === 'preview' && preview && (
          <div className="space-y-5">
            {/* Stats Bar */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm text-center" data-testid="preview-total">
                <p className="text-2xl font-bold text-slate-800">{preview.total_rows}</p>
                <p className="text-xs text-slate-500 font-medium">Total Rows</p>
              </div>
              <div className="bg-white rounded-xl border border-emerald-200 p-4 shadow-sm text-center" data-testid="preview-valid">
                <p className="text-2xl font-bold text-emerald-600">{preview.valid_count}</p>
                <p className="text-xs text-emerald-600 font-medium">Valid</p>
              </div>
              <div className="bg-white rounded-xl border border-red-200 p-4 shadow-sm text-center" data-testid="preview-errors">
                <p className="text-2xl font-bold text-red-500">{preview.validation_errors?.length || 0}</p>
                <p className="text-xs text-red-500 font-medium">Errors</p>
              </div>
            </div>

            {/* Validation Errors */}
            {preview.validation_errors?.length > 0 && (
              <div className="bg-red-50 rounded-xl border border-red-200 p-4" data-testid="preview-error-list">
                <h4 className="text-sm font-semibold text-red-700 mb-2">Validation Errors</h4>
                <div className="space-y-1 max-h-40 overflow-y-auto">
                  {preview.validation_errors.map((err, i) => (
                    <p key={i} className="text-xs text-red-600 font-mono">{err.error}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Preview Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="px-5 py-3 border-b border-slate-200 bg-slate-50">
                <h3 className="text-sm font-semibold text-slate-700">Data Preview (first {Math.min(preview.preview_rows.length, 50)} rows)</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200" data-testid="preview-table">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-2.5 text-left text-[11px] font-semibold text-slate-500 uppercase">#</th>
                      {preview.headers.filter(h => !h.startsWith('_')).map(h => (
                        <th key={h} className="px-4 py-2.5 text-left text-[11px] font-semibold text-slate-500 uppercase">{h}</th>
                      ))}
                      <th className="px-4 py-2.5 text-left text-[11px] font-semibold text-slate-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {preview.preview_rows.map((row, i) => (
                      <tr key={i} className={row._has_error ? 'bg-red-50/50' : 'hover:bg-slate-50'} data-testid={`preview-row-${i}`}>
                        <td className="px-4 py-2 text-xs text-slate-400 font-mono">{i + 2}</td>
                        {preview.headers.filter(h => !h.startsWith('_')).map(h => (
                          <td key={h} className="px-4 py-2 text-xs text-slate-700 max-w-[160px] truncate">
                            {h === 'status' ? (
                              <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold ${STATUS_BADGE[row[h]] || 'bg-slate-100 text-slate-600'}`}>{row[h] || 'draft'}</span>
                            ) : h === 'platforms' ? (
                              <span className="text-[11px]">{Array.isArray(row[h]) ? row[h].join(', ') : row[h]}</span>
                            ) : (
                              row[h] || <span className="text-slate-300">-</span>
                            )}
                          </td>
                        ))}
                        <td className="px-4 py-2">
                          {row._has_error ? (
                            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-red-600">
                              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" /></svg>
                              Error
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-600">
                              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                              Valid
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setStep('upload')}
                className="text-sm text-slate-600 hover:text-slate-800 font-medium flex items-center gap-1"
                data-testid="back-to-upload-btn"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                Back to Upload
              </button>
              <button
                onClick={handleImport}
                disabled={importing || !preview.valid_count}
                className="flex items-center gap-2 bg-emerald-600 text-white px-6 py-2.5 rounded-lg font-medium text-sm hover:bg-emerald-700 disabled:opacity-40 transition"
                data-testid="import-btn"
              >
                {importing ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                )}
                {importing ? 'Importing...' : `Import ${preview.valid_count} Assets`}
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Results */}
        {step === 'result' && importResult && (
          <div className="space-y-5" data-testid="import-results">
            {/* Summary Cards */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm text-center" data-testid="result-total">
                <p className="text-2xl font-bold text-slate-800">{importResult.total_rows}</p>
                <p className="text-xs text-slate-500 font-medium">Total Rows</p>
              </div>
              <div className="bg-emerald-50 rounded-xl border border-emerald-200 p-4 text-center" data-testid="result-imported">
                <p className="text-2xl font-bold text-emerald-600">{importResult.imported_count}</p>
                <p className="text-xs text-emerald-600 font-medium">Imported</p>
              </div>
              <div className="bg-amber-50 rounded-xl border border-amber-200 p-4 text-center" data-testid="result-skipped">
                <p className="text-2xl font-bold text-amber-600">{importResult.skipped_count}</p>
                <p className="text-xs text-amber-600 font-medium">Skipped</p>
              </div>
              <div className="bg-red-50 rounded-xl border border-red-200 p-4 text-center" data-testid="result-errors">
                <p className="text-2xl font-bold text-red-500">{importResult.error_count}</p>
                <p className="text-xs text-red-500 font-medium">Errors</p>
              </div>
            </div>

            {/* Imported Assets */}
            {importResult.imported?.length > 0 && (
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="px-5 py-3 border-b border-slate-200 bg-emerald-50">
                  <h3 className="text-sm font-semibold text-emerald-700">Imported Assets ({importResult.imported.length})</h3>
                </div>
                <div className="max-h-60 overflow-y-auto">
                  <table className="min-w-full divide-y divide-slate-100" data-testid="imported-table">
                    <thead className="bg-slate-50 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left text-[11px] font-semibold text-slate-500 uppercase">Asset ID</th>
                        <th className="px-4 py-2 text-left text-[11px] font-semibold text-slate-500 uppercase">Title</th>
                        <th className="px-4 py-2 text-left text-[11px] font-semibold text-slate-500 uppercase">Type</th>
                        <th className="px-4 py-2 text-left text-[11px] font-semibold text-slate-500 uppercase">Artist</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {importResult.imported.map((a) => (
                        <tr key={a.asset_id} className="hover:bg-slate-50">
                          <td className="px-4 py-2 text-xs font-mono text-slate-500">{a.asset_id}</td>
                          <td className="px-4 py-2 text-xs font-medium text-slate-800">{a.title}</td>
                          <td className="px-4 py-2 text-xs text-slate-600 capitalize">{a.type}</td>
                          <td className="px-4 py-2 text-xs text-slate-600">{a.artist || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Skipped */}
            {importResult.skipped?.length > 0 && (
              <div className="bg-amber-50 rounded-xl border border-amber-200 p-4" data-testid="skipped-list">
                <h4 className="text-sm font-semibold text-amber-700 mb-2">Skipped ({importResult.skipped.length})</h4>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {importResult.skipped.map((s, i) => (
                    <p key={i} className="text-xs text-amber-700">Row {s.row}: <span className="font-medium">{s.title}</span> — {s.reason}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Errors */}
            {importResult.errors?.length > 0 && (
              <div className="bg-red-50 rounded-xl border border-red-200 p-4" data-testid="error-list">
                <h4 className="text-sm font-semibold text-red-700 mb-2">Errors ({importResult.errors.length})</h4>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {importResult.errors.map((err, i) => (
                    <p key={i} className="text-xs text-red-600 font-mono">{err.error}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-2">
              <button
                onClick={resetImport}
                className="flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-800 font-medium"
                data-testid="import-another-btn"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                Import Another CSV
              </button>
              <button
                onClick={() => navigate('/uln')}
                className="flex items-center gap-2 bg-purple-600 text-white px-5 py-2.5 rounded-lg font-medium text-sm hover:bg-purple-700 transition"
                data-testid="view-catalog-btn"
              >
                View Catalog
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
