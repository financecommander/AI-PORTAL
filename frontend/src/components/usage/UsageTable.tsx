import type { UsageLog } from '../../types';

interface UsageTableProps {
  logs: UsageLog[];
}

function relativeTime(timestamp: string): string {
  if (!timestamp) return '—';
  const parsed = new Date(timestamp).getTime();
  if (isNaN(parsed)) return '—';
  const diff = Date.now() - parsed;
  const seconds = Math.floor(diff / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return 'yesterday';
  return `${days}d ago`;
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

function costColor(cost: number): string {
  if (cost < 0.05) return 'var(--green)';
  if (cost <= 0.5) return 'var(--orange)';
  return 'var(--red)';
}

export default function UsageTable({ logs }: UsageTableProps) {
  const rows = logs.slice(0, 50);

  if (rows.length === 0) {
    return (
      <div
        style={{
          background: 'var(--navy)',
          borderRadius: 12,
          padding: 40,
          textAlign: 'center',
          color: '#667788',
          fontSize: 14,
        }}
      >
        No usage logs yet — start chatting to see your usage here
      </div>
    );
  }

  const headerStyle: React.CSSProperties = {
    background: 'var(--navy-dark)',
    color: '#8899AA',
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    padding: '10px 14px',
    textAlign: 'left',
    fontWeight: 600,
  };

  return (
    <div style={{ background: 'var(--navy)', borderRadius: 12, overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>
            <th style={headerStyle}>Time</th>
            <th style={headerStyle}>Specialist</th>
            <th style={headerStyle}>Provider</th>
            <th style={headerStyle}>Model</th>
            <th style={headerStyle}>Tokens</th>
            <th style={headerStyle}>Cost</th>
            <th style={headerStyle}>Latency</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((log, i) => (
            <tr
              key={log.id}
              style={{
                background: i % 2 === 0 ? 'var(--navy)' : 'rgba(36,54,86,0.5)',
              }}
            >
              <td style={{ padding: '9px 14px', color: '#8899AA', whiteSpace: 'nowrap' }}>
                {relativeTime(log.timestamp)}
              </td>
              <td style={{ padding: '9px 14px', color: '#E0E0E0' }}>
                {log.specialist_id ?? '—'}
              </td>
              <td style={{ padding: '9px 14px', color: '#E0E0E0' }}>{log.provider}</td>
              <td style={{ padding: '9px 14px', color: '#8899AA', fontFamily: 'monospace', fontSize: 12 }}>
                {log.model}
              </td>
              <td style={{ padding: '9px 14px', color: '#E0E0E0' }}>
                {formatTokens(log.input_tokens + log.output_tokens)}
              </td>
              <td style={{ padding: '9px 14px', color: costColor(log.cost_usd), fontWeight: 600 }}>
                ${log.cost_usd.toFixed(4)}
              </td>
              <td style={{ padding: '9px 14px', color: '#8899AA' }}>
                {log.latency_ms >= 1000
                  ? `${(log.latency_ms / 1000).toFixed(1)}s`
                  : `${log.latency_ms}ms`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
