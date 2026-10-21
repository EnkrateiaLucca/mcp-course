FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
# claude-agent-sdk ships the Claude Code binary in its wheel: no Node.js needed.
RUN uv sync --frozen --no-dev
COPY app.py ./
COPY static ./static
RUN useradd --create-home agent && mkdir .claude-home && chown agent .claude-home
ENV PATH="/app/.venv/bin:$PATH"
USER agent
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
