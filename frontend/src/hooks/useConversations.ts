import { useState, useCallback, useEffect } from 'react';
import { api } from '../api/client';

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Conversation {
  conversation_id: string;
  title: string;
  specialist_id: string | null;
  provider: string | null;
  model: string | null;
  created_at: string;
  updated_at: string;
  messages: ConversationMessage[];
}

interface UseConversationsReturn {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  isLoading: boolean;
  error: string | null;
  createConversation: (opts?: {
    title?: string;
    provider?: string;
    model?: string;
    specialist_id?: string;
  }) => Promise<Conversation>;
  loadConversation: (conversationId: string) => Promise<void>;
  saveMessages: (
    conversationId: string,
    messages: Array<{ role: 'user' | 'assistant'; content: string }>,
  ) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  clearActive: () => void;
}

export function useConversations(): UseConversationsReturn {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load conversation list on mount
  useEffect(() => {
    api
      .request<Conversation[]>('/conversations/')
      .then(setConversations)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load conversations'));
  }, []);

  const createConversation = useCallback(
    async (opts: { title?: string; provider?: string; model?: string; specialist_id?: string } = {}) => {
      const conv = await api.post<Conversation>('/conversations/', {
        title: opts.title ?? 'New Conversation',
        provider: opts.provider ?? null,
        model: opts.model ?? null,
        specialist_id: opts.specialist_id ?? null,
      });
      setConversations((prev) => [conv, ...prev]);
      setActiveConversation(conv);
      return conv;
    },
    [],
  );

  const loadConversation = useCallback(async (conversationId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const conv = await api.request<Conversation>(`/conversations/${conversationId}`);
      setActiveConversation(conv);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const saveMessages = useCallback(
    async (
      conversationId: string,
      messages: Array<{ role: 'user' | 'assistant'; content: string }>,
    ) => {
      try {
        const updated = await api.post<Conversation>(`/conversations/${conversationId}/messages`, {
          messages,
        });
        // Update active and list
        setActiveConversation(updated);
        setConversations((prev) =>
          prev.map((c) => (c.conversation_id === conversationId ? { ...c, title: updated.title, updated_at: updated.updated_at } : c)),
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to save messages');
      }
    },
    [],
  );

  const deleteConversation = useCallback(async (conversationId: string) => {
    await api.delete<void>(`/conversations/${conversationId}`);
    setConversations((prev) => prev.filter((c) => c.conversation_id !== conversationId));
    setActiveConversation((prev) => (prev?.conversation_id === conversationId ? null : prev));
  }, []);

  const clearActive = useCallback(() => {
    setActiveConversation(null);
  }, []);

  return {
    conversations,
    activeConversation,
    isLoading,
    error,
    createConversation,
    loadConversation,
    saveMessages,
    deleteConversation,
    clearActive,
  };
}
