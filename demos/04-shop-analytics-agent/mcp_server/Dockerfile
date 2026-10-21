FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY seed.py server.py ./
# Demo data is baked into the image. Swap this line for your real database (mounted volume or copied file).
RUN uv run --no-sync python seed.py shop.db
ENV PATH="/app/.venv/bin:$PATH"
USER nobody
EXPOSE 8001
CMD ["python", "server.py"]
