import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ChatMessage } from '../../types';
import { FileText, Image as ImageIcon } from 'lucide-react';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

export default function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isEmpty = !message.content;
  const isThinking = isStreaming && isEmpty;

  // Estimated live token count during streaming (4 chars per token)
  const liveTokenEstimate = isStreaming && message.content.length > 0
    ? Math.ceil(message.content.length / 4)
    : null;

  // Memoize markdown components to prevent re-creation on every render
  const markdownComponents = useMemo(() => ({
    // Style code blocks
    pre: ({ children, ...props }: React.HTMLAttributes<HTMLPreElement>) => (
      <pre
        {...props}
        style={{
          background: 'var(--cr-surface)',
          border: '1px solid var(--cr-border)',
          borderRadius: 8,
          padding: '12px 16px',
          overflow: 'auto',
          fontSize: 13,
          lineHeight: 1.5,
          margin: '8px 0',
        }}
      >
        {children}
      </pre>
    ),
    code: ({ children, className, ...props }: React.HTMLAttributes<HTMLElement>) => {
      const isInline = !className;
      return isInline ? (
        <code
          {...props}
          style={{
            background: 'var(--cr-surface)',
            border: '1px solid var(--cr-border)',
            borderRadius: 4,
            padding: '1px 5px',
            fontSize: '0.88em',
          }}
        >
          {children}
        </code>
      ) : (
        <code {...props} className={className} style={{ fontFamily: "'Fira Code', 'Consolas', monospace" }}>
          {children}
        </code>
      );
    },
    // Style tables
    table: ({ children, ...props }: React.HTMLAttributes<HTMLTableElement>) => (
      <div style={{ overflow: 'auto', margin: '8px 0' }}>
        <table
          {...props}
          style={{
            borderCollapse: 'collapse',
            fontSize: 13,
            width: '100%',
          }}
        >
          {children}
        </table>
      </div>
    ),
    th: ({ children, ...props }: React.HTMLAttributes<HTMLTableCellElement>) => (
      <th
        {...props}
        style={{
          border: '1px solid var(--cr-border)',
          padding: '6px 10px',
          background: 'var(--cr-surface)',
          fontWeight: 600,
          textAlign: 'left',
        }}
      >
        {children}
      </th>
    ),
    td: ({ children, ...props }: React.HTMLAttributes<HTMLTableCellElement>) => (
      <td
        {...props}
        style={{
          border: '1px solid var(--cr-border)',
          padding: '6px 10px',
        }}
      >
        {children}
      </td>
    ),
    // Reasonable heading sizes
    h1: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
      <h1 {...props} style={{ fontSize: 18, fontWeight: 700, margin: '16px 0 8px', lineHeight: 1.3 }}>{children}</h1>
    ),
    h2: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
      <h2 {...props} style={{ fontSize: 16, fontWeight: 600, margin: '14px 0 6px', lineHeight: 1.3 }}>{children}</h2>
    ),
    h3: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
      <h3 {...props} style={{ fontSize: 14, fontWeight: 600, margin: '12px 0 4px', lineHeight: 1.4 }}>{children}</h3>
    ),
    // Lists
    ul: ({ children, ...props }: React.HTMLAttributes<HTMLUListElement>) => (
      <ul {...props} style={{ paddingLeft: 20, margin: '6px 0' }}>{children}</ul>
    ),
    ol: ({ children, ...props }: React.HTMLAttributes<HTMLOListElement>) => (
      <ol {...props} style={{ paddingLeft: 20, margin: '6px 0' }}>{children}</ol>
    ),
    li: ({ children, ...props }: React.HTMLAttributes<HTMLLIElement>) => (
      <li {...props} style={{ marginBottom: 2 }}>{children}</li>
    ),
    // Paragraphs
    p: ({ children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
      <p {...props} style={{ margin: '6px 0', lineHeight: 1.6 }}>{children}</p>
    ),
    // Blockquotes
    blockquote: ({ children, ...props }: React.HTMLAttributes<HTMLQuoteElement>) => (
      <blockquote
        {...props}
        style={{
          borderLeft: '3px solid var(--cr-green-600)',
          paddingLeft: 12,
          margin: '8px 0',
          color: 'var(--cr-text-secondary)',
        }}
      >
        {children}
      </blockquote>
    ),
    // Links
    a: ({ children, href, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
      <a
        {...props}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        style={{ color: 'var(--cr-green-600)', textDecoration: 'underline' }}
      >
        {children}
      </a>
    ),
  }), []);

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

        {/* Content */}
        {isUser ? (
          <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
        ) : isThinking ? (
          /* Thinking indicator — shown while waiting for first token */
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
            <div className="thinking-dots" style={{ display: 'flex', gap: 4 }}>
              <span className="thinking-dot" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--cr-green-600)', animation: 'thinking-pulse 1.4s ease-in-out infinite', animationDelay: '0s' }} />
              <span className="thinking-dot" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--cr-green-600)', animation: 'thinking-pulse 1.4s ease-in-out infinite', animationDelay: '0.2s' }} />
              <span className="thinking-dot" style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--cr-green-600)', animation: 'thinking-pulse 1.4s ease-in-out infinite', animationDelay: '0.4s' }} />
            </div>
            <span style={{ fontSize: 12, color: 'var(--cr-text-muted)' }}>Thinking...</span>
          </div>
        ) : (
          /* Assistant message — rendered as Markdown */
          <div className="markdown-content" style={{ color: 'inherit' }}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={markdownComponents}
            >
              {message.content}
            </ReactMarkdown>
            {isStreaming && (
              <span className="animate-blink" style={{ color: 'var(--cr-green-600)', fontSize: 16, marginLeft: 2 }}>▌</span>
            )}
          </div>
        )}

        {/* Live token counter during streaming */}
        {liveTokenEstimate != null && (
          <div
            style={{
              marginTop: 6,
              fontSize: 11,
              color: isUser ? 'rgba(255,255,255,0.5)' : 'var(--cr-text-dim)',
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            ~{liveTokenEstimate.toLocaleString()} tokens
          </div>
        )}

        {/* Final token info (after streaming complete) */}
        {message.tokens && !isStreaming && (
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
