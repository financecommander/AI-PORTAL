import { useState, useEffect, useCallback } from 'react';
import { blueprintApi } from '../api/blueprintClient';
import type {
  BlueprintSession,
  CreateBlueprintRequest,
  BlueprintValidationResult,
  BlueprintExecutionStatus,
  BlueprintGraph,
  TritonModel,
} from '../types/blueprint';

interface UseBlueprintReturn {
  sessions: BlueprintSession[];
  activeSession: BlueprintSession | null;
  models: TritonModel[];
  loading: boolean;
  saving: boolean;
  error: string | null;
  validation: BlueprintValidationResult | null;
  execution: BlueprintExecutionStatus | null;

  refreshSessions: () => Promise<void>;
  selectSession: (sessionId: string) => Promise<void>;
  deselectSession: () => void;
  createSession: (req: CreateBlueprintRequest) => Promise<BlueprintSession>;
  updateOrcSource: (source: string) => Promise<void>;
  updateGraph: (graph: BlueprintGraph) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  parseOrc: (source: string) => Promise<BlueprintGraph | null>;
  generateOrc: (graph: BlueprintGraph) => Promise<string | null>;
  validate: (source: string) => Promise<BlueprintValidationResult>;
  execute: () => Promise<void>;
  loadModels: () => Promise<void>;
}

export function useBlueprint(): UseBlueprintReturn {
  const [sessions, setSessions] = useState<BlueprintSession[]>([]);
  const [activeSession, setActiveSession] = useState<BlueprintSession | null>(null);
  const [models, setModels] = useState<TritonModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validation, setValidation] = useState<BlueprintValidationResult | null>(null);
  const [execution, setExecution] = useState<BlueprintExecutionStatus | null>(null);

  // Sync auth token
  useEffect(() => {
    const token = localStorage.getItem('fc_token');
    blueprintApi.setToken(token);
  }, []);

  const refreshSessions = useCallback(async () => {
    try {
      setLoading(true);
      const list = await blueprintApi.listSessions();
      setSessions(list);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refreshSessions(); }, [refreshSessions]);

  const selectSession = useCallback(async (sessionId: string) => {
    try {
      setLoading(true);
      const session = await blueprintApi.getSession(sessionId);
      setActiveSession(session);
      setValidation(null);
      setExecution(null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load session');
    } finally {
      setLoading(false);
    }
  }, []);

  const deselectSession = useCallback(() => {
    setActiveSession(null);
    setValidation(null);
    setExecution(null);
  }, []);

  const createSession = useCallback(async (req: CreateBlueprintRequest) => {
    const session = await blueprintApi.createSession(req);
    setSessions(prev => [session, ...prev]);
    setActiveSession(session);
    return session;
  }, []);

  const updateOrcSource = useCallback(async (source: string) => {
    if (!activeSession) return;
    setSaving(true);
    try {
      const updated = await blueprintApi.updateSession(activeSession.session_id, { orc_source: source });
      setActiveSession(updated);
      setSessions(prev => prev.map(s => s.session_id === updated.session_id ? updated : s));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  }, [activeSession]);

  const updateGraph = useCallback(async (graph: BlueprintGraph) => {
    if (!activeSession) return;
    setSaving(true);
    try {
      const updated = await blueprintApi.updateSession(activeSession.session_id, { graph });
      setActiveSession(updated);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to save graph');
    } finally {
      setSaving(false);
    }
  }, [activeSession]);

  const deleteSession = useCallback(async (sessionId: string) => {
    await blueprintApi.deleteSession(sessionId);
    setSessions(prev => prev.filter(s => s.session_id !== sessionId));
    if (activeSession?.session_id === sessionId) {
      setActiveSession(null);
    }
  }, [activeSession]);

  const parseOrc = useCallback(async (source: string) => {
    try {
      return await blueprintApi.parseOrc(source);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Parse failed');
      return null;
    }
  }, []);

  const generateOrc = useCallback(async (graph: BlueprintGraph) => {
    try {
      const result = await blueprintApi.generateOrc(graph);
      return result.source;
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Generate failed');
      return null;
    }
  }, []);

  const validate = useCallback(async (source: string) => {
    const result = await blueprintApi.validateOrc(source);
    setValidation(result);
    return result;
  }, []);

  const execute = useCallback(async () => {
    if (!activeSession) return;
    try {
      const status = await blueprintApi.executeBlueprint(activeSession.session_id);
      setExecution(status);
      // Poll for completion
      const poll = setInterval(async () => {
        try {
          const updated = await blueprintApi.getExecutionStatus(status.execution_id);
          setExecution(updated);
          if (updated.status === 'completed' || updated.status === 'failed') {
            clearInterval(poll);
          }
        } catch {
          clearInterval(poll);
        }
      }, 2000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Execution failed');
    }
  }, [activeSession]);

  const loadModels = useCallback(async () => {
    try {
      const m = await blueprintApi.listTritonModels();
      setModels(m);
    } catch {
      // Non-critical — models are supplementary
    }
  }, []);

  return {
    sessions, activeSession, models, loading, saving, error, validation, execution,
    refreshSessions, selectSession, deselectSession, createSession,
    updateOrcSource, updateGraph, deleteSession,
    parseOrc, generateOrc, validate, execute, loadModels,
  };
}
