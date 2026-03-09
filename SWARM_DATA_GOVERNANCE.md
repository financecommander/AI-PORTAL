# Swarm Data Governance — AI-PORTAL

**Calculus Ecosystem • Governance Rule 4 Compliance**

## Rule

> **super-duper-spork retains ALL swarm management data.**
>
> External repos that generate, test, or benchmark swarm algorithms
> must push assessment results back to `financecommander/super-duper-spork`.

## This Repo's Obligations

AI-PORTAL owns model evaluation (Governance Rule 3). When evaluation runs
involve swarm routing decisions, algorithm performance, or agent selection
metrics, those results must be reported upstream.

| Obligation | Target | Format |
|-----------|--------|--------|
| Push model evaluation scores involving swarm routing | `super-duper-spork/swarm/assessments/` | `ai-portal_{description}_{YYYY-MM-DD}.md` |
| Report swarm agent performance in eval benchmarks | `super-duper-spork/swarm/assessments/` | Assessment markdown |

## Canonical Source of Truth

The single source of truth for all swarm state is:

    financecommander/super-duper-spork

This repo runs model evaluations. super-duper-spork retains all swarm
management data, assessment results, and cross-repo totals.

---
*Governance Rule 4 — established 2026-03-09*
