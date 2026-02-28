#!/bin/bash
set -e
echo "🚀 AI Portal — Light Theme (TS fixes)"
echo "======================================="
cd /workspaces/AI-PORTAL 2>/dev/null || cd ~/AI-PORTAL 2>/dev/null || { echo "❌ Cannot find AI-PORTAL"; exit 1; }
echo "📁 Working in: $(pwd)"
echo ""
mkdir -p 'frontend/src/components'
cat > 'frontend/src/components/ConversationList.tsx' << 'FILEEOF_frontend_src_components_ConversationList_tsx'
import { useState, useEffect } from 'react';
import { MessageSquare, Plus, Trash2 } from 'lucide-react';
import { api } from '../api/client';

interface Conversation {
  id: string;
  title: string;
  updated_at: string;
  message_count: number;
}

interface ConversationListProps {
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
}

export default function ConversationList({ activeId, onSelect, onNew }: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchConversations = async () => {
    try {
      const data = await api.request<{ conversations: Conversation[] }>('/conversations/');
      setConversations(data.conversations || []);
    } catch {
      console.error('Failed to fetch conversations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchConversations(); }, []);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.request(`/conversations/${id}`, { method: 'DELETE' });
      setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch { console.error('Failed to delete'); }
  };

  if (loading) {
    return <div style={{ padding: '12px', color: 'var(--cr-text-muted)', fontSize: 12, textAlign: 'center' }}>Loading...</div>;
  }

  return (
    <div>
      <button
        onClick={onNew}
        style={{
          display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '8px 12px',
          marginBottom: 4, borderRadius: 'var(--cr-radius-sm)', border: '1px dashed var(--cr-border)',
          background: 'transparent', color: 'var(--cr-text-muted)', fontSize: 12, cursor: 'pointer',
          transition: 'all 120ms',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; e.currentTarget.style.color = 'var(--cr-green-600)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; e.currentTarget.style.color = 'var(--cr-text-muted)'; }}
      >
        <Plus size={14} /> New conversation
      </button>
      {conversations.map((c) => (
        <button
          key={c.id}
          onClick={() => onSelect(c.id)}
          style={{
            display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '8px 12px',
            marginBottom: 2, borderRadius: 'var(--cr-radius-sm)', border: 'none',
            background: activeId === c.id ? 'var(--cr-surface)' : 'transparent',
            cursor: 'pointer', textAlign: 'left', transition: 'background 100ms',
            position: 'relative',
          }}
          onMouseEnter={(e) => { if (activeId !== c.id) e.currentTarget.style.background = 'var(--cr-surface-2)'; }}
          onMouseLeave={(e) => { if (activeId !== c.id) e.currentTarget.style.background = 'transparent'; }}
        >
          <MessageSquare style={{ width: 14, height: 14, color: 'var(--cr-text-muted)', flexShrink: 0 }} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 12, color: activeId === c.id ? 'var(--cr-green-900)' : 'var(--cr-text-secondary)', fontWeight: activeId === c.id ? 500 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {c.title || 'New conversation'}
            </div>
          </div>
          <button
            onClick={(e) => handleDelete(e, c.id)}
            style={{ opacity: 0, position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--cr-text-muted)', padding: 4 }}
            onMouseEnter={(e) => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.color = 'var(--cr-danger)'; }}
          >
            <Trash2 size={12} />
          </button>
        </button>
      ))}
      {conversations.length === 0 && (
        <div style={{ padding: '12px', color: 'var(--cr-text-dim)', fontSize: 11, textAlign: 'center' }}>No conversations yet</div>
      )}
    </div>
  );
}

FILEEOF_frontend_src_components_ConversationList_tsx
echo '  ✅ frontend/src/components/ConversationList.tsx'

mkdir -p 'frontend/src/components'
cat > 'frontend/src/components/Sidebar.tsx' << 'FILEEOF_frontend_src_components_Sidebar_tsx'

import { useLocation, useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  Bot,
  Layers,
  BarChart3,
  LogOut,
  Settings,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ConversationList from './ConversationList';

interface SidebarProps {
  activeConversationId?: string | null;
  onSelectConversation?: (id: string) => void;
  onNewConversation?: () => void;
  onNavigate?: () => void;
}

const NAV_ITEMS = [
  { label: 'Chat', icon: MessageSquare, path: '/' },
  { label: 'Specialists', icon: Bot, path: '/specialists' },
  { label: 'Pipelines', icon: Layers, path: '/pipelines' },
  { label: 'Usage', icon: BarChart3, path: '/usage' },
];

export default function Sidebar({
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onNavigate,
}: SidebarProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--cr-white)',
        borderRight: '1px solid var(--cr-border)',
        flexShrink: 0,
      }}
    >
      {/* Brand */}
      <div style={{ padding: '20px 20px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: 'var(--cr-green-900)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              fontSize: 14,
              fontWeight: 700,
              fontFamily: "'Space Grotesk', sans-serif",
            }}
          >
            C
          </div>
          <div>
            <div
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 600,
                fontSize: 15,
                color: 'var(--cr-text)',
                lineHeight: 1.2,
              }}
            >
              Calculus Research
            </div>
            <div style={{ fontSize: 10, color: 'var(--cr-text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              Financial Innovations
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ padding: '0 12px' }}>
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <button
              key={item.path}
              onClick={() => { navigate(item.path); onNavigate?.(); }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                width: '100%',
                padding: '10px 12px',
                marginBottom: 2,
                borderRadius: 'var(--cr-radius-sm)',
                border: 'none',
                background: isActive ? 'var(--cr-surface)' : 'transparent',
                cursor: 'pointer',
                transition: 'all 120ms',
                color: isActive ? 'var(--cr-green-900)' : 'var(--cr-text-secondary)',
                fontWeight: isActive ? 600 : 400,
                fontSize: 14,
              }}
            >
              <Icon style={{ width: 18, height: 18 }} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Recent chats */}
      {onSelectConversation && (
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', marginTop: 8 }}>
          <div style={{ padding: '8px 20px 4px', fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Recent Chats
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '0 8px' }}>
            <ConversationList
              activeId={activeConversationId ?? null}
              onSelect={onSelectConversation}
              onNew={onNewConversation ?? (() => {})}
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ padding: '12px 12px', borderTop: '1px solid var(--cr-border)', marginTop: 'auto' }}>
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, padding: '0 8px' }}>
            {user.avatar_url ? (
              <img src={user.avatar_url} alt="" style={{ width: 28, height: 28, borderRadius: '50%' }} />
            ) : (
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  background: 'var(--cr-green-600)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 12,
                  fontWeight: 600,
                }}
              >
                {(user.name || user.email)?.[0]?.toUpperCase() ?? 'U'}
              </div>
            )}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--cr-text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user.name || user.email}
              </div>
            </div>
          </div>
        )}
        <div style={{ display: 'flex', gap: 4 }}>
          <button
            onClick={() => navigate('/settings')}
            style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              padding: '8px', borderRadius: 'var(--cr-radius-xs)', border: 'none',
              background: 'transparent', color: 'var(--cr-text-muted)', cursor: 'pointer', fontSize: 12,
            }}
          >
            <Settings size={14} />
          </button>
          <button
            onClick={logout}
            style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              padding: '8px', borderRadius: 'var(--cr-radius-xs)', border: 'none',
              background: 'transparent', color: 'var(--cr-text-muted)', cursor: 'pointer', fontSize: 12,
            }}
          >
            <LogOut size={14} />
            Sign Out
          </button>
        </div>
      </div>
    </aside>
  );
}

FILEEOF_frontend_src_components_Sidebar_tsx
echo '  ✅ frontend/src/components/Sidebar.tsx'

mkdir -p 'frontend/src/components/chat'
cat > 'frontend/src/components/chat/ChatInput.tsx' << 'FILEEOF_frontend_src_components_chat_ChatInput_tsx'
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

FILEEOF_frontend_src_components_chat_ChatInput_tsx
echo '  ✅ frontend/src/components/chat/ChatInput.tsx'

mkdir -p 'frontend/src/components/chat'
cat > 'frontend/src/components/chat/MessageBubble.tsx' << 'FILEEOF_frontend_src_components_chat_MessageBubble_tsx'

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

        {/* Content */}
        {isUser ? (
          <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
        ) : (
          <div className="prose prose-sm max-w-none" style={{ color: 'inherit' }}>
            <div dangerouslySetInnerHTML={{ __html: message.content.replace(/\n/g, '<br/>') }} />
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

FILEEOF_frontend_src_components_chat_MessageBubble_tsx
echo '  ✅ frontend/src/components/chat/MessageBubble.tsx'

mkdir -p 'frontend/src/components/chat'
cat > 'frontend/src/components/chat/ModelSelector.tsx' << 'FILEEOF_frontend_src_components_chat_ModelSelector_tsx'
import { useState, useRef, useEffect } from 'react';
import { ChevronDown, ChevronRight, Crown, Sparkles, Zap } from 'lucide-react';
import type { LLMProvider } from '../../types';

const PROVIDER_COLORS: Record<string, string> = {
  openai: '#3E9B5F', anthropic: '#F2A41F', google: '#4285F4',
  grok: '#D64545', deepseek: '#7C8CF5', mistral: '#E8853D', groq: '#E8853D',
};

const TIER_CONFIG: Record<string, { icon: typeof Crown; color: string }> = {
  top: { icon: Crown, color: '#F2A41F' },
  mid: { icon: Sparkles, color: 'var(--cr-text-muted)' },
  budget: { icon: Zap, color: 'var(--cr-green-600)' },
};

interface ModelSelectorProps {
  providers: LLMProvider[];
  selectedProvider: string | null;
  selectedModel: string | null;
  onSelect: (provider: string, model: string) => void;
  mode: 'grid' | 'compact';
}

function formatPrice(input?: number, output?: number): string {
  if (input == null || output == null) return '';
  if (input < 1) return `$${input.toFixed(2)}/$${output.toFixed(2)}`;
  return `$${input.toFixed(2)}/$${output.toFixed(0)}`;
}

function GridSelector({ providers, selectedProvider, selectedModel, onSelect }: Omit<ModelSelectorProps, 'mode'>) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    providers.forEach((p, i) => { init[p.id] = i === 0; });
    return init;
  });

  useEffect(() => {
    if (selectedProvider) setExpanded((prev) => ({ ...prev, [selectedProvider]: true }));
  }, [selectedProvider]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxWidth: 700, width: '100%' }}>
      {providers.map((prov) => {
        const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
        const isExpanded = expanded[prov.id] ?? false;
        return (
          <div key={prov.id} style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', overflow: 'hidden' }}>
            <button
              onClick={() => setExpanded((prev) => ({ ...prev, [prov.id]: !prev[prov.id] }))}
              style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: '12px 16px', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: accent, flexShrink: 0 }} />
              <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--cr-text)', flex: 1, textAlign: 'left', fontFamily: "'Space Grotesk', sans-serif" }}>{prov.name}</span>
              <span style={{ fontSize: 11, color: 'var(--cr-text-muted)', marginRight: 4 }}>{prov.models.length} model{prov.models.length !== 1 ? 's' : ''}</span>
              {isExpanded ? <ChevronDown style={{ width: 16, height: 16, color: 'var(--cr-text-muted)' }} /> : <ChevronRight style={{ width: 16, height: 16, color: 'var(--cr-text-muted)' }} />}
            </button>
            {isExpanded && (
              <div style={{ padding: '0 8px 8px' }}>
                {prov.models.map((m) => {
                  const isSelected = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button key={m.id} onClick={() => onSelect(prov.id, m.id)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 10, width: '100%', padding: '10px 12px', margin: '2px 0',
                        borderRadius: 'var(--cr-radius-sm)', border: isSelected ? `1px solid ${accent}` : '1px solid transparent',
                        background: isSelected ? `${accent}10` : 'transparent', cursor: 'pointer', textAlign: 'left', transition: 'all 100ms',
                      }}
                      onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.background = 'var(--cr-surface)'; }}
                      onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.background = 'transparent'; }}
                    >
                      <TierIcon style={{ width: 14, height: 14, color: tier.color, flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: isSelected ? 600 : 400, color: 'var(--cr-text)' }}>{m.name}</div>
                        {m.description && <div style={{ fontSize: 11, color: 'var(--cr-text-muted)', marginTop: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{m.description}</div>}
                      </div>
                      {m.context && <span style={{ fontSize: 10, color: 'var(--cr-text-muted)', background: 'var(--cr-surface-2)', padding: '2px 6px', borderRadius: 'var(--cr-radius-xs)', flexShrink: 0 }}>{m.context}</span>}
                      <span style={{ fontSize: 11, color: 'var(--cr-text-muted)', flexShrink: 0 }}>{formatPrice(m.input_price, m.output_price)}/1M</span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function CompactSelector({ providers, selectedProvider, selectedModel, onSelect }: Omit<ModelSelectorProps, 'mode'>) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => { if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) setIsOpen(false); };
    if (isOpen) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isOpen]);

  let selectedModelName = 'Select model';
  let selectedAccent = 'var(--cr-green-600)';
  for (const prov of providers) {
    for (const m of prov.models) {
      if (prov.id === selectedProvider && m.id === selectedModel) {
        selectedModelName = m.name;
        selectedAccent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
      }
    }
  }

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button onClick={() => setIsOpen(!isOpen)}
        style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px', borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)', background: 'var(--cr-white)', cursor: 'pointer' }}>
        <div style={{ width: 8, height: 8, borderRadius: '50%', background: selectedAccent }} />
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--cr-text)' }}>{selectedModelName}</span>
        <ChevronDown style={{ width: 14, height: 14, color: 'var(--cr-text-muted)', transform: isOpen ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 150ms' }} />
      </button>
      {isOpen && (
        <div style={{ position: 'absolute', top: 'calc(100% + 6px)', left: 0, minWidth: 340, maxHeight: 420, overflowY: 'auto', background: 'var(--cr-white)', border: '1px solid var(--cr-border)', borderRadius: 'var(--cr-radius)', padding: 8, zIndex: 50, boxShadow: '0 8px 30px rgba(0,0,0,0.08)' }}>
          {providers.map((prov) => {
            const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
            return (
              <div key={prov.id}>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', padding: '8px 10px 4px', letterSpacing: '0.04em', textTransform: 'uppercase' }}>{prov.name}</div>
                {prov.models.map((m) => {
                  const isActive = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button key={m.id} onClick={() => { onSelect(prov.id, m.id); setIsOpen(false); }}
                      style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '8px 10px', borderRadius: 'var(--cr-radius-xs)', border: 'none', background: isActive ? `${accent}10` : 'transparent', cursor: 'pointer', textAlign: 'left', transition: 'background 100ms' }}
                      onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = 'var(--cr-surface)'; }}
                      onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = isActive ? `${accent}10` : 'transparent'; }}>
                      <TierIcon style={{ width: 13, height: 13, color: tier.color, flexShrink: 0 }} />
                      <span style={{ flex: 1, fontSize: 13, fontWeight: isActive ? 500 : 400, color: 'var(--cr-text)' }}>{m.name}</span>
                      <span style={{ fontSize: 11, color: 'var(--cr-text-muted)', flexShrink: 0 }}>{formatPrice(m.input_price, m.output_price)}</span>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function ModelSelector(props: ModelSelectorProps) {
  return props.mode === 'grid' ? <GridSelector {...props} /> : <CompactSelector {...props} />;
}

FILEEOF_frontend_src_components_chat_ModelSelector_tsx
echo '  ✅ frontend/src/components/chat/ModelSelector.tsx'

mkdir -p 'frontend/src/components/chat'
cat > 'frontend/src/components/chat/SpecialistHeader.tsx' << 'FILEEOF_frontend_src_components_chat_SpecialistHeader_tsx'
import type { Specialist } from '../../types';

interface SpecialistHeaderProps {
  specialist: Specialist;
  messageCount: number;
}

export default function SpecialistHeader({ specialist, messageCount }: SpecialistHeaderProps) {
  return (
    <div
      style={{
        height: 56,
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'var(--cr-white)',
        borderBottom: '1px solid var(--cr-border)',
        flexShrink: 0,
      }}
    >
      <div style={{ minWidth: 0, flex: 1, marginRight: 16 }}>
        <div style={{ color: 'var(--cr-text)', fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, fontSize: 16, lineHeight: '20px' }}>
          {specialist.name}
        </div>
        <div style={{ color: 'var(--cr-text-muted)', fontSize: 12, marginTop: 2, overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
          {specialist.description}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
        <span style={{ background: 'var(--cr-surface)', color: 'var(--cr-text-muted)', fontSize: 11, padding: '3px 10px', borderRadius: 20, border: '1px solid var(--cr-border)' }}>
          {specialist.provider} / {specialist.model}
        </span>
        {messageCount > 0 && (
          <span style={{ background: 'var(--cr-surface)', color: 'var(--cr-text-muted)', fontSize: 11, padding: '3px 10px', borderRadius: 20, border: '1px solid var(--cr-border)' }}>
            {messageCount} msg{messageCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  );
}

FILEEOF_frontend_src_components_chat_SpecialistHeader_tsx
echo '  ✅ frontend/src/components/chat/SpecialistHeader.tsx'

mkdir -p 'frontend/src'
cat > 'frontend/src/index.css' << 'FILEEOF_frontend_src_index_css'
@import "tailwindcss";
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
  /* Calculus Research — Light Institutional Theme */
  --cr-green-900: #0F4D2C;
  --cr-green-700: #1A6B3C;
  --cr-green-600: #3E9B5F;
  --cr-green-400: #5FBD7A;
  --cr-green-50: #EDF7F0;
  --cr-gold-500: #F2A41F;
  --cr-gold-400: #F5B94E;

  /* Light surfaces */
  --cr-surface: #F7F9F8;
  --cr-surface-2: #EEF2F0;
  --cr-white: #FFFFFF;
  --cr-charcoal: #1C1F22;

  /* Borders & muted */
  --cr-border: #DDE6E1;
  --cr-border-dark: #C4D1CA;
  --cr-mist: #A9B7AE;
  --cr-danger: #D64545;

  /* Text — dark on light */
  --cr-text: #1C1F22;
  --cr-text-secondary: #4A5650;
  --cr-text-muted: #7A8A80;
  --cr-text-dim: #A9B7AE;

  /* Layout */
  --sidebar-width: 260px;
  --cr-radius: 14px;
  --cr-radius-sm: 8px;
  --cr-radius-xs: 6px;

  /* Legacy aliases */
  --navy: var(--cr-surface);
  --navy-light: var(--cr-surface-2);
  --navy-dark: var(--cr-white);
  --blue: var(--cr-green-600);
  --blue-light: var(--cr-green-400);
  --green: var(--cr-green-600);
  --orange: var(--cr-gold-500);
  --red: var(--cr-danger);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background-color: var(--cr-surface);
  color: var(--cr-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Space Grotesk', system-ui, sans-serif;
  letter-spacing: -0.01em;
}

.cr-focus:focus-visible, *:focus-visible {
  outline: 2px solid var(--cr-gold-500);
  outline-offset: 2px;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--cr-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--cr-mist); }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.animate-fade-in-up { animation: fadeInUp 180ms ease-out both; }
.animate-blink { animation: blink 800ms infinite; }

@keyframes subtlePulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.animate-pulse-glow { animation: subtlePulse 2s ease-in-out infinite; }
button:active:not(:disabled) { transform: translateY(1px); }
::selection { background: var(--cr-green-600); color: #FFFFFF; }

FILEEOF_frontend_src_index_css
echo '  ✅ frontend/src/index.css'

mkdir -p 'frontend/src/pages'
cat > 'frontend/src/pages/ChatPage.tsx' << 'FILEEOF_frontend_src_pages_ChatPage_tsx'
import { useState, useEffect, useRef, useCallback } from 'react';
import { ChevronDown, ChevronUp, Bot } from 'lucide-react';
import { api } from '../api/client';
import type { Specialist } from '../types';
import { useChat } from '../hooks/useChat';
import MessageBubble from '../components/chat/MessageBubble';
import ChatInput from '../components/chat/ChatInput';
import SpecialistHeader from '../components/chat/SpecialistHeader';

const DEFAULT_PROMPTS = [
  'Help me understand this topic in detail',
  'What are the key considerations for this situation?',
];

export default function ChatPage() {
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [selected, setSelected] = useState<Specialist | null>(null);
  const [showSpecialistPanel, setShowSpecialistPanel] = useState(false);
  const { messages, isStreaming, error, sendMessage, stopStreaming } = useChat(selected?.id ?? null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollPill, setShowScrollPill] = useState(false);

  useEffect(() => {
    api.request<{ specialists: Specialist[] }>('/specialists/')
      .then((data) => { setSpecialists(data.specialists); if (data.specialists.length > 0) setSelected(data.specialists[0]); })
      .catch(console.error);
  }, []);

  const isAtBottom = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < 100;
  }, []);

  useEffect(() => {
    if (isAtBottom()) { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); setShowScrollPill(false); }
    else if (messages.length > 0) setShowScrollPill(true);
  }, [messages, isAtBottom]);

  return (
    <div className="flex" style={{ height: '100vh', background: 'var(--cr-surface)' }}>
      {/* Desktop specialist sidebar */}
      <div className="hidden md:block overflow-y-auto" style={{ width: 260, borderRight: '1px solid var(--cr-border)', background: 'var(--cr-white)', padding: 16, flexShrink: 0 }}>
        <h2 style={{ fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12, padding: '0 4px' }}>
          Specialists
        </h2>
        {specialists.map((s) => (
          <button
            key={s.id}
            onClick={() => setSelected(s)}
            style={{
              width: '100%', textAlign: 'left', padding: '10px 12px', marginBottom: 2,
              borderRadius: 'var(--cr-radius-sm)', border: 'none',
              background: selected?.id === s.id ? 'var(--cr-surface)' : 'transparent',
              cursor: 'pointer', transition: 'all 100ms',
            }}
          >
            <div style={{ fontSize: 13, fontWeight: selected?.id === s.id ? 600 : 400, color: selected?.id === s.id ? 'var(--cr-green-900)' : 'var(--cr-text-secondary)' }}>
              {s.name}
            </div>
            <div style={{ fontSize: 11, color: 'var(--cr-text-muted)', marginTop: 2 }}>{s.description}</div>
          </button>
        ))}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col" style={{ minWidth: 0, overflow: 'hidden' }}>
        {/* Mobile specialist selector */}
        <div className="md:hidden" style={{ borderBottom: '1px solid var(--cr-border)', background: 'var(--cr-white)' }}>
          <button onClick={() => setShowSpecialistPanel(!showSpecialistPanel)} className="w-full flex items-center justify-between px-4 py-3" style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--cr-text)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Bot style={{ width: 16, height: 16, color: 'var(--cr-green-600)' }} />
              <span style={{ fontSize: 14, fontWeight: 500 }}>{selected?.name ?? 'Select Specialist'}</span>
            </div>
            {showSpecialistPanel ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
          {showSpecialistPanel && (
            <div style={{ padding: '0 8px 10px' }}>
              {specialists.map((s) => (
                <button key={s.id} onClick={() => { setSelected(s); setShowSpecialistPanel(false); }}
                  style={{ width: '100%', textAlign: 'left', padding: '10px 12px', margin: '2px 0', borderRadius: 'var(--cr-radius-sm)', border: 'none', background: selected?.id === s.id ? 'var(--cr-surface)' : 'transparent', cursor: 'pointer' }}>
                  <div style={{ fontSize: 13, fontWeight: selected?.id === s.id ? 600 : 400, color: selected?.id === s.id ? 'var(--cr-green-900)' : 'var(--cr-text-secondary)' }}>{s.name}</div>
                  <div style={{ fontSize: 11, color: 'var(--cr-text-muted)', marginTop: 2 }}>{s.description}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        {selected ? (
          <>
            <div className="hidden md:block"><SpecialistHeader specialist={selected} messageCount={messages.length} /></div>
            <div ref={scrollContainerRef} onScroll={() => { if (isAtBottom()) setShowScrollPill(false); }} className="flex-1 overflow-y-auto" style={{ padding: 16 }}>
              {messages.length === 0 ? (
                <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 12 }}>
                  <div style={{ width: 48, height: 48, borderRadius: 12, background: 'var(--cr-green-50)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Bot style={{ width: 24, height: 24, color: 'var(--cr-green-600)' }} />
                  </div>
                  <div style={{ color: 'var(--cr-text)', fontSize: 18, fontWeight: 600, fontFamily: "'Space Grotesk', sans-serif" }}>{selected.name}</div>
                  <div style={{ color: 'var(--cr-text-muted)', fontSize: 13, maxWidth: 400 }}>{selected.description}</div>
                  <div style={{ fontSize: 11, color: 'var(--cr-text-dim)' }}>Powered by {selected.provider}/{selected.model}</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 500, marginTop: 8 }}>
                    {DEFAULT_PROMPTS.map((prompt) => (
                      <button key={prompt} onClick={() => sendMessage(prompt)}
                        style={{ background: 'var(--cr-white)', border: '1px solid var(--cr-border)', borderRadius: 20, color: 'var(--cr-text-secondary)', fontSize: 12, padding: '8px 16px', cursor: 'pointer', transition: 'all 150ms' }}
                        onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}>
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <MessageBubble key={idx} message={msg} isStreaming={isStreaming && idx === messages.length - 1 && msg.role === 'assistant'} />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
            {showScrollPill && (
              <div style={{ position: 'relative' }}>
                <button onClick={() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); setShowScrollPill(false); }}
                  style={{ position: 'absolute', bottom: 8, left: '50%', transform: 'translateX(-50%)', background: 'var(--cr-green-900)', border: 'none', borderRadius: 20, color: '#fff', fontSize: 12, padding: '5px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, zIndex: 10 }}>
                  <ChevronDown size={14} /> New messages
                </button>
              </div>
            )}
            {error && <div style={{ margin: '0 16px 8px', padding: '8px 12px', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 8, color: 'var(--cr-danger)', fontSize: 13 }}>{error}</div>}
            <ChatInput onSend={sendMessage} onStop={stopStreaming} isStreaming={isStreaming} disabled={false} specialistName={selected.name} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p style={{ color: 'var(--cr-text-muted)' }}>Select a specialist to begin</p>
          </div>
        )}
      </div>
    </div>
  );
}

FILEEOF_frontend_src_pages_ChatPage_tsx
echo '  ✅ frontend/src/pages/ChatPage.tsx'

mkdir -p 'frontend/src/pages'
cat > 'frontend/src/pages/LLMChatPage.tsx' << 'FILEEOF_frontend_src_pages_LLMChatPage_tsx'
import { useState, useEffect, useRef, useCallback } from 'react';
import { Plus, ChevronDown, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import type { LLMProvider } from '../types';
import { useDirectChat } from '../hooks/useDirectChat';
import MessageBubble from '../components/chat/MessageBubble';
import ChatInput from '../components/chat/ChatInput';
import ModelSelector from '../components/chat/ModelSelector';

const SUGGESTION_PROMPTS = [
  'Explain CRE cap rate compression and its impact on deal underwriting',
  'What are the key financial covenants in a CMBS loan?',
  'Help me analyze a multifamily acquisition pro forma',
  'Compare fixed vs floating rate debt structures for a bridge loan',
];

export default function LLMChatPage() {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [loadingModels, setLoadingModels] = useState(true);

  const { messages, isStreaming, error, sendMessage, stopStreaming, clearChat } =
    useDirectChat(selectedProvider, selectedModel);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollPill, setShowScrollPill] = useState(false);

  useEffect(() => {
    api
      .request<{ providers: LLMProvider[] }>('/chat/direct/models')
      .then((data) => {
        setProviders(data.providers);
        if (data.providers.length > 0) {
          const first = data.providers[0];
          setSelectedProvider(first.id);
          const topModel = first.models.find((m) => m.tier === 'top');
          setSelectedModel(topModel?.id ?? first.models[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoadingModels(false));
  }, []);

  const isAtBottom = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < 100;
  }, []);

  useEffect(() => {
    if (isAtBottom()) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setShowScrollPill(false);
    } else if (messages.length > 0) {
      setShowScrollPill(true);
    }
  }, [messages, isAtBottom]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setShowScrollPill(false);
  };

  const handleScroll = () => {
    if (isAtBottom()) setShowScrollPill(false);
  };

  const handleModelSelect = (provider: string, model: string) => {
    setSelectedProvider(provider);
    setSelectedModel(model);
  };

  let selectedModelName = '';
  for (const prov of providers) {
    for (const m of prov.models) {
      if (prov.id === selectedProvider && m.id === selectedModel) {
        selectedModelName = m.name;
      }
    }
  }

  const hasMessages = messages.length > 0;

  if (loadingModels) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--cr-surface)' }}>
        <div style={{ color: 'var(--cr-text-muted)', fontSize: 14 }}>Loading models...</div>
      </div>
    );
  }

  if (!hasMessages) {
    return (
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 24, gap: 24, overflow: 'auto', background: 'var(--cr-surface)' }}>
        <div style={{ textAlign: 'center', marginBottom: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 8 }}>
            <Sparkles style={{ width: 24, height: 24, color: 'var(--cr-green-600)' }} />
            <span style={{ fontSize: 20, fontWeight: 700, color: 'var(--cr-text)', letterSpacing: '-0.02em', fontFamily: "'Space Grotesk', sans-serif" }}>
              Calculus Research
            </span>
          </div>
          <div style={{ fontSize: 13, color: 'var(--cr-text-muted)' }}>Direct LLM Access</div>
        </div>

        <h1 style={{ fontSize: 24, fontWeight: 600, color: 'var(--cr-text)', textAlign: 'center', margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>
          What do you want to know?
        </h1>

        <div style={{ width: '100%', maxWidth: 700 }}>
          <ChatInput onSend={sendMessage} onStop={stopStreaming} isStreaming={isStreaming} disabled={!selectedModel} specialistName={selectedModelName || undefined} />
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
          <ModelSelector providers={providers} selectedProvider={selectedProvider} selectedModel={selectedModel} onSelect={handleModelSelect} mode="grid" />
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 700 }}>
          {SUGGESTION_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => sendMessage(prompt)}
              style={{
                background: 'var(--cr-white)',
                border: '1px solid var(--cr-border)',
                borderRadius: 20,
                color: 'var(--cr-text-secondary)',
                fontSize: 12,
                padding: '8px 16px',
                cursor: 'pointer',
                transition: 'all 150ms',
                maxWidth: 340,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; e.currentTarget.style.color = 'var(--cr-text)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; e.currentTarget.style.color = 'var(--cr-text-secondary)'; }}
            >
              {prompt}
            </button>
          ))}
        </div>

        {error && (
          <div style={{ padding: '8px 14px', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 8, color: 'var(--cr-danger)', fontSize: 13, maxWidth: 700, width: '100%' }}>
            {error}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col" style={{ height: '100vh', background: 'var(--cr-surface)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 20px', borderBottom: '1px solid var(--cr-border)', flexShrink: 0, background: 'var(--cr-white)' }}>
        <ModelSelector providers={providers} selectedProvider={selectedProvider} selectedModel={selectedModel} onSelect={handleModelSelect} mode="compact" />
        <div style={{ flex: 1 }} />
        <button
          onClick={() => clearChat()}
          style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px',
            borderRadius: 'var(--cr-radius-sm)', border: '1px solid var(--cr-border)',
            background: 'var(--cr-white)', color: 'var(--cr-text-secondary)', fontSize: 13, cursor: 'pointer',
          }}
        >
          <Plus style={{ width: 14, height: 14 }} />
          New Chat
        </button>
      </div>

      <div ref={scrollContainerRef} onScroll={handleScroll} className="flex-1 overflow-y-auto" style={{ padding: 16 }}>
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} isStreaming={isStreaming && idx === messages.length - 1 && msg.role === 'assistant'} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {showScrollPill && (
        <div style={{ position: 'relative' }}>
          <button onClick={scrollToBottom} style={{ position: 'absolute', bottom: 8, left: '50%', transform: 'translateX(-50%)', background: 'var(--cr-green-900)', border: 'none', borderRadius: 20, color: '#fff', fontSize: 12, padding: '5px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, zIndex: 10 }}>
            <ChevronDown size={14} /> New messages
          </button>
        </div>
      )}

      {error && (
        <div style={{ margin: '0 16px 8px', padding: '8px 12px', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 8, color: 'var(--cr-danger)', fontSize: 13 }}>
          {error}
        </div>
      )}

      <ChatInput onSend={sendMessage} onStop={stopStreaming} isStreaming={isStreaming} disabled={!selectedModel} specialistName={selectedModelName || undefined} />
    </div>
  );
}

FILEEOF_frontend_src_pages_LLMChatPage_tsx
echo '  ✅ frontend/src/pages/LLMChatPage.tsx'

mkdir -p 'frontend/src/pages'
cat > 'frontend/src/pages/LoginPage.tsx' << 'FILEEOF_frontend_src_pages_LoginPage_tsx'
import { useState } from 'react';
import { Shield, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email.trim()) return;
    setLoading(true);
    setError('');
    try {
      await login(email.trim());
    } catch (err: any) {
      setError(err?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--cr-surface)',
        padding: 24,
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 400,
          background: 'var(--cr-white)',
          borderRadius: 'var(--cr-radius)',
          border: '1px solid var(--cr-border)',
          padding: '48px 40px',
        }}
      >
        {/* Brand */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: 12,
              background: 'var(--cr-green-900)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16,
            }}
          >
            <Shield style={{ width: 24, height: 24, color: '#FFFFFF' }} />
          </div>
          <h1
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: 22,
              fontWeight: 700,
              color: 'var(--cr-text)',
              margin: '0 0 4px',
              letterSpacing: '-0.02em',
            }}
          >
            Calculus Research
          </h1>
          <p style={{ fontSize: 13, color: 'var(--cr-text-muted)', margin: 0 }}>
            AI Intelligence Portal v2.2
          </p>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 14px',
              background: '#FEF2F2',
              border: '1px solid #FECACA',
              borderRadius: 'var(--cr-radius-sm)',
              marginBottom: 16,
              color: 'var(--cr-danger)',
              fontSize: 13,
            }}
          >
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {/* Email field */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--cr-text-secondary)', marginBottom: 6 }}>
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder="finance@calculusresearch.io"
            style={{
              width: '100%',
              padding: '12px 14px',
              borderRadius: 'var(--cr-radius-sm)',
              border: '1px solid var(--cr-border)',
              background: 'var(--cr-white)',
              color: 'var(--cr-text)',
              fontSize: 14,
              outline: 'none',
              transition: 'border-color 150ms',
            }}
            onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; }}
          />
          <p style={{ fontSize: 11, color: 'var(--cr-text-muted)', marginTop: 4 }}>
            Domain-restricted access: @calculusresearch.io
          </p>
        </div>

        {/* Sign in button */}
        <button
          onClick={handleSubmit}
          disabled={loading || !email.trim()}
          style={{
            width: '100%',
            padding: '12px',
            borderRadius: 'var(--cr-radius-sm)',
            border: 'none',
            background: 'var(--cr-green-900)',
            color: '#FFFFFF',
            fontSize: 14,
            fontWeight: 600,
            cursor: loading ? 'wait' : 'pointer',
            opacity: loading || !email.trim() ? 0.6 : 1,
            transition: 'opacity 150ms',
          }}
        >
          {loading ? 'Signing in...' : 'Sign In'}
        </button>

        <p style={{ textAlign: 'center', fontSize: 11, color: 'var(--cr-text-dim)', marginTop: 20 }}>
          Calculus Holdings LLC · Secured with JWT authentication
        </p>
      </div>
    </div>
  );
}

FILEEOF_frontend_src_pages_LoginPage_tsx
echo '  ✅ frontend/src/pages/LoginPage.tsx'


echo ""
echo "📦 Committing..."
git add -A
git status --short
git commit --no-gpg-sign -m "fix: TS errors — useAuth hook, token fields, onNavigate prop, remove react-markdown" || echo "Nothing to commit"

echo "🚀 Pushing..."
git push origin main

echo ""
echo "✅ Done! On VM run:"
echo "  cd ~/AI-PORTAL && git fetch origin main && git reset --hard origin/main"
echo "  sudo docker compose -f docker-compose.v2.yml build --no-cache frontend"
echo "  sudo docker compose -f docker-compose.v2.yml up -d --force-recreate"
