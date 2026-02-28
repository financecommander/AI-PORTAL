import { useState } from 'react';
import { FileText } from 'lucide-react';
import type { ChatMessage } from '../../types';
import { isImageType, formatFileSize } from '../../utils/fileUpload';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

type Segment = { type: 'text'; html: string } | { type: 'code'; content: string };

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function parseSegments(text: string): Segment[] {
  const segments: Segment[] = [];
  const parts = text.split(/(```[\w]*\n?[\s\S]*?```)/g);
  for (const part of parts) {
    const codeMatch = part.match(/^```[\w]*\n?([\s\S]*?)```$/);
    if (codeMatch) {
      segments.push({ type: 'code', content: codeMatch[1] });
    } else {
      segments.push({ type: 'text', html: renderInlineMarkdown(part) });
    }
  }
  return segments;
}

function renderInlineMarkdown(text: string): string {
  let html = escapeHtml(text);

  // Inline code (already HTML-escaped, so no XSS risk)
  html = html.replace(
    /`([^`]+)`/g,
    '<code style="background:#0D1520;padding:2px 6px;border-radius:4px;font-family:monospace">$1</code>',
  );

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Bullet lists
  html = html.replace(
    /^[ \t]*[-*] (.+)$/gm,
    '<li style="margin-left:16px;list-style:disc">$1</li>',
  );
  html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/g, '<ul style="margin:4px 0;padding:0">$&</ul>');

  // Numbered lists
  html = html.replace(
    /^[ \t]*\d+\. (.+)$/gm,
    '<li style="margin-left:16px;list-style:decimal">$1</li>',
  );

  // Newlines → <br>
  html = html.replace(/\n/g, '<br>');

  return html;
}

function CodeBlock({ content }: { content: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  return (
    <div style={{ position: 'relative', margin: '8px 0' }}>
      <pre
        style={{
          background: '#0D1520',
          fontFamily: 'monospace',
          fontSize: 14,
          padding: 12,
          borderRadius: 8,
          overflowX: 'auto',
          margin: 0,
          whiteSpace: 'pre',
        }}
      >
        {content}
      </pre>
      <button
        onClick={handleCopy}
        style={{
          position: 'absolute',
          top: 6,
          right: 8,
          background: '#2A3A5C',
          border: 'none',
          color: '#8899AA',
          fontSize: 11,
          padding: '2px 8px',
          borderRadius: 4,
          cursor: 'pointer',
        }}
      >
        {copied ? 'Copied!' : 'Copy'}
      </button>
    </div>
  );
}

export default function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  const hasStats =
    !isStreaming &&
    message.tokens !== undefined &&
    message.cost_usd !== undefined;

  const segments = isUser ? null : parseSegments(message.content);

  return (
    <div
      className="animate-fade-in-up flex flex-col mb-4"
      style={{ alignItems: isUser ? 'flex-end' : 'flex-start' }}
    >
      <div
        style={{
          maxWidth: '80%',
          background: isUser ? 'var(--blue)' : 'var(--navy-light)',
          color: isUser ? '#FFFFFF' : '#E0E0E0',
          borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
          padding: '10px 14px',
          wordBreak: 'break-word',
        }}
      >
        {isUser ? (
          <>
            {/* Render file attachments above message text */}
            {message.attachments && message.attachments.length > 0 && (
              <div
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: 6,
                  marginBottom: message.content.trim() ? 8 : 0,
                }}
              >
                {message.attachments.map((att, i) =>
                  isImageType(att.content_type) ? (
                    <img
                      key={i}
                      src={`data:${att.content_type};base64,${att.data_base64}`}
                      alt={att.filename}
                      style={{
                        maxWidth: 200,
                        maxHeight: 200,
                        borderRadius: 8,
                        cursor: 'pointer',
                        display: 'block',
                      }}
                      onClick={() => {
                        // Open full-size image in new tab
                        const win = window.open();
                        if (win) {
                          win.document.write(
                            `<img src="data:${att.content_type};base64,${att.data_base64}" style="max-width:100%;height:auto" />`
                          );
                          win.document.title = att.filename;
                        }
                      }}
                      title={`${att.filename} — click to view full size`}
                    />
                  ) : (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                        background: 'rgba(255,255,255,0.15)',
                        borderRadius: 8,
                        padding: '4px 8px',
                        fontSize: 12,
                      }}
                    >
                      <FileText size={14} />
                      <span>{att.filename}</span>
                      <span style={{ opacity: 0.7 }}>
                        ({formatFileSize(att.size_bytes)})
                      </span>
                    </div>
                  ),
                )}
              </div>
            )}
            {message.content.trim() && (
              <span style={{ whiteSpace: 'pre-wrap' }}>{message.content}</span>
            )}
          </>
        ) : (
          <>
            {segments!.map((seg, i) =>
              seg.type === 'code' ? (
                <CodeBlock key={i} content={seg.content} />
              ) : (
                <span key={i} dangerouslySetInnerHTML={{ __html: seg.html }} />
              ),
            )}
            {isStreaming && (
              <span className="animate-blink" style={{ marginLeft: 1 }}>
                ▌
              </span>
            )}
          </>
        )}
      </div>

      {!isUser && hasStats && (
        <div style={{ fontSize: 11, color: '#556677', marginTop: 4 }}>
          {(message.tokens!.input + message.tokens!.output).toLocaleString()} tokens
          &nbsp;·&nbsp;${message.cost_usd!.toFixed(4)}
        </div>
      )}
    </div>
  );
}
