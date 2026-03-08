import { useState, useEffect, useRef, useCallback } from 'react';
import { ArrowLeft, Plus, Send, Pause, Play, CheckCircle, Wifi, WifiOff, RefreshCw, Lock, Layers } from 'lucide-react';
import { useSwarm } from '../hooks/useSwarm';
import type { CollaborationMode, CreateSessionRequest, SwarmSession } from '../types/swarm';
import BlueprintEditor from '../components/blueprint/BlueprintEditor';

// ── Helpers ─────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  active: '#1A6B3C',
  paused: '#D4A017',
  completed: '#2E75B6',
  failed: '#D64545',
};

const MODE_LABELS: Record<string, string> = {
  round_table: 'Round Table',
  review_chain: 'Review Chain',
  specialist: 'Specialist',
  debate: 'Debate',
};

function formatCost(cost: number): string {
  return cost === 0 ? '$0.00 (local)' : `$${cost.toFixed(4)}`;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── Caste Badge ─────────────────────────────────────────────────────

const CASTE_COLORS: Record<string, string> = {
  guardian_claude: '#7C3AED',
  guardian_opus: '#8B5CF6',
  hydra_code: '#059669',
  hydra_financial: '#D97706',
  hydra_compliance: '#9333EA',
  hydra_marketing: '#F59E0B',
  ultra_reasoning: '#2563EB',
  ultra_research: '#0891B2',
  mutalisk_legal: '#DC2626',
  mutalisk_conversational: '#EC4899',
  mutalisk_quick: '#F472B6',
  drone_ultra_cheap: '#14B8A6',
  drone_cheap: '#10B981',
  drone_fast: '#34D399',
  overseer: '#F97316',
  changeling: '#A855F7',
  nydus: '#6366F1',
};

function CasteBadge({ caste }: { caste: string }) {
  const color = CASTE_COLORS[caste] || '#6B7280';
  const label = caste.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '9999px',
        fontSize: '11px',
        fontWeight: 600,
        color: '#fff',
        background: color,
        marginRight: '4px',
        marginBottom: '4px',
      }}
    >
      {label}
    </span>
  );
}

// ── VM Status Dashboard Types ───────────────────────────────────────

interface HealthData {
  status: string;
  uptime_seconds: number;
  environment: string;
  version: string;
  workers?: number;
}

interface StatsData {
  total_tasks: number;
  total_cost: number;
  tasks_by_caste: Record<string, number>;
  cost_by_caste: Record<string, number>;
}

interface SkillsSnapshotData {
  skills: Record<string, { name: string; category: string; description: string }>;
  proficiencies: Record<string, { score: number; level: string; tasks_completed: number }>;
  event_count: number;
}

interface ModelsData {
  castes: Record<string, { model: string; provider: string; cost_input_per_1m: number; cost_output_per_1m: number }>;
}

interface ServiceRow {
  name: string;
  status: 'healthy' | 'down' | 'up' | 'loading';
  notes: string;
}

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
}

// ── Matrix Rain Background ──────────────────────────────────────────

function MatrixRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext('2d')!;

    let animId: number;
    const chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF<>{}[]|/\\';
    const fontSize = 14;
    let columns: number;
    let drops: number[];

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      columns = Math.floor(canvas.width / fontSize);
      drops = Array(columns).fill(1).map(() => Math.random() * -100);
    };

    resize();
    window.addEventListener('resize', resize);

    const draw = () => {
      ctx.fillStyle = 'rgba(247, 249, 248, 0.04)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < columns; i++) {
        const char = chars[Math.floor(Math.random() * chars.length)];
        const x = i * fontSize;
        const y = drops[i] * fontSize;

        const brightness = Math.random();
        if (brightness > 0.95) {
          ctx.fillStyle = 'rgba(26, 107, 60, 0.35)';
        } else if (brightness > 0.8) {
          ctx.fillStyle = 'rgba(62, 155, 95, 0.25)';
        } else {
          ctx.fillStyle = 'rgba(15, 77, 44, 0.12)';
        }

        ctx.fillText(char, x, y);

        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i] += 0.5 + Math.random() * 0.5;
      }

      animId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
      }}
    />
  );
}

// ── VM Status Dashboard ─────────────────────────────────────────────

function VMStatusDashboard({ onUnlock }: { onUnlock: () => void }) {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [stats, setStats] = useState<StatsData | null>(null);
  const [skills, setSkills] = useState<SkillsSnapshotData | null>(null);
  const [models, setModels] = useState<ModelsData | null>(null);
  const [swarmUp, setSwarmUp] = useState<boolean | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [showPasswordInput, setShowPasswordInput] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const fetchAll = useCallback(async () => {
    setRefreshing(true);

    // Health
    try {
      const res = await fetch('/swarm/health', { signal: AbortSignal.timeout(8000) });
      if (res.ok) {
        const data: HealthData = await res.json();
        setHealth(data);
        setSwarmUp(true);
      } else {
        setSwarmUp(false);
      }
    } catch {
      setSwarmUp(false);
    }

    // Stats
    try {
      const res = await fetch('/swarm/api/v1/stats', { signal: AbortSignal.timeout(8000) });
      if (res.ok) setStats(await res.json());
    } catch { /* ignore */ }

    // Skills snapshot
    try {
      const res = await fetch('/swarm/api/v1/skills/snapshot', { signal: AbortSignal.timeout(8000) });
      if (res.ok) setSkills(await res.json());
    } catch { /* ignore */ }

    // Models
    try {
      const res = await fetch('/swarm/api/v1/models', { signal: AbortSignal.timeout(8000) });
      if (res.ok) setModels(await res.json());
    } catch { /* ignore */ }

    setRefreshing(false);
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === 'Alpha007!') {
      sessionStorage.setItem('swarm_unlocked', '1');
      onUnlock();
    } else {
      setPasswordError('Invalid password');
      setPassword('');
    }
  };

  // ── Derive service table rows ──
  const services: ServiceRow[] = (() => {
    const apiUp = swarmUp === true;
    const loading = swarmUp === null;
    const versionStr = health?.version ? `v${health.version}` : '';
    const workersStr = health?.workers ? `${health.workers} workers` : '';
    const apiNotes = [versionStr, workersStr].filter(Boolean).join(', ') || (loading ? 'Checking...' : '');

    return [
      { name: 'Hive Mind Core', status: loading ? 'loading' : apiUp ? 'healthy' : 'down', notes: apiNotes },
      { name: 'Memory Nexus', status: loading ? 'loading' : apiUp ? 'healthy' : 'down', notes: apiUp ? 'Synapses linked' : '' },
      { name: 'Creep Cache', status: loading ? 'loading' : apiUp ? 'healthy' : 'down', notes: apiUp ? 'Spreading active' : '' },
      { name: 'Overseer Eye', status: 'up', notes: 'Scanning telemetry' },
      { name: 'Neural Cortex', status: 'up', notes: 'Dashboards online' },
      { name: 'Nydus Network', status: 'up', notes: 'Trace tunnels open' },
    ];
  })();

  // ── Derive agent castes table ──
  const casteRows = (() => {
    if (!models?.castes) return [];
    return Object.entries(models.castes).map(([casteName, info]) => {
      // Count proficiencies for this caste
      let skillCount = 0;
      let topLevel = '';
      const levelOrder: Record<string, number> = { novice: 0, beginner: 1, intermediate: 2, advanced: 3, expert: 4, master: 5 };
      let topLevelRank = -1;

      if (skills?.proficiencies) {
        Object.entries(skills.proficiencies).forEach(([key, prof]) => {
          if (key.startsWith(casteName + ':')) {
            skillCount++;
            const rank = levelOrder[prof.level] ?? -1;
            if (rank > topLevelRank) {
              topLevelRank = rank;
              topLevel = prof.level;
            }
          }
        });
      }

      return {
        caste: casteName,
        provider: info.provider,
        model: info.model,
        costInput: info.cost_input_per_1m,
        costOutput: info.cost_output_per_1m,
        skillCount,
        topLevel: topLevel || '-',
      };
    });
  })();

  // ── Derive skills overview ──
  const skillsSummary = (() => {
    if (!skills) return { totalSkills: 0, categories: {} as Record<string, number>, totalProficiencies: 0 };
    const categories: Record<string, number> = {};
    Object.values(skills.skills).forEach(s => {
      categories[s.category] = (categories[s.category] || 0) + 1;
    });
    return {
      totalSkills: Object.keys(skills.skills).length,
      categories,
      totalProficiencies: Object.keys(skills.proficiencies).length,
    };
  })();

  const categoryCount = Object.keys(skillsSummary.categories).length;

  // ── Table shared styles ──
  const thStyle: React.CSSProperties = {
    textAlign: 'left', padding: '10px 14px', fontSize: '11px', fontWeight: 600,
    color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px',
    borderBottom: '2px solid var(--cr-border-dark)', whiteSpace: 'nowrap',
  };
  const tdStyle: React.CSSProperties = {
    padding: '10px 14px', fontSize: '13px', color: 'var(--cr-text)', borderBottom: '1px solid var(--cr-border)',
  };

  return (
    <div style={{ position: 'relative', minHeight: '100vh' }}>
      <MatrixRain />
      <div style={{ position: 'relative', zIndex: 1, padding: '32px', maxWidth: '960px', margin: '0 auto' }}>

      {/* ── 1. Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h1 style={{ color: 'var(--cr-text)', fontSize: '22px', fontWeight: 700, margin: 0 }}>
            Swarm Mainframe
          </h1>
          <p style={{ color: 'var(--cr-text-muted)', fontSize: '13px', margin: '4px 0 0 0' }}>
            Orchestra Swarm — 17 agents, 9 castes, 5 providers
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={fetchAll}
            disabled={refreshing}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '8px 14px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)',
              background: 'transparent', color: 'var(--cr-text-secondary)', fontSize: '13px',
              cursor: refreshing ? 'wait' : 'pointer', opacity: refreshing ? 0.6 : 1,
            }}
          >
            <RefreshCw style={{ width: 14, height: 14, animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          <button
            onClick={() => setShowPasswordInput(true)}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '8px 14px', borderRadius: 'var(--cr-radius-sm)', border: 'none',
              background: 'var(--cr-green-700)', color: '#fff', fontSize: '13px',
              fontWeight: 600, cursor: 'pointer',
            }}
          >
            <Lock style={{ width: 14, height: 14 }} /> Session Console
          </button>
        </div>
      </div>

      {/* ── 2. Service Status Table ── */}
      <div
        style={{
          background: 'var(--cr-white)', border: '1px solid var(--cr-border)',
          borderRadius: 'var(--cr-radius)', overflow: 'hidden', marginBottom: '24px',
        }}
      >
        <div style={{ padding: '16px 20px 0 20px' }}>
          <h3 style={{ color: 'var(--cr-text)', fontSize: '15px', fontWeight: 600, margin: '0 0 12px 0' }}>
            Service Status
          </h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: 'var(--cr-surface)' }}>
              <th style={thStyle}>Service</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Notes</th>
            </tr>
          </thead>
          <tbody>
            {services.map((svc, i) => (
              <tr key={svc.name} style={{ background: i % 2 === 1 ? 'var(--cr-surface)' : 'var(--cr-white)' }}>
                <td style={{ ...tdStyle, fontWeight: 600 }}>{svc.name}</td>
                <td style={tdStyle}>
                  {svc.status === 'loading' ? (
                    <span style={{ color: 'var(--cr-text-muted)' }}>... checking</span>
                  ) : svc.status === 'healthy' ? (
                    <span style={{ color: 'var(--cr-green-700)', fontWeight: 600 }}>{'\u{1F7E2}'} HEALTHY</span>
                  ) : svc.status === 'up' ? (
                    <span style={{ color: 'var(--cr-green-700)', fontWeight: 600 }}>{'\u{1F7E2}'} UP</span>
                  ) : (
                    <span style={{ color: 'var(--cr-danger)', fontWeight: 600 }}>{'\u{1F534}'} DOWN</span>
                  )}
                </td>
                <td style={{ ...tdStyle, color: 'var(--cr-text-secondary)' }}>{svc.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── 3. System Resources ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px', marginBottom: '24px' }}>
        {[
          { label: 'Uptime', value: health ? formatUptime(health.uptime_seconds) : '-' },
          { label: 'Environment', value: health?.environment || '-' },
          { label: 'Version', value: health?.version ? `v${health.version}` : '-' },
          { label: 'Total Tasks', value: stats ? String(stats.total_tasks) : '-' },
          { label: 'Total Cost', value: stats ? `$${stats.total_cost.toFixed(2)}` : '-' },
        ].map(card => (
          <div
            key={card.label}
            style={{
              background: 'var(--cr-white)', border: '1px solid var(--cr-border)',
              borderRadius: 'var(--cr-radius-sm)', padding: '14px 16px', textAlign: 'center',
            }}
          >
            <p style={{ color: 'var(--cr-text-muted)', fontSize: '11px', fontWeight: 600, margin: '0 0 4px 0', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              {card.label}
            </p>
            <p style={{ color: 'var(--cr-text)', fontSize: '18px', fontWeight: 700, margin: 0 }}>
              {card.value}
            </p>
          </div>
        ))}
      </div>

      {/* ── 4. Agent Castes Table ── */}
      {casteRows.length > 0 && (
        <div
          style={{
            background: 'var(--cr-white)', border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius)', overflow: 'hidden', marginBottom: '24px',
          }}
        >
          <div style={{ padding: '16px 20px 0 20px' }}>
            <h3 style={{ color: 'var(--cr-text)', fontSize: '15px', fontWeight: 600, margin: '0 0 12px 0' }}>
              Agent Castes
            </h3>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--cr-surface)' }}>
                <th style={thStyle}>Caste</th>
                <th style={thStyle}>Provider</th>
                <th style={thStyle}>Model</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Input $/1M</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Output $/1M</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Skills</th>
                <th style={thStyle}>Level</th>
              </tr>
            </thead>
            <tbody>
              {casteRows.map((row, i) => (
                <tr key={row.caste} style={{ background: i % 2 === 1 ? 'var(--cr-surface)' : 'var(--cr-white)' }}>
                  <td style={tdStyle}><CasteBadge caste={row.caste} /></td>
                  <td style={{ ...tdStyle, color: 'var(--cr-text-secondary)' }}>{row.provider}</td>
                  <td style={{ ...tdStyle, fontFamily: 'monospace', fontSize: '12px' }}>{row.model}</td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'monospace', fontSize: '12px' }}>
                    {row.costInput === 0 ? '$0.00' : `$${row.costInput.toFixed(2)}`}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontFamily: 'monospace', fontSize: '12px' }}>
                    {row.costOutput === 0 ? '$0.00' : `$${row.costOutput.toFixed(2)}`}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontWeight: 600 }}>{row.skillCount}</td>
                  <td style={{ ...tdStyle, textTransform: 'capitalize', color: 'var(--cr-text-secondary)' }}>{row.topLevel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── 5. Skills Overview ── */}
      {skills && (
        <div
          style={{
            background: 'var(--cr-white)', border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius)', padding: '20px 24px', marginBottom: '24px',
          }}
        >
          <h3 style={{ color: 'var(--cr-text)', fontSize: '15px', fontWeight: 600, margin: '0 0 14px 0' }}>
            Skills Overview
          </h3>
          <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
            {[
              { label: 'Total Skills', value: String(skillsSummary.totalSkills) },
              { label: 'Categories', value: String(categoryCount) },
              { label: 'Proficiency Assignments', value: String(skillsSummary.totalProficiencies) },
            ].map(card => (
              <div
                key={card.label}
                style={{
                  flex: 1, padding: '12px 16px', borderRadius: 'var(--cr-radius-sm)',
                  background: 'var(--cr-surface)', border: '1px solid var(--cr-border)', textAlign: 'center',
                }}
              >
                <p style={{ color: 'var(--cr-text-muted)', fontSize: '11px', fontWeight: 600, margin: '0 0 2px 0', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  {card.label}
                </p>
                <p style={{ color: 'var(--cr-text)', fontSize: '20px', fontWeight: 700, margin: 0 }}>
                  {card.value}
                </p>
              </div>
            ))}
          </div>
          <p style={{ color: 'var(--cr-text-secondary)', fontSize: '12px', margin: '0 0 10px 0' }}>
            {skillsSummary.totalSkills} skills across {categoryCount} categories
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '8px' }}>
            {Object.entries(skillsSummary.categories)
              .sort((a, b) => b[1] - a[1])
              .map(([cat, count]) => (
                <div
                  key={cat}
                  style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '8px 12px', borderRadius: 'var(--cr-radius-xs)',
                    background: 'var(--cr-surface-2)', border: '1px solid var(--cr-border)',
                  }}
                >
                  <span style={{ fontSize: '12px', color: 'var(--cr-text-secondary)', textTransform: 'capitalize' }}>
                    {cat.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--cr-text)' }}>
                    {count}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* ── 6. Architecture Card ── */}
      <div
        style={{
          background: 'var(--cr-white)',
          border: '1px solid var(--cr-border)',
          borderRadius: 'var(--cr-radius)',
          padding: '20px 24px',
          marginBottom: '24px',
        }}
      >
        <h3 style={{ color: 'var(--cr-text)', fontSize: '15px', fontWeight: 600, margin: '0 0 12px 0' }}>
          Swarm Architecture
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
          {[
            { label: 'Agents', value: '17 specialized' },
            { label: 'Castes', value: '9 tiers' },
            { label: 'Providers', value: 'Claude, Gemini, Grok, Llama, DeepSeek' },
            { label: 'Local Inference', value: 'Ollama (NVIDIA L4 24GB)' },
            { label: 'Collaboration Modes', value: 'Round Table, Review Chain, Specialist, Debate' },
            { label: 'Monitoring', value: 'Prometheus + Grafana + Jaeger' },
          ].map(item => (
            <div key={item.label}>
              <p style={{ color: 'var(--cr-text-muted)', fontSize: '11px', fontWeight: 600, margin: '0 0 2px 0', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                {item.label}
              </p>
              <p style={{ color: 'var(--cr-text)', fontSize: '13px', margin: 0 }}>
                {item.value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Password Modal ── */}
      {showPasswordInput && (
        <div
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
          }}
          onClick={() => { setShowPasswordInput(false); setPasswordError(''); setPassword(''); }}
        >
          <form
            onClick={e => e.stopPropagation()}
            onSubmit={handlePasswordSubmit}
            style={{
              background: 'var(--cr-white)', border: '1px solid var(--cr-border)',
              borderRadius: 'var(--cr-radius)', padding: '28px', width: '360px',
              boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <Lock style={{ width: 20, height: 20, color: 'var(--cr-green-700)' }} />
              <h2 style={{ color: 'var(--cr-text)', fontSize: '18px', fontWeight: 700, margin: 0 }}>
                Session Console Access
              </h2>
            </div>
            <p style={{ color: 'var(--cr-text-muted)', fontSize: '13px', margin: '0 0 16px 0' }}>
              Enter the access password to manage swarm sessions.
            </p>
            <input
              type="password"
              value={password}
              onChange={e => { setPassword(e.target.value); setPasswordError(''); }}
              placeholder="Password"
              autoFocus
              style={{
                width: '100%', padding: '10px 12px', borderRadius: 'var(--cr-radius-sm)',
                border: `1px solid ${passwordError ? 'var(--cr-danger)' : 'var(--cr-border)'}`,
                background: 'var(--cr-surface)', color: 'var(--cr-text)', fontSize: '14px',
                marginBottom: passwordError ? '6px' : '16px', boxSizing: 'border-box',
              }}
            />
            {passwordError && (
              <p style={{ color: 'var(--cr-danger)', fontSize: '12px', margin: '0 0 12px 0' }}>{passwordError}</p>
            )}
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                type="button"
                onClick={() => { setShowPasswordInput(false); setPasswordError(''); setPassword(''); }}
                style={{
                  padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)',
                  border: '1px solid var(--cr-border)', background: 'transparent',
                  color: 'var(--cr-text-secondary)', fontSize: '14px', cursor: 'pointer',
                }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!password}
                style={{
                  padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)', border: 'none',
                  background: 'var(--cr-green-700)', color: '#fff', fontSize: '14px',
                  fontWeight: 600, cursor: 'pointer', opacity: !password ? 0.5 : 1,
                }}
              >
                Unlock
              </button>
            </div>
          </form>
        </div>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
    </div>
  );
}

// ── Create Session Modal ────────────────────────────────────────────

interface CreateModalProps {
  presets: Record<string, string[]>;
  onClose: () => void;
  onCreate: (req: CreateSessionRequest) => Promise<void>;
}

function CreateSessionModal({ presets, onClose, onCreate }: CreateModalProps) {
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [mode, setMode] = useState<CollaborationMode>('round_table');
  const [teamPreset, setTeamPreset] = useState('code');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectName.trim() || !description.trim()) return;
    setSubmitting(true);
    try {
      await onCreate({
        project_name: projectName.trim(),
        description: description.trim(),
        mode,
        team_preset: teamPreset,
        created_by: 'portal-user',
      });
      onClose();
    } catch {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
      }}
      onClick={onClose}
    >
      <form
        onClick={e => e.stopPropagation()}
        onSubmit={handleSubmit}
        style={{
          background: 'var(--cr-white)', border: '1px solid var(--cr-border)',
          borderRadius: 'var(--cr-radius)', padding: '28px', width: '480px', maxWidth: '90vw',
          boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
        }}
      >
        <h2 style={{ color: 'var(--cr-text)', fontSize: '18px', fontWeight: 700, marginBottom: '20px' }}>
          New Swarm Session
        </h2>

        <label style={{ color: 'var(--cr-text-muted)', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
          Project Name
        </label>
        <input
          value={projectName}
          onChange={e => setProjectName(e.target.value)}
          placeholder="e.g. API Refactor Sprint"
          style={{
            width: '100%', padding: '10px 12px', borderRadius: 'var(--cr-radius-sm)',
            border: '1px solid var(--cr-border)', background: 'var(--cr-surface)',
            color: 'var(--cr-text)', fontSize: '14px', marginBottom: '14px', boxSizing: 'border-box',
          }}
        />

        <label style={{ color: 'var(--cr-text-muted)', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
          Description / First Prompt
        </label>
        <textarea
          value={description}
          onChange={e => setDescription(e.target.value)}
          rows={3}
          placeholder="Describe what the swarm should work on..."
          style={{
            width: '100%', padding: '10px 12px', borderRadius: 'var(--cr-radius-sm)',
            border: '1px solid var(--cr-border)', background: 'var(--cr-surface)',
            color: 'var(--cr-text)', fontSize: '14px', marginBottom: '14px',
            resize: 'vertical', boxSizing: 'border-box',
          }}
        />

        <div style={{ display: 'flex', gap: '12px', marginBottom: '14px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ color: 'var(--cr-text-muted)', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
              Mode
            </label>
            <select
              value={mode}
              onChange={e => setMode(e.target.value as CollaborationMode)}
              style={{
                width: '100%', padding: '10px 12px', borderRadius: 'var(--cr-radius-sm)',
                border: '1px solid var(--cr-border)', background: 'var(--cr-surface)',
                color: 'var(--cr-text)', fontSize: '14px',
              }}
            >
              <option value="round_table">Round Table</option>
              <option value="review_chain">Review Chain</option>
              <option value="specialist">Specialist</option>
              <option value="debate">Debate</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ color: 'var(--cr-text-muted)', fontSize: '13px', display: 'block', marginBottom: '4px' }}>
              Team Preset
            </label>
            <select
              value={teamPreset}
              onChange={e => setTeamPreset(e.target.value)}
              style={{
                width: '100%', padding: '10px 12px', borderRadius: 'var(--cr-radius-sm)',
                border: '1px solid var(--cr-border)', background: 'var(--cr-surface)',
                color: 'var(--cr-text)', fontSize: '14px',
              }}
            >
              {Object.keys(presets).map(k => (
                <option key={k} value={k}>{k.charAt(0).toUpperCase() + k.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>

        {presets[teamPreset] && (
          <div style={{ marginBottom: '16px' }}>
            <span style={{ color: 'var(--cr-text-muted)', fontSize: '12px' }}>Castes: </span>
            {presets[teamPreset].map(c => <CasteBadge key={c} caste={c} />)}
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button type="button" onClick={onClose} style={{ padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'transparent', color: 'var(--cr-text-secondary)', fontSize: '14px', cursor: 'pointer' }}>
            Cancel
          </button>
          <button type="submit" disabled={!projectName.trim() || !description.trim() || submitting} style={{ padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)', border: 'none', background: submitting ? 'var(--cr-green-600)' : 'var(--cr-green-700)', color: '#fff', fontSize: '14px', fontWeight: 600, cursor: submitting ? 'wait' : 'pointer', opacity: (!projectName.trim() || !description.trim()) ? 0.5 : 1 }}>
            {submitting ? 'Creating...' : 'Create Session'}
          </button>
        </div>
      </form>
    </div>
  );
}

// ── Session Card ────────────────────────────────────────────────────

function SessionCard({ session, onSelect }: { session: SwarmSession; onSelect: (id: string) => void }) {
  return (
    <div
      onClick={() => onSelect(session.session_id)}
      style={{
        background: 'var(--cr-white)', border: '1px solid var(--cr-border)',
        borderRadius: 'var(--cr-radius-sm)', padding: '16px', cursor: 'pointer', transition: 'all 150ms',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
        <h3 style={{ color: 'var(--cr-text)', fontSize: '15px', fontWeight: 600, margin: 0, flex: 1 }}>
          {session.project_name}
        </h3>
        <span style={{ padding: '2px 8px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600, color: '#fff', background: STATUS_COLORS[session.status] || '#6B7280', marginLeft: '8px', textTransform: 'uppercase' }}>
          {session.status}
        </span>
      </div>
      <p style={{ color: 'var(--cr-text-muted)', fontSize: '13px', margin: '0 0 10px 0', lineHeight: 1.4 }}>
        {session.description.length > 100 ? session.description.slice(0, 100) + '...' : session.description}
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
        {session.participating_castes.map(c => <CasteBadge key={c} caste={c} />)}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--cr-text-dim)', fontSize: '12px' }}>
        <span>{MODE_LABELS[session.mode] || session.mode}</span>
        <span>Round {session.current_round} | {session.message_count} msgs</span>
        <span>{formatCost(session.total_cost)}</span>
      </div>
      <div style={{ color: 'var(--cr-mist)', fontSize: '11px', marginTop: '4px', textAlign: 'right' }}>
        {timeAgo(session.created_at)}
      </div>
    </div>
  );
}

// ── Session Console (password-protected) ────────────────────────────

function SessionConsole({ onLock, onOpenBlueprint }: { onLock: () => void; onOpenBlueprint: () => void }) {
  const {
    sessions, selectedSession, presets, health, loading, sending, error, connected,
    refreshSessions, selectSession, deselectSession, createSession,
    sendMessage, pauseSession, resumeSession, completeSession, loadPresets,
  } = useSwarm();

  const [showCreate, setShowCreate] = useState(false);
  const [messageInput, setMessageInput] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { loadPresets(); }, [loadPresets]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [selectedSession?.messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim() || sending) return;
    const msg = messageInput;
    setMessageInput('');
    await sendMessage(msg);
  };

  const handleCreate = async (req: CreateSessionRequest) => {
    const session = await createSession(req);
    await selectSession(session.session_id);
  };

  const filteredSessions = statusFilter === 'all' ? sessions : sessions.filter(s => s.status === statusFilter);
  const activeSessions = sessions.filter(s => s.status === 'active').length;
  const totalCost = sessions.reduce((sum, s) => sum + s.total_cost, 0);

  // ── Session Detail View
  if (selectedSession) {
    return (
      <div style={{ padding: '32px', maxWidth: '900px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
          <button onClick={deselectSession} style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'none', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-xs)', padding: '6px 12px', color: 'var(--cr-text-secondary)', fontSize: '13px', cursor: 'pointer' }}>
            <ArrowLeft style={{ width: 14, height: 14 }} /> Back
          </button>
          <h1 style={{ color: 'var(--cr-text)', fontSize: '20px', fontWeight: 700, margin: 0, flex: 1 }}>
            {selectedSession.project_name}
          </h1>
          <span style={{ padding: '4px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: 600, color: '#fff', background: STATUS_COLORS[selectedSession.status] || '#6B7280', textTransform: 'uppercase' }}>
            {selectedSession.status}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', padding: '12px 16px', borderRadius: 'var(--cr-radius-sm)', background: 'var(--cr-surface-2)', border: '1px solid var(--cr-border)', marginBottom: '16px', fontSize: '13px', color: 'var(--cr-text-secondary)' }}>
          <span>Mode: <strong style={{ color: 'var(--cr-text)' }}>{MODE_LABELS[selectedSession.mode]}</strong></span>
          <span>Round: <strong style={{ color: 'var(--cr-text)' }}>{selectedSession.current_round}/{selectedSession.max_rounds}</strong></span>
          <span>Cost: <strong style={{ color: 'var(--cr-text)' }}>{formatCost(selectedSession.total_cost)}</strong></span>
          <span>Messages: <strong style={{ color: 'var(--cr-text)' }}>{selectedSession.message_count}</strong></span>
          <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
            {selectedSession.participating_castes.map(c => <CasteBadge key={c} caste={c} />)}
          </div>
        </div>

        {selectedSession.status !== 'completed' && selectedSession.status !== 'failed' && (
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
            {selectedSession.status === 'active' && (
              <button onClick={pauseSession} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid #D4A017', background: 'transparent', color: '#D4A017', fontSize: '13px', cursor: 'pointer' }}>
                <Pause style={{ width: 14, height: 14 }} /> Pause
              </button>
            )}
            {selectedSession.status === 'paused' && (
              <button onClick={resumeSession} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-green-700)', background: 'transparent', color: 'var(--cr-green-700)', fontSize: '13px', cursor: 'pointer' }}>
                <Play style={{ width: 14, height: 14 }} /> Resume
              </button>
            )}
            <button onClick={completeSession} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 16px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid #2E75B6', background: 'transparent', color: '#2E75B6', fontSize: '13px', cursor: 'pointer' }}>
              <CheckCircle style={{ width: 14, height: 14 }} /> Complete
            </button>
          </div>
        )}

        <div style={{ background: 'var(--cr-white)', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-sm)', padding: '16px', maxHeight: '500px', overflowY: 'auto', marginBottom: '16px' }}>
          {(!selectedSession.messages || selectedSession.messages.length === 0) && (
            <p style={{ color: 'var(--cr-text-muted)', textAlign: 'center', padding: '40px 0' }}>No messages yet. Send a prompt to start the session.</p>
          )}
          {selectedSession.messages?.map((msg, i) => (
            <div key={msg.message_id || i} style={{ marginBottom: '14px', padding: '12px 14px', borderRadius: 'var(--cr-radius-sm)', background: msg.role === 'human' ? 'var(--cr-green-50)' : 'var(--cr-surface)', borderLeft: `3px solid ${msg.role === 'human' ? 'var(--cr-green-700)' : (CASTE_COLORS[msg.caste || ''] || 'var(--cr-border)')}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {msg.caste && <CasteBadge caste={msg.caste} />}
                  <span style={{ color: 'var(--cr-text-secondary)', fontSize: '12px', fontWeight: 600 }}>
                    {msg.role === 'human' ? 'You' : msg.caste ? '' : 'System'}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '12px', color: 'var(--cr-text-dim)', fontSize: '11px' }}>
                  {msg.model_used && <span>{msg.model_used}</span>}
                  {msg.latency_ms > 0 && <span>{(msg.latency_ms / 1000).toFixed(1)}s</span>}
                  <span>{formatCost(msg.cost)}</span>
                  <span>R{msg.round_number}</span>
                </div>
              </div>
              <div style={{ color: 'var(--cr-text)', fontSize: '14px', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{msg.content}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
          {sending && (
            <div style={{ textAlign: 'center', padding: '16px', color: 'var(--cr-text-muted)', fontSize: '13px' }}>
              <span className="animate-blink">Castes are responding...</span>
            </div>
          )}
        </div>

        {selectedSession.status === 'active' && (
          <form onSubmit={handleSend} style={{ display: 'flex', gap: '10px' }}>
            <input value={messageInput} onChange={e => setMessageInput(e.target.value)} placeholder="Send a message to the swarm..." disabled={sending} style={{ flex: 1, padding: '12px 16px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'var(--cr-surface)', color: 'var(--cr-text)', fontSize: '14px' }} />
            <button type="submit" disabled={!messageInput.trim() || sending} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '12px 20px', borderRadius: 'var(--cr-radius-sm)', border: 'none', background: sending ? 'var(--cr-green-600)' : 'var(--cr-green-700)', color: '#fff', fontSize: '14px', fontWeight: 600, cursor: sending ? 'wait' : 'pointer', opacity: !messageInput.trim() ? 0.5 : 1 }}>
              <Send style={{ width: 16, height: 16 }} /> Send
            </button>
          </form>
        )}
      </div>
    );
  }

  // ── Sessions List View
  return (
    <div style={{ padding: '32px', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ color: 'var(--cr-text)', fontSize: '22px', fontWeight: 700, margin: 0 }}>Session Console</h1>
          <p style={{ color: 'var(--cr-text-muted)', fontSize: '13px', margin: '4px 0 0 0' }}>Multi-model live collaboration</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: connected ? 'var(--cr-green-700)' : 'var(--cr-danger)', fontSize: '13px' }}>
            {connected ? <Wifi style={{ width: 16, height: 16 }} /> : <WifiOff style={{ width: 16, height: 16 }} />}
            {connected ? 'Connected' : 'Offline'}
          </div>
          <button onClick={onLock} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'transparent', color: 'var(--cr-text-secondary)', fontSize: '13px', cursor: 'pointer' }}>
            <Lock style={{ width: 14, height: 14 }} /> Lock
          </button>
          <button onClick={refreshSessions} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 12px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'transparent', color: 'var(--cr-text-secondary)', fontSize: '13px', cursor: 'pointer' }}>
            <RefreshCw style={{ width: 14, height: 14 }} />
          </button>
          <button onClick={onOpenBlueprint} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '10px 18px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid #7C3AED', background: 'transparent', color: '#7C3AED', fontSize: '14px', fontWeight: 600, cursor: 'pointer' }}>
            <Layers style={{ width: 16, height: 16 }} /> Blueprint
          </button>
          <button onClick={() => setShowCreate(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '10px 18px', borderRadius: 'var(--cr-radius-sm)', border: 'none', background: 'var(--cr-green-700)', color: '#fff', fontSize: '14px', fontWeight: 600, cursor: 'pointer' }}>
            <Plus style={{ width: 16, height: 16 }} /> New Session
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '24px' }}>
        {[
          { label: 'Active Sessions', value: String(activeSessions), color: 'var(--cr-green-700)' },
          { label: 'Total Sessions', value: String(sessions.length), color: '#2E75B6' },
          { label: 'Total Cost', value: formatCost(totalCost), color: 'var(--cr-gold-500)' },
          { label: 'Swarm Health', value: health?.status === 'ok' ? 'Healthy' : 'Unknown', color: connected ? 'var(--cr-green-700)' : 'var(--cr-danger)' },
        ].map(card => (
          <div key={card.label} style={{ background: 'var(--cr-white)', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-sm)', padding: '16px', textAlign: 'center' }}>
            <p style={{ color: 'var(--cr-text-muted)', fontSize: '12px', margin: '0 0 6px 0' }}>{card.label}</p>
            <p style={{ color: card.color, fontSize: '20px', fontWeight: 700, margin: 0 }}>{card.value}</p>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        {['all', 'active', 'paused', 'completed'].map(f => (
          <button key={f} onClick={() => setStatusFilter(f)} style={{ padding: '6px 14px', borderRadius: '9999px', border: '1px solid var(--cr-border)', background: statusFilter === f ? 'var(--cr-surface-2)' : 'transparent', color: statusFilter === f ? 'var(--cr-text)' : 'var(--cr-text-muted)', fontSize: '13px', cursor: 'pointer', textTransform: 'capitalize', fontWeight: statusFilter === f ? 600 : 400 }}>
            {f}
          </button>
        ))}
      </div>

      {error && (
        <div style={{ padding: '12px 16px', borderRadius: 'var(--cr-radius-sm)', marginBottom: '16px', background: 'rgba(214, 69, 69, 0.08)', border: '1px solid var(--cr-danger)', color: 'var(--cr-danger)', fontSize: '13px' }}>
          {error}
        </div>
      )}

      {loading && sessions.length === 0 ? (
        <p style={{ color: 'var(--cr-text-muted)', textAlign: 'center', padding: '40px 0' }}>Loading sessions...</p>
      ) : filteredSessions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <p style={{ color: 'var(--cr-text-muted)', fontSize: '15px', marginBottom: '12px' }}>
            {sessions.length === 0 ? 'No sessions yet.' : 'No sessions match this filter.'}
          </p>
          {sessions.length === 0 && (
            <button onClick={() => setShowCreate(true)} style={{ padding: '10px 20px', borderRadius: 'var(--cr-radius-sm)', border: 'none', background: 'var(--cr-green-700)', color: '#fff', fontSize: '14px', fontWeight: 600, cursor: 'pointer' }}>
              Create Your First Session
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '14px' }}>
          {filteredSessions.map(s => <SessionCard key={s.session_id} session={s} onSelect={selectSession} />)}
        </div>
      )}

      {showCreate && <CreateSessionModal presets={presets} onClose={() => setShowCreate(false)} onCreate={handleCreate} />}
    </div>
  );
}

// ── Main Page (Router) ──────────────────────────────────────────────

export default function SwarmPage() {
  const [unlocked, setUnlocked] = useState(() => sessionStorage.getItem('swarm_unlocked') === '1');
  const [view, setView] = useState<'console' | 'blueprint'>('console');

  if (!unlocked) {
    return <VMStatusDashboard onUnlock={() => setUnlocked(true)} />;
  }

  if (view === 'blueprint') {
    return <BlueprintEditor onBack={() => setView('console')} />;
  }

  return (
    <SessionConsole
      onLock={() => { sessionStorage.removeItem('swarm_unlocked'); setUnlocked(false); }}
      onOpenBlueprint={() => setView('blueprint')}
    />
  );
}
