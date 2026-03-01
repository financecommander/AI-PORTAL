import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import type { Specialist, Pipeline } from '../types';

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 20, marginBottom: 16 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 14 }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function Pill({ label, color = 'var(--cr-surface-2)' }: { label: string; color?: string }) {
  return (
    <span style={{ display: 'inline-block', padding: '3px 10px', borderRadius: 20, background: color, fontSize: 12, color: 'var(--cr-text-secondary)', marginRight: 6, marginBottom: 4, border: '1px solid var(--cr-border)' }}>
      {label}
    </span>
  );
}

export default function SettingsPage() {
  const { user } = useAuth();
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);

  useEffect(() => {
    api.request<{ specialists: Specialist[] }>('/specialists/').then((d) => setSpecialists(d.specialists)).catch(() => {});
    api.request<{ pipelines: Pipeline[] }>('/api/v2/pipelines/list').then((d) => setPipelines(d.pipelines)).catch(() => {});
  }, []);

  return (
    <div style={{ padding: '28px 32px', maxWidth: 800 }}>
      <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 22, fontWeight: 700, color: 'var(--cr-text)', marginBottom: 24 }}>
        Settings
      </h1>

      <Card title="Account">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {user?.avatar_url ? (
            <img src={user.avatar_url} alt="" style={{ width: 40, height: 40, borderRadius: '50%' }} />
          ) : (
            <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--cr-green-600)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, fontWeight: 600 }}>
              {(user?.name || user?.email)?.[0]?.toUpperCase() ?? 'U'}
            </div>
          )}
          <div>
            <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--cr-text)' }}>{user?.name || 'User'}</div>
            <div style={{ fontSize: 13, color: 'var(--cr-text-muted)' }}>{user?.email}</div>
          </div>
        </div>
      </Card>

      <Card title={`Active Specialists (${specialists.length})`}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {specialists.map((s) => <Pill key={s.id} label={s.name} />)}
          {specialists.length === 0 && <span style={{ color: 'var(--cr-text-muted)', fontSize: 13 }}>Loading...</span>}
        </div>
      </Card>

      <Card title={`Intelligence Pipelines (${pipelines.length})`}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {pipelines.map((p) => <Pill key={p.name} label={p.name} />)}
          {pipelines.length === 0 && <span style={{ color: 'var(--cr-text-muted)', fontSize: 13 }}>Loading...</span>}
        </div>
      </Card>

      <Card title="System">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--cr-text-muted)' }}>Version</span>
            <span style={{ color: 'var(--cr-text)', fontWeight: 500 }}>v2.2</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--cr-text-muted)' }}>Backend</span>
            <span style={{ color: 'var(--cr-text)', fontWeight: 500 }}>FastAPI + PostgreSQL</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--cr-text-muted)' }}>Theme</span>
            <span style={{ color: 'var(--cr-text)', fontWeight: 500 }}>Light Institutional</span>
          </div>
        </div>
      </Card>
    </div>
  );
}

