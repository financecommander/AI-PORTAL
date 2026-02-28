import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Crown, Sparkles, Zap } from 'lucide-react';
import type { LLMProvider } from '../../types';

// Provider accent colors
const PROVIDER_COLORS: Record<string, string> = {
  openai: '#10A37F',
  anthropic: '#D97706',
  google: '#4285F4',
  grok: '#EF4444',
  deepseek: '#6366F1',
  mistral: '#F97316',
  groq: '#F97316',  // orange (Groq brand)
};

// Tier config
const TIER_CONFIG: Record<string, { icon: typeof Crown; color: string; label: string }> = {
  top: { icon: Crown, color: '#F59E0B', label: 'TOP' },
  mid: { icon: Sparkles, color: '#6B7280', label: 'MID' },
  budget: { icon: Zap, color: '#22C55E', label: '💰' },
};

interface ModelSelectorProps {
  providers: LLMProvider[];
  selectedProvider: string | null;
  selectedModel: string | null;
  onSelect: (provider: string, model: string) => void;
  mode: 'grid' | 'compact';
}

function formatPrice(input?: number, output?: number): string {
  if (input == null || output == null) return '';
  if (input < 1) return `$${input.toFixed(2)}/$${output.toFixed(2)}`;
  return `$${input.toFixed(2)}/$${output.toFixed(0)}`;
}

// ── Grid Mode ───────────────────────────────────────────────────

function GridSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelect,
}: Omit<ModelSelectorProps, 'mode'>) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '12px',
        maxWidth: '960px',
        width: '100%',
      }}
    >
      {providers.map((prov) => {
        const accent = PROVIDER_COLORS[prov.id] || '#2E75B6';
        return (
          <div
            key={prov.id}
            style={{
              background: 'var(--navy-light)',
              borderRadius: '12px',
              border: '1px solid #2A3A5C',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
            }}
          >
            {/* Provider header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: accent,
                }}
              />
              <span
                style={{
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#C8D0D8',
                  letterSpacing: '0.02em',
                }}
              >
                {prov.name}
              </span>
            </div>

            {/* Models */}
            {prov.models.map((m) => {
              const isSelected = selectedProvider === prov.id && selectedModel === m.id;
              const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
              const TierIcon = tier.icon;
              return (
                <button
                  key={m.id}
                  onClick={() => onSelect(prov.id, m.id)}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: isSelected ? `2px solid ${accent}` : '1px solid #2A3A5C',
                    background: isSelected ? `${accent}15` : 'var(--navy-dark)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    width: '100%',
                    transition: 'all 150ms',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TierIcon style={{ width: '14px', height: '14px', color: tier.color, flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div
                        style={{
                          fontSize: '13px',
                          fontWeight: 500,
                          color: isSelected ? '#FFFFFF' : '#D0D8E0',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {m.name}
                      </div>
                    </div>
                    {m.context && (
                      <span
                        style={{
                          fontSize: '10px',
                          fontWeight: 500,
                          color: '#8899AA',
                          background: '#1A2A44',
                          padding: '1px 5px',
                          borderRadius: '3px',
                          flexShrink: 0,
                        }}
                      >
                        {m.context}
                      </span>
                    )}
                  </div>
                  {m.description && (
                    <div
                      style={{
                        fontSize: '11px',
                        color: '#667788',
                        lineHeight: '1.3',
                        overflow: 'hidden',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {m.description}
                    </div>
                  )}
                  <div style={{ fontSize: '11px', color: '#667788' }}>
                    {formatPrice(m.input_price, m.output_price)}/1M
                  </div>
                </button>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

// ── Compact Mode ────────────────────────────────────────────────

function CompactSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelect,
}: Omit<ModelSelectorProps, 'mode'>) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isOpen]);

  // Find selected model info
  let selectedModelName = 'Select model';
  let selectedAccent = '#2E75B6';
  let selectedContext = '';
  for (const prov of providers) {
    for (const m of prov.models) {
      if (prov.id === selectedProvider && m.id === selectedModel) {
        selectedModelName = m.name;
        selectedAccent = PROVIDER_COLORS[prov.id] || '#2E75B6';
        selectedContext = m.context || '';
      }
    }
  }

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 14px',
          borderRadius: '8px',
          border: '1px solid #2A3A5C',
          background: 'var(--navy-light)',
          cursor: 'pointer',
          transition: 'all 150ms',
        }}
      >
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: selectedAccent,
          }}
        />
        <span style={{ fontSize: '13px', fontWeight: 500, color: '#FFFFFF' }}>
          {selectedModelName}
        </span>
        {selectedContext && (
          <span style={{ fontSize: '10px', color: '#667788' }}>
            {selectedContext}
          </span>
        )}
        <ChevronDown
          style={{
            width: '14px',
            height: '14px',
            color: '#8899AA',
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0)',
            transition: 'transform 150ms',
          }}
        />
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            minWidth: '320px',
            maxHeight: '420px',
            overflowY: 'auto',
            background: 'var(--navy)',
            border: '1px solid #2A3A5C',
            borderRadius: '12px',
            padding: '8px',
            zIndex: 50,
            boxShadow: '0 12px 32px rgba(0,0,0,0.4)',
          }}
        >
          {providers.map((prov) => {
            const accent = PROVIDER_COLORS[prov.id] || '#2E75B6';
            return (
              <div key={prov.id}>
                <div
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    color: '#667788',
                    padding: '8px 10px 4px',
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                  }}
                >
                  {prov.name}
                </div>
                {prov.models.map((m) => {
                  const isActive = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button
                      key={m.id}
                      onClick={() => {
                        onSelect(prov.id, m.id);
                        setIsOpen(false);
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        width: '100%',
                        padding: '8px 10px',
                        borderRadius: '6px',
                        border: 'none',
                        background: isActive ? `${accent}15` : 'transparent',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'background 100ms',
                      }}
                      onMouseEnter={(e) => {
                        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'var(--navy-light)';
                      }}
                      onMouseLeave={(e) => {
                        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'transparent';
                      }}
                    >
                      <TierIcon style={{ width: '13px', height: '13px', color: tier.color, flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <span
                          style={{
                            fontSize: '13px',
                            fontWeight: isActive ? 500 : 400,
                            color: isActive ? '#FFFFFF' : '#C0C8D0',
                          }}
                        >
                          {m.name}
                        </span>
                        {m.description && (
                          <div
                            style={{
                              fontSize: '10px',
                              color: '#556677',
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              marginTop: '1px',
                            }}
                          >
                            {m.description}
                          </div>
                        )}
                      </div>
                      {m.context && (
                        <span
                          style={{
                            fontSize: '10px',
                            color: '#667788',
                            background: '#1A2A44',
                            padding: '1px 4px',
                            borderRadius: '3px',
                            flexShrink: 0,
                          }}
                        >
                          {m.context}
                        </span>
                      )}
                      <span style={{ fontSize: '11px', color: '#667788', flexShrink: 0 }}>
                        {formatPrice(m.input_price, m.output_price)}
                      </span>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── Export ───────────────────────────────────────────────────────

export default function ModelSelector(props: ModelSelectorProps) {
  return props.mode === 'grid' ? (
    <GridSelector {...props} />
  ) : (
    <CompactSelector {...props} />
  );
}
