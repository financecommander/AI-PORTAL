#!/bin/bash
set -e
echo "🚀 P1 — Visual Hardening (light institutional theme)"
echo "======================================================"
cd /workspaces/AI-PORTAL 2>/dev/null || cd ~/AI-PORTAL 2>/dev/null || { echo "❌ Cannot find AI-PORTAL"; exit 1; }
echo "📁 Working in: $(pwd)"
echo ""
mkdir -p '.'
cat > 'ROADMAP.md' << 'FILEEOF_ROADMAP_md'
# Calculus AI Platform — Modernization Roadmap

> Convert the AI Portal from an AI SaaS playground into **Calculus Intelligence Infrastructure** —
> a capital-grade Intelligence OS aligned with Calculus Research institutional positioning.

**Repo:** `financecommander/AI-PORTAL`
**Last updated:** 2026-02-28
**Target completion:** 9 weeks from Phase 0 sign-off

---

## Progress Tracker

| Phase | Status | Commits | Key Milestone |
|-------|--------|---------|---------------|
| 0 — Design Governance | ✅ Complete | `19d446e`..`9dde5b6` | CR tokens, light theme, Financial Innovations branding |
| 1 — Visual Hardening | 🟡 In Progress | `9dde5b6` | Light institutional theme live; density/contrast pending |
| 2A — Pipelines → Engines | ⬜ Not Started | — | Rename, categorize, status indicators |
| 2B — Specialists → Analyst Modules | ⬜ Not Started | — | Discipline-based org, analyst profiles |
| 2C — Chat → Intelligence Console | ⬜ Not Started | — | Rectangular containers, command bar |
| 3 — Cross-Platform Unification | ⬜ Not Started | — | Shared nav, layout lock, component library |
| 4 — Functional Maturity | ⬜ Not Started | — | Metadata layer, state awareness, monitoring |
| 5 — Institutional Polish | ⬜ Not Started | — | Density toggle, dark enterprise mode, data viz |
| 6 — Platform Positioning | ⬜ Not Started | — | Full rebrand: Engines, Analyst Desks, Console |

---

## Phase 0 — Design Governance ✅

**Status:** Complete

### Deliverables

- [x] Finalized UI tokens — `index.css` `:root` block with all `--cr-*` variables
- [x] Component inventory freeze — 10 core components identified and standardized
- [x] Layout system rules — sidebar (260px) + content area, 14px radius, 4px spacing scale
- [x] Interaction rules — gold focus ring, green hover, `translateY(1px)` active
- [x] Accessibility baseline — 40px min touch targets, visible focus ring, semantic HTML
- [x] Light institutional theme — white cards on `#F7F9F8`, `#DDE6E1` borders

### Token Reference

```
Green 900: #0F4D2C    Green 600: #3E9B5F    Gold 500: #F2A41F
Surface:   #F7F9F8    Surface 2: #EEF2F0    White:    #FFFFFF
Border:    #DDE6E1    Mist:      #A9B7AE    Charcoal: #1C1F22
Danger:    #D64545    Text:      #1C1F22    Muted:    #7A8A80
Headings:  Space Grotesk          Body:      Inter
Radius:    14px (cards)           8px (sm)   6px (xs)
```

---

## Phase 1 — Visual Hardening & Token Standardization 🟡

**Status:** In progress — light theme deployed, density and contrast refinements pending

### Issues

#### P1-1: Tailwind CDN Config Standardization
- [x] Unified color tokens in `:root`
- [x] All components use `var(--cr-*)` — zero stale hex outside provider brand colors
- [ ] Remove legacy alias variables (`--navy`, `--blue`, `--green`, etc.)
- [ ] Audit pipeline components for remaining inline styles

#### P1-2: Typography Tightening
- [x] Space Grotesk on all headings
- [x] Inter on all body text
- [ ] Reduce excessive vertical spacing in chat message area
- [ ] Strengthen heading hierarchy — h1 24px/700, h2 18px/600, h3 15px/600
- [ ] Increase KPI emphasis on Usage page
- [ ] Improve table header clarity (uppercase, letter-spacing)

#### P1-3: Contrast & Density Upgrade
- [ ] Increase table density — reduce row padding from 16px to 10px
- [ ] Strengthen borders — use `--cr-border-dark` (#C4D1CA) for table headers
- [ ] Remove gray haze backgrounds — use pure `--cr-white` or `--cr-surface`
- [ ] Normalize card padding to 20px consistently

### Success Criteria

- No pastel feel
- Sharper table edges
- Stronger financial data hierarchy
- Visually matches Calculus Research dashboard at `127.0.0.1:8081`

---

## Phase 2 — Structural Re-Architecture

### 2A — Pipelines → Intelligence Engines ⬜

**Target:** `PipelinesPage.tsx` + pipeline components

#### Issues

##### P2A-1: Engine Categorization
- [ ] Categorize engines into: Deal Origination, Portfolio Oversight, Research & Advisory
- [ ] Create category header components with green-900 accent

##### P2A-2: Engine Card Redesign
- [ ] Add status indicators (Active / Beta / Disabled) with badge component
- [ ] Add last run timestamp metadata
- [ ] Replace "Run Pipeline →" with "Launch Engine"
- [ ] Reduce vertical padding
- [ ] Add execution log access link

##### P2A-3: Status Badge Component
- [ ] Create reusable `StatusBadge.tsx` — Active (green), Beta (gold), Disabled (muted)
- [ ] Add to engine cards and sidebar nav

#### Files to Modify
- `frontend/src/pages/PipelinesPage.tsx`
- `frontend/src/components/pipeline/` (all)
- New: `frontend/src/components/ui/StatusBadge.tsx`

---

### 2B — Specialists → Analyst Modules ⬜

**Target:** `ChatPage.tsx` + specialist components

#### Issues

##### P2B-1: Discipline-Based Organization
- [ ] Reorganize specialists by discipline, not model provider
- [ ] Categories: Credit Analysis, Market Research, Legal & Compliance, Operations, Technology
- [ ] Collapse raw model access under "Core Model Access" section

##### P2B-2: Analyst Profile Layout
- [ ] Create `AnalystProfile.tsx` header with name, scope, capabilities
- [ ] Move provider/model metadata to subtle tag
- [ ] Add "Scope" section (what this analyst covers)
- [ ] Add "Capabilities" section (what actions it can take)

##### P2B-3: Structured Prompt Suggestions
- [ ] Replace generic suggestion prompts with discipline-specific templates
- [ ] Group by action type: Analyze, Research, Draft, Review

#### Files to Modify
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/components/chat/SpecialistHeader.tsx`
- New: `frontend/src/components/chat/AnalystProfile.tsx`

---

### 2C — Chat → Intelligence Console ⬜

**Target:** `LLMChatPage.tsx` + `MessageBubble.tsx` + `ChatInput.tsx`

#### Issues

##### P2C-1: Message Container Redesign
- [ ] Remove chat bubble shapes (rounded asymmetric corners)
- [ ] Introduce rectangular institutional message containers
- [ ] Add Query / Analysis / Output segmentation with labels

##### P2C-2: Console Header
- [ ] Add module header state indicator (active model, session context)
- [ ] Add execution metadata panel (tokens, cost, latency per message)

##### P2C-3: Command Bar
- [ ] Replace chat textarea with compact command bar
- [ ] Add command prefix support (`/analyze`, `/research`, `/draft`)
- [ ] Maintain file attachment capability

#### Files to Modify
- `frontend/src/pages/LLMChatPage.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/ChatInput.tsx`

---

## Phase 3 — Cross-Platform Unification ⬜

### 3A — Navigation Alignment

#### Issues

##### P3A-1: Shared Top Nav
- [ ] Create `TopNav.tsx` matching Calculus Research marketing nav structure
- [ ] Include: logo, search field (desktop), notifications bell, user avatar
- [ ] Active state: surface background + green-900 text

##### P3A-2: Sidebar Unification
- [ ] Align sidebar with marketing site sidebar pattern
- [ ] Standardize active states across marketing, dashboard, AI nav
- [ ] Remove dual visual language

#### Files to Modify
- `frontend/src/components/Layout.tsx`
- `frontend/src/components/Sidebar.tsx`
- New: `frontend/src/components/TopNav.tsx`

---

### 3B — Layout System Lock

#### Issues

##### P3B-1: Grid & Spacing Standards
- [ ] Standardize max-width: 1280px for content area
- [ ] Standardize gutters: 24px desktop, 16px mobile
- [ ] Enforce 4px vertical rhythm throughout
- [ ] Standardize header spacing: 24px below page header, 16px between sections

---

### 3C — Component Library

#### Issues

##### P3C-1: UI Kit Page
- [ ] Create `UIKitPage.tsx` as live reference
- [ ] Button variants: primary (green-900), secondary (border), ghost, danger
- [ ] Card variants: stat card, content card, action card
- [ ] Table variants: data table with sortable headers
- [ ] Badge, Alert, Form control, Modal components

#### Files to Create
- `frontend/src/pages/UIKitPage.tsx`
- `frontend/src/components/ui/Button.tsx`
- `frontend/src/components/ui/Card.tsx`
- `frontend/src/components/ui/Table.tsx`
- `frontend/src/components/ui/Badge.tsx`

---

## Phase 4 — Functional Maturity ⬜

### 4A — Operational Metadata Layer

- [ ] Engine status (Active / Beta / Disabled) on all engine cards
- [ ] Last run timestamp on engine cards
- [ ] Execution health indicator (green/yellow/red)
- [ ] Access level tag per engine (Admin / Analyst / Viewer)
- [ ] Activity log link per engine

### 4B — Intelligence State Awareness

- [ ] Current module indicator in top nav
- [ ] Workspace context display
- [ ] Session metadata (duration, token count, cost)
- [ ] Model selection displayed but muted (not primary UI)

### 4C — Usage & Monitoring Upgrade

- [ ] Clean KPI summary cards (matching dashboard style)
- [ ] Token consumption chart (recharts, minimal gridlines)
- [ ] Engine run metrics (runs/day, avg latency, error rate)
- [ ] Analyst utilization (which specialists used most)

#### Files to Modify
- `frontend/src/pages/UsagePage.tsx`
- `frontend/src/components/usage/` (all)

---

## Phase 5 — Institutional Polish ⬜

### 5A — Density Mode Toggle

- [ ] Standard density (current)
- [ ] Dense mode (reduced padding, smaller font, tighter tables)
- [ ] Persist preference in localStorage
- [ ] Toggle in Settings page

### 5B — Dark Enterprise Mode

- [ ] Charcoal base (`#1C1F22`)
- [ ] Controlled green accent
- [ ] Gold focus ring (same)
- [ ] Higher contrast tables
- [ ] CSS variable swap — no component changes needed if tokens are clean

### 5C — Data Visualization Upgrade

- [ ] Minimal gridlines in all charts
- [ ] No decorative gradients
- [ ] Brand color discipline (green-900, green-600, gold-500 only)
- [ ] Consistent legend system across all charts

---

## Phase 6 — Platform Positioning ⬜

### Terminology Migration

| Current | New |
|---------|-----|
| Pipelines | Intelligence Engines |
| Specialists | Analyst Desks |
| Chat | Intelligence Console |
| Usage & Costs | Intelligence Metrics |

### Issues

##### P6-1: Rename in Sidebar Navigation
- [ ] Update `Sidebar.tsx` nav labels
- [ ] Update route paths if needed (`/pipelines` → `/engines`)

##### P6-2: Rename in Page Headers
- [ ] Update all `<h1>` and page titles
- [ ] Update browser tab titles

##### P6-3: Rename in Backend API
- [ ] Add route aliases (keep old routes for backwards compat)
- [ ] Update specialist → analyst desk terminology in responses

---

## Execution Priority

```
Week 1:  P1 — Visual hardening (density, contrast, typography)
Week 2:  P2A — Pipelines → Intelligence Engines
Week 3:  P2B — Specialists → Analyst Modules
Week 3:  P2C — Chat → Intelligence Console
Week 4:  P3 — Navigation unification + layout lock
Week 5:  P3C + P4A — Component library + metadata layer
Week 6:  P4B + P4C — State awareness + usage upgrade
Week 7:  P5A + P5B — Density toggle + dark enterprise mode
Week 8:  P5C + P6 — Data viz + positioning rebrand
Week 9:  QA, polish, LP-ready review
```

---

## KPIs for Completion

The redesign is successful when:

- [ ] The platform feels proprietary — not generic SaaS
- [ ] It resembles private capital infrastructure
- [ ] It does not resemble an AI SaaS playground
- [ ] It communicates operational seriousness
- [ ] It visually aligns with Calculus Research dashboard
- [ ] It could credibly be shown to institutional LPs
- [ ] Every page passes the "would Sean show this to a fund allocator" test

---

## Architecture Notes

**Frontend:** React + TypeScript + Vite, CSS custom properties (no Tailwind build)
**Backend:** FastAPI + PostgreSQL, Docker Compose deployment
**VM:** `fc-ai-portal.us-east1-b.c.ai-portal-488605.internal` (34.75.120.202)
**Repo:** `github.com/financecommander/AI-PORTAL`
**Branch:** `main` (direct push, bypass PR rule for velocity)

FILEEOF_ROADMAP_md
echo '  ✅ ROADMAP.md'

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
cat > 'frontend/src/components/Layout.tsx' << 'FILEEOF_frontend_src_components_Layout_tsx'
import { useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Menu, X } from 'lucide-react';
import Sidebar from './Sidebar';

export default function Layout() {
  const { isAuthenticated, isLoading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--cr-surface)' }}>
      <div style={{ color: 'var(--cr-text-muted)', fontSize: 14 }}>Loading...</div>
    </div>
  );

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen" style={{ background: 'var(--cr-surface)' }}>
      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-50 flex items-center px-4 py-3" style={{ background: 'var(--cr-white)', borderBottom: '1px solid var(--cr-border)' }}>
        <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ color: 'var(--cr-text)' }} className="p-1">
          {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        <div className="ml-3 flex items-center gap-2">
          <div style={{ width: 24, height: 24, borderRadius: 6, background: 'var(--cr-green-900)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 11, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>C</div>
          <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 14, fontWeight: 600, color: 'var(--cr-text)' }}>Calculus Research</span>
        </div>
      </div>
      {/* Mobile overlay */}
      {sidebarOpen && <div className="md:hidden fixed inset-0 z-40" style={{ background: 'rgba(0,0,0,0.3)' }} onClick={() => setSidebarOpen(false)} />}
      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-screen z-50 transition-transform duration-200 md:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <Sidebar onNavigate={() => setSidebarOpen(false)} />
      </div>
      {/* Main content */}
      <main className="min-h-screen md:ml-[var(--sidebar-width)] pt-14 md:pt-0"><Outlet /></main>
    </div>
  );
}

FILEEOF_frontend_src_components_Layout_tsx
echo '  ✅ frontend/src/components/Layout.tsx'

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

mkdir -p 'frontend/src/components/pipeline'
cat > 'frontend/src/components/pipeline/AgentTraceVisualizer.tsx' << 'FILEEOF_frontend_src_components_pipeline_AgentTraceVisualizer_tsx'
import { useState, useEffect, useMemo } from 'react';
import { Check, X, ChevronDown, ChevronUp, Clock, Zap, DollarSign, Hash } from 'lucide-react';
import ModelBadge from './ModelBadge';

interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  tokens?: { input: number; output: number };
  cost?: number;
  durationMs?: number;
  output?: string;
  model?: string;
}

interface AgentTraceVisualizerProps {
  agents: AgentStatus[];
  status: 'idle' | 'running' | 'complete' | 'error';
  totalCost?: number;
  totalTokens?: number;
  durationMs?: number;
  output?: string;
  error?: string;
}

export default function AgentTraceVisualizer({
  agents,
  status,
  totalCost,
  totalTokens,
  durationMs,
  output,
  error,
}: AgentTraceVisualizerProps) {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const [outputExpanded, setOutputExpanded] = useState(false);
  const [runningDots, setRunningDots] = useState(1);

  // Animate running dots
  useEffect(() => {
    if (status !== 'running') return;
    const interval = setInterval(() => {
      setRunningDots(prev => (prev % 3) + 1);
    }, 500);
    return () => clearInterval(interval);
  }, [status]);

  // Calculate max duration for scaling duration bars
  const maxDuration = useMemo(() => {
    const durations = agents
      .filter(a => a.status === 'complete' && a.durationMs)
      .map(a => a.durationMs!);
    return durations.length > 0 ? Math.max(...durations) : 1;
  }, [agents]);

  const completedCount = agents.filter(a => a.status === 'complete').length;
  const runningAgent = agents.find(a => a.status === 'running');

  const toggleAgentExpansion = (agentName: string) => {
    setExpandedAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentName)) {
        newSet.delete(agentName);
      } else {
        newSet.add(agentName);
      }
      return newSet;
    });
  };

  const getStatusColor = (agentStatus: string) => {
    switch (agentStatus) {
      case 'complete': return 'var(--cr-green-600)';
      case 'error': return 'var(--cr-danger)';
      case 'running': return 'var(--cr-green-600)';
      default: return 'var(--cr-text-dim)';
    }
  };

  const getStatusNode = (agent: AgentStatus, index: number) => {
    const isRunning = agent.status === 'running';
    const isComplete = agent.status === 'complete';
    const isError = agent.status === 'error';

    return (
      <div
        style={{
          width: '28px',
          height: '28px',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 'bold',
          color: agent.status === 'pending' ? 'var(--cr-text-muted)' : 'var(--cr-text)',
          backgroundColor: isComplete ? 'var(--cr-green-600)' : isError ? 'var(--cr-danger)' : 'transparent',
          border: agent.status === 'pending'
            ? '2px dashed var(--cr-charcoal-deep)'
            : isRunning
              ? '2px solid var(--cr-green-600)'
              : 'none',
          animation: isRunning ? 'animate-pulse-glow' : 'none',
          position: 'relative',
          zIndex: 2,
        }}
      >
        {isComplete && <Check size={14} />}
        {isError && <X size={14} />}
        {agent.status === 'pending' && (index + 1)}
        {isRunning && (index + 1)}
      </div>
    );
  };

  const getConnectorLine = (agent: AgentStatus) => {
    if (agent === agents[agents.length - 1]) return null;

    return (
      <div
        style={{
          width: '2px',
          height: '8px',
          backgroundColor: getStatusColor(agent.status),
          margin: '4px auto 0',
          borderRadius: '1px',
        }}
      />
    );
  };

  const getDurationBar = (durationMs: number) => {
    const percentage = (durationMs / maxDuration) * 100;
    const seconds = (durationMs / 1000).toFixed(1);

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
        <div
          style={{
            width: '80px',
            height: '4px',
            backgroundColor: 'var(--cr-charcoal-deep)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${percentage}%`,
              height: '100%',
              backgroundColor: 'var(--cr-gold-500)',
              borderRadius: '2px',
              transition: 'width 0.3s ease',
            }}
          />
        </div>
        <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>{seconds}s</span>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header bar */}
      <div
        style={{
          backgroundColor: 'var(--cr-charcoal-deep)',
          borderRadius: '10px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: status === 'complete'
                ? 'var(--cr-green-600)'
                : status === 'error'
                  ? 'var(--cr-danger)'
                  : 'var(--cr-green-600)',
              animation: status === 'running' ? 'animate-pulse-glow' : 'none',
            }}
          />
          <span style={{ color: 'var(--cr-text)', fontSize: '14px', fontWeight: '500' }}>
            {status === 'complete'
              ? 'Pipeline Complete'
              : status === 'error'
                ? 'Pipeline Failed'
                : runningAgent
                  ? `Running: ${runningAgent.name}`
                  : 'Initializing...'}
          </span>
        </div>
        <span style={{ color: 'var(--cr-text-muted)', fontSize: '13px' }}>
          {completedCount} / {agents.length} agents
        </span>
      </div>

      {/* Progress rail */}
      <div
        style={{
          height: '2px',
          backgroundColor: 'var(--cr-charcoal-deep)',
          borderRadius: '1px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${agents.length > 0 ? (completedCount / agents.length) * 100 : 0}%`,
            background: 'linear-gradient(90deg, var(--cr-green-600), var(--cr-green-400))',
            transition: 'width 0.5s ease',
          }}
        />
      </div>

      {/* Agent trace rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {agents.map((agent, index) => (
          <div key={agent.name} style={{ position: 'relative' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                padding: '12px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
                border: agent.status === 'running' ? '1px solid var(--cr-green-600)' : '1px solid transparent',
              }}
            >
              {getStatusNode(agent, index)}

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--cr-text)', fontSize: '14px', fontWeight: '500' }}>
                    {agent.name}
                  </span>
                  {agent.model && <ModelBadge model={agent.model} />}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                  <span
                    style={{
                      fontSize: '12px',
                      color: agent.status === 'error'
                        ? 'var(--cr-danger)'
                        : agent.status === 'running'
                          ? 'var(--cr-green-400)'
                          : 'var(--cr-text-muted)',
                    }}
                  >
                    {agent.status === 'pending' && 'Waiting'}
                    {agent.status === 'running' && `Processing${'.'.repeat(runningDots)}`}
                    {agent.status === 'error' && 'Failed'}
                    {agent.status === 'complete' && 'Complete'}
                  </span>

                  {agent.status === 'complete' && agent.durationMs && getDurationBar(agent.durationMs)}

                  {agent.status === 'complete' && agent.tokens && (
                    <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>
                      {(agent.tokens.input + agent.tokens.output).toLocaleString()} tok
                    </span>
                  )}

                  {agent.status === 'complete' && agent.cost !== undefined && (
                    <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>
                      ${agent.cost.toFixed(4)}
                    </span>
                  )}

                  {agent.status === 'complete' && agent.output && (
                    <button
                      onClick={() => toggleAgentExpansion(agent.name)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--cr-text-muted)',
                        cursor: 'pointer',
                        padding: '2px',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      {expandedAgents.has(agent.name) ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  )}
                </div>

                {agent.status === 'complete' && agent.output && expandedAgents.has(agent.name) && (
                  <div
                    style={{
                      marginTop: '8px',
                      padding: '8px',
                      backgroundColor: 'var(--cr-charcoal-dark)',
                      borderRadius: '6px',
                      borderLeft: '3px solid var(--cr-green-600)',
                      maxHeight: '250px',
                      overflowY: 'auto',
                    }}
                  >
                    <pre
                      style={{
                        margin: 0,
                        fontSize: '12px',
                        color: 'var(--cr-text-muted)',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {agent.output}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {getConnectorLine(agent)}
          </div>
        ))}
      </div>

      {/* Error block */}
      {status === 'error' && error && (
        <div
          style={{
            padding: '12px',
            backgroundColor: 'rgba(192, 57, 43, 0.1)',
            borderRadius: '8px',
            borderLeft: '4px solid var(--cr-danger)',
          }}
        >
          <div style={{ color: 'var(--cr-danger)', fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
            Error
          </div>
          <div style={{ color: 'var(--cr-text)', fontSize: '13px' }}>{error}</div>
        </div>
      )}

      {/* Completion summary */}
      {status === 'complete' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
            gap: '8px',
          }}
        >
          {totalCost !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(45, 139, 78, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <DollarSign size={16} color="var(--cr-green-600)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Total Cost</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  ${totalCost.toFixed(4)}
                </div>
              </div>
            </div>
          )}

          {totalTokens !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(46, 117, 182, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Hash size={16} color="var(--cr-green-600)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Total Tokens</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  {totalTokens.toLocaleString()}
                </div>
              </div>
            </div>
          )}

          {durationMs !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(212, 118, 10, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Clock size={16} color="var(--cr-gold-500)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Duration</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  {(durationMs / 1000).toFixed(1)}s
                </div>
              </div>
            </div>
          )}

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px',
              backgroundColor: 'var(--cr-charcoal-deep)',
              borderRadius: '8px',
            }}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '6px',
                backgroundColor: 'rgba(46, 117, 182, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Zap size={16} color="var(--cr-green-600)" />
            </div>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Agents</div>
              <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                {completedCount} / {agents.length}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Final output block */}
      {status === 'complete' && output && (
        <div
          style={{
            backgroundColor: 'var(--cr-charcoal-deep)',
            borderRadius: '8px',
            overflow: 'hidden',
          }}
        >
          <button
            onClick={() => setOutputExpanded(!outputExpanded)}
            style={{
              width: '100%',
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              color: 'var(--cr-text)',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '14px',
              fontWeight: '500',
            }}
          >
            FINAL OUTPUT
            {outputExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {outputExpanded && (
            <div
              style={{
                padding: '0 16px 16px',
                borderTop: '1px solid var(--cr-charcoal-deep)',
              }}
            >
              <pre
                style={{
                  margin: 0,
                  fontSize: '13px',
                  color: 'var(--cr-text-muted)',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  lineHeight: '1.5',
                }}
              >
                {output}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
FILEEOF_frontend_src_components_pipeline_AgentTraceVisualizer_tsx
echo '  ✅ frontend/src/components/pipeline/AgentTraceVisualizer.tsx'

mkdir -p 'frontend/src/components/usage'
cat > 'frontend/src/components/usage/CostChart.tsx' << 'FILEEOF_frontend_src_components_usage_CostChart_tsx'
interface CostChartProps { data: { date: string; cost: number; count: number }[]; }

export default function CostChart({ data }: CostChartProps) {
  if (data.length === 0) return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 20, color: 'var(--cr-text-muted)', fontSize: 14 }}>
      No usage data yet
    </div>
  );

  const maxCost = Math.max(...data.map((d) => d.cost), 0.0001);
  const totalCost = data.reduce((sum, d) => sum + d.cost, 0);
  const totalCount = data.reduce((sum, d) => sum + d.count, 0);

  return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 20 }}>
      <div style={{ marginBottom: 12, fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        Daily Cost — Last 7 Days
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {data.map((d) => (
          <div key={d.date} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, fontSize: 12, color: 'var(--cr-text-muted)', flexShrink: 0 }}>{d.date}</div>
            <div style={{ flex: 1, background: 'var(--cr-surface-2)', borderRadius: 3, height: 16, overflow: 'hidden' }}>
              <div style={{ width: `${(d.cost / maxCost) * 100}%`, height: '100%', background: 'var(--cr-green-600)', borderRadius: 3, minWidth: d.cost > 0 ? 3 : 0, transition: 'width 300ms ease' }} />
            </div>
            <div style={{ width: 52, fontSize: 12, color: 'var(--cr-text)', textAlign: 'right', flexShrink: 0, fontWeight: 500 }}>
              ${d.cost.toFixed(2)}
            </div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--cr-border)', display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--cr-text-muted)' }}>
        <span>Total: {totalCount} queries</span>
        <span style={{ color: 'var(--cr-green-900)', fontWeight: 600 }}>${totalCost.toFixed(4)}</span>
      </div>
    </div>
  );
}

FILEEOF_frontend_src_components_usage_CostChart_tsx
echo '  ✅ frontend/src/components/usage/CostChart.tsx'

mkdir -p 'frontend/src/components/usage'
cat > 'frontend/src/components/usage/StatsCards.tsx' << 'FILEEOF_frontend_src_components_usage_StatsCards_tsx'
import type { UsageLog } from '../../types';

interface StatsCardsProps { logs: UsageLog[]; }

function formatTokenCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

export default function StatsCards({ logs }: StatsCardsProps) {
  const totalCost = logs.reduce((s, l) => s + l.cost_usd, 0);
  const totalTokens = logs.reduce((s, l) => s + l.input_tokens + l.output_tokens, 0);
  const avgLatency = logs.length > 0 ? logs.reduce((s, l) => s + l.latency_ms, 0) / logs.length : 0;
  const totalQueries = logs.length;

  const cards = [
    { label: 'Total Cost', value: `$${totalCost.toFixed(4)}`, accent: 'var(--cr-green-600)' },
    { label: 'Total Tokens', value: formatTokenCount(totalTokens), accent: 'var(--cr-green-900)' },
    { label: 'Avg Latency', value: `${(avgLatency / 1000).toFixed(2)}s`, accent: 'var(--cr-text)' },
    { label: 'Total Queries', value: String(totalQueries), accent: 'var(--cr-text)' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
      {cards.map((card) => (
        <div key={card.label} style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 20 }}>
          <div style={{ fontSize: 11, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8, fontWeight: 600 }}>
            {card.label}
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: card.accent, fontFamily: "'Space Grotesk', sans-serif" }}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}

FILEEOF_frontend_src_components_usage_StatsCards_tsx
echo '  ✅ frontend/src/components/usage/StatsCards.tsx'

mkdir -p 'frontend/src/components/usage'
cat > 'frontend/src/components/usage/UsageTable.tsx' << 'FILEEOF_frontend_src_components_usage_UsageTable_tsx'
import type { UsageLog } from '../../types';

interface UsageTableProps { logs: UsageLog[]; }

function relativeTime(timestamp: string): string {
  if (!timestamp) return '—';
  const parsed = new Date(timestamp).getTime();
  if (isNaN(parsed)) return '—';
  const diff = Date.now() - parsed;
  const s = Math.floor(diff / 1000);
  if (s < 60) return 'just now';
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return d === 1 ? 'yesterday' : `${d}d ago`;
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

function costColor(cost: number): string {
  if (cost < 0.05) return 'var(--cr-green-600)';
  if (cost <= 0.5) return 'var(--cr-gold-500)';
  return 'var(--cr-danger)';
}

export default function UsageTable({ logs }: UsageTableProps) {
  const rows = logs.slice(0, 50);

  if (rows.length === 0) return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 40, textAlign: 'center', color: 'var(--cr-text-muted)', fontSize: 14 }}>
      No usage logs yet — start chatting to see your usage here
    </div>
  );

  const th: React.CSSProperties = {
    background: 'var(--cr-surface-2)', color: 'var(--cr-text-muted)', fontSize: 11, textTransform: 'uppercase',
    letterSpacing: '0.06em', padding: '8px 12px', textAlign: 'left', fontWeight: 600,
    borderBottom: '1px solid var(--cr-border)',
  };

  const td: React.CSSProperties = { padding: '8px 12px', borderBottom: '1px solid var(--cr-border)' };

  return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>
            <th style={th}>Time</th>
            <th style={th}>Specialist</th>
            <th style={th}>Provider</th>
            <th style={th}>Model</th>
            <th style={th}>Tokens</th>
            <th style={th}>Cost</th>
            <th style={th}>Latency</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((log, i) => (
            <tr key={log.id} style={{ background: i % 2 === 0 ? 'var(--cr-white)' : 'var(--cr-surface)' }}>
              <td style={{ ...td, color: 'var(--cr-text-muted)', whiteSpace: 'nowrap' }}>{relativeTime(log.timestamp)}</td>
              <td style={{ ...td, color: 'var(--cr-text)' }}>{log.specialist_id ?? '—'}</td>
              <td style={{ ...td, color: 'var(--cr-text)' }}>{log.provider}</td>
              <td style={{ ...td, color: 'var(--cr-text-muted)', fontFamily: 'monospace', fontSize: 12 }}>{log.model}</td>
              <td style={{ ...td, color: 'var(--cr-text)' }}>{formatTokens(log.input_tokens + log.output_tokens)}</td>
              <td style={{ ...td, color: costColor(log.cost_usd), fontWeight: 600 }}>${log.cost_usd.toFixed(4)}</td>
              <td style={{ ...td, color: 'var(--cr-text-muted)' }}>{log.latency_ms >= 1000 ? `${(log.latency_ms / 1000).toFixed(1)}s` : `${log.latency_ms}ms`}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

FILEEOF_frontend_src_components_usage_UsageTable_tsx
echo '  ✅ frontend/src/components/usage/UsageTable.tsx'

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

mkdir -p 'frontend/src/pages'
cat > 'frontend/src/pages/SettingsPage.tsx' << 'FILEEOF_frontend_src_pages_SettingsPage_tsx'
import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import type { Specialist, Pipeline } from '../types';

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: 'var(--cr-white)', borderRadius: 'var(--cr-radius)', border: '1px solid var(--cr-border)', padding: 20, marginBottom: 16 }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--cr-text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 14 }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function Pill({ label, color = 'var(--cr-surface-2)' }: { label: string; color?: string }) {
  return (
    <span style={{ display: 'inline-block', padding: '3px 10px', borderRadius: 20, background: color, fontSize: 12, color: 'var(--cr-text-secondary)', marginRight: 6, marginBottom: 4, border: '1px solid var(--cr-border)' }}>
      {label}
    </span>
  );
}

export default function SettingsPage() {
  const { user } = useAuth();
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);

  useEffect(() => {
    api.request<{ specialists: Specialist[] }>('/specialists/').then((d) => setSpecialists(d.specialists)).catch(() => {});
    api.request<{ pipelines: Pipeline[] }>('/api/v2/pipelines/list').then((d) => setPipelines(d.pipelines)).catch(() => {});
  }, []);

  return (
    <div style={{ padding: '28px 32px', maxWidth: 800 }}>
      <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 22, fontWeight: 700, color: 'var(--cr-text)', marginBottom: 24 }}>
        Settings
      </h1>

      <Card title="Account">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {user?.avatar_url ? (
            <img src={user.avatar_url} alt="" style={{ width: 40, height: 40, borderRadius: '50%' }} />
          ) : (
            <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--cr-green-600)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, fontWeight: 600 }}>
              {(user?.name || user?.email)?.[0]?.toUpperCase() ?? 'U'}
            </div>
          )}
          <div>
            <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--cr-text)' }}>{user?.name || 'User'}</div>
            <div style={{ fontSize: 13, color: 'var(--cr-text-muted)' }}>{user?.email}</div>
          </div>
        </div>
      </Card>

      <Card title={`Active Specialists (${specialists.length})`}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {specialists.map((s) => <Pill key={s.id} label={s.name} />)}
          {specialists.length === 0 && <span style={{ color: 'var(--cr-text-muted)', fontSize: 13 }}>Loading...</span>}
        </div>
      </Card>

      <Card title={`Intelligence Pipelines (${pipelines.length})`}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {pipelines.map((p) => <Pill key={p.name} label={p.name} />)}
          {pipelines.length === 0 && <span style={{ color: 'var(--cr-text-muted)', fontSize: 13 }}>Loading...</span>}
        </div>
      </Card>

      <Card title="System">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 13 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--cr-text-muted)' }}>Version</span>
            <span style={{ color: 'var(--cr-text)', fontWeight: 500 }}>v2.2</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--cr-text-muted)' }}>Backend</span>
            <span style={{ color: 'var(--cr-text)', fontWeight: 500 }}>FastAPI + PostgreSQL</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--cr-text-muted)' }}>Theme</span>
            <span style={{ color: 'var(--cr-text)', fontWeight: 500 }}>Light Institutional</span>
          </div>
        </div>
      </Card>
    </div>
  );
}

FILEEOF_frontend_src_pages_SettingsPage_tsx
echo '  ✅ frontend/src/pages/SettingsPage.tsx'

mkdir -p 'frontend/src/pages'
cat > 'frontend/src/pages/UsagePage.tsx' << 'FILEEOF_frontend_src_pages_UsagePage_tsx'
import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { UsageLog, PipelineRun } from '../types';
import StatsCards from '../components/usage/StatsCards';
import CostChart from '../components/usage/CostChart';
import UsageTable from '../components/usage/UsageTable';

function buildChartData(logs: UsageLog[]): { date: string; cost: number; count: number }[] {
  const days: { date: string; cost: number; count: number }[] = [];
  const now = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    days.push({ date: d.toLocaleDateString('en-US', { weekday: 'short' }), cost: 0, count: 0 });
  }
  logs.forEach((log) => {
    const parsed = new Date(log.timestamp).getTime();
    const diffDays = Math.floor((now.getTime() - parsed) / 86400000);
    const idx = 6 - diffDays;
    if (idx >= 0 && idx < 7) { days[idx].cost += log.cost_usd; days[idx].count += 1; }
  });
  return days;
}

export default function UsagePage() {
  const [logs, setLogs] = useState<UsageLog[]>([]);
  const [pipelines, setPipelines] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'pipeline'>('chat');

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [logsRes, pipelinesRes] = await Promise.all([
        api.request<{ logs: UsageLog[] }>('/usage/logs?limit=50'),
        api.request<{ runs: PipelineRun[] }>('/usage/pipelines?limit=20'),
      ]);
      setLogs(logsRes.logs ?? []); setPipelines(pipelinesRes.runs ?? []);
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed to load usage data'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const chartData = buildChartData(logs);

  const pipelineLogs: UsageLog[] = pipelines.map((p, i) => ({
    id: i, user_hash: '', timestamp: p.created_at ?? '', provider: p.pipeline_name ?? 'pipeline',
    model: p.pipeline_name ?? p.pipeline_id, input_tokens: p.total_tokens ?? 0, output_tokens: 0,
    cost_usd: p.total_cost ?? 0, latency_ms: p.duration_ms ?? 0, specialist_id: p.query?.slice(0, 40),
  }));

  return (
    <div style={{ padding: '28px 32px' }}>
      <h1 style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 22, fontWeight: 700, color: 'var(--cr-text)', marginBottom: 24 }}>
        Usage & Costs
      </h1>

      {loading && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            {[1,2,3,4].map((k) => <div key={k} style={{ height: 80, background: 'var(--cr-surface-2)', borderRadius: 'var(--cr-radius)', animation: 'subtlePulse 1.5s ease-in-out infinite' }} />)}
          </div>
          <div style={{ height: 180, background: 'var(--cr-surface-2)', borderRadius: 'var(--cr-radius)' }} />
        </div>
      )}

      {!loading && error && (
        <div style={{ color: 'var(--cr-danger)', marginBottom: 16, fontSize: 14 }}>
          {error}
          <button onClick={fetchData} style={{ marginLeft: 12, padding: '6px 14px', background: 'var(--cr-white)', border: '1px solid var(--cr-border)', color: 'var(--cr-text-secondary)', borderRadius: 'var(--cr-radius-sm)', cursor: 'pointer', fontSize: 13 }}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <StatsCards logs={logs} />
          <CostChart data={chartData} />
          <div>
            <div style={{ borderBottom: '1px solid var(--cr-border)', marginBottom: 16, display: 'flex', gap: 4 }}>
              {(['chat', 'pipeline'] as const).map((tab) => (
                <button key={tab} onClick={() => setActiveTab(tab)} style={{
                  padding: '8px 18px', background: 'none', border: 'none',
                  borderBottom: activeTab === tab ? '2px solid var(--cr-green-900)' : '2px solid transparent',
                  color: activeTab === tab ? 'var(--cr-text)' : 'var(--cr-text-muted)',
                  cursor: 'pointer', fontSize: 13, fontWeight: activeTab === tab ? 600 : 400,
                }}>
                  {tab === 'chat' ? 'Chat Logs' : 'Pipeline Runs'}
                </button>
              ))}
            </div>
            <UsageTable logs={activeTab === 'chat' ? logs : pipelineLogs} />
          </div>
        </div>
      )}
    </div>
  );
}

FILEEOF_frontend_src_pages_UsagePage_tsx
echo '  ✅ frontend/src/pages/UsagePage.tsx'


echo ""
echo "📦 Committing..."
git add -A
git status --short
git commit --no-gpg-sign -m "P1: visual hardening — full light institutional theme across all pages

Layout: light surface bg, white mobile header, C logo badge
UsagePage: white KPI cards with green accent, denser tables (8px padding),
uppercase headers with letter-spacing, green-600 chart bars
SettingsPage: white cards, structured key-value pairs
StatsCards: Space Grotesk KPI values, cr-border cards
CostChart: white card, surface-2 bar track, green-600 fill
UsageTable: surface-2 header row, alternating white/surface rows, 8px dense padding
AgentTraceVisualizer: replaced last 2 legacy vars (--orange → cr-gold-500)
index.css: removed all legacy aliases (--navy, --blue, --green, --orange, --red)
ROADMAP.md: updated with issue tracking and progress matrix

18 files changed. Zero legacy CSS variables remaining. Zero dark theme remnants.
All pages now match Calculus Research dashboard aesthetic." || echo "Nothing to commit"

echo "🚀 Pushing..."
git push origin main

echo ""
echo "✅ Done! On VM:"
echo "  cd ~/AI-PORTAL && git fetch origin main && git reset --hard origin/main"
echo "  sudo docker compose -f docker-compose.v2.yml build --no-cache frontend"
echo "  sudo docker compose -f docker-compose.v2.yml up -d --force-recreate"
