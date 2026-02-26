import { useRef, useState, useEffect } from 'react';
import { Send, Square } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled: boolean;
  specialistName?: string;
}

export default function ChatInput({
  onSend,
  onStop,
  isStreaming,
  disabled,
  specialistName,
}: ChatInputProps) {
  const [value, setValue] = useState('');
  const [focused, setFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-grow textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    const lineHeight = 24;
    const maxHeight = lineHeight * 6 + 20; // 6 rows + padding
    el.style.height = Math.min(el.scrollHeight, maxHeight) + 'px';
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isStreaming || disabled) return;
    onSend(trimmed);
    setValue('');
    setTimeout(() => textareaRef.current?.focus(), 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const placeholder = specialistName
    ? `Ask ${specialistName} a question...`
    : 'Type a message...';

  const canSend = value.trim().length > 0 && !isStreaming && !disabled;

  return (
    <div
      style={{
        padding: '12px 24px 16px',
        borderTop: '1px solid #2A3A5C',
        background: 'var(--navy-dark)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 8,
          background: 'var(--navy-light)',
          border: `1px solid ${focused ? 'var(--blue)' : '#2A3A5C'}`,
          borderRadius: 12,
          padding: '8px 8px 8px 14px',
          opacity: disabled ? 0.5 : 1,
          transition: 'border-color 200ms',
        }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          disabled={disabled}
          placeholder={placeholder}
          rows={1}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            resize: 'none',
            color: '#E0E0E0',
            fontSize: 14,
            lineHeight: '24px',
            minHeight: 24,
            maxHeight: 24 * 6 + 20,
            fontFamily: 'inherit',
          }}
        />

        {isStreaming ? (
          <button
            onClick={onStop}
            style={{
              flexShrink: 0,
              width: 36,
              height: 36,
              borderRadius: '50%',
              background: 'var(--red)',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
            }}
            title="Stop"
          >
            <Square size={16} />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!canSend}
            style={{
              flexShrink: 0,
              width: 36,
              height: 36,
              borderRadius: '50%',
              background: canSend ? 'var(--blue)' : '#2A3A5C',
              border: 'none',
              cursor: canSend ? 'pointer' : 'default',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: canSend ? '#fff' : '#556677',
              transition: 'background 200ms',
            }}
            title="Send"
          >
            <Send size={16} />
          </button>
        )}
      </div>
    </div>
  );
}

