import { useState } from 'react';
import { Search } from 'lucide-react';
import type { PermitSearchParams } from '../../types';

interface PermitFiltersProps {
  onSearch: (params: PermitSearchParams) => void;
  loading: boolean;
}

export default function PermitFilters({ onSearch, loading }: PermitFiltersProps) {
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [permitType, setPermitType] = useState('');
  const [status, setStatus] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      city: city || undefined,
      state: state || undefined,
      permit_type: permitType || undefined,
      status: status || undefined,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: 'flex',
        gap: 8,
        flexWrap: 'wrap',
        alignItems: 'flex-end',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <label style={{ fontSize: 11, color: 'var(--cr-text-muted)', textTransform: 'uppercase' }}>City</label>
        <input
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Any"
          style={{
            background: 'var(--cr-charcoal-dark)',
            border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius-xs)',
            padding: '6px 10px',
            color: 'var(--cr-text)',
            fontSize: 13,
            width: 140,
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <label style={{ fontSize: 11, color: 'var(--cr-text-muted)', textTransform: 'uppercase' }}>State</label>
        <input
          value={state}
          onChange={(e) => setState(e.target.value)}
          placeholder="Any"
          style={{
            background: 'var(--cr-charcoal-dark)',
            border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius-xs)',
            padding: '6px 10px',
            color: 'var(--cr-text)',
            fontSize: 13,
            width: 80,
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <label style={{ fontSize: 11, color: 'var(--cr-text-muted)', textTransform: 'uppercase' }}>Type</label>
        <input
          value={permitType}
          onChange={(e) => setPermitType(e.target.value)}
          placeholder="Any"
          style={{
            background: 'var(--cr-charcoal-dark)',
            border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius-xs)',
            padding: '6px 10px',
            color: 'var(--cr-text)',
            fontSize: 13,
            width: 120,
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <label style={{ fontSize: 11, color: 'var(--cr-text-muted)', textTransform: 'uppercase' }}>Status</label>
        <input
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          placeholder="Any"
          style={{
            background: 'var(--cr-charcoal-dark)',
            border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius-xs)',
            padding: '6px 10px',
            color: 'var(--cr-text)',
            fontSize: 13,
            width: 100,
          }}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          background: loading ? 'var(--cr-border)' : 'var(--cr-green-600)',
          border: 'none',
          borderRadius: 'var(--cr-radius-xs)',
          padding: '7px 14px',
          color: 'var(--cr-text)',
          fontSize: 13,
          cursor: loading ? 'not-allowed' : 'pointer',
          fontWeight: 500,
        }}
      >
        <Search style={{ width: 14, height: 14 }} />
        Search
      </button>
    </form>
  );
}
