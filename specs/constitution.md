# Constitution — mcp-rag-showcase

Rules that no spec, plan or task may violate. A condensed, testable version of `AGENTS.md` for the specification
layer.

**Status:** approved · **Owner:** orchestrator · **Last updated:** 2026-11-20

## Article 1 — Contract before code

`docs/tool-contract.md` defines chunking, tokenization, BM25 constants, ordering and tool schemas. No implementation
may deviate from it. When code and contract disagree, the contract wins until an ADR records a deliberate change.
A contract change bumps `contractVersion` and invalidates the golden vectors.

## Article 2 — One dependency direction

```
adapters (MCP stdio · MCP HTTP · REST · CLI · filesystem)
        │
        ▼
      core (tokenizer · chunker · bm25 · engine)
```

- `core` imports no framework, no HTTP client or server, no MCP SDK, no filesystem API, no environment variable.
- Adapters depend on `core`. `core` never depends on an adapter.
- Enforced by `import-linter` (Python) and `NetArchTest` (.NET), not by good intentions.

## Article 3 — Parity is asserted on identifiers, not floats

The conformance suite compares the `docId` sequence produced by both servers for the same query. Scores may differ
in the last bits because `ln` implementations differ. A test that asserts float equality is a defect.

Golden expectations are written from the contract, never captured from an implementation's output.

## Article 4 — Zero cost, zero secrets

The repository must clone, build, test and run with no account, no API key, no paid dependency and no model
download. Any change that requires a secret requires an ADR and an explicit owner decision.

## Article 5 — Determinism

`core` has no clock, no randomness, no network, no locale-sensitive operation, no global mutable state. Given the
same corpus and query it returns the same result, in the same order, in both languages, on any platform.

## Article 6 — Evidence or it did not happen

Every acceptance criterion maps to a named test or a named manual check. Every claim about a command includes the
command and its real output. A transcript in the README comes from a real run, pasted verbatim.

## Article 7 — The corpus is frozen once expectations exist

Golden vectors are derived against a specific `N` and `avgdl`. Adding or editing a document invalidates all of them.
Corpus changes require a new spec, re-derived expectations reviewed line by line, and a contract version bump if
chunking behavior changes.

## Article 8 — Scope is defended in public

The README lists what is deliberately not built. Adding a feature that is on that list requires removing it from the
list in the same change, with a reason. Silent scope growth is a defect.
