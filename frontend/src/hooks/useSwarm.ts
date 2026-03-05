import { useState, useRef, useEffect, useCallback } from 'react';
import { swarmApi } from '../api/swarmClient';
import type {
  SwarmSession,
  SessionDetail,
  SessionMessage,
  CreateSessionRequest,
  RoundResponse,
  TeamPresets,
  SwarmWSEvent,
} from '../types/swarm';

interface SwarmHealth {
  status: string;
  uptime?: number;
  [key: string]: unknown;
}

interface UseSwarmReturn {
  // State
  sessions: SwarmSession[];
  selectedSession: SessionDetail | null;
  presets: TeamPresets;
  health: SwarmHealth | null;
  loading: boolean;
  sending: boolean;
  error: string | null;
  connected: boolean;

  // Actions
  refreshSessions: () => Promise<void>;
  selectSession: (sessionId: string) => Promise<void>;
  deselectSession: () => void;
  createSession: (req: CreateSessionRequest) => Promise<SwarmSession>;
  sendMessage: (content: string) => Promise<RoundResponse | null>;
  pauseSession: () => Promise<void>;
  resumeSession: () => Promise<void>;
  completeSession: () => Promise<void>;
  loadPresets: () => Promise<void>;
}

export function useSwarm(): UseSwarmReturn {
  const [sessions, setSessions] = useState<SwarmSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<SessionDetail | null>(null);
  const [presets, setPresets] = useState<TeamPresets>({});
  const [health, setHealth] = useState<SwarmHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Sync auth token from main API client ─────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('fc_token');
    swarmApi.setToken(token);
  }, []);

  // ── Poll health every 30s ─────────────────────────────────────────
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const h = await swarmApi.getHealth();
        setHealth(h as SwarmHealth);
        setConnected(true);
      } catch {
        setHealth(null);
        setConnected(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30_000);
    return () => clearInterval(interval);
  }, []);

  // ── Refresh sessions list ─────────────────────────────────────────
  const refreshSessions = useCallback(async () => {
    try {
      setLoading(true);
      const list = await swarmApi.listSessions();
      setSessions(Array.isArray(list) ? list : []);
      setError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load sessions';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  // ── Initial load + polling ────────────────────────────────────────
  useEffect(() => {
    refreshSessions();
    pollRef.current = setInterval(refreshSessions, 15_000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [refreshSessions]);

  // ── Cleanup WS on unmount ─────────────────────────────────────────
  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  // ── Select a session (load detail + connect WS) ───────────────────
  const selectSession = useCallback(async (sessionId: string) => {
    try {
      setLoading(true);
      const detail = await swarmApi.getSession(sessionId);
      setSelectedSession(detail);
      setError(null);

      // Connect WebSocket for live updates
      wsRef.current?.close();
      const ws = swarmApi.connectSessionWS(
        sessionId,
        (event: SwarmWSEvent) => {
          // Guard against events from a previous session after rapid switching
          if (event.session_id && event.session_id !== sessionId) return;

          if (event.type === 'new_message') {
            const msg = event.data as unknown as SessionMessage;
            setSelectedSession(prev => {
              if (!prev) return prev;
              return {
                ...prev,
                messages: [...(prev.messages || []), msg],
                message_count: prev.message_count + 1,
                total_cost: prev.total_cost + (msg.cost || 0),
              };
            });
          } else if (event.type === 'session_update') {
            setSelectedSession(prev => {
              if (!prev) return prev;
              return { ...prev, ...(event.data as Partial<SessionDetail>) };
            });
          }
        },
        () => { /* ws closed */ },
      );
      wsRef.current = ws;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load session';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const deselectSession = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setSelectedSession(null);
  }, []);

  // ── Create session ────────────────────────────────────────────────
  const createSession = useCallback(async (req: CreateSessionRequest): Promise<SwarmSession> => {
    const session = await swarmApi.createSession(req);
    await refreshSessions();
    return session;
  }, [refreshSessions]);

  // ── Send message ──────────────────────────────────────────────────
  const sendMessage = useCallback(async (content: string): Promise<RoundResponse | null> => {
    if (!selectedSession) return null;
    try {
      setSending(true);
      const result = await swarmApi.sendMessage(selectedSession.session_id, content);

      // Merge new messages into state
      setSelectedSession(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          messages: [...prev.messages, ...result.messages],
          current_round: result.round_number,
          total_cost: result.total_cost,
          message_count: prev.message_count + result.response_count + 1,
        };
      });

      return result;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to send message';
      setError(msg);
      return null;
    } finally {
      setSending(false);
    }
  }, [selectedSession]);

  // ── Lifecycle ─────────────────────────────────────────────────────
  const pauseSession = useCallback(async () => {
    if (!selectedSession) return;
    await swarmApi.pauseSession(selectedSession.session_id);
    setSelectedSession(prev => prev ? { ...prev, status: 'paused' } : prev);
    await refreshSessions();
  }, [selectedSession, refreshSessions]);

  const resumeSession = useCallback(async () => {
    if (!selectedSession) return;
    await swarmApi.resumeSession(selectedSession.session_id);
    setSelectedSession(prev => prev ? { ...prev, status: 'active' } : prev);
    await refreshSessions();
  }, [selectedSession, refreshSessions]);

  const completeSession = useCallback(async () => {
    if (!selectedSession) return;
    await swarmApi.completeSession(selectedSession.session_id);
    setSelectedSession(prev => prev ? { ...prev, status: 'completed' } : prev);
    await refreshSessions();
  }, [selectedSession, refreshSessions]);

  // ── Load presets ──────────────────────────────────────────────────
  const loadPresets = useCallback(async () => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw: any = await swarmApi.getPresets();
      // API returns {presets: {name: {castes: [...], descriptions: {...}}}}
      // Unwrap to {name: string[]}
      const source = raw.presets ?? raw;
      const flat: Record<string, string[]> = {};
      for (const [key, val] of Object.entries(source)) {
        if (Array.isArray(val)) {
          flat[key] = val;
        } else if (val && typeof val === 'object' && 'castes' in (val as object)) {
          flat[key] = (val as { castes: string[] }).castes;
        }
      }
      if (Object.keys(flat).length > 0) {
        setPresets(flat);
        return;
      }
      throw new Error('Empty presets after parsing');
    } catch (err) {
      console.warn('Failed to load presets from API, using defaults:', err);
      setPresets({
        code: ['hydra_code', 'guardian_claude', 'ultra_reasoning'],
        finance: ['hydra_financial', 'ultra_reasoning', 'guardian_claude'],
        research: ['ultra_research', 'guardian_claude', 'ultra_reasoning'],
        legal: ['mutalisk_legal', 'hydra_compliance', 'guardian_claude'],
        marketing: ['hydra_marketing', 'mutalisk_conversational', 'guardian_claude'],
        ops: ['nydus', 'hydra_code', 'guardian_claude'],
        full: ['guardian_claude', 'hydra_code', 'hydra_financial', 'ultra_reasoning', 'mutalisk_legal'],
      });
    }
  }, []);

  return {
    sessions,
    selectedSession,
    presets,
    health,
    loading,
    sending,
    error,
    connected,
    refreshSessions,
    selectSession,
    deselectSession,
    createSession,
    sendMessage,
    pauseSession,
    resumeSession,
    completeSession,
    loadPresets,
  };
}
