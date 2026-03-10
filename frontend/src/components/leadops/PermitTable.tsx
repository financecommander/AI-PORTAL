import { useState } from 'react';
import { ChevronDown, ChevronRight, ChevronLeft } from 'lucide-react';
import type { PermitRecord } from '../../types';

interface Props {
  permits: PermitRecord[];
  total: number;
  loading: boolean;
  currentPage: number;
  totalPages: number;
  onNextPage: () => void;
  onPrevPage: () => void;
}

const tierColors: Record<string, { bg: string; text: string }> = {
  hot: { bg: '#fde8e8', text: '#c0392b' },
  warm: { bg: '#fef3e2', text: '#d35400' },
  cold: { bg: '#e8f4f8', text: '#2980b9' },
};

const tagColors: Record<string, string> = {
  'new-construction': '#27ae60',
  'renovation': '#8e44ad',
  'solar': '#f39c12',
  'adu': '#2980b9',
  'demolition': '#c0392b',
  'commercial': '#2c3e50',
  'residential': '#16a085',
  'high-value': '#e74c3c',
};

export default function PermitTable({ permits, total, loading, currentPage, totalPages, onNextPage, onPrevPage }: Props) {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: 'var(--cr-text-muted)' }}>
        Loading permits...
      </div>
    );
  }

  if (permits.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: 'var(--cr-text-muted)' }}>
        No permits found. Run an ingestion to populate data.
      </div>
    );
  }

  return (
    <div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--cr-border)' }}>
              <th style={thStyle}></th>
              <th style={thStyle}>Address</th>
              <th style={thStyle}>Type</th>
              <th style={thStyle}>Est. Cost</th>
              <th style={thStyle}>Score</th>
              <th style={thStyle}>Tier</th>
              <th style={thStyle}>Tags</th>
              <th style={thStyle}>Applicant</th>
            </tr>
          </thead>
          <tbody>
            {permits.map(p => (
              <>
                <tr
                  key={p.id}
                  onClick={() => setExpandedId(expandedId === p.id ? null : p.id)}
                  style={{
                    borderBottom: '1px solid var(--cr-border)',
                    cursor: 'pointer',
                    background: expandedId === p.id ? 'var(--cr-surface)' : 'transparent',
                    transition: 'background 100ms',
                  }}
                >
                  <td style={tdStyle}>
                    {expandedId === p.id
                      ? <ChevronDown style={{ width: 14, height: 14, color: 'var(--cr-text-muted)' }} />
                      : <ChevronRight style={{ width: 14, height: 14, color: 'var(--cr-text-muted)' }} />
                    }
                  </td>
                  <td style={tdStyle}>
                    <div style={{ fontWeight: 500 }}>{p.address || 'N/A'}</div>
                    <div style={{ fontSize: 11, color: 'var(--cr-text-muted)' }}>{p.permit_number}</div>
                  </td>
                  <td style={tdStyle}>{p.permit_type || '-'}</td>
                  <td style={tdStyle}>
                    {p.estimated_cost != null ? `$${p.estimated_cost.toLocaleString()}` : '-'}
                  </td>
                  <td style={tdStyle}>
                    <ScoreBadge score={p.lead_score} />
                  </td>
                  <td style={tdStyle}>
                    <TierBadge tier={p.lead_tier} />
                  </td>
                  <td style={tdStyle}>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {(p.ai_tags || []).slice(0, 3).map(tag => (
                        <span key={tag} style={{
                          padding: '2px 6px', borderRadius: 4, fontSize: 10, fontWeight: 600,
                          background: `${tagColors[tag] ?? '#95a5a6'}20`,
                          color: tagColors[tag] ?? '#95a5a6',
                        }}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td style={tdStyle}>
                    <div style={{ maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {p.applicant_name || '-'}
                    </div>
                  </td>
                </tr>
                {expandedId === p.id && (
                  <tr key={`${p.id}-detail`}>
                    <td colSpan={8} style={{ padding: '12px 20px', background: 'var(--cr-surface)', borderBottom: '1px solid var(--cr-border)' }}>
                      <PermitDetail permit={p} />
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0' }}>
        <div style={{ fontSize: 12, color: 'var(--cr-text-muted)' }}>
          {total.toLocaleString()} total permits
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={onPrevPage} disabled={currentPage <= 1} style={pageBtnStyle}>
            <ChevronLeft style={{ width: 14, height: 14 }} />
          </button>
          <span style={{ fontSize: 13, color: 'var(--cr-text-secondary)' }}>
            {currentPage} / {totalPages || 1}
          </span>
          <button onClick={onNextPage} disabled={currentPage >= totalPages} style={pageBtnStyle}>
            <ChevronRight style={{ width: 14, height: 14 }} />
          </button>
        </div>
      </div>
    </div>
  );
}

function ScoreBadge({ score }: { score: number | null }) {
  if (score == null) return <span style={{ color: 'var(--cr-text-muted)' }}>-</span>;
  const color = score >= 70 ? '#c0392b' : score >= 40 ? '#d35400' : '#2980b9';
  return (
    <span style={{ fontWeight: 700, color, fontFamily: "'Space Grotesk', sans-serif" }}>
      {score}
    </span>
  );
}

function TierBadge({ tier }: { tier: string }) {
  if (!tier) return <span style={{ color: 'var(--cr-text-muted)' }}>-</span>;
  const colors = tierColors[tier] ?? { bg: 'var(--cr-surface)', text: 'var(--cr-text-muted)' };
  return (
    <span style={{
      padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 600,
      background: colors.bg, color: colors.text, textTransform: 'uppercase',
    }}>
      {tier}
    </span>
  );
}

function PermitDetail({ permit: p }: { permit: PermitRecord }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
      <div>
        <DetailRow label="Description" value={p.work_description} />
        <DetailRow label="Property Type" value={p.ai_property_type} />
        <DetailRow label="Project Category" value={p.ai_project_category} />
        <DetailRow label="AI Summary" value={p.ai_summary} />
        <DetailRow label="Lead Rationale" value={p.lead_rationale} />
      </div>
      <div>
        <DetailRow label="Contractor" value={p.contractor_name} />
        <DetailRow label="Owner" value={p.owner_name} />
        <DetailRow label="Fee Paid" value={p.fee_paid != null ? `$${p.fee_paid.toLocaleString()}` : '-'} />
        <DetailRow label="Issue Date" value={p.issue_date ? new Date(p.issue_date).toLocaleDateString() : '-'} />
        <DetailRow label="Source" value={p.source_jurisdiction} />
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value?: string }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ fontSize: 11, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</div>
      <div style={{ fontSize: 13, color: 'var(--cr-text)' }}>{value || '-'}</div>
    </div>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: 'left', padding: '8px 12px', fontSize: 11,
  color: 'var(--cr-text-muted)', textTransform: 'uppercase',
  letterSpacing: '0.04em', fontWeight: 600,
};

const tdStyle: React.CSSProperties = {
  padding: '10px 12px', verticalAlign: 'middle',
};

const pageBtnStyle: React.CSSProperties = {
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  width: 28, height: 28, borderRadius: 'var(--cr-radius-xs)',
  border: '1px solid var(--cr-border)', background: 'var(--cr-white)',
  color: 'var(--cr-text-secondary)', cursor: 'pointer',
};
