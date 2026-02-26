# Claude Opus — Architecture & Directives Agent

**Type:** Coding Agent (Poly-Agent Orchestration)
**Role:** Lead Architect, Directive Generator, Code Reviewer, Security Auditor
**Access:** claude.ai (Opus 4.6) with computer tools enabled

---

## Overview

Claude Opus serves as the lead architect and technical director of the FinanceCommander development pipeline. It does not write code directly into the repository — instead, it generates precise, executable directives that other agents (GitHub Copilot Agent, Codespace Chat) implement. Think of it as the principal engineer who designs the system, writes the spec, reviews the output, and signs off on production readiness.

## Capabilities

| Capability | Description |
|-----------|-------------|
| **Architecture design** | System design, API surface mapping, database schema, component hierarchy |
| **Directive generation** | Detailed, step-by-step implementation specs with exact file paths, code, and commit messages |
| **Repository analysis** | Clones repos, reads code, maps dependencies, identifies gaps |
| **Code review** | Reviews PR output from other agents, identifies security/correctness issues |
| **Document generation** | SOWs, roadmaps, team summaries, README files (Word, PDF, Markdown) |
| **Web research** | Searches for API docs, pricing, model availability, competitor analysis |
| **File creation** | Generates files directly (documents, configs, scripts) |
| **Gap analysis** | Compares spec vs. actual codebase, identifies missing modules |

## Tools Available

- **Terminal/Bash** — Clone repos, run scripts, inspect file trees, execute commands
- **File creation** — Generate .md, .docx, .pdf, .py, .ts, .json files
- **Web search** — Research APIs, documentation, pricing, current events
- **Web fetch** — Read full web pages for deep research
- **View/Edit** — Read and modify files in workspace

## How It Fits in the Pipeline

```
Sean (CEO) → Describes what he wants
    │
    ▼
Claude Opus → Designs architecture, generates directive document
    │
    ├──► 🤖 AGENT directive → GitHub Copilot Agent (new code)
    ├──► 💻 CODESPACE directive → Codespace Chat (fixes, testing)
    │
    ▼
Claude Opus → Reviews output, identifies issues, generates next directive
```

## Directive Format

Every directive Claude Opus generates follows this structure:

1. **Mode tag** — 🤖 AGENT or 💻 CODESPACE
2. **Context** — What exists, what's being built, which files to touch
3. **Step-by-step implementation** — Exact file paths, complete code blocks, validation commands
4. **Commit messages** — Pre-written conventional commit format
5. **Verification** — Commands to run after implementation
6. **DO NOT list** — Explicit guardrails on what the implementing agent should NOT do

## What It's Built So Far

- Complete v2.0 backend architecture (FastAPI + 4 providers + pipeline engine)
- 9 execution directives across 3 days of backend development
- Gap fill directive (14 new files for providers, specialists, chat, auth)
- Token estimator directive with cost calculation
- SOW v2.0 (16 sections, pricing, acceptance criteria)
- Product roadmap (v2.0 through v2.1)
- Phase 3A React frontend directive
- All agent README documentation

## Strengths

- **Deepest reasoning** — Opus 4.6 is the most capable model available for architectural decisions
- **Full repo access** — Can clone, read, and analyze the entire codebase
- **Cross-cutting awareness** — Maintains context across backend, frontend, infrastructure, and business requirements
- **Document generation** — Professional-grade output (Word docs, PDFs) with formatting
- **Security focus** — Reviews for auth bypasses, injection, secret exposure

## Limitations

- **Cannot push to GitHub directly** — Generates directives that other agents execute
- **No live server** — Cannot run `uvicorn` or `npm run dev` to test interactively
- **Session-bounded** — Context resets between conversations (uses transcripts for continuity)
- **Token-limited** — Very long conversations require compaction

## Cost

Anthropic Pro subscription. Per-token costs are embedded in the subscription — no separate API billing for directive generation.

---

*Part of the FinanceCommander Poly-Agent Development Orchestration*
