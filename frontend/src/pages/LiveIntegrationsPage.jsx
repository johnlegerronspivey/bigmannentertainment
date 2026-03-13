import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Progress } from "../components/ui/progress";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

/* ─── status colours ─── */
const statusStyle = (ok) =>
  ok
    ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
    : "bg-rose-500/15 text-rose-400 border-rose-500/30";

/* ─── platform icons (lucide-style SVG paths) ─── */
const PlatformIcon = ({ platform, size = 20 }) => {
  const icons = {
    twitter_x: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
      </svg>
    ),
    tiktok: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .55.05.81.13V9.04a6.27 6.27 0 0 0-.81-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34c3.5 0 6.34-2.84 6.34-6.34V9.41a8.16 8.16 0 0 0 4.77 1.53V7.49a4.84 4.84 0 0 1-1.01-.8z" />
      </svg>
    ),
    snapchat: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
        <path d="M12.206.793c.99 0 4.347.276 5.93 3.821.529 1.193.403 3.219.299 4.847l-.003.06c-.012.18-.022.345-.03.51.075.045.203.09.401.09.3-.016.659-.12.989-.23.662-.24 1.22-.39 1.697-.26.341.09.574.29.647.548.106.37-.085.8-.476 1.112-.21.173-.53.352-.938.576-.04.02-.078.04-.116.06-.11.061-.22.121-.327.189-.233.148-.412.33-.536.549-.22.39-.15.802-.082 1.21.007.04.014.081.02.121.06.391.12.782.12 1.133a.44.44 0 01-.03.15c-.1.31-.476.568-.92.707a3.1 3.1 0 01-1.007.139c-.158 0-.31-.009-.452-.024a3.55 3.55 0 00-.338-.025c-.13 0-.256.01-.382.033-.317.053-.59.228-.854.399-.364.236-.731.474-1.23.474-.036 0-.072-.003-.107-.005h-.04c-.499 0-.867-.237-1.23-.474-.263-.17-.536-.346-.854-.399a2.39 2.39 0 00-.382-.033c-.114 0-.228.007-.337.025a4 4 0 01-.453.024 3.1 3.1 0 01-1.006-.14c-.444-.138-.82-.397-.92-.706a.44.44 0 01-.031-.15c0-.351.06-.742.12-1.133l.02-.122c.068-.407.138-.82-.082-1.21a1.52 1.52 0 00-.536-.548 7.9 7.9 0 00-.327-.19c-.038-.02-.076-.04-.116-.06-.407-.224-.728-.403-.938-.576-.39-.313-.582-.742-.476-1.112.073-.258.306-.459.647-.549.477-.129 1.035.02 1.697.261.33.11.689.214.99.23.198 0 .326-.046.4-.09-.006-.165-.017-.33-.029-.51l-.003-.06c-.104-1.628-.23-3.654.3-4.847C7.866 1.069 11.217.793 12.206.793" />
      </svg>
    ),
    cloudfront: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z" />
      </svg>
    ),
  };
  return icons[platform] || icons.cloudfront;
};

/* ─── Connection Card ─── */
const ConnectionCard = ({ platform, data, onTest, onConnect, testing }) => {
  const connected = data?.has_credentials || data?.configured || false;
  const canWrite = data?.can_write || false;
  const oauthRequired = data?.oauth_required || false;

  return (
    <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm hover:border-zinc-700 transition-colors" data-testid={`connection-card-${platform}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-lg ${connected ? "bg-emerald-500/10 text-emerald-400" : "bg-zinc-800 text-zinc-500"}`}>
              <PlatformIcon platform={platform} size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-zinc-100 text-sm">{data?.platform || platform}</h3>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline" className={`text-[10px] px-1.5 py-0 ${statusStyle(connected)}`}>
                  {connected ? "Connected" : "Not Connected"}
                </Badge>
                {connected && canWrite && (
                  <Badge variant="outline" className="text-[10px] px-1.5 py-0 bg-blue-500/15 text-blue-400 border-blue-500/30">
                    Read + Write
                  </Badge>
                )}
                {connected && !canWrite && data?.has_credentials && (
                  <Badge variant="outline" className="text-[10px] px-1.5 py-0 bg-amber-500/15 text-amber-400 border-amber-500/30">
                    Read Only
                  </Badge>
                )}
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              className="text-xs h-8 border-zinc-700 hover:bg-zinc-800"
              onClick={() => onTest(platform)}
              disabled={testing === platform}
              data-testid={`test-${platform}-btn`}
            >
              {testing === platform ? "Testing..." : "Test"}
            </Button>
            {oauthRequired && !canWrite && (
              <Button
                size="sm"
                className="text-xs h-8 bg-indigo-600 hover:bg-indigo-700"
                onClick={() => onConnect(platform)}
                data-testid={`connect-${platform}-btn`}
              >
                Connect OAuth
              </Button>
            )}
          </div>
        </div>
        {data?.credential_source && (
          <p className="text-[11px] text-zinc-500 mt-3">
            Source: <span className="text-zinc-400">{data.credential_source === "env" ? "Environment Config" : data.credential_source === "env_fallback" ? "Environment (Fallback)" : "User OAuth"}</span>
            {data?.note && <span className="block mt-0.5">{data.note}</span>}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

/* ─── CloudFront Card ─── */
const CloudFrontCard = ({ data, onSetup, setting }) => {
  const configured = data?.configured || false;

  return (
    <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm" data-testid="cloudfront-card">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-lg ${configured ? "bg-emerald-500/10 text-emerald-400" : "bg-zinc-800 text-zinc-500"}`}>
              <PlatformIcon platform="cloudfront" size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-zinc-100 text-sm">AWS CloudFront CDN</h3>
              <Badge variant="outline" className={`text-[10px] px-1.5 py-0 mt-1 ${statusStyle(configured)}`}>
                {configured ? "Deployed" : "Not Configured"}
              </Badge>
            </div>
          </div>
          {!configured && (
            <Button
              size="sm"
              className="text-xs h-8 bg-amber-600 hover:bg-amber-700"
              onClick={onSetup}
              disabled={setting}
              data-testid="setup-cloudfront-btn"
            >
              {setting ? "Creating..." : "Create Distribution"}
            </Button>
          )}
        </div>
        {configured && (
          <div className="mt-3 p-3 rounded-md bg-zinc-800/50 space-y-1">
            <p className="text-[11px] text-zinc-500">Distribution ID: <span className="text-zinc-300 font-mono">{data.distribution_id}</span></p>
            <p className="text-[11px] text-zinc-500">Domain: <span className="text-emerald-400 font-mono">{data.domain}</span></p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

/* ─── Test Result Panel ─── */
const TestResultPanel = ({ result, platform }) => {
  if (!result) return null;
  const ok = result.connected || result.token_valid;

  return (
    <Card className={`border ${ok ? "border-emerald-500/30 bg-emerald-500/5" : "border-rose-500/30 bg-rose-500/5"}`} data-testid={`test-result-${platform}`}>
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <div className={`w-2 h-2 rounded-full ${ok ? "bg-emerald-400" : "bg-rose-400"}`} />
          <h4 className="text-sm font-medium text-zinc-200">{platform} — {ok ? "Connected" : "Failed"}</h4>
        </div>
        <pre className="text-[11px] text-zinc-400 overflow-auto max-h-40 whitespace-pre-wrap font-mono">
          {JSON.stringify(result, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
};

/* ─── Main Page ─── */
export default function LiveIntegrationsPage() {
  const { user } = useAuth();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(null);
  const [testResults, setTestResults] = useState({});
  const [settingCF, setSettingCF] = useState(false);

  const getHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem("token")}`,
    "Content-Type": "application/json",
  });

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/integrations/status/all`, { headers: getHeaders() });
      if (res.ok) setStatus(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const testPlatform = async (platform) => {
    setTesting(platform);
    try {
      const endpoint = platform === "twitter_x" ? "twitter" : platform;
      const res = await fetch(`${API}/api/integrations/${endpoint}/test`, { headers: getHeaders() });
      const data = await res.json();
      setTestResults((prev) => ({ ...prev, [platform]: data }));
      toast(data.connected || data.token_valid ? `${platform} connected!` : `${platform} test failed`);
    } catch (e) {
      toast.error(`Test failed: ${e.message}`);
    } finally {
      setTesting(null);
    }
  };

  const connectOAuth = async (platform) => {
    const endpoint = platform === "twitter_x" ? "twitter" : platform;
    const redirectUri = `${window.location.origin}/oauth/callback`;
    try {
      const res = await fetch(`${API}/api/integrations/${endpoint}/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`, { headers: getHeaders() });
      const data = await res.json();
      if (data.url) {
        if (data.code_verifier) {
          sessionStorage.setItem("oauth_code_verifier", data.code_verifier);
          sessionStorage.setItem("oauth_state", data.state);
          sessionStorage.setItem("oauth_platform", platform);
        }
        window.open(data.url, "_blank", "width=600,height=700");
        toast("OAuth window opened. Complete authorization there.");
      }
    } catch (e) {
      toast.error(`OAuth init failed: ${e.message}`);
    }
  };

  const setupCloudFront = async () => {
    setSettingCF(true);
    try {
      const res = await fetch(`${API}/api/integrations/cloudfront/setup`, { method: "POST", headers: getHeaders() });
      const data = await res.json();
      if (data.status === "success") {
        toast.success(`CloudFront created: ${data.data.domain_name}`);
        fetchStatus();
      } else {
        toast.error(data.data?.message || "Setup failed");
      }
    } catch (e) {
      toast.error(`Setup error: ${e.message}`);
    } finally {
      setSettingCF(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <Progress value={40} className="w-48" />
      </div>
    );
  }

  const platforms = status?.platforms || {};
  const socialPlatforms = ["twitter_x", "tiktok", "snapchat"];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="live-integrations-page">
      {/* Header */}
      <div className="border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-5">
          <h1 className="text-xl font-bold tracking-tight">Live Integrations</h1>
          <p className="text-sm text-zinc-500 mt-1">Manage connections to social platforms and AWS infrastructure</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-6">
        <Tabs defaultValue="social" className="space-y-5">
          <TabsList className="bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="social" className="data-[state=active]:bg-zinc-800" data-testid="tab-social">Social Platforms</TabsTrigger>
            <TabsTrigger value="infra" className="data-[state=active]:bg-zinc-800" data-testid="tab-infra">Infrastructure</TabsTrigger>
            <TabsTrigger value="results" className="data-[state=active]:bg-zinc-800" data-testid="tab-results">
              Test Results {Object.keys(testResults).length > 0 && `(${Object.keys(testResults).length})`}
            </TabsTrigger>
          </TabsList>

          {/* Social tab */}
          <TabsContent value="social" className="space-y-4">
            <CardDescription className="text-zinc-500 text-sm">
              Connect Twitter/X, TikTok, and Snapchat for live content distribution and metrics.
            </CardDescription>
            <div className="grid gap-4">
              {socialPlatforms.map((p) => (
                <ConnectionCard
                  key={p}
                  platform={p}
                  data={platforms[p]}
                  onTest={testPlatform}
                  onConnect={connectOAuth}
                  testing={testing}
                />
              ))}
            </div>
            <Card className="border-zinc-800 bg-zinc-900/40">
              <CardContent className="p-4">
                <p className="text-xs text-zinc-500">
                  <strong className="text-zinc-400">OAuth Flow:</strong> Twitter/X and TikTok require user authorization. Click "Connect OAuth" to open the authorization window. After granting access, tokens are saved automatically for live posting and metrics.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Infrastructure tab */}
          <TabsContent value="infra" className="space-y-4">
            <CardDescription className="text-zinc-500 text-sm">
              AWS CloudFront CDN for media delivery. Uses your configured AWS access keys.
            </CardDescription>
            <CloudFrontCard data={platforms.cloudfront} onSetup={setupCloudFront} setting={settingCF} />
          </TabsContent>

          {/* Test Results tab */}
          <TabsContent value="results" className="space-y-4">
            {Object.keys(testResults).length === 0 ? (
              <Card className="border-zinc-800 bg-zinc-900/40">
                <CardContent className="p-8 text-center">
                  <p className="text-sm text-zinc-500">No tests run yet. Go to Social Platforms and click "Test".</p>
                </CardContent>
              </Card>
            ) : (
              Object.entries(testResults).map(([p, r]) => (
                <TestResultPanel key={p} platform={p} result={r} />
              ))
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
