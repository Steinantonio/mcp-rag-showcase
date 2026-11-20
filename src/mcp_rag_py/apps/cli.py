"""CLI: the proof-of-concept surface. ingest | query | answer.

No MCP server is involved in this wave. If this works, the RAG works.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from mcp_rag_py.adapters.corpus_fs import load_documents
from mcp_rag_py.apps.config import resolve_corpus_dir
from mcp_rag_py.core.engine import RagEngine


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-rag-py",
        description="Retrieval over the mcp-rag-showcase corpus.",
    )
    parser.add_argument("--corpus", help="corpus directory (default: ./corpus or $MCP_RAG_CORPUS)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ingest", help="build the index and print corpus stats")

    query = subparsers.add_parser("query", help="ranked chunks for a query")
    query.add_argument("text")
    query.add_argument("-k", type=int, default=5)
    query.add_argument("--json", action="store_true", help="machine-readable output")

    answer = subparsers.add_parser("answer", help="extractive answer with citations")
    answer.add_argument("text")
    answer.add_argument("-k", type=int, default=3)
    answer.add_argument("--json", action="store_true", help="machine-readable output")

    return parser


def _search_payload(result: Any) -> dict[str, Any]:
    return {
        "query": result.query,
        "k": result.k,
        "totalMatched": result.total_matched,
        "results": [
            {
                "docId": hit.doc_id,
                "chunkId": hit.chunk_id,
                "title": hit.title,
                "heading": hit.heading,
                "score": hit.score,
                "citation": hit.citation,
                "text": hit.text,
            }
            for hit in result.results
        ],
    }


def _answer_payload(result: Any) -> dict[str, Any]:
    return {
        "query": result.query,
        "answer": result.answer,
        "citations": list(result.citations),
        "grounded": result.grounded,
    }


def _print_error(code: str, message: str) -> None:
    print(f"error {code}: {message}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    loaded = load_documents(resolve_corpus_dir(args.corpus))
    if not loaded.is_ok:
        _print_error(loaded.error.code.value, loaded.error.message)
        return 1

    engine = RagEngine(loaded.value)

    if args.command == "ingest":
        stats = engine.stats()
        print(f"{stats.documents} documents, {stats.chunks} chunks, avgdl {stats.avg_chunk_tokens}")
        return 0

    if args.command == "query":
        result = engine.search(args.text, args.k)
        if not result.is_ok:
            _print_error(result.error.code.value, result.error.message)
            return 2
        if args.json:
            print(json.dumps(_search_payload(result.value), ensure_ascii=False, indent=2))
            return 0
        print(f"query: {args.text}  (matched {result.value.total_matched})")
        for position, hit in enumerate(result.value.results, start=1):
            print(f"{position}. {hit.chunk_id}  {hit.score:.4f}  {hit.heading}")
        return 0

    result = engine.answer(args.text, args.k)
    if not result.is_ok:
        _print_error(result.error.code.value, result.error.message)
        return 2
    if args.json:
        print(json.dumps(_answer_payload(result.value), ensure_ascii=False, indent=2))
        return 0
    print(result.value.answer)
    if result.value.citations:
        print(f"\nsources: {', '.join(result.value.citations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
