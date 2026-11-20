from __future__ import annotations

from mcp_rag_py.core.tokenizer import tokenize


def test_contract_example_ac_002_01() -> None:
    assert tokenize("Rotate the API key! (v2)") == ["rotate", "the", "api", "key", "v2"]


def test_punctuation_and_underscore_separate_tokens() -> None:
    assert tokenize("snake_case-name.v2") == ["snake", "case", "name", "v2"]


def test_letters_and_digits_stay_together() -> None:
    assert tokenize("sev1 sev-1") == ["sev1", "sev", "1"]


def test_non_ascii_letters_are_kept_and_lowercased() -> None:
    assert tokenize("Ação Crédito") == ["ação", "crédito"]


def test_no_stemming_and_no_stopwords() -> None:
    assert tokenize("rotating rotation rotated the of") == [
        "rotating",
        "rotation",
        "rotated",
        "the",
        "of",
    ]


def test_empty_and_separator_only_input() -> None:
    assert tokenize("") == []
    assert tokenize("   !!! --- ... ") == []
