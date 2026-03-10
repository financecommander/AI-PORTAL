import type { PermitStats } from '../../types';

interface Props {
  stats: PermitStats | null;
  loading: boolean;
}

export default function LeadOpsStats({ stats, loading }: Props) {
  if (loading || !stats) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        {[1, 2, 3, 4].map(i => (
          <div key={i} style={{
            padding: '16px 20px', borderRadius: 'var(--cr-radius-sm)',
            border: '1px solid var(--cr-border)', background: 'var(--cr-surface)',
          }}>
            <div style={{ height: 14, width: 60, background: 'var(--cr-border)', borderRadius: 4, marginBottom: 8 }} />
            <div style={{ height: 24, width: 40, background: 'var(--cr-border)', borderRadius: 4 }} />
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    { label: 'Total Permits', value: stats.total_permits.toLocaleString(), color: 'var(--cr-green-700)' },
    { label: 'Hot Leads', value: (stats.by_tier?.hot ?? 0).toLocaleString(), color: '#e74c3c' },
    { label: 'Warm Leads', value: (stats.by_tier?.warm ?? 0).toLocaleString(), color: '#f39c12' },
    { label: 'Avg Score', value: stats.avg_lead_score.toString(), color: 'var(--cr-text)' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
      {cards.map(c => (
        <div key={c.label} style={{
          padding: '16px 20px', borderRadius: 'var(--cr-radius-sm)',
          border: '1px solid var(--cr-border)', background: 'var(--cr-white)',
        }}>
          <div style={{ fontSize: 12, color: 'var(--cr-text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            {c.label}
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: c.color, fontFamily: "'Space Grotesk', sans-serif" }}>
            {c.value}
          </div>
        </div>
      ))}
    </div>
  );
}
