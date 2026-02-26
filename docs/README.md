# FinanceCommander AI Portal — Documentation Index

## Architecture & Operations
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture overview
- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment guide
- [SECURITY.md](SECURITY.md) — Security policies
- [SECURITY_FIXES.md](SECURITY_FIXES.md) — Security fix log
- [ADMIN.md](ADMIN.md) — Admin operations
- [TECH_DEBT.md](TECH_DEBT.md) — Known technical debt

## Planning
- [LEX v2.2 Planning Spec](planning/LEX_v2.2_PLANNING_SPEC.md) — Multi-jurisdictional expansion, governance agents, go-to-market (Rev 3.0)
- [Dev Team Summary](planning/AI_Portal_Dev_Team_Summary.md) — Current develop branch capabilities (accurate, not aspirational)

## Agent Documentation

### Chat Specialists (4 single-agent endpoints)
- [Financial Analyst](agents/specialists/README_Financial_Analyst.md) — Claude Sonnet 4.5, data-driven financial analysis
- [Research Assistant](agents/specialists/README_Research_Assistant.md) — GPT-4o, multi-source synthesis
- [Code Reviewer](agents/specialists/README_Code_Reviewer.md) — Claude Opus 4, security-focused review
- [Legal Quick Consult](agents/specialists/README_Legal_Quick_Consult.md) — Grok, fast legal guidance

### Lex Intelligence Pipeline (6-agent legal research)
- [Lex Intelligence Ultimate](agents/pipeline/README_Lex_Intelligence_Ultimate.md) — Full pipeline: 6 agents, 4 LLMs, IRAC output

### Coding Agents (poly-agent dev workflow)
- [Claude Opus — Architecture & Directives](agents/coding/README_Claude_Opus.md)
- [GitHub Copilot Agent — PR Generation](agents/coding/README_GitHub_Copilot_Agent.md)
- [Codespace Copilot Chat — Terminal & Debug](agents/coding/README_Codespace_Copilot_Chat.md)
- [Grok — Boilerplate & Infrastructure](agents/coding/README_Grok_Infrastructure.md)

## Directives (Copilot Agent execution instructions)
- [Phase 3A: React Scaffold + Auth](directives/Agent_Phase3A_React_Scaffold_Auth.md) — Vite + React 19 + TypeScript + Tailwind
