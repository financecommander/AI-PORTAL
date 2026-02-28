import { useRef, useState, useEffect, useCallback } from 'react';
import { Send, Square, Paperclip, X, FileText } from 'lucide-react';
import type { Attachment } from '../../types';
import {
  ALLOWED_EXTENSIONS,
  MAX_FILES_PER_MESSAGE,
  validateFile,
  readFileAsBase64,
  getMimeType,
  isImageType,
  formatFileSize,
} from '../../utils/fileUpload';

// ── Pending file (in-memory before send) ──────────────────────

interface PendingFile {
  file: File;
  preview?: string;       // data: URI for image thumbnails
  attachment: Attachment;
}

// ── Props ─────────────────────────────────────────────────────

interface ChatInputProps {
  onSend: (message: string, attachments?: Attachment[]) => void;
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
  const [pendingFiles, setPendingFiles] = useState<PendingFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-grow textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    const lineHeight = 24;
    const maxHeight = lineHeight * 6 + 20; // 6 rows + padding
    el.style.height = Math.min(el.scrollHeight, maxHeight) + 'px';
  }, [value]);

  // Auto-clear file errors after 5 seconds
  useEffect(() => {
    if (!fileError) return;
    const timer = setTimeout(() => setFileError(null), 5000);
    return () => clearTimeout(timer);
  }, [fileError]);

  // ── File handling ─────────────────────────────────────────

  const handleFiles = useCallback(async (files: FileList | File[]) => {
    const incoming = Array.from(files);
    const errors: string[] = [];

    for (const file of incoming) {
      if (pendingFiles.length + incoming.indexOf(file) >= MAX_FILES_PER_MESSAGE) {
        errors.push(`Maximum ${MAX_FILES_PER_MESSAGE} files per message`);
        break;
      }

      const validationError = validateFile(file);
      if (validationError) {
        errors.push(`${validationError.filename}: ${validationError.error}`);
        continue;
      }

      try {
        const data_base64 = await readFileAsBase64(file);
        const contentType = getMimeType(file);
        const attachment: Attachment = {
          filename: file.name,
          content_type: contentType,
          data_base64,
          size_bytes: file.size,
        };
        const preview = isImageType(contentType)
          ? `data:${contentType};base64,${data_base64}`
          : undefined;

        setPendingFiles((prev) => {
          if (prev.length >= MAX_FILES_PER_MESSAGE) return prev;
          return [...prev, { file, preview, attachment }];
        });
      } catch {
        errors.push(`Failed to read ${file.name}`);
      }
    }

    if (errors.length > 0) {
      setFileError(errors.join('. '));
    }
  }, [pendingFiles.length]);

  const removeFile = (index: number) => {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // ── Send ──────────────────────────────────────────────────

  const handleSend = () => {
    const trimmed = value.trim();
    if ((!trimmed && pendingFiles.length === 0) || isStreaming || disabled) return;

    onSend(
      trimmed || ' ',  // Ensure non-empty content even with file-only messages
      pendingFiles.length > 0 ? pendingFiles.map((f) => f.attachment) : undefined,
    );
    setValue('');
    setPendingFiles([]);
    setFileError(null);
    setTimeout(() => textareaRef.current?.focus(), 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ── Drag and drop ─────────────────────────────────────────

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  // ── Derived state ─────────────────────────────────────────

  const placeholder = specialistName
    ? `Ask ${specialistName} a question...`
    : 'Type a message...';

  const canSend =
    (value.trim().length > 0 || pendingFiles.length > 0) &&
    !isStreaming &&
    !disabled;

  // ── Render ────────────────────────────────────────────────

  return (
    <div
      style={{
        padding: '12px 24px 16px',
        borderTop: '1px solid #2A3A5C',
        background: 'var(--navy-dark)',
        position: 'relative',
      }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {isDragOver && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'rgba(46, 117, 182, 0.15)',
            border: '2px dashed var(--blue)',
            borderRadius: 12,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 20,
            pointerEvents: 'none',
          }}
        >
          <span style={{ color: 'var(--blue)', fontSize: 15, fontWeight: 600 }}>
            Drop files here
          </span>
        </div>
      )}

      {/* File error message */}
      {fileError && (
        <div
          style={{
            marginBottom: 8,
            padding: '6px 12px',
            background: '#3A1A1A',
            border: '1px solid var(--red)',
            borderRadius: 8,
            color: '#FF8888',
            fontSize: 12,
          }}
        >
          {fileError}
        </div>
      )}

      {/* Preview strip */}
      {pendingFiles.length > 0 && (
        <div
          style={{
            display: 'flex',
            gap: 8,
            marginBottom: 8,
            flexWrap: 'wrap',
          }}
        >
          {pendingFiles.map((pf, i) => (
            <div
              key={`${pf.attachment.filename}-${i}`}
              style={{
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                background: 'var(--navy-light)',
                border: '1px solid #2A3A5C',
                borderRadius: 8,
                padding: 4,
                maxWidth: 180,
              }}
            >
              {/* Thumbnail or doc icon */}
              {pf.preview ? (
                <img
                  src={pf.preview}
                  alt={pf.attachment.filename}
                  style={{
                    width: 40,
                    height: 40,
                    objectFit: 'cover',
                    borderRadius: 6,
                    flexShrink: 0,
                  }}
                />
              ) : (
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: 6,
                    background: '#2A3A5C',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    color: '#8899AA',
                  }}
                >
                  <FileText size={18} />
                </div>
              )}

              {/* Filename + size */}
              <div style={{ minWidth: 0, flex: 1 }}>
                <div
                  style={{
                    fontSize: 11,
                    color: '#C0C8D0',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {pf.attachment.filename}
                </div>
                <div style={{ fontSize: 10, color: '#667788' }}>
                  {formatFileSize(pf.attachment.size_bytes)}
                </div>
              </div>

              {/* Remove button */}
              <button
                onClick={() => removeFile(i)}
                style={{
                  position: 'absolute',
                  top: -6,
                  right: -6,
                  width: 18,
                  height: 18,
                  borderRadius: '50%',
                  background: '#556677',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  padding: 0,
                }}
                title="Remove"
              >
                <X size={10} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 8,
          background: 'var(--navy-light)',
          border: `1px solid ${focused || isDragOver ? 'var(--blue)' : '#2A3A5C'}`,
          borderRadius: 12,
          padding: '8px 8px 8px 6px',
          opacity: disabled ? 0.5 : 1,
          transition: 'border-color 200ms',
        }}
      >
        {/* Paperclip (attach) button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || isStreaming}
          style={{
            flexShrink: 0,
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: 'transparent',
            border: 'none',
            cursor: disabled || isStreaming ? 'default' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: pendingFiles.length > 0 ? 'var(--blue)' : '#667788',
            transition: 'color 200ms',
          }}
          title="Attach file"
        >
          <Paperclip size={18} />
        </button>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={ALLOWED_EXTENSIONS}
          onChange={(e) => {
            if (e.target.files) handleFiles(e.target.files);
            e.target.value = ''; // Reset so same file can be re-selected
          }}
          style={{ display: 'none' }}
        />

        {/* Textarea */}
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

        {/* Send / Stop button */}
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
