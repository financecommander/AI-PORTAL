# Financial Analyst

**Type:** Single-Specialist Chat Agent
**ID:** `financial-analyst`
**Portal Location:** `/chat` → Specialist Sidebar → Financial Analyst

---

## Overview

The Financial Analyst is a precision-tuned AI specialist for data-driven financial analysis, modeling, and decision support. It operates as a virtual employee of FinanceCommander, providing institutional-grade financial reasoning with built-in accuracy safeguards.

## Technical Configuration

| Parameter | Value |
|-----------|-------|
| **Provider** | Anthropic |
| **Model** | `claude-sonnet-4-5-20250929` (Claude Sonnet 4.5) |
| **Temperature** | 0.2 (highly deterministic — minimizes creative variance) |
| **Max Tokens** | 4,096 |
| **Version** | 1 |

## Why Claude Sonnet 4.5

Sonnet was selected over Opus for this role because financial analysis requires a balance of speed and accuracy. Sonnet provides strong analytical reasoning at 5x lower cost than Opus ($3.00 vs $15.00 per 1M input tokens), with sub-second response times critical for interactive financial Q&A. The low temperature (0.2) further constrains output to factual, conservative analysis — appropriate for financial contexts where creative interpretation introduces risk.

## Capabilities

- **Financial statement analysis** — Income statements, balance sheets, cash flow decomposition
- **Ratio analysis** — Liquidity, profitability, leverage, efficiency metrics
- **Valuation modeling** — DCF, comparables, precedent transactions
- **Market analysis** — Sector trends, competitive positioning, risk factors
- **Regulatory context** — SEC filings, compliance frameworks (SOX, Dodd-Frank)
- **Portfolio analysis** — Risk-return profiles, correlation analysis, allocation strategy

## Accuracy Protocol

The Financial Analyst operates under FinanceCommander's hallucination mitigation framework:

- States confidence level when not fully certain
- Never fabricates citations, data points, or financial figures
- Prefixes unverified claims with `[UNVERIFIED]`
- Distinguishes between historical data and forward-looking projections
- Caveats all analysis with "not financial advice" when appropriate

## Example Prompts

```
"Analyze the debt-to-equity implications of a $20M senior secured note issuance 
for a 20MW biomass facility"

"Break down the working capital cycle for a wholesale food manufacturing operation 
with 30-day payables and 15-day receivables"

"Compare the risk profiles of ERC-1400 tokenized debt vs traditional municipal bonds"

"What are the key financial metrics I should track for a precious metals 
trading platform in the first 6 months?"
```

## API Endpoint

```bash
POST /chat/send
Authorization: Bearer <jwt>

{
  "specialist_id": "financial-analyst",
  "message": "your question here",
  "conversation_history": []
}
```

## Cost Estimate

Typical interaction (1,000 input + 2,000 output tokens): **~$0.033**
Extended analysis session (10 exchanges): **~$0.30 - $0.50**

---

*Part of the FinanceCommander AI Intelligence Portal v2.0*
