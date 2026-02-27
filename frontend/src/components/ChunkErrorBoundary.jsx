import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

function isChunkLoadError(error) {
  if (!error) return false;
  const msg = error.message || "";
  return (
    error.name === "ChunkLoadError" ||
    msg.includes("Loading chunk") ||
    msg.includes("Loading CSS chunk") ||
    msg.includes("dynamically imported module") ||
    msg.includes("Failed to fetch dynamically imported module") ||
    msg.includes("Importing a module script failed")
  );
}

export class ChunkErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  handleRetry = () => {
    if (isChunkLoadError(this.state.error)) {
      // After a deploy the old chunk is gone — a full reload fetches the new manifest
      window.location.reload();
    } else {
      // For non-chunk errors, just reset state so React re-renders the children
      this.setState({ hasError: false, error: null });
    }
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    const isChunk = isChunkLoadError(this.state.error);
    const variant = this.props.variant || "page"; // "page" | "tab"

    if (variant === "tab") {
      return (
        <div data-testid="chunk-error-boundary-tab" className="flex flex-col items-center justify-center py-20 gap-4">
          <AlertTriangle className="w-8 h-8 text-amber-400" />
          <p className="text-slate-300 text-sm text-center max-w-md">
            {isChunk
              ? "This section failed to load — the app may have been updated since you opened this tab."
              : "Something went wrong loading this section."}
          </p>
          <button
            data-testid="chunk-error-retry-btn"
            onClick={this.handleRetry}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            {isChunk ? "Reload page" : "Try again"}
          </button>
        </div>
      );
    }

    // Full-page variant (for route-level boundaries)
    return (
      <div data-testid="chunk-error-boundary-page" className="min-h-[60vh] flex items-center justify-center px-4">
        <div className="text-center max-w-md space-y-4">
          <div className="mx-auto w-14 h-14 rounded-full bg-amber-500/10 flex items-center justify-center">
            <AlertTriangle className="w-7 h-7 text-amber-400" />
          </div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
            Page failed to load
          </h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            {isChunk
              ? "A newer version of the app is available. Click below to refresh and load the latest version."
              : "An unexpected error occurred while loading this page."}
          </p>
          <button
            data-testid="chunk-error-retry-btn"
            onClick={this.handleRetry}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
          >
            <RefreshCw className="w-4 h-4" />
            {isChunk ? "Reload page" : "Try again"}
          </button>
        </div>
      </div>
    );
  }
}
