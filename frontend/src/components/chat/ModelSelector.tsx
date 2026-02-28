import { useState, useRef, useEffect } from 'react';
import { ChevronDown, ChevronRight, Crown, Sparkles, Zap } from 'lucide-react';
import type { LLMProvider } from '../../types';

const PROVIDER_COLORS: Record<string, string> = {
  openai: '#3E9B5F', anthropic: '#F2A41F', google: '#4285F4',
  grok: '#D64545', deepseek: '#7C8CF5', mistral: '#E8853D', groq: '#E8853D',
};

const TIER_CONFIG: Record<string, { icon: typeof Crown; color: string }> = {
  top: { icon: Crown, color: '#F2A41F' },
  mid: { icon: Sparkles, color: 'var(--cr-text-muted)' },
  budget: { icon: Zap, color: 'var(--cr-green-600)' },
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

function GridSelector({ providers, selectedProvider, selectedModel, onSelect }: Omit<ModelSelectorProps, 'mode'>) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    providers.forEach((p, i) => { init[p.id] = i === 0; });
    return init;
  });

  useEffect(() => {
    if (selectedProvider) setExpanded((prev) => ({ ...prev, [selectedProvider]: true }));
  }, [selectedProvider]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxWidth: 700, width: '100%' }}>
      {providers.map((prov) => {
        const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
        const isExpanded = expanded[prov.id] ?? false;
        return (
          <div key={prov.id} style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', overflow: 'hidden' }}>
            <button
              onClick={() => setExpanded((prev) => ({ ...prev, [prov.id]: !prev[prov.id] }))}
              style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: '12px 16px', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: accent, flexShrink: 0 }} />
              <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--cr-text)', flex: 1, textAlign: 'left', fontFamily: "'Space Grotesk', sans-serif" }}>{prov.name}</span>
              <span style={{ fontSize: 11, color: 'var(--cr-text-muted)', marginRight: 4 }}>{prov.models.length} model{prov.models.length !== 1 ? 's' : ''}</span>
              {isExpanded ? <ChevronDown style={{ width: 16, height: 16, color: 'var(--cr-text-muted)' }} /> : <ChevronRight style={{ width: 16, height: 16, color: 'var(--cr-text-muted)' }} />}
            </button>
            {isExpanded && (
              <div style={{ padding: '0 8px 8px' }}>
                {prov.models.map((m) => {
                  const isSelected = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button key={m.id} onClick={() => onSelect(prov.id, m.id)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: '10px 12px', margin: '2px 0',
                        borderRadius: 'var(--cr-radius-sm)', border: isSelected ? `1px solid ${accent}` : '1px solid transparent',
                        background: isSelected ? `${accent}10` : 'transparent', cursor: 'pointer', textAlign: 'left', transition: 'all 100ms',
                      }}
                      onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.background = 'var(--cr-surface)'; }}
                      onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.background = 'transparent'; }}
                    >
                      <TierIcon style={{ width: 14, height: 14, color: tier.color, flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: isSelected ? 600 : 400, color: 'var(--cr-text)' }}>{m.name}</div>
                        {m.description && <div style={{ fontSize: 11, color: 'var(--cr-text-muted)', marginTop: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{m.description}</div>}
                      </div>
                      {m.context && <span style={{ fontSize: 10, color: 'var(--cr-text-muted)', background: 'var(--cr-surface-2)', padding: '2px 6px', borderRadius: 'var(--cr-radius-xs)', flexShrink: 0 }}>{m.context}</span>}
                      <span style={{ fontSize: 11, color: 'var(--cr-text-muted)', flexShrink: 0 }}>{formatPrice(m.input_price, m.output_price)}/1M</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function CompactSelector({ providers, selectedProvider, selectedModel, onSelect }: Omit<ModelSelectorProps, 'mode'>) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => { if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) setIsOpen(false); };
    if (isOpen) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isOpen]);

  let selectedModelName = 'Select model';
  let selectedAccent = 'var(--cr-green-600)';
  for (const prov of providers) {
    for (const m of prov.models) {
      if (prov.id === selectedProvider && m.id === selectedModel) {
        selectedModelName = m.name;
        selectedAccent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
      }
    }
  }

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button onClick={() => setIsOpen(!isOpen)}
        style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'var(--cr-white)', cursor: 'pointer' }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: selectedAccent }} />
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--cr-text)' }}>{selectedModelName}</span>
        <ChevronDown style={{ width: 14, height: 14, color: 'var(--cr-text-muted)', transform: isOpen ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 150ms' }} />
      </button>
      {isOpen && (
        <div style={{ position: 'absolute', top: 'calc(100% + 6px)', left: 0, minWidth: 340, maxHeight: 420, overflowY: 'auto', background: 'var(--cr-white)', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius)', padding: 8, zIndex: 50, boxShadow: '0 8px 30px rgba(0,0,0,0.08)' }}>
          {providers.map((prov) => {
            const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
            return (
              <div key={prov.id}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', padding: '8px 10px 4px', letterSpacing: '0.04em', textTransform: 'uppercase' }}>{prov.name}</div>
                {prov.models.map((m) => {
                  const isActive = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button key={m.id} onClick={() => { onSelect(prov.id, m.id); setIsOpen(false); }}
                      style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '8px 10px', borderRadius: 'var(--cr-radius-xs)', border: 'none', background: isActive ? `${accent}10` : 'transparent', cursor: 'pointer', textAlign: 'left', transition: 'background 100ms' }}
                      onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = 'var(--cr-surface)'; }}
                      onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = isActive ? `${accent}10` : 'transparent'; }}>
                      <TierIcon style={{ width: 13, height: 13, color: tier.color, flexShrink: 0 }} />
                      <span style={{ flex: 1, fontSize: 13, fontWeight: isActive ? 500 : 400, color: 'var(--cr-text)' }}>{m.name}</span>
                      <span style={{ fontSize: 11, color: 'var(--cr-text-muted)', flexShrink: 0 }}>{formatPrice(m.input_price, m.output_price)}</span>
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

export default function ModelSelector(props: ModelSelectorProps) {
  return props.mode === 'grid' ? <GridSelector {...props} /> : <CompactSelector {...props} />;
}

