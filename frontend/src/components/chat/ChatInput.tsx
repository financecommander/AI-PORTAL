import { useRef, useState, useEffect, useCallback } from 'react';
import { Send, Square, Paperclip, X, FileText } from 'lucide-react';
import type { Attachment } from '../../types';
import { ALLOWED_EXTENSIONS, MAX_FILES_PER_MESSAGE, validateFile, readFileAsBase64, getMimeType, isImageType, formatFileSize } from '../../utils/fileUpload';

interface PendingFile { file: File; preview?: string; attachment: Attachment; }

interface ChatInputProps {
  onSend: (message: string, attachments?: Attachment[]) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled: boolean;
  specialistName?: string;
}

export default function ChatInput({ onSend, onStop, isStreaming, disabled, specialistName }: ChatInputProps) {
  const [value, setValue] = useState('');
  const [focused, setFocused] = useState(false);
  const [pendingFiles, setPendingFiles] = useState<PendingFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 24 * 6 + 20) + 'px';
  }, [value]);

  useEffect(() => {
    if (!fileError) return;
    const timer = setTimeout(() => setFileError(null), 5000);
    return () => clearTimeout(timer);
  }, [fileError]);

  const handleFiles = useCallback(async (files: FileList | File[]) => {
    const incoming = Array.from(files);
    const errors: string[] = [];
    for (const file of incoming) {
      if (pendingFiles.length + incoming.indexOf(file) >= MAX_FILES_PER_MESSAGE) { errors.push(`Maximum ${MAX_FILES_PER_MESSAGE} files per message`); break; }
      const validationError = validateFile(file);
      if (validationError) { errors.push(`${validationError.filename}: ${validationError.error}`); continue; }
      try {
        const data_base64 = await readFileAsBase64(file);
        const contentType = getMimeType(file);
        const attachment: Attachment = { filename: file.name, content_type: contentType, data_base64, size_bytes: file.size };
        const preview = isImageType(contentType) ? `data:${contentType};base64,${data_base64}` : undefined;
        setPendingFiles((prev) => prev.length >= MAX_FILES_PER_MESSAGE ? prev : [...prev, { file, preview, attachment }]);
      } catch { errors.push(`Failed to read ${file.name}`); }
    }
    if (errors.length > 0) setFileError(errors.join('. '));
  }, [pendingFiles.length]);

  const handleSend = () => {
    const trimmed = value.trim();
    if ((!trimmed && pendingFiles.length === 0) || isStreaming || disabled) return;
    onSend(trimmed || ' ', pendingFiles.length > 0 ? pendingFiles.map((f) => f.attachment) : undefined);
    setValue(''); setPendingFiles([]); setFileError(null);
    setTimeout(() => textareaRef.current?.focus(), 0);
  };

  const placeholder = specialistName ? `Ask ${specialistName} a question...` : 'Type a message...';
  const canSend = (value.trim().length > 0 || pendingFiles.length > 0) && !isStreaming && !disabled;

  return (
    <div style={{ padding: '12px 24px 16px', borderTop: '1px solid var(--cr-border)', background: 'var(--cr-white)' }}
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={(e) => { e.preventDefault(); setIsDragOver(false); }}
      onDrop={(e) => { e.preventDefault(); setIsDragOver(false); if (e.dataTransfer.files.length > 0) handleFiles(e.dataTransfer.files); }}>

      {isDragOver && (
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(62, 155, 95, 0.08)', border: '2px dashed var(--cr-green-600)', borderRadius: 'var(--cr-radius)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 20, pointerEvents: 'none' }}>
          <span style={{ color: 'var(--cr-green-600)', fontSize: 15, fontWeight: 600 }}>Drop files here</span>
        </div>
      )}

      {fileError && (
        <div style={{ marginBottom: 8, padding: '6px 12px', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 'var(--cr-radius-sm)', color: 'var(--cr-danger)', fontSize: 12 }}>{fileError}</div>
      )}

      {pendingFiles.length > 0 && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
          {pendingFiles.map((pf, i) => (
            <div key={`${pf.attachment.filename}-${i}`} style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 6, background: 'var(--cr-surface)', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius-sm)', padding: 4, maxWidth: 180 }}>
              {pf.preview ? <img src={pf.preview} alt="" style={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 6 }} /> : (
                <div style={{ width: 40, height: 40, borderRadius: 6, background: 'var(--cr-surface-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--cr-text-muted)' }}><FileText size={18} /></div>
              )}
              <div style={{ minWidth: 0, flex: 1 }}>
                <div style={{ fontSize: 11, color: 'var(--cr-text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{pf.attachment.filename}</div>
                <div style={{ fontSize: 10, color: 'var(--cr-text-muted)' }}>{formatFileSize(pf.attachment.size_bytes)}</div>
              </div>
              <button onClick={() => setPendingFiles((prev) => prev.filter((_, j) => j !== i))} style={{ position: 'absolute', top: -6, right: -6, width: 18, height: 18, borderRadius: '50%', background: 'var(--cr-text-muted)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', padding: 0 }}>
                <X size={10} />
              </button>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, background: 'var(--cr-surface)', border: `1px solid ${focused || isDragOver ? 'var(--cr-green-600)' : 'var(--cr-border)'}`, borderRadius: 'var(--cr-radius)', padding: '8px 8px 8px 6px', opacity: disabled ? 0.5 : 1, transition: 'border-color 200ms' }}>
        <button onClick={() => fileInputRef.current?.click()} disabled={disabled || isStreaming} style={{ flexShrink: 0, width: 36, height: 36, borderRadius: '50%', background: 'transparent', border: 'none', cursor: disabled || isStreaming ? 'default' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: pendingFiles.length > 0 ? 'var(--cr-green-600)' : 'var(--cr-text-muted)' }} title="Attach file">
          <Paperclip size={18} />
        </button>
        <input ref={fileInputRef} type="file" multiple accept={ALLOWED_EXTENSIONS} onChange={(e) => { if (e.target.files) handleFiles(e.target.files); e.target.value = ''; }} style={{ display: 'none' }} />
        <textarea ref={textareaRef} value={value} onChange={(e) => setValue(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }} onFocus={() => setFocused(true)} onBlur={() => setFocused(false)} disabled={disabled} placeholder={placeholder} rows={1}
          style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', resize: 'none', color: 'var(--cr-text)', fontSize: 14, lineHeight: '24px', minHeight: 24, maxHeight: 24 * 6 + 20, fontFamily: 'inherit' }} />
        {isStreaming ? (
          <button onClick={onStop} style={{ flexShrink: 0, width: 36, height: 36, borderRadius: '50%', background: 'var(--cr-danger)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }} title="Stop"><Square size={16} /></button>
        ) : (
          <button onClick={handleSend} disabled={!canSend} style={{ flexShrink: 0, width: 36, height: 36, borderRadius: '50%', background: canSend ? 'var(--cr-green-900)' : 'var(--cr-border)', border: 'none', cursor: canSend ? 'pointer' : 'default', display: 'flex', alignItems: 'center', justifyContent: 'center', color: canSend ? '#fff' : 'var(--cr-text-muted)', transition: 'background 200ms' }} title="Send"><Send size={16} /></button>
        )}
      </div>
    </div>
  );
}

