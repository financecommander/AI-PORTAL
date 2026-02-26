import type { Specialist } from '../../types';

interface SpecialistHeaderProps {
  specialist: Specialist;
  messageCount: number;
}

export default function SpecialistHeader({ specialist, messageCount }: SpecialistHeaderProps) {
  return (
    <div
      style={{
        height: 60,
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'var(--navy)',
        borderBottom: '1px solid #2A3A5C',
        flexShrink: 0,
      }}
    >
      <div style={{ minWidth: 0, flex: 1, marginRight: 16 }}>
        <div
          style={{
            color: '#FFFFFF',
            fontWeight: 600,
            fontSize: 18,
            lineHeight: '22px',
          }}
        >
          {specialist.name}
        </div>
        <div
          style={{
            color: '#8899AA',
            fontSize: 13,
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
            background: '#2A3A5C',
            color: '#8899AA',
            fontSize: 12,
            padding: '3px 10px',
            borderRadius: 20,
          }}
        >
          {specialist.provider} / {specialist.model}
        </span>
        {messageCount > 0 && (
          <span
            style={{
              background: '#2A3A5C',
              color: '#8899AA',
              fontSize: 12,
              padding: '3px 10px',
              borderRadius: 20,
            }}
          >
            {messageCount} msg{messageCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  );
}
