import type { UsageLog } from '../../types';

interface StatsCardsProps { logs: UsageLog[]; }

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
    { label: 'Total Cost', value: `$${totalCost.toFixed(4)}`, accent: 'var(--cr-green-600)' },
    { label: 'Total Tokens', value: formatTokenCount(totalTokens), accent: 'var(--cr-green-900)' },
    { label: 'Avg Latency', value: `${(avgLatency / 1000).toFixed(2)}s`, accent: 'var(--cr-text)' },
    { label: 'Total Queries', value: String(totalQueries), accent: 'var(--cr-text)' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
      {cards.map((card) => (
        <div key={card.label} style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 20 }}>
          <div style={{ fontSize: 11, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8, fontWeight: 600 }}>
            {card.label}
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: card.accent, fontFamily: "'Space Grotesk', sans-serif" }}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}

