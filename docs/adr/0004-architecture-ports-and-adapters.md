# ADR 0004 — Ports and adapters with a pure functional core

- **Status:** accepted
- **Date:** 2026-11-20
- **Deciders:** repo owner
- **Contract impact:** none (defines structure, not behavior)

## Context

The repository must expose one retrieval engine through three protocols (MCP stdio, MCP streamable HTTP, REST/OpenAPI)
in two languages, and prove the two languages agree. That is an architecture problem before it is a coding problem:
if retrieval logic lives inside a FastAPI route or an MCP tool handler, it cannot be tested without a transport, it
cannot be ported without translation, and parity becomes a matter of luck.

Two failure modes are common in repositories like this one:

1. **Logic in the transport.** The handler tokenizes, ranks and formats. Tests then need a client, and the second
   implementation re-derives the logic from the first one's behavior instead of from a spec.
2. **Ceremony instead of boundaries.** Four projects named Domain/Application/Infrastructure/Api for ~2k LOC, where
   the only real variation is the protocol on the outside. The dependency rule is technically enforced, and nothing
   is actually easier to test.

## Decision

1. **Ports and adapters (hexagonal).** `core` holds the retrieval semantics. `adapters` translate protocols. The
   dependency arrow points one way: `adapters → core`. Never the reverse.
2. **Functional core.** `core` is pure functions over immutable values: no clock, no randomness, no network, no
   filesystem, no environment, no global mutable state. Given the corpus and a query, the result is a value.
3. **Imperative shell.** Validation, serialization, error mapping, logging and I/O live in the adapters and in the
   composition root. The shell may be as ugly as reality requires; the core may not.
4. **Typed results, not exceptions.** Errors cross the boundary as `RagError` values with the codes from contract §6.
   Exceptions are for programmer error, not for "document not found".
5. **One composition root per server.** `Program.cs` and `apps/http.py` wire the object graph explicitly. No service
   locator, no module-level singleton holding the index.
6. **Enforced, not documented.** `import-linter` (Python) and `NetArchTest` (.NET) fail the build if `core` imports a
   framework, a transport, or the filesystem.
7. **Deliberate duplication.** The tokenizer, chunker and BM25 exist twice, ~60–120 lines each. A shared library or a
   network call would delete the artifact the repository exists to demonstrate (ADR 0002).

## Consequences

**Good**

- The engine is testable with plain data: no server, no port, no fixture with a network.
- The PoC milestone (SPEC-002) needs no MCP at all; MCP becomes a door added later.
- Adding a fourth surface (say, a gRPC adapter) touches no core file.
- The boundary is a failing test, not a code-review opinion.
- The architecture diagram in the README is executable: the tests prove the arrows.

**Bad**

- Two implementations of the same algorithm, by design, with the maintenance cost that implies.
- Some duplication inside `core` itself: the answer pipeline repeats a retrieval call that the `search` tool also
  makes. Cheap here, wasteful at scale.
- Adapters can still drift in *serialization* (field names, envelope shape). Mitigated by the committed OpenAPI
  document and the drift check, not by architecture.
- Purity is a discipline that erodes: someone will eventually want `datetime.now()` in the core. The architecture test
  catches imports, not intentions.

## Alternatives rejected

| Alternative | Why rejected |
|---|---|
| Clean Architecture with four projects (Domain/Application/Infrastructure/Api) | The variation here is protocol, not layer. Four assemblies for 2k LOC adds ceremony without a test that gets easier to write |
| Vertical slice per tool | Three tools × two languages × two surfaces = 12 slices; the shared algorithm would be duplicated 12 times instead of 2 |
| Service-oriented: one engine service, thin clients | Deletes the parity artifact, adds a network hop, and makes the .NET server useless without the Python one running |
| CQRS | Read-only system; there is no write model to separate |
| MediatR / handler-per-use-case | Three operations. The indirection costs more than it explains |
| Generic repository over the corpus | The corpus is an immutable collection loaded once; an explicit `CorpusSource` port is smaller and clearer |
| Tactical DDD (aggregates, domain events) | No transactional invariants exist. The invariants are arithmetic (chunk bounds, ordering), not business state |
| Framework-native structure (FastAPI routers as the unit of design) | Ties the semantics to one transport and makes the C# port a translation of Python's routing choices |

## Follow-up

- SPEC-002 adds `tests/arch/test_boundaries.py` with the `import-linter` contract.
- SPEC-003 adds the `NetArchTest` equivalent and the tokenizer differential test.
- If a fourth adapter ever appears, this ADR is the checklist: new adapter, zero core changes.
