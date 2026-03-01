import { useState, useRef, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { ChatMessage, Attachment } from '../types';

interface UseDirectChatReturn {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  conversationUuid: string | null;
  sendMessage: (content: string, attachments?: Attachment[]) => Promise<void>;
  stopStreaming: () => void;
  clearChat: () => void;
  loadConversation: (uuid: string) => Promise<{ provider: string; model: string } | null>;
}

let _msgIdCounter = 0;
function nextMsgId(): string {
  return `dm-${++_msgIdCounter}-${Date.now()}`;
}

export function useDirectChat(
  provider: string | null,
  model: string | null,
): UseDirectChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationUuid, setConversationUuid] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const stoppedRef = useRef(false);
  const conversationUuidRef = useRef<string | null>(null);
  const creatingConvRef = useRef<Promise<string | null> | null>(null);

  // Keep ref in sync with state (for use in callbacks without stale closures)
  useEffect(() => {
    conversationUuidRef.current = conversationUuid;
  }, [conversationUuid]);

  // Track previous provider/model to detect actual changes
  const prevProviderRef = useRef(provider);
  const prevModelRef = useRef(model);

  useEffect(() => {
    const providerChanged = prevProviderRef.current !== provider;
    const modelChanged = prevModelRef.current !== model;
    prevProviderRef.current = provider;
    prevModelRef.current = model;

    // Only clear if there are messages and the selection actually changed
    if ((providerChanged || modelChanged) && messages.length > 0) {
      setMessages([]);
      setIsStreaming(false);
      setError(null);
      setConversationUuid(null);
      conversationUuidRef.current = null;
      stoppedRef.current = false;
      if (abortRef.current) {
        abortRef.current.abort();
        abortRef.current = null;
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [provider, model]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    setConversationUuid(null);
    conversationUuidRef.current = null;
    creatingConvRef.current = null;
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
  }, []);

  const stopStreaming = useCallback(() => {
    stoppedRef.current = true;
    setIsStreaming(false);
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
  }, []);

  const loadConversation = useCallback(async (uuid: string): Promise<{ provider: string; model: string } | null> => {
    try {
      const data = await api.loadConversation(uuid);
      const loaded: ChatMessage[] = data.messages.map((m) => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
        _id: nextMsgId(),
        tokens: m.input_tokens || m.output_tokens ? { input: m.input_tokens, output: m.output_tokens } : undefined,
        cost_usd: m.cost_usd || undefined,
      }));
      setMessages(loaded);
      setConversationUuid(uuid);
      conversationUuidRef.current = uuid;
      setError(null);
      return { provider: data.provider, model: data.model };
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversation');
      return null;
    }
  }, []);

  const sendMessage = useCallback(async (content: string, attachments?: Attachment[]) => {
    if (!provider || !model) return;

    setError(null);
    stoppedRef.current = false;

    // Create conversation on first message if none exists (with race-condition guard)
    let uuid = conversationUuidRef.current;
    if (!uuid) {
      // If another sendMessage call is already creating the conversation, wait for it
      if (creatingConvRef.current) {
        uuid = await creatingConvRef.current;
      } else {
        const promise = api.createConversation(provider, model, 'direct')
          .then((conv) => {
            setConversationUuid(conv.uuid);
            conversationUuidRef.current = conv.uuid;
            return conv.uuid;
          })
          .catch((err) => {
            console.error('Failed to create conversation:', err);
            return null;  // Continue without persistence
          })
          .finally(() => { creatingConvRef.current = null; });
        creatingConvRef.current = promise;
        uuid = await promise;
      }
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content,
      _id: nextMsgId(),
      attachments: attachments && attachments.length > 0 ? attachments : undefined,
    };

    // Build history BEFORE appending new message
    const history = messages.map((m) => ({ role: m.role, content: m.content }));

    const assistantId = nextMsgId();

    // Append user message + empty assistant placeholder
    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: 'assistant', content: '', _id: assistantId },
    ]);

    // Save user message (fire-and-forget)
    if (uuid) {
      api.saveMessage(uuid, { role: 'user', content, model }).catch(() => {});
    }

    setIsStreaming(true);

    // Create abort controller for this request
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      await api.streamDirectChat(
        provider,
        model,
        content,
        history,
        (chunk) => {
          if (stoppedRef.current) return;

          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx < 0 || updated[lastIdx].role !== 'assistant') return prev;

            if (chunk.is_final) {
              updated[lastIdx] = {
                ...updated[lastIdx],
                content: updated[lastIdx].content + chunk.content,
                tokens: {
                  input: chunk.input_tokens,
                  output: chunk.output_tokens,
                },
                cost_usd: chunk.cost_usd,
              };

              // Save assistant message on completion
              const finalContent = updated[lastIdx].content;
              const currentUuid = conversationUuidRef.current;
              if (currentUuid) {
                api.saveMessage(currentUuid, {
                  role: 'assistant',
                  content: finalContent,
                  model: model || '',
                  input_tokens: chunk.input_tokens,
                  output_tokens: chunk.output_tokens,
                  cost_usd: chunk.cost_usd,
                }).catch(() => {});
              }
            } else {
              updated[lastIdx] = {
                ...updated[lastIdx],
                content: updated[lastIdx].content + chunk.content,
              };
            }
            return updated;
          });
        },
        undefined,
        undefined,
        controller.signal,
      );
    } catch (err) {
      if (!stoppedRef.current && !(err instanceof DOMException && err.name === 'AbortError')) {
        setError(err instanceof Error ? err.message : 'Stream failed');
      }
    } finally {
      abortRef.current = null;
      if (!stoppedRef.current) {
        setIsStreaming(false);
      }
    }
  }, [provider, model, messages]);

  return { messages, isStreaming, error, conversationUuid, sendMessage, stopStreaming, clearChat, loadConversation };
}
