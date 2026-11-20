# Methodology — spec-driven delivery with a small agent team

This document explains how the repository is built, not what it does. It exists so the process can be audited the
same way the code is.

## 1. The chain

```
brief (why) → constitution (rules) → spec (what) → plan (how) → tasks (steps)
   → red test → implementation → validation → evidence → learning
```

| Artifact | Answers | Owner | Fails when missing |
|---|---|---|---|
| Brief | why does this exist | orchestrator | the repo becomes a pile of code with no claim |
| Constitution | what is never negotiable | orchestrator | every decision becomes a debate |
| Spec | what must be true | architect | two implementations invent two behaviors |
| Plan | how, in which order | architect | work happens in the wrong sequence and gets redone |
| Tasks | what is the next step | implementers | progress is invisible |
| Evidence | how do we know | everyone | claims become adjectives |

## 2. Why this shape and not a framework

Three options were considered:

| Option | Verdict |
|---|---|
| Home-grown chain, copied from `IT_CrudWorks` | **chosen** — zero tooling, readable in a browser, identical in shape to Spec Kit |
| OpenSpec | rejected for this repo: adds npm tooling to a repository whose selling point is "clone and run" |
| GitHub Spec Kit CLI | rejected: another CLI, and its templates would be rewritten by the first customization anyway |

The shape is deliberately the same as Spec Kit's artifact chain (`constitution → specify → plan → tasks → implement`),
so a reader who knows that vocabulary recognizes this immediately. The difference is that nothing here needs to be
installed to read it.

## 3. Spec lifecycle

`draft → approved → implementing → implemented → retired`

- Only `approved` specs can be implemented. Approval requires testable criteria, closed scope and resolved questions.
- Specs 003–005 are written at the start of their wave. A spec written before its inputs exist is fiction, and
  fiction in a spec is worse than no spec.
- `implemented` is set by the conformance engineer, when every criterion has evidence.

## 4. The team

Six agents, one primary and five subagents, mirroring the six kinds of risk rather than an org chart.

| Agent | Risk it owns |
|---|---|
| Orchestrator | sequencing, integration, honesty of the final narrative |
| Architect | the shape; whether two implementers could disagree |
| Python implementer | retrieval correctness in Python |
| .NET implementer | retrieval correctness in C#, and fidelity to the contract |
| Conformance engineer | whether the two are actually equivalent, in CI and in a container |
| Reviewer | what a stranger would catch |

Plus `shared-reviewer-pilot`: a read-only reviewer with fresh context, used when a change is large enough that the
author's assumptions are a liability.

Rules that keep the team from becoming theatre:

- One owner per artifact. No agent restates another's job.
- The reviewer never edits the fix; the conformance engineer never rewrites the feature.
- Every handoff carries evidence, and the orchestrator verifies it instead of forwarding it.
- Commits are local, by the orchestrator. Pushing is the owner's decision.

## 5. The loop, per wave

1. **Spec** — approved, with ordered tasks.
2. **Brief** — the orchestrator writes scope, criteria, boundary, definition of done.
3. **Red** — the owner writes a failing test with the exact expected value from the criterion.
4. **Green** — the minimum implementation.
5. **Refactor** — clarity without behavior change.
6. **Verify** — run the suite; paste the real output.
7. **Review** — independent review for anything non-trivial.
8. **Integrate** — tasks, traceability, plan status, README/ADR if behavior changed.
9. **Commit** — one wave, one conventional commit.

## 6. Evidence protocol

- Code claim → `path:line`.
- Command claim → command plus real output.
- Test claim → test name plus result.
- Unverifiable claim → marked **Unverified** or deleted.
- AI-assisted change → `docs/ai/NNN-topic.md` with prompt summary, what was validated, what was corrected, what was
  rejected.

The point is not bureaucracy. It is that this repository's entire value proposition is *"the claim is checkable"*, and
a claim cannot be checkable if its own construction is not.

## 7. What the process deliberately does not do

- No story points, no velocity, no sprint ceremonies. A 15-document demo does not need a backlog.
- No CI-gated spec linting. The specs are read by humans; a linter would only enforce formatting.
- No agent-to-agent chatter. Agents return handoffs to the orchestrator, which integrates.
- No retro documents. The evidence log and the ADRs are the retro.
