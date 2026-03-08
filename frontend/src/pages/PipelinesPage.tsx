import { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Brain, Zap } from 'lucide-react';
import { api } from '../api/client';
import AgentTraceVisualizer from '../components/pipeline/AgentTraceVisualizer';
import QueryInput from '../components/pipeline/QueryInput';
import ModelBadge from '../components/pipeline/ModelBadge';

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
  agentNames: string[];
  type: string;
  estimated_cost?: number;
}

const SAMPLE_QUERIES: Record<string, string> = {
  'lex-intelligence-ultimate': 'Research and draft a legal opinion on force majeure clauses in commercial lease agreements during public health emergencies',
  'calculus-intelligence': 'Analyze the financial viability of a $50M mixed-use development in downtown Atlanta with 200 residential units and 30,000 sq ft retail',
  'forge-intelligence': 'Generate a Python FastAPI microservice for real-time portfolio risk monitoring with WebSocket streaming',
  'lead-ranking-engine': 'Score and rank the top 50 commercial mortgage leads maturing in Q2 2026 with LTV above 70%',
  'underwriting-engine': 'Underwrite a $25M bridge loan for a 150-unit multifamily acquisition in Nashville with 85% occupancy',
  'due-diligence-engine': 'Conduct full due diligence on Apex Capital Partners for a $100M fund investment including litigation and regulatory checks',
  'portfolio-monitoring-engine': 'Run covenant compliance check across all active CMBS loans and flag any early warning signals',
  'investor-reporting-engine': 'Generate Q4 2025 investor report for Fund III including IRR waterfall, asset-level performance, and market commentary',
  'skip-trace-engine': 'Locate current contact information and business affiliations for the principals of Sterling Development Group LLC',
  'financial-strategy-analyst': 'Synthesize a market outlook for CRE lending in 2026 with interest rate scenarios, cap rate forecasts, and sector-level risk assessment',
};

export default function PipelinesPage() {
  const [pipelines, setPipelines] = useState<PipelineInfo[]>([]);
  const [hoveredPipeline, setHoveredPipeline] = useState<PipelineInfo | null>(null);
  const [selectedPipeline, setSelectedPipeline] = useState<PipelineInfo | null>(null);
  const [activeQuery, setActiveQuery] = useState('');
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

  useEffect(() => {
    if (status === 'running' && progressRef.current) {
      progressRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [agents, status]);

  const handleSelectAndRun = (p: PipelineInfo) => {
    setSelectedPipeline(p);
    const sample = SAMPLE_QUERIES[p.name] || `Analyze using ${p.display_name}`;
    setActiveQuery(sample);
    runPipeline(p.name, p.agents.map(a => a.name), sample);
  };

  const handleBack = () => {
    reset();
    setActiveQuery('');
    setSelectedPipeline(null);
  };

  const isRunning = status !== 'idle';

  // The pipeline to show in the detail panel
  const detailPipeline = isRunning ? selectedPipeline : (hoveredPipeline || selectedPipeline);

  return (
    <div className="page-bg bg-datacenter" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 12,
        padding: '16px 24px', borderBottom: '1px solid var(--cr-border)',
        background: 'var(--cr-panel)', flexShrink: 0,
      }}>
        {isRunning && (
          <button onClick={handleBack} style={{
            display: 'flex', alignItems: 'center', gap: 6,
            background: 'none', border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius-xs)', padding: '6px 12px',
            color: 'var(--cr-text-muted)', fontSize: 13, cursor: 'pointer',
          }}>
            <ArrowLeft style={{ width: 14, height: 14 }} /> Back
          </button>
        )}
        <h1 style={{
          color: 'var(--cr-text)', fontSize: 22, fontWeight: 700, margin: 0,
          fontFamily: "'Space Grotesk', sans-serif",
        }}>
          {isRunning && selectedPipeline ? selectedPipeline.display_name : 'Intelligence Engines'}
        </h1>
      </div>

      {/* Body: 2-column layout */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left column: engine list */}
        <div style={{
          width: 340, flexShrink: 0, borderRight: '1px solid var(--cr-border)',
          overflowY: 'auto', background: 'var(--cr-panel)',
        }}>
          {pipelines.map(p => {
            const isHovered = hoveredPipeline?.name === p.name;
            const isSelected = selectedPipeline?.name === p.name;
            const isActive = isHovered || isSelected;
            return (
              <div
                key={p.name}
                onMouseEnter={() => { if (!isRunning) setHoveredPipeline(p); }}
                onMouseLeave={() => { if (!isRunning) setHoveredPipeline(null); }}
                onClick={() => {
                  if (!isRunning) setSelectedPipeline(p);
                }}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: 10,
                  padding: '14px 16px',
                  borderLeft: `3px solid ${isActive ? 'var(--cr-green-600)' : 'transparent'}`,
                  background: isActive ? 'var(--cr-green-50)' : 'transparent',
                  cursor: 'pointer',
                  borderBottom: '1px solid var(--cr-border)',
                  transition: 'all 150ms',
                }}
              >
                <Brain style={{
                  width: 18, height: 18, flexShrink: 0, marginTop: 1,
                  color: isActive ? 'var(--cr-green-600)' : 'var(--cr-muted)',
                }} />
                <div style={{ minWidth: 0 }}>
                  <div style={{
                    fontSize: 14, fontWeight: 600,
                    color: isActive ? 'var(--cr-green-900)' : 'var(--cr-text)',
                    marginBottom: 2,
                  }}>
                    {p.display_name}
                  </div>
                  <div style={{
                    fontSize: 12, color: 'var(--cr-muted)',
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }}>
                    {p.agents.length} agents &middot; {p.description.slice(0, 60)}...
                  </div>
                </div>
              </div>
            );
          })}
          {pipelines.length === 0 && (
            <div style={{ padding: 24, color: 'var(--cr-muted)', fontSize: 13 }}>Loading engines...</div>
          )}
        </div>

        {/* Right column: detail / execution panel */}
        <div style={{ flex: 1, position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {!isRunning ? (
            /* Browse / preview mode */
            <div style={{ flex: 1, position: 'relative', overflow: 'auto' }}>
              {detailPipeline ? (
                /* Engine detail overlay */
                <div style={{
                  position: 'relative', zIndex: 1,
                  padding: 32, minHeight: '100%',
                }}>
                  <div style={{
                    background: 'rgba(255,255,255,0.88)',
                    borderRadius: 'var(--cr-radius)',
                    border: '1px solid var(--cr-border)',
                    padding: '28px 24px',
                    backdropFilter: 'blur(8px)',
                  }}>
                    {/* Title */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                      <Brain style={{ width: 24, height: 24, color: 'var(--cr-green-600)' }} />
                      <h2 style={{
                        fontSize: 22, fontWeight: 700, color: 'var(--cr-text)', margin: 0,
                        fontFamily: "'Space Grotesk', sans-serif",
                      }}>
                        {detailPipeline.display_name}
                      </h2>
                    </div>

                    {/* Description */}
                    <p style={{
                      fontSize: 14, lineHeight: 1.6, color: 'var(--cr-text-secondary)',
                      margin: '0 0 20px',
                    }}>
                      {detailPipeline.description}
                    </p>

                    {/* Agents */}
                    <div style={{ marginBottom: 20 }}>
                      <div style={{
                        fontSize: 11, fontWeight: 600, color: 'var(--cr-muted)',
                        textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10,
                      }}>
                        Agent Pipeline ({detailPipeline.agents.length} agents)
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {detailPipeline.agents.map((agent, i) => (
                          <div key={agent.name} style={{
                            display: 'flex', alignItems: 'flex-start', gap: 10,
                            padding: '10px 12px',
                            background: 'var(--cr-panel2)',
                            borderRadius: 'var(--cr-radius-sm)',
                            border: '1px solid var(--cr-border)',
                          }}>
                            <div style={{
                              width: 22, height: 22, borderRadius: '50%',
                              background: 'var(--cr-green-600)', color: '#fff',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontSize: 11, fontWeight: 700, flexShrink: 0,
                            }}>
                              {i + 1}
                            </div>
                            <div style={{ minWidth: 0, flex: 1 }}>
                              <div style={{
                                display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3,
                              }}>
                                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--cr-text)' }}>
                                  {agent.name}
                                </span>
                                <ModelBadge model={agent.model} />
                              </div>
                              <div style={{ fontSize: 12, color: 'var(--cr-muted)', lineHeight: 1.4 }}>
                                {agent.goal}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Sample query */}
                    {SAMPLE_QUERIES[detailPipeline.name] && (
                      <div style={{ marginBottom: 20 }}>
                        <div style={{
                          fontSize: 11, fontWeight: 600, color: 'var(--cr-muted)',
                          textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6,
                        }}>
                          Sample Query
                        </div>
                        <div style={{
                          fontSize: 13, color: 'var(--cr-text-secondary)', lineHeight: 1.5,
                          padding: '10px 14px', background: 'var(--cr-panel2)',
                          borderRadius: 'var(--cr-radius-sm)',
                          border: '1px solid var(--cr-border)',
                          fontStyle: 'italic',
                        }}>
                          "{SAMPLE_QUERIES[detailPipeline.name]}"
                        </div>
                      </div>
                    )}

                    {/* Footer: cost + run button */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      {detailPipeline.estimated_cost != null && (
                        <span style={{ fontSize: 13, color: 'var(--cr-gold-500)', fontWeight: 600 }}>
                          ~${detailPipeline.estimated_cost.toFixed(3)} est.
                        </span>
                      )}
                      <button
                        onClick={() => handleSelectAndRun(detailPipeline)}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 8,
                          padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)',
                          background: 'var(--cr-green-900)', color: '#fff', border: 'none',
                          fontSize: 14, fontWeight: 600, cursor: 'pointer',
                          transition: 'background 150ms',
                        }}
                      >
                        <Zap style={{ width: 16, height: 16 }} />
                        Run Pipeline
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                /* Empty state */
                <div style={{
                  position: 'relative', zIndex: 1,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  height: '100%',
                }}>
                  <div style={{
                    textAlign: 'center',
                    background: 'rgba(255,255,255,0.7)',
                    padding: '32px 40px', borderRadius: 'var(--cr-radius)',
                    backdropFilter: 'blur(4px)',
                  }}>
                    <Brain style={{ width: 32, height: 32, color: 'var(--cr-muted)', marginBottom: 12 }} />
                    <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--cr-text)', marginBottom: 4 }}>
                      Select an Engine
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--cr-muted)' }}>
                      Hover over an engine to preview its agents and capabilities
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Execution mode */
            <div style={{ flex: 1, overflow: 'auto', padding: 24 }}>
              <div style={{ marginBottom: 20 }}>
                <QueryInput onSubmit={() => {}} isRunning={true} readOnly value={activeQuery} />
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
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
