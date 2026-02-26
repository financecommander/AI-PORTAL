# Code Reviewer

**Type:** Single-Specialist Chat Agent
**ID:** `code-reviewer`
**Portal Location:** `/chat` → Specialist Sidebar → Code Reviewer

---

## Overview

The Code Reviewer is a senior software architect agent that evaluates code for correctness, security, performance, and maintainability. It provides the same level of scrutiny as a principal engineer code review, optimized for the FinanceCommander technology stack (Python/FastAPI, React/TypeScript, PostgreSQL, Docker).

## Technical Configuration

| Parameter | Value |
|-----------|-------|
| **Provider** | Anthropic |
| **Model** | `claude-opus-4-20250514` (Claude Opus 4) |
| **Temperature** | 0.3 (low — precision-focused with minimal creative variance) |
| **Max Tokens** | 4,096 |
| **Version** | 1 |

## Why Claude Opus 4

Opus was deliberately selected as the most powerful available model for code review. Security-critical code, architectural decisions, and complex system interactions require the deepest reasoning capabilities. The higher per-token cost ($15.00 per 1M input) is justified because code review errors have outsized downstream cost — a missed security vulnerability or architectural flaw in financial infrastructure is orders of magnitude more expensive than the review itself. Temperature 0.3 keeps output precise while allowing enough flexibility to suggest creative architectural alternatives.

## Capabilities

- **Security review** — SQL injection, XSS, authentication bypasses, secret exposure, input validation
- **Architecture evaluation** — Design patterns, separation of concerns, coupling analysis, scalability
- **Performance analysis** — N+1 queries, async bottlenecks, memory leaks, connection pooling
- **Type safety** — Python type hints, TypeScript strict mode, generic correctness
- **Test coverage** — Missing edge cases, test strategy, mocking patterns, integration gaps
- **Code quality** — Naming conventions, DRY violations, error handling, logging strategy
- **Dependency audit** — Version conflicts, security advisories, license compatibility

## Review Framework

The Code Reviewer evaluates against five dimensions:

1. **Correctness** — Does the code do what it claims? Are edge cases handled?
2. **Security** — Are inputs validated? Are secrets protected? Is auth enforced?
3. **Performance** — Are there obvious bottlenecks? Is async used appropriately?
4. **Maintainability** — Is the code readable? Are abstractions appropriate? Is it testable?
5. **Standards** — Does it follow project conventions? Type hints? Docstrings? Commit format?

## Example Prompts

```
"Review this FastAPI route for security issues:
@router.post('/transfer')
async def transfer(data: dict, session: Session = Depends(get_session)):
    ..."

"Evaluate this provider abstraction pattern — is the factory approach 
the right choice vs dependency injection for 4 LLM providers?"

"Review the CrewAI ProgressCallback implementation for thread safety 
issues when running in asyncio.run_in_executor()"

"Audit the JWT authentication flow — are there any token replay 
or session fixation vulnerabilities?"
```

## API Endpoint

```bash
POST /chat/send
Authorization: Bearer <jwt>

{
  "specialist_id": "code-reviewer",
  "message": "your code or question here",
  "conversation_history": []
}
```

## Cost Estimate

Typical review (2,000 input + 2,000 output tokens): **~$0.060**
Deep architecture review (10 exchanges): **~$0.50 - $1.00**

---

*Part of the FinanceCommander AI Intelligence Portal v2.0*
