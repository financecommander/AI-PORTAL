# Research Assistant

**Type:** Single-Specialist Chat Agent
**ID:** `research-assistant`
**Portal Location:** `/chat` → Specialist Sidebar → Research Assistant

---

## Overview

The Research Assistant is a general-purpose synthesis engine designed to consume complex, multi-source information and produce clear, structured summaries. It serves as the team's first-pass research tool for topics spanning finance, technology, regulation, and business strategy.

## Technical Configuration

| Parameter | Value |
|-----------|-------|
| **Provider** | OpenAI |
| **Model** | `gpt-4o` |
| **Temperature** | 0.5 (balanced — factual with moderate synthesis flexibility) |
| **Max Tokens** | 4,096 |
| **Version** | 1 |

## Why GPT-4o

GPT-4o was selected for research synthesis because of its strong information organization capabilities, broad training corpus, and fast inference speed. At $2.50 per 1M input tokens, it provides cost-effective throughput for high-volume research tasks. The moderate temperature (0.5) allows enough flexibility for creative synthesis while keeping outputs grounded in source material.

## Capabilities

- **Multi-source synthesis** — Combines information from disparate sources into coherent narratives
- **Structured summarization** — Executive summaries, bullet-point extractions, comparison matrices
- **Competitive analysis** — Market landscape mapping, competitor profiling, SWOT analysis
- **Technology research** — API evaluations, platform comparisons, architecture reviews
- **Regulatory research** — Policy summaries, compliance requirement mapping
- **Due diligence support** — Company profiles, risk factor identification, market sizing

## Accuracy Protocol

- Never fabricates citations or source references
- Prefixes unverified claims with `[UNVERIFIED]`
- Distinguishes between established facts and interpretive analysis
- Identifies gaps in available information rather than filling them speculatively

## Example Prompts

```
"Summarize the current regulatory landscape for precious metals trading 
platforms in the United States, focusing on state-level requirements"

"Compare CrewAI, AutoGen, and LangGraph for multi-agent pipeline 
orchestration — focus on production readiness and token efficiency"

"Research the wholesale food distribution market in southeastern Massachusetts, 
including demographics for Portuguese, Brazilian, and Hispanic communities"

"What are the key differences between Nymbus and Finxact core banking platforms 
for community bank partnerships?"
```

## API Endpoint

```bash
POST /chat/send
Authorization: Bearer <jwt>

{
  "specialist_id": "research-assistant",
  "message": "your question here",
  "conversation_history": []
}
```

## Cost Estimate

Typical interaction (1,500 input + 3,000 output tokens): **~$0.034**
Deep research session (15 exchanges): **~$0.40 - $0.70**

---

*Part of the FinanceCommander AI Intelligence Portal v2.0*
