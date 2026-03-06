import React, { useState, useEffect, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { toast } from "sonner";
import {
  Database,
  ArrowUpCircle,
  RefreshCw,
  Shield,
  Clock,
  Server,
  HardDrive,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  ChevronRight,
  Info,
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

function StatusBadge({ status }) {
  const map = {
    available: { color: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30", label: "Available" },
    modifying: { color: "bg-amber-500/15 text-amber-400 border-amber-500/30", label: "Modifying" },
    upgrading: { color: "bg-blue-500/15 text-blue-400 border-blue-500/30", label: "Upgrading" },
    "backing-up": { color: "bg-violet-500/15 text-violet-400 border-violet-500/30", label: "Backing Up" },
  };
  const s = map[status] || { color: "bg-gray-500/15 text-gray-400 border-gray-500/30", label: status };
  return <Badge data-testid="rds-status-badge" className={`${s.color} border font-medium`}>{s.label}</Badge>;
}

export default function RDSUpgradePage() {
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedInstance, setSelectedInstance] = useState(null);
  const [targets, setTargets] = useState([]);
  const [targetsLoading, setTargetsLoading] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState(null);
  const [applyImmediately, setApplyImmediately] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const fetchInstances = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/api/cve/iac/rds/instances`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setInstances(data.instances || []);
      if (data.instances?.length === 1) {
        setSelectedInstance(data.instances[0]);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchTargets = useCallback(async (instanceId) => {
    setTargetsLoading(true);
    setTargets([]);
    setSelectedTarget(null);
    try {
      const res = await fetch(`${API}/api/cve/iac/rds/upgrade-targets/${instanceId}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setTargets(data.targets?.filter(t => t.is_valid_target) || []);
    } catch (e) {
      toast.error("Failed to fetch upgrade targets: " + e.message);
    } finally {
      setTargetsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInstances();
  }, [fetchInstances]);

  useEffect(() => {
    if (selectedInstance) {
      fetchTargets(selectedInstance.db_instance_id);
    }
  }, [selectedInstance, fetchTargets]);

  const handleUpgrade = async () => {
    if (!selectedInstance || !selectedTarget) return;
    setUpgrading(true);
    try {
      const res = await fetch(`${API}/api/cve/iac/rds/upgrade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          instance_id: selectedInstance.db_instance_id,
          target_version: selectedTarget,
          apply_immediately: applyImmediately,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upgrade failed");
      toast.success(`Upgrade to PostgreSQL ${selectedTarget} initiated successfully!`);
      setShowConfirm(false);
      setSelectedTarget(null);
      // Refresh instance data after a short delay
      setTimeout(() => fetchInstances(), 3000);
    } catch (e) {
      toast.error("Upgrade failed: " + e.message);
    } finally {
      setUpgrading(false);
    }
  };

  if (loading) {
    return (
      <div data-testid="rds-loading" className="min-h-screen bg-[#0a0e1a] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  return (
    <div data-testid="rds-upgrade-page" className="min-h-screen bg-[#0a0e1a] text-gray-100">
      <div className="max-w-5xl mx-auto px-4 py-10">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2.5 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <Database className="w-6 h-6 text-blue-400" />
            </div>
            <h1 data-testid="rds-page-title" className="text-2xl font-bold tracking-tight">
              Amazon RDS PostgreSQL Upgrade
            </h1>
          </div>
          <p className="text-gray-400 ml-14">
            Upgrade your RDS PostgreSQL instances to the latest minor version for security patches and performance improvements.
          </p>
        </div>

        {error && (
          <div data-testid="rds-error" className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 mt-0.5 shrink-0" />
            <div>
              <p className="font-medium text-red-300">Connection Error</p>
              <p className="text-sm text-red-400/80">{error}</p>
            </div>
          </div>
        )}

        {/* Instance Cards */}
        {instances.length === 0 && !error ? (
          <Card className="bg-[#111827] border-gray-800">
            <CardContent className="p-8 text-center text-gray-400">
              No PostgreSQL RDS instances found in this region.
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {instances.map((inst) => (
              <Card
                key={inst.db_instance_id}
                data-testid={`rds-instance-card-${inst.db_instance_id}`}
                className={`bg-[#111827] border transition-all cursor-pointer ${
                  selectedInstance?.db_instance_id === inst.db_instance_id
                    ? "border-blue-500/50 ring-1 ring-blue-500/20"
                    : "border-gray-800 hover:border-gray-700"
                }`}
                onClick={() => setSelectedInstance(inst)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Server className="w-5 h-5 text-blue-400" />
                      <CardTitle data-testid="rds-instance-id" className="text-lg text-gray-100">
                        {inst.db_instance_id}
                      </CardTitle>
                      <StatusBadge status={inst.status} />
                    </div>
                    <Button
                      data-testid="rds-refresh-btn"
                      variant="ghost"
                      size="sm"
                      onClick={(e) => { e.stopPropagation(); fetchInstances(); }}
                      className="text-gray-400 hover:text-gray-200"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </Button>
                  </div>
                  <CardDescription className="text-gray-500 ml-8">
                    {inst.endpoint}:{inst.port}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <InfoBlock
                      icon={<Database className="w-4 h-4" />}
                      label="Engine Version"
                      value={`PostgreSQL ${inst.engine_version}`}
                      testId="rds-current-version"
                    />
                    <InfoBlock
                      icon={<HardDrive className="w-4 h-4" />}
                      label="Instance Class"
                      value={inst.db_instance_class}
                      testId="rds-instance-class"
                    />
                    <InfoBlock
                      icon={<Shield className="w-4 h-4" />}
                      label="Multi-AZ"
                      value={inst.multi_az ? "Enabled" : "Disabled"}
                      testId="rds-multi-az"
                    />
                    <InfoBlock
                      icon={<Clock className="w-4 h-4" />}
                      label="Maintenance Window"
                      value={inst.preferred_maintenance_window || "Not set"}
                      testId="rds-maintenance-window"
                    />
                  </div>

                  {/* Additional details row */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3 pt-3 border-t border-gray-800/50">
                    <InfoBlock
                      icon={<HardDrive className="w-4 h-4" />}
                      label="Storage"
                      value={`${inst.allocated_storage_gb} GB ${inst.storage_type}`}
                      testId="rds-storage"
                    />
                    <InfoBlock
                      icon={<Shield className="w-4 h-4" />}
                      label="Encrypted"
                      value={inst.storage_encrypted ? "Yes" : "No"}
                      testId="rds-encrypted"
                    />
                    <InfoBlock
                      icon={<Clock className="w-4 h-4" />}
                      label="Backup Retention"
                      value={`${inst.backup_retention_period} days`}
                      testId="rds-backup-retention"
                    />
                    <InfoBlock
                      icon={<ArrowUpCircle className="w-4 h-4" />}
                      label="Auto Minor Upgrade"
                      value={inst.auto_minor_version_upgrade ? "Enabled" : "Disabled"}
                      testId="rds-auto-upgrade"
                    />
                  </div>

                  {Object.keys(inst.pending_modified_values || {}).length > 0 && (
                    <div data-testid="rds-pending-changes" className="mt-3 p-3 rounded-md bg-amber-500/10 border border-amber-500/20">
                      <p className="text-sm text-amber-300 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" />
                        Pending changes: {JSON.stringify(inst.pending_modified_values)}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}

            {/* Upgrade Targets Section */}
            {selectedInstance && (
              <Card data-testid="rds-upgrade-section" className="bg-[#111827] border-gray-800">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <ArrowUpCircle className="w-5 h-5 text-emerald-400" />
                    <div>
                      <CardTitle className="text-lg text-gray-100">
                        Available Minor Version Upgrades
                      </CardTitle>
                      <CardDescription className="text-gray-500">
                        Current: PostgreSQL {selectedInstance.engine_version} &mdash; Select a target version to upgrade
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {targetsLoading ? (
                    <div data-testid="rds-targets-loading" className="flex items-center justify-center py-8">
                      <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
                      <span className="ml-2 text-gray-400">Fetching available versions...</span>
                    </div>
                  ) : targets.length === 0 ? (
                    <div data-testid="rds-no-upgrades" className="text-center py-8">
                      <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
                      <p className="text-gray-300 font-medium">Already on the latest minor version!</p>
                      <p className="text-sm text-gray-500 mt-1">
                        PostgreSQL {selectedInstance.engine_version} is the most recent available version.
                      </p>
                    </div>
                  ) : (
                    <>
                      <div className="space-y-2 mb-6">
                        {targets.map((t) => (
                          <button
                            key={t.engine_version}
                            data-testid={`rds-target-${t.engine_version}`}
                            onClick={() => setSelectedTarget(t.engine_version)}
                            className={`w-full flex items-center justify-between p-3.5 rounded-lg border transition-all text-left ${
                              selectedTarget === t.engine_version
                                ? "bg-blue-500/10 border-blue-500/40 ring-1 ring-blue-500/20"
                                : "bg-[#0d1322] border-gray-800 hover:border-gray-700"
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <ChevronRight className={`w-4 h-4 transition-transform ${
                                selectedTarget === t.engine_version ? "rotate-90 text-blue-400" : "text-gray-600"
                              }`} />
                              <div>
                                <p className="font-medium text-gray-200">PostgreSQL {t.engine_version}</p>
                                <p className="text-xs text-gray-500">{t.description}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {t.engine_version === targets[0]?.engine_version && (
                                <Badge className="bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-xs">
                                  Latest
                                </Badge>
                              )}
                              <Badge className="bg-gray-700/50 text-gray-400 border-gray-600 text-xs">
                                {t.status}
                              </Badge>
                            </div>
                          </button>
                        ))}
                      </div>

                      {/* Apply mode toggle */}
                      <div className="flex items-center gap-3 mb-6 p-3 rounded-lg bg-[#0d1322] border border-gray-800">
                        <label className="flex items-center gap-2 cursor-pointer" data-testid="rds-apply-toggle">
                          <input
                            type="checkbox"
                            checked={applyImmediately}
                            onChange={(e) => setApplyImmediately(e.target.checked)}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500/30"
                          />
                          <span className="text-sm text-gray-300">Apply immediately</span>
                        </label>
                        <span className="text-xs text-gray-500">
                          {applyImmediately
                            ? "Upgrade starts now (brief downtime expected)"
                            : "Upgrade applies during next maintenance window"}
                        </span>
                      </div>

                      {/* Upgrade button */}
                      <Button
                        data-testid="rds-upgrade-btn"
                        onClick={() => setShowConfirm(true)}
                        disabled={!selectedTarget || upgrading}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 disabled:opacity-40"
                      >
                        {upgrading ? (
                          <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Upgrading...</>
                        ) : (
                          <><ArrowUpCircle className="w-4 h-4 mr-2" /> Upgrade to PostgreSQL {selectedTarget || "..."}</>
                        )}
                      </Button>
                    </>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Info card */}
            <Card className="bg-[#111827] border-gray-800">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-400 mt-0.5 shrink-0" />
                  <div className="text-sm text-gray-400 space-y-1">
                    <p><strong className="text-gray-300">Minor version upgrades</strong> include security patches, bug fixes, and performance improvements.</p>
                    <p>Applying immediately causes a brief outage (typically under 10 minutes). Alternatively, schedule for the maintenance window.</p>
                    <p>After upgrading, review your extensions with <code className="bg-gray-800 px-1.5 py-0.5 rounded text-blue-300">ALTER EXTENSION UPDATE</code> if needed.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Confirmation Modal */}
        {showConfirm && (
          <div data-testid="rds-confirm-modal" className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="bg-[#111827] border border-gray-700 rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-amber-500/10">
                  <AlertTriangle className="w-6 h-6 text-amber-400" />
                </div>
                <h2 className="text-lg font-bold text-gray-100">Confirm Upgrade</h2>
              </div>
              <div className="space-y-3 mb-6 text-sm text-gray-400">
                <p>You are about to upgrade:</p>
                <div className="p-3 rounded-lg bg-[#0d1322] border border-gray-800 space-y-1.5">
                  <p><span className="text-gray-500">Instance:</span> <span className="text-gray-200">{selectedInstance?.db_instance_id}</span></p>
                  <p><span className="text-gray-500">Current:</span> <span className="text-gray-200">PostgreSQL {selectedInstance?.engine_version}</span></p>
                  <p><span className="text-gray-500">Target:</span> <span className="text-emerald-400 font-medium">PostgreSQL {selectedTarget}</span></p>
                  <p><span className="text-gray-500">Timing:</span> <span className="text-gray-200">{applyImmediately ? "Immediately" : "Next maintenance window"}</span></p>
                </div>
                {applyImmediately && (
                  <p className="text-amber-400/80 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
                    This will cause a brief service interruption.
                  </p>
                )}
              </div>
              <div className="flex gap-3">
                <Button
                  data-testid="rds-confirm-cancel-btn"
                  variant="outline"
                  className="flex-1 border-gray-700 text-gray-300 hover:bg-gray-800"
                  onClick={() => setShowConfirm(false)}
                  disabled={upgrading}
                >
                  Cancel
                </Button>
                <Button
                  data-testid="rds-confirm-upgrade-btn"
                  className="flex-1 bg-blue-600 hover:bg-blue-500 text-white"
                  onClick={handleUpgrade}
                  disabled={upgrading}
                >
                  {upgrading ? (
                    <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Upgrading...</>
                  ) : (
                    "Confirm Upgrade"
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function InfoBlock({ icon, label, value, testId }) {
  return (
    <div data-testid={testId} className="flex items-start gap-2">
      <span className="text-gray-500 mt-0.5">{icon}</span>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-sm text-gray-300 font-medium">{value}</p>
      </div>
    </div>
  );
}
