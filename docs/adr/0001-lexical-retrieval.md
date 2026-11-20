# ADR 0001 — Lexical retrieval and extractive answers instead of embeddings + LLM

- **Status:** Accepted
- **Date:** 2026-11-20
- **Deciders:** repo owner
- **Contract impact:** defines `docs/tool-contract.md` §3, §4, §5.3

## Context

The repository has to demonstrate a RAG pipeline that anyone can clone, run and verify, on hardware the reader
already owns, with **zero recurring cost** and **zero secrets**. The pipeline is also deployed to Render's free
tier, which caps the instance at **0.1 CPU / 512 MB RAM** and gives an ephemeral filesystem.

The obvious default — sentence embeddings plus a hosted LLM for the generation step — collides with four
constraints at once:

1. **Cost and secrets.** Any hosted model requires an API key, a billing account, and a rate limit that will
   eventually make the demo fail in front of someone. A portfolio repo whose demo is "currently rate limited"
   is worse than no demo.
2. **Memory.** `sentence-transformers` with a CPU torch wheel needs roughly 700 MB–1 GB RSS. The free instance has
   512 MB total, including the Python interpreter, FastAPI, and the MCP runtime.
3. **Determinism.** Neural inference is not bit-reproducible across runtimes, CPU feature sets, or library versions.
   The core claim of this repo is that two *different* implementations return the same answer; a float-comparison
   test over embeddings would need tolerance thresholds that quietly weaken the claim.
4. **Verifiability.** A reviewer can read 60 lines of BM25 in two languages and confirm they match. Nobody can
   verify two independent embedding pipelines match by reading code.

## Decision

1. **Retrieval is BM25** over the frozen tokenizer in `docs/tool-contract.md` §3, with `k1 = 1.2`, `b = 0.75`.
   Implemented twice: ~60 lines of C# and ~60 lines of Python, no dependencies, no model files.
2. **No vector database.** The index is built in memory at boot from `corpus/`. At 15 documents / ~5k tokens the
   build takes single-digit milliseconds and a brute-force scoring pass is faster than any ANN structure's overhead.
3. **The answer is extractive.** `answer` retrieves `k` chunks, scores individual sentences by query-token overlap,
   and returns up to three source sentences verbatim with citations. No generator model is called, ever.
4. **No optional LLM in v1.** A pluggable generator would double the surface area (prompt design, timeout, error
   paths, a second demo mode) for a feature nobody can test without a key. It is listed as a deferred roadmap item
   with the interface it would need.

## Consequences

**Good**

- Clone → `./scripts/test.ps1` works offline on a laptop with no GPU and no account.
- The demo cannot fail because of quota, latency, or an upstream model change.
- Cross-language parity is assertable on exact document ids.
- The deployed free instance fits comfortably inside 512 MB (measured target: < 120 MB RSS).
- Reviewers can audit the ranking logic in one sitting.

**Bad**

- **No semantic matching.** "reset my password" will not retrieve a document that only says "credential recovery".
  This is the single most visible quality gap and it is called out in the README's limitations section.
- **Answers read like quotes.** Stitched sentences have no transitions and no summarization.
- **Corpus size is a hard ceiling.** Brute-force scoring is fine at 5k tokens, uncomfortable at 5M. The design does
  not scale, by intent.
- **Language bias.** Tokenization without stemming favors languages whose morphology is shallow for this corpus
  (English). Documented, not hidden.

## Alternatives rejected

| Alternative | Why rejected |
|---|---|
| OpenAI / Anthropic embeddings + chat completion | Paid, needs a key, breaks offline reproducibility, and turns a deterministic test into a mocked one |
| Local `sentence-transformers` (all-MiniLM-L6-v2) | ~700 MB–1 GB RSS with torch: does not fit the 512 MB free instance, and the download makes first run hostile |
| ONNX Runtime + MiniLM (C# and Python) | Fits memory (~90 MB model), but two runtimes produce slightly different vectors, so the parity assertion degrades to "top-3 usually overlaps" |
| SQLite FTS5 instead of hand-written BM25 | FTS5's tokenizer and ranking are an implementation detail of the SQLite build, which makes the "two implementations, one spec" story depend on the same binary in both languages — and it hides the algorithm being demonstrated |
| TF-IDF instead of BM25 | Cheaper to write, but punishes long chunks badly; BM25 is the 15-line difference and is the standard baseline a reviewer expects |
| Hybrid (BM25 + embeddings) | Best quality, doubles the implementation in both languages and defeats the memory budget |

## Follow-up

If this ever needed to answer semantic queries, the cheapest honest upgrade path is a **shared** embedding model
loaded through ONNX in both languages, with conformance loosened to recall@3 over a labeled set, and the free-tier
deployment moved to a paid 512 MB instance with a persistent index. That is a different repo with a different
budget; it is deliberately out of scope here.
