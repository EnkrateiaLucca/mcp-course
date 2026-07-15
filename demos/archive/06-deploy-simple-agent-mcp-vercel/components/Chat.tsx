"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import MessageRenderer, { AssistantBlock, ChatMessage } from "./MessageRenderer";

const STORAGE_KEY = "data-analysis-chat:messages";
const SESSION_KEY = "data-analysis-chat:session";

function getSessionId(): string {
  if (typeof window === "undefined") return "ssr";
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try { setMessages(JSON.parse(raw)); } catch {}
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  // Cleanup the sandbox when the tab closes.
  useEffect(() => {
    const handler = () => {
      navigator.sendBeacon?.(
        "/api/agent/cleanup",
        new Blob([JSON.stringify({ session_id: getSessionId() })],
                 { type: "application/json" })
      );
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, []);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || streaming) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput("");
    setStreaming(true);

    // Start an assistant message that we'll stream into.
    const assistantMsg: ChatMessage = { role: "assistant", blocks: [] };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      const resp = await fetch("/api/agent/stream", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          session_id: getSessionId(),
          messages: nextMessages.map(m => ({
            role: m.role,
            content: m.role === "user"
              ? m.content
              : (m.blocks ?? []).map(b => b.kind === "text" ? b.text : "").join(""),
          })),
        }),
      });
      if (!resp.ok || !resp.body) {
        appendBlock({ kind: "error", message: `HTTP ${resp.status}` });
        return;
      }
      await readSSE(resp.body, (evt, data) => applyEvent(evt, data));
    } catch (e) {
      appendBlock({ kind: "error", message: String(e) });
    } finally {
      setStreaming(false);
    }

    function applyEvent(event: string, data: any) {
      if (event === "delta" && typeof data?.text === "string") {
        appendText(data.text);
      } else if (event === "tool_use") {
        appendBlock({
          kind: "tool_use",
          id: data.id, name: data.name, input: data.input,
        });
      } else if (event === "tool_result") {
        applyToolResult(data);
      } else if (event === "error") {
        appendBlock({ kind: "error", message: data.message ?? "error" });
      }
    }

    function appendText(text: string) {
      setMessages(prev => {
        const copy = [...prev];
        const last = copy[copy.length - 1];
        if (last?.role !== "assistant") return copy;
        const blocks = [...(last.blocks ?? [])];
        const tail = blocks[blocks.length - 1];
        if (tail && tail.kind === "text") {
          blocks[blocks.length - 1] = { kind: "text", text: tail.text + text };
        } else {
          blocks.push({ kind: "text", text });
        }
        copy[copy.length - 1] = { ...last, blocks };
        return copy;
      });
    }

    function appendBlock(block: AssistantBlock) {
      setMessages(prev => {
        const copy = [...prev];
        const last = copy[copy.length - 1];
        if (last?.role !== "assistant") return copy;
        copy[copy.length - 1] = {
          ...last,
          blocks: [...(last.blocks ?? []), block],
        };
        return copy;
      });
    }

    function applyToolResult(data: any) {
      const parsed = data?.result ?? {};
      const type = parsed?.type;
      const payload = parsed?.payload ?? {};
      if (type === "chart") {
        appendBlock({ kind: "chart", figure: payload.figure, toolUseId: data.tool_use_id });
      } else if (type === "table") {
        appendBlock({ kind: "table", columns: payload.columns, rows: payload.rows, toolUseId: data.tool_use_id });
      } else if (type === "kpi") {
        appendBlock({ kind: "kpi", value: payload.value, label: payload.label, delta: payload.delta, toolUseId: data.tool_use_id });
      } else if (type === "error") {
        appendBlock({ kind: "error", message: payload.message ?? "Tool error" });
      } else {
        appendBlock({ kind: "text", text: JSON.stringify(payload) });
      }
    }
  }, [input, messages, streaming]);

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-border bg-panel">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="rounded-lg border border-dashed border-border p-6 text-center text-gray-400">
            <p className="mb-2 font-medium">Try:</p>
            <ul className="space-y-1 text-sm">
              <li>“List the available tables.”</li>
              <li>“Show me the top 10 companies by 2025 revenue as a bar chart.”</li>
              <li>“Compare EBITDA across sectors over 5 years as a line chart.”</li>
              <li>“Which district has the highest total revenue?”</li>
              <li>“Find companies with the highest debt-to-equity ratio.”</li>
            </ul>
          </div>
        )}
        {messages.map((m, i) => <MessageRenderer key={i} message={m} />)}
        {streaming && <div className="text-xs text-gray-500">streaming…</div>}
      </div>
      <form
        className="flex gap-2 border-t border-border bg-panel p-3"
        onSubmit={e => { e.preventDefault(); send(); }}
      >
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a question about the dataset…"
          className="flex-1 rounded-md border border-border bg-bg px-3 py-2 text-sm outline-none focus:border-accent"
          disabled={streaming}
        />
        <button
          type="submit"
          disabled={streaming || !input.trim()}
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
        <button
          type="button"
          onClick={clearChat}
          className="rounded-md border border-border px-3 py-2 text-sm text-gray-300 hover:bg-bg"
        >
          Clear
        </button>
      </form>
    </div>
  );
}

// ----- SSE reader ------------------------------------------------------------
// Parse `event:` + `data:` lines and hand them to `onEvent(event, data)`.

async function readSSE(
  body: ReadableStream<Uint8Array>,
  onEvent: (event: string, data: any) => void
): Promise<void> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  let currentEvent = "message";
  // Find the next event boundary. SSE allows both LF and CRLF line endings,
  // so the separator is any blank line — `\n\n`, `\r\n\r\n`, or a mix.
  const boundary = (s: string): number => {
    const a = s.indexOf("\n\n");
    const b = s.indexOf("\r\n\r\n");
    if (a === -1) return b;
    if (b === -1) return a;
    return Math.min(a, b);
  };
  const boundaryLen = (s: string, idx: number): number =>
    s.startsWith("\r\n\r\n", idx) ? 4 : 2;

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = boundary(buf)) !== -1) {
      const chunk = buf.slice(0, idx);
      buf = buf.slice(idx + boundaryLen(buf, idx));
      currentEvent = "message";
      const dataLines: string[] = [];
      for (const rawLine of chunk.split(/\r?\n/)) {
        const line = rawLine; // keep as-is, trim on match below
        if (line.startsWith("event:")) currentEvent = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
      }
      if (!dataLines.length) continue;
      const raw = dataLines.join("\n");
      try {
        onEvent(currentEvent, JSON.parse(raw));
      } catch {
        onEvent(currentEvent, { raw });
      }
    }
  }
}
