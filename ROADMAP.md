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

