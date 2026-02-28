const BASE_URL = '';  // Uses Vite proxy in dev

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  getToken(): string | null {
    return this.token;
  }

  async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${BASE_URL}${path}`, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (response.status === 401) {
      this.token = null;
      localStorage.removeItem('fc_token');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || error.detail || 'Request failed');
    }

    return response.json();
  }

  async post<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: 'POST', body });
  }

  async put<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>(path, { method: 'PUT', body });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }

  async streamChat(
    specialistId: string,
    message: string,
    history: Array<{ role: string; content: string }>,
    onChunk: (chunk: { content: string; is_final: boolean; input_tokens: number; output_tokens: number; cost_usd: number }) => void,
  ): Promise<void> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;

    const response = await fetch(`${BASE_URL}/chat/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        specialist_id: specialistId,
        message,
        conversation_history: history,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ error: 'Stream failed' }));
      throw new Error(err.error || err.detail || 'Stream failed');
    }
    if (!response.body) throw new Error('No response body');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onChunk(data);
          } catch { /* skip malformed */ }
        }
      }
    }
  }

  connectPipelineWS(
    pipelineId: string,
    onEvent: (event: { type: string; pipeline_id: string; timestamp: string; data: Record<string, unknown> }) => void,
    onClose?: () => void,
  ): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v2/pipelines/ws/${pipelineId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      // Authenticate via first message instead of query param (avoids token in URL/logs)
      ws.send(JSON.stringify({ type: 'auth', token: this.token }));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onEvent(data);
      } catch { /* skip */ }
    };

    ws.onerror = () => onClose?.();
    ws.onclose = () => onClose?.();
    return ws;
  }
}

export const api = new ApiClient();
