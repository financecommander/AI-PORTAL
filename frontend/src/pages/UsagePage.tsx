import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { UsageLog, PipelineRun } from '../types';
import StatsCards from '../components/usage/StatsCards';
import CostChart from '../components/usage/CostChart';
import UsageTable from '../components/usage/UsageTable';

function buildChartData(logs: UsageLog[]): { date: string; cost: number; count: number }[] {
  const days: { date: string; cost: number; count: number }[] = [];
  const now = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    days.push({
      date: d.toLocaleDateString('en-US', { weekday: 'short' }),
      cost: 0,
      count: 0,
    });
  }
  logs.forEach((log) => {
    const logDate = new Date(log.timestamp);
    const diffDays = Math.floor((now.getTime() - logDate.getTime()) / 86400000);
    const idx = 6 - diffDays;
    if (idx >= 0 && idx < 7) {
      days[idx].cost += log.cost_usd;
      days[idx].count += 1;
    }
  });
  return days;
}

function SkeletonBlock({ height = 80 }: { height?: number }) {
  return (
    <div
      style={{
        height,
        background: 'var(--navy-light)',
        borderRadius: 12,
        animation: 'pulse 1.5s ease-in-out infinite',
      }}
    />
  );
}

export default function UsagePage() {
  const [logs, setLogs] = useState<UsageLog[]>([]);
  const [pipelines, setPipelines] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'pipeline'>('chat');

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [logsRes, pipelinesRes] = await Promise.all([
        api.request<{ logs: UsageLog[] }>('/usage/logs?limit=50'),
        api.request<{ runs: PipelineRun[] }>('/usage/pipelines?limit=20'),
      ]);
      setLogs(logsRes.logs ?? []);
      setPipelines(pipelinesRes.runs ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load usage data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const chartData = buildChartData(logs);

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: '8px 18px',
    background: 'none',
    border: 'none',
    borderBottom: active ? '2px solid var(--blue)' : '2px solid transparent',
    color: active ? '#FFFFFF' : '#8899AA',
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: active ? 600 : 400,
    marginRight: 4,
  });

  // Convert pipeline runs to UsageLog-like rows for the table
  const pipelineLogs: UsageLog[] = pipelines.map((p, i) => ({
    id: i,
    user_hash: '',
    timestamp: p.created_at ?? '',
    provider: p.pipeline_name ?? 'pipeline',
    model: p.pipeline_name ?? p.pipeline_id,
    input_tokens: p.total_tokens ?? 0,
    output_tokens: 0,
    cost_usd: p.total_cost ?? 0,
    latency_ms: p.duration_ms ?? 0,
    specialist_id: p.query?.slice(0, 40),
  }));

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Usage &amp; Costs</h1>

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            {[1, 2, 3, 4].map((k) => <SkeletonBlock key={k} height={80} />)}
          </div>
          <SkeletonBlock height={180} />
          <SkeletonBlock height={200} />
        </div>
      )}

      {!loading && error && (
        <div style={{ color: 'var(--red)', marginBottom: 16 }}>
          {error}
          <button
            onClick={fetchData}
            style={{
              marginLeft: 12,
              padding: '6px 14px',
              background: 'var(--navy)',
              border: '1px solid var(--navy-light)',
              color: '#E0E0E0',
              borderRadius: 6,
              cursor: 'pointer',
              fontSize: 13,
            }}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <StatsCards logs={logs} />
          <CostChart data={chartData} />

          <div>
            <div style={{ borderBottom: '1px solid var(--navy-light)', marginBottom: 16 }}>
              <button style={tabStyle(activeTab === 'chat')} onClick={() => setActiveTab('chat')}>
                Chat Logs
              </button>
              <button style={tabStyle(activeTab === 'pipeline')} onClick={() => setActiveTab('pipeline')}>
                Pipeline Runs
              </button>
            </div>
            <UsageTable logs={activeTab === 'chat' ? logs : pipelineLogs} />
          </div>
        </div>
      )}
    </div>
  );
}
