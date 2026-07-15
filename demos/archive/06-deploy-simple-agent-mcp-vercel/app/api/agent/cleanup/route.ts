// Pass-through proxy for local `next dev` — see /api/agent/stream/route.ts.
export const runtime = "nodejs";

const PY_TARGET = process.env.PY_AGENT_URL ?? "http://localhost:3000/api/agent";

export async function POST(req: Request) {
  const body = await req.text();
  const upstream = await fetch(PY_TARGET + "/cleanup", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });
  const text = await upstream.text();
  return new Response(text, {
    status: upstream.status,
    headers: { "content-type": "application/json" },
  });
}
