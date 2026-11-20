"""Generate tokenizer fixture: 200 plain strings for cross-language differential testing."""

from __future__ import annotations

import json
from pathlib import Path

from mcp_rag_py.core.tokenizer import tokenize

cases = [
    # contract examples and edge cases
    "Rotate the API key! (v2)",
    "snake_case-name.v2",
    "Ação crédito Débito",
    "sev1 sev-1 sev_1",
    "UPPERCASE lowercase MiXeD",
    "",
    "   ",
    "!!! --- ... ???",
    "hello",
    "the quick brown fox",
    "123 456 789",
    "a1 b2 c3",
    # repeated characters
    "aaa bbb ccc",
    "...leading-punctuation",
    "trailing-punctuation...",
    "multiple   spaces   here",
    "underscore_between_words",
    "hyphen-between-words",
    "period.between.words",
    "numbers123and456letters",
    "UPPERCASE123mixed",
    # non-ASCII
    "cafe naive Noel",
    "straße",
    "señor",
    # real query shapes
    "how do I rotate an api key",
    "restore a database backup",
    "what is a sev1 incident",
    "quarterly access review",
    "roll back the previous artifact",
    "egress rules",
    "error budget",
    "kubernetes helm chart",
    "backup backup restore restore",
    # single terms
    "rotation",
    "api",
    "key",
    "SEV1",
    "SEV2",
    "database",
    "backup",
    "restore",
    "deployment",
    "rollback",
    "incident",
    "escalation",
    "onboarding",
    "credentials",
    "monitoring",
    "networking",
    "access",
    "review",
    "retention",
    "cost",
    "budget",
    # multi-word phrases
    "api key rotation procedure",
    "database backup restore process",
    "incident response escalation ladder",
    "quarterly access review meeting",
    "deployment pipeline canary rollout",
    "error budget burn rate",
    "service level objective monitoring",
    "credential vault audit log",
    "postmortem action item owner",
    "blast radius confirmation step",
    # punctuation variants
    'quoted text',
    "(parenthesized)",
    "[bracketed]",
    "key: value pair",
    "path/to/resource",
    "user@domain",
    "https://example.com",
    "version 2.4.0",
    # mixed with special chars
    "api-key-v2",
    "backup_restore_v3",
    "SEV1-SEV2 escalation",
    "99.9% uptime",
    "#channel-name",
    "@username",
    # edge lengths
    "a",
    "ab",
    "a" * 500,
    "x" * 1000,
]

# add variations to reach ~200
more = [
    f"query about {topic} with details"
    for topic in [
        "keys", "backups", "incidents", "deployment", "access",
        "monitoring", "networking", "cost", "retention", "onboarding",
    ]
    for _ in range(6)
]
cases.extend(more)

# add numbered suffixes to pad
for i in range(len(cases), 200):
    cases.append(f"pad item {i}")

cases = cases[:200]
fixture_dir = Path("tests/fixtures")
fixture_dir.mkdir(parents=True, exist_ok=True)
fixture_dir.joinpath("tokenizer_cases.json").write_text(
    json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8"
)

# sanity: tokenize all and print sample
tokens = [tokenize(c) for c in cases[:10]]
for c, t in zip(cases[:10], tokens):
    print(f"{c!r} => {t}")
print(f"{len(cases)} cases written")
