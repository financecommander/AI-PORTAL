import type { PermitStats } from '../../types';

interface LeadOpsStatsProps {
  stats: PermitStats | null;
  loading: boolean;
}

export default function LeadOpsStats({ stats, loading }: LeadOpsStatsProps) {
  if (loading) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            style={{
              background: 'var(--cr-charcoal-deep)',
              borderRadius: 'var(--cr-radius)',
              padding: 16,
              height: 80,
              opacity: 0.5,
            }}
          />
        ))}
      </div>
    );
  }

  if (!stats) return null;

  const cards = [
    { label: 'Total Permits', value: stats.total_permits.toLocaleString() },
    { label: 'Active', value: stats.active_permits.toLocaleString() },
    { label: 'Expired', value: stats.expired_permits.toLocaleString() },
    { label: 'Avg Valuation', value: `$${stats.avg_valuation.toLocaleString(undefined, { maximumFractionDigits: 0 })}` },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
      {cards.map((card) => (
        <div
          key={card.label}
          style={{
            background: 'var(--cr-charcoal-deep)',
            borderRadius: 'var(--cr-radius)',
            padding: 16,
          }}
        >
          <div style={{ fontSize: 11, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>
            {card.label}
          </div>
          <div style={{ fontSize: 22, fontWeight: 600, color: 'var(--cr-text)' }}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}
