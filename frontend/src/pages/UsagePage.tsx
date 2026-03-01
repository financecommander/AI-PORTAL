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
    days.push({ date: d.toLocaleDateString('en-US', { weekday: 'short' }), cost: 0, count: 0 });
  }
  logs.forEach((log) => {
    const parsed = new Date(log.timestamp).getTime();
    const diffDays = Math.floor((now.getTime() - parsed) / 86400000);
    const idx = 6 - diffDays;
    if (idx >= 0 && idx < 7) { days[idx].cost += log.cost_usd; days[idx].count += 1; }
  });
  return days;
}

export default function UsagePage() {
  const [logs, setLogs] = useState<UsageLog[]>([]);
  const [pipelines, setPipelines] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'pipeline'>('chat');

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [logsRes, pipelinesRes] = await Promise.all([
        api.request<{ logs: UsageLog[] }>('/usage/logs?limit=50'),
        api.request<{ runs: PipelineRun[] }>('/usage/pipelines?limit=20'),
      ]);
      setLogs(logsRes.logs ?? []); setPipelines(pipelinesRes.runs ?? []);
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed to load usage data'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const chartData = buildChartData(logs);

  const pipelineLogs: UsageLog[] = pipelines.map((p, i) => ({
    id: i, user_hash: '', timestamp: p.created_at ?? '', provider: p.pipeline_name ?? 'pipeline',
    model: p.pipeline_name ?? p.pipeline_id, input_tokens: p.total_tokens ?? 0, output_tokens: 0,
    cost_usd: p.total_cost ?? 0, latency_ms: p.duration_ms ?? 0, specialist_id: p.query?.slice(0, 40),
  }));

  return (
    <div style={{ padding: '28px 32px' }}>
      <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 22, fontWeight: 700, color: 'var(--cr-text)', marginBottom: 24 }}>
        Intelligence Metrics
      </h1>

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            {[1,2,3,4].map((k) => <div key={k} style={{ height: 80, background: 'var(--cr-surface-2)', borderRadius: 'var(--cr-radius)', animation: 'subtlePulse 1.5s ease-in-out infinite' }} />)}
          </div>
          <div style={{ height: 180, background: 'var(--cr-surface-2)', borderRadius: 'var(--cr-radius)' }} />
        </div>
      )}

      {!loading && error && (
        <div style={{ color: 'var(--cr-danger)', marginBottom: 16, fontSize: 14 }}>
          {error}
          <button onClick={fetchData} style={{ marginLeft: 12, padding: '6px 14px', background: 'var(--cr-white)', border: '1px solid var(--cr-border)', color: 'var(--cr-text-secondary)', borderRadius: 'var(--cr-radius-sm)', cursor: 'pointer', fontSize: 13 }}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <StatsCards logs={logs} />
          <CostChart data={chartData} />
          <div>
            <div style={{ borderBottom: '1px solid var(--cr-border)', marginBottom: 16, display: 'flex', gap: 4 }}>
              {(['chat', 'pipeline'] as const).map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)} style={{
                  padding: '8px 18px', background: 'none', border: 'none',
                  borderBottom: activeTab === tab ? '2px solid var(--cr-green-900)' : '2px solid transparent',
                  color: activeTab === tab ? 'var(--cr-text)' : 'var(--cr-text-muted)',
                  cursor: 'pointer', fontSize: 13, fontWeight: activeTab === tab ? 600 : 400,
                }}>
                  {tab === 'chat' ? 'Console Logs' : 'Engine Runs'}
                </button>
              ))}
            </div>
            <UsageTable logs={activeTab === 'chat' ? logs : pipelineLogs} />
          </div>
        </div>
      )}
    </div>
  );
}

