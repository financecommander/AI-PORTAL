/**
 * Blueprint Editor API Client
 *
 * Handles REST communication with AI-PORTAL backend for Blueprint sessions,
 * and with the Swarm Mainframe for execution.
 */

import type {
  BlueprintSession,
  CreateBlueprintRequest,
  BlueprintValidationResult,
  BlueprintExecutionStatus,
  BlueprintGraph,
  TritonModel,
} from '../types/blueprint';

const API_BASE = '/api/v2/blueprint';
const SWARM_BASE = '/swarm';

class BlueprintClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  private async request<T>(base: string, path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${base}${path}`, {
      ...options,
      headers: { ...this.headers(), ...(options.headers as Record<string, string> || {}) },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || err.error || `Request failed: ${res.status}`);
    }
    return res.json();
  }

  // ── Session CRUD ────────────────────────────────────────────────

  async listSessions(): Promise<BlueprintSession[]> {
    return this.request<BlueprintSession[]>(API_BASE, '/sessions');
  }

  async getSession(sessionId: string): Promise<BlueprintSession> {
    return this.request<BlueprintSession>(API_BASE, `/sessions/${sessionId}`);
  }

  async createSession(req: CreateBlueprintRequest): Promise<BlueprintSession> {
    return this.request<BlueprintSession>(API_BASE, '/sessions', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  }

  async updateSession(sessionId: string, data: Partial<CreateBlueprintRequest> & { orc_source?: string; graph?: BlueprintGraph }): Promise<BlueprintSession> {
    return this.request<BlueprintSession>(API_BASE, `/sessions/${sessionId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.request<void>(API_BASE, `/sessions/${sessionId}`, { method: 'DELETE' });
  }

  // ── Parse / Generate / Validate ─────────────────────────────────

  async parseOrc(source: string): Promise<BlueprintGraph> {
    return this.request<BlueprintGraph>(API_BASE, '/parse', {
      method: 'POST',
      body: JSON.stringify({ source }),
    });
  }

  async generateOrc(graph: BlueprintGraph): Promise<{ source: string }> {
    return this.request<{ source: string }>(API_BASE, '/generate', {
      method: 'POST',
      body: JSON.stringify(graph),
    });
  }

  async validateOrc(source: string): Promise<BlueprintValidationResult> {
    return this.request<BlueprintValidationResult>(API_BASE, '/validate', {
      method: 'POST',
      body: JSON.stringify({ source }),
    });
  }

  // ── Execution (via Swarm Mainframe) ─────────────────────────────

  async executeBlueprint(sessionId: string): Promise<BlueprintExecutionStatus> {
    return this.request<BlueprintExecutionStatus>(SWARM_BASE, `/api/v1/blueprint/${sessionId}/execute`, {
      method: 'POST',
    });
  }

  async getExecutionStatus(executionId: string): Promise<BlueprintExecutionStatus> {
    return this.request<BlueprintExecutionStatus>(SWARM_BASE, `/api/v1/blueprint/executions/${executionId}`);
  }

  // ── Triton Models ───────────────────────────────────────────────

  async listTritonModels(): Promise<TritonModel[]> {
    return this.request<TritonModel[]>(API_BASE, '/models');
  }
}

export const blueprintApi = new BlueprintClient();
