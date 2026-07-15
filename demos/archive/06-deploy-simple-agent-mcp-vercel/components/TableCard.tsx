"use client";

import { useState } from "react";

const PAGE = 25;

function formatCell(v: any): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "number") return Number.isInteger(v) ? v.toLocaleString() : v.toFixed(2);
  return String(v);
}

export default function TableCard({ columns, rows }: { columns: string[]; rows: any[][] }) {
  const [page, setPage] = useState(0);
  const pages = Math.max(1, Math.ceil(rows.length / PAGE));
  const slice = rows.slice(page * PAGE, page * PAGE + PAGE);
  return (
    <div className="overflow-hidden rounded-md border border-border bg-bg text-xs">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead className="bg-panel">
            <tr>
              {columns.map(c => (
                <th key={c} className="border-b border-border px-3 py-1.5 text-left font-medium text-gray-400">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slice.map((row, i) => (
              <tr key={i} className="odd:bg-panel/40">
                {row.map((cell, j) => (
                  <td key={j} className="border-b border-border/50 px-3 py-1 text-gray-200">
                    {formatCell(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {pages > 1 && (
        <div className="flex items-center justify-between border-t border-border px-3 py-1.5 text-[11px] text-gray-400">
          <span>{rows.length.toLocaleString()} rows</span>
          <span className="flex gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
              className="disabled:opacity-30"
            >← prev</button>
            <span>{page + 1} / {pages}</span>
            <button
              disabled={page >= pages - 1}
              onClick={() => setPage(p => p + 1)}
              className="disabled:opacity-30"
            >next →</button>
          </span>
        </div>
      )}
    </div>
  );
}
