# Delegation brief — orchestrator → <agent>

- **Spec:** SPEC-NNN, criteria AC-NNN-XX…
- **Date:** YYYY-MM-DD
- **Deadline:** end of this wave

## Objective

One paragraph. What must exist when this is done, stated as an observable outcome.

## Scope

**Files you own in this task**

- `path/**`

**Do not touch**

- `path/**` — owned by …

## Acceptance criteria in play

| Criterion | What proves it |
|---|---|
| AC-NNN-XX | `tests/…::test_name` |

## Definition of done

- [ ] Every criterion above has evidence.
- [ ] Full relevant suite run; output pasted in the handoff.
- [ ] Task status updated in `specs/NNN-*/tasks.md`.

## Constraints

- Contract first: do not change constants, regexes, ordering or schemas.
- No new dependency without an ADR.
- Report a blocker instead of working around it.

## Return

`templates/handoff.md`.
