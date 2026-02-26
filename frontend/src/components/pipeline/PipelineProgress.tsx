import AgentProgressCard from './AgentProgressCard';

interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  tokens?: { input: number; output: number };
  cost?: number;
  durationMs?: number;
  output?: string;
}

interface PipelineProgressProps {
  agents: AgentStatus[];
  status: 'idle' | 'running' | 'complete' | 'error';
  totalCost?: number;
  totalTokens?: number;
  durationMs?: number;
  output?: string;
  error?: string;
}

export default function PipelineProgress({
  agents,
  status,
  totalCost,
  totalTokens,
  durationMs,
  output,
  error,
}: PipelineProgressProps) {
  const completedCount = agents.filter(a => a.status === 'complete').length;
  const runningIndex = agents.findIndex(a => a.status === 'running');
  const currentIndex = runningIndex >= 0 ? runningIndex : completedCount;
  const progressPct = agents.length > 0 ? (completedCount / agents.length) * 100 : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
      {/* Progress summary bar */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ color: '#8899AA', fontSize: '13px' }}>
            {status === 'complete'
              ? 'All agents complete'
              : status === 'error'
              ? 'Pipeline failed'
              : `Agent ${currentIndex + 1} / ${agents.length}`}
          </span>
          <span style={{ color: '#8899AA', fontSize: '13px' }}>{Math.round(progressPct)}%</span>
        </div>
        <div
          style={{
            height: '3px',
            background: 'var(--navy)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              background: status === 'error' ? 'var(--red)' : 'var(--blue)',
              width: `${progressPct}%`,
              transition: 'width 400ms ease',
              borderRadius: '2px',
            }}
          />
        </div>
      </div>

      {/* Agent cards */}
      <div>
        {agents.map((agent, i) => (
          <AgentProgressCard
            key={agent.name}
            name={agent.name}
            status={agent.status}
            index={i}
            totalAgents={agents.length}
            tokens={agent.tokens}
            cost={agent.cost}
            durationMs={agent.durationMs}
            output={agent.output}
          />
        ))}
      </div>

      {/* Error message */}
      {status === 'error' && error && (
        <div
          style={{
            marginTop: '16px',
            background: 'var(--navy)',
            borderLeft: '4px solid var(--red)',
            borderRadius: '8px',
            padding: '14px 16px',
          }}
        >
          <p style={{ color: 'var(--red)', fontSize: '13px', margin: 0, fontWeight: 500 }}>Error</p>
          <p style={{ color: '#8899AA', fontSize: '13px', margin: '4px 0 0 0' }}>{error}</p>
        </div>
      )}

      {/* Completion summary */}
      {status === 'complete' && (
        <div
          style={{
            marginTop: '16px',
            background: 'var(--navy)',
            borderLeft: '4px solid var(--green)',
            borderRadius: '8px',
            padding: '14px 16px',
          }}
        >
          <p style={{ color: 'var(--green)', fontSize: '13px', margin: '0 0 8px 0', fontWeight: 500 }}>
            Pipeline Complete
          </p>
          <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
            {totalCost != null && (
              <div>
                <span style={{ color: '#556677', fontSize: '11px', display: 'block' }}>Total Cost</span>
                <span style={{ color: 'white', fontSize: '15px', fontWeight: 600 }}>${totalCost.toFixed(4)}</span>
              </div>
            )}
            {totalTokens != null && (
              <div>
                <span style={{ color: '#556677', fontSize: '11px', display: 'block' }}>Total Tokens</span>
                <span style={{ color: 'white', fontSize: '15px', fontWeight: 600 }}>{totalTokens.toLocaleString()}</span>
              </div>
            )}
            {durationMs != null && (
              <div>
                <span style={{ color: '#556677', fontSize: '11px', display: 'block' }}>Duration</span>
                <span style={{ color: 'white', fontSize: '15px', fontWeight: 600 }}>
                  {(durationMs / 1000).toFixed(1)}s
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Final output */}
      {status === 'complete' && output && (
        <div
          style={{
            marginTop: '12px',
            background: 'var(--navy)',
            borderRadius: '8px',
            padding: '16px',
          }}
        >
          <p style={{ color: '#8899AA', fontSize: '12px', margin: '0 0 8px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Final Output
          </p>
          <p style={{ color: '#D0D8E8', fontSize: '14px', margin: 0, whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {output}
          </p>
        </div>
      )}
    </div>
  );
}
