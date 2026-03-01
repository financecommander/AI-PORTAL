
import type { ChatMessage } from '../../types';
import { FileText, Image as ImageIcon } from 'lucide-react';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

export default function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className="animate-fade-in-up"
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: 12,
        maxWidth: '100%',
      }}
    >
      <div
        style={{
          maxWidth: '72%',
          minWidth: 60,
          padding: '12px 16px',
          borderRadius: isUser ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
          background: isUser ? 'var(--cr-green-900)' : 'var(--cr-white)',
          border: isUser ? 'none' : '1px solid var(--cr-border)',
          color: isUser ? '#FFFFFF' : 'var(--cr-text)',
          fontSize: 14,
          lineHeight: 1.6,
          wordBreak: 'break-word',
          position: 'relative',
        }}
      >
        {/* Attachments */}
        {message.attachments && message.attachments.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
            {message.attachments.map((att, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '4px 8px',
                  borderRadius: 6,
                  background: isUser ? 'rgba(255,255,255,0.15)' : 'var(--cr-surface)',
                  fontSize: 11,
                }}
              >
                {att.content_type.startsWith('image/') ? <ImageIcon size={12} /> : <FileText size={12} />}
                <span style={{ maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {att.filename}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Content — no dangerouslySetInnerHTML to prevent XSS */}
        {isUser ? (
          <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
        ) : (
          <div className="prose prose-sm max-w-none" style={{ color: 'inherit', whiteSpace: 'pre-wrap' }}>
            {message.content}
            {isStreaming && (
              <span className="animate-blink" style={{ color: 'var(--cr-green-600)', fontSize: 16, marginLeft: 2 }}>▌</span>
            )}
          </div>
        )}

        {/* Token info */}
        {message.tokens && (
          <div
            style={{
              marginTop: 8,
              paddingTop: 6,
              borderTop: isUser ? '1px solid rgba(255,255,255,0.15)' : '1px solid var(--cr-border)',
              display: 'flex',
              gap: 12,
              fontSize: 11,
              color: isUser ? 'rgba(255,255,255,0.6)' : 'var(--cr-text-muted)',
            }}
          >
            <span>{message.tokens.input}→{message.tokens.output} tok</span>
            {message.cost_usd != null && <span>${message.cost_usd.toFixed(4)}</span>}
          </div>
        )}
      </div>
    </div>
  );
}

