import { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';

interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  tokens?: { input: number; output: number };
  cost?: number;
  durationMs?: number;
  output?: string;
}

interface UsePipelineReturn {
  agents: AgentStatus[];
  status: 'idle' | 'running' | 'complete' | 'error';
  output: string | null;
  totalCost: number | null;
  totalTokens: number | null;
  durationMs: number | null;
  error: string | null;
  runPipeline: (pipelineName: string, agentNames: string[], query: string) => Promise<void>;
  reset: () => void;
}

interface WSEvent {
  type: string;
  pipeline_id: string;
  timestamp: string;
  data: Record<string, unknown>;
}

interface RunResponse {
  pipeline_id: string;
  status: string;
  output: string;
  total_tokens: number;
  total_cost: number;
  duration_ms: number;
  agent_breakdown: unknown;
  ws_url: string;
}

export function usePipeline(): UsePipelineReturn {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [status, setStatus] = useState<'idle' | 'running' | 'complete' | 'error'>('idle');
  const [output, setOutput] = useState<string | null>(null);
  const [totalCost, setTotalCost] = useState<number | null>(null);
  const [totalTokens, setTotalTokens] = useState<number | null>(null);
  const [durationMs, setDurationMs] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const statusRef = useRef<'idle' | 'running' | 'complete' | 'error'>('idle');
  const finishedRef = useRef(false);

  // Keep statusRef in sync
  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  const reset = () => {
    wsRef.current?.close();
    wsRef.current = null;
    setAgents([]);
    setStatus('idle');
    setOutput(null);
    setTotalCost(null);
    setTotalTokens(null);
    setDurationMs(null);
    setError(null);
  };

  const runPipeline = async (pipelineName: string, agentNames: string[], query: string) => {
    // Reset state
    const initialAgents: AgentStatus[] = agentNames.map(name => ({ name, status: 'pending' }));
    setAgents(initialAgents);
    setStatus('running');
    setOutput(null);
    setTotalCost(null);
    setTotalTokens(null);
    setDurationMs(null);
    setError(null);
    statusRef.current = 'running';
    finishedRef.current = false;

    const handleEvent = (event: WSEvent) => {
      if (event.type === 'agent_start') {
        const agentName = event.data.agent as string;
        setAgents(prev =>
          prev.map(a => a.name === agentName ? { ...a, status: 'running' } : a)
        );
      } else if (event.type === 'agent_complete') {
        const agentName = event.data.agent as string;
        const tokensData = event.data.tokens as { input: number; output: number } | undefined;
        setAgents(prev =>
          prev.map(a =>
            a.name === agentName
              ? {
                  ...a,
                  status: 'complete',
                  tokens: tokensData,
                  cost: event.data.cost as number | undefined,
                  durationMs: event.data.duration_ms as number | undefined,
                  output: event.data.output as string | undefined,
                }
              : a
          )
        );
      } else if (event.type === 'complete') {
        finishedRef.current = true;
        setOutput((event.data.output as string) ?? null);
        setTotalCost((event.data.total_cost as number) ?? null);
        setTotalTokens((event.data.total_tokens as number) ?? null);
        setDurationMs((event.data.duration_ms as number) ?? null);
        
        // Update all agents with breakdown data
        const breakdown = event.data.agent_breakdown as Array<{
          agent: string;
          input_tokens: number;
          output_tokens: number;
          cost: number;
        }> | undefined;
        
        if (breakdown) {
          setAgents(prev =>
            prev.map(a => {
              const match = breakdown.find(b => b.agent === a.name);
              return {
                ...a,
                status: 'complete' as const,
                tokens: match ? { input: match.input_tokens, output: match.output_tokens } : a.tokens,
                cost: match ? match.cost : a.cost,
              };
            })
          );
        } else {
          // Mark all agents complete even without breakdown
          setAgents(prev => prev.map(a => ({ ...a, status: 'complete' as const })));
        }
        
        setStatus('complete');
        statusRef.current = 'complete';
      } else if (event.type === 'error') {
        finishedRef.current = true;
        setError((event.data.message as string) ?? 'Unknown error');
        setStatus('error');
        statusRef.current = 'error';
      }
    };

    const handleClose = () => {
      if (statusRef.current === 'running') {
        setError('Connection lost');
        setStatus('error');
        statusRef.current = 'error';
      }
    };

    try {
      // POST now returns immediately with pipeline_id (execution is async)
      const runResponse = await api.post<RunResponse>('/api/v2/pipelines/run', {
        pipeline_name: pipelineName,
        query,
      });

      const pipelineId = runResponse.pipeline_id;

      // Connect WebSocket immediately — backend sends events as agents execute
      const ws = api.connectPipelineWS(pipelineId, handleEvent, handleClose);
      wsRef.current = ws;

      // No fallback needed — all state comes from WebSocket events
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Pipeline failed';
      setError(message);
      setStatus('error');
      statusRef.current = 'error';
    }
  };

  return { agents, status, output, totalCost, totalTokens, durationMs, error, runPipeline, reset };
}
