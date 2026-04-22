"use client";

type Props = {
  value: number;
  label: string;
  delta?: number;
  format?: "currency" | "percent" | "number";
};

// TODO — YOUR IMPLEMENTATION
// Format `value` based on `format`. If `format` is undefined, pick a reasonable
// default. Consider:
//   - "currency"  → "€1,234,567" (use Intl.NumberFormat with pt-PT + EUR)
//   - "percent"   → "21.4%" (multiply by 100 if value is a fraction 0..1,
//                   otherwise treat as already-a-percentage — your call)
//   - "number"    → "1,234,567.89" (locale-aware thousands separator, 2 decimals max)
//   - default     → decide: fall through to "number"? Or sniff magnitude?
//
// This function is the *only* place the whole UI formats a KPI, so getting it
// right once pays off everywhere.
function formatValue(value: number, format?: "currency" | "percent" | "number"): string {
  // ← IMPLEMENT ME
  return String(value);
}

export default function KPICard({ value, label, delta, format }: Props) {
  const positive = (delta ?? 0) >= 0;
  return (
    <div className="inline-block min-w-[180px] rounded-md border border-border bg-bg px-4 py-3">
      <div className="text-xs uppercase tracking-wider text-gray-400">{label}</div>
      <div className="mt-1 text-2xl font-semibold tabular-nums">{formatValue(value, format)}</div>
      {delta !== undefined && (
        <div className={`mt-0.5 text-xs ${positive ? "text-emerald-400" : "text-red-400"}`}>
          {positive ? "▲" : "▼"} {Math.abs(delta).toFixed(2)}
        </div>
      )}
    </div>
  );
}
