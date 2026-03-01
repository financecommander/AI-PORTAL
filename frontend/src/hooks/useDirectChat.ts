import { useState, useRef, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { ChatMessage, Attachment } from '../types';

interface UseDirectChatReturn {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  sendMessage: (content: string, attachments?: Attachment[]) => Promise<void>;
  stopStreaming: () => void;
  clearChat: () => void;
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

  const abortRef = useRef<AbortController | null>(null);
  const stoppedRef = useRef(false);

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
      stoppedRef.current = false;
      // Abort any in-flight stream
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

  const sendMessage = useCallback(async (content: string, attachments?: Attachment[]) => {
    if (!provider || !model) return;

    setError(null);
    stoppedRef.current = false;

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

  return { messages, isStreaming, error, sendMessage, stopStreaming, clearChat };
}
