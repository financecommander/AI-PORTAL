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

  // Fetch model catalog on mount
  useEffect(() => {
    api
      .request<{ providers: LLMProvider[] }>('/chat/direct/models')
      .then((data) => {
        setProviders(data.providers);
        // Default to first provider's top model
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

  // Scroll logic (same pattern as ChatPage)
  const isAtBottom = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < 100;
  }, []);

  useEffect(() => {
    const atBottom = isAtBottom();
    if (atBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
    queueMicrotask(() => setShowScrollPill(!atBottom && messages.length > 0));
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

  const handleNewChat = () => {
    clearChat();
  };

  // Find selected model display name
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
      <div
        style={{
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div style={{ color: 'var(--cr-text-dim)', fontSize: 14 }}>Loading models...</div>
      </div>
    );
  }

  // ── Empty State: Perplexity-style welcome ─────────────────────
  if (!hasMessages) {
    return (
      <div
        style={{
          height: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
          gap: '24px',
          overflow: 'auto',
        }}
      >
        {/* Branding */}
        <div style={{ textAlign: 'center', marginBottom: '8px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px',
              marginBottom: '8px',
            }}
          >
            <Sparkles style={{ width: 28, height: 28, color: 'var(--cr-green-400)' }} />
            <span
              style={{
                fontSize: '22px',
                fontWeight: 700,
                color: 'var(--cr-green-400)',
                letterSpacing: '-0.02em',
              }}
            >
              CALCULUS LABS
            </span>
          </div>
          <div style={{ fontSize: '13px', color: 'var(--cr-text-dim)' }}>Direct LLM Access</div>
        </div>

        {/* Heading */}
        <h1
          style={{
            fontSize: '26px',
            fontWeight: 600,
            color: 'var(--cr-text)',
            textAlign: 'center',
            margin: 0,
          }}
        >
          What do you want to know?
        </h1>

        {/* Input */}
        <div style={{ width: '100%', maxWidth: '700px' }}>
          <ChatInput
            onSend={sendMessage}
            onStop={stopStreaming}
            isStreaming={isStreaming}
            disabled={!selectedModel}
            specialistName={selectedModelName || undefined}
          />
        </div>

        {/* Model selector grid */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            width: '100%',
          }}
        >
          <ModelSelector
            providers={providers}
            selectedProvider={selectedProvider}
            selectedModel={selectedModel}
            onSelect={handleModelSelect}
            mode="grid"
          />
        </div>

        {/* Suggestion pills */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px',
            justifyContent: 'center',
            maxWidth: '700px',
          }}
        >
          {SUGGESTION_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => sendMessage(prompt)}
              style={{
                background: 'var(--cr-charcoal)',
                border: '1px solid var(--cr-border)',
                borderRadius: '20px',
                color: 'var(--cr-text-muted)',
                fontSize: '12px',
                padding: '6px 14px',
                cursor: 'pointer',
                transition: 'background 200ms, color 200ms',
                maxWidth: '340px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = 'var(--cr-charcoal-deep)';
                (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-mist)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = 'var(--cr-charcoal-deep)';
                (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-muted)';
              }}
            >
              {prompt}
            </button>
          ))}
        </div>

        {error && (
          <div
            style={{
              padding: '8px 14px',
              background: 'rgba(214, 69, 69, 0.08)',
              border: '1px solid var(--cr-danger)',
              borderRadius: 8,
              color: 'var(--cr-danger)',
              fontSize: 13,
              maxWidth: '700px',
              width: '100%',
            }}
          >
            {error}
          </div>
        )}
      </div>
    );
  }

  // ── Active Conversation ───────────────────────────────────────
  return (
    <div className="flex flex-col" style={{ height: '100vh' }}>
      {/* Header bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '10px 20px',
          borderBottom: '1px solid var(--cr-border)',
          flexShrink: 0,
          background: 'var(--cr-charcoal-deep)',
        }}
      >
        <ModelSelector
          providers={providers}
          selectedProvider={selectedProvider}
          selectedModel={selectedModel}
          onSelect={handleModelSelect}
          mode="compact"
        />
        <div style={{ flex: 1 }} />
        <button
          onClick={handleNewChat}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 14px',
            borderRadius: '8px',
            border: '1px solid var(--cr-border)',
            background: 'transparent',
            color: 'var(--cr-text-muted)',
            fontSize: '13px',
            cursor: 'pointer',
            transition: 'all 150ms',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'var(--cr-charcoal-deep)';
            (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
            (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-muted)';
          }}
        >
          <Plus style={{ width: 14, height: 14 }} />
          New Chat
        </button>
      </div>

      {/* Messages */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
        style={{ padding: '16px 16px' }}
      >
        {messages.map((msg, idx) => (
          <MessageBubble
            key={idx}
            message={msg}
            isStreaming={
              isStreaming && idx === messages.length - 1 && msg.role === 'assistant'
            }
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Scroll pill */}
      {showScrollPill && (
        <div style={{ position: 'relative' }}>
          <button
            onClick={scrollToBottom}
            style={{
              position: 'absolute',
              bottom: 8,
              left: '50%',
              transform: 'translateX(-50%)',
              background: 'var(--cr-green-900)',
              border: 'none',
              borderRadius: 20,
              color: 'var(--cr-text)',
              fontSize: 12,
              padding: '5px 14px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              zIndex: 10,
            }}
          >
            <ChevronDown size={14} />
            New messages
          </button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            margin: '0 16px 8px',
            padding: '8px 12px',
            background: 'rgba(214, 69, 69, 0.08)',
            border: '1px solid var(--cr-danger)',
            borderRadius: 8,
            color: 'var(--cr-danger)',
            fontSize: 13,
          }}
        >
          {error}
        </div>
      )}

      {/* Input */}
      <ChatInput
        onSend={sendMessage}
        onStop={stopStreaming}
        isStreaming={isStreaming}
        disabled={!selectedModel}
        specialistName={selectedModelName || undefined}
      />
    </div>
  );
}
