# 🤖 AGENT DIRECTIVE — Phase 3A: React Frontend Scaffold + Auth

## Build the React 19 frontend for FinanceCommander AI Portal v2.0

**Repository:** `financecommander/AI-PORTAL`
**Base Branch:** `develop`
**Target Directory:** `frontend/` (new — does not exist yet)
**PR Target:** `develop` (NOT main)

---

## CONTEXT

The FastAPI backend is complete on `develop` branch at `backend/`. This directive creates the React frontend from scratch in `frontend/`. The backend API surface is:

```
POST   /auth/login                  → { access_token, token_type }
GET    /specialists/                → { specialists: [...] }
GET    /specialists/{id}            → specialist object
POST   /specialists/                → create specialist
PUT    /specialists/{id}            → update specialist
DELETE /specialists/{id}            → { deleted: true }
POST   /chat/send                   → { content, model, input_tokens, output_tokens, latency_ms, cost_usd }
POST   /chat/stream                 → SSE stream of { content, is_final, input_tokens, output_tokens, cost_usd }
GET    /api/v2/pipelines/list       → { pipelines: [...] }
POST   /api/v2/pipelines/run        → { pipeline_id }
WS     /api/v2/pipelines/ws/{id}    → WebSocket events { type, pipeline_id, timestamp, data }
GET    /usage/logs                   → { logs: [...] }
GET    /usage/pipelines              → { runs: [...] }
GET    /health                       → { status, version }
```

All authenticated endpoints require `Authorization: Bearer <jwt>` header.
Login accepts `{ email: "user@financecommander.com" }` and returns a JWT.

---

## STEP 0: Initialize Vite + React Project

```bash
cd /workspaces/AI-PORTAL
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install react-router-dom@6 lucide-react clsx
npm install -D tailwindcss @tailwindcss/vite
```

## STEP 1: Tailwind Configuration

**`frontend/vite.config.ts`**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/specialists': 'http://localhost:8000',
      '/api': 'http://localhost:8000',
      '/usage': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})
```

**`frontend/src/index.css`** — replace entire file:
```css
@import "tailwindcss";

:root {
  --navy: #1B2A4A;
  --navy-light: #243656;
  --navy-dark: #111D35;
  --blue: #2E75B6;
  --blue-light: #4A9ADE;
  --green: #2D8B4E;
  --orange: #D4760A;
  --red: #C0392B;
  --sidebar-width: 280px;
}

body {
  margin: 0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background-color: var(--navy-dark);
  color: #E8E8E8;
}

/* Scrollbar styling */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--navy-dark); }
::-webkit-scrollbar-thumb { background: var(--navy-light); border-radius: 3px; }
```

## STEP 2: API Client Layer

**`frontend/src/api/client.ts`**
```typescript
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

    if (!response.ok) throw new Error('Stream failed');
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
    const wsUrl = `${protocol}//${window.location.host}/api/v2/pipelines/ws/${pipelineId}?token=${this.token}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onEvent(data);
      } catch { /* skip */ }
    };

    ws.onclose = () => onClose?.();
    return ws;
  }
}

export const api = new ApiClient();
```

## STEP 3: TypeScript Types

**`frontend/src/types/index.ts`**
```typescript
export interface Specialist {
  id: string;
  name: string;
  description: string;
  provider: string;
  model: string;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
  version: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  tokens?: { input: number; output: number };
  cost_usd?: number;
  latency_ms?: number;
}

export interface ChatResponse {
  content: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  cost_usd: number;
}

export interface Pipeline {
  name: string;
  description: string;
  agents: string[];
  estimated_cost: number;
}

export interface PipelineAgent {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  input_tokens?: number;
  output_tokens?: number;
  cost_usd?: number;
  duration_ms?: number;
  output?: string;
}

export interface PipelineRun {
  pipeline_id: string;
  status: 'running' | 'complete' | 'error';
  agents: PipelineAgent[];
  query: string;
  output?: string;
  total_cost?: number;
  total_tokens?: number;
}

export interface UsageLog {
  id: number;
  user_hash: string;
  timestamp: string;
  provider: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number;
  specialist_id?: string;
}
```

## STEP 4: Auth Context

**`frontend/src/contexts/AuthContext.tsx`**
```tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '../api/client';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('fc_token');
    if (token) {
      api.setToken(token);
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string) => {
    setError(null);
    try {
      const response = await api.post<{ access_token: string }>('/auth/login', { email });
      api.setToken(response.access_token);
      localStorage.setItem('fc_token', response.access_token);
      setIsAuthenticated(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    }
  };

  const logout = () => {
    api.setToken(null);
    localStorage.removeItem('fc_token');
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

## STEP 5: Login Page

**`frontend/src/pages/LoginPage.tsx`**
```tsx
import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email);
      navigate('/');
    } catch {
      // error is set in context
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--navy-dark)' }}>
      <div className="w-full max-w-md p-8 rounded-2xl shadow-2xl" style={{ background: 'var(--navy)' }}>
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
               style={{ background: 'var(--blue)', opacity: 0.9 }}>
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">FinanceCommander</h1>
          <p className="text-sm mt-1" style={{ color: '#8899AA' }}>AI Intelligence Portal v2.0</p>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-3 rounded-lg mb-4 text-sm"
               style={{ background: 'rgba(192, 57, 43, 0.15)', color: '#E74C3C' }}>
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <label className="block text-sm font-medium mb-2" style={{ color: '#8899AA' }}>
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@financecommander.com"
            required
            className="w-full px-4 py-3 rounded-lg text-white text-sm outline-none transition-all
                       focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
            style={{ background: 'var(--navy-dark)', border: '1px solid #2A3A5C' }}
          />
          <p className="text-xs mt-2" style={{ color: '#667788' }}>
            Domain-restricted access: @financecommander.com only
          </p>

          <button
            type="submit"
            disabled={loading || !email}
            className="w-full mt-6 py-3 rounded-lg text-white font-semibold text-sm transition-all
                       disabled:opacity-50 disabled:cursor-not-allowed hover:brightness-110"
            style={{ background: 'var(--blue)' }}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* Footer */}
        <p className="text-center text-xs mt-6" style={{ color: '#556677' }}>
          Calculus Holdings LLC &middot; Secured with JWT authentication
        </p>
      </div>
    </div>
  );
}
```

## STEP 6: Layout Shell + Sidebar

**`frontend/src/components/Sidebar.tsx`**
```tsx
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  MessageSquare, Brain, BarChart3, Settings, LogOut, ChevronRight
} from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { to: '/', icon: MessageSquare, label: 'Chat' },
  { to: '/pipelines', icon: Brain, label: 'Intelligence Pipelines' },
  { to: '/usage', icon: BarChart3, label: 'Usage & Costs' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside
      className="fixed left-0 top-0 h-screen flex flex-col z-50"
      style={{ width: 'var(--sidebar-width)', background: 'var(--navy)' }}
    >
      {/* Logo */}
      <div className="px-5 py-5 border-b" style={{ borderColor: '#2A3A5C' }}>
        <h1 className="text-lg font-bold text-white tracking-tight">FinanceCommander</h1>
        <p className="text-xs mt-0.5" style={{ color: '#667788' }}>AI Portal v2.0</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all group',
              isActive
                ? 'text-white font-medium'
                : 'hover:text-white'
            )}
            style={({ isActive }) => ({
              background: isActive ? 'var(--navy-light)' : 'transparent',
              color: isActive ? '#FFFFFF' : '#8899AA',
            })}
          >
            <Icon className="w-5 h-5 shrink-0" />
            <span className="flex-1">{label}</span>
            <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-50 transition-opacity" />
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="px-3 py-4 border-t" style={{ borderColor: '#2A3A5C' }}>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm w-full transition-all hover:text-white"
          style={{ color: '#8899AA' }}
        >
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
```

**`frontend/src/components/Layout.tsx`**
```tsx
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from './Sidebar';

export default function Layout() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--navy-dark)' }}>
        <div className="text-white text-lg">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen" style={{ background: 'var(--navy-dark)' }}>
      <Sidebar />
      <main className="min-h-screen" style={{ marginLeft: 'var(--sidebar-width)' }}>
        <Outlet />
      </main>
    </div>
  );
}
```

## STEP 7: Stub Pages

**`frontend/src/pages/ChatPage.tsx`**
```tsx
import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Specialist } from '../types';

export default function ChatPage() {
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [selected, setSelected] = useState<Specialist | null>(null);

  useEffect(() => {
    api.request<{ specialists: Specialist[] }>('/specialists/')
      .then(data => {
        setSpecialists(data.specialists);
        if (data.specialists.length > 0) setSelected(data.specialists[0]);
      })
      .catch(console.error);
  }, []);

  return (
    <div className="flex h-screen">
      {/* Specialist selector */}
      <div className="w-64 p-4 border-r overflow-y-auto" style={{ borderColor: '#2A3A5C' }}>
        <h2 className="text-sm font-semibold text-white mb-3">Specialists</h2>
        {specialists.map(s => (
          <button
            key={s.id}
            onClick={() => setSelected(s)}
            className="w-full text-left px-3 py-2.5 rounded-lg text-sm mb-1 transition-all"
            style={{
              background: selected?.id === s.id ? 'var(--navy-light)' : 'transparent',
              color: selected?.id === s.id ? '#FFFFFF' : '#8899AA',
            }}
          >
            <div className="font-medium">{s.name}</div>
            <div className="text-xs mt-0.5 opacity-60">{s.provider} / {s.model}</div>
          </button>
        ))}
      </div>

      {/* Chat area — Phase 3B will implement full chat interface */}
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        {selected ? (
          <div className="text-center">
            <h2 className="text-xl font-bold text-white mb-2">{selected.name}</h2>
            <p className="text-sm" style={{ color: '#8899AA' }}>{selected.description}</p>
            <p className="text-xs mt-4" style={{ color: '#556677' }}>
              Chat interface coming in Phase 3B
            </p>
          </div>
        ) : (
          <p style={{ color: '#667788' }}>Select a specialist to begin</p>
        )}
      </div>
    </div>
  );
}
```

**`frontend/src/pages/PipelinesPage.tsx`**
```tsx
import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Brain } from 'lucide-react';

interface Pipeline {
  name: string;
  description: string;
  agents: string[];
}

export default function PipelinesPage() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);

  useEffect(() => {
    api.request<{ pipelines: Pipeline[] }>('/api/v2/pipelines/list')
      .then(data => setPipelines(data.pipelines))
      .catch(console.error);
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Intelligence Pipelines</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {pipelines.map(p => (
          <div key={p.name} className="p-5 rounded-xl" style={{ background: 'var(--navy)' }}>
            <div className="flex items-center gap-3 mb-3">
              <Brain className="w-5 h-5" style={{ color: 'var(--blue)' }} />
              <h3 className="font-semibold text-white">{p.name}</h3>
            </div>
            <p className="text-sm mb-3" style={{ color: '#8899AA' }}>{p.description}</p>
            <div className="flex flex-wrap gap-1">
              {p.agents.map(a => (
                <span key={a} className="px-2 py-0.5 rounded text-xs"
                      style={{ background: 'var(--navy-dark)', color: '#8899AA' }}>
                  {a}
                </span>
              ))}
            </div>
            <p className="text-xs mt-3" style={{ color: '#556677' }}>
              Pipeline execution coming in Phase 3C
            </p>
          </div>
        ))}
        {pipelines.length === 0 && (
          <p style={{ color: '#667788' }}>Loading pipelines...</p>
        )}
      </div>
    </div>
  );
}
```

**`frontend/src/pages/UsagePage.tsx`**
```tsx
export default function UsagePage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Usage & Costs</h1>
      <p style={{ color: '#667788' }}>Usage dashboard coming in Phase 3C</p>
    </div>
  );
}
```

**`frontend/src/pages/SettingsPage.tsx`**
```tsx
export default function SettingsPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>
      <p style={{ color: '#667788' }}>Settings page coming in Phase 3D</p>
    </div>
  );
}
```

## STEP 8: App Router

**`frontend/src/App.tsx`** — replace entire file:
```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import PipelinesPage from './pages/PipelinesPage';
import UsagePage from './pages/UsagePage';
import SettingsPage from './pages/SettingsPage';

function LoginGuard() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (isAuthenticated) return <Navigate to="/" replace />;
  return <LoginPage />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginGuard />} />
          <Route element={<Layout />}>
            <Route index element={<ChatPage />} />
            <Route path="pipelines" element={<PipelinesPage />} />
            <Route path="usage" element={<UsagePage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
```

**`frontend/src/main.tsx`** — replace entire file:
```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

## STEP 9: Clean Up Default Files

Delete these Vite boilerplate files:
- `frontend/src/App.css`
- `frontend/src/assets/react.svg`
- `frontend/public/vite.svg`

## STEP 10: Verification

```bash
cd /workspaces/AI-PORTAL/frontend
npm run build    # Should compile with 0 errors
npm run dev      # Should start on :5173
```

Open browser:
1. `http://localhost:5173/login` → Login page renders with dark theme
2. Enter `user@financecommander.com` → Redirects to chat page (if backend running)
3. Sidebar shows: Chat, Intelligence Pipelines, Usage & Costs, Settings
4. Click each nav link → Pages render with stub content
5. Sign Out → Returns to login

## COMMIT

```
feat(frontend): scaffold React 19 + TypeScript + Tailwind with auth flow

- Vite + React 19 + TypeScript project structure
- Tailwind CSS with dark navy theme
- API client with JWT auth, SSE streaming, WebSocket support
- AuthContext with login/logout/token persistence
- Login page with domain validation UX
- Sidebar navigation with 4 routes
- Layout shell with protected route guard
- Stub pages for Chat, Pipelines, Usage, Settings
- Vite proxy config for backend API routes
- TypeScript types for all API models
```

## WHAT THIS PR DOES NOT INCLUDE

- Full chat interface with message bubbles (Phase 3B)
- Pipeline execution UI with agent progress (Phase 3C)
- Usage charts and cost dashboard (Phase 3C)
- Settings page (Phase 3D)
- Specialist create/edit forms (Phase 3D)
- Tests (Phase 3E)

## DO NOT

- Do NOT modify any files in `backend/`
- Do NOT modify any Streamlit files at the repo root
- Do NOT install a CSS framework other than Tailwind
- Do NOT use Next.js, Remix, or any other framework — this is Vite + React
- Do NOT add Redux or Zustand — use React Context only
- Do NOT create `frontend/.env` — Vite proxy handles API routing
