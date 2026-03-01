import type { UsageLog } from '../../types';

interface UsageTableProps { logs: UsageLog[]; }

function relativeTime(timestamp: string): string {
  if (!timestamp) return '—';
  const parsed = new Date(timestamp).getTime();
  if (isNaN(parsed)) return '—';
  const diff = Date.now() - parsed;
  const s = Math.floor(diff / 1000);
  if (s < 60) return 'just now';
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return d === 1 ? 'yesterday' : `${d}d ago`;
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

function costColor(cost: number): string {
  if (cost < 0.05) return 'var(--cr-green-600)';
  if (cost <= 0.5) return 'var(--cr-gold-500)';
  return 'var(--cr-danger)';
}

export default function UsageTable({ logs }: UsageTableProps) {
  const rows = logs.slice(0, 50);

  if (rows.length === 0) return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 40, textAlign: 'center', color: 'var(--cr-text-muted)', fontSize: 14 }}>
      No usage logs yet — start chatting to see your usage here
    </div>
  );

  const th: React.CSSProperties = {
    background: 'var(--cr-surface-2)', color: 'var(--cr-text-muted)', fontSize: 11, textTransform: 'uppercase',
    letterSpacing: '0.06em', padding: '8px 12px', textAlign: 'left', fontWeight: 600,
    borderBottom: '1px solid var(--cr-border)',
  };

  const td: React.CSSProperties = { padding: '8px 12px', borderBottom: '1px solid var(--cr-border)' };

  return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>
            <th style={th}>Time</th>
            <th style={th}>Specialist</th>
            <th style={th}>Provider</th>
            <th style={th}>Model</th>
            <th style={th}>Tokens</th>
            <th style={th}>Cost</th>
            <th style={th}>Latency</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((log, i) => (
            <tr key={log.id} style={{ background: i % 2 === 0 ? 'var(--cr-white)' : 'var(--cr-surface)' }}>
              <td style={{ ...td, color: 'var(--cr-text-muted)', whiteSpace: 'nowrap' }}>{relativeTime(log.timestamp)}</td>
              <td style={{ ...td, color: 'var(--cr-text)' }}>{log.specialist_id ?? '—'}</td>
              <td style={{ ...td, color: 'var(--cr-text)' }}>{log.provider}</td>
              <td style={{ ...td, color: 'var(--cr-text-muted)', fontFamily: 'monospace', fontSize: 12 }}>{log.model}</td>
              <td style={{ ...td, color: 'var(--cr-text)' }}>{formatTokens(log.input_tokens + log.output_tokens)}</td>
              <td style={{ ...td, color: costColor(log.cost_usd), fontWeight: 600 }}>${log.cost_usd.toFixed(4)}</td>
              <td style={{ ...td, color: 'var(--cr-text-muted)' }}>{log.latency_ms >= 1000 ? `${(log.latency_ms / 1000).toFixed(1)}s` : `${log.latency_ms}ms`}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

