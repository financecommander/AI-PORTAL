import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import type { Specialist, Pipeline } from '../types';

function Card({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        background: 'var(--navy)',
        borderRadius: 12,
        padding: 20,
        marginBottom: 16,
      }}
    >
      {children}
    </div>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        fontSize: 13,
        fontWeight: 700,
        color: '#8899AA',
        textTransform: 'uppercase',
        letterSpacing: '0.06em',
        marginBottom: 14,
      }}
    >
      {children}
    </div>
  );
}

function Pill({ label, color = 'var(--navy-light)' }: { label: string; color?: string }) {
  return (
    <span
      style={{
        background: color,
        color: '#E0E0E0',
        borderRadius: 4,
        padding: '2px 8px',
        fontSize: 11,
        fontFamily: 'monospace',
      }}
    >
      {label}
    </span>
  );
}

function maskToken(token: string | null): string {
  if (!token) return '—';
  if (token.length <= 10) return '***';
  return `${token.slice(0, 6)}***${token.slice(-4)}`;
}

export default function SettingsPage() {
  const { logout } = useAuth();
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const token = api.getToken();

  useEffect(() => {
    Promise.all([
      api.request<{ specialists: Specialist[] }>('/specialists/'),
      api.request<{ pipelines: Pipeline[] }>('/api/v2/pipelines/list'),
    ]).then(([specRes, pipeRes]) => {
      setSpecialists(specRes.specialists ?? []);
      setPipelines(pipeRes.pipelines ?? []);
    }).catch((err) => {
      setLoadError(err instanceof Error ? err.message : 'Failed to load settings data');
    });
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>

      {loadError && (
        <div style={{ color: 'var(--orange)', fontSize: 13, marginBottom: 12 }}>
          {loadError}
        </div>
      )}

      {/* Portal Info */}
      <Card>
        <SectionTitle>Portal Info</SectionTitle>
        {[
          ['Version', '2.0.0'],
          ['Backend', 'FastAPI + Python 3.12'],
          ['Frontend', 'React 19 + TypeScript'],
          ['LLM Providers', '4 (Anthropic, OpenAI, xAI, Google)'],
        ].map(([label, value]) => (
          <div
            key={label}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              padding: '7px 0',
              borderBottom: '1px solid var(--navy-light)',
              fontSize: 14,
            }}
          >
            <span style={{ color: '#8899AA' }}>{label}</span>
            <span style={{ color: '#E0E0E0' }}>{value}</span>
          </div>
        ))}
      </Card>

      {/* Specialists */}
      <Card>
        <SectionTitle>Configured Specialists</SectionTitle>
        {specialists.length === 0 && (
          <div style={{ color: '#667788', fontSize: 13 }}>Loading specialists…</div>
        )}
        {specialists.map((s) => (
          <div
            key={s.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '8px 0',
              borderBottom: '1px solid var(--navy-light)',
              flexWrap: 'wrap',
            }}
          >
            <span style={{ flex: 1, color: '#E0E0E0', fontSize: 14 }}>{s.name}</span>
            <Pill label={s.provider} color="var(--navy-dark)" />
            <Pill label={s.model} />
            <span
              style={{
                background: 'rgba(46,117,182,0.15)',
                color: 'var(--blue)',
                borderRadius: 4,
                padding: '2px 6px',
                fontSize: 11,
              }}
            >
              temp {s.temperature}
            </span>
          </div>
        ))}
        <div style={{ marginTop: 10, fontSize: 12, color: '#556677' }}>
          Specialist configuration available in v2.1
        </div>
      </Card>

      {/* Pipelines */}
      <Card>
        <SectionTitle>Available Pipelines</SectionTitle>
        {pipelines.length === 0 && (
          <div style={{ color: '#667788', fontSize: 13 }}>Loading pipelines…</div>
        )}
        {pipelines.map((p) => (
          <div
            key={p.name}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 10,
              padding: '8px 0',
              borderBottom: '1px solid var(--navy-light)',
            }}
          >
            <div style={{ flex: 1 }}>
              <div style={{ color: '#E0E0E0', fontSize: 14, marginBottom: 2 }}>{p.name}</div>
              <div style={{ color: '#8899AA', fontSize: 12 }}>{p.description}</div>
            </div>
            <span
              style={{
                background: 'rgba(46,117,182,0.15)',
                color: 'var(--blue)',
                borderRadius: 4,
                padding: '2px 8px',
                fontSize: 11,
                whiteSpace: 'nowrap',
              }}
            >
              {p.agents.length} agents
            </span>
          </div>
        ))}
      </Card>

      {/* Session */}
      <Card>
        <SectionTitle>Your Session</SectionTitle>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '7px 0',
            borderBottom: '1px solid var(--navy-light)',
            marginBottom: 14,
          }}
        >
          <span style={{ color: '#8899AA', fontSize: 13 }}>Token</span>
          <span style={{ fontFamily: 'monospace', fontSize: 12, color: '#E0E0E0' }}>
            {maskToken(token)}
          </span>
        </div>
        <button
          onClick={logout}
          style={{
            background: 'var(--red)',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: 8,
            padding: '8px 20px',
            fontSize: 14,
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          Sign Out
        </button>
      </Card>
    </div>
  );
}
