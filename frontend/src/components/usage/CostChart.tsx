interface CostChartProps { data: { date: string; cost: number; count: number }[]; }

export default function CostChart({ data }: CostChartProps) {
  if (data.length === 0) return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 20, color: 'var(--cr-text-muted)', fontSize: 14 }}>
      No usage data yet
    </div>
  );

  const maxCost = Math.max(...data.map((d) => d.cost), 0.0001);
  const totalCost = data.reduce((sum, d) => sum + d.cost, 0);
  const totalCount = data.reduce((sum, d) => sum + d.count, 0);

  return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 20 }}>
      <div style={{ marginBottom: 12, fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        Daily Cost — Last 7 Days
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {data.map((d) => (
          <div key={d.date} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, fontSize: 12, color: 'var(--cr-text-muted)', flexShrink: 0 }}>{d.date}</div>
            <div style={{ flex: 1, background: 'var(--cr-surface-2)', borderRadius: 3, height: 16, overflow: 'hidden' }}>
              <div style={{ width: `${(d.cost / maxCost) * 100}%`, height: '100%', background: 'var(--cr-green-600)', borderRadius: 3, minWidth: d.cost > 0 ? 3 : 0, transition: 'width 300ms ease' }} />
            </div>
            <div style={{ width: 52, fontSize: 12, color: 'var(--cr-text)', textAlign: 'right', flexShrink: 0, fontWeight: 500 }}>
              ${d.cost.toFixed(2)}
            </div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--cr-border)', display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--cr-text-muted)' }}>
        <span>Total: {totalCount} queries</span>
        <span style={{ color: 'var(--cr-green-900)', fontWeight: 600 }}>${totalCost.toFixed(4)}</span>
      </div>
    </div>
  );
}

