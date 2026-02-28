import type { Specialist } from '../../types';

interface SpecialistHeaderProps {
  specialist: Specialist;
  messageCount: number;
}

export default function SpecialistHeader({ specialist, messageCount }: SpecialistHeaderProps) {
  return (
    <div
      style={{
        height: 56,
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'var(--cr-charcoal)',
        borderBottom: '1px solid var(--cr-border)',
        flexShrink: 0,
      }}
    >
      <div style={{ minWidth: 0, flex: 1, marginRight: 16 }}>
        <div
          style={{
            color: 'var(--cr-text)',
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 600,
            fontSize: 16,
            lineHeight: '20px',
          }}
        >
          {specialist.name}
        </div>
        <div
          style={{
            color: 'var(--cr-text-muted)',
            fontSize: 12,
            marginTop: 2,
            overflow: 'hidden',
            whiteSpace: 'nowrap',
            textOverflow: 'ellipsis',
          }}
        >
          {specialist.description}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
        <span
          style={{
            background: 'var(--cr-charcoal-deep)',
            color: 'var(--cr-text-muted)',
            fontSize: 11,
            padding: '3px 10px',
            borderRadius: 20,
            border: '1px solid var(--cr-border)',
          }}
        >
          {specialist.provider} / {specialist.model}
        </span>
        {messageCount > 0 && (
          <span
            style={{
              background: 'var(--cr-charcoal-deep)',
              color: 'var(--cr-text-muted)',
              fontSize: 11,
              padding: '3px 10px',
              borderRadius: 20,
              border: '1px solid var(--cr-border)',
            }}
          >
            {messageCount} msg{messageCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  );
}

