import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Card, CardContent } from "../components/ui/card";

const API = process.env.REACT_APP_BACKEND_URL;

export default function OAuthCallbackPage() {
  const [params] = useSearchParams();
  const [status, setStatus] = useState("processing");
  const [message, setMessage] = useState("Processing OAuth callback...");

  useEffect(() => {
    const code = params.get("code");
    const state = params.get("state");
    const error = params.get("error");

    if (error) {
      setStatus("error");
      setMessage(`OAuth error: ${error} - ${params.get("error_description") || ""}`);
      return;
    }

    if (!code) {
      setStatus("error");
      setMessage("No authorization code received.");
      return;
    }

    const platform = sessionStorage.getItem("oauth_platform") || "twitter_x";
    const codeVerifier = sessionStorage.getItem("oauth_code_verifier") || "";
    const savedState = sessionStorage.getItem("oauth_state") || "";

    if (savedState && state !== savedState) {
      setStatus("error");
      setMessage("State mismatch. Possible CSRF attack.");
      return;
    }

    const endpoint = platform === "twitter_x" ? "twitter" : platform;
    const redirectUri = `${window.location.origin}/oauth/callback`;

    fetch(`${API}/api/integrations/${endpoint}/callback`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        redirect_uri: redirectUri,
        code_verifier: codeVerifier,
        state,
      }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.success) {
          setStatus("success");
          setMessage(`${platform} connected successfully! You can close this window.`);
          sessionStorage.removeItem("oauth_code_verifier");
          sessionStorage.removeItem("oauth_state");
          sessionStorage.removeItem("oauth_platform");
        } else {
          setStatus("error");
          setMessage(data.error || "Token exchange failed.");
        }
      })
      .catch((e) => {
        setStatus("error");
        setMessage(`Error: ${e.message}`);
      });
  }, [params, token]);

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4" data-testid="oauth-callback-page">
      <Card className="border-zinc-800 bg-zinc-900/80 w-full max-w-md">
        <CardContent className="p-8 text-center">
          <div className={`w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center ${
            status === "success" ? "bg-emerald-500/20" : status === "error" ? "bg-rose-500/20" : "bg-zinc-800"
          }`}>
            {status === "processing" && (
              <div className="w-5 h-5 border-2 border-zinc-500 border-t-zinc-200 rounded-full animate-spin" />
            )}
            {status === "success" && <span className="text-emerald-400 text-xl">&#10003;</span>}
            {status === "error" && <span className="text-rose-400 text-xl">&#10007;</span>}
          </div>
          <h2 className="text-lg font-semibold text-zinc-100 mb-2">
            {status === "processing" ? "Processing..." : status === "success" ? "Connected!" : "Connection Failed"}
          </h2>
          <p className="text-sm text-zinc-400">{message}</p>
          {status !== "processing" && (
            <button
              onClick={() => window.close()}
              className="mt-4 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-md text-sm"
              data-testid="close-oauth-window-btn"
            >
              Close Window
            </button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
