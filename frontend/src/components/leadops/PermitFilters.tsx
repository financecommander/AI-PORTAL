import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import type { PermitSearchParams } from '../../types';

interface Props {
  onSearch: (params: Partial<PermitSearchParams>) => void;
}

export default function PermitFilters({ onSearch }: Props) {
  const [q, setQ] = useState('');
  const [tier, setTier] = useState('');
  const [city, setCity] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [minCost, setMinCost] = useState('');
  const [maxCost, setMaxCost] = useState('');

  const handleSearch = () => {
    onSearch({
      q: q || undefined,
      lead_tier: tier || undefined,
      city: city || undefined,
      min_cost: minCost ? Number(minCost) : undefined,
      max_cost: maxCost ? Number(maxCost) : undefined,
      offset: 0,
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };

  const handleReset = () => {
    setQ('');
    setTier('');
    setCity('');
    setMinCost('');
    setMaxCost('');
    onSearch({ q: undefined, lead_tier: undefined, city: undefined, min_cost: undefined, max_cost: undefined, offset: 0 });
  };

  const selectStyle: React.CSSProperties = {
    padding: '8px 12px',
    borderRadius: 'var(--cr-radius-xs)',
    border: '1px solid var(--cr-border)',
    background: 'var(--cr-white)',
    color: 'var(--cr-text)',
    fontSize: 13,
    outline: 'none',
  };

  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        {/* Search input */}
        <div style={{ position: 'relative', flex: '1 1 200px', minWidth: 200 }}>
          <Search style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', width: 16, height: 16, color: 'var(--cr-text-muted)' }} />
          <input
            type="text"
            value={q}
            onChange={e => setQ(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search permits..."
            style={{
              width: '100%',
              padding: '8px 12px 8px 32px',
              borderRadius: 'var(--cr-radius-xs)',
              border: '1px solid var(--cr-border)',
              background: 'var(--cr-white)',
              color: 'var(--cr-text)',
              fontSize: 13,
              outline: 'none',
            }}
          />
        </div>

        {/* Tier filter */}
        <select value={tier} onChange={e => setTier(e.target.value)} style={selectStyle}>
          <option value="">All Tiers</option>
          <option value="hot">Hot</option>
          <option value="warm">Warm</option>
          <option value="cold">Cold</option>
        </select>

        {/* City filter */}
        <select value={city} onChange={e => setCity(e.target.value)} style={selectStyle}>
          <option value="">All Cities</option>
          <option value="Chicago">Chicago</option>
        </select>

        {/* Advanced toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          style={{
            display: 'flex', alignItems: 'center', gap: 4,
            padding: '8px 12px', borderRadius: 'var(--cr-radius-xs)',
            border: '1px solid var(--cr-border)', background: showAdvanced ? 'var(--cr-surface)' : 'var(--cr-white)',
            color: 'var(--cr-text-secondary)', fontSize: 13, cursor: 'pointer',
          }}
        >
          <Filter style={{ width: 14, height: 14 }} />
          Filters
        </button>

        {/* Search button */}
        <button
          onClick={handleSearch}
          style={{
            padding: '8px 16px', borderRadius: 'var(--cr-radius-xs)',
            border: 'none', background: 'var(--cr-green-900)',
            color: '#fff', fontSize: 13, fontWeight: 600, cursor: 'pointer',
          }}
        >
          Search
        </button>

        {/* Reset */}
        <button
          onClick={handleReset}
          style={{
            padding: '8px 12px', borderRadius: 'var(--cr-radius-xs)',
            border: '1px solid var(--cr-border)', background: 'var(--cr-white)',
            color: 'var(--cr-text-muted)', fontSize: 13, cursor: 'pointer',
          }}
        >
          Reset
        </button>
      </div>

      {/* Advanced filters */}
      {showAdvanced && (
        <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
          <input
            type="number"
            value={minCost}
            onChange={e => setMinCost(e.target.value)}
            placeholder="Min cost"
            style={{ ...selectStyle, width: 120 }}
          />
          <input
            type="number"
            value={maxCost}
            onChange={e => setMaxCost(e.target.value)}
            placeholder="Max cost"
            style={{ ...selectStyle, width: 120 }}
          />
        </div>
      )}
    </div>
  );
}
