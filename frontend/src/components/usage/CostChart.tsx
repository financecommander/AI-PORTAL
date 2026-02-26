interface CostChartProps {
  data: { date: string; cost: number; count: number }[];
}

export default function CostChart({ data }: CostChartProps) {
  if (data.length === 0) {
    return (
      <div
        style={{
          background: 'var(--navy)',
          borderRadius: 12,
          padding: 20,
          color: '#667788',
          fontSize: 14,
        }}
      >
        No usage data yet
      </div>
    );
  }

  const maxCost = Math.max(...data.map((d) => d.cost), 0.0001);
  const totalCost = data.reduce((sum, d) => sum + d.cost, 0);
  const totalCount = data.reduce((sum, d) => sum + d.count, 0);

  return (
    <div style={{ background: 'var(--navy)', borderRadius: 12, padding: 20 }}>
      <div style={{ marginBottom: 8, fontSize: 13, fontWeight: 600, color: '#8899AA', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Daily Cost — Last 7 Days
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {data.map((d) => (
          <div key={d.date} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, fontSize: 12, color: '#8899AA', flexShrink: 0 }}>{d.date}</div>
            <div style={{ flex: 1, background: 'var(--navy-light)', borderRadius: 4, height: 18, overflow: 'hidden' }}>
              <div
                style={{
                  width: `${(d.cost / maxCost) * 100}%`,
                  height: '100%',
                  background: 'var(--blue)',
                  borderRadius: 4,
                  minWidth: d.cost > 0 ? 4 : 0,
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
            <div style={{ width: 52, fontSize: 12, color: '#E0E0E0', textAlign: 'right', flexShrink: 0 }}>
              ${d.cost.toFixed(2)}
            </div>
          </div>
        ))}
      </div>
      <div
        style={{
          marginTop: 12,
          paddingTop: 10,
          borderTop: '1px solid var(--navy-light)',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: 12,
          color: '#8899AA',
        }}
      >
        <span>Total: {totalCount} queries</span>
        <span style={{ color: 'var(--blue)', fontWeight: 600 }}>${totalCost.toFixed(4)}</span>
      </div>
    </div>
  );
}
