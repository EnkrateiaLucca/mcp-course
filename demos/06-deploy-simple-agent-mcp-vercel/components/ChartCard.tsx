"use client";

import dynamic from "next/dynamic";

// Plotly ships ~3MB of JS; load only on the client.
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export default function ChartCard({ figure }: { figure: any }) {
  if (!figure) return null;
  const layout = {
    ...(figure.layout ?? {}),
    paper_bgcolor: "#121826",
    plot_bgcolor: "#121826",
    font: { color: "#e5e7eb" },
    margin: { l: 50, r: 20, t: 50, b: 50 },
    autosize: true,
  };
  return (
    <div className="rounded-md border border-border bg-bg p-2">
      <Plot
        data={figure.data ?? []}
        layout={layout}
        useResizeHandler
        style={{ width: "100%", height: "360px" }}
        config={{ displaylogo: false, responsive: true }}
      />
    </div>
  );
}
