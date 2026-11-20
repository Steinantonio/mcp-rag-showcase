"""Tokenization, contract §3.

A token character is a Unicode letter (category L*) or a decimal digit (category Nd). Everything else separates
tokens. No stemming, no stopwords, no accent folding, no locale-sensitive casing.

Known edge, documented rather than hidden: casing is locale-independent but not identical across runtimes for a
handful of characters (for example U+0130 in Python vs .NET). The differential fixture in SPEC-003 sticks to
ASCII and Latin-1, where both agree.
"""

from __future__ import annotations


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []

    for char in text.lower():
        if char.isalpha() or char.isdecimal():
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current.clear()

    if current:
        tokens.append("".join(current))

    return tokens
