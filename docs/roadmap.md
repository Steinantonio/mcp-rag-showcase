# Roadmap — from lexical PoC to a complete RAG flow

> **Status:** proposal. Nothing in this document is built. Every stage lists what changes, what it costs, and — more
> importantly — what it breaks. A roadmap that only lists features is a wish list; this one lists consequences.

## 1. Where the project stands

| Dimension | Today | Consequence |
|---|---|---|
| Retrieval | BM25, frozen constants, no semantics | "reset my password" misses "credential recovery" |
| Chunking | H2 sections, 1200 chars, no overlap | a fact split across a heading boundary is unreachable |
| Storage | in-memory index, rebuilt at boot | 63 chunks fit; 63k would not |
| Answers | extractive, sentence selection | quotes, not prose |
| Evaluation | 10 golden queries, parity + spec conformance | agreement is measured; **quality** is not |
| Surface | 3 MCP tools + REST facade | no ingestion, no admin, no auth |
| Cost | R$ 0, no secret | any provider key breaks "clone and run" |

## 2. Gap map

Every row is a limitation from the README mapped to the capability that would fix it.

| Limitation today | Capability that fixes it | Stage |
|---|---|---|
| No semantic matching | embeddings + hybrid retrieval | 1 |
| Ranking ignores intent | cross-encoder rerank | 1 |
| No quality metric | labeled set + recall@k / MRR | 1 |
| One fixed chunk size | structure-aware chunking with overlap | 1 |
| Index dies with the process | persisted index + incremental updates | 2 |
| No relational data | Postgres for documents, versions, citations | 2 |
| 63 chunks is the ceiling | ANN vector index (HNSW / IVF) | 2 |
| Answers are quotes | grounded LLM generation with citation checks | 3 |
| No ingestion | `POST /documents`, async pipeline, dedupe | 4 |
| Anyone can read everything | auth, tenancy, per-corpus scoping | 4 |
| No observability | structured logs, traces, latency/recall dashboards | 5 |
| Free tier is 512 MB | paid instance or a smaller footprint | 5 |

## 3. Stages

### Stage 1 — Retrieval quality (the highest value per hour)

| Item | What changes | Cost | What it breaks |
|---|---|---|---|
| Embeddings | ONNX `all-MiniLM-L6-v2` (~90 MB) in both languages | 0 € · ~150–250 MB RSS · 2–3 days | parity test as written |
| Hybrid scoring | `score = α·bm25 + (1−α)·cosine`, α as a contract constant | 0 € · 1 day | one more constant to freeze |
| Rerank | cross-encoder over top-20, CPU only | 0 € · ~400 MB · 2 days | the 512 MB free tier |
| Eval harness | 30 labeled questions, recall@3 and MRR | 0 € · 1 day | nothing — it is additive |
| Chunking v2 | overlap 15%, split on sentence boundaries | 0 € · 1 day | every `chunkId`; full re-derivation |

**Why first:** it is the only stage where the demo gets *visibly better* without adding an external dependency, and
the eval harness is what makes every later stage measurable instead of anecdotal.

**What it breaks:** the parity suite cannot compare embeddings across runtimes bit-for-bit. Conformance changes from
"same `docId` sequence" to "recall@3 ≥ 0.9 on the labeled set, and the same `docId` for ≥ 90% of queries". That is a
weaker claim, stated honestly.

### Stage 2 — Storage: relational and vector

| Item | What changes | Cost | What it breaks |
|---|---|---|---|
| Postgres | documents, versions, chunks, citations as rows | 0 € (Neon free, 0.5 GB) · 2 days | "no database" simplicity |
| `pgvector` | embeddings in the same database, HNSW index | 0 € · 1 day | one more extension to operate |
| Incremental index | upsert on document change, no full rebuild | 0 € · 2 days | the "rebuild at boot" story |
| Migrations | versioned SQL, applied at deploy | 0 € · 1 day | Render's ephemeral filesystem needs an external DB |
| Alternative: `sqlite-vec` | embedded, zero infrastructure, ships in the image | 0 € · 1 day | write concurrency; no shared state between containers |

**Why a relational base at all:** citations, document versions and evaluation labels are relational data. A vector
store answers "what is similar"; it cannot answer "which version of which document did this answer cite". The
honest architecture is Postgres + `pgvector` for one database, or SQLite + `sqlite-vec` if the goal stays
single-node.

**What it breaks:** Render's free Postgres **expires after 30 days**, which would silently kill the demo. A free
Neon branch does not. This is the kind of detail that decides whether a demo survives a month.

### Stage 3 — Generation

| Item | What changes | Cost | What it breaks |
|---|---|---|---|
| Grounded generation | LLM receives only retrieved chunks, must cite | key required · ~0.0002 €/query | determinism |
| Citation verification | every claim must map to a cited chunk, else reject | 0 € · 1 day | the "always answers" property |
| Streaming | token stream over SSE | 0 € · 1 day | the REST contract (additive) |
| Local fallback | Ollama (`qwen2.5:3b`) behind a flag | 0 € · 2–3 GB RAM | the free tier; local only |
| Prompt/response logging | opt-in, redacted | 0 € | privacy surface |

**What it breaks:** determinism, and therefore the golden vectors. Conformance for `answer` becomes "the citation set
must contain the expected document" rather than "the answer equals". The extractive `answer` stays as the
deterministic path, so the parity claim survives on `search`.

### Stage 4 — Product surface

| Item | What changes | Cost | What it breaks |
|---|---|---|---|
| Ingestion API | `POST /documents`, validation, dedupe by hash | 0 € · 2 days | read-only simplicity |
| Async pipeline | queue + worker for chunk/embed | 0 € self-hosted · 3 days | single-process deployment |
| Auth | API keys or OIDC, per-corpus scoping | 0 € · 2 days | "clone and run" without a secret |
| Multi-tenancy | `corpus_id` on every row and every query | 0 € · 3 days | the frozen corpus |
| Admin UI | browse documents, reindex, see citations | 0 € · 3 days | scope |

**What it breaks:** every one of these adds a secret or a state, and the repository's current selling point is that
it has neither. The honest move is a `--demo` mode that keeps the anonymous read-only surface and a `--full` mode
that requires configuration.

### Stage 5 — Operations

| Item | What changes | Cost | What it breaks |
|---|---|---|---|
| Structured logs | JSON, request id, latency, `docId`s retrieved | 0 € · 1 day | nothing |
| Metrics | p95 latency, recall on a canary set, error rate | 0 € · 2 days | needs a store |
| Tracing | OpenTelemetry across adapter → core → store | 0 € · 2 days | adds dependencies to the shell only |
| Cost guard | per-day query budget, hard stop | 0 € · 1 day | availability during abuse |
| Paid instance | 1 CPU / 2 GB, no cold start | ~7 €/month | the "zero cost" claim |

## 4. What each stage does to the claims

| Stage | Contract | Parity test | Free tier | README claim that dies |
|---|---|---|---|---|
| 1 | `contractVersion` 2 (α, chunk overlap) | becomes recall-based | embeddings fit, rerank does not | "no model download" |
| 2 | unchanged | unchanged | needs an external DB | "no database" |
| 3 | additive (`answer` gains a mode) | `search` only | needs a key | "no API key", "deterministic" |
| 4 | breaking (auth headers) | unchanged | unchanged | "clone and run" |
| 5 | unchanged | unchanged | paid | "R$ 0" |

## 5. Technology options, with the trade-off that matters

| Choice | Option A | Option B | What decides it |
|---|---|---|---|
| Embeddings | ONNX local (free, deterministic-ish, 90 MB) | hosted API (tiny cost, needs key) | whether "clone and run" survives |
| Vector store | `pgvector` (one database, relational joins) | Qdrant (better ANN, another service) | whether citations and vectors live together |
| Generator | hosted small model (quality, latency) | Ollama local (free, private, slow) | whether the demo runs offline |
| Eval | 30 hand-labeled questions | synthetic Q/A generated by an LLM | whether the metric can be trusted |
| Rerank | cross-encoder CPU | hosted rerank API | memory budget |

## 6. Decision gates

These are the decisions that must be taken **before** writing code, not during:

1. **Does the free-tier demo survive?** If yes, no reranker, no torch, no paid instance. If no, the README's cost
   table changes and the repo stops being "clone and run for free".
2. **Is determinism still the differentiator?** Adding an LLM trades the strongest claim for the most familiar one.
3. **One database or two?** Postgres + `pgvector` is simpler to operate; Qdrant is better at scale. At 63 chunks the
   answer is obvious; at 63 million it is the opposite.
4. **Who owns the labels?** An eval harness without hand-labeled data measures nothing.

## 7. Recommended order, if the goal is portfolio value

| Order | Item | Effort | Why now |
|---|---|---|---|
| 1 | Eval harness (30 questions, recall@3) | 1 day | turns every later change into a measurement |
| 2 | Hybrid retrieval (BM25 + ONNX embeddings) | 3 days | visible quality jump, still free |
| 3 | `sqlite-vec` or `pgvector` + incremental index | 2 days | removes the "63 chunks" ceiling |
| 4 | Grounded generation behind a flag | 3 days | the feature everyone expects to see |
| 5 | Everything else | — | only if a real user asks |

## 8. Deliberately not planned

- **A framework migration** (LangChain, LlamaIndex). The point of the repository is that the pipeline is readable in
  one sitting; a framework would hide exactly what it is trying to show.
- **Multi-modal retrieval.** Real work, wrong repository.
- **A benchmark against public datasets.** Interesting, but it would replace "checkable in five minutes" with
  "trust our numbers".
- **Kubernetes.** Two containers and a compose file are the correct amount of orchestration for two containers.
