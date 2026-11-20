"""The contract version must be identical in four places, SPEC-005 AC-005-04."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

import mcp_rag_py

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_contract_version_is_consistent_everywhere() -> None:
    python_version = mcp_rag_py.CONTRACT_VERSION

    golden = json.loads((REPO_ROOT / "corpus" / "golden" / "queries.json").read_text(encoding="utf-8"))
    golden_version = golden["contractVersion"]

    csharp_source = (REPO_ROOT / "src" / "Mcp.Rag.Dotnet" / "Core" / "Contract.cs").read_text(encoding="utf-8")
    match = re.search(r"public const int Version = (\d+);", csharp_source)
    assert match, "Contract.cs must declare 'public const int Version = N;'"
    csharp_version = int(match.group(1))

    spec = yaml.safe_load((REPO_ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8"))
    openapi_version = spec["components"]["schemas"]["Health"]["properties"]["contractVersion"]["const"]

    versions = {
        "src/mcp_rag_py/__init__.py": python_version,
        "corpus/golden/queries.json": golden_version,
        "src/Mcp.Rag.Dotnet/Core/Contract.cs": csharp_version,
        "docs/openapi.yaml": openapi_version,
    }

    mismatched = {path: value for path, value in versions.items() if value != python_version}
    assert not mismatched, f"contractVersion drift: {mismatched} (expected {python_version})"
