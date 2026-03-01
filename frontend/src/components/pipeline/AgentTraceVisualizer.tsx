import { useState, useEffect, useMemo } from 'react';
import { Check, X, ChevronDown, ChevronUp, Clock, Zap, DollarSign, Hash } from 'lucide-react';
import ModelBadge from './ModelBadge';

interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  tokens?: { input: number; output: number };
  cost?: number;
  durationMs?: number;
  output?: string;
  model?: string;
}

interface AgentTraceVisualizerProps {
  agents: AgentStatus[];
  status: 'idle' | 'running' | 'complete' | 'error';
  totalCost?: number;
  totalTokens?: number;
  durationMs?: number;
  output?: string;
  error?: string;
}

export default function AgentTraceVisualizer({
  agents,
  status,
  totalCost,
  totalTokens,
  durationMs,
  output,
  error,
}: AgentTraceVisualizerProps) {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const [outputExpanded, setOutputExpanded] = useState(false);
  const [runningDots, setRunningDots] = useState(1);

  // Animate running dots
  useEffect(() => {
    if (status !== 'running') return;
    const interval = setInterval(() => {
      setRunningDots(prev => (prev % 3) + 1);
    }, 500);
    return () => clearInterval(interval);
  }, [status]);

  // Calculate max duration for scaling duration bars
  const maxDuration = useMemo(() => {
    const durations = agents
      .filter(a => a.status === 'complete' && a.durationMs)
      .map(a => a.durationMs!);
    return durations.length > 0 ? Math.max(...durations) : 1;
  }, [agents]);

  const completedCount = agents.filter(a => a.status === 'complete').length;
  const runningAgent = agents.find(a => a.status === 'running');

  const toggleAgentExpansion = (agentName: string) => {
    setExpandedAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentName)) {
        newSet.delete(agentName);
      } else {
        newSet.add(agentName);
      }
      return newSet;
    });
  };

  const getStatusColor = (agentStatus: string) => {
    switch (agentStatus) {
      case 'complete': return 'var(--cr-green-600)';
      case 'error': return 'var(--cr-danger)';
      case 'running': return 'var(--cr-green-600)';
      default: return 'var(--cr-text-dim)';
    }
  };

  const getStatusNode = (agent: AgentStatus, index: number) => {
    const isRunning = agent.status === 'running';
    const isComplete = agent.status === 'complete';
    const isError = agent.status === 'error';

    return (
      <div
        style={{
          width: '28px',
          height: '28px',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 'bold',
          color: agent.status === 'pending' ? 'var(--cr-text-muted)' : 'var(--cr-text)',
          backgroundColor: isComplete ? 'var(--cr-green-600)' : isError ? 'var(--cr-danger)' : 'transparent',
          border: agent.status === 'pending'
            ? '2px dashed var(--cr-charcoal-deep)'
            : isRunning
              ? '2px solid var(--cr-green-600)'
              : 'none',
          animation: isRunning ? 'animate-pulse-glow' : 'none',
          position: 'relative',
          zIndex: 2,
        }}
      >
        {isComplete && <Check size={14} />}
        {isError && <X size={14} />}
        {agent.status === 'pending' && (index + 1)}
        {isRunning && (index + 1)}
      </div>
    );
  };

  const getConnectorLine = (agent: AgentStatus) => {
    if (agent === agents[agents.length - 1]) return null;

    return (
      <div
        style={{
          width: '2px',
          height: '8px',
          backgroundColor: getStatusColor(agent.status),
          margin: '4px auto 0',
          borderRadius: '1px',
        }}
      />
    );
  };

  const getDurationBar = (durationMs: number) => {
    const percentage = (durationMs / maxDuration) * 100;
    const seconds = (durationMs / 1000).toFixed(1);

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
        <div
          style={{
            width: '80px',
            height: '4px',
            backgroundColor: 'var(--cr-charcoal-deep)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${percentage}%`,
              height: '100%',
              backgroundColor: 'var(--cr-gold-500)',
              borderRadius: '2px',
              transition: 'width 0.3s ease',
            }}
          />
        </div>
        <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>{seconds}s</span>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header bar */}
      <div
        style={{
          backgroundColor: 'var(--cr-charcoal-deep)',
          borderRadius: '10px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: status === 'complete'
                ? 'var(--cr-green-600)'
                : status === 'error'
                  ? 'var(--cr-danger)'
                  : 'var(--cr-green-600)',
              animation: status === 'running' ? 'animate-pulse-glow' : 'none',
            }}
          />
          <span style={{ color: 'var(--cr-text)', fontSize: '14px', fontWeight: '500' }}>
            {status === 'complete'
              ? 'Pipeline Complete'
              : status === 'error'
                ? 'Pipeline Failed'
                : runningAgent
                  ? `Running: ${runningAgent.name}`
                  : 'Initializing...'}
          </span>
        </div>
        <span style={{ color: 'var(--cr-text-muted)', fontSize: '13px' }}>
          {completedCount} / {agents.length} agents
        </span>
      </div>

      {/* Progress rail */}
      <div
        style={{
          height: '2px',
          backgroundColor: 'var(--cr-charcoal-deep)',
          borderRadius: '1px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${agents.length > 0 ? (completedCount / agents.length) * 100 : 0}%`,
            background: 'linear-gradient(90deg, var(--cr-green-600), var(--cr-green-400))',
            transition: 'width 0.5s ease',
          }}
        />
      </div>

      {/* Agent trace rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {agents.map((agent, index) => (
          <div key={agent.name} style={{ position: 'relative' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                padding: '12px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
                border: agent.status === 'running' ? '1px solid var(--cr-green-600)' : '1px solid transparent',
              }}
            >
              {getStatusNode(agent, index)}

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--cr-text)', fontSize: '14px', fontWeight: '500' }}>
                    {agent.name}
                  </span>
                  {agent.model && <ModelBadge model={agent.model} />}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                  <span
                    style={{
                      fontSize: '12px',
                      color: agent.status === 'error'
                        ? 'var(--cr-danger)'
                        : agent.status === 'running'
                          ? 'var(--cr-green-400)'
                          : 'var(--cr-text-muted)',
                    }}
                  >
                    {agent.status === 'pending' && 'Waiting'}
                    {agent.status === 'running' && `Processing${'.'.repeat(runningDots)}`}
                    {agent.status === 'error' && 'Failed'}
                    {agent.status === 'complete' && 'Complete'}
                  </span>

                  {agent.status === 'complete' && agent.durationMs && getDurationBar(agent.durationMs)}

                  {agent.status === 'complete' && agent.tokens && (
                    <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>
                      {(agent.tokens.input + agent.tokens.output).toLocaleString()} tok
                    </span>
                  )}

                  {agent.status === 'complete' && agent.cost !== undefined && (
                    <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>
                      ${agent.cost.toFixed(4)}
                    </span>
                  )}

                  {agent.status === 'complete' && agent.output && (
                    <button
                      onClick={() => toggleAgentExpansion(agent.name)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--cr-text-muted)',
                        cursor: 'pointer',
                        padding: '2px',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      {expandedAgents.has(agent.name) ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  )}
                </div>

                {agent.status === 'complete' && agent.output && expandedAgents.has(agent.name) && (
                  <div
                    style={{
                      marginTop: '8px',
                      padding: '8px',
                      backgroundColor: 'var(--cr-charcoal-dark)',
                      borderRadius: '6px',
                      borderLeft: '3px solid var(--cr-green-600)',
                      maxHeight: '250px',
                      overflowY: 'auto',
                    }}
                  >
                    <pre
                      style={{
                        margin: 0,
                        fontSize: '12px',
                        color: 'var(--cr-text-muted)',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {agent.output}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {getConnectorLine(agent)}
          </div>
        ))}
      </div>

      {/* Error block */}
      {status === 'error' && error && (
        <div
          style={{
            padding: '12px',
            backgroundColor: 'rgba(192, 57, 43, 0.1)',
            borderRadius: '8px',
            borderLeft: '4px solid var(--cr-danger)',
          }}
        >
          <div style={{ color: 'var(--cr-danger)', fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
            Error
          </div>
          <div style={{ color: 'var(--cr-text)', fontSize: '13px' }}>{error}</div>
        </div>
      )}

      {/* Completion summary */}
      {status === 'complete' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
            gap: '8px',
          }}
        >
          {totalCost !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(45, 139, 78, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <DollarSign size={16} color="var(--cr-green-600)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Total Cost</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  ${totalCost.toFixed(4)}
                </div>
              </div>
            </div>
          )}

          {totalTokens !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(46, 117, 182, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Hash size={16} color="var(--cr-green-600)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Total Tokens</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  {totalTokens.toLocaleString()}
                </div>
              </div>
            </div>
          )}

          {durationMs !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(212, 118, 10, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Clock size={16} color="var(--cr-gold-500)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Duration</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  {(durationMs / 1000).toFixed(1)}s
                </div>
              </div>
            </div>
          )}

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px',
              backgroundColor: 'var(--cr-charcoal-deep)',
              borderRadius: '8px',
            }}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '6px',
                backgroundColor: 'rgba(46, 117, 182, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Zap size={16} color="var(--cr-green-600)" />
            </div>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Agents</div>
              <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                {completedCount} / {agents.length}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Final output block */}
      {status === 'complete' && output && (
        <div
          style={{
            backgroundColor: 'var(--cr-charcoal-deep)',
            borderRadius: '8px',
            overflow: 'hidden',
          }}
        >
          <button
            onClick={() => setOutputExpanded(!outputExpanded)}
            style={{
              width: '100%',
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              color: 'var(--cr-text)',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '14px',
              fontWeight: '500',
            }}
          >
            FINAL OUTPUT
            {outputExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {outputExpanded && (
            <div
              style={{
                padding: '0 16px 16px',
                borderTop: '1px solid var(--cr-charcoal-deep)',
              }}
            >
              <pre
                style={{
                  margin: 0,
                  fontSize: '13px',
                  color: 'var(--cr-text-muted)',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  lineHeight: '1.5',
                }}
              >
                {output}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
