/**
 * Swarm Mainframe API Client
 *
 * Handles REST and WebSocket communication with the Swarm Mainframe.
 * In dev: Vite proxies /swarm → SWARM_URL (default http://localhost:8080)
 * In prod: nginx proxies /swarm → swarm-mainframe:8080
 */

import type {
  SwarmSession,
  SessionDetail,
  CreateSessionRequest,
  RoundResponse,
  TeamPresets,
  SwarmWSEvent,
} from '../types/swarm';

const SWARM_BASE = '/swarm';

class SwarmClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${SWARM_BASE}${path}`, {
      ...options,
      headers: { ...this.headers(), ...(options.headers as Record<string, string> || {}) },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || err.error || `Request failed: ${res.status}`);
    }
    return res.json();
  }

  // ── Sessions ────────────────────────────────────────────────────

  async listSessions(status?: string): Promise<SwarmSession[]> {
    const query = status ? `?status=${status}` : '';
    return this.request<SwarmSession[]>(`/api/v1/sessions${query}`);
  }

  async getSession(sessionId: string): Promise<SessionDetail> {
    return this.request<SessionDetail>(`/api/v1/sessions/${sessionId}`);
  }

  async createSession(req: CreateSessionRequest): Promise<SwarmSession> {
    return this.request<SwarmSession>('/api/v1/sessions', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async sendMessage(sessionId: string, content: string): Promise<RoundResponse> {
    return this.request<RoundResponse>(`/api/v1/sessions/${sessionId}/message`, {
      method: 'POST',
      body: JSON.stringify({ content, role: 'human' }),
    });
  }

  async pauseSession(sessionId: string): Promise<SwarmSession> {
    return this.request<SwarmSession>(`/api/v1/sessions/${sessionId}/pause`, { method: 'POST' });
  }

  async resumeSession(sessionId: string): Promise<SwarmSession> {
    return this.request<SwarmSession>(`/api/v1/sessions/${sessionId}/resume`, { method: 'POST' });
  }

  async completeSession(sessionId: string): Promise<SwarmSession> {
    return this.request<SwarmSession>(`/api/v1/sessions/${sessionId}/complete`, { method: 'POST' });
  }

  async getPresets(): Promise<TeamPresets> {
    return this.request<TeamPresets>('/api/v1/sessions/presets');
  }

  // ── Health ──────────────────────────────────────────────────────

  async getHealth(): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>('/health');
  }

  // ── WebSocket ───────────────────────────────────────────────────

  connectSessionWS(
    sessionId: string,
    onEvent: (event: SwarmWSEvent) => void,
    onClose?: () => void,
  ): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}${SWARM_BASE}/ws/sessions/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      if (this.token) {
        try {
          ws.send(JSON.stringify({ type: 'auth', token: this.token }));
        } catch (err) {
          console.error('Failed to send auth token:', err);
          onClose?.();
        }
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onEvent(data);
      } catch (err) {
        console.warn('Invalid WebSocket message:', err);
      }
    };

    ws.onerror = () => onClose?.();
    ws.onclose = () => onClose?.();
    return ws;
  }
}

export const swarmApi = new SwarmClient();
