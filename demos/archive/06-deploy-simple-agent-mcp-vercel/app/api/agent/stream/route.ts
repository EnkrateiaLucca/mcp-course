// This Next.js route exists only for local `next dev`. In production on
// Vercel, the vercel.json rewrite routes /api/agent/stream directly to the
// Python function and this file is never invoked.
//
// During `next dev`, Python functions under /api run on a separate port
// started by `vercel dev`. We just pass the request through.

export const runtime = "nodejs";

const PY_TARGET = process.env.PY_AGENT_URL ?? "http://localhost:3000/api/agent";

export async function POST(req: Request) {
  const body = await req.text();
  const upstream = await fetch(PY_TARGET + "/stream", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });
  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "content-type": "text/event-stream",
      "cache-control": "no-cache, no-transform",
      connection: "keep-alive",
    },
  });
}
