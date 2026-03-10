import { useState, useEffect, useRef } from 'react';
import { ArrowLeft } from 'lucide-react';
import { api } from '../api/client';
import { usePermits } from '../hooks/usePermits';
import { usePipeline } from '../hooks/usePipeline';
import LeadOpsStats from '../components/leadops/LeadOpsStats';
import PermitFilters from '../components/leadops/PermitFilters';
import PermitTable from '../components/leadops/PermitTable';
import AgentTraceVisualizer from '../components/pipeline/AgentTraceVisualizer';
import QueryInput from '../components/pipeline/QueryInput';

type Tab = 'shovels' | 'skiptrace';

interface PipelineInfo {
  name: string;
  display_name: string;
  description: string;
  agents: Array<{ name: string; goal: string; model: string }>;
  agentNames: string[];
  type: string;
  category: string;
}

export default function LeadOpsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('shovels');
  const [pipelineMap, setPipelineMap] = useState<Record<string, PipelineInfo>>({});
  const [activeQuery, setActiveQuery] = useState('');
  const progressRef = useRef<HTMLDivElement>(null);

  const permits = usePermits();
  const pipeline = usePipeline();

  // Load pipeline info for lead_ops pipelines
  useEffect(() => {
    api.request<{ pipelines: PipelineInfo[] }>('/api/v2/pipelines/list')
      .then(data => {
        const map: Record<string, PipelineInfo> = {};
        for (const p of data.pipelines) {
          const norm = { ...p, agentNames: p.agents.map(a => a.name) };
          if (p.name === 'shovels') map.shovels = norm;
          if (p.name === 'skiptrace') map.skiptrace = norm;
        }
        setPipelineMap(map);
      })
      .catch(console.error);
  }, []);

  // Auto-scroll on agent progress
  useEffect(() => {
    if (pipeline.status === 'running' && progressRef.current) {
      progressRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [pipeline.agents, pipeline.status]);

  const handleRunPipeline = async (pipelineName: string, query: string) => {
    const info = pipelineMap[pipelineName];
    if (!info) return;
    setActiveQuery(query);
    await pipeline.runPipeline(info.name, info.agentNames, query);
    // Refresh permits data after shovels run
    if (pipelineName === 'shovels') {
      setTimeout(() => {
        permits.search();
        permits.loadStats();
      }, 1000);
    }
  };

  const handleBack = () => {
    pipeline.reset();
    setActiveQuery('');
  };

  const isRunning = pipeline.status !== 'idle';
  const activePipelineInfo = activeTab === 'shovels' ? pipelineMap.shovels
    : pipelineMap.skiptrace;

  const tabs: { key: Tab; label: string }[] = [
    { key: 'shovels', label: 'Shovels' },
    { key: 'skiptrace', label: 'Skiptrace' },
  ];

  return (
    <div style={{ padding: '32px', maxWidth: '1100px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        {isRunning && (
          <button onClick={handleBack} style={backBtnStyle}>
            <ArrowLeft style={{ width: 14, height: 14 }} /> Back
          </button>
        )}
        <h1 style={{ color: 'var(--cr-text)', fontSize: 22, fontWeight: 700, margin: 0 }}>
          {isRunning && activePipelineInfo
            ? activePipelineInfo.display_name
            : 'Lead Ops'}
        </h1>
      </div>

      {/* Tabs (only when not running) */}
      {!isRunning && (
        <div style={{ display: 'flex', gap: 0, borderBottom: '2px solid var(--cr-border)', marginBottom: 20 }}>
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              style={{
                padding: '10px 20px', border: 'none', background: 'none',
                fontSize: 14, fontWeight: activeTab === t.key ? 600 : 400,
                color: activeTab === t.key ? 'var(--cr-green-900)' : 'var(--cr-text-secondary)',
                borderBottom: activeTab === t.key ? '2px solid var(--cr-green-900)' : '2px solid transparent',
                marginBottom: -2, cursor: 'pointer', transition: 'all 120ms',
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
      )}

      {/* Running state — show agent trace */}
      {isRunning && (
        <>
          <div style={{ marginBottom: 20 }}>
            <QueryInput onSubmit={() => {}} isRunning readOnly value={activeQuery} />
          </div>
          <div ref={progressRef}>
            <AgentTraceVisualizer
              agents={pipeline.agents.map(a => {
                const pa = activePipelineInfo?.agents.find(x => x.name === a.name);
                return { ...a, model: pa?.model };
              })}
              status={pipeline.status}
              totalCost={pipeline.totalCost ?? undefined}
              totalTokens={pipeline.totalTokens ?? undefined}
              durationMs={pipeline.durationMs ?? undefined}
              output={pipeline.output ?? undefined}
              error={pipeline.error ?? undefined}
            />
          </div>
        </>
      )}

      {/* Shovels Tab */}
      {!isRunning && activeTab === 'shovels' && (
        <>
          <LeadOpsStats stats={permits.stats} loading={permits.statsLoading} />

          {/* Run Ingestion */}
          <div style={{
            marginBottom: 20, padding: 16,
            borderRadius: 'var(--cr-radius-sm)',
            border: '1px solid var(--cr-border)',
            background: 'var(--cr-white)',
          }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--cr-text)', marginBottom: 8 }}>
              Run Permit Ingestion
            </div>
            <QueryInput
              onSubmit={(q) => handleRunPipeline('shovels', q)}
              isRunning={false}
              placeholder="e.g., Ingest 200 recent Chicago permits since 2024-06-01"
            />
          </div>

          {/* Permit Browse */}
          <div style={{
            borderRadius: 'var(--cr-radius-sm)',
            border: '1px solid var(--cr-border)',
            background: 'var(--cr-white)',
            overflow: 'hidden',
          }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--cr-border)' }}>
              <PermitFilters onSearch={permits.search} />
            </div>
            <PermitTable
              permits={permits.permits}
              total={permits.total}
              loading={permits.loading}
              currentPage={permits.currentPage}
              totalPages={permits.totalPages}
              onNextPage={permits.nextPage}
              onPrevPage={permits.prevPage}
            />
          </div>
        </>
      )}

      {/* Skiptrace Tab */}
      {!isRunning && activeTab === 'skiptrace' && (
        <div>
          <div style={{ marginBottom: 16, color: 'var(--cr-text-secondary)', fontSize: 14 }}>
            {pipelineMap.skiptrace?.description ?? 'Multi-agent skip tracing for locating contacts and verifying identities.'}
          </div>
          <QueryInput
            onSubmit={(q) => handleRunPipeline('skiptrace', q)}
            isRunning={false}
            placeholder="e.g., Skip trace John Smith in Chicago, IL"
          />
        </div>
      )}

    </div>
  );
}

const backBtnStyle: React.CSSProperties = {
  display: 'flex', alignItems: 'center', gap: 6,
  background: 'none', border: '1px solid var(--cr-border)',
  borderRadius: 'var(--cr-radius-xs)', padding: '6px 12px',
  color: 'var(--cr-text-muted)', fontSize: 13, cursor: 'pointer',
};
