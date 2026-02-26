import { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';
import type { ChatMessage } from '../types';

interface UseChatReturn {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  stopStreaming: () => void;
  clearChat: () => void;
}

export function useChat(specialistId: string | null): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stoppedRef = useRef(false);

  // Clear chat when specialist changes
  useEffect(() => {
    setMessages([]);
    setIsStreaming(false);
    setError(null);
    stoppedRef.current = false;
  }, [specialistId]);

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  const stopStreaming = () => {
    stoppedRef.current = true;
    setIsStreaming(false);
  };

  const sendMessage = async (content: string) => {
    if (!specialistId) return;

    setError(null);
    stoppedRef.current = false;

    const userMessage: ChatMessage = { role: 'user', content };

    // Build history BEFORE appending new message
    const history = messages.map((m) => ({ role: m.role, content: m.content }));

    // Append user message + empty assistant placeholder
    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: 'assistant', content: '' },
    ]);

    setIsStreaming(true);

    try {
      await api.streamChat(
        specialistId,
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
      );
    } catch (err) {
      if (!stoppedRef.current) {
        setError(err instanceof Error ? err.message : 'Stream failed');
      }
    } finally {
      if (!stoppedRef.current) {
        setIsStreaming(false);
      }
    }
  };

  return { messages, isStreaming, error, sendMessage, stopStreaming, clearChat };
}
