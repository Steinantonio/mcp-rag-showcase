"""MCP entry point: stdio or streamable HTTP transport."""

from __future__ import annotations

import argparse
import sys

from mcp_rag_py.adapters.corpus_fs import load_documents
from mcp_rag_py.adapters.mcp_server import create_mcp_server
from mcp_rag_py.apps.config import resolve_corpus_dir
from mcp_rag_py.core.engine import RagEngine


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mcp-rag-py-mcp")
    parser.add_argument("--corpus", help="corpus directory")
    parser.add_argument(
        "--transport",
        choices=("stdio", "http"),
        default="stdio",
        help="transport to use (default: stdio)",
    )
    parser.add_argument("--port", type=int, default=8080, help="port for HTTP transport")
    args = parser.parse_args(argv)

    loaded = load_documents(resolve_corpus_dir(args.corpus))
    if not loaded.is_ok:
        print(f"fatal {loaded.error.code.value}: {loaded.error.message}", file=sys.stderr)
        return 1

    engine = RagEngine(loaded.value)
    server = create_mcp_server(engine)

    if args.transport == "http":
        server.run(transport="streamable-http", host="0.0.0.0", port=args.port)
    else:
        server.run(transport="stdio")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
