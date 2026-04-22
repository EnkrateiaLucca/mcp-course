"use client";

import ChartCard from "./ChartCard";
import TableCard from "./TableCard";
import KPICard from "./KPICard";

export type AssistantBlock =
  | { kind: "text"; text: string }
  | { kind: "tool_use"; id: string; name: string; input: any }
  | { kind: "chart"; figure: any; toolUseId?: string }
  | { kind: "table"; columns: string[]; rows: any[][]; toolUseId?: string }
  | { kind: "kpi"; value: number; label: string; delta?: number | null; toolUseId?: string }
  | { kind: "error"; message: string };

export type ChatMessage =
  | { role: "user"; content: string }
  | { role: "assistant"; blocks: AssistantBlock[] };

export default function MessageRenderer({ message }: { message: ChatMessage }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-lg bg-accent/30 px-3 py-2 text-sm">
          {message.content}
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-3">
      {message.blocks.map((b, i) => <BlockRenderer key={i} block={b} />)}
    </div>
  );
}

function BlockRenderer({ block }: { block: AssistantBlock }) {
  switch (block.kind) {
    case "text":
      return (
        <div className="whitespace-pre-wrap text-sm leading-relaxed text-gray-100">
          {block.text}
        </div>
      );
    case "tool_use":
      return (
        <details className="rounded-md border border-border bg-bg/60 text-xs">
          <summary className="cursor-pointer px-3 py-1.5 text-gray-400">
            → {block.name.replace(/^mcp__analysis__/, "")}
          </summary>
          <pre className="overflow-x-auto px-3 py-2 text-[11px] text-gray-400">
            {JSON.stringify(block.input, null, 2)}
          </pre>
        </details>
      );
    case "chart":
      return <ChartCard figure={block.figure} />;
    case "table":
      return <TableCard columns={block.columns} rows={block.rows} />;
    case "kpi":
      return <KPICard value={block.value} label={block.label} delta={block.delta ?? undefined} />;
    case "error":
      return (
        <div className="rounded-md border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-300">
          {block.message}
        </div>
      );
  }
}
