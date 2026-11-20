# Corpus

Fifteen documents describing a fictional internal operations handbook. Everything here is written for this
repository: no third-party text, no real company data, nothing that needs a license.

## Why it exists

Every number in the engine comes from this corpus: `N` (chunk count), `avgdl` (average chunk length), every IDF.
The documents are the *ruler*. Change them and every previous measurement becomes meaningless.

The corpus is therefore **frozen** after `golden/queries.json` is derived (Constitution, Article 7). A change here
requires a new spec and a full re-derivation of the expectations, reviewed line by line.

## Rules

| Rule | Value |
|---|---|
| Count | exactly 15 documents |
| Length | 300–600 words each |
| Structure | 3–5 `##` sections per document |
| Front matter | `id`, `title`, `tags` only, restricted grammar (no YAML library) |
| File name | `<id>.md` |
| Language | English, matching the rest of the artifacts |

## Clusters (deliberate near-duplicates)

Ranking is only interesting when documents compete for the same query.

| Cluster | Documents | Shared vocabulary |
|---|---|---|
| Credentials | `ops-credentials`, `ops-runbook`, `ops-faq` | key, rotation, revoke, overlap window, ninety days |
| Incidents | `ops-incidents`, `ops-escalation` | SEV1, SEV2, pager, on-call, incident commander |
| Backups | `ops-backups`, `ops-data-retention` | backup, snapshot, restore, retention window |

Each document takes a different angle on the shared terms — policy, procedure, or definition — so BM25 has to
discriminate by term frequency and document length rather than by vocabulary alone.

## Documents

| Id | Title | Angle |
|---|---|---|
| `ops-onboarding` | Your first week on call | access and expectations |
| `ops-credentials` | Rotating API keys | procedure |
| `ops-runbook` | Runbooks and quarterly drills | drills |
| `ops-faq` | Operations FAQ | short answers |
| `ops-incidents` | Incident severity and response | policy |
| `ops-escalation` | Paging and escalation paths | routing |
| `ops-backups` | Backups and restores | procedure |
| `ops-data-retention` | Data retention and deletion | policy |
| `ops-monitoring` | Monitoring, alerts and error budgets | signals |
| `ops-networking` | Network access, VPN and egress | access |
| `ops-deployments` | Deploying and rolling back | delivery |
| `ops-access-review` | Quarterly access review | governance |
| `ops-cost-controls` | Cost controls and budgets | finance |
| `ops-glossary` | Glossary | definitions |
| `ops-changelog` | Changelog of operations policy | history |

## Golden vectors

`golden/queries.json` holds ten cases with the exact `docId` sequence a conforming implementation must return. They
are derived from the contract and the documents, never captured from a running implementation — capturing would
only prove that two implementations agree with each other.

The set deliberately includes a query with no lexical match, a query with repeated tokens, and a query whose
ranking depends on a rare term (high IDF) rather than on repetition.

## Measured shape

| Metric | Value |
|---|---|
| Documents | 15 |
| Chunks | 63 |
| Tokens | 3 847 |
| `avgdl` | 61.06 |
| Largest chunk | 714 characters |
| Smallest chunk count per document | 4 |

These numbers are the ruler. They are recorded here so a future change to the corpus is visibly a change to every
score in the system.
