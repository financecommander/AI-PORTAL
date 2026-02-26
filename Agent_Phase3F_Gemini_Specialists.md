# Phase 3F — Gemini Specialists & Provider Fixes

## Context

You are working on the `financecommander/AI-PORTAL` repo, branch: `develop`.

This is a full-stack AI Intelligence Portal (v2.0.0) with:
- **Backend**: FastAPI (Python 3.12) at `backend/`
- **Frontend**: React 19 + TypeScript at `frontend/`
- **Active providers**: Google (Gemini), xAI (Grok) — both have valid API keys
- **Inactive providers**: OpenAI ($0 credits), Anthropic (no key yet)

## CRITICAL CONSTRAINTS

- **Branch**: Create `feature/phase-3f-gemini-specialists` from `develop`
- Commit message: `feat: Phase 3F — add Gemini specialists, switch Research Assistant to Gemini`
- Open PR to `develop` when complete

---

## TASK 1: Update `backend/config/specialists.json`

Replace the entire contents with this JSON. This switches Research Assistant from OpenAI to Gemini, keeps Legal Quick Consult on Grok, moves Financial Analyst to Gemini 2.5 Pro, and adds a new Gemini-powered Data Analyst:

```json
{
  "specialists": [
    {
      "id": "financial-analyst",
      "name": "Financial Analyst",
      "description": "Expert financial analysis and modeling powered by Gemini",
      "provider": "google",
      "model": "gemini-2.5-flash",
      "temperature": 0.2,
      "max_tokens": 8192,
      "system_prompt": "You are an employee of FinanceCommander. You are an expert financial analyst with deep knowledge in market analysis, financial modeling, valuation, and investment strategy. Provide detailed, data-driven analysis with clear reasoning. When citing figures, note the source and date. ACCURACY: If not confident, state your confidence level. Never fabricate citations or data. Prefix unverified claims with [UNVERIFIED].",
      "version": 2
    },
    {
      "id": "research-assistant",
      "name": "Research Assistant",
      "description": "Deep research synthesis powered by Gemini 2.5 Pro",
      "provider": "google",
      "model": "gemini-2.5-pro",
      "temperature": 0.4,
      "max_tokens": 8192,
      "system_prompt": "You are an employee of FinanceCommander. You are a meticulous research assistant specializing in financial, legal, and regulatory research. Synthesize complex information into clear, structured analysis. Cross-reference multiple sources when possible. ACCURACY: Never fabricate citations. Clearly distinguish between established facts, consensus views, and speculative analysis. Prefix unverified claims with [UNVERIFIED].",
      "version": 2
    },
    {
      "id": "code-reviewer",
      "name": "Code Reviewer",
      "description": "Expert code review and architecture guidance",
      "provider": "google",
      "model": "gemini-2.5-pro",
      "temperature": 0.2,
      "max_tokens": 8192,
      "system_prompt": "You are an employee of FinanceCommander. You are a senior software architect specializing in Python, TypeScript, and financial systems. Review code for correctness, security vulnerabilities, performance bottlenecks, and maintainability. Provide specific, actionable feedback with code examples. Flag any potential compliance or data privacy issues.",
      "version": 2
    },
    {
      "id": "legal-quick",
      "name": "Legal Quick Consult",
      "description": "Fast legal questions (use Lex Intelligence for deep research)",
      "provider": "grok",
      "model": "grok-4-1-fast-non-reasoning",
      "temperature": 0.1,
      "max_tokens": 4096,
      "system_prompt": "You are an employee of FinanceCommander. You provide quick legal guidance on business matters. You are NOT a substitute for qualified legal counsel. Always recommend professional legal review for actionable decisions. Never fabricate case names, statutes, or regulatory citations. Prefix unverified claims with [UNVERIFIED].",
      "version": 2
    },
    {
      "id": "data-analyst",
      "name": "Data Analyst",
      "description": "Quantitative analysis and data interpretation powered by Gemini",
      "provider": "google",
      "model": "gemini-2.5-flash",
      "temperature": 0.3,
      "max_tokens": 8192,
      "system_prompt": "You are an employee of FinanceCommander. You are an expert data analyst specializing in financial data, statistical analysis, and data visualization recommendations. Help interpret datasets, identify trends, calculate key metrics, and suggest analytical approaches. Provide formulas, SQL queries, or Python code snippets when helpful. ACCURACY: Always show your calculations. Note assumptions clearly.",
      "version": 1
    },
    {
      "id": "compliance-scanner",
      "name": "Compliance Scanner",
      "description": "Regulatory compliance checks across financial regulations",
      "provider": "google",
      "model": "gemini-2.5-flash",
      "temperature": 0.1,
      "max_tokens": 8192,
      "system_prompt": "You are an employee of FinanceCommander. You are a regulatory compliance specialist with expertise in SEC regulations, FINRA rules, CFPB requirements, state lending laws, money transmitter licenses, and financial technology compliance. Analyze business activities, documents, and processes for regulatory compliance issues. Flag potential violations with specific regulatory citations. Always note that this is guidance only and not legal advice. Prefix unverified claims with [UNVERIFIED].",
      "version": 1
    }
  ]
}
```

## TASK 2: Update `config/specialists.json` (root config)

Update this file to match the same specialist list as Task 1. This file is used by the legacy v1 config loader. Keep the same JSON structure as Task 1.

## TASK 3: Update `backend/providers/google_provider.py`

Review the existing Google provider. Ensure it:

1. Supports streaming via `stream_message()` method (check if `langchain_google_genai` or direct Google GenAI SDK is used)
2. Has proper error handling similar to the OpenAI provider (auth errors, rate limits, timeouts)
3. Uses the `GOOGLE_API_KEY` environment variable

If the Google provider does NOT support streaming, add streaming support following the same pattern as `openai_provider.py`. The Google GenAI SDK (`google-generativeai`) supports streaming via:

```python
# Using google.generativeai
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)
response = model.generate_content(contents, stream=True)
for chunk in response:
    yield chunk.text
```

Or if using `langchain_google_genai`:
```python
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
# streaming
async for chunk in llm.astream(messages):
    yield chunk.content
```

Ensure the provider class follows the `BaseProvider` interface with both `send_message()` and `stream_message()` methods returning `ProviderResponse` and `StreamChunk` respectively.

## TASK 4: Update `backend/utils/token_estimator.py`

Add Gemini pricing to the cost calculation. Current Gemini API pricing:

| Model | Input (per 1M) | Output (per 1M) |
|-------|----------------|------------------|
| gemini-2.5-pro | $1.25 | $10.00 |
| gemini-2.5-flash | $0.15 | $0.60 |
| gemini-2.5-flash-lite | $0.02 | $0.10 |
| gemini-2.0-flash | $0.10 | $0.40 |

Add these to whatever pricing lookup exists in the token estimator.

## TASK 5: Update frontend specialist display

In `frontend/src/pages/ChatPage.tsx` or wherever the specialist list renders, ensure the display shows the correct provider/model for each specialist. The frontend reads from the `/specialists/` API endpoint, so this should work automatically if the backend config is correct.

No frontend code changes should be needed — just verify the specialist list endpoint returns the updated data.

## TASK 6: Update `docker-compose.v2.yml`

Ensure the `GOOGLE_API_KEY` environment variable is passed to the backend container. Check that the environment section includes:

```yaml
environment:
  - GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
```

## Verification Checklist

Before opening the PR, verify:

1. `backend/config/specialists.json` has 6 specialists (3 Gemini, 1 Grok, 1 Gemini data analyst, 1 Gemini compliance scanner)
2. `backend/providers/google_provider.py` has both `send_message()` and `stream_message()` 
3. `backend/utils/token_estimator.py` includes Gemini model pricing
4. The backend starts without errors: `cd backend && python -c "from backend.main import app; print('OK')"`
5. No existing tests break

## Commit & PR

```bash
git add -A
git commit -m "feat: Phase 3F — add Gemini specialists, switch Research Assistant to Gemini"
```

Open PR to `develop` with title: **Phase 3F: Gemini Specialists & Provider Migration**

PR description:
```
## What
- Migrated Financial Analyst, Research Assistant, and Code Reviewer from OpenAI/Anthropic to Gemini
- Added new Data Analyst specialist (Gemini 2.5 Flash)
- Added new Compliance Scanner specialist (Gemini 2.5 Flash)
- Ensured Google provider supports streaming
- Added Gemini pricing to token estimator
- Legal Quick Consult remains on Grok (xAI)

## Why
OpenAI API has $0 credits. Anthropic API key not yet configured. 
Gemini API is active with valid key — migrate all possible specialists to working providers.
Grok remains for Legal Quick Consult (fast, cheap, already working).

## Result
6 specialists total:
| Specialist | Provider | Model |
|-----------|----------|-------|
| Financial Analyst | Google | gemini-2.5-flash |
| Research Assistant | Google | gemini-2.5-pro |
| Code Reviewer | Google | gemini-2.5-pro |
| Legal Quick Consult | xAI | grok-4-1-fast-non-reasoning |
| Data Analyst | Google | gemini-2.5-flash |
| Compliance Scanner | Google | gemini-2.5-flash |

## Testing
- Backend starts without errors
- Existing tests pass
- Manual test: send chat to each specialist
```
