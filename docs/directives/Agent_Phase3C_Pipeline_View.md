# Phase 3C: Pipeline Execution View with WebSocket Streaming

**Target branch:** `develop`
**New branch:** `feature/phase-3c-pipeline-view`
**PR target:** `develop`
**Scope:** Replace PipelinesPage stub with full pipeline execution UI — query input, real-time agent progress via WebSocket, cost tracking, and final output display.

---

## CRITICAL CONSTRAINTS

- **DO NOT** modify any files in `backend/`, `api/client.ts`, or `types/index.ts`
- **DO NOT** modify `Sidebar.tsx`, `Layout.tsx`, `AuthContext.tsx`, or `App.tsx`
- **DO NOT** add any new npm dependencies — use only what Phase 3A installed (React, Tailwind, lucide-react, clsx)
- **DO** reuse existing CSS variables from `index.css` (`--navy`, `--navy-light`, `--navy-dark`, `--blue`, `--blue-light`, `--green`, `--orange`, `--red`)
- **DO** use the existing `api.connectPipelineWS()` method from `api/client.ts` for WebSocket
- **DO** use the existing `api.post()` method for `POST /api/v2/pipelines/run`
- **DO** use existing types from `types/index.ts` (`Pipeline`, `PipelineAgent`, `PipelineRun`)

---

## Backend API Contract (DO NOT MODIFY — build frontend to match)

**List pipelines:**
```
GET /api/v2/pipelines/list
Response: { pipelines: [{ name, display_name, description, agents: string[], type }], count }
```

**Execute pipeline:**
```
POST /api/v2/pipelines/run
Body: { pipeline_name: string, query: string }
Response: { pipeline_id, status, output, total_tokens, total_cost, duration_ms, agent_breakdown, ws_url }
```

**WebSocket progress events:**
```
WS /api/v2/pipelines/ws/{pipeline_id}?token={jwt}
Events:
  { type: "agent_start", pipeline_id, timestamp, data: { agent: "Agent Name" } }
  { type: "agent_complete", pipeline_id, timestamp, data: { agent, tokens: {input, output}, cost, duration_ms, output } }
  { type: "complete", pipeline_id, timestamp, data: { output, total_cost, total_tokens, duration_ms } }
  { type: "error", pipeline_id, timestamp, data: { message } }
```

---

## Files to Create/Modify

### 1. CREATE `frontend/src/components/pipeline/PipelineCard.tsx`

Displays a single pipeline in the grid (selection card before execution).

```typescript
interface PipelineCardProps {
  pipeline: { name: string; display_name: string; description: string; agents: string[]; type: string };
  onSelect: (name: string) => void;
  isSelected: boolean;
}
```

**Requirements:**
- Card with background var(--navy), rounded-xl, padding 20px, hover border glow effect (border transitions to var(--blue) on hover)
- Top row: Brain icon (lucide, color var(--blue)) + display_name (white, font-semibold)
- Description: muted text (#8899AA), text-sm, 2-line clamp
- Agent pills row: each agent name in a small rounded pill (background var(--navy-dark), text #8899AA, text-xs)
- Bottom: "Run Pipeline →" button or selected state indicator
- Selected state: border solid var(--blue), subtle blue glow shadow

### 2. CREATE `frontend/src/components/pipeline/AgentProgressCard.tsx`

Shows a single agent's status during pipeline execution.

```typescript
interface AgentProgressCardProps {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  index: number;
  totalAgents: number;
  tokens?: { input: number; output: number };
  cost?: number;
  durationMs?: number;
  output?: string;
}
```

**Requirements:**
- Horizontal card, full width, background var(--navy), rounded-lg, padding 16px
- Left: step number circle (32px, centered number)
  - pending: border dashed #2A3A5C, text #556677
  - running: border solid var(--blue), animated pulse glow, text white
  - complete: background var(--green), text white, show checkmark icon instead of number
  - error: background var(--red), text white, show X icon
- Center: agent name (white when running/complete, muted when pending) + status text below
  - pending: "Waiting..."
  - running: "Analyzing..." with animated dots (1-3 dots cycling)
  - complete: show tokens + cost + duration in muted text: "{input+output} tokens · ${cost.toFixed(4)} · {(durationMs/1000).toFixed(1)}s"
  - error: "Failed" in red
- Right: expand/collapse chevron (only when complete and output exists)
- Expanded: show agent output text below card in a collapsible panel, muted text, text-sm, max-height 200px with overflow scroll
- Connection line: thin vertical line (2px, #2A3A5C) connecting each card to the next. Running agent's line segment should be animated (gradient pulse). Last agent has no line below.

### 3. CREATE `frontend/src/components/pipeline/PipelineProgress.tsx`

Container for the full pipeline execution progress view.

```typescript
interface PipelineProgressProps {
  agents: AgentStatus[];
  status: 'idle' | 'running' | 'complete' | 'error';
  totalCost?: number;
  totalTokens?: number;
  durationMs?: number;
  output?: string;
  error?: string;
}

interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  tokens?: { input: number; output: number };
  cost?: number;
  durationMs?: number;
  output?: string;
}
```

**Requirements:**
- Vertical stack of AgentProgressCard components with connecting lines
- Top: progress summary bar showing "Agent {currentIndex}/{total}" with a thin horizontal progress bar (var(--blue) fill, animated width transition)
- When status is 'complete': show total cost summary card at bottom
  - Background var(--navy), green left border (4px), rounded-lg
  - "Pipeline Complete" heading + total tokens, total cost, total duration
  - Below: "View Full Opinion" button that expands the final output
- When status is 'error': show error card with red left border and error message
- Final output panel: when expanded, show the full synthesis output with the same markdown rendering used in MessageBubble (bold, italic, code blocks, lists). Reuse or extract the markdown renderer from Phase 3B.

### 4. CREATE `frontend/src/components/pipeline/QueryInput.tsx`

Input form for submitting a legal query to the pipeline.

```typescript
interface QueryInputProps {
  onSubmit: (query: string) => void;
  isRunning: boolean;
  pipelineName: string;
}
```

**Requirements:**
- Large textarea (4 rows default, auto-grows to 8 max), background var(--navy-light), border #2A3A5C, rounded-xl
- Placeholder: "Enter your legal question for Lex Intelligence..."
- Below textarea: row with estimated cost badge ("Est. $0.50–$1.20 per run", muted) on left, "Run Analysis" button on right
- Button: background var(--blue), white text, rounded-lg, flex with Play icon (lucide `Play`). Disabled + spinner when isRunning.
- Shift+Enter for newline, Enter alone does NOT submit (opposite of chat — legal queries are longer)
- 3 example query chips below the textarea (clickable, populate the textarea):
  - "What are the Article I Section 10 implications for precious metals as constitutional tender?"
  - "Analyze the enforceability of acceleration clauses in TILT consumer lending agreements under TILA"
  - "Evaluate litigation risk for the Eureka settlement coordination model under state escrow regulations"

### 5. CREATE `frontend/src/hooks/usePipeline.ts`

Custom hook encapsulating pipeline execution logic.

```typescript
interface UsePipelineReturn {
  agents: AgentStatus[];
  status: 'idle' | 'running' | 'complete' | 'error';
  output: string | null;
  totalCost: number | null;
  totalTokens: number | null;
  durationMs: number | null;
  error: string | null;
  runPipeline: (pipelineName: string, query: string) => Promise<void>;
  reset: () => void;
}
```

**Requirements:**
- `runPipeline`:
  1. Set status to 'running'
  2. Initialize agents array from pipeline's agent list (all 'pending')
  3. Call `api.post('/api/v2/pipelines/run', { pipeline_name, query })` 
  4. On response, get `pipeline_id`
  5. Connect WebSocket via `api.connectPipelineWS(pipeline_id, onEvent, onClose)`
  6. Handle events:
     - `agent_start`: Set that agent's status to 'running'
     - `agent_complete`: Set agent's status to 'complete', store tokens/cost/duration/output
     - `complete`: Set overall status to 'complete', store output/totalCost/totalTokens/durationMs
     - `error`: Set overall status to 'error', store error message
  7. On WebSocket close: if status is still 'running', set to 'error' with "Connection lost"
- `reset`: Clear all state back to idle
- Store WebSocket ref for cleanup on unmount (useEffect cleanup)

NOTE: The backend POST `/api/v2/pipelines/run` is synchronous — it runs the full pipeline and returns the result. The WebSocket provides real-time progress during execution. The hook should:
1. Connect WebSocket FIRST
2. Then POST to start the pipeline
3. WebSocket receives progress events while POST is pending
4. POST returns final result (use as fallback if WebSocket missed events)

### 6. MODIFY `frontend/src/pages/PipelinesPage.tsx`

Replace the entire stub with the full pipeline execution interface.

**Requirements:**
- Two-state layout:

**State 1: Pipeline Selection (status === 'idle')**
```
┌──────────────────────────────────────────┐
│ Page header: "Intelligence Pipelines"      │
├──────────────────────────────────────────┤
│ Pipeline cards grid (1-3 columns)         │
│ [Lex Intelligence] [Calculus] [Forge]     │
├──────────────────────────────────────────┤
│ Selected pipeline details + QueryInput    │
└──────────────────────────────────────────┘
```

**State 2: Pipeline Running/Complete (status !== 'idle')**
```
┌──────────────────────────────────────────┐
│ Header: pipeline name + "← Back" button   │
├──────────────────────────────────────────┤
│ QueryInput (readonly, showing the query)  │
├──────────────────────────────────────────┤
│ PipelineProgress                          │
│  ┌─ Agent 1: ✅ complete ─────────────┐   │
│  │  Agent 2: ✅ complete              │   │
│  │  Agent 3: 🔄 running...           │   │
│  │  Agent 4: ⏳ pending              │   │
│  │  Agent 5: ⏳ pending              │   │
│  └─ Agent 6: ⏳ pending ─────────────┘   │
├──────────────────────────────────────────┤
│ Results summary + full output (on done)   │
└──────────────────────────────────────────┘
```

- "← Back" button (top left, when not idle): calls `reset()` and returns to selection
- Pipeline cards: clicking one selects it and shows QueryInput below
- Running state: transition from selection to progress with a smooth animation
- Scrollable: the progress section should auto-scroll to the currently running agent

### 7. ADD to `frontend/src/index.css`

Append these animations (if not already present from Phase 3B):

```css
/* Pipeline animations */
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 4px rgba(46, 117, 182, 0.3); }
  50% { box-shadow: 0 0 12px rgba(46, 117, 182, 0.6); }
}

@keyframes dotCycle {
  0% { content: '.'; }
  33% { content: '..'; }
  66% { content: '...'; }
}

.animate-pulse-glow {
  animation: pulseGlow 2s ease-in-out infinite;
}
```

---

## Verification Steps

After all files are created:

1. `cd frontend && npm run build` — should complete with 0 errors
2. `cd frontend && npx tsc --noEmit` — should pass type checking
3. Verify no imports from `backend/` or modifications to `api/client.ts`, `types/index.ts`
4. Verify all new components are in `frontend/src/components/pipeline/`
5. Verify `usePipeline` hook is in `frontend/src/hooks/`

---

## Commit Message

```
feat(frontend): Phase 3C — pipeline execution view with WebSocket streaming

- PipelineCard component for pipeline selection grid
- AgentProgressCard with status indicators, connecting lines, and expandable output
- PipelineProgress container with progress bar and completion summary
- QueryInput with example prompts and cost estimate badge
- usePipeline hook: WebSocket connection, agent status tracking, error handling
- PipelinesPage: two-state layout (selection → execution → results)
- CSS animations for agent pulse glow during execution
```
