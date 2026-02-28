import { Brain } from 'lucide-react';

interface PipelineCardProps {
  pipeline: { name: string; display_name: string; description: string; agents: string[]; type: string };
  onSelect: (name: string) => void;
  isSelected: boolean;
}

export default function PipelineCard({ pipeline, onSelect, isSelected }: PipelineCardProps) {
  return (
    <div
      onClick={() => onSelect(pipeline.name)}
      style={{
        background: 'var(--cr-charcoal-deep)',
        border: `1px solid ${isSelected ? 'var(--cr-green-600)' : 'transparent'}`,
        boxShadow: isSelected ? '0 0 12px rgba(34, 197, 94, 0.2)' : undefined,
        borderRadius: 'var(--cr-radius)',
        padding: '20px',
        cursor: 'pointer',
        transition: 'border-color 200ms, box-shadow 200ms',
      }}
      onMouseEnter={e => {
        if (!isSelected) {
          (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--cr-green-600)';
        }
      }}
      onMouseLeave={e => {
        if (!isSelected) {
          (e.currentTarget as HTMLDivElement).style.borderColor = 'transparent';
        }
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
        <Brain style={{ width: 20, height: 20, color: 'var(--cr-green-600)', flexShrink: 0 }} />
        <span style={{ color: 'var(--cr-text)', fontWeight: 600, fontSize: '15px' }}>{pipeline.display_name}</span>
      </div>

      <p
        style={{
          color: 'var(--cr-text-muted)',
          fontSize: '13px',
          marginBottom: '12px',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {pipeline.description}
      </p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '12px' }}>
        {pipeline.agents.map(agent => (
          <span
            key={agent}
            style={{
              background: 'var(--cr-charcoal-dark)',
              color: 'var(--cr-text-muted)',
              fontSize: '11px',
              borderRadius: 'var(--cr-radius-xs)',
              padding: '2px 6px',
            }}
          >
            {agent}
          </span>
        ))}
      </div>

      <div
        style={{
          color: isSelected ? 'var(--cr-green-600)' : 'var(--cr-text-dim)',
          fontSize: '13px',
          fontWeight: 500,
          transition: 'color 200ms',
        }}
      >
        {isSelected ? '✓ Selected' : 'Run Pipeline →'}
      </div>
    </div>
  );
}
