# Transport notes

stdio: host spawns the server as a subprocess, JSON-RPC over stdin/stdout.
Streamable HTTP: one POST endpoint, optional SSE stream for server->client.
Remote servers should be stateless so any instance can answer any request.
