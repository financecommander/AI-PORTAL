import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { UsageLog, PipelineRun } from '../types';
import StatsCards from '../components/usage/StatsCards';
import CostChart from '../components/usage/CostChart';
import UsageTable from '../components/usage/UsageTable';

interface DistillationStats {
  total_turns: number;
  unexported_count: number;
  by_provider: Record<string, number>;
  by_source: Record<string, number>;
}

interface DistillationReadiness {
  total_turns: number;
  exportable: number;
  recommended_min: number;
  ready: boolean;
}

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

function SkeletonBlock({ height = 80 }: { height?: number }) {
  return (
    <div
      style={{
        height,
        background: 'var(--cr-surface-2)',
        borderRadius: 12,
        animation: 'subtlePulse 1.5s ease-in-out infinite',
      }}
    />
  );
}

function TrainingDataTab() {
  const [stats, setStats] = useState<DistillationStats | null>(null);
  const [readiness, setReadiness] = useState<DistillationReadiness | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [s, r] = await Promise.all([
          api.request<DistillationStats>('/distillation/stats'),
          api.request<DistillationReadiness>('/distillation/readiness'),
        ]);
        setStats(s);
        setReadiness(r);
      } catch {
        // silently handle -- stats are optional
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleExport = async () => {
    setExporting(true);
    try {
      const token = api.getToken();
      const res = await fetch('/distillation/export?format=alpaca&min_output_tokens=50', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'training_data.jsonl';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert('Failed to export training data');
    } finally {
      setExporting(false);
    }
  };

  if (loading) return <SkeletonBlock height={200} />;

  const progress = readiness
    ? Math.min(100, Math.round((readiness.exportable / readiness.recommended_min) * 100))
    : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Readiness indicator */}
      <div style={{
        background: 'var(--cr-surface)',
        borderRadius: 12,
        padding: 20,
        border: '1px solid var(--cr-border)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <span style={{ color: 'var(--cr-text)', fontWeight: 600, fontSize: 15 }}>Fine-Tuning Readiness</span>
          <span style={{
            padding: '4px 12px',
            borderRadius: 20,
            fontSize: 12,
            fontWeight: 600,
            background: readiness?.ready ? 'rgba(34,197,94,0.15)' : 'rgba(234,179,8,0.15)',
            color: readiness?.ready ? '#22c55e' : '#eab308',
          }}>
            {readiness?.ready ? 'Ready' : 'Collecting Data'}
          </span>
        </div>
        <div style={{
          background: 'var(--cr-surface-2)',
          borderRadius: 8,
          height: 8,
          overflow: 'hidden',
          marginBottom: 8,
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            background: readiness?.ready ? '#22c55e' : 'var(--cr-green-600)',
            borderRadius: 8,
            transition: 'width 0.5s ease',
          }} />
        </div>
        <div style={{ color: 'var(--cr-text-muted)', fontSize: 13 }}>
          {readiness?.exportable ?? 0} / {readiness?.recommended_min ?? 5000} quality turns ({progress}%)
        </div>
      </div>

      {/* Stats breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div style={{
          background: 'var(--cr-surface)',
          borderRadius: 12,
          padding: 16,
          border: '1px solid var(--cr-border)',
        }}>
          <div style={{ color: 'var(--cr-text-muted)', fontSize: 12, marginBottom: 8 }}>By Provider</div>
          {stats?.by_provider && Object.entries(stats.by_provider).map(([provider, count]) => (
            <div key={provider} style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--cr-text-secondary)', fontSize: 13, marginBottom: 4 }}>
              <span>{provider}</span>
              <span style={{ color: 'var(--cr-text)', fontWeight: 500 }}>{count}</span>
            </div>
          ))}
          {(!stats?.by_provider || Object.keys(stats.by_provider).length === 0) && (
            <div style={{ color: 'var(--cr-text-muted)', fontSize: 13 }}>No data yet</div>
          )}
        </div>
        <div style={{
          background: 'var(--cr-surface)',
          borderRadius: 12,
          padding: 16,
          border: '1px solid var(--cr-border)',
        }}>
          <div style={{ color: 'var(--cr-text-muted)', fontSize: 12, marginBottom: 8 }}>By Source</div>
          {stats?.by_source && Object.entries(stats.by_source).map(([source, count]) => (
            <div key={source} style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--cr-text-secondary)', fontSize: 13, marginBottom: 4 }}>
              <span>{source}</span>
              <span style={{ color: 'var(--cr-text)', fontWeight: 500 }}>{count}</span>
            </div>
          ))}
          {(!stats?.by_source || Object.keys(stats.by_source).length === 0) && (
            <div style={{ color: 'var(--cr-text-muted)', fontSize: 13 }}>No data yet</div>
          )}
        </div>
      </div>

      {/* Summary + export */}
      <div style={{
        background: 'var(--cr-surface)',
        borderRadius: 12,
        padding: 16,
        border: '1px solid var(--cr-border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div>
          <div style={{ color: 'var(--cr-text)', fontWeight: 600, fontSize: 15 }}>
            {stats?.total_turns ?? 0} Total Turns
          </div>
          <div style={{ color: 'var(--cr-text-muted)', fontSize: 13 }}>
            {stats?.unexported_count ?? 0} not yet exported
          </div>
        </div>
        <button
          onClick={handleExport}
          disabled={exporting || !stats?.total_turns}
          style={{
            padding: '8px 20px',
            background: stats?.total_turns ? 'var(--cr-green-600)' : 'var(--cr-surface-2)',
            border: 'none',
            borderRadius: 8,
            color: '#FFFFFF',
            fontWeight: 600,
            fontSize: 13,
            cursor: stats?.total_turns ? 'pointer' : 'not-allowed',
            opacity: exporting ? 0.6 : 1,
          }}
        >
          {exporting ? 'Exporting...' : 'Export JSONL'}
        </button>
      </div>
    </div>
  );
}


export default function UsagePage() {
  const [logs, setLogs] = useState<UsageLog[]>([]);
  const [pipelines, setPipelines] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'pipeline' | 'training'>('chat');

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
    <div className="tech-grid-bg" style={{ padding: '28px 32px', minHeight: '100vh' }}>
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
          <button onClick={fetchData} style={{ marginLeft: 12, padding: '6px 14px', background: 'var(--cr-panel)', border: '1px solid var(--cr-border)', color: 'var(--cr-text-secondary)', borderRadius: 'var(--cr-radius-sm)', cursor: 'pointer', fontSize: 13 }}>
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
              {(['chat', 'pipeline', 'training'] as const).map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)} style={{
                  padding: '8px 18px', background: 'none', border: 'none',
                  borderBottom: activeTab === tab ? '2px solid var(--cr-green-900)' : '2px solid transparent',
                  color: activeTab === tab ? 'var(--cr-text)' : 'var(--cr-text-muted)',
                  cursor: 'pointer', fontSize: 13, fontWeight: activeTab === tab ? 600 : 400,
                }}>
                  {tab === 'chat' ? 'Console Logs' : tab === 'pipeline' ? 'Engine Runs' : 'Training Data'}
                </button>
              ))}
            </div>
            {activeTab === 'training' ? (
              <TrainingDataTab />
            ) : (
              <UsageTable logs={activeTab === 'chat' ? logs : pipelineLogs} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

