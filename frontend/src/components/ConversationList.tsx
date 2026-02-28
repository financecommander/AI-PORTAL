import { useState, useEffect } from 'react';
import { Plus, Trash2, MessageSquare } from 'lucide-react';
import { api } from '../api/client';

interface ConversationItem {
  uuid: string;
  title: string;
  provider: string;
  model: string;
  mode: string;
  message_count: number;
  updated_at: string;
  preview: string;
}

interface ConversationListProps {
  activeId: string | null;
  onSelect: (uuid: string) => void;
  onNew: () => void;
}

export default function ConversationList({ activeId, onSelect, onNew }: ConversationListProps) {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadConversations = async () => {
    try {
      const data = await api.request<{ conversations: ConversationItem[] }>('/conversations/');
      setConversations(data.conversations);
    } catch {
      // silently fail — user might not be authed yet
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  // Refresh when activeId changes (new messages may have updated title)
  useEffect(() => {
    if (activeId) loadConversations();
  }, [activeId]);

  const handleDelete = async (e: React.MouseEvent, uuid: string) => {
    e.stopPropagation();
    try {
      await api.delete(`/conversations/${uuid}`);
      setConversations((prev) => prev.filter((c) => c.uuid !== uuid));
      if (activeId === uuid) onNew();
    } catch {
      // ignore
    }
  };

  const formatTime = (iso: string) => {
    const d = new Date(iso);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffHours = diffMs / (1000 * 60 * 60);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${Math.floor(diffHours)}h ago`;
    if (diffHours < 48) return 'Yesterday';
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div style={{ padding: '12px', color: 'var(--cr-text-dim)', fontSize: '12px' }}>
        Loading...
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* New chat button */}
      <button
        onClick={onNew}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          margin: '8px 10px',
          padding: '8px 12px',
          borderRadius: 'var(--cr-radius-sm)',
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
        New chat
      </button>

      {/* Conversation list */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '0 6px',
        }}
      >
        {conversations.length === 0 && (
          <div
            style={{
              padding: '20px 12px',
              textAlign: 'center',
              color: 'var(--cr-text-dim)',
              fontSize: '12px',
            }}
          >
            <MessageSquare
              style={{ width: 20, height: 20, margin: '0 auto 8px', opacity: 0.4 }}
            />
            No conversations yet
          </div>
        )}

        {conversations.map((conv) => {
          const isActive = conv.uuid === activeId;
          return (
            <button
              key={conv.uuid}
              onClick={() => onSelect(conv.uuid)}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
                width: '100%',
                padding: '10px 10px',
                margin: '1px 0',
                borderRadius: 'var(--cr-radius-xs)',
                border: 'none',
                background: isActive ? 'var(--cr-charcoal-deep)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'background 100ms',
                position: 'relative',
              }}
              onMouseEnter={(e) => {
                if (!isActive)
                  (e.currentTarget as HTMLButtonElement).style.background =
                    'rgba(42, 46, 50, 0.5)';
              }}
              onMouseLeave={(e) => {
                if (!isActive)
                  (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
              }}
            >
              <div style={{ flex: 1, overflow: 'hidden', minWidth: 0 }}>
                <div
                  style={{
                    fontSize: '13px',
                    fontWeight: isActive ? 500 : 400,
                    color: isActive ? 'var(--cr-text)' : 'var(--cr-text-muted)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {conv.title}
                </div>
                <div
                  style={{
                    fontSize: '11px',
                    color: 'var(--cr-text-dim)',
                    marginTop: '2px',
                  }}
                >
                  {formatTime(conv.updated_at)}
                  {conv.model && (
                    <span style={{ marginLeft: '6px', opacity: 0.7 }}>
                      {conv.model.split('/').pop()?.split('-').slice(0, 2).join('-')}
                    </span>
                  )}
                </div>
              </div>
              {/* Delete button — shows on hover via CSS would be ideal, but inline works */}
              <button
                onClick={(e) => handleDelete(e, conv.uuid)}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: '2px',
                  cursor: 'pointer',
                  color: 'var(--cr-text-dim)',
                  opacity: 0.4,
                  transition: 'opacity 150ms, color 150ms',
                  flexShrink: 0,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                  e.currentTarget.style.color = 'var(--cr-danger)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.4';
                  e.currentTarget.style.color = 'var(--cr-text-dim)';
                }}
                title="Delete conversation"
              >
                <Trash2 style={{ width: 13, height: 13 }} />
              </button>
            </button>
          );
        })}
      </div>
    </div>
  );
}

