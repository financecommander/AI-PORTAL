import { useState, useEffect, useRef, useCallback } from 'react';
import { Plus, ChevronDown, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import type { LLMProvider } from '../types';
import { useDirectChat } from '../hooks/useDirectChat';
import MessageBubble from '../components/chat/MessageBubble';
import ChatInput from '../components/chat/ChatInput';
import ModelSelector from '../components/chat/ModelSelector';

const SUGGESTION_PROMPTS = [
  'Explain CRE cap rate compression and its impact on deal underwriting',
  'What are the key financial covenants in a CMBS loan?',
  'Help me analyze a multifamily acquisition pro forma',
  'Compare fixed vs floating rate debt structures for a bridge loan',
];

export default function LLMChatPage() {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [loadingModels, setLoadingModels] = useState(true);

  const { messages, isStreaming, error, sendMessage, stopStreaming, clearChat } =
    useDirectChat(selectedProvider, selectedModel);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollPill, setShowScrollPill] = useState(false);

  useEffect(() => {
    api
      .request<{ providers: LLMProvider[] }>('/chat/direct/models')
      .then((data) => {
        setProviders(data.providers);
        if (data.providers.length > 0) {
          const first = data.providers[0];
          setSelectedProvider(first.id);
          const topModel = first.models.find((m) => m.tier === 'top');
          setSelectedModel(topModel?.id ?? first.models[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoadingModels(false));
  }, []);

  const isAtBottom = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < 100;
  }, []);

  useEffect(() => {
    if (isAtBottom()) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setShowScrollPill(false);
    } else if (messages.length > 0) {
      setShowScrollPill(true);
    }
  }, [messages, isAtBottom]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setShowScrollPill(false);
  };

  const handleScroll = () => {
    if (isAtBottom()) setShowScrollPill(false);
  };

  const handleModelSelect = (provider: string, model: string) => {
    setSelectedProvider(provider);
    setSelectedModel(model);
  };

  let selectedModelName = '';
  for (const prov of providers) {
    for (const m of prov.models) {
      if (prov.id === selectedProvider && m.id === selectedModel) {
        selectedModelName = m.name;
      }
    }
  }

  const hasMessages = messages.length > 0;

  if (loadingModels) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--cr-surface)' }}>
        <div style={{ color: 'var(--cr-text-muted)', fontSize: 14 }}>Loading models...</div>
      </div>
    );
  }

  if (!hasMessages) {
    return (
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 24, gap: 24, overflow: 'auto', background: 'var(--cr-surface)' }}>
        <div style={{ textAlign: 'center', marginBottom: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 8 }}>
            <Sparkles style={{ width: 24, height: 24, color: 'var(--cr-green-600)' }} />
            <span style={{ fontSize: 20, fontWeight: 700, color: 'var(--cr-text)', letterSpacing: '-0.02em', fontFamily: "'Space Grotesk', sans-serif" }}>
              Calculus Research
            </span>
          </div>
          <div style={{ fontSize: 13, color: 'var(--cr-text-muted)' }}>Intelligence Console</div>
        </div>

        <h1 style={{ fontSize: 24, fontWeight: 600, color: 'var(--cr-text)', textAlign: 'center', margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>
          What do you need to analyze?
        </h1>

        <div style={{ width: '100%', maxWidth: 700 }}>
          <ChatInput onSend={sendMessage} onStop={stopStreaming} isStreaming={isStreaming} disabled={!selectedModel} specialistName={selectedModelName || undefined} />
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
          <ModelSelector providers={providers} selectedProvider={selectedProvider} selectedModel={selectedModel} onSelect={handleModelSelect} mode="grid" />
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 700 }}>
          {SUGGESTION_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => sendMessage(prompt)}
              style={{
                background: 'var(--cr-white)',
                border: '1px solid var(--cr-border)',
                borderRadius: 20,
                color: 'var(--cr-text-secondary)',
                fontSize: 12,
                padding: '8px 16px',
                cursor: 'pointer',
                transition: 'all 150ms',
                maxWidth: 340,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; e.currentTarget.style.color = 'var(--cr-text)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; e.currentTarget.style.color = 'var(--cr-text-secondary)'; }}
            >
              {prompt}
            </button>
          ))}
        </div>

        {error && (
          <div style={{ padding: '8px 14px', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 8, color: 'var(--cr-danger)', fontSize: 13, maxWidth: 700, width: '100%' }}>
            {error}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col" style={{ height: '100vh', background: 'var(--cr-surface)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 20px', borderBottom: '1px solid var(--cr-border)', flexShrink: 0, background: 'var(--cr-white)' }}>
        <ModelSelector providers={providers} selectedProvider={selectedProvider} selectedModel={selectedModel} onSelect={handleModelSelect} mode="compact" />
        <div style={{ flex: 1 }} />
        <button
          onClick={() => clearChat()}
          style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px',
            borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)',
            background: 'var(--cr-white)', color: 'var(--cr-text-secondary)', fontSize: 13, cursor: 'pointer',
          }}
        >
          <Plus style={{ width: 14, height: 14 }} />
          New Chat
        </button>
      </div>

      <div ref={scrollContainerRef} onScroll={handleScroll} className="flex-1 overflow-y-auto" style={{ padding: 16 }}>
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} isStreaming={isStreaming && idx === messages.length - 1 && msg.role === 'assistant'} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {showScrollPill && (
        <div style={{ position: 'relative' }}>
          <button onClick={scrollToBottom} style={{ position: 'absolute', bottom: 8, left: '50%', transform: 'translateX(-50%)', background: 'var(--cr-green-900)', border: 'none', borderRadius: 20, color: '#fff', fontSize: 12, padding: '5px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, zIndex: 10 }}>
            <ChevronDown size={14} /> New messages
          </button>
        </div>
      )}

      {error && (
        <div style={{ margin: '0 16px 8px', padding: '8px 12px', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 8, color: 'var(--cr-danger)', fontSize: 13 }}>
          {error}
        </div>
      )}

      <ChatInput onSend={sendMessage} onStop={stopStreaming} isStreaming={isStreaming} disabled={!selectedModel} specialistName={selectedModelName || undefined} />
    </div>
  );
}

