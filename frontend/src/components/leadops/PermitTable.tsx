import { MapPin, Calendar } from 'lucide-react';
import type { PermitRecord } from '../../types';

interface PermitTableProps {
  permits: PermitRecord[];
  loading: boolean;
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

export default function PermitTable({ permits, loading, total, page, pageSize, onPageChange }: PermitTableProps) {
  const totalPages = Math.ceil(total / pageSize);

  if (loading) {
    return (
      <div style={{ padding: 24, textAlign: 'center', color: 'var(--cr-text-muted)', fontSize: 14 }}>
        Loading permits...
      </div>
    );
  }

  if (permits.length === 0) {
    return (
      <div style={{ padding: 24, textAlign: 'center', color: 'var(--cr-text-muted)', fontSize: 14 }}>
        No permits found. Try adjusting your search criteria.
      </div>
    );
  }

  return (
    <div>
      <div style={{ overflowX: 'auto' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: 13,
          }}
        >
          <thead>
            <tr style={{ borderBottom: '1px solid var(--cr-border)' }}>
              <th style={thStyle}>Permit #</th>
              <th style={thStyle}>Address</th>
              <th style={thStyle}>Type</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Issued</th>
              <th style={thStyle}>Valuation</th>
              <th style={thStyle}>Tags</th>
            </tr>
          </thead>
          <tbody>
            {permits.map((permit) => (
              <tr key={permit.id} style={{ borderBottom: '1px solid var(--cr-border)' }}>
                <td style={tdStyle}>
                  <span style={{ fontWeight: 500, color: 'var(--cr-green-400)' }}>{permit.permit_number}</span>
                </td>
                <td style={tdStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <MapPin style={{ width: 12, height: 12, color: 'var(--cr-text-dim)', flexShrink: 0 }} />
                    <span>{permit.address}, {permit.city}, {permit.state} {permit.zip}</span>
                  </div>
                </td>
                <td style={tdStyle}>{permit.permit_type}</td>
                <td style={tdStyle}>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: 'var(--cr-radius-xs)',
                      fontSize: 11,
                      fontWeight: 500,
                      background: permit.status === 'active' ? 'rgba(34,197,94,0.15)' : 'rgba(200,200,200,0.1)',
                      color: permit.status === 'active' ? 'var(--cr-green-400)' : 'var(--cr-text-muted)',
                    }}
                  >
                    {permit.status}
                  </span>
                </td>
                <td style={tdStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Calendar style={{ width: 12, height: 12, color: 'var(--cr-text-dim)' }} />
                    <span>{permit.issue_date}</span>
                  </div>
                </td>
                <td style={tdStyle}>
                  {permit.valuation != null ? `$${permit.valuation.toLocaleString()}` : '--'}
                </td>
                <td style={tdStyle}>
                  <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                    {(permit.tags ?? []).map((tag: string) => (
                      <span
                        key={tag}
                        style={{
                          padding: '1px 6px',
                          borderRadius: 'var(--cr-radius-xs)',
                          fontSize: 10,
                          background: 'var(--cr-charcoal-dark)',
                          color: 'var(--cr-text-dim)',
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', marginTop: 8 }}>
          <span style={{ fontSize: 12, color: 'var(--cr-text-muted)' }}>
            {total.toLocaleString()} results -- page {page} of {totalPages}
          </span>
          <div style={{ display: 'flex', gap: 4 }}>
            <button
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
              style={paginationBtnStyle(page <= 1)}
            >
              Prev
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
              style={paginationBtnStyle(page >= totalPages)}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: 'left',
  padding: '8px 10px',
  fontSize: 11,
  fontWeight: 600,
  color: 'var(--cr-text-muted)',
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
};

const tdStyle: React.CSSProperties = {
  padding: '10px 10px',
  color: 'var(--cr-text)',
  verticalAlign: 'middle',
};

function paginationBtnStyle(disabled: boolean): React.CSSProperties {
  return {
    background: disabled ? 'var(--cr-charcoal-dark)' : 'var(--cr-charcoal-deep)',
    border: '1px solid var(--cr-border)',
    borderRadius: 'var(--cr-radius-xs)',
    padding: '4px 12px',
    color: disabled ? 'var(--cr-text-dim)' : 'var(--cr-text)',
    fontSize: 12,
    cursor: disabled ? 'not-allowed' : 'pointer',
  };
}
