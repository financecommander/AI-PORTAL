# Legal Quick Consult

**Type:** Single-Specialist Chat Agent
**ID:** `legal-quick`
**Portal Location:** `/chat` → Specialist Sidebar → Legal Quick Consult

---

## Overview

Legal Quick Consult provides fast, directional legal guidance on business matters. It is designed for rapid answers to legal questions that don't require the full 6-agent Lex Intelligence pipeline — think "quick take" vs "full legal memo." It explicitly disclaims being a substitute for qualified legal counsel and always recommends professional review for actionable decisions.

## Technical Configuration

| Parameter | Value |
|-----------|-------|
| **Provider** | xAI (Grok) |
| **Model** | `grok-beta` (Grok 4.20 when API available) |
| **Temperature** | 0.1 (extremely conservative — minimal creative interpretation) |
| **Max Tokens** | 4,096 |
| **Version** | 1 |

## Why Grok

Grok was selected for legal quick consult for two reasons. First, its real-time access to X platform data provides current awareness of regulatory developments, enforcement actions, and industry sentiment that other models lack. Second, with Grok 4.20's internal 4-agent architecture, even a single API call benefits from multi-agent peer review — reducing hallucination risk on legal topics where fabricated case citations are particularly dangerous. The extremely low temperature (0.1) further constrains output to conservative, factual responses appropriate for legal guidance.

**Upgrade path:** When the Grok 4.20 API becomes available (expected March 2026), this specialist will be updated from `grok-beta` to the new model string. Heavy mode's 16-agent internal architecture will make single-query legal guidance significantly more reliable.

## Capabilities

- **Business formation** — Entity selection, operating agreements, corporate governance
- **Contract questions** — Clause interpretation, enforceability, common terms
- **Regulatory overview** — Financial services compliance, state licensing, reporting requirements
- **Employment law** — Hiring, termination, non-competes, independent contractors
- **Intellectual property** — Trademark basics, trade secrets, patent eligibility
- **Liability assessment** — Risk exposure, limitation of liability, indemnification

## Accuracy Protocol

This specialist operates under the strictest accuracy constraints:

- Temperature 0.1 — the lowest of all specialists
- Never fabricates case names, statutes, or legal citations
- Prefixes unverified claims with `[UNVERIFIED]`
- Always recommends professional legal review for actionable decisions
- Explicitly states it is NOT a substitute for qualified legal counsel
- Refuses to provide specific legal advice on matters with significant liability exposure

## When to Use This vs Lex Intelligence

| Scenario | Use Legal Quick Consult | Use Lex Intelligence |
|----------|------------------------|---------------------|
| "Can an LLC own precious metals?" | ✅ Quick answer | Overkill |
| "What's the SOX compliance timeline?" | ✅ Quick reference | Overkill |
| "Is our ERC-1400 structure legal?" | ❌ Too complex | ✅ Full pipeline |
| "Analyze Article I Section 10 implications" | ❌ Too deep | ✅ Full pipeline |
| "Draft a legal opinion on tender law" | ❌ Wrong tool | ✅ Full pipeline |

## Example Prompts

```
"What are the basic requirements for a money services business license 
in Connecticut?"

"Can a non-custodial settlement coordinator hold client funds in transit, 
or does that trigger custodial regulations?"

"What's the difference between a Series LLC and a traditional LLC for 
holding multiple business ventures?"

"Do I need a separate broker-dealer registration if Constitutional Tender 
only facilitates precious metals transactions?"
```

## API Endpoint

```bash
POST /chat/send
Authorization: Bearer <jwt>

{
  "specialist_id": "legal-quick",
  "message": "your question here",
  "conversation_history": []
}
```

## Cost Estimate

Typical interaction (800 input + 1,500 output tokens): **~$0.027**
Extended Q&A session (8 exchanges): **~$0.20 - $0.35**

---

*Part of the FinanceCommander AI Intelligence Portal v2.0*
