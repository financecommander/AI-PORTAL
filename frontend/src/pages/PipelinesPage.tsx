import { useState, useEffect, useRef } from 'react';
import { ArrowLeft } from 'lucide-react';
import { api } from '../api/client';
import PipelineCard from '../components/pipeline/PipelineCard';
import AgentTraceVisualizer from '../components/pipeline/AgentTraceVisualizer';
import QueryInput from '../components/pipeline/QueryInput';
import { usePipeline } from '../hooks/usePipeline';

interface PipelineInfo {
  name: string;
  display_name: string;
  description: string;
  agents: Array<{
    name: string;
    goal: string;
    backstory: string;
    model: string;
  }>;
  agentNames: string[]; // For display components
  type: string;
  estimated_cost?: number;
}

export default function PipelinesPage() {
  const [pipelines, setPipelines] = useState<PipelineInfo[]>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<PipelineInfo | null>(null);
  const [activeQuery, setActiveQuery] = useState<string>('');
  const progressRef = useRef<HTMLDivElement>(null);

  const { agents, status, output, totalCost, totalTokens, durationMs, error, runPipeline, reset } =
    usePipeline();

  useEffect(() => {
    api.request<{ pipelines: PipelineInfo[] }>('/api/v2/pipelines/list')
      .then(data => {
        const normalized = data.pipelines.map(p => ({
          ...p,
          agentNames: p.agents.map(a => a.name),
        }));
        setPipelines(normalized);
      })
      .catch(console.error);
  }, []);

  // Auto-scroll to running agent
  useEffect(() => {
    if (status === 'running' && progressRef.current) {
      progressRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [agents, status]);

  const handleRun = async (query: string) => {
    if (!selectedPipeline) return;
    setActiveQuery(query);
    await runPipeline(selectedPipeline.name, selectedPipeline.agents.map(a => a.name), query);
  };

  const handleBack = () => {
    reset();
    setActiveQuery('');
  };

  const isRunning = status !== 'idle';

  return (
    <div style={{ padding: '32px', maxWidth: '900px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        {isRunning && (
          <button
            onClick={handleBack}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'none',
              border: '1px solid #2A3A5C',
              borderRadius: '6px',
              padding: '6px 12px',
              color: '#8899AA',
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'color 150ms',
            }}
          >
            <ArrowLeft style={{ width: 14, height: 14 }} />
            Back
          </button>
        )}
        <h1 style={{ color: 'white', fontSize: '22px', fontWeight: 700, margin: 0 }}>
          {isRunning && selectedPipeline
            ? selectedPipeline.display_name
            : 'Intelligence Pipelines'}
        </h1>
      </div>

      {/* Pipeline Selection (idle state) */}
      {!isRunning && (
        <>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
              gap: '16px',
              marginBottom: '24px',
            }}
          >
            {pipelines.map(p => (
              <PipelineCard
                key={p.name}
                pipeline={{
                  ...p,
                  agents: p.agentNames,
                }}
                isSelected={selectedPipeline?.name === p.name}
                onSelect={name => {
                  const found = pipelines.find(pl => pl.name === name) ?? null;
                  setSelectedPipeline(found);
                }}
              />
            ))}
            {pipelines.length === 0 && (
              <p style={{ color: '#667788' }}>Loading pipelines...</p>
            )}
          </div>

          {selectedPipeline && (
            <QueryInput
              onSubmit={handleRun}
              isRunning={false}
              estimatedCost={selectedPipeline.estimated_cost}
            />
          )}
        </>
      )}

      {/* Execution state */}
      {isRunning && (
        <>
          <div style={{ marginBottom: '20px' }}>
            <QueryInput
              onSubmit={() => {}}
              isRunning={true}
              readOnly
              value={activeQuery}
            />
          </div>

          <div ref={progressRef}>
            <AgentTraceVisualizer
              agents={agents.map(a => {
                const pipelineAgent = selectedPipeline?.agents.find(pa => pa.name === a.name);
                return { ...a, model: pipelineAgent?.model };
              })}
              status={status}
              totalCost={totalCost ?? undefined}
              totalTokens={totalTokens ?? undefined}
              durationMs={durationMs ?? undefined}
              output={output ?? undefined}
              error={error ?? undefined}
            />
          </div>
        </>
      )}
    </div>
  );
}
