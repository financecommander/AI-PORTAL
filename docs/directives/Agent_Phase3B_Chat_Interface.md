# Phase 3B: Full Chat Interface with SSE Streaming

**Target branch:** `develop`
**New branch:** `feature/phase-3b-chat-interface`
**PR target:** `develop`
**Scope:** Replace ChatPage stub with full chat interface — message bubbles, streaming display, conversation history, input controls, cost tracking.

---

## CRITICAL CONSTRAINTS

- **DO NOT** modify any files outside `frontend/src/`
- **DO NOT** modify `api/client.ts` — the `streamChat()` method is already implemented and working
- **DO NOT** modify `types/index.ts` — all needed types (`ChatMessage`, `Specialist`, `ChatResponse`) already exist
- **DO NOT** add Redux, Zustand, or any state library — React Context + useState only
- **DO NOT** modify `Sidebar.tsx`, `Layout.tsx`, `AuthContext.tsx`, or `App.tsx`
- **DO** reuse existing CSS variables from `index.css` (`--navy`, `--navy-light`, `--navy-dark`, `--blue`, `--blue-light`)
- **DO** use Tailwind utility classes for layout — inline `style={{}}` only for CSS variable references
- **DO** use `lucide-react` for all icons (already installed)

---

## Files to Create/Modify

### 1. CREATE `frontend/src/components/chat/MessageBubble.tsx`

A single chat message bubble component.

```typescript
interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}
```

**Requirements:**
- User messages: right-aligned, background `var(--blue)`, white text, rounded-2xl with rounded-br-md
- Assistant messages: left-aligned, background `var(--navy-light)`, light text (#E0E0E0), rounded-2xl with rounded-bl-md
- Render markdown in assistant messages: bold, italic, code blocks (inline and fenced), bullet lists, numbered lists. Use basic regex/string replacement — DO NOT add a markdown library.
- Fenced code blocks: dark background (#0D1520), monospace font, 14px, horizontal scroll, top-right "Copy" button using clipboard API
- Inline code: background #0D1520, padding 2px 6px, rounded, monospace
- If `isStreaming` is true, show a blinking cursor (▌) after the last character using CSS animation
- Below assistant messages, show a muted stats line: `{input_tokens + output_tokens} tokens · ${cost_usd.toFixed(4)}` — only if tokens/cost are available and message is not streaming
- Max width: 80% of container
- Smooth fade-in animation on mount (opacity 0→1, translateY 8px→0, 200ms ease-out)

### 2. CREATE `frontend/src/components/chat/ChatInput.tsx`

The message input area at the bottom of the chat.

```typescript
interface ChatInputProps {
  onSend: (message: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled: boolean;
}
```

**Requirements:**
- Textarea (not input) that auto-grows from 1 row to max 6 rows based on content
- Background: var(--navy-light), border: 1px solid #2A3A5C, rounded-xl
- Focus: border color transitions to var(--blue)
- Placeholder: "Ask {specialistName} a question..." (pass specialist name via prop or context)
- **Send button**: right side of textarea row, blue circular button with Send icon (lucide `Send`), disabled when empty or streaming
- **Stop button**: replaces Send button when `isStreaming` is true — red circular button with Square icon (lucide `Square`), calls `onStop`
- **Enter** sends message (unless Shift+Enter for newline)
- After sending, clear textarea and refocus
- Disabled state: reduced opacity, no interaction

### 3. CREATE `frontend/src/components/chat/SpecialistHeader.tsx`

Header bar showing the selected specialist info.

```typescript
interface SpecialistHeaderProps {
  specialist: Specialist;
  messageCount: number;
}
```

**Requirements:**
- Fixed at top of chat area, background var(--navy) with bottom border (#2A3A5C)
- Left: specialist name (white, font-semibold, text-lg) + description (muted, text-sm, truncated to 1 line)
- Right: provider badge (small rounded pill, background #2A3A5C, text showing `{provider} / {model}`) + message count badge
- Height: 60px, padding 0 24px, flex items-center justify-between

### 4. CREATE `frontend/src/hooks/useChat.ts`

Custom hook encapsulating all chat logic.

```typescript
interface UseChatReturn {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  stopStreaming: () => void;
  clearChat: () => void;
}

function useChat(specialistId: string | null): UseChatReturn
```

**Requirements:**
- Maintains `messages` array in useState
- `sendMessage`:
  1. Append user message to messages array immediately
  2. Append empty assistant message (content: '') — this is the streaming target
  3. Call `api.streamChat()` with specialist_id, message, and conversation history (all prior messages as {role, content} pairs)
  4. On each chunk from `onChunk` callback: update the last assistant message's content by appending `chunk.content`
  5. When `chunk.is_final` is true: update the last assistant message with tokens and cost_usd from the final chunk
  6. Set `isStreaming` to false when stream completes
- `stopStreaming`: Uses an AbortController ref to abort the fetch. Sets isStreaming to false. Keeps whatever content was received so far.
- `clearChat`: Resets messages to empty array
- `error`: Set on stream failure, cleared on next sendMessage
- When `specialistId` changes, call `clearChat()` automatically

**AbortController pattern:**
```typescript
const abortRef = useRef<AbortController | null>(null);

const sendMessage = async (content: string) => {
  abortRef.current = new AbortController();
  // ... pass signal to streamChat if needed, or just abort the reader
};

const stopStreaming = () => {
  abortRef.current?.abort();
  setIsStreaming(false);
};
```

NOTE: The existing `api.streamChat()` does not accept an AbortSignal. For stop functionality, the simplest approach is to set a `stoppedRef` flag and have the onChunk callback check it — if stopped, ignore further chunks and don't update state.

### 5. MODIFY `frontend/src/pages/ChatPage.tsx`

Replace the entire stub with the full chat interface.

**Requirements:**
- Use the `useChat` hook for all chat state
- Layout structure (full height of viewport minus sidebar):

```
┌──────────────────────────────────────────┐
│ SpecialistHeader (fixed top)              │
├──────────────────────────────────────────┤
│                                          │
│  Messages area (scrollable, flex-1)       │
│  - MessageBubble for each message         │
│  - Auto-scroll to bottom on new message   │
│  - Empty state when no messages            │
│                                          │
├──────────────────────────────────────────┤
│ ChatInput (fixed bottom)                  │
└──────────────────────────────────────────┘
```

- **Specialist selector**: Keep the existing left panel (w-64) with specialist list. When a specialist is selected, the right side shows the chat for that specialist.
- **Auto-scroll**: Use a `messagesEndRef` with `scrollIntoView({ behavior: 'smooth' })` on message array changes
- **Empty state** (no messages yet): Centered in the messages area, show specialist name + "Start a conversation with {name}" in muted text + 3-4 example prompts as clickable chips that populate the input. Example prompts:
  - Financial Analyst: "Analyze the risk profile of a precious metals portfolio", "What are the key financial ratios for evaluating a lending company?"
  - Research Assistant: "Compare TILT lending regulations across northeastern states", "Summarize recent changes to UCC Article 9"
  - Code Reviewer: "Review this Python function for security vulnerabilities", "What are best practices for JWT token rotation?"
  - Legal Quick Consult: "What are the Article I Section 10 implications for precious metals as legal tender?", "Outline the key TILA disclosure requirements for consumer lending"
  - Default (if specialist doesn't match above): "Help me understand...", "What are the key considerations for..."
- **Scroll behavior**: Messages area has `overflow-y-auto`. New messages trigger auto-scroll ONLY if user was already at bottom (within 100px). If user scrolled up to read history, don't auto-scroll (show a "↓ New messages" pill button at bottom that scrolls to bottom on click).

### 6. ADD to `frontend/src/index.css`

Append these animations:

```css
/* Chat animations */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.animate-fade-in-up {
  animation: fadeInUp 200ms ease-out both;
}

.animate-blink {
  animation: blink 800ms infinite;
}
```

---

## Verification Steps

After all files are created:

1. `cd frontend && npm run build` — should complete with 0 errors
2. `cd frontend && npx tsc --noEmit` — should pass type checking
3. Verify no imports from files outside `frontend/src/`
4. Verify `api/client.ts` and `types/index.ts` are NOT modified
5. Verify all new components import from correct relative paths

---

## Commit Message

```
feat(frontend): Phase 3B — full chat interface with SSE streaming

- MessageBubble component with markdown rendering and streaming cursor
- ChatInput with auto-grow textarea, send/stop controls, Enter to send
- SpecialistHeader showing selected specialist info and message count
- useChat hook: message state, SSE streaming via api.streamChat(), stop/clear
- ChatPage: specialist selector + message list + auto-scroll + empty state with example prompts
- CSS animations for message fade-in and streaming cursor blink
```
