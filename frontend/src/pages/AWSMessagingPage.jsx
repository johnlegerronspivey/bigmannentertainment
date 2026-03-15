import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

const statusBadge = (ok) => (
  <Badge variant="outline" className={`text-[10px] ${ok ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : "bg-rose-500/15 text-rose-400 border-rose-500/30"}`}>
    {ok ? "Connected" : "Unavailable"}
  </Badge>
);

const ServiceCard = ({ title, data, icon }) => (
  <Card className="border-zinc-800 bg-zinc-900/60 backdrop-blur-sm" data-testid={`service-status-${title.toLowerCase().replace(/\s+/g, "-")}`}>
    <CardContent className="p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className={`p-2.5 rounded-lg ${data?.available ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`}>{icon}</div>
        <div>
          <h3 className="font-semibold text-zinc-100 text-sm">{title}</h3>
          {statusBadge(data?.available)}
        </div>
      </div>
      <div className="text-xs text-zinc-500 space-y-1">
        {data?.region && <p>Region: <span className="text-zinc-300">{data.region}</span></p>}
        {data?.service && <p>Service: <span className="text-zinc-300">{data.service}</span></p>}
      </div>
    </CardContent>
  </Card>
);

const DataTable = ({ columns, rows, emptyMsg }) => (
  <div className="overflow-x-auto">
    <table className="w-full text-sm" data-testid="data-table">
      <thead>
        <tr className="border-b border-zinc-800">
          {columns.map((c, i) => <th key={i} className="text-left py-2 px-3 text-zinc-400 font-medium text-xs">{c.label}</th>)}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr><td colSpan={columns.length} className="py-8 text-center text-zinc-500">{emptyMsg || "No data"}</td></tr>
        ) : rows.map((row, i) => (
          <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
            {columns.map((c, j) => <td key={j} className="py-2 px-3 text-zinc-300 text-xs">{c.render ? c.render(row) : row[c.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default function AWSMessagingPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("kinesis");

  // Kinesis
  const [streams, setStreams] = useState([]);
  const [firehose, setFirehose] = useState([]);
  // SNS
  const [topics, setTopics] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  // SQS
  const [queues, setQueues] = useState([]);
  // EventBridge
  const [buses, setBuses] = useState([]);
  const [rules, setRules] = useState([]);
  const [archives, setArchives] = useState([]);

  const token = localStorage.getItem("token");
  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchStatus = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/aws-messaging/status`, { headers });
      if (res.ok) setStatus(await res.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const fetchKinesis = async () => {
    try {
      const [s, f] = await Promise.all([
        fetch(`${API}/api/aws-messaging/kinesis/streams`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-messaging/kinesis/firehose`, { headers }).then(r => r.ok ? r.json() : null),
      ]);
      if (s) setStreams(s.streams || []);
      if (f) setFirehose(f.firehose_streams || []);
    } catch (e) { console.error(e); }
  };

  const fetchSNS = async () => {
    try {
      const [t, sub] = await Promise.all([
        fetch(`${API}/api/aws-messaging/sns/topics`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-messaging/sns/subscriptions`, { headers }).then(r => r.ok ? r.json() : null),
      ]);
      if (t) setTopics(t.topics || []);
      if (sub) setSubscriptions(sub.subscriptions || []);
    } catch (e) { console.error(e); }
  };

  const fetchSQS = async () => {
    try {
      const res = await fetch(`${API}/api/aws-messaging/sqs/queues`, { headers });
      if (res.ok) { const d = await res.json(); setQueues(d.queues || []); }
    } catch (e) { console.error(e); }
  };

  const fetchEventBridge = async () => {
    try {
      const [b, r, a] = await Promise.all([
        fetch(`${API}/api/aws-messaging/eventbridge/buses`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-messaging/eventbridge/rules`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/aws-messaging/eventbridge/archives`, { headers }).then(r => r.ok ? r.json() : null),
      ]);
      if (b) setBuses(b.event_buses || []);
      if (r) setRules(r.rules || []);
      if (a) setArchives(a.archives || []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    if (tab === "kinesis") fetchKinesis();
    if (tab === "sns") fetchSNS();
    if (tab === "sqs") fetchSQS();
    if (tab === "eventbridge") fetchEventBridge();
  }, [tab]);

  if (loading) return <div className="min-h-screen bg-zinc-950 flex items-center justify-center"><div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" /></div>;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100" data-testid="aws-messaging-page">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">Messaging & Events</h1>
          <p className="text-zinc-400 text-sm">Kinesis Streaming, SNS Notifications, SQS Queues, EventBridge</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <ServiceCard title="Kinesis" data={status?.kinesis} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>} />
          <ServiceCard title="SNS" data={status?.sns} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>} />
          <ServiceCard title="SQS" data={status?.sqs} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>} />
          <ServiceCard title="EventBridge" data={status?.eventbridge} icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>} />
        </div>

        <Tabs value={tab} onValueChange={setTab} className="space-y-6">
          <TabsList className="bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="kinesis" data-testid="tab-kinesis">Kinesis</TabsTrigger>
            <TabsTrigger value="sns" data-testid="tab-sns">SNS</TabsTrigger>
            <TabsTrigger value="sqs" data-testid="tab-sqs">SQS</TabsTrigger>
            <TabsTrigger value="eventbridge" data-testid="tab-eventbridge">EventBridge</TabsTrigger>
          </TabsList>

          {/* KINESIS TAB */}
          <TabsContent value="kinesis">
            <div className="space-y-6">
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Data Streams ({streams.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Stream" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className="text-[10px]">{r.status}</Badge> },
                    { key: "shard_count", label: "Shards" },
                    { key: "retention_hours", label: "Retention (hrs)" },
                    { key: "encryption", label: "Encryption" },
                  ]} rows={streams} emptyMsg="No data streams" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Firehose Delivery Streams ({firehose.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Stream" },
                    { key: "status", label: "Status", render: (r) => <Badge variant="outline" className="text-[10px]">{r.status}</Badge> },
                    { key: "type", label: "Type" },
                    { key: "created_at", label: "Created" },
                  ]} rows={firehose} emptyMsg="No firehose streams" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* SNS TAB */}
          <TabsContent value="sns">
            <div className="space-y-6">
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Topics ({topics.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Topic" },
                    { key: "subscriptions_confirmed", label: "Subscriptions" },
                    { key: "subscriptions_pending", label: "Pending" },
                    { key: "display_name", label: "Display Name" },
                  ]} rows={topics} emptyMsg="No SNS topics" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Subscriptions ({subscriptions.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "protocol", label: "Protocol" },
                    { key: "endpoint", label: "Endpoint" },
                    { key: "topic_arn", label: "Topic ARN", render: (r) => <span className="truncate max-w-[200px] inline-block">{(r.topic_arn || "").split(":").pop()}</span> },
                  ]} rows={subscriptions} emptyMsg="No subscriptions" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* SQS TAB */}
          <TabsContent value="sqs">
            <Card className="border-zinc-800 bg-zinc-900/60">
              <CardHeader><CardTitle className="text-lg">Queues ({queues.length})</CardTitle></CardHeader>
              <CardContent>
                <DataTable columns={[
                  { key: "name", label: "Queue" },
                  { key: "messages_available", label: "Available" },
                  { key: "messages_in_flight", label: "In Flight" },
                  { key: "messages_delayed", label: "Delayed" },
                  { key: "visibility_timeout", label: "Timeout (s)" },
                  { key: "is_fifo", label: "FIFO", render: (r) => r.is_fifo ? <Badge variant="outline" className="text-[10px] bg-violet-500/15 text-violet-400">FIFO</Badge> : "Standard" },
                ]} rows={queues} emptyMsg="No SQS queues" />
              </CardContent>
            </Card>
          </TabsContent>

          {/* EVENTBRIDGE TAB */}
          <TabsContent value="eventbridge">
            <div className="space-y-6">
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Event Buses ({buses.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Bus Name" },
                    { key: "arn", label: "ARN", render: (r) => <span className="truncate max-w-[300px] inline-block text-xs">{r.arn}</span> },
                    { key: "policy", label: "Has Policy", render: (r) => r.policy ? "Yes" : "No" },
                  ]} rows={buses} emptyMsg="No event buses" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Rules ({rules.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Rule" },
                    { key: "state", label: "State", render: (r) => <Badge variant="outline" className={`text-[10px] ${r.state === "ENABLED" ? "bg-emerald-500/15 text-emerald-400" : "bg-zinc-500/15 text-zinc-400"}`}>{r.state}</Badge> },
                    { key: "schedule", label: "Schedule" },
                    { key: "description", label: "Description" },
                  ]} rows={rules} emptyMsg="No rules" />
                </CardContent>
              </Card>
              <Card className="border-zinc-800 bg-zinc-900/60">
                <CardHeader><CardTitle className="text-lg">Archives ({archives.length})</CardTitle></CardHeader>
                <CardContent>
                  <DataTable columns={[
                    { key: "name", label: "Archive" },
                    { key: "state", label: "State", render: (r) => <Badge variant="outline" className="text-[10px]">{r.state}</Badge> },
                    { key: "retention_days", label: "Retention (days)" },
                    { key: "event_count", label: "Events" },
                  ]} rows={archives} emptyMsg="No archives" />
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
