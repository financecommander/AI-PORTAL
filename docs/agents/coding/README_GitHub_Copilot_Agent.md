# GitHub Copilot Agent — PR Generator

**Type:** Coding Agent (Poly-Agent Orchestration)
**Role:** Greenfield Code Generator, Branch Creator, PR Author
**Access:** GitHub Copilot (included with GitHub subscription), triggered via Copilot Agent Mode

---

## Overview

GitHub Copilot Agent is the primary code generation workhorse. It takes detailed directives from Claude Opus and translates them into actual repository code — creating branches, writing files, running basic validation, and opening pull requests. It excels at generating large volumes of new code from a well-structured specification, but struggles with complex multi-file refactoring or tasks requiring terminal interaction.

## Capabilities

| Capability | Description |
|-----------|-------------|
| **File creation** | Generates new files from scratch with full implementations |
| **Branch management** | Creates feature branches automatically |
| **PR creation** | Opens draft PRs with descriptive titles and summaries |
| **Multi-file generation** | Can create 20-30+ files in a single session |
| **Code structure** | Follows project conventions when given clear examples |
| **Commit authoring** | Creates logical commit messages (though not always matching spec) |

## How to Trigger

1. Navigate to the repository on GitHub
2. Open the **Copilot Agent** panel (or use the Agents tab)
3. Paste the directive document (tagged 🤖 AGENT)
4. Copilot creates a branch, writes code, opens a PR

## How It Fits in the Pipeline

```
Claude Opus → Generates 🤖 AGENT directive
    │
    ▼
GitHub Copilot Agent → Creates branch → Writes code → Opens PR
    │
    ▼
Sean → Reviews PR → Merges into develop
    │
    ▼
Claude Opus → Reviews merged code → Generates next directive
```

## Configuration

| Setting | Value |
|---------|-------|
| **Model** | Claude Sonnet 4.5 (GitHub's default for Agent mode) |
| **Repository** | `financecommander/AI-PORTAL` |
| **Base branch** | `develop` (must be set manually — defaults to `main`) |
| **PR type** | Draft (requires "Ready for review" before merging) |

## What It's Built So Far

- Complete backend scaffold (Phase 1A: project structure, config, errors)
- JWT authentication system
- Provider abstraction layer attempt (overlapping with gap fill)
- Pipeline engine with CrewAI wrapper (438 lines)
- Lex Intelligence Ultimate (308 lines, 6 agents)
- WebSocket streaming manager
- Token estimator with pricing
- Database models and ORM setup
- Test suite (76+ tests)

## Strengths

- **Volume** — Can generate 2,000+ lines of code in a single session
- **Consistency** — Follows patterns well when given explicit examples
- **Speed** — Creates PRs within minutes of receiving a directive
- **Multi-file** — Handles 30+ file creation in one pass
- **Self-documenting** — Generates README files and code comments

## Limitations

- **No terminal access** — Cannot run `pip install`, `pytest`, or verify code works
- **No internet** — Firewall blocks external URLs (can't install packages or hit APIs)
- **Branch targeting** — Defaults to `main`, must manually change PR base to `develop`
- **Overlapping PRs** — Creates independent branches that conflict when multiple directives run in parallel
- **Context limits** — Long directives (600+ lines) may cause truncation or drift
- **Wrong repo risk** — Can accidentally run against the wrong repository if not carefully scoped
- **No conflict resolution** — Cannot resolve merge conflicts (requires Codespace or CLI)

## Known Issues (Lessons Learned)

1. **Overlapping branches** — When given Days 1-3 directives simultaneously, Copilot created 11 independent PRs that all modified the same files. Solution: submit one directive at a time, merge before submitting the next.

2. **Wrong repo execution** — PR #21 was generated against AI-PORTAL but contained lead-ranking-engine test code. Solution: verify repo name in directive header.

3. **Draft PR state** — All PRs open as drafts. Must click "Ready for review" before merging on mobile.

4. **Base branch** — Always check that the PR targets `develop`, not `main`.

## Best Practices

- **One directive per session** — Don't submit multiple directives simultaneously
- **Keep directives under 500 lines** — Split longer specs into parts
- **Include DO NOT sections** — Explicitly list what the agent should not touch
- **Specify exact file paths** — `backend/providers/factory.py`, not "create a factory"
- **Include commit messages** — Agent follows them ~70% of the time
- **Verify base branch** — Always check PR targets `develop`
- **Review before merge** — Agent code requires human review for security-critical paths

## When to Use vs. Codespace Chat

| Scenario | Use Agent | Use Codespace |
|----------|-----------|---------------|
| New module from scratch | ✅ | |
| 10+ new files | ✅ | |
| Fixing existing code | | ✅ |
| Resolving merge conflicts | | ✅ |
| Running tests | | ✅ |
| Installing dependencies | | ✅ |
| Multi-file refactoring | | ✅ |
| Docker/deployment setup | | ✅ |

## Cost

Included with GitHub Copilot subscription ($19/month individual, $19/seat business).

---

*Part of the FinanceCommander Poly-Agent Development Orchestration*
