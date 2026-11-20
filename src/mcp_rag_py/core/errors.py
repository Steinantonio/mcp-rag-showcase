"""Typed errors and a minimal Result type.

Errors cross the boundary as values, never as exceptions carrying stack traces: the codes are part of the
contract (docs/tool-contract.md §6) and both implementations must produce the same ones.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar

T = TypeVar("T")


class ErrorCode(StrEnum):
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    DOC_NOT_FOUND = "DOC_NOT_FOUND"
    CORPUS_UNAVAILABLE = "CORPUS_UNAVAILABLE"
    INTERNAL = "INTERNAL"


@dataclass(frozen=True, slots=True)
class RagError:
    code: ErrorCode
    message: str

    def to_payload(self) -> dict[str, dict[str, str]]:
        return {"error": {"code": self.code.value, "message": self.message}}


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    value: T

    @property
    def is_ok(self) -> bool:
        return True


@dataclass(frozen=True, slots=True)
class Err(Generic[T]):
    error: RagError

    @property
    def is_ok(self) -> bool:
        return False


Result = Ok[T] | Err[T]


def invalid_argument(message: str) -> Err[T]:
    return Err(RagError(ErrorCode.INVALID_ARGUMENT, message))


def doc_not_found(doc_id: str) -> Err[T]:
    return Err(RagError(ErrorCode.DOC_NOT_FOUND, f"document not found: {doc_id}"))
