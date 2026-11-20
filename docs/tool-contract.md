# Tool contract v1

This document is the **single source of truth** for both MCP servers. If an implementation disagrees with this file,
the implementation is wrong. Changing anything here is a contract change: bump `contractVersion` and update the
golden vectors.

- `contractVersion`: `1`
- Reference implementations: `src/Mcp.Rag.Dotnet`, `src/mcp_rag_py`
- Conformance data: `corpus/golden/queries.json`

---

## 1. Corpus format

Each document is a markdown file in `corpus/` with a **restricted front-matter block** — deliberately not full YAML,
so both languages can parse it with the same 20 lines of code and no dependency:

```markdown
---
id: ops-credentials
title: Rotating API keys
tags: security, credentials, api
---
## Why rotate

Body text...

## How to rotate

Body text...
```

Rules:

| Rule | Value |
|---|---|
| File name | `<id>.md`, where `id` matches `^[a-z0-9]+(-[a-z0-9]+)*$` |
| Front matter | First line `---`, terminated by a second `---`. Only `id:`, `title:`, `tags:` are read |
| `tags` | Comma-separated, trimmed, lowercased |
| Unknown front-matter keys | Ignored |
| Encoding | UTF-8, LF or CRLF (normalized to LF before chunking) |
| Heading level used for chunk boundaries | `##` (H2) only |
| Content before the first `##` | Merged into a chunk with `heading: ""` |

## 2. Chunking

Deterministic, no overlap, no token counting:

1. Normalize line endings to `\n`, trim trailing whitespace on every line, drop trailing blank lines.
2. Split the body on lines matching `^## ` (the `## ` prefix is stripped and kept as `heading`).
3. For each section: if the section body exceeds **1200 characters**, split on blank lines (`\n\n`) into
   paragraphs and greedily pack paragraphs into pieces of at most 1200 characters. A single paragraph longer
   than 1200 characters is split at the last space before the limit.
4. Chunk `text` = the packed body **only** (no heading prefix, no title prefix).
5. `chunkId` = `"{docId}#{index}"` where `index` is the zero-based position, formatted with two digits (`#00`).

Metadata travels beside the text, never inside it, so tokenization stays identical across languages.

## 3. Tokenization

The scoring spec is only portable if tokenization is frozen:

1. Lowercase using invariant/root-locale lowercasing (Python: `str.lower()`; .NET: `ToLowerInvariant()`).
2. Split on every run of characters that are **not** Unicode letters or digits: regex `[^\p{L}\p{N}]+`.
3. Keep every token, including single characters. No stemming. No stopword list. No accent folding.
4. A token is the resulting string; empty tokens are discarded.

No language-specific analyzer, no ICU segmentation, no `string.Split` overloads with culture. If a future change
needs stemming, it needs a shared stemmer ported to both languages and new golden vectors.

## 4. Scoring (BM25)

For query `q` with tokens `t`, over the chunk collection `D`:

```
score(chunk) = Σ over t in q:
                 idf(t) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))

idf(t)  = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
k1      = 1.2
b       = 0.75
N       = number of chunks
df(t)   = number of chunks containing t
tf      = raw count of t in the chunk
dl      = token count of the chunk
avgdl   = mean token count across all chunks
```

Repeated query tokens count repeatedly (no query-side deduplication).

**Ordering.** Sort by `score` descending, then `docId` ascending, then `chunkId` ascending. Chunks with `score = 0`
are excluded. If fewer than `k` chunks score above zero, return what exists — never pad with zeros.

**Float handling.** Scores are compared only for ordering. Cross-language conformance asserts the **`docId`
sequence**, never float equality; `ln` implementations may differ in the last bits and that is acceptable.

## 5. Tools

All tools return `content: [{ type: "text", text: <json> }]` where `<json>` is the serialized payload below, plus
`structuredContent` with the same object. Errors use the MCP error result with `isError: true` and a payload of
`{ "error": { "code": <string>, "message": <string> } }`.

### 5.1 `search`

```json
{
  "name": "search",
  "description": "Search the corpus. Returns ranked chunks with citations.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "minLength": 1, "maxLength": 512 },
      "k": { "type": "integer", "minimum": 1, "maximum": 20, "default": 5 }
    },
    "required": ["query"],
    "additionalProperties": false
  }
}
```

Result:

```json
{
  "query": "rotate api key",
  "k": 2,
  "totalMatched": 7,
  "results": [
    {
      "docId": "ops-credentials",
      "chunkId": "ops-credentials#02",
      "title": "Rotating API keys",
      "heading": "How to rotate",
      "score": 0.8421,
      "citation": "ops-credentials#02",
      "text": "Rotate a key by creating a new one, ..."
    }
  ]
}
```

Field notes: `totalMatched` counts all chunks with `score > 0`. `score` is rounded to 4 decimals **for display
only**; ordering uses the unrounded value. `text` is the chunk body, unmodified.

### 5.2 `get_document`

```json
{
  "name": "get_document",
  "description": "Fetch a full corpus document by id.",
  "inputSchema": {
    "type": "object",
    "properties": { "docId": { "type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$" } },
    "required": ["docId"],
    "additionalProperties": false
  }
}
```

Result:

```json
{
  "docId": "ops-credentials",
  "title": "Rotating API keys",
  "tags": ["security", "credentials", "api"],
  "chunkCount": 3,
  "markdown": "---\nid: ops-credentials\n...",
  "source": "corpus/ops-credentials.md"
}
```

`markdown` is the file content exactly as stored, normalized to LF. Unknown id → error code `DOC_NOT_FOUND`.

### 5.3 `answer`

```json
{
  "name": "answer",
  "description": "Answer a question using only corpus content. Extractive, with citations.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "minLength": 1, "maxLength": 512 },
      "k": { "type": "integer", "minimum": 1, "maximum": 10, "default": 3 }
    },
    "required": ["query"],
    "additionalProperties": false
  }
}
```

Algorithm (frozen):

1. Run `search(query, k)`.
2. If no chunk scored above zero → return `grounded: false`, `answer: "No content in the corpus matches this question."`,
   `citations: []`.
3. Split each retrieved chunk into sentences: split on `.`, `!`, `?` followed by whitespace or end of text; drop
   fragments shorter than 20 characters.
4. Score each sentence by the number of distinct query tokens it contains. Keep the top 3 sentences.
5. Emit them in **document order** (chunk rank, then sentence position) and join with a single space.
6. `citations` = the chunkIds of the chunks those sentences came from, in the same order, deduplicated.
7. `grounded: true`.

Result:

```json
{
  "query": "how do I rotate an api key",
  "answer": "Rotate a key by creating a new one, deploying it, and revoking the old one after 24 hours. ...",
  "citations": ["ops-credentials#02", "ops-runbook#04"],
  "grounded": true
}
```

Conformance for `answer` is **looser than for `search`**: the test asserts `grounded` and the `citations` array.
Sentence splitting is the one place where two standard libraries can legitimately disagree on an edge case, so the
contract does not pretend otherwise.

## 6. Error codes

| Code | When | REST mapping |
|---|---|---|
| `INVALID_ARGUMENT` | Schema violation, empty query, `k` out of range | `400` |
| `DOC_NOT_FOUND` | `get_document` with unknown id | `404` |
| `CORPUS_UNAVAILABLE` | Index failed to build at boot | `503` |
| `INTERNAL` | Anything else | `500` |

## 7. Conformance

`corpus/golden/queries.json` holds 10 queries:

```json
{
  "contractVersion": 1,
  "cases": [
    {
      "id": "rotate-api-key",
      "query": "how do I rotate an api key",
      "k": 3,
      "expectDocIds": ["ops-credentials", "ops-runbook", "ops-faq"],
      "expectGrounded": true
    }
  ]
}
```

Rules:

- `expectDocIds` is written by hand against the spec, not captured from an implementation. Capturing output would
  make the test assert that two implementations agree with each other, which is weaker than agreeing with the spec.
- At least one case must exercise the `grounded: false` path.
- At least one case must be a deliberate miss (query whose tokens appear nowhere) to prove no false positives.
- Adding a document to `corpus/` requires re-checking every case, because `avgdl` and `N` change scores.

## 8. Versioning

Any change to chunking, tokenization, BM25 constants, ordering, or tool schemas is a breaking change:

1. Bump `contractVersion` in both servers and in `golden/queries.json`.
2. Update this document first.
3. Regenerate golden expectations **by hand** and review the diff.
