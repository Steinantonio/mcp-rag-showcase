# ADR 0002 — Freeze the scoring spec and prove parity with golden vectors

- **Status:** Accepted
- **Date:** 2026-11-20
- **Deciders:** repo owner
- **Contract impact:** defines `docs/tool-contract.md` §7, §8

## Context

The repo's differentiator is the claim *"the same contract, implemented twice, returns the same answers"*. That
claim is worthless unless it is mechanically checkable, and it is easy to fake: run one implementation, capture its
output as the expected value, and assert the other matches. Such a test proves the two implementations agree with
each other — including on each other's bugs — and proves nothing about either being correct.

There is a second, subtler risk: two implementations can drift without anyone noticing. A `string.Split(' ')` in C#
versus `re.split(r'\s+')` in Python tokenizes differently; `ToLower()` versus `ToLowerInvariant()` differs on
Turkish `I`; BM25 with `dl` computed over characters instead of tokens silently produces different rankings. None of
these throw. All of them are invisible in a demo and fatal to the claim.

## Decision

1. **`docs/tool-contract.md` is the source of truth**, and it is written at a level of detail that leaves no
   discretionary choices: exact regex for tokenization, exact chunk size and splitting rule, exact BM25 constants,
   exact tie-break order, exact rounding rule, and an explicit statement that scores are compared only for ordering.
2. **Golden expectations are written by hand from the spec**, before or independently of the implementations, and
   stored in `corpus/golden/queries.json`. They are never captured from program output.
3. **The conformance suite asserts document ids, not floats.** For `search` it compares the `docId` sequence for
   `k` results. For `answer` it compares `grounded` and the `citations` array — deliberately looser, because
   sentence splitting is the one place where two standard libraries can legitimately disagree on an edge case, and
   pretending otherwise would produce a flaky test that teaches the reader to ignore failures.
4. **The golden set must include the ugly cases:** one query with zero matches (proves no false positives), one
   query that ranks a document first for a non-obvious reason (proves IDF is actually applied), and one query with
   repeated tokens (proves query-side deduplication is absent, per spec).
5. **`contractVersion` is embedded in both servers and in the golden file.** A mismatch fails the build before any
   ranking test runs, so a half-applied contract change cannot masquerade as a ranking regression.
6. **Duplication is intentional and documented.** Two ~60-line BM25 implementations are not an abstraction failure;
   they are the artifact being demonstrated. A shared library or a service call would delete the point of the repo.

## Consequences

**Good**

- The parity claim is falsifiable: a reviewer can edit a constant in one implementation and watch the suite go red.
- Contract changes are forced through documentation first, which keeps `tool-contract.md` honest instead of
  descriptive of whatever the code happens to do.
- Adding a corpus document is a deliberate act, because it shifts `N` and `avgdl` and requires re-deriving
  expectations by hand. That friction is the feature.

**Bad**

- **Hand-computed expectations are laborious** and slightly error-prone; a mistake means re-deriving by hand after
  investigating a red test, not just accepting the new output.
- **The suite is corpus-locked.** Any corpus edit can break all 10 cases, so the corpus is effectively frozen after
  W1. New documents go in a `corpus-v2` branch with new expectations.
- **No quality metric.** The suite proves agreement and spec-conformance, not retrieval quality. There is no
  recall@k, no MRR, no labeled relevance set. Adding one would be honest work and is out of scope.
- **Two implementations to maintain** for every future contract change, which is exactly the cost the repo is
  advertising.

## Alternatives rejected

| Alternative | Why rejected |
|---|---|
| Capture expectations from one implementation | Proves mutual agreement, not correctness; hides shared bugs; trivially circular |
| Golden JSON of full response bodies (scores included) | Cross-language float formatting makes it flaky; the `ln` implementations are not required to be bit-identical |
| One shared implementation behind an HTTP call | Deletes the differentiator; also makes the .NET server useless without the Python one running |
| Property-based testing (rank invariants only) | Nice complement, but it cannot catch a tokenizer divergence that is internally consistent |
| Differential fuzzing of the tokenizer | Genuinely valuable, and a good W6+ addition: 1k random strings through both tokenizers, compare token lists exactly |

## Follow-up

- W3 adds a **tokenizer differential test** (same 200 fixed strings, both languages, exact token-list equality). This
  is the cheapest possible guard against the failure mode this ADR is most worried about.
- If a corpus-v2 ever appears, expectations are regenerated by hand with the diff reviewed line by line.

## Amendment (2026-11-20) — ordering parity is not arithmetic parity

While writing the CI spec, the red-path check exposed a gap. Changing `k1` from `1.2` to `2.0` in the C#
implementation moved every score by up to 70% and still produced the **same `docId` sequence** for all ten golden
queries. The parity suite passed, which means it was proving less than the spec claimed: it proves the two
implementations *rank* the same documents, not that they *compute* the same numbers.

The decision stands — ordering never uses floats — but the suite now also compares scores with a tolerance of `1e-4`,
which is one unit in the last place of the 4-decimal CLI payload. This is a drift detector, not an equality
assertion: `1e-4` absorbs the last bits of two `ln` implementations and still catches a changed constant. A subtle
formula change smaller than `1e-4` would slip through, and that limitation is stated rather than hidden.
