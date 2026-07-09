"""Substrate-agnostic backend interface.

The whole point of Mnestra is that the *logical* memory model is independent of the
*physical* substrate. Every backend — classical RAM/phase-change, photonic holographic,
or quantum (atomic-frequency-comb) — implements this one interface. Application code and
language bindings target the interface, never the physics, so a program written today
against the classical backend runs unchanged on photonic or quantum hardware as it matures.

Five logical operations span all three substrates:

    write(address, pattern)   store an interference/state pattern at a content address
    read(address)             recall the exact pattern (causal/positional access)
    query(cue, k)             content-addressed / associative recall ("read by meaning")
    reconstruct()             return the global, structure-complete view (the "hologram")
    stats()                   substrate-specific health (capacity, coherence, fidelity)

`query` and `reconstruct` are what let a generator "read the rest of the book": associative
recall surfaces semantically related regions, and reconstruct exposes the whole structure
from any single point — the defining property of a hologram, and of this memory model.
"""
from __future__ import annotations

import abc
import hashlib
import json
import math
import re
from typing import Any


def content_address(data: Any) -> str:
    """Stable content address (BLAKE2b). Two equal payloads → one address, on any
    substrate. This is the bridge between the logical model and physical storage."""
    blob = json.dumps(data, sort_keys=True, default=str, ensure_ascii=False).encode("utf-8")
    return hashlib.blake2b(blob, digest_size=16).hexdigest()


_TOKEN = re.compile(r"[a-z0-9]+")


def embed(text: str, dim: int = 64) -> list[float]:
    """Tiny dependency-free hashed bag-of-words embedding.

    Stands in for the physical feature representation: spectral channels (photonic),
    frequency bins of an absorption comb (quantum AFC), or a learned vector (classical).
    Pure stdlib so the reference runs anywhere with no install."""
    vec = [0.0] * dim
    for tok in _TOKEN.findall(text.lower()):
        h = int(hashlib.blake2b(tok.encode(), digest_size=8).hexdigest(), 16)
        vec[h % dim] += 1.0
        vec[(h >> 8) % dim] -= 1.0  # signed hashing reduces collisions
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class Backend(abc.ABC):
    """One physical substrate behind the Mnestra logical memory model."""

    name: str = "abstract"
    substrate: str = "abstract"

    @abc.abstractmethod
    def write(self, address: str, pattern: dict) -> None: ...

    @abc.abstractmethod
    def read(self, address: str) -> dict | None: ...

    @abc.abstractmethod
    def query(self, cue: str, k: int = 1) -> list[tuple[str, float]]:
        """Associative / content-addressed recall: return up to k (address, score)."""

    @abc.abstractmethod
    def reconstruct(self) -> dict:
        """The structure-complete global view recoverable from the whole store."""

    def stats(self) -> dict:
        return {"backend": self.name, "substrate": self.substrate}
