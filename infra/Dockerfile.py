FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY corpus/ corpus/

RUN pip install --no-cache-dir -e .

EXPOSE 8080
ENV MCP_RAG_CORPUS=/app/corpus

# PORT is injected by the platform (Render sets it). Falling back to 8080 keeps local runs working.
CMD ["sh", "-c", "python -m uvicorn mcp_rag_py.apps.http:app --host 0.0.0.0 --port ${PORT:-8080}"]
