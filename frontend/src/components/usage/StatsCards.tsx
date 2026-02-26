import type { UsageLog } from '../../types';

interface StatsCardsProps {
  logs: UsageLog[];
}

function formatTokenCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

export default function StatsCards({ logs }: StatsCardsProps) {
  const totalCost = logs.reduce((s, l) => s + l.cost_usd, 0);
  const totalTokens = logs.reduce((s, l) => s + l.input_tokens + l.output_tokens, 0);
  const avgLatency = logs.length > 0 ? logs.reduce((s, l) => s + l.latency_ms, 0) / logs.length : 0;
  const totalQueries = logs.length;

  const cards = [
    { label: 'Total Cost', value: `$${totalCost.toFixed(4)}` },
    { label: 'Total Tokens', value: formatTokenCount(totalTokens) },
    { label: 'Avg Latency', value: `${(avgLatency / 1000).toFixed(2)}s` },
    { label: 'Total Queries', value: String(totalQueries) },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
      {cards.map((card) => (
        <div
          key={card.label}
          style={{
            background: 'var(--navy)',
            borderRadius: 12,
            padding: 20,
          }}
        >
          <div style={{ fontSize: 11, color: '#8899AA', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
            {card.label}
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--blue)' }}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}
